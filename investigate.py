#!/usr/bin/env python3
"""Run the investigating agent once, live. Needs Anthropic API credentials
(ANTHROPIC_API_KEY, or an `ant auth login` profile).

A live run writes to runs/live/<time>-<arm>/, which git ignores, and never
touches the recorded runs. --record NAME writes runs/recorded/NAME/ instead,
and refuses if it exists. Every run is checked and scored the same way.
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

from alertcase import agent, facts
from alertcase.graph import Graph
from alertcase.recording import record


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--arm", choices=sorted(agent.ARMS), default="graph",
                        help="graph: Cypher over the Relate store (default); table: SQL over the same records")
    parser.add_argument("--record", metavar="NAME", help="write runs/recorded/NAME instead of a live run directory")
    args = parser.parse_args()

    if args.record:
        directory = Path("runs/recorded") / args.record
    else:
        directory = Path("runs/live") / f"{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}-{args.arm}"
    if directory.exists():
        raise SystemExit(f"refused     {directory} exists")
    if not agent.have_credentials():
        raise SystemExit(agent.NO_CREDENTIALS)
    events = facts.from_events()
    with Graph() as graph:
        graph_facts = facts.from_graph(graph)
    print(f"{'recorded' if args.record else 'live'} run, {args.arm} arm, model {agent.MODEL}, effort {agent.EFFORT}")
    result = agent.run(args.arm)
    scored = record(result, directory, recorded=bool(args.record), events=events, graph=graph_facts,
                    title="Case note: fan-in alerts in a bounded replay")
    print(f"{result.status}: correctness {scored['correctness']:.2f}, {scored['supported']} of {scored['claims']} "
          f"claims supported, reference validity {scored['reference_validity']}")
    print(f"wrote       {directory}/case_note.md")
    return 0 if result.status == "completed" else 1


if __name__ == "__main__":
    sys.exit(main())
