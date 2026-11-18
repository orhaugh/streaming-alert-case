"""Evidence-driven revision of investigative findings.

A staged evolving investigation, not continuous streaming. Each evidence
revision is a bounded replay of everything known at that revision: revision 1
replays data/events.ndjson, and a later revision adds the transfers that
arrived after the one before it (pipeline/revision.sql). clink derives every
indicator and onward link; this module reads what clink wrote, and the checker
judges every claim against that and against the independent reference.

A claim has a stable id, a structured predicate, the evidence revision it was
asserted at, and a validation history that is only ever appended to. The claim
types it supports, and what each one's verdict can be changed by when only new
transfers arrive:

  event               one transfer, as recorded; nothing (an existing transfer
                      never changes, and a different one under its id is refused)
  indicator           a fan-in indicator's values and contributing transfers;
                      credits to its account inside its window
  onward_path         recorded onward links and, with ends_at, that none leaves
                      the last transfer; debits from the account the last
                      transfer paid, in the 30 minutes after it
  onward_reach        an alert's candidate paths; debits from each account a
                      path transfer paid, in the 30 minutes after it, and
                      credits to the alerted account inside its window
  no_onward_transfer  an absence with a recorded search scope: no qualifying
                      onward transfer from an account, its debit inside an
                      event-time interval, in one evidence revision; debits
                      from the account inside the interval, and credits to it
                      from 30 minutes before the interval to its end

Each of those is a window on one account. New evidence selects the claims with
a window one of its transfers falls into. Every onward link a new transfer
makes has that transfer at one end, inside a window of each claim the link can
affect, so selection misses nothing, given two preconditions this module keeps:
evidence is only added, and a claim is asserted only when the checker supports
it at its revision. Selecting a claim that turns out unchanged is allowed.
"""

from __future__ import annotations

import hashlib
import json
import os
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from . import claims as checker
from . import reference
from .events import FIELDS, load_events
from .facts import Facts

GAP_MS = reference.ONWARD_MAX_GAP_MS     # an onward link: a debit up to 30 minutes after a credit
HOUR_MS = reference.HOUR_MS              # a fan-in window
LAG_MS = 300_000                         # pipeline/revision.sql's watermark_lag_ms; a test holds them equal

TYPES = ("event", "indicator", "onward_path", "onward_reach", "no_onward_transfer")
ABSENCE_FIELDS = {"account": str, "start_ms": int, "end_ms": int}
ABSENCE_PATTERN = ("(c:Transfer)-[:PASSED_ON]->(d:Transfer)<-[:SENT]-(:Account {id: account}) "
                   "with d.ts inside the interval")


# ---------------------------------------------------------------------------
# Small helpers

def canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def moment(ms: int) -> datetime:
    return datetime.fromtimestamp(ms / 1000, tz=timezone.utc)


def hms(ms: int) -> str:
    return moment(ms).strftime("%H:%M:%S")


def day(ms: int) -> str:
    at = moment(ms)
    return f"{at.day} {at:%B %Y}"


def money(minor: int) -> str:
    return f"{minor // 100:,}.{minor % 100:02d}"


def links_text(n: int) -> str:
    return f"{n} onward link{'' if n == 1 else 's'}"


def duration(ms: int) -> str:
    minutes = abs(ms) // 60_000
    return f"{minutes // 60} h {minutes % 60} min" if minutes >= 60 else f"{minutes} min"


# ---------------------------------------------------------------------------
# Datasets. An evidence revision's dataset is every transfer known at it.

def dataset_of(investigation: Path, revision: dict) -> list[dict]:
    """Every transfer known at the revision, read from the inputs it records:
    the repository's event file, and the arrivals kept with the investigation.
    Refuses an input that is not the one recorded."""
    found = []
    for item in revision["inputs"]:
        path = Path(item["path"]) if item["under"] == "repository" else Path(investigation) / item["path"]
        if sha256_file(path) != item["sha256"]:
            raise ValueError(f"{path} is not the input revision {revision['id']} recorded")
        found += load_events(path)
    return found


def dataset_digest(events: list[dict]) -> str:
    """A digest of the records themselves, whatever files they came in."""
    lines = "".join(canonical({k: e[k] for k in FIELDS}) + "\n" for e in sorted(events, key=lambda e: e["transfer_id"]))
    return sha256_text(lines)


def merge_arrival(known: list[dict], arrival: list[dict]) -> tuple[list[dict], list[str], list[str]]:
    """The arrival's new transfers, the ids it repeats exactly, and the ids it
    contradicts. A transfer delivered again unchanged adds nothing. A different
    transfer under a known id is a correction, which this does not support."""
    by_id = {e["transfer_id"]: e for e in known}
    new: dict[str, dict] = {}
    replayed, conflicting = [], []
    for e in arrival:
        seen = by_id.get(e["transfer_id"]) or new.get(e["transfer_id"])
        if seen is None:
            new[e["transfer_id"]] = e
        elif seen == e:
            replayed.append(e["transfer_id"])
        else:
            conflicting.append(e["transfer_id"])
    return list(new.values()), sorted(set(replayed)), sorted(set(conflicting))


def lateness(known: list[dict], new: list[dict], lag_ms: int = LAG_MS) -> list[dict]:
    """Would each new transfer still be accepted, had it been appended to the
    replay of the transfers already known? That replay's last transfer sets its
    watermark to that transfer's event time minus the lag; a transfer at or
    behind it is late. Its potential onward partners' 30-minute intervals, and
    its fan-in hour, are closed once the watermark has passed their end."""
    last = max(e["ts"] for e in known)
    watermark = last - lag_ms
    found = []
    for e in sorted(new, key=lambda e: (e["ts"], e["transfer_id"])):
        partners = []
        for other in known:
            if other["dst"] == e["src"] and 0 <= e["ts"] - other["ts"] <= GAP_MS:      # a credit it would follow
                end = other["ts"] + GAP_MS
                partners.append({"transfer": other["transfer_id"], "as": "credit", "interval_end_ms": end,
                                 "closed": watermark > end})
            if other["src"] == e["dst"] and 0 <= other["ts"] - e["ts"] <= GAP_MS:      # a debit it would precede
                partners.append({"transfer": other["transfer_id"], "as": "debit", "interval_end_ms": other["ts"],
                                 "closed": watermark > other["ts"]})
        hour_end = e["ts"] - e["ts"] % HOUR_MS + HOUR_MS
        found.append({"transfer": e["transfer_id"], "ts": e["ts"], "last_event_ms": last, "watermark_ms": watermark,
                      "behind_ms": watermark - e["ts"], "allowance_ms": lag_ms, "accepted": e["ts"] > watermark,
                      "hour_end_ms": hour_end, "hour_closed": watermark >= hour_end,
                      "partners": sorted(partners, key=lambda p: p["transfer"])})
    return found


# ---------------------------------------------------------------------------
# The rule for the scoped absence, and the checker's verdict on any claim.

def _no_onward_transfer(p: dict, f: Facts) -> tuple[bool, str]:
    if p["account"] not in f.accounts:
        return False, f"{p['account']} is not an account in the dataset"
    found = sorted(link_id for link_id, link in f.links.items()
                   if link["account"] == p["account"] and p["start_ms"] <= f.transfers[link["out_id"]]["ts"] <= p["end_ms"])
    if found:
        return False, "qualifying onward transfer(s) from " + p["account"] + ": " + ", ".join(
            f"{link_id} ({f.links[link_id]['out_id']} at {hms(f.transfers[f.links[link_id]['out_id']]['ts'])})"
            for link_id in found)
    return True, f"no qualifying onward transfer from {p['account']} between {hms(p['start_ms'])} and {hms(p['end_ms'])}"


def shape_error(claim: dict) -> str | None:
    if claim.get("type") not in TYPES:
        return f"claim type {claim.get('type')!r} is not one revision supports"
    predicate = claim.get("predicate")
    if not isinstance(predicate, dict):
        return "the predicate is not an object"
    if claim["type"] != "no_onward_transfer":
        return checker.shape_error({"id": claim.get("id") or "?", "type": claim["type"], **predicate})
    if set(predicate) != set(ABSENCE_FIELDS):
        return f"a no_onward_transfer predicate has exactly the fields {sorted(ABSENCE_FIELDS)}"
    for name, kind in ABSENCE_FIELDS.items():
        if type(predicate[name]) is not kind:
            return f"{name} is not {kind.__name__}"
    if predicate["start_ms"] > predicate["end_ms"]:
        return "the interval ends before it starts"
    return None


def judge(claim: dict, events: Facts, graph: Facts) -> dict:
    """The checker's verdict on one claim, against one revision's two sources:
    supported, unsupported, inconsistent (the sources disagree) or malformed."""
    error = shape_error(claim)
    if error:
        return {"status": "malformed", "events": error, "graph": error}
    if claim["type"] == "no_onward_transfer":
        in_events, why_events = _no_onward_transfer(claim["predicate"], events)
        in_graph, why_graph = _no_onward_transfer(claim["predicate"], graph)
    else:
        rule = checker.RULES[claim["type"]]
        flat = {"id": claim["id"], "type": claim["type"], **claim["predicate"]}
        in_events, why_events = rule(flat, events)
        in_graph, why_graph = rule(flat, graph)
    status = ("supported" if in_events and in_graph else
              "unsupported" if not in_events and not in_graph else "inconsistent")
    return {"status": status, "events": why_events, "graph": why_graph}


# ---------------------------------------------------------------------------
# Dependencies: what a claim cites, and the windows that select it.

def path_transfers(f: Facts, starts: list[str]) -> set[str]:
    """The transfers on the candidate paths from these starts, starts included."""
    following: dict[str, list[str]] = defaultdict(list)
    for link in f.links.values():
        following[link["in_id"]].append(link["out_id"])
    seen, pending = set(starts), list(starts)
    while pending:
        for nxt in following.get(pending.pop(), ()):
            if nxt not in seen:
                seen.add(nxt)
                pending.append(nxt)
    return seen


def _indicator_window(indicator_id: str) -> tuple[str, int, int]:
    _, account, start = indicator_id.split(":")
    return account, int(start), int(start) + HOUR_MS


def window(role: str, account: str, start_ms: int, end_ms: int, via: str) -> dict:
    return {"role": role, "account": account, "start_ms": start_ms, "end_ms": end_ms, "via": via}


def windows(claim: dict, f: Facts) -> list[dict]:
    """The claim's dependency windows at a revision whose facts these are:
    debits from, or credits to, one account inside an event-time interval,
    both ends included. A transfer inside one may change the claim's verdict."""
    kind, p = claim["type"], claim["predicate"]
    found: list[dict] = []
    if kind == "indicator":
        found.append(window("credit", p["account"], p["window_start_ms"], p["window_end_ms"], p["indicator"]))
    elif kind == "onward_path":
        last = f.transfers.get(p["transfers"][-1]) if p["transfers"] else None
        if p["ends_at"] is not None and last is not None:
            found.append(window("debit", last["dst"], last["ts"], last["ts"] + GAP_MS, p["transfers"][-1]))
    elif kind == "onward_reach":
        account, start, end = _indicator_window(p["indicator"])
        found.append(window("credit", account, start, end, p["indicator"]))
        alert = f.indicators.get(p["indicator"])
        for tid in sorted(path_transfers(f, alert["transfer_ids"]) if alert else ()):
            t = f.transfers[tid]
            found.append(window("debit", t["dst"], t["ts"], t["ts"] + GAP_MS, tid))
    elif kind == "no_onward_transfer":
        found.append(window("debit", p["account"], p["start_ms"], p["end_ms"], "search scope"))
        found.append(window("credit", p["account"], p["start_ms"] - GAP_MS, p["end_ms"], "search scope"))
    unique = {canonical(w): w for w in found}
    return sorted(unique.values(), key=lambda w: (w["start_ms"], w["end_ms"], w["role"], w["account"], w["via"]))


def references(claim: dict, f: Facts) -> dict:
    """The evidence a positive claim cites at the revision it is asserted at."""
    kind, p = claim["type"], claim["predicate"]
    cited = {"transfers": set(), "indicators": set(), "links": set()}
    if kind == "event":
        cited["transfers"].add(p["transfer"])
    elif kind == "indicator":
        cited["indicators"].add(p["indicator"])
        cited["transfers"] |= set(p["contributing"])
    elif kind == "onward_path":
        cited["transfers"] |= set(p["transfers"])
        cited["links"] |= {f"onward:{a}:{b}" for a, b in zip(p["transfers"], p["transfers"][1:])}
        if p["from_indicator"] is not None:
            cited["indicators"].add(p["from_indicator"])
    elif kind == "onward_reach":
        cited["indicators"].add(p["indicator"])
        alert = f.indicators.get(p["indicator"])
        on_paths = path_transfers(f, alert["transfer_ids"]) if alert else set()
        cited["transfers"] |= on_paths
        cited["links"] |= {link_id for link_id, link in f.links.items() if link["in_id"] in on_paths}
    return {k: sorted(v) for k, v in cited.items()}


def select(previous_windows: dict[str, list[dict]], new: list[dict]) -> dict[str, list[dict]]:
    """The rule, over records alone: each claim with a window one of the new
    transfers falls into, and the windows it fell into."""
    hits: dict[str, list[dict]] = {}
    for claim_id, claim_windows in previous_windows.items():
        for w in claim_windows:
            for e in new:
                account = e["src"] if w["role"] == "debit" else e["dst"]
                if account == w["account"] and w["start_ms"] <= e["ts"] <= w["end_ms"]:
                    hits.setdefault(claim_id, []).append({"transfer": e["transfer_id"], **w})
    return {k: sorted(v, key=canonical) for k, v in sorted(hits.items(), key=lambda kv: claim_order(kv[0]))}


def claim_order(claim_id: str) -> tuple[str, int]:
    prefix = claim_id.rstrip("0123456789")
    return prefix, int(claim_id[len(prefix):] or 0)


# ---------------------------------------------------------------------------
# The deterministic investigator: the findings a revision's evidence supports,
# written from the graph's facts. No model.

def _alert_claims(indicator_id: str, f: Facts) -> list[dict]:
    i = f.indicators[indicator_id]
    return [{"type": "indicator", "predicate": {
        "indicator": indicator_id, "account": i["account"], "window_start_ms": i["window_start"],
        "window_end_ms": i["window_end"], "senders": i["senders"], "transfers": i["transfers"],
        "total_minor": i["total_minor"], "contributing": list(i["transfer_ids"])}}]


def path_ends(indicator_id: str, f: Facts) -> list[str]:
    """The transfers where the alert's candidate paths end: reached by an onward
    link and followed by none. With no path at all, its contributing transfers."""
    alert = f.indicators[indicator_id]
    on_paths = path_transfers(f, alert["transfer_ids"])
    reached = {link["out_id"] for link in f.links.values() if link["in_id"] in on_paths}
    ends = sorted(t for t in reached if not f.links_from(t))
    return ends or sorted(alert["transfer_ids"])


def _paths_claims(indicator_id: str, f: Facts) -> list[dict]:
    inv = f.investigation[indicator_id]
    found = [{"type": "onward_reach", "predicate": {
        "indicator": indicator_id, "max_depth": inv["onward_depth"],
        "terminal_accounts": list(inv["terminal_accounts"]), "route_accounts": list(inv["route_accounts"])}}]
    seen = set()
    for tid in sorted(path_ends(indicator_id, f), key=lambda t: (f.transfers[t]["ts"], t)):
        t = f.transfers[tid]
        key = (t["dst"], t["ts"])
        if key not in seen:
            seen.add(key)
            found.append({"type": "no_onward_transfer", "basis": tid, "predicate": {
                "account": t["dst"], "start_ms": t["ts"], "end_ms": t["ts"] + GAP_MS}})
    return found


def _alert_statement(indicator_id: str, f: Facts, revision: str) -> str:
    i = f.indicators[indicator_id]
    return (f"{indicator_id}: {i['senders']} distinct senders paid {i['account']} {money(i['total_minor'])} in "
            f"{i['transfers']} transfers between {hms(i['window_start'])} and {hms(i['window_end'])} UTC on "
            f"{day(i['window_start'])}, by event time, in evidence revision {revision}.")


def _paths_statement(indicator_id: str, f: Facts, absences: list[dict], revision: str) -> str:
    inv = f.investigation[indicator_id]
    days = {day(a["predicate"]["start_ms"]) for a in absences} | {day(a["predicate"]["end_ms"]) for a in absences}
    one_day = len(days) == 1
    scopes = [f"from {a['predicate']['account']} between {hms(a['predicate']['start_ms'])} and "
              f"{hms(a['predicate']['end_ms'])}{'' if one_day else ' on ' + day(a['predicate']['start_ms'])}, "
              f"the 30 minutes after {a['basis']} paid it" for a in absences]
    when = f" (UTC, {days.pop()})" if one_day else " (UTC)"
    if inv["onward_depth"] == 0:
        return (f"No contributing transfer of {indicator_id} starts a candidate onward-transfer path: in evidence "
                f"revision {revision} there is no qualifying onward transfer " + "; or ".join(scopes) + when + ".")
    return (f"From {indicator_id} the candidate onward-transfer paths run at most {links_text(inv['onward_depth'])} and end at "
            f"{', '.join(inv['terminal_accounts'])}: in evidence revision {revision} there is no qualifying onward "
            "transfer " + "; or ".join(scopes) + when + ".")


def investigate(f: Facts, revision: str) -> list[tuple[dict, list[dict]]]:
    """Every alert's two findings, about the alert and about its paths, each
    with the claims it rests on (ids not yet assigned)."""
    found = []
    for indicator_id in sorted(f.indicators):
        found.append(({"about": "alert", "subject": indicator_id,
                       "statement": _alert_statement(indicator_id, f, revision)}, _alert_claims(indicator_id, f)))
        paths = _paths_claims(indicator_id, f)
        absences = [c for c in paths if c["type"] == "no_onward_transfer"]
        found.append(({"about": "paths", "subject": indicator_id,
                       "statement": _paths_statement(indicator_id, f, absences, revision)}, paths))
    return found


def restate(finding: dict, f: Facts, revision: str, new_ids: set[str], new_links: list[str]) -> tuple[dict, list[dict]]:
    """A superseded finding written again from a later revision's facts, with
    the new evidence it rests on: for an alert, each new contributing transfer;
    for its paths, each new onward link on them, one candidate path through it,
    and the new transfers at its ends."""
    indicator_id = finding["subject"]
    alert = f.indicators[indicator_id]
    sentences, extra = [], []
    if finding["about"] == "alert":
        drafts = _alert_claims(indicator_id, f)
        statement = _alert_statement(indicator_id, f, revision)
        arrived = sorted(set(alert["transfer_ids"]) & new_ids)
        if arrived:
            sentences.append(f"New in {revision}: {', '.join(arrived)}, contributing to it.")
    else:
        drafts = _paths_claims(indicator_id, f)
        statement = _paths_statement(indicator_id, f, [c for c in drafts if c["type"] == "no_onward_transfer"], revision)
        on_paths = path_transfers(f, alert["transfer_ids"])
        arrived = set()
        for link_id in sorted(l for l in new_links if f.links[l]["in_id"] in on_paths):
            link = f.links[link_id]
            credit, debit = f.transfers[link["in_id"]], f.transfers[link["out_id"]]
            path = _one_path(f, set(alert["transfer_ids"]), on_paths, link_id)
            sentences.append(
                f"New in {revision}: {link_id}, from {link['in_id']} (paid {credit['dst']} at {hms(credit['ts'])}) to "
                f"{link['out_id']} ({debit['src']} to {debit['dst']}, {money(debit['amount_minor'])}, at "
                f"{hms(debit['ts'])}), {duration(link['gap_ms'])} apart; one candidate path through it runs "
                f"{', '.join(path)}.")
            extra.append({"type": "onward_path", "predicate": {
                "transfers": path, "from_indicator": indicator_id,
                "ends_at": None if f.links_from(path[-1]) else f.transfers[path[-1]]["dst"]}})
            arrived |= {link["in_id"], link["out_id"]} & new_ids
        arrived = sorted(arrived)
    for tid in arrived:
        t = f.transfers[tid]
        extra.append({"type": "event", "predicate": {
            "transfer": tid, "sender": t["src"], "receiver": t["dst"], "amount_minor": t["amount_minor"],
            "event_time_ms": t["ts"], "device": t["device"]}})
    return ({"about": finding["about"], "subject": indicator_id, "statement": " ".join([statement, *sentences])},
            drafts + extra)


def _one_path(f: Facts, starts: set[str], on_paths: set[str], link_id: str) -> list[str]:
    """The first candidate path, in id order, from a start through the link to
    a transfer with no onward link (or until it would repeat a transfer)."""
    into: dict[str, list[str]] = defaultdict(list)
    for link in f.links.values():
        if link["in_id"] in on_paths:
            into[link["out_id"]].append(link["in_id"])
    path = [f.links[link_id]["in_id"], f.links[link_id]["out_id"]]
    while path[0] not in starts and into.get(path[0]):
        earlier = [t for t in sorted(into[path[0]]) if t not in path]
        if not earlier:
            break
        path.insert(0, earlier[0])
    while True:
        later = [l["out_id"] for l in f.links_from(path[-1]) if l["out_id"] not in path]
        if not later:
            return path
        path.append(sorted(later)[0])


# ---------------------------------------------------------------------------
# The ledger: the published investigation, one JSON record per line, each
# naming the sha256 of the line before it. Only ever appended to, and only by
# a publication, which is the line that names the revision's store.

class LedgerError(Exception):
    pass


def line_hash(line: str) -> str:
    return sha256_text(line)


class Ledger:
    def __init__(self, path: Path) -> None:
        self.path = Path(path)
        self.lines: list[str] = self.path.read_text().splitlines() if self.path.exists() else []
        self.records: list[dict] = []
        prev = None
        for number, line in enumerate(self.lines, start=1):
            record = json.loads(line)
            if record.get("seq") != number or record.get("prev") != prev:
                raise LedgerError(f"{self.path}:{number}: the hash chain is broken")
            self.records.append(record)
            prev = line_hash(line)

    # -- reading
    def of(self, kind: str) -> list[dict]:
        return [r for r in self.records if r["kind"] == kind]

    def published(self) -> dict | None:
        found = self.of("publication")
        return found[-1] if found else None

    def revision(self, revision_id: str) -> dict:
        return next(r for r in self.of("revision") if r["id"] == revision_id)

    def claims(self) -> dict[str, dict]:
        return {r["id"]: r for r in self.of("claim")}

    def claim_by_digest(self, digest: str) -> dict | None:
        return next((r for r in self.of("claim") if r["digest"] == digest), None)

    def findings(self) -> dict[str, dict]:
        return {r["id"]: r for r in self.of("finding")}

    def current_findings(self) -> list[dict]:
        """Findings no amendment has superseded, in the order they were made."""
        gone = {s["finding"] for a in self.of("amendment") for s in a["superseded"]}
        return [r for r in self.of("finding") if r["id"] not in gone]

    def validation(self, claim_id: str, revision_id: str) -> dict | None:
        return next((r for r in self.of("validation") if r["claim"] == claim_id and r["revision"] == revision_id), None)

    def history(self, claim_id: str) -> list[dict]:
        return [r for r in self.of("validation") if r["claim"] == claim_id]

    def through(self, revision_id: str) -> list[dict]:
        """Every record up to and including that revision's publication."""
        end = next(i for i, r in enumerate(self.records)
                   if r["kind"] == "publication" and r["revision"] == revision_id)
        return self.records[:end + 1]

    def next_id(self, prefix: str, taken: list[dict] = ()) -> str:
        used = [r["id"] for r in [*self.records, *taken] if isinstance(r.get("id"), str) and r["id"].startswith(prefix)
                and r["id"][len(prefix):].isdigit()]
        return f"{prefix}{max((int(u[len(prefix):]) for u in used), default=0) + 1}"

    # -- the one way to write: append records and commit them atomically
    def append(self, records: list[dict]) -> None:
        lines = list(self.lines)
        prev = line_hash(lines[-1]) if lines else None
        for record in records:
            body = {"seq": len(lines) + 1, "prev": prev, **{k: v for k, v in record.items() if k not in ("seq", "prev")}}
            line = json.dumps(body, ensure_ascii=False)
            lines.append(line)
            prev = line_hash(line)
        partial = self.path.with_name(f"{self.path.name}.writing.{os.getpid()}")
        with open(partial, "w") as out:
            out.write("".join(line + "\n" for line in lines))
            out.flush()
            os.fsync(out.fileno())
        os.replace(partial, self.path)
        self.__init__(self.path)


def claim_digest(kind: str, predicate: dict) -> str:
    return sha256_text(canonical({"type": kind, "predicate": predicate}))[:16]


def scope_record(predicate: dict, basis: str | None, revision: dict) -> dict:
    """What an absence searched: which account, which relationship, which
    event-time interval, over which dataset."""
    return {"entity": {"account": predicate["account"]}, "pattern": ABSENCE_PATTERN,
            "interval": {"start_ms": predicate["start_ms"], "end_ms": predicate["end_ms"], "bounds": "both included"},
            "basis": f"the 30 minutes after {basis} paid {predicate['account']}" if basis else None,
            "coverage": {"revision": revision["id"], "dataset_sha256": revision["dataset_sha256"],
                         "events": revision["events"]}}


def assert_claims(ledger: Ledger, drafts: list[dict], revision: dict, f: Facts, taken: list[dict]) -> list[str]:
    """Claim records for the drafts, new ids for new predicates and the existing
    id for a predicate already claimed; returns their ids. New records are
    appended to taken."""
    ids = []
    for draft in drafts:
        digest = claim_digest(draft["type"], draft["predicate"])
        existing = ledger.claim_by_digest(digest) or next(
            (r for r in taken if r["kind"] == "claim" and r["digest"] == digest), None)
        if existing:
            ids.append(existing["id"])
            continue
        record = {"kind": "claim", "id": ledger.next_id("C", taken), "type": draft["type"],
                  "revision": revision["id"], "predicate": draft["predicate"], "digest": digest}
        if draft["type"] == "no_onward_transfer":
            record["scope"] = scope_record(draft["predicate"], draft.get("basis"), revision)
        else:
            record["references"] = references(draft, f)
        taken.append(record)
        ids.append(record["id"])
    return ids


def validation_record(claim: dict, revision: str, verdict: dict, method: str, f: Facts,
                      full: dict | None = None, selected_by: list[dict] | None = None) -> dict:
    record = {"kind": "validation", "id": f"{claim['id']}@{revision}", "claim": claim["id"], "revision": revision,
              "status": verdict["status"], "method": method, "events": verdict["events"], "graph": verdict["graph"],
              "windows": windows(claim, f)}
    if full is not None:
        record["full_recheck"] = full["status"]
    if selected_by is not None:
        record["selected_by"] = selected_by
    return record
