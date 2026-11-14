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
from alertcase.cases import CASES
from alertcase.comparison import summarise
from alertcase.graph import Graph
from alertcase.recording import record


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--runs", type=int, default=3, help="runs per arm (default 3)")
    parser.add_argument("--case", choices=sorted(CASES), default="small",
                        help="small: the 55-transfer case (default); large: 50,000 transfers")
    parser.add_argument("--provider", choices=agent.PROVIDERS, default="anthropic",
                        help="anthropic: the Claude API (default); bedrock: Amazon Bedrock. Both arms use the same one.")
    parser.add_argument("--record", metavar="NAME", help="write runs/recorded/NAME instead of a live directory")
    parser.add_argument("--request-timeout", type=float, default=agent.REQUEST_TIMEOUT_S, metavar="SECONDS",
                        help=f"each attempt at a model request (default {agent.REQUEST_TIMEOUT_S})")
    parser.add_argument("--max-retries", type=int, default=agent.MAX_RETRIES, metavar="N",
                        help=f"the SDK's retries of a request that fails or times out (default {agent.MAX_RETRIES})")
    args = parser.parse_args()

    root = (Path("runs/recorded") / args.record if args.record
            else Path("runs/live") / f"comparison-{args.case}-{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}")
    if root.exists():
        raise SystemExit(f"refused     {root} exists")
    problem = agent.missing_credentials(args.provider)
    if problem:
        raise SystemExit(problem)
    case = CASES[args.case]
    case.unpack()
    events = facts.from_events(case.events)
    with Graph(case.store) as graph:
        graph_facts = facts.from_graph(graph)
    print(f"{args.case} case, {args.runs} run(s) per arm, {args.provider}, model {agent.model_for(args.provider)}, "
          f"effort {agent.EFFORT}, writing {root}")
    for n in range(1, args.runs + 1):
        order = ("graph", "table") if n % 2 else ("table", "graph")
        for arm in order:
            print(f"{arm} {n}")
            result = agent.run(arm, provider=args.provider, case=args.case, request_timeout=args.request_timeout,
                               max_retries=args.max_retries)
            scored = record(result, root / f"{arm}-{n}", recorded=bool(args.record), events=events,
                            graph=graph_facts, title=f"Case note: {args.case} case, {arm} arm, run {n}")
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
