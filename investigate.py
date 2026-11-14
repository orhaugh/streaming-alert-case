#!/usr/bin/env python3
"""Run the investigating agent once, live. Needs model access: Claude API
credentials (ANTHROPIC_API_KEY, or an `ant auth login` profile), or, with
--provider bedrock, AWS credentials and AWS_REGION for Amazon Bedrock.

A live run writes to runs/live/<time>-<arm>/, which git ignores, and never
touches the recorded runs. --record NAME writes runs/recorded/NAME/ instead,
and refuses if it exists. Every run is checked and scored the same way.
--smoke sends only a run's first request, to check the provider accepts it,
and writes nothing. --backend mcp sends the graph arm's queries to Relate's own
MCP server (scripts/serve-mcp.sh) instead of the Python library; it needs the relate
command line (scripts/fetch-relate-cli.sh) and requirements-mcp.txt.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from alertcase import agent, facts
from alertcase.cases import CASES
from alertcase.graph import Graph
from alertcase.recording import record


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--arm", choices=sorted(agent.ARMS), default="graph",
                        help="graph: Cypher over the Relate store (default); table: SQL over the same records")
    parser.add_argument("--case", choices=sorted(CASES), default="small",
                        help="small: the 55-transfer case (default); large: 50,000 transfers")
    parser.add_argument("--provider", choices=agent.PROVIDERS, default="anthropic",
                        help="anthropic: the Claude API (default); bedrock: Amazon Bedrock")
    parser.add_argument("--backend", choices=agent.BACKENDS, default="embedded",
                        help="embedded: the graph arm opens the store with relate-db (default); "
                             "mcp: it asks Relate's MCP server, over stdio")
    parser.add_argument("--record", metavar="NAME", help="write runs/recorded/NAME instead of a live run directory")
    parser.add_argument("--smoke", action="store_true", help="send one request and report; write nothing")
    parser.add_argument("--request-timeout", type=float, default=agent.REQUEST_TIMEOUT_S, metavar="SECONDS",
                        help=f"each attempt at a model request (default {agent.REQUEST_TIMEOUT_S}); "
                             "300 for a live demonstration")
    parser.add_argument("--max-retries", type=int, default=agent.MAX_RETRIES, metavar="N",
                        help=f"the SDK's retries of a request that fails or times out (default {agent.MAX_RETRIES}); "
                             "1 for a live demonstration")
    args = parser.parse_args()
    if args.backend == "mcp" and args.arm != "graph":
        parser.error("--backend mcp is for the graph arm")

    problem = agent.missing_credentials(args.provider)
    if problem:
        raise SystemExit(problem)
    if args.smoke:
        try:
            print(json.dumps(agent.smoke(args.arm, args.provider, args.case, request_timeout=args.request_timeout,
                                         max_retries=args.max_retries), indent=2))
        except Exception as error:
            if not agent.provider_error(error):
                raise
            raise SystemExit(f"{type(error).__name__}: {agent.redact(str(error))}")
        return 0

    if args.record:
        directory = Path("runs/recorded") / args.record
    else:
        directory = Path("runs/live") / (f"{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}-{args.case}-{args.arm}"
                                         + ("-mcp" if args.backend == "mcp" else ""))
    if directory.exists():
        raise SystemExit(f"refused     {directory} exists")
    case = CASES[args.case]
    case.unpack()
    events = facts.from_events(case.events)
    with Graph(case.store) as graph:
        graph_facts = facts.from_graph(graph)
    print(f"{'recorded' if args.record else 'live'} run, {args.case} case, {args.arm} arm, {args.backend} backend, "
          f"{args.provider}, model {agent.model_for(args.provider)}, effort {agent.EFFORT}")
    result = agent.run(args.arm, provider=args.provider, case=args.case, backend=args.backend,
                       request_timeout=args.request_timeout, max_retries=args.max_retries)
    scored = record(result, directory, recorded=bool(args.record), events=events, graph=graph_facts,
                    title=f"Case note: fan-in alerts in a bounded replay ({args.case} case)")
    print(f"{result.status}: correctness {scored['correctness']:.2f}, {scored['supported']} of {scored['claims']} "
          f"claims supported, reference validity {scored['reference_validity']}")
    print(f"wrote       {directory}/case_note.md")
    return 0 if result.status == "completed" else 1


if __name__ == "__main__":
    sys.exit(main())
