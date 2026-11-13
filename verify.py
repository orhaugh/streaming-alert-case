#!/usr/bin/env python3
"""Verify what this repository claims, with no model and no API key.

  1. the store: the published Relate store against expectations calculated
     independently from the raw events, and the run that wrote it;
  2. the checker: every claim of the answer key is supported, and every
     deliberately unsupported claim in claims/planted.json is rejected;
  3. the tables: the SQLite tables the table-based agent reads hold the same
     records as the store;
  4. the recorded agent runs: each run's claims are checked again against the
     store and the events, and its verdicts and scores must equal the ones
     recorded beside it.

Exit status 0 only when every check passes. What it checks is structured:
records, values, references and query results. It does not judge prose.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from alertcase import answers, facts, tables
from alertcase.claims import check_claims, flatten_claims
from alertcase.comparison import summarise
from alertcase.graph import Graph
from alertcase.scoring import score
from alertcase.store_checks import check_store


class Report:
    def __init__(self) -> None:
        self.results: list[bool] = []

    def record(self, name: str, ok: bool, detail: str) -> bool:
        self.results.append(ok)
        print(f"{'PASS' if ok else 'FAIL'}  {name:<26} {detail}")
        return ok

    @staticmethod
    def section(title: str) -> None:
        print(f"\n{title}")


def recorded_runs(root: Path) -> list[Path]:
    return sorted(p.parent for p in root.glob("**/meta.json"))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--events", type=Path, default=Path("data/events.ndjson"))
    parser.add_argument("--scenario", type=Path, default=Path("data/scenario.json"))
    parser.add_argument("--store", type=Path, default=Path("store/case.rl"))
    parser.add_argument("--tables", type=Path, default=tables.TABLES)
    parser.add_argument("--planted", type=Path, default=Path("claims/planted.json"))
    parser.add_argument("--runs", type=Path, default=Path("runs/recorded"))
    args = parser.parse_args()

    report = Report()
    events = facts.from_events(args.events)
    with Graph(args.store) as graph:
        report.section(f"The store, {args.store}")
        check_store(graph, args.events, args.scenario, report.record)
        graph_facts = facts.from_graph(graph)

    report.section("The claim checker")
    key_claims = answers.expected_claims(events)
    verdicts = check_claims(key_claims, events, graph_facts)
    report.record("answer key supported", all(v["status"] == "supported" for v in verdicts),
                  f"{sum(v['status'] == 'supported' for v in verdicts)} of {len(verdicts)} claims of the answer key "
                  "are supported by the events and the graph")
    planted = json.loads(args.planted.read_text())
    for entry, verdict in zip(planted, check_claims([p["claim"] for p in planted], events, graph_facts)):
        reason = verdict.get("reason") or f"events: {verdict['events']}; graph: {verdict['graph']}"
        report.record(f"planted {verdict['claim']} rejected", verdict["status"] == "unsupported",
                      f"{verdict['status']}: {reason}")

    report.section(f"The tables, {args.tables}")
    if args.tables.exists():
        held = tables.from_tables(args.tables)
        same = {name: getattr(held, name) == getattr(events, name)
                for name in ("transfers", "indicators", "links", "device_senders", "run")}
        report.record("same records as the store", all(same.values()),
                      "transfers, fan-in alerts with contributions, onward links and the run equal the bounded dataset"
                      if all(same.values()) else f"differ: {[k for k, ok in same.items() if not ok]}")
    else:
        report.record("same records as the store", False, "missing: run export_tables.py")

    report.section(f"Recorded agent runs, {args.runs}")
    runs = recorded_runs(args.runs)
    if not runs:
        print("      none recorded")
    for run in runs:
        meta = json.loads((run / "meta.json").read_text())
        output = json.loads((run / "output.json").read_text()) if (run / "output.json").exists() else None
        claims = flatten_claims(output["claims"]) if output else []
        again = check_claims(claims, events, graph_facts)
        recorded_check = json.loads((run / "check.json").read_text())
        recorded_score = json.loads((run / "score.json").read_text())
        rescored = score(output, events, graph_facts, meta["effort"])
        same = again == recorded_check and rescored == recorded_score
        name = str(run.relative_to(args.runs))
        report.record(name, same,
                      f"{meta['arm']} arm, {meta['status']}: correctness {rescored['correctness']:.2f}, "
                      f"{rescored['supported']} of {rescored['claims']} claims supported, reference validity "
                      f"{rescored['reference_validity']}; verdicts and scores equal the recorded ones"
                      if same else "the verdicts or scores differ from the ones recorded beside the run")
    for summary_path in sorted(args.runs.glob("**/summary.json")):
        same = summarise(summary_path.parent) == json.loads(summary_path.read_text())
        report.record(str(summary_path.relative_to(args.runs)), same,
                      "the comparison's summary equals the one computed again from its runs' scores"
                      if same else "the summary differs from the one computed from its runs' scores")

    passed = sum(report.results)
    print(f"\n{passed} of {len(report.results)} checks passed")
    return 0 if passed == len(report.results) else 1


if __name__ == "__main__":
    sys.exit(main())
