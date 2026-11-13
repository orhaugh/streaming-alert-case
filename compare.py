#!/usr/bin/env python3
"""Compare a table-based and a Relate-based investigation of the same evidence.

Runs the agent N times on each arm, alternating arms, with the same model,
effort, prompt, task, output schema and budgets (alertcase/agent.py), scores
every run with the same checker and answer key (alertcase/scoring.py), and
writes each run and a summary computed from them. Needs Anthropic API
credentials, and costs a model run per investigation.

Without --record, writes runs/live/comparison-<time>/; with --record NAME,
runs/recorded/NAME/. Every number in the summary comes from a run directory
beside it, and verify.py recomputes it.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from alertcase import agent, facts
from alertcase.comparison import summarise
from alertcase.graph import Graph
from alertcase.recording import record


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--runs", type=int, default=3, help="runs per arm (default 3)")
    parser.add_argument("--record", metavar="NAME", help="write runs/recorded/NAME instead of a live directory")
    args = parser.parse_args()

    root = (Path("runs/recorded") / args.record if args.record
            else Path("runs/live") / f"comparison-{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}")
    if root.exists():
        raise SystemExit(f"refused     {root} exists")
    events = facts.from_events()
    with Graph() as graph:
        graph_facts = facts.from_graph(graph)
    print(f"{args.runs} run(s) per arm, model {agent.MODEL}, effort {agent.EFFORT}, writing {root}")
    for n in range(1, args.runs + 1):
        order = ("graph", "table") if n % 2 else ("table", "graph")
        for arm in order:
            print(f"{arm} {n}")
            result = agent.run(arm)
            scored = record(result, root / f"{arm}-{n}", recorded=bool(args.record), events=events,
                            graph=graph_facts, title=f"Case note: {arm} arm, run {n}")
            print(f"  {result.status}: correctness {scored['correctness']:.2f}, {scored['unsupported']} claim(s) not "
                  f"supported, reference validity {scored['reference_validity']}")
    summary = summarise(root)
    (root / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    for arm, s in summary.items():
        m = s["mean"]
        print(f"{arm:<6} {s['completed']} of {s['runs']} completed; mean correctness {m['correctness']}, "
              f"unsupported claims {m['unsupported_claims']}, reference validity {m['reference_validity']}, "
              f"queries {m['tool_calls']}, input tokens {m['input_tokens_total']}, output tokens {m['output_tokens']}")
    print(f"wrote       {root}/summary.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
