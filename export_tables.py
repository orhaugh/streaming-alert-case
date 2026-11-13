#!/usr/bin/env python3
"""Write the published store's records into tables/case.sqlite, for the
table-based side of the comparison. Same records, rows instead of a graph."""

from __future__ import annotations

import sys
from pathlib import Path

from alertcase import tables
from alertcase.graph import Graph


def main() -> int:
    with Graph(Path("store/case.rl")) as graph:
        path = tables.export(graph)
    print(f"exported    {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
