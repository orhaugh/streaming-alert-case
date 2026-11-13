"""The same evidence as SQLite tables, for the table-based investigation.

export() reads every record from the published Relate store and writes it into
five tables, so the table arm of the comparison sees exactly the records the
graph arm sees, as rows instead of nodes and relationships. from_tables()
reads them back, so verify.py can show the tables still hold the bounded
dataset's facts.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

from .facts import Facts, _device_senders
from .graph import Graph

TABLES = Path("tables/case.sqlite")

SCHEMA = """
CREATE TABLE run (
    run_id TEXT PRIMARY KEY, replay TEXT NOT NULL, dataset_sha256 TEXT NOT NULL, dataset_events INTEGER NOT NULL,
    jobs INTEGER NOT NULL, jobs_completed INTEGER NOT NULL, clink_exit_status INTEGER NOT NULL,
    cancelled INTEGER NOT NULL, pipeline TEXT NOT NULL, clink TEXT NOT NULL, relate TEXT NOT NULL,
    lag_ms INTEGER NOT NULL, fan_in_min_senders INTEGER NOT NULL, fan_in_window_ms INTEGER NOT NULL,
    onward_max_gap_ms INTEGER NOT NULL);
CREATE TABLE transfers (
    transfer_id TEXT PRIMARY KEY, sender TEXT NOT NULL, receiver TEXT NOT NULL,
    amount_minor INTEGER NOT NULL, event_time_ms INTEGER NOT NULL, device TEXT NOT NULL);
CREATE TABLE fan_in_alerts (
    indicator_id TEXT PRIMARY KEY, account TEXT NOT NULL, window_start_ms INTEGER NOT NULL,
    window_end_ms INTEGER NOT NULL, senders INTEGER NOT NULL, transfers INTEGER NOT NULL,
    total_minor INTEGER NOT NULL);
CREATE TABLE alert_contributions (
    indicator_id TEXT NOT NULL REFERENCES fan_in_alerts, transfer_id TEXT NOT NULL REFERENCES transfers,
    PRIMARY KEY (indicator_id, transfer_id));
CREATE TABLE onward_links (
    link_id TEXT PRIMARY KEY, credit_transfer_id TEXT NOT NULL REFERENCES transfers,
    debit_transfer_id TEXT NOT NULL REFERENCES transfers, account TEXT NOT NULL, gap_ms INTEGER NOT NULL);
"""

# What the table-based agent is told about the tables. The graph-based agent
# is told the same things about the graph (agent.py).
DESCRIPTION = """SQLite database, opened read-only. Times are epoch milliseconds (event time, UTC); amounts are in minor units (cents).
- run(run_id, replay, dataset_sha256, dataset_events, jobs, jobs_completed, clink_exit_status, cancelled, pipeline, clink, relate, lag_ms, fan_in_min_senders, fan_in_window_ms, onward_max_gap_ms): the bounded replay these rows come from, one row.
- transfers(transfer_id, sender, receiver, amount_minor, event_time_ms, device): every transfer; sender and receiver are account ids; device is the device the transfer was sent from.
- fan_in_alerts(indicator_id, account, window_start_ms, window_end_ms, senders, transfers, total_minor): fan-in indicators derived by clink: an account that received transfers from at least fan_in_min_senders distinct senders inside one event-time hour.
- alert_contributions(indicator_id, transfer_id): the transfers that make up each fan-in indicator.
- onward_links(link_id, credit_transfer_id, debit_transfer_id, account, gap_ms): onward links derived by clink: a credit to an account followed, within onward_max_gap_ms by event time, by a debit from that same account; gap_ms is the time between them."""


INDEXES = """
CREATE INDEX transfers_sender ON transfers(sender);
CREATE INDEX transfers_receiver ON transfers(receiver);
CREATE INDEX transfers_device ON transfers(device);
CREATE INDEX alerts_account ON fan_in_alerts(account);
CREATE INDEX contributions_transfer ON alert_contributions(transfer_id);
CREATE INDEX links_credit ON onward_links(credit_transfer_id);
CREATE INDEX links_debit ON onward_links(debit_transfer_id);
CREATE INDEX links_account ON onward_links(account);
"""


def export(graph: Graph, path: Path = TABLES, indexes: bool = False) -> Path:
    """indexes: an index on every id the tables join on, as the Relate store
    keeps uniqueness constraints on its ids. The large case uses them."""
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        path.unlink()
    db = sqlite3.connect(path)
    try:
        db.executescript(SCHEMA)
        runs = [r["run"] for r in graph.run_records()]
        if len(runs) != 1:
            raise SystemExit(f"refused     the store holds {len(runs)} Run records, not one")
        run = runs[0]
        db.execute("INSERT INTO run VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (
            run["id"], run["replay"], run["dataset_sha256"], run["dataset_events"], run["jobs"],
            run["jobs_completed"], run["clink_exit_status"], int(run["cancelled"]), run["pipeline"], run["clink"],
            run["relate"], run["lag_ms"], run["fan_in_min_senders"], run["fan_in_window_ms"], run["onward_max_gap_ms"]))
        db.executemany("INSERT INTO transfers VALUES (?,?,?,?,?,?)", sorted(
            (t["transfer_id"], t["src"], t["dst"], t["amount_minor"], t["ts"], t["device"]) for t in graph.transfers()))
        for i in graph.indicators():
            db.execute("INSERT INTO fan_in_alerts VALUES (?,?,?,?,?,?,?)", (
                i["id"], i["account"], i["window_start"], i["window_end"], i["senders"], i["transfers"], i["total_minor"]))
            db.executemany("INSERT INTO alert_contributions VALUES (?,?)", [(i["id"], t) for t in i["transfer_ids"]])
        db.executemany("INSERT INTO onward_links VALUES (?,?,?,?,?)", [
            (p["id"], p["in_id"], p["out_id"], p["account"], p["gap_ms"]) for p in graph.onward_links()])
        if indexes:
            db.executescript(INDEXES)
        db.commit()
    finally:
        db.close()
    return path


def connect_read_only(path: Path = TABLES) -> sqlite3.Connection:
    if not path.exists():
        raise FileNotFoundError(f"no tables at {path}: run export_tables.py")
    db = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    db.execute("PRAGMA query_only = ON")
    return db


def from_tables(path: Path = TABLES) -> Facts:
    """The records the tables hold. The investigation is left empty: deriving
    routes from rows is what the table-based agent has to do itself."""
    db = connect_read_only(path)
    try:
        transfers = {r[0]: {"src": r[1], "dst": r[2], "amount_minor": r[3], "ts": r[4], "device": r[5]}
                     for r in db.execute("SELECT * FROM transfers")}
        contributions: dict[str, list[str]] = {}
        for ind, tid in db.execute("SELECT indicator_id, transfer_id FROM alert_contributions"):
            contributions.setdefault(ind, []).append(tid)
        indicators = {r[0]: {"account": r[1], "window_start": r[2], "window_end": r[3], "senders": r[4],
                             "transfers": r[5], "total_minor": r[6], "transfer_ids": sorted(contributions.get(r[0], []))}
                      for r in db.execute("SELECT * FROM fan_in_alerts")}
        links = {r[0]: {"in_id": r[1], "out_id": r[2], "account": r[3], "gap_ms": r[4]}
                 for r in db.execute("SELECT * FROM onward_links")}
        run = dict(zip(("dataset_sha256", "dataset_events"),
                       db.execute("SELECT dataset_sha256, dataset_events FROM run").fetchone()))
    finally:
        db.close()
    return Facts(source="tables", transfers=transfers, indicators=indicators, links=links, investigation={},
                 device_senders=_device_senders(transfers), run=run)
