#!/usr/bin/env python3
"""Reopen the store read-only and read the investigation from it. No model.

With no arguments, prints each alert with its evidence, its onward routes and
the devices on them, where the two alerts differ, and what event-time
processing kept that arrival order would have lost. With --cypher or --sql,
runs one read-only query against the store or the tables and prints the rows.
"""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

from alertcase import reference, tables
from alertcase.cases import CASES
from alertcase.events import load_events
from alertcase.graph import Graph


def money(minor: int) -> str:
    return f"{minor // 100:,}.{minor % 100:02d}"


def clock(ms: int) -> str:
    return datetime.fromtimestamp(ms / 1000, tz=timezone.utc).strftime("%H:%M:%S")


def investigation(graph: Graph, events_path: Path, scenario_path: Path) -> None:
    designed = json.loads(scenario_path.read_text())["designed"]
    if "alerts" in designed:  # the large case lists its alerts
        labels = {a["account"]: f"designed as {'suspicious' if a['label'] == 'suspicious' else 'a benign lookalike'}"
                  for a in designed["alerts"]}
    else:
        labels = {designed["suspicious"]["account"]: "designed as suspicious",
                  designed["benign"]["account"]: "designed as the benign lookalike"}
    run = graph.run_records()[0]["run"]
    transfers = {t["transfer_id"]: t for t in graph.transfers()}
    indicators = graph.indicators()
    found = {r["indicator"]: r for r in graph.investigation()}

    print(f"{run['id']}: a {run['replay']} replay of {run['dataset_events']} events "
          f"(sha256 {run['dataset_sha256'][:12]}...), {run['jobs_completed']} of {run['jobs']} clink jobs completed, "
          f"written through {run['route']}.")
    print("Everything below holds for this dataset only. A recorded relationship is not proof of fraud, "
          "ownership, identity or causation.")

    for i in indicators:
        f = found[i["id"]]
        print(f"\nALERT {i['id']}   ({labels.get(i['account'], 'not designed')})")
        print(f"  indicator  {i['senders']} senders paid {i['account']} {money(i['total_minor'])} in "
              f"{i['transfers']} transfers between {clock(i['window_start'])} and {clock(i['window_end'])} UTC, event time")
        print(f"  evidence   {' '.join(i['transfer_ids'])}")
        routes = graph.routes(i["id"])
        if not routes:
            print("  onward     nothing passed on within 30 minutes")
        # Routes that share everything after their first transfer are one chain
        # fed by several contributing transfers.
        chains: dict[tuple[str, ...], list[dict]] = {}
        for r in routes:
            chains.setdefault(tuple(r["transfers"][1:]), []).append(r)
        for chain, fed in chains.items():
            accounts = " -> ".join([i["account"]] + [transfers[t]["dst"] for t in chain])
            sources = " ".join(r["transfers"][0] for r in fed)
            steps = "  ".join(f"{t} {money(transfers[t]['amount_minor'])} at {clock(transfers[t]['ts'])}" for t in chain)
            print(f"  route      {accounts}, {len(chain)} onward link(s)")
            print(f"             from {sources}; then {steps}")
            example = fed[0]
            print(f"             e.g. path:{'>'.join(example['transfers'])} = {' '.join(example['links'])}")
        if routes:
            print(f"  onward     {f['onward_depth']} onward link(s) at most; came to rest at {', '.join(f['terminal_accounts'])}")
        if f["shared_devices"]:
            for device, accounts in f["shared_devices"].items():
                print(f"  device     {device} was used to send from {', '.join(accounts)}, all on this alert's routes")
        else:
            print("  device     no device is shared between accounts on this alert's routes")

    if len(indicators) != 2:
        print("\nTHE ALERTS SIDE BY SIDE")
        print(f"  {'account':<10} {'label':<34} {'senders':>7} {'total':>12}  {'depth':>5}  {'came to rest at':<22} shared on route")
        for i in indicators:
            f = found[i["id"]]
            shared = "; ".join(f"{d} ({len(acc)})" for d, acc in f["shared_devices"].items()) or "none"
            print(f"  {i['account']:<10} {labels.get(i['account'], 'not designed'):<34} {i['senders']:>7} "
                  f"{money(i['total_minor']):>12}  {f['onward_depth']:>5}  {', '.join(f['terminal_accounts']) or '-':<22} {shared}")
        print("  Every alert fires on the same rule. The relationships, read from Relate, are what separate them.")
        event_time_kept(designed, events_path, transfers)
        return

    a, b = indicators
    fa, fb = found[a["id"]], found[b["id"]]
    rows = [
        ("distinct senders in one hour", a["senders"], b["senders"]),
        ("transfers in the window", a["transfers"], b["transfers"]),
        ("total received", money(a["total_minor"]), money(b["total_minor"])),
        ("passed on within 30 minutes", "yes" if fa["onward_depth"] else "no", "yes" if fb["onward_depth"] else "no"),
        ("onward links, at most", fa["onward_depth"], fb["onward_depth"]),
        ("came to rest at", ", ".join(fa["terminal_accounts"]), ", ".join(fb["terminal_accounts"])),
        ("accounts on the routes", len(fa["route_accounts"]), len(fb["route_accounts"])),
        ("device shared on the routes",
         "; ".join(f"{d} ({len(acc)} accounts)" for d, acc in fa["shared_devices"].items()) or "none",
         "; ".join(f"{d} ({len(acc)} accounts)" for d, acc in fb["shared_devices"].items()) or "none"),
    ]
    sources = ["fan-in indicator"] * 3 + ["onward-transfer indicator"] + ["relationships, read from Relate"] * 4
    print("\nWHERE THE TWO ALERTS DIFFER")
    print(f"  {'':<30} {a['account']:<20} {b['account']:<20} from")
    for (name, x, y), source in zip(rows, sources):
        print(f"  {name:<30} {str(x):<20} {str(y):<20} {source}")
    print("  Both alerts fire on the same rules and both pass money on within 30 minutes. They differ in the totals,"
          " and in the relationships: how far the money went, where it came to rest, and a device shared along"
          " the way.")

    event_time_kept(designed, events_path, transfers)


def event_time_kept(designed: dict, events_path: Path, transfers: dict) -> None:
    events = load_events(events_path)
    full = {i["account"]: i for i in reference.fan_in(events)}
    strict = {i["account"]: i for i in reference.fan_in_without_tolerance(events)}
    all_links = {p["id"] for p in reference.onward(events)}
    lost_links = sorted(all_links - {p["id"] for p in reference.onward_in_arrival_order(events)})
    inv = designed["inversions"]
    print("\nWHAT EVENT TIME KEPT")
    late = inv["window_boundary"]
    suspect = late.get("account") or designed["suspicious"]["account"]
    after = f" after {late['arrives_after']}, which belongs to the next hour" if "arrives_after" in late else \
        " after events from the next hour"
    print(f"  {late['credit']} arrived{after}. With no allowance for late events the window closes first: "
          f"{strict[suspect]['senders']} senders and {money(strict[suspect]['total_minor'])}, instead of "
          f"{full[suspect]['senders']} and {money(full[suspect]['total_minor'])}.")
    fwd = inv["forwarding"]
    missed = ", ".join(lost_links) if len(lost_links) <= 3 else f"{len(lost_links)} of {len(all_links)} onward links"
    print(f"  {fwd['debit_arrives_first']} (the debit) arrived before {fwd['credit']} (the credit it passes on). A lookup made "
          f"as events arrive misses {missed} and reports {transfers[fwd['credit']]['dst']} as a resting point.")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--case", choices=sorted(CASES), default="small",
                        help="small: the 55-transfer case (default); large: 50,000 transfers")
    query = parser.add_mutually_exclusive_group()
    query.add_argument("--cypher", help="a read-only Cypher query against the store")
    query.add_argument("--sql", help="a read-only SQL query against tables/case.sqlite")
    args = parser.parse_args()
    case = CASES[args.case]
    case.unpack()

    if args.sql:
        db = tables.connect_read_only(case.tables)
        try:
            cursor = db.execute(args.sql)
            names = [d[0] for d in cursor.description or []]
            for row in cursor:
                print(json.dumps(dict(zip(names, row))))
        except sqlite3.Error as error:
            print(f"error: {error}", file=sys.stderr)
            return 1
        finally:
            db.close()
        return 0
    with Graph(case.store) as graph:
        if args.cypher:
            try:
                for row in graph.rows(args.cypher):
                    print(json.dumps(row, default=str))
            except Exception as error:  # Relate reports query errors with a fix in the message
                print(f"error: {error}", file=sys.stderr)
                return 1
            return 0
        investigation(graph, case.events, case.scenario)
    return 0


if __name__ == "__main__":
    sys.exit(main())
