#!/usr/bin/env python3
"""Evidence-driven revision of investigative findings, as a staged evolving
investigation: two bounded replays, run end to end. No model and no API key;
needs Docker (clink runs from the pinned runtime image) and the venv.

  .venv/bin/python revise.py

Stage 1, evidence revision r1: clink replays data/events.ndjson through
pipeline/revision.sql, nothing arrived yet, into a Relate store. The store is
published only when clink exited 0, every record of the dataset is in it as
written, and its indicators and onward links equal the independent reference.
A case note is written from its evidence and every claim checked.

Stage 2, evidence revision r2: data/arrival.ndjson arrives. Its event time is
checked against the lateness the pipeline allows, and the revision is a
bounded recomputation: clink replays revision 1's file and the arrival as two
inputs, merged by event time. The same gates apply. The claims whose
dependency windows a new transfer falls into are selected, by a query in
Relate and by the same rule over the ledger, which must agree; they are
checked again, and so is every claim, and the two must agree too. A finding
whose claims no longer hold is superseded by an amendment, with a replacement
finding checked at r2. Nothing earlier is rewritten. A refused update
publishes nothing, and the previous revision stays the published one.

Prints what the investigation said before, what arrived and what it changed,
and what it says after. Exit status 0 when the investigation is published or
the arrival adds nothing; 1 when an update is refused.

  --out DIR            publish into DIR (default build/revision, replaced on each run)
  --continue           DIR already holds a published investigation: apply the arrival to it
  --arrival FILE       the delivery that arrives (default data/arrival.ndjson)
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import textwrap
from pathlib import Path

import relate

from alertcase import facts
from alertcase import revision as rv
from alertcase import revision_store as rs
from alertcase.events import load_events
from alertcase.graph import Graph

ROOT = Path(__file__).resolve().parent
IMAGE = "ghcr.io/orhaugh/clink-runtime:0.16.2@sha256:da007cf3f288497a05447ae6d9d65914d0a31471b929cc38af02e297971b1fd8"
PIPELINE = Path("pipeline/revision.sql")
FIRST = Path("data/events.ndjson")
ARRIVAL = Path("data/arrival.ndjson")
STAGING = Path("build/revision-stage")
DEFAULT_OUT = Path("build/revision")
SCOPE_NOTE = (
    "Scope: bounded replays of a synthetic event file and what arrived after it, each conclusion relative to the "
    "evidence revision it names. Nothing here is a conclusion about data outside those revisions, and recorded "
    "relationships are not proof of fraud, ownership, identity or causation. An onward link records timing: a "
    "debit within 30 minutes after a credit to the same account. It is a candidate onward-transfer relationship, "
    "not evidence that the same funds moved, and a path ends where no further qualifying transfer exists in that "
    "revision. A shared device is context, not proof of ownership or fraud. The checker validates the structured "
    "claims against the original events and the graph of each revision; it does not validate the wording of "
    "findings.")


class Refused(Exception):
    """An update that must publish nothing."""


# ---------------------------------------------------------------------------
# Running clink

def docker_clink(stage: Path) -> tuple[int, str]:
    """The pinned image runs the staged pipeline: no network, the stage mounted."""
    done = subprocess.run(["docker", "run", "--rm", "--network", "none", "--user", f"{os.getuid()}:{os.getgid()}",
                           "-v", f"{stage.resolve()}:/work", "-w", "/work", IMAGE, "run", str(PIPELINE)],
                          capture_output=True, text=True)
    return done.returncode, done.stdout + done.stderr


def stage_run(name: str, recorded: str, arrived: str, runner) -> tuple[int, str, Path]:
    """Stages the two inputs and the pipeline in a directory of their own, and
    runs clink there. Returns its exit status, what it printed and the store.
    Each run gets a new directory: Docker Desktop's file sharing can still see
    a directory removed and made again at the same path a moment before."""
    STAGING.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix=f"{name}-", dir=STAGING))
    for sub in ("data", "pipeline", "store"):
        (stage / sub).mkdir(parents=True)
    (stage / "data" / "events.ndjson").write_text(recorded)
    (stage / "data" / "arrived.ndjson").write_text(arrived)
    shutil.copyfile(PIPELINE, stage / PIPELINE)
    status, log = runner(stage)
    (stage / "clink-run.log").write_text(log)
    return status, log, stage / "store" / "evidence.building.rl"


def gate_clink(status: int, log: str) -> None:
    if status != 0:
        raise Refused(f"clink exited {status}: not every job ended without error")
    if "stopping: cancelling" in log:
        raise Refused("the run was cancelled, so its jobs did not all complete")


def gate_evidence(store: Path, dataset: list[dict]) -> tuple[int, facts.Facts]:
    if not store.exists():
        raise Refused("clink wrote no store")
    with Graph(store) as graph:
        if graph.run_records():
            raise Refused("the store already holds a run record")
        reconciled, differences = rs.evidence_check(graph, dataset)
        if differences:
            raise Refused("the store's evidence differs from the dataset and the reference rules: "
                          + "; ".join(differences))
        return reconciled, facts.from_graph(graph)


# ---------------------------------------------------------------------------
# The record of a revision

def input_record(under: str, path: Path, base: Path) -> dict:
    return {"under": under, "path": str(path), "sha256": rv.sha256_file(base / path),
            "events": len(load_events(base / path))}


def dataset_of(out: Path, revision: dict) -> list[dict]:
    try:
        return rv.dataset_of(out, revision)
    except ValueError as error:
        raise Refused(str(error)) from None


def revision_record(rid: str, parent: str | None, inputs: list[dict], arrived: list[str], dataset: list[dict],
                    reconciled: int, graph: facts.Facts, event_time: dict, new_links: list[str],
                    changed_indicators: list[str]) -> dict:
    digest = rv.dataset_digest(dataset)
    return {"kind": "revision", "id": rid, "parent": parent, "inputs": inputs, "arrived": arrived,
            "dataset_sha256": digest, "events": len(dataset),
            "pipeline": {"path": str(PIPELINE), "sha256": rv.sha256_file(PIPELINE)}, "clink": IMAGE,
            "clink_exit_status": 0, "cancelled": False, "jobs": 3, "jobs_completed": 3,
            "reconciled": [reconciled, len(dataset)],
            "evidence": {"transfers": len(graph.transfers), "indicators": len(graph.indicators),
                         "onward_links": len(graph.links), "equals_reference": True},
            "new_links": new_links, "changed_indicators": changed_indicators, "event_time": event_time,
            "run": f"run:{digest[:12]}"}


def gate_written(store: Path, dataset: list[dict], records: list[dict]) -> None:
    """The last gate before publication: with the investigation written beside
    it, the store's evidence still equals the reference, and the investigation
    in it equals the records about to be published."""
    with Graph(store) as graph:
        _, differences = rs.evidence_check(graph, dataset)
        held = rs.layer(graph)
    if differences:
        raise Refused("with the investigation written beside it, the store's evidence differs: " + "; ".join(differences))
    want = rs.layer_from_records(records)
    if held != want:
        raise Refused(f"the investigation in the store differs from its records: {[k for k in want if held[k] != want[k]]}")


def write_store(store: Path, records: list[dict], revision: dict | None = None) -> None:
    conn = relate.connect(str(store))
    try:
        rs.write_records(conn, records)
        if revision is not None:
            rs.write_run(conn, revision, IMAGE, rv.LAG_MS, rv.GAP_MS)
    finally:
        conn.close()


def publish(out: Path, ledger: rv.Ledger, records: list[dict], rid: str, store: Path, note: tuple[str, str],
            arrival: list[dict] | None = None) -> None:
    """The last step, in this order: the store moves to its published path, the
    arrival and the note are written, and then the ledger's records are
    appended, the publication last. Until that append the published
    investigation is the one before: a file written before it is not named by
    any publication, and the next run replaces it."""
    os.replace(store, out / f"{rid}.rl")
    shutil.rmtree(store.parent.parent, ignore_errors=True)
    if arrival is not None:
        (out / "arrivals").mkdir(exist_ok=True)
        (out / "arrivals" / f"{rid}.ndjson").write_text("".join(json.dumps(e, separators=(",", ":")) + "\n"
                                                              for e in arrival))
    (out / note[0]).write_text(note[1])
    ledger.append([*records, {"kind": "publication", "revision": rid, "store": f"{rid}.rl",
                              "store_sha256": rv.sha256_file(out / f"{rid}.rl"), "note": note[0],
                              "note_sha256": rv.sha256_file(out / note[0])}])


# ---------------------------------------------------------------------------
# Stage 1: the initial bounded replay, and a checked case note

def initial(out: Path, runner=docker_clink) -> dict:
    out.mkdir(parents=True, exist_ok=True)
    ledger = rv.Ledger(out / "ledger.jsonl")
    if ledger.records:
        raise Refused(f"{out} already holds an investigation; use --continue to apply an arrival to it")
    dataset = load_events(FIRST)
    status, log, store = stage_run("r1", FIRST.read_text(), "", runner)
    gate_clink(status, log)
    reconciled, graph = gate_evidence(store, dataset)
    reference = facts.from_records(dataset)
    revision = revision_record("r1", None, [input_record("repository", FIRST, Path("."))], [], dataset, reconciled,
                               graph, {"decision": "the initial bounded replay"}, [], [])
    pending: list[dict] = []
    findings = []
    for finding, drafts in rv.investigate(graph, "r1"):
        ids = rv.assert_claims(ledger, drafts, revision, graph, pending)
        findings.append({"kind": "finding", "id": ledger.next_id("F", [*pending, *findings]), "revision": "r1",
                         **finding, "claims": ids, "replaces": None})
    claims = [r for r in pending if r["kind"] == "claim"]
    validations = []
    for claim in claims:
        verdict = rv.judge(claim, reference, graph)
        if verdict["status"] != "supported":
            raise Refused(f"the case note's claim {claim['id']} is {verdict['status']}: {verdict['events']}")
        validations.append(rv.validation_record(claim, "r1", verdict, "asserted", graph, full=verdict))
    records = [revision, *claims, *findings, *validations]
    write_store(store, records, revision)
    gate_written(store, dataset, records)
    publish(out, ledger, records, "r1", store, ("r1-case-note.md", case_note(records)))
    return {"revision": revision, "status": status}


# ---------------------------------------------------------------------------
# Stage 2: an arrival, a bounded recomputation, selection and amendment

def apply(out: Path, arrival_path: Path, runner=docker_clink, append_to_stream: bool = False) -> dict:
    """Applies an arrival to the investigation published in out: nothing when
    it holds nothing new, otherwise a new revision, published only through
    every gate, with an amendment when a finding no longer holds.

    append_to_stream is a control for the tests, not a way to make a revision:
    the arrival goes after the published revision's transfers in one input, as
    a continuing stream would read it. It is late there, and whether clink
    pairs it then varies from run to run; the gates must refuse whenever the
    evidence is not whole."""
    ledger = rv.Ledger(out / "ledger.jsonl")
    published = ledger.published()
    if published is None:
        raise Refused(f"{out} holds no published investigation")
    previous = ledger.revision(published["revision"])
    known = dataset_of(out, previous)
    arrival = load_events(arrival_path, unique=False)
    new, replayed, conflicting = rv.merge_arrival(known, arrival)
    if conflicting:
        raise Refused(f"the arrival holds a different transfer under a known id: {conflicting}; a correction of an "
                      "existing transfer is not supported")
    if not new:
        return {"outcome": "nothing new", "arrival": arrival_path, "replayed": replayed, "previous": previous}
    rid = ledger.next_id("r")
    dataset = known + new
    new_ids = {e["transfer_id"] for e in new}
    late = rv.lateness(known, new)
    earlier = "".join((out / i["path"]).read_text() for i in previous["inputs"] if i["under"] == "investigation")
    arrived = earlier + "".join(json.dumps(e, separators=(",", ":")) + "\n" for e in new)
    if append_to_stream:
        status, log, store = stage_run(rid, FIRST.read_text() + arrived, "", runner)
    else:
        status, log, store = stage_run(rid, FIRST.read_text(), arrived, runner)
    gate_clink(status, log)
    reconciled, graph = gate_evidence(store, dataset)
    reference = facts.from_records(dataset)
    with Graph(out / published["store"]) as g:
        before = facts.from_graph(g)
    new_links = sorted(set(graph.links) - set(before.links))
    reference_links = sorted(set(reference.links) - set(facts.from_records(known).links))
    if new_links != reference_links:
        raise Refused(f"the new onward links {new_links} differ from the reference's {reference_links}")
    changed = sorted(i for i in graph.indicators if before.indicators.get(i) != graph.indicators[i])
    event_time = {"lateness": late, "previous_jobs_completed": True,
                  "decision": "bounded recomputation" if not append_to_stream else "appended to the stream (control)",
                  "inputs": "data/events.ndjson and every arrival since, as two inputs merged by event time in clink"
                  if not append_to_stream else "data/events.ndjson with the arrivals appended, one input"}
    inputs = [*previous["inputs"], {"under": "investigation", "path": f"arrivals/{rid}.ndjson",
                                    "sha256": rv.sha256_text("".join(json.dumps(e, separators=(",", ":")) + "\n"
                                                                     for e in new)), "events": len(new)}]
    revision = revision_record(rid, previous["id"], inputs, sorted(new_ids), dataset, reconciled, graph, event_time,
                               new_links, changed)

    # The investigation as published, and the new revision, go into the new store first.
    write_store(store, [*ledger.through(previous["id"]), revision])
    claims = ledger.claims()
    with Graph(store) as g:
        in_store = rs.selected_in_store(g, rid, previous["id"])
    by_rule = rv.select({cid: ledger.validation(cid, previous["id"])["windows"] for cid in claims}, new)
    if normalised(in_store) != normalised(by_rule):
        raise Refused(f"the dependency query in Relate selected {sorted(in_store)}, the rule over the ledger "
                      f"{sorted(by_rule)}")

    # Incremental: check the selected claims again, carry the rest. Full: check every claim. They must agree.
    was = {cid: ledger.validation(cid, previous["id"])["status"] for cid in claims}
    incremental = {cid: rv.judge(c, reference, graph)["status"] if cid in by_rule else was[cid]
                   for cid, c in claims.items()}
    full = {cid: rv.judge(c, reference, graph) for cid, c in claims.items()}
    differ = sorted((cid for cid in claims if incremental[cid] != full[cid]["status"]), key=rv.claim_order)
    if differ:
        raise Refused(f"incremental revalidation and a full recheck differ for {differ}")
    torn = sorted((cid for cid, v in full.items() if v["status"] in ("inconsistent", "malformed")), key=rv.claim_order)
    if torn:
        raise Refused(f"the events and the graph disagree about {torn}")
    validations = [rv.validation_record(c, rid, {**full[cid], "status": incremental[cid]},
                                        "revalidated" if cid in by_rule else "carried", graph, full=full[cid],
                                        selected_by=by_rule.get(cid, []))
                   for cid, c in sorted(claims.items(), key=lambda kv: rv.claim_order(kv[0]))]
    selection = {"kind": "selection", "revision": rid, "previous": previous["id"], "selected": by_rule,
                 "not_selected": [cid for cid in sorted(claims, key=rv.claim_order) if cid not in by_rule],
                 "query_agrees_with_rule": True, "claims": len(claims),
                 "incremental_equals_full": True}

    # Findings whose claims no longer hold are superseded; the rest stand.
    turned = {cid for cid in claims if incremental[cid] != was[cid]}
    pending: list[dict] = []
    findings, superseded, unchanged = [], [], []
    for finding in ledger.current_findings():
        if not set(finding["claims"]) & turned:
            unchanged.append({"finding": finding["id"], "claims": [
                {"claim": cid, "status": incremental[cid], "how": "revalidated" if cid in by_rule else "carried"}
                for cid in finding["claims"]]})
            continue
        restated, drafts = rv.restate(finding, graph, rid, new_ids, new_links)
        ids = rv.assert_claims(ledger, drafts, revision, graph, pending)
        replacement = {"kind": "finding", "id": ledger.next_id("F", [*pending, *findings]), "revision": rid,
                       **restated, "claims": ids, "replaces": finding["id"]}
        findings.append(replacement)
        superseded.append({"finding": finding["id"], "revision": finding["revision"], "claims": [
            {"claim": cid, "at_previous": was[cid], "at_new": incremental[cid], "reason": full[cid]["events"]}
            for cid in finding["claims"]], "replacement": replacement["id"]})
    asserted = [r for r in pending if r["kind"] == "claim"]
    new_validations = []
    for claim in asserted:
        verdict = rv.judge(claim, reference, graph)
        if verdict["status"] != "supported":
            raise Refused(f"replacement claim {claim['id']} is {verdict['status']} at {rid}: {verdict['events']}")
        new_validations.append(rv.validation_record(claim, rid, verdict, "asserted", graph, full=verdict))
    for replacement in findings:  # a replacement may also cite a claim already made; it must hold at rid too
        failing = [cid for cid in replacement["claims"] if cid in incremental and incremental[cid] != "supported"]
        if failing:
            raise Refused(f"replacement finding {replacement['id']} cites {failing}, which do not hold at {rid}")
    records = [revision, selection, *validations, *asserted, *new_validations, *findings]
    if superseded:
        records.append({"kind": "amendment", "id": ledger.next_id("A"), "from": previous["id"], "to": rid,
                        "new_events": sorted(new, key=lambda e: e["transfer_id"]),
                        "changes": {"links": new_links, "indicators": changed},
                        "superseded": superseded, "unchanged": unchanged,
                        "selected": list(by_rule), "incremental_equals_full": True})
    write_store(store, records[1:], revision)
    gate_written(store, dataset, [*ledger.through(previous["id"]), *records])
    view_ledger = _with(ledger, records)
    note = (f"{rid}-amendment.md", amendment_note(view_ledger, records[-1], out)) if superseded else \
        (f"{rid}-revalidation.md", revalidation_note(view_ledger, rid))
    publish(out, ledger, records, rid, store, note, new)
    return {"outcome": "published", "revision": revision, "replayed": replayed}


def normalised(hits: dict[str, list[dict]]) -> set:
    return {(claim, h["transfer"], h["role"], h["account"], h["start_ms"], h["end_ms"], h["via"])
            for claim, found in hits.items() for h in found}


def _with(ledger: rv.Ledger, records: list[dict]) -> rv.Ledger:
    """The ledger as it will read once these records are appended, without writing them."""
    view = rv.Ledger.__new__(rv.Ledger)
    view.path, view.lines = ledger.path, ledger.lines
    view.records = [*ledger.records, *records]
    return view


# ---------------------------------------------------------------------------
# Notes, written once each and never rewritten

def claim_text(claim: dict) -> str:
    p = claim["predicate"]
    if claim["type"] == "no_onward_transfer":
        s = claim["scope"]
        return (f"no qualifying onward transfer from {p['account']} between {rv.hms(p['start_ms'])} and "
                f"{rv.hms(p['end_ms'])} UTC, {rv.day(p['start_ms'])} ({s['basis']}); searched: onward links into a "
                f"debit sent by {p['account']} inside the interval, both ends included, over revision "
                f"{s['coverage']['revision']} ({s['coverage']['events']} transfers)")
    if claim["type"] == "onward_reach":
        return (f"{p['indicator']}: at most {rv.links_text(p['max_depth'])}, paths end at "
                f"{', '.join(p['terminal_accounts'])}, path accounts {', '.join(p['route_accounts'])}")
    if claim["type"] == "indicator":
        return (f"{p['indicator']}: {p['senders']} senders, {p['transfers']} transfers, total "
                f"{rv.money(p['total_minor'])}, contributing {', '.join(p['contributing'])}")
    if claim["type"] == "onward_path":
        end = f", ends at {p['ends_at']}" if p["ends_at"] else ""
        return f"path {' > '.join(p['transfers'])} from {p['from_indicator']}{end}"
    return (f"{p['transfer']}: {p['sender']} to {p['receiver']}, {rv.money(p['amount_minor'])} at "
            f"{rv.hms(p['event_time_ms'])} UTC, device {p['device']}")


def via_text(claim: str, via: str) -> str:
    if via == "search scope":
        return f"{claim}'s search scope"
    if via.startswith("fan_in:"):
        return f"the window of {via}"
    return f"the 30 minutes after {via}"


def hit_text(claim: str, h: dict) -> str:
    return (f"{h['transfer']} is a {h['role']} {'from' if h['role'] == 'debit' else 'to'} {h['account']} inside "
            f"{rv.hms(h['start_ms'])}-{rv.hms(h['end_ms'])}, {via_text(claim, h['via'])}")


def windows_text(windows: list[dict]) -> str:
    return "; ".join(f"{'debits from' if w['role'] == 'debit' else 'credits to'} {w['account']} "
                     f"{rv.hms(w['start_ms'])}-{rv.hms(w['end_ms'])}" for w in windows)


def header(revision: dict) -> str:
    inputs = " and ".join(f"`{i['path']}` ({i['events']} transfer{'s' if i['events'] != 1 else ''})"
                          for i in revision["inputs"])
    total = f", {revision['events']} transfers in all" if len(revision["inputs"]) > 1 else ""
    how = ("the initial bounded replay" if revision["parent"] is None else
           f"a bounded recomputation following {revision['parent']}")
    return (f"Evidence revision {revision['id']}, {how}: {inputs}{total}, dataset sha256 "
            f"{revision['dataset_sha256'][:12]}..., through `{revision['pipeline']['path']}`. clink exited 0 with "
            f"{revision['jobs_completed']} of {revision['jobs']} jobs completed; {revision['reconciled'][0]} of "
            f"{revision['reconciled'][1]} records reconciled, and the derived indicators and onward links equal the "
            "independent reference.")


def case_note(records: list[dict]) -> str:
    revision = records[0]
    claims = {r["id"]: r for r in records if r["kind"] == "claim"}
    verdicts = {r["claim"]: r for r in records if r["kind"] == "validation"}
    lines = [f"# Case note, evidence revision {revision['id']}", "", header(revision), "",
             "Written by `revise.py` from the evidence in Relate, with no model. Each claim was checked against the "
             "original events and the graph of this revision.", "", SCOPE_NOTE, "", "## Findings", ""]
    for f in (r for r in records if r["kind"] == "finding"):
        lines.append(f"- **{f['id']}** {f['statement']}  ")
        lines.append("  Claims: " + ", ".join(f"{c} ({verdicts[c]['status']} at {revision['id']})" for c in f["claims"]))
    lines += ["", f"## Claims, as checked at {revision['id']}", "",
              "| Claim | Type | Asserts | Depends on | Checker |", "|---|---|---|---|---|"]
    for cid, c in claims.items():
        lines.append(f"| {cid} | {c['type']} | {claim_text(c)} | {windows_text(verdicts[cid]['windows']) or 'none'} "
                     f"| {verdicts[cid]['status']} |")
    return "\n".join(lines) + "\n"


def event_time_text(revision: dict) -> list[str]:
    found = []
    for late in revision["event_time"]["lateness"]:
        behind = [p for p in late["partners"] if p["closed"]]
        intervals = "".join(f", and {p['transfer']}'s 30-minute onward interval, which it falls in, ended at "
                            f"{rv.hms(p['interval_end_ms'])}, also behind it" for p in behind if p["as"] == "credit")
        found.append(
            f"{late['transfer']} has event time {rv.hms(late['ts'])}. The last transfer revision {revision['parent']}'s "
            f"replay read, at {rv.hms(late['last_event_ms'])}, put the watermark at {rv.hms(late['watermark_ms'])} "
            f"(the pipeline allows {late['allowance_ms'] // 60000} minutes). "
            + (f"Appended to that stream, {late['transfer']} would be {rv.duration(late['behind_ms'])} behind the "
               f"watermark, far beyond that allowance{intervals}. A transfer that late has no guarantee of being paired."
               if not late["accepted"] else
               f"Appended to that stream, {late['transfer']} would be ahead of the watermark, within the allowance."))
    found.append(f"{revision['parent']}'s jobs have completed in any case: a bounded replay ends with its input, and its "
                 "state with it, so nothing can be appended to it.")
    return found


def amendment_note(ledger: rv.Ledger, amendment: dict, out: Path) -> str:
    revision = ledger.revision(amendment["to"])
    claims, findings = ledger.claims(), ledger.findings()
    first_note = next(p for p in ledger.of("publication") if p["revision"] == amendment["from"])
    lines = [f"# Amendment {amendment['id']}: evidence revision {amendment['from']} to {amendment['to']}", "",
             f"This amends the investigation published at {amendment['from']} (`{first_note['note']}`, sha256 "
             f"{first_note['note_sha256'][:12]}...), which stays as it was written. A claim supported at "
             f"{amendment['from']} remains supported relative to {amendment['from']}; this records whether it still "
             f"applies at {amendment['to']}.", "", header(revision), "", SCOPE_NOTE, "",
             "## What arrived", "", "| Transfer | From | To | Amount | Event time (UTC) | Device |", "|---|---|---|---|---|---|"]
    for e in amendment["new_events"]:
        lines.append(f"| {e['transfer_id']} | {e['src']} | {e['dst']} | {rv.money(e['amount_minor'])} | "
                     f"{rv.hms(e['ts'])}, {rv.day(e['ts'])} | {e['device']} |")
    lines += ["", "## Event time, and how the revision was made", ""]
    lines += [f"- {t}" for t in event_time_text(revision)]
    lines.append(f"- So {amendment['to']} is a bounded recomputation: clink replayed `data/events.ndjson` and every "
                 "transfer that arrived since as two inputs and merged them by event time, so the arrival is judged by "
                 "the same five-minute allowance as every other transfer.")
    lines += ["", "## What changed in the evidence", ""]
    for link in amendment["changes"]["links"]:
        lines.append(f"- New onward link `{link}`, derived by clink in {amendment['to']}: a candidate onward-transfer "
                     "relationship, timing only.")
    for indicator in amendment["changes"]["indicators"]:
        lines.append(f"- Indicator `{indicator}` changed.")
    selection = next(s for s in ledger.of("selection") if s["revision"] == amendment["to"])
    lines += ["", "## Claims selected for revalidation", ""]
    for cid, hits in selection["selected"].items():
        lines.append(f"- {cid}: " + "; ".join(hit_text(cid, h) for h in hits))
    lines.append(f"- Not selected: {', '.join(selection['not_selected']) or 'none'}. Revalidating only the selected "
                 f"claims gave the same verdicts as checking all {selection['claims']} again.")
    for s in amendment["superseded"]:
        old, new = findings[s["finding"]], findings[s["replacement"]]
        lines += ["", f"## {s['finding']}, superseded at {amendment['to']}", "",
                  f"As written at {s['revision']}: {old['statement']}", "",
                  f"| Claim | Asserts | At {amendment['from']} | At {amendment['to']} |", "|---|---|---|---|"]
        for c in s["claims"]:
            at_new = c["at_new"] + ("" if c["at_new"] == "supported" else f": {c['reason']}")
            lines.append(f"| {c['claim']} | {claim_text(claims[c['claim']])} | {c['at_previous']} | {at_new} |")
        lines += ["", f"Replacement, **{new['id']}**, asserted at {amendment['to']}: {new['statement']}", "",
                  f"| Claim | Type | Asserts | At {amendment['to']} |", "|---|---|---|---|"]
        for cid in new["claims"]:
            lines.append(f"| {cid} | {claims[cid]['type']} | {claim_text(claims[cid])} | "
                         f"{ledger.validation(cid, amendment['to'])['status']} |")
    lines += ["", f"## Unchanged at {amendment['to']}", ""]
    for u in amendment["unchanged"]:
        lines.append(f"- **{u['finding']}** {findings[u['finding']]['statement']}  ")
        lines.append("  " + ", ".join(f"{c['claim']} {c['status']} at {amendment['to']} ("
                                      + ("not selected, so carried; a full recheck agrees" if c["how"] == "carried"
                                         else "selected, checked again, unchanged") + ")" for c in u["claims"]))
    return "\n".join(lines) + "\n"


def revalidation_note(ledger: rv.Ledger, rid: str) -> str:
    revision = ledger.revision(rid)
    selection = next(s for s in ledger.of("selection") if s["revision"] == rid)
    lines = [f"# Revalidation at evidence revision {rid}", "", header(revision), "",
             f"No finding is affected: every claim keeps its verdict at {rid}.", ""]
    lines += [f"- {t}" for t in event_time_text(revision)]
    lines.append(f"- Selected for revalidation: {', '.join(selection['selected']) or 'none'}; not selected: "
                 f"{', '.join(selection['not_selected']) or 'none'}. Revalidating only the selected claims gave the "
                 f"same verdicts as checking all {selection['claims']} again.")
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# The before, change and after view

WIDTH = 116


def wrap(text: str, indent: int, hanging: int | None = None) -> list[str]:
    return textwrap.wrap(text, WIDTH, initial_indent=" " * indent,
                         subsequent_indent=" " * (indent if hanging is None else hanging)) or [""]


def summary(finding: dict, claims: dict) -> str:
    cs = [claims[c] for c in finding["claims"]]
    if finding["about"] == "alert":
        p = cs[0]["predicate"]
        return (f"{p['indicator']}: {p['senders']} senders paid {p['account']} {rv.money(p['total_minor'])}, "
                f"{rv.hms(p['window_start_ms'])}-{rv.hms(p['window_end_ms'])}")
    reach = next(c["predicate"] for c in cs if c["type"] == "onward_reach")
    gaps = " or ".join(f"{rv.hms(c['predicate']['start_ms'])}-{rv.hms(c['predicate']['end_ms'])}"
                       for c in cs if c["type"] == "no_onward_transfer")
    ends = ", ".join(reach["terminal_accounts"])
    path = next((" path " + " > ".join(c["predicate"]["transfers"]) for c in cs if c["type"] == "onward_path"), "")
    return (f"its paths: at most {rv.links_text(reach['max_depth'])}, ending at {ends}; no qualifying onward "
            f"transfer from {ends} at {gaps}" + (";" + path if path else ""))


def show_findings(ledger: rv.Ledger, ids: list[str], rid: str) -> list[str]:
    claims, findings = ledger.claims(), ledger.findings()
    lines = []
    for fid in ids:
        f = findings[fid]
        verdicts = " ".join(f"{c}" for c in f["claims"])
        statuses = {ledger.validation(c, rid)["status"] for c in f["claims"]}
        lines += wrap(f"{fid}  {summary(f, claims)}  [{verdicts}: {', '.join(sorted(statuses))} at {rid}]", 2, 6)
    return lines


def view(out: Path, second: dict) -> str:
    ledger = rv.Ledger(out / "ledger.jsonl")
    lines = ["Evidence-driven revision of investigative findings: a staged evolving investigation.",
             f"Bounded replays by clink ({PIPELINE}); no model, no API key. Published in {out}/.", ""]
    r1 = ledger.revision("r1")
    lines += wrap(f"BEFORE  r1: {r1['events']} transfers from {FIRST}. clink exited 0, {r1['jobs_completed']} of "
                  f"{r1['jobs']} jobs; {r1['reconciled'][0]} of {r1['reconciled'][1]} records reconciled; derived "
                  "evidence equals the independent reference.", 0, 8)
    lines += show_findings(ledger, [f["id"] for f in ledger.of("finding") if f["revision"] == "r1"], "r1")
    lines.append(f"  Case note: {out / 'r1-case-note.md'}")
    lines.append("")
    if second.get("outcome") == "nothing new":
        lines += wrap(f"CHANGE  {second['arrival']}: nothing new (already known: "
                      f"{', '.join(second['replayed']) or 'none'}). Nothing to recompute; "
                      f"{second['previous']['id']} stays published, and no amendment is made.", 0)
        return "\n".join(lines) + "\n"
    revision = second["revision"]
    rid = revision["id"]
    dataset = dataset_of(out, revision)
    new = [e for e in dataset if e["transfer_id"] in set(revision["arrived"])]
    lines.append(f"CHANGE  {second.get('arrival_path', ARRIVAL)}: {len(new)} new transfer{'' if len(new) == 1 else 's'}"
                 + (f", {len(second['replayed'])} already known" if second.get("replayed") else ""))
    for e in new:
        lines.append(f"  {e['transfer_id']}  {e['src']} -> {e['dst']}  {rv.money(e['amount_minor'])}  "
                     f"{rv.hms(e['ts'])} UTC {rv.day(e['ts'])}  {e['device']}")
    for text in event_time_text(revision):
        lines += wrap(text, 2)
    lines += wrap(f"So {rid} is a bounded recomputation of {FIRST} and the arrival, merged by event time in clink, "
                  "which judges the arrival by the same allowance as every other transfer: "
                  f"clink exited 0, {revision['jobs_completed']} of {revision['jobs']} jobs; "
                  f"{revision['reconciled'][0]} of {revision['reconciled'][1]} records reconciled; derived evidence "
                  "equals the reference.", 2)
    for link in revision["new_links"]:
        lines.append(f"  New relationship, derived by clink: {link}")
    selection = next(s for s in ledger.of("selection") if s["revision"] == rid)
    lines.append("  Selected by the dependency query in Relate, and by the same rule over the ledger:")
    for cid, hits in selection["selected"].items():
        for h in hits:
            lines += wrap(f"{cid}  {hit_text(cid, h)}", 4, 8)
    if not selection["selected"]:
        lines.append("    none")
    lines += wrap(f"Not selected: {' '.join(selection['not_selected']) or 'none'}. Incremental revalidation equals "
                  f"a full recheck: {selection['claims']} of {selection['claims']} verdicts.", 2)
    lines.append("")
    amendment = next((a for a in ledger.of("amendment") if a["to"] == rid), None)
    publication = ledger.published()
    if amendment is None:
        lines += wrap(f"AFTER   {rid} published; no finding is affected, so no amendment. Note: "
                      f"{out / publication['note']}", 0)
        return "\n".join(lines) + "\n"
    lines.append(f"AFTER   {rid} published, with amendment {amendment['id']} ({amendment['from']} -> {rid}).")
    for s in amendment["superseded"]:
        lines.append(f"  {s['finding']}  superseded at {rid}. Its claims stay supported relative to {s['revision']}; "
                     f"at {rid}:")
        for c in s["claims"]:
            if c["at_new"] != c["at_previous"]:
                lines += wrap(textwrap.shorten(f"{c['claim']} {c['at_new']}: {c['reason']}", WIDTH - 6,
                                               placeholder=" ..."), 6, 8)
        lines += show_findings(ledger, [s["replacement"]], rid)
    lines += wrap(unchanged_text(amendment), 2)
    lines.append(f"  Amendment: {out / publication['note']}")
    lines.append(f"  Ledger: {out / 'ledger.jsonl'} (append-only; {amendment['from']}'s records and note unchanged)")
    return "\n".join(lines) + "\n"


def unchanged_text(amendment: dict) -> str:
    names = [u["finding"] for u in amendment["unchanged"]]
    carried = [c["claim"] for u in amendment["unchanged"] for c in u["claims"] if c["how"] == "carried"]
    checked = [c["claim"] for u in amendment["unchanged"] for c in u["claims"] if c["how"] != "carried"]
    text = f"Unchanged: {', '.join(names) or 'none'}."
    if carried:
        text += f" Not selected, so carried: {' '.join(carried)}."
    if checked:
        text += f" Selected, checked again and unchanged: {' '.join(checked)}."
    return text + " A full recheck agrees with each."


def main() -> int:
    os.chdir(ROOT)
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--continue", dest="resume", action="store_true")
    parser.add_argument("--arrival", type=Path, default=ARRIVAL)
    args = parser.parse_args()

    try:
        if not args.resume:
            if args.out == DEFAULT_OUT:
                shutil.rmtree(args.out, ignore_errors=True)
            elif args.out.exists() and any(args.out.iterdir()):
                raise Refused(f"{args.out} is not empty: remove it, or use --continue to apply an arrival to it")
            initial(args.out)
        second = apply(args.out, args.arrival)
        second["arrival_path"] = args.arrival
    except Refused as refused:
        published = rv.Ledger(args.out / "ledger.jsonl").published() if (args.out / "ledger.jsonl").exists() else None
        print(f"refused     {refused}")
        print("published   nothing; " + (f"{published['revision']} stays the published revision ({args.out})"
                                          if published else "no revision is published"))
        return 1
    sys.stdout.write(view(args.out, second))
    return 0


if __name__ == "__main__":
    sys.exit(main())
