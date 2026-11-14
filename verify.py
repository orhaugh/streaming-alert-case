#!/usr/bin/env python3
"""Verify what this repository claims, with no model and no API key.

For each bounded dataset (the small case, and the same pipeline at scale):
  1. the store: the published Relate store against expectations calculated
     independently from the raw events, and the run that wrote it;
  2. the checker: every claim of the answer key is supported, and every
     deliberately unsupported claim in claims/ is rejected;
  3. the tables: the SQLite tables the table-based agent reads hold the same
     records as the store.
Then every recorded agent run: its claims are checked again against its
dataset's store and events, and each claim's verdict and every score recorded
beside the run must equal the ones computed again; each comparison's summary
must equal the one computed again from its runs. A recording keeps the words
its checker gave as reasons, and the metrics of its time: what is compared is
each verdict, and every number the recording holds.

Exit status 0 only when every check passes. What it checks is structured:
records, values, references and query results. It does not judge prose.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from alertcase import answers, facts, tables
from alertcase.cases import CASES, Case
from alertcase.casenote import arm_text
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


def check_case(case: Case, report: Report) -> tuple[facts.Facts, facts.Facts] | None:
    case.unpack()
    if not case.store.exists():
        report.section(f"The {case.name} case")
        report.record("store", False, f"no store at {case.store}: run ./rebuild.sh {case.name}")
        return None
    events = facts.from_events(case.events)
    with Graph(case.store) as graph:
        report.section(f"The {case.name} case: the store, {case.store}")
        check_store(graph, case.events, case.scenario, report.record)
        graph_facts = facts.from_graph(graph)

    report.section(f"The {case.name} case: the claim checker")
    verdicts = check_claims(answers.expected_claims(events), events, graph_facts)
    report.record("answer key supported", all(v["status"] == "supported" for v in verdicts),
                  f"{sum(v['status'] == 'supported' for v in verdicts)} of {len(verdicts)} claims of the answer key "
                  "are supported by the events and the graph")
    if case.planted.exists():
        planted = json.loads(case.planted.read_text())
        for verdict in check_claims([p["claim"] for p in planted], events, graph_facts):
            reason = verdict.get("reason") or f"events: {verdict['events']}; graph: {verdict['graph']}"
            report.record(f"planted {verdict['claim']} rejected", verdict["status"] == "unsupported",
                          f"{verdict['status']}: {reason}")

    report.section(f"The {case.name} case: the tables, {case.tables}")
    if case.tables.exists():
        held = tables.from_tables(case.tables)
        same = {name: getattr(held, name) == getattr(events, name)
                for name in ("transfers", "indicators", "links", "device_senders", "run")}
        report.record("same records as the store", all(same.values()),
                      "transfers, fan-in alerts with contributions, onward links and the run equal the bounded dataset"
                      if all(same.values()) else f"differ: {[k for k, ok in same.items() if not ok]}")
    else:
        report.record("same records as the store", False, f"missing: run export_tables.py --case {case.name}")
    return events, graph_facts


def agrees(recorded, again) -> bool:
    """Every value the recording holds equals the one computed again. A metric
    added after the recording was made has nothing to compare against."""
    if isinstance(recorded, dict):
        return isinstance(again, dict) and all(k in again and agrees(v, again[k]) for k, v in recorded.items())
    if isinstance(recorded, list):
        return isinstance(again, list) and len(recorded) == len(again) and all(map(agrees, recorded, again))
    return recorded == again


def verdicts(checked: list[dict]) -> list[tuple]:
    return [(v["claim"], v["type"], v["status"]) for v in checked]


def check_runs(root: Path, title: str, sources: dict, report: Report) -> None:
    report.section(f"{title}, {root}")
    runs = sorted(p.parent for p in root.glob("**/meta.json"))
    if not runs:
        print("      none recorded")
    for run in runs:
        meta = json.loads((run / "meta.json").read_text())
        name = str(run.relative_to(root))
        case = meta.get("case", "small")
        if case not in sources:
            continue  # a case this invocation does not check
        if sources[case] is None:
            report.record(name, False, f"the {case} case's store is not available to check it against")
            continue
        events, graph_facts = sources[case]
        output = json.loads((run / "output.json").read_text()) if (run / "output.json").exists() else None
        claims = flatten_claims(output["claims"]) if output else []
        again = check_claims(claims, events, graph_facts)
        recorded_check = json.loads((run / "check.json").read_text())
        recorded_score = json.loads((run / "score.json").read_text())
        rescored = score(output, events, graph_facts, meta["effort"])
        same = verdicts(again) == verdicts(recorded_check) and agrees(recorded_score, rescored)
        report.record(name, same,
                      f"{case} case, {arm_text(meta)}, {meta['status']}: correctness {rescored['correctness']:.2f}, "
                      f"{rescored['supported']} of {rescored['claims']} claims supported, reference validity "
                      f"{rescored['reference_validity']}; every verdict and recorded score equal"
                      if same else "the verdicts or scores differ from the ones recorded beside the run")
    for summary_path in sorted(root.glob("**/summary.json")):
        same = agrees(json.loads(summary_path.read_text()), summarise(summary_path.parent))
        report.record(str(summary_path.relative_to(root)), same,
                      "the comparison's summary equals the one computed again from its runs' scores"
                      if same else "the summary differs from the one computed from its runs' scores")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--case", choices=["all", *sorted(CASES)], default="all")
    parser.add_argument("--runs", type=Path, default=Path("runs/recorded"))
    parser.add_argument("--superseded", type=Path, default=Path("runs/superseded"),
                        help="recorded runs kept for the record, made with an earlier version of the prompt")
    parser.add_argument("--shakedown", type=Path, default=Path("runs/shakedown"),
                        help="live runs that checked the harness before recording; part of no result")
    args = parser.parse_args()

    report = Report()
    names = sorted(CASES, key=lambda n: n != "small") if args.case == "all" else [args.case]
    sources = {name: check_case(CASES[name], report) for name in names}
    check_runs(args.runs, "Recorded agent runs", sources, report)
    if args.superseded.exists():
        check_runs(args.superseded, "Superseded agent runs", sources, report)
    if args.shakedown.exists():
        check_runs(args.shakedown, "Shakedown runs, live and part of no result", sources, report)

    passed = sum(report.results)
    print(f"\n{passed} of {len(report.results)} checks passed")
    return 0 if passed == len(report.results) else 1


if __name__ == "__main__":
    sys.exit(main())
