"""The evolving investigation in Relate.

Each evidence revision has its own store. clink writes the evidence into it
(transfers, accounts, devices, fan-in indicators, onward links); at
publication revise.py writes the investigation beside it, as of that revision:

  (:Revision)-[:FOLLOWS]->(:Revision), and -[:ADDED]->(:Transfer) for each
      transfer that arrived at it
  (:Claim) with its predicate, -[:ASSERTED_AT]->(:Revision), -[:CITES]->(:Transfer)
      and (:Indicator) for the evidence a positive claim cites, and for an absence
      -[:SEARCHES {start_ms, end_ms, pattern}]->(:Account), its recorded search scope
  (:Claim)-[:SCOPE {revision, role, start_ms, end_ms, via}]->(:Account): the claim's
      dependency windows at a revision, debits from or credits to the account
  (:Validation)-[:OF]->(:Claim), -[:AGAINST]->(:Revision): every verdict so far
  (:Revision)-[:SELECTED {transfer, role, ...}]->(:Claim): what new evidence put in question
  (:Finding)-[:CITES]->(:Claim), -[:REPLACES]->(:Finding)
  (:Amendment)-[:FROM_REVISION|TO_REVISION]->(:Revision), -[:SUPERSEDES|REPLACEMENT|UNCHANGED]->(:Finding),
      -[:NEW_EVIDENCE]->(:Transfer)

The selection query reads the dependency windows of the revision before and
the transfers the new revision added, in one store. No relationship type here
is one the evidence uses, so every evidence count stays clink's.
"""

from __future__ import annotations

import json
from collections import Counter

import relate

from . import reference
from .events import FIELDS
from .graph import Graph

EVIDENCE_NODES = ("Account", "Device", "Indicator", "Transfer")
EVIDENCE_RELATIONSHIPS = ("ABOUT", "CONTRIBUTING", "FROM_DEVICE", "PASSED_ON", "SENT", "TO")
LAYER = ("Revision", "Claim", "Finding", "Validation", "Amendment", "Run")

# The claims whose dependency windows, as of the previous revision, a transfer
# the new revision added falls into: a debit from the window's account, or a
# credit to it, inside the window, both ends included.
SELECTED_BY_DEBIT = """
MATCH (:Revision {id: $revision})-[:ADDED]->(t:Transfer)<-[:SENT]-(a:Account)<-[s:SCOPE {revision: $previous, role: 'debit'}]-(c:Claim)
WHERE s.start_ms <= t.ts AND t.ts <= s.end_ms
RETURN c.id AS claim, t.id AS transfer, s.role AS role, a.id AS account, s.start_ms AS start_ms, s.end_ms AS end_ms, s.via AS via
"""
SELECTED_BY_CREDIT = """
MATCH (:Revision {id: $revision})-[:ADDED]->(t:Transfer)-[:TO]->(a:Account)<-[s:SCOPE {revision: $previous, role: 'credit'}]-(c:Claim)
WHERE s.start_ms <= t.ts AND t.ts <= s.end_ms
RETURN c.id AS claim, t.id AS transfer, s.role AS role, a.id AS account, s.start_ms AS start_ms, s.end_ms AS end_ms, s.via AS via
"""


def evidence_check(graph: Graph, events: list[dict]) -> tuple[int, list[str]]:
    """How many of the dataset's records the store holds as written, and every
    way the store's evidence differs from what the reference rules derive from
    the dataset: transfers, indicators, onward links, the paths, the counts."""
    key = lambda r: tuple(r.get(name) for name in FIELDS)  # noqa: E731
    want, got = Counter(map(key, events)), Counter(map(key, graph.transfers()))
    differences = []
    if want != got:
        differences.append(f"transfers: {sum((want - got).values())} record(s) of the dataset are not in the store as "
                           f"written, {sum((got - want).values())} transfer(s) in the store are not in the dataset")
    indicators, pairs = reference.fan_in(events), reference.onward(events)
    if graph.indicators() != indicators:
        differences.append("fan-in indicators differ from the reference's")
    held = {p["id"]: p for p in graph.onward_links()}
    wanted = {p["id"]: p for p in pairs}
    if held != wanted:
        differences.append(f"onward links: missing {sorted(set(wanted) - set(held))}, not derived by the reference "
                           f"{sorted(set(held) - set(wanted))}"
                           + ("" if set(held) != set(wanted) else ", or a link's values differ"))
    try:
        if graph.investigation() != reference.investigate(events, indicators, pairs):
            differences.append("the candidate paths, their ends or the devices on them differ from the reference's")
    except ValueError as error:  # the reference rules refuse onward links that form a cycle
        differences.append(f"the reference cannot follow the paths: {error}")
    counts = reference.graph_counts(events, indicators, pairs)
    nodes = {r["label"]: r["n"] for r in graph.rows("MATCH (n) RETURN labels(n)[0] AS label, count(*) AS n")
             if r["label"] in EVIDENCE_NODES}
    rels = {r["type"]: r["n"] for r in graph.rows("MATCH ()-[r]->() RETURN type(r) AS type, count(*) AS n")
            if r["type"] in EVIDENCE_RELATIONSHIPS}
    if nodes != {k: v for k, v in counts["nodes"].items() if k in EVIDENCE_NODES} or rels != counts["relationships"]:
        differences.append(f"evidence counts {nodes}, {rels} differ from the reference's")
    return sum((want & got).values()), differences


def selected_in_store(graph: Graph, revision: str, previous: str) -> dict[str, list[dict]]:
    """The selection, answered by Relate from the store's dependency windows."""
    hits: dict[str, list[dict]] = {}
    for query in (SELECTED_BY_DEBIT, SELECTED_BY_CREDIT):
        for row in graph.rows(query, revision=revision, previous=previous):
            claim = row.pop("claim")
            hits.setdefault(claim, []).append(row)
    return hits


# ---------------------------------------------------------------------------
# Writing the investigation layer. Every record is written once, by CREATE,
# into a store no one else has open; ids are unique by constraint.

CONSTRAINTS = [f"CREATE CONSTRAINT {label.lower()}_id IF NOT EXISTS FOR (n:{label}) REQUIRE n.id IS UNIQUE"
               for label in LAYER]


def _json(value) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=False)


def write_records(conn, records: list[dict]) -> None:
    for statement in CONSTRAINTS:
        conn.execute(statement)
    for record in records:
        WRITERS.get(record["kind"], lambda c, r: None)(conn, record)


def _revision(conn, r: dict) -> None:
    conn.execute("""
        CREATE (v:Revision {id: $id, parent: $parent, events: $events, dataset_sha256: $dataset_sha256,
                            run: $run, inputs: $inputs, arrived: $arrived, pipeline_sha256: $pipeline_sha256})""",
                 {"id": r["id"], "parent": r["parent"], "events": r["events"], "dataset_sha256": r["dataset_sha256"],
                  "run": r["run"], "inputs": _json(r["inputs"]), "arrived": r["arrived"],
                  "pipeline_sha256": r["pipeline"]["sha256"]})
    if r["parent"]:
        conn.execute("MATCH (v:Revision {id: $id}), (p:Revision {id: $parent}) CREATE (v)-[:FOLLOWS]->(p)",
                     {"id": r["id"], "parent": r["parent"]})
    conn.execute("MATCH (v:Revision {id: $id}) UNWIND $arrived AS tid MATCH (t:Transfer {id: tid}) "
                 "CREATE (v)-[:ADDED]->(t)", {"id": r["id"], "arrived": r["arrived"]})


def _claim(conn, c: dict) -> None:
    p = c["predicate"]
    conn.execute("""
        MATCH (r:Revision {id: $revision})
        CREATE (c:Claim {id: $id, type: $type, revision: $revision, digest: $digest, predicate: $predicate,
                         subject: $subject, links: $links})-[:ASSERTED_AT]->(r)""",
                 {"id": c["id"], "type": c["type"], "revision": c["revision"], "digest": c["digest"],
                  "predicate": _json(p), "links": c.get("references", {}).get("links", []),
                  "subject": p.get("indicator") or p.get("account") or p.get("transfer")
                  or ">".join(p.get("transfers", []))})
    refs = c.get("references", {})
    conn.execute("MATCH (c:Claim {id: $id}) UNWIND $ids AS tid MATCH (t:Transfer {id: tid}) CREATE (c)-[:CITES]->(t)",
                 {"id": c["id"], "ids": refs.get("transfers", [])})
    conn.execute("MATCH (c:Claim {id: $id}) UNWIND $ids AS iid MATCH (i:Indicator {id: iid}) CREATE (c)-[:CITES]->(i)",
                 {"id": c["id"], "ids": refs.get("indicators", [])})
    if "scope" in c:
        s = c["scope"]
        conn.execute("""
            MATCH (c:Claim {id: $id}), (a:Account {id: $account})
            CREATE (c)-[:SEARCHES {start_ms: $start, end_ms: $end, pattern: $pattern, basis: $basis,
                                   coverage_revision: $coverage, coverage_events: $events}]->(a)""",
                     {"id": c["id"], "account": s["entity"]["account"], "start": s["interval"]["start_ms"],
                      "end": s["interval"]["end_ms"], "pattern": s["pattern"], "basis": s["basis"],
                      "coverage": s["coverage"]["revision"], "events": s["coverage"]["events"]})


def _finding(conn, f: dict) -> None:
    conn.execute("""
        CREATE (f:Finding {id: $id, revision: $revision, about: $about, subject: $subject, statement: $statement})
        WITH f UNWIND $claims AS cid MATCH (c:Claim {id: cid}) CREATE (f)-[:CITES]->(c)""",
                 {k: f[k] for k in ("id", "revision", "about", "subject", "statement", "claims")})
    if f.get("replaces"):
        conn.execute("MATCH (f:Finding {id: $id}), (old:Finding {id: $old}) CREATE (f)-[:REPLACES]->(old)",
                     {"id": f["id"], "old": f["replaces"]})


def _validation(conn, v: dict) -> None:
    conn.execute("""
        MATCH (c:Claim {id: $claim}), (r:Revision {id: $revision})
        CREATE (v:Validation {id: $id, claim: $claim, revision: $revision, status: $status, method: $method,
                              full_recheck: $full, events: $events, graph: $graph})
        CREATE (v)-[:OF]->(c), (v)-[:AGAINST]->(r)""",
                 {"id": v["id"], "claim": v["claim"], "revision": v["revision"], "status": v["status"],
                  "method": v["method"], "full": v.get("full_recheck"), "events": v["events"], "graph": v["graph"]})
    conn.execute("""
        MATCH (c:Claim {id: $claim}) UNWIND $windows AS w MATCH (a:Account {id: w.account})
        CREATE (c)-[:SCOPE {revision: $revision, role: w.role, start_ms: w.start_ms, end_ms: w.end_ms, via: w.via}]->(a)""",
                 {"claim": v["claim"], "revision": v["revision"], "windows": v["windows"]})


def _selection(conn, s: dict) -> None:
    hits = [{"claim": claim, **hit} for claim, found in s["selected"].items() for hit in found]
    conn.execute("""
        MATCH (r:Revision {id: $revision}) UNWIND $hits AS h MATCH (c:Claim {id: h.claim})
        CREATE (r)-[:SELECTED {transfer: h.transfer, role: h.role, account: h.account, start_ms: h.start_ms,
                               end_ms: h.end_ms, via: h.via, previous: $previous}]->(c)""",
                 {"revision": s["revision"], "previous": s["previous"], "hits": hits})


def _amendment(conn, a: dict) -> None:
    conn.execute("""
        MATCH (f:Revision {id: $from}), (t:Revision {id: $to})
        CREATE (a:Amendment {id: $id, from_revision: $from, to_revision: $to, links: $links, record: $record})
        CREATE (a)-[:FROM_REVISION]->(f), (a)-[:TO_REVISION]->(t)""",
                 {"id": a["id"], "from": a["from"], "to": a["to"], "links": a["changes"]["links"], "record": _json(a)})
    for s in a["superseded"]:
        conn.execute("""
            MATCH (a:Amendment {id: $id}), (old:Finding {id: $old}), (new:Finding {id: $new})
            CREATE (a)-[:SUPERSEDES {revision: $revision}]->(old), (a)-[:REPLACEMENT]->(new)""",
                     {"id": a["id"], "old": s["finding"], "new": s["replacement"], "revision": s["revision"]})
    conn.execute("MATCH (a:Amendment {id: $id}) UNWIND $ids AS tid MATCH (t:Transfer {id: tid}) "
                 "CREATE (a)-[:NEW_EVIDENCE]->(t)", {"id": a["id"], "ids": [e["transfer_id"] for e in a["new_events"]]})
    conn.execute("MATCH (a:Amendment {id: $id}) UNWIND $ids AS fid MATCH (f:Finding {id: fid}) "
                 "CREATE (a)-[:UNCHANGED]->(f)", {"id": a["id"], "ids": [u["finding"] for u in a["unchanged"]]})


WRITERS = {"revision": _revision, "claim": _claim, "finding": _finding, "validation": _validation,
           "selection": _selection, "amendment": _amendment}


def write_run(conn, revision: dict, clink: str, lag_ms: int, gap_ms: int) -> None:
    """The run record, as scripts/publish_run.py writes one for the case's own
    store, naming the revision it is the evidence of."""
    conn.execute("""
        CREATE (:Run {id: $run, replay: 'bounded', route: "connector='relate'", revision: $revision,
                      recomputation: $recomputation, dataset_sha256: $dataset_sha256, dataset_events: $events,
                      inputs: $inputs, pipeline: $pipeline, pipeline_sha256: $pipeline_sha256, jobs: 3,
                      jobs_completed: 3, clink_exit_status: 0, cancelled: false, clink: $clink, relate: $relate,
                      lag_ms: $lag_ms, source_batch_size: 1, fan_in_min_senders: 5, fan_in_window_ms: 3600000,
                      onward_max_gap_ms: $gap_ms})""",
                 {"run": revision["run"], "revision": revision["id"], "recomputation": revision["parent"] is not None,
                  "dataset_sha256": revision["dataset_sha256"], "events": revision["events"],
                  "inputs": _json(revision["inputs"]), "pipeline": revision["pipeline"]["path"],
                  "pipeline_sha256": revision["pipeline"]["sha256"], "clink": clink, "relate": relate.__version__,
                  "lag_ms": lag_ms, "gap_ms": gap_ms})


# ---------------------------------------------------------------------------
# Reading the layer back, to compare with the ledger.

def layer(graph: Graph) -> dict:
    return {
        "revisions": sorted(r["id"] for r in graph.rows("MATCH (r:Revision) RETURN r.id AS id")),
        "added": sorted((r["revision"], r["transfer"]) for r in graph.rows(
            "MATCH (r:Revision)-[:ADDED]->(t:Transfer) RETURN r.id AS revision, t.id AS transfer")),
        "claims": sorted((r["id"], r["digest"], r["revision"]) for r in graph.rows(
            "MATCH (c:Claim) RETURN c.id AS id, c.digest AS digest, c.revision AS revision")),
        "searches": sorted((r["claim"], r["account"], r["start_ms"], r["end_ms"], r["coverage"]) for r in graph.rows(
            "MATCH (c:Claim)-[s:SEARCHES]->(a:Account) RETURN c.id AS claim, a.id AS account, s.start_ms AS start_ms, "
            "s.end_ms AS end_ms, s.coverage_revision AS coverage")),
        "findings": sorted((r["id"], r["revision"], tuple(sorted(r["claims"]))) for r in graph.rows(
            "MATCH (f:Finding)-[:CITES]->(c:Claim) RETURN f.id AS id, f.revision AS revision, collect(c.id) AS claims")),
        "validations": sorted((r["id"], r["status"], r["method"]) for r in graph.rows(
            "MATCH (v:Validation) RETURN v.id AS id, v.status AS status, v.method AS method")),
        "windows": sorted((r["claim"], r["revision"], r["role"], r["account"], r["start_ms"], r["end_ms"], r["via"])
                          for r in graph.rows(
            "MATCH (c:Claim)-[s:SCOPE]->(a:Account) RETURN c.id AS claim, s.revision AS revision, s.role AS role, "
            "a.id AS account, s.start_ms AS start_ms, s.end_ms AS end_ms, s.via AS via")),
        "amendments": sorted(r["id"] for r in graph.rows("MATCH (a:Amendment) RETURN a.id AS id")),
    }


def layer_from_records(records: list[dict]) -> dict:
    """What layer() should read from a store the records were written to."""
    of = lambda kind: [r for r in records if r["kind"] == kind]  # noqa: E731
    return {
        "revisions": sorted(r["id"] for r in of("revision")),
        "added": sorted((r["id"], t) for r in of("revision") for t in r["arrived"]),
        "claims": sorted((c["id"], c["digest"], c["revision"]) for c in of("claim")),
        "searches": sorted((c["id"], c["scope"]["entity"]["account"], c["scope"]["interval"]["start_ms"],
                            c["scope"]["interval"]["end_ms"], c["scope"]["coverage"]["revision"])
                           for c in of("claim") if "scope" in c),
        "findings": sorted((f["id"], f["revision"], tuple(sorted(f["claims"]))) for f in of("finding")),
        "validations": sorted((v["id"], v["status"], v["method"]) for v in of("validation")),
        "windows": sorted((v["claim"], v["revision"], w["role"], w["account"], w["start_ms"], w["end_ms"], w["via"])
                          for v in of("validation") for w in v["windows"]),
        "amendments": sorted(a["id"] for a in of("amendment")),
    }


# ---------------------------------------------------------------------------
# Checking a published investigation, with no model and no Docker: what
# verify.py runs over the shipped record (revision/).

def verify_investigation(root, record) -> None:
    """Reports each check through record(name, ok, detail)."""
    from pathlib import Path

    from . import facts
    from . import revision as rv

    root = Path(root)
    try:
        ledger = rv.Ledger(root / "ledger.jsonl")
    except (rv.LedgerError, ValueError) as error:
        record("ledger", False, str(error))
        return
    publications = ledger.of("publication")
    files_ok = bool(publications) and all(
        (root / p["store"]).exists() and rv.sha256_file(root / p["store"]) == p["store_sha256"]
        and (root / p["note"]).exists() and rv.sha256_file(root / p["note"]) == p["note_sha256"] for p in publications)
    revisions = [r["id"] for r in ledger.of("revision")]
    record("ledger", files_ok and [p["revision"] for p in publications] == revisions,
           f"{len(ledger.records)} records, each naming the sha256 of the one before; "
           f"{len(publications)} publications ({', '.join(revisions)}), each store and note on disk as published; "
           f"{ledger.published()['revision'] if publications else 'none'} is the published revision")

    for revision_id in revisions:
        revision = ledger.revision(revision_id)
        through = ledger.through(revision_id)
        try:
            dataset = rv.dataset_of(root, revision)
        except ValueError as error:
            record(f"{revision_id} evidence", False, str(error))
            continue
        reference_facts = facts.from_records(dataset)
        with Graph(root / f"{revision_id}.rl") as graph:
            reconciled, differences = evidence_check(graph, dataset)
            runs = [r["run"] for r in graph.run_records()]
            run_ok = (len(runs) == 1 and runs[0].get("revision") == revision_id
                      and runs[0].get("dataset_sha256") == revision["dataset_sha256"] == rv.dataset_digest(dataset)
                      and runs[0].get("jobs_completed") == runs[0].get("jobs") == 3
                      and runs[0].get("clink_exit_status") == 0 and runs[0].get("cancelled") is False)
            graph_facts = facts.from_graph(graph)
            held = layer(graph)
            in_store = selected_in_store(graph, revision_id, revision["parent"]) if revision["parent"] else {}
        record(f"{revision_id} evidence", not differences and run_ok and reconciled == len(dataset),
               f"{revision['events']} transfers ({' + '.join(str(i['events']) for i in revision['inputs'])}): "
               f"{reconciled} of {len(dataset)} reconciled; indicators, {len(graph_facts.links)} onward links and "
               "paths equal the reference; one run record, every job completed"
               if not differences and run_ok else f"differs: {differences or 'the run record'}")
        want = layer_from_records(through)
        record(f"{revision_id} investigation in Relate", held == want,
               f"{len(want['claims'])} claims, {len(want['findings'])} findings, {len(want['validations'])} "
               f"validations, {len(want['windows'])} dependency windows and {len(want['amendments'])} amendment(s) "
               "in the store equal the ledger through this revision"
               if held == want else f"differs: {[k for k in want if held[k] != want[k]]}")

        claims = {c["id"]: c for c in through if c["kind"] == "claim"}
        again, wrong = 0, []
        for v in (r for r in through if r["kind"] == "validation" and r["revision"] == revision_id):
            verdict = rv.judge(claims[v["claim"]], reference_facts, graph_facts)
            again += 1
            if (verdict["status"] != v["full_recheck"] or v["status"] != v["full_recheck"]
                    or rv.windows(claims[v["claim"]], graph_facts) != v["windows"]):
                wrong.append(v["id"])
        record(f"{revision_id} verdicts", not wrong and again > 0,
               f"{again} validations recomputed against this revision's events and graph: each verdict, its full "
               "recheck and its dependency windows equal the ones recorded" if not wrong else f"differ: {wrong}")

        if revision["parent"]:
            parent = revision["parent"]
            selection = next(s for s in through if s["kind"] == "selection" and s["revision"] == revision_id)
            earlier = {c: ledger.validation(c, parent) for c in claims if ledger.validation(c, parent)}
            new = [e for e in dataset if e["transfer_id"] in set(revision["arrived"])]
            by_rule = rv.select({c: v["windows"] for c, v in earlier.items()}, new)
            agree = (_normal(by_rule) == _normal(selection["selected"]) == _normal(in_store)
                     and selection["not_selected"] == [c for c in sorted(earlier, key=rv.claim_order) if c not in by_rule])
            carried_ok = all(ledger.validation(c, revision_id)["status"] == earlier[c]["status"]
                             for c in earlier if c not in by_rule)
            record(f"{revision_id} selection", agree and carried_ok,
                   f"the rule over the ledger and the dependency query in Relate both select "
                   f"{', '.join(by_rule) or 'nothing'} of {len(earlier)} claims, as recorded; each claim not selected "
                   "kept its verdict, which the full recheck confirms" if agree and carried_ok else
                   f"selection differs: rule {sorted(by_rule)}, recorded {sorted(selection['selected'])}, "
                   f"store {sorted(in_store)}")

    for amendment in ledger.of("amendment"):
        record(f"amendment {amendment['id']}", *_amendment_ok(ledger, amendment, root))


def _normal(hits: dict) -> set:
    return {(c, h["transfer"], h["role"], h["account"], h["start_ms"], h["end_ms"], h["via"])
            for c, found in hits.items() for h in found}


def _amendment_ok(ledger, a: dict, root) -> tuple[bool, str]:
    """Names the previous findings and revision, the new events, the changed
    relationships, the verdicts at the new revision, a replacement for each
    superseded finding, supported in full, and every other finding as unchanged."""
    from . import revision as rv

    findings = ledger.findings()
    revision = ledger.revision(a["to"])
    current = [f["id"] for f in ledger.through(a["from"]) if f["kind"] == "finding"]
    number = lambda r: int(r[1:])  # noqa: E731
    gone = {s["finding"] for b in ledger.of("amendment") if number(b["to"]) <= number(a["from"]) for s in b["superseded"]}
    current = [f for f in current if f not in gone]
    problems = []
    if sorted(e["transfer_id"] for e in a["new_events"]) != revision["arrived"]:
        problems.append("its new events are not the revision's arrivals")
    if a["changes"]["links"] != revision["new_links"]:
        problems.append("its changed relationships are not the revision's new onward links")
    accounted = [s["finding"] for s in a["superseded"]] + [u["finding"] for u in a["unchanged"]]
    if sorted(accounted) != sorted(current):
        problems.append(f"it accounts for {sorted(accounted)}, not every finding standing at {a['from']}")
    for s in a["superseded"]:
        for c in s["claims"]:
            if (ledger.validation(c["claim"], a["from"])["status"] != c["at_previous"]
                    or ledger.validation(c["claim"], a["to"])["status"] != c["at_new"]):
                problems.append(f"{c['claim']}'s verdicts are not the recorded ones")
        if not any(c["at_new"] != c["at_previous"] for c in s["claims"]):
            problems.append(f"{s['finding']} is superseded though none of its claims changed")
        replacement = findings.get(s["replacement"])
        if (replacement is None or replacement["replaces"] != s["finding"] or replacement["revision"] != a["to"]
                or any(ledger.validation(c, a["to"])["status"] != "supported" for c in replacement["claims"])):
            problems.append(f"{s['finding']}'s replacement is not a finding of {a['to']} supported in full")
    for u in a["unchanged"]:
        for c in u["claims"]:
            if ledger.validation(c["claim"], a["to"])["status"] != ledger.validation(c["claim"], a["from"])["status"]:
                problems.append(f"{u['finding']} is listed unchanged, but {c['claim']}'s verdict changed")
    note = next(p for p in ledger.of("publication") if p["revision"] == a["to"])
    if a["id"] not in (root / note["note"]).read_text().splitlines()[0]:
        problems.append("the revision's note is not this amendment's")
    if problems:
        return False, "; ".join(problems)
    supersedes = ", ".join(f"{s['finding']} ({s['revision']}) by {s['replacement']}" for s in a["superseded"])
    return True, (f"{a['from']} to {a['to']}: new {', '.join(e['transfer_id'] for e in a['new_events'])}, new "
                  f"{', '.join(a['changes']['links']) or 'no links'}; supersedes {supersedes}, every replacement "
                  f"claim supported at {a['to']}; {len(a['unchanged'])} findings unchanged, their verdicts kept")
