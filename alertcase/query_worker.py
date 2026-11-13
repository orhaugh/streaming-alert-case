"""Runs read-only Cypher queries in a process of its own, so that the agent's
harness can stop a query that runs too long: relate-db 1.0.1 has no timeout.

The worker opens the store once (a read-only open loads it), writes
{"ready": true}, then answers one query per line: it reads {"query": "..."}
and writes {"rows": [the first LIMIT rows], "row_count": n} or
{"error": "..."}, each as one line of JSON.

    python -m alertcase.query_worker <store> <limit>
"""

from __future__ import annotations

import json
import sys

from .graph import Graph


def answer(graph: Graph, query: str, limit: int) -> dict:
    try:
        rows, count = [], 0
        for record in graph.conn.execute(query, {}):
            if count < limit:
                rows.append(dict(record))
            count += 1
        return {"rows": rows, "row_count": count}
    except Exception as error:  # Relate explains what is wrong and how to fix it
        return {"error": str(error)}


def main() -> int:
    store, limit = sys.argv[1], int(sys.argv[2])
    with Graph(store) as graph:
        print(json.dumps({"ready": True}), flush=True)
        for line in sys.stdin:
            request = json.loads(line)
            print(json.dumps(answer(graph, request["query"], limit), default=str), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
