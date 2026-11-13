#!/usr/bin/env python3
"""Write a published store's records into SQLite tables, for the table-based
side of the comparison. Same records, rows instead of a graph."""

from __future__ import annotations

import argparse
import sys

from alertcase import tables
from alertcase.cases import CASES
from alertcase.graph import Graph


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--case", choices=sorted(CASES), default="small")
    args = parser.parse_args()
    case = CASES[args.case]
    with Graph(case.store) as graph:
        path = tables.export(graph, case.tables, indexes=case.table_indexes)
    print(f"exported    {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
