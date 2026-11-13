#!/usr/bin/env python3
"""Publish a store that clink wrote through connector='relate'.

clink's Relate sink commits batch by batch, so a run that fails part way
leaves part of a graph. This step turns a finished run into a published one,
and refuses unless the run is whole:

  1. clink must have exited 0 without being cancelled: its embedded runner
     returns 0 only when every job reached completion and none reported an
     error, and prints "stopping: cancelling" when a run is cancelled instead;
  2. the transfers in the store must equal the event file, record for record;
  3. only then is the Run record written, naming the dataset, the pipeline,
     the image and the versions;
  4. only then is the store moved to its published path.

A store without a Run record is not a published run, and verify.py fails it.
"""

from __future__ import annotations

import argparse
import os
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import relate  # noqa: E402

from alertcase.events import FIELDS, load_events, sha256_of  # noqa: E402

JOBS = 3  # the three INSERT statements in pipeline/case.sql, one job each


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--events", type=Path, default=Path("data/events.ndjson"))
    parser.add_argument("--pipeline", type=Path, default=Path("pipeline/case.sql"))
    parser.add_argument("--building", type=Path, default=Path("store/case.building.rl"))
    parser.add_argument("--store", type=Path, default=Path("store/case.rl"))
    parser.add_argument("--clink", required=True, help="the clink that ran the pipeline (image reference or build)")
    parser.add_argument("--clink-exit-status", type=int, required=True)
    parser.add_argument("--clink-log", type=Path, required=True, help="what clink printed")
    args = parser.parse_args()

    if args.clink_exit_status != 0:
        raise SystemExit(f"refused     clink exited {args.clink_exit_status}: not every job ended without error")
    if "stopping: cancelling" in args.clink_log.read_text():
        raise SystemExit("refused     the run was cancelled, so its jobs did not all complete")

    events = load_events(args.events)
    dataset_sha256 = sha256_of(args.events)
    conn = relate.connect(str(args.building))
    try:
        if conn.execute("MATCH (r:Run) RETURN count(r) AS n").single()["n"] != 0:
            raise SystemExit("refused     the store already holds a Run record")
        in_store = [dict(r) for r in conn.execute("""
            MATCH (s:Account)-[:SENT]->(t:Transfer)-[:TO]->(d:Account)
            MATCH (t)-[:FROM_DEVICE]->(v:Device)
            RETURN t.id AS transfer_id, s.id AS src, d.id AS dst, t.amount_minor AS amount_minor, t.ts AS ts, v.id AS device""")]
        key = lambda r: tuple(r.get(name) for name in FIELDS)  # noqa: E731
        want, got = Counter(map(key, events)), Counter(map(key, in_store))
        if want != got:
            raise SystemExit(
                "refused     the store's transfers differ from the file: "
                f"{sum((want - got).values())} record(s) of the file are not in the store as written, "
                f"{sum((got - want).values())} transfer(s) in the store are not in the file")
        print(f"reconciled  {len(events)} of {len(events)} records are in the store as written")

        conn.execute("CREATE CONSTRAINT run_id IF NOT EXISTS FOR (n:Run) REQUIRE n.id IS UNIQUE")
        conn.execute("""
            CREATE (:Run {id: $id, replay: 'bounded', route: $route, dataset_sha256: $dataset_sha256,
                          dataset_events: $dataset_events, pipeline: $pipeline, pipeline_sha256: $pipeline_sha256,
                          jobs: $jobs, jobs_completed: $jobs, clink_exit_status: 0, cancelled: false,
                          clink: $clink, relate: $relate, lag_ms: 300000, source_batch_size: 1,
                          fan_in_min_senders: 5, fan_in_window_ms: 3600000, onward_max_gap_ms: 1800000})""",
                     {"id": f"run:{dataset_sha256[:12]}", "route": "connector='relate'", "dataset_sha256": dataset_sha256,
                      "dataset_events": len(events), "pipeline": str(args.pipeline),
                      "pipeline_sha256": sha256_of(args.pipeline), "jobs": JOBS, "clink": args.clink,
                      "relate": relate.__version__})
    finally:
        conn.close()
    os.replace(args.building, args.store)
    print(f"published   {args.store} ({args.store.stat().st_size} bytes), run:{dataset_sha256[:12]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
