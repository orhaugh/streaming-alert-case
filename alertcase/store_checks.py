"""The published store, checked against expectations calculated independently
from the raw events. Structured checks only: records, values, links and query
results. Nothing here reads prose."""

from __future__ import annotations

import json
from pathlib import Path

from . import reference
from .events import FIELDS, load_events, sha256_of
from .graph import Graph


def check_store(graph: Graph, events_path: Path, scenario_path: Path, record) -> None:
    """Runs the nine checks, reporting each through record(name, ok, detail)."""
    events = load_events(events_path)
    want_indicators = reference.fan_in(events)
    want_pairs = reference.onward(events)
    want_investigation = reference.investigate(events, want_indicators, want_pairs)
    want_counts = reference.graph_counts(events, want_indicators, want_pairs)
    designed = json.loads(scenario_path.read_text())["designed"]

    def equal(name: str, got, want, detail: str) -> None:
        if got != want:
            detail = f"differs from the expectation\n      store:    {got}\n      expected: {want}"
        record(name, got == want, detail)

    # 1. The store says which bounded dataset it holds, that it is the file on
    #    disk, and that every job of the run that wrote it succeeded.
    runs = [r["run"] for r in graph.run_records()]
    run = runs[0] if len(runs) == 1 else {}
    whole = (len(runs) == 1 and run.get("dataset_sha256") == sha256_of(events_path)
             and run.get("dataset_events") == len(events) and run.get("replay") == "bounded"
             and run.get("jobs") == run.get("jobs_completed") == 3
             and run.get("clink_exit_status") == 0 and run.get("cancelled") is False)
    record("dataset and run", whole,
           f"{run.get('id')} is a {run.get('replay')} replay of {run.get('dataset_events')} events, sha256 "
           f"{str(run.get('dataset_sha256'))[:12]}..., the file on disk; {run.get('jobs_completed')} of "
           f"{run.get('jobs')} jobs completed, clink exit status {run.get('clink_exit_status')}, not cancelled")

    # 2. Nothing extra and nothing missing.
    got_counts = {
        "nodes": {r["label"]: r["n"] for r in graph.rows("MATCH (n) RETURN labels(n)[0] AS label, count(*) AS n")},
        "relationships": {r["type"]: r["n"] for r in graph.rows("MATCH ()-[r]->() RETURN type(r) AS type, count(*) AS n")},
    }
    equal("graph counts", got_counts, want_counts,
          ", ".join(f"{n} {label}" for label, n in sorted(want_counts["nodes"].items())) + "; "
          + ", ".join(f"{n} {kind}" for kind, n in sorted(want_counts["relationships"].items())))

    # 3. Every event in the store is the event in the file.
    got_events = graph.transfers()
    as_tuple = lambda e: tuple(e[name] for name in FIELDS)  # noqa: E731
    equal("events", sorted(map(as_tuple, got_events)), sorted(map(as_tuple, events)),
          f"{len(events)} transfers with sender, receiver, device, amount and time as in the file")

    # 4. clink's fan-in indicators, with their contributing transfers.
    got_indicators = graph.indicators()
    equal("fan-in indicators", got_indicators, want_indicators,
          f"{len(want_indicators)} indicators equal the reference, contributing transfers included")

    # 5. Each indicator's values follow from the events it is linked to.
    recount = graph.rows("""
        MATCH (i:Indicator {kind: 'fan_in'})-[:CONTRIBUTING]->(t:Transfer)<-[:SENT]-(s:Account)
        RETURN i.id AS id, count(DISTINCT s) AS senders, count(t) AS transfers, sum(t.amount_minor) AS total_minor,
               min(t.ts) AS first_ts, max(t.ts) AS last_ts""")
    stated = {i["id"]: i for i in got_indicators}
    supported = len(recount) == len(stated) and all(
        r["id"] in stated
        and (r["senders"], r["transfers"], r["total_minor"])
        == tuple(stated[r["id"]][k] for k in ("senders", "transfers", "total_minor"))
        and stated[r["id"]]["window_start"] <= r["first_ts"] and r["last_ts"] < stated[r["id"]]["window_end"]
        for r in recount)
    record("indicator evidence", supported,
           "each indicator's sender count, transfer count, total and window recount from its linked transfers")

    # 6. clink's onward links, each joining a credit to a debit from the
    #    account credited, with the gap its transfers' times give.
    got_pairs = graph.rows("""
        MATCH (c:Transfer)-[p:PASSED_ON]->(d:Transfer)
        MATCH (c)-[:TO]->(a:Account)-[:SENT]->(d)
        RETURN p.id AS id, c.id AS in_id, d.id AS out_id, a.id AS account, p.gap_ms AS gap_ms, d.ts - c.ts AS gap_from_events""")
    gaps_agree = all(p.pop("gap_from_events") == p["gap_ms"] for p in got_pairs)
    got_pairs.sort(key=lambda p: p["id"])
    equal("onward links", got_pairs if gaps_agree else "a stored gap differs from its transfers' times", want_pairs,
          f"{len(want_pairs)} links equal the reference; each joins a credit to a debit from the account credited")

    # 7. The relationship questions, answered by Cypher.
    equal("relationship queries", graph.investigation(), want_investigation,
          "onward depth, resting accounts, route accounts and shared devices equal the reference for every indicator")

    # 8 and 9 compare the reference with what the scenario was designed to
    # contain; the large case's scenario lists its alerts.
    if json.loads(scenario_path.read_text()).get("format") == "cases":
        _designed_cases(events, want_indicators, want_pairs, want_investigation, designed, record)
        return

    # 8. The reference agrees with what the scenario was designed to contain.
    by_account = {r["account"]: r for r in want_investigation}
    senders_of = {i["account"]: sorted({e["src"] for e in events if e["transfer_id"] in i["transfer_ids"]})
                  for i in want_indicators}
    as_designed = set(by_account) == {designed["suspicious"]["account"], designed["benign"]["account"]}
    for case in ("suspicious", "benign"):
        plan, found = designed[case], by_account.get(designed[case]["account"])
        shared = {plan["shared_device"]["device"]: plan["shared_device"]["accounts"]} if plan["shared_device"] else {}
        as_designed = as_designed and found is not None and (
            found["indicator"] == f"fan_in:{plan['account']}:{plan['window_start']}"
            and senders_of[plan["account"]] == plan["senders"]
            and found["onward_depth"] == plan["onward_depth"]
            and found["route_accounts"] == sorted(plan["route"])
            and found["terminal_accounts"] == [plan["route"][-1]]
            and found["shared_devices"] == shared)
    off_route = designed["shared_device_off_route"]
    as_designed = as_designed and sorted({e["src"] for e in events if e["device"] == off_route["device"]}) == off_route["accounts"] \
        and all(off_route["device"] not in r["shared_devices"] for r in want_investigation)
    record("designed scenario", as_designed,
           "two alerts and no others; routes, depths and shared devices as designed; "
           f"the shared device {off_route['device']} elsewhere in the data appears on no route")

    # 9. The dataset is one where arrival order gives different answers.
    inversions = designed["inversions"]
    lost_pairs = {p["id"] for p in want_pairs} - {p["id"] for p in reference.onward_in_arrival_order(events)}
    forwarding = f"onward:{inversions['forwarding']['credit']}:{inversions['forwarding']['debit_arrives_first']}"
    strict = {i["account"]: i for i in reference.fan_in_without_tolerance(events)}
    full = {i["account"]: i for i in want_indicators}
    suspect = designed["suspicious"]["account"]
    lost_credits = set(full[suspect]["transfer_ids"]) - set(strict[suspect]["transfer_ids"]) if suspect in strict else None
    record("order matters", lost_pairs == {forwarding} and lost_credits == {inversions["window_boundary"]["credit"]},
           f"taken in arrival order, a lookup misses {forwarding} and a window with no allowance loses "
           f"{inversions['window_boundary']['credit']}; the store holds both")


def _designed_cases(events, want_indicators, want_pairs, want_investigation, designed, record) -> None:
    """Checks 8 and 9 for a scenario that lists its alerts (the large case)."""
    by_account = {r["account"]: r for r in want_investigation}
    senders_of = {i["account"]: sorted({e["src"] for e in events if e["transfer_id"] in i["transfer_ids"]})
                  for i in want_indicators}
    alerts = designed["alerts"]
    as_designed = set(by_account) == {a["account"] for a in alerts}
    for plan in alerts:
        found = by_account.get(plan["account"])
        as_designed = as_designed and found is not None and (
            found["indicator"] == f"fan_in:{plan['account']}:{plan['window_start']}"
            and senders_of[plan["account"]] == plan["senders"]
            and found["onward_depth"] == plan["onward_depth"]
            and found["route_accounts"] == plan["route"]
            and found["terminal_accounts"] == plan["terminal"]
            and found["shared_devices"] == plan["shared_devices"])
    decoys = designed["decoys"]
    chain = set(decoys["chain"]["accounts"])
    chain_links = sum(1 for p in want_pairs if p["account"] in chain)
    off_route = all(account not in r["shared_devices"].get(device, [])
                    for device, account in decoys["devices_used_off_route"].items() for r in want_investigation)
    on_no_route = all(not chain & set(r["route_accounts"]) for r in want_investigation)
    as_designed = as_designed and chain_links == decoys["chain"]["onward_links"] and off_route and on_no_route
    labels = [a["label"] for a in alerts]
    record("designed scenario", as_designed,
           f"{len(alerts)} alerts and no others ({labels.count('suspicious')} designed as suspicious, "
           f"{labels.count('benign')} as benign lookalikes); routes, depths and shared devices as designed; the "
           f"{chain_links}-link decoy chain is on no route, and devices also used off a route are listed only for "
           "the route accounts that used them")

    inversions = designed["inversions"]
    lost_pairs = {p["id"] for p in want_pairs} - {p["id"] for p in reference.onward_in_arrival_order(events)}
    forwarding = f"onward:{inversions['forwarding']['credit']}:{inversions['forwarding']['debit_arrives_first']}"
    strict = {i["account"]: i for i in reference.fan_in_without_tolerance(events)}
    full = {i["account"]: i for i in want_indicators}
    account = inversions["window_boundary"]["account"]
    lost_credits = set(full[account]["transfer_ids"]) - set(strict[account]["transfer_ids"]) if account in strict else None
    record("order matters", forwarding in lost_pairs and lost_credits == {inversions["window_boundary"]["credit"]},
           f"taken in arrival order, a lookup misses {len(lost_pairs)} of {len(want_pairs)} onward links, "
           f"{forwarding} among them, and a window with no allowance loses {inversions['window_boundary']['credit']}; "
           "the store holds them all")
