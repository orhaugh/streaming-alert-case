"""The comparison's summary, computed from the scores recorded beside each run.

compare.py writes summary.json with it, and verify.py computes it again from
the same files and fails if the two differ. Every number in the summary comes
from a recorded run; none is entered by hand.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from statistics import mean


def _total_input(effort: dict) -> int:
    return effort["input_tokens"] + effort["cache_creation_input_tokens"] + effort["cache_read_input_tokens"]


def traversal(run: Path, arm: str) -> dict:
    """How a run's queries followed onward links in the database. path_queries:
    a variable-length pattern (Cypher) or a recursive query (SQL), any number of
    links in one query. multi_hop_queries: two or more onward links written out
    in one query."""
    calls = [e for e in json.loads((run / "transcript.json").read_text()) if "tool_call" in e]
    if arm == "graph":
        path = sum(bool(re.search(r"\[\w*:\w+\*|\[\*", c["query"])) for c in calls)
        hops = sum(c["query"].count("PASSED_ON") >= 2 and not re.search(r"\[\w*:\w+\*|\[\*", c["query"]) for c in calls)
    else:
        path = sum(bool(re.search(r"WITH\s+RECURSIVE", c["query"], re.I)) for c in calls)
        hops = sum(len(re.findall(r"\bonward_links\b", c["query"], re.I)) >= 2
                   and not re.search(r"WITH\s+RECURSIVE", c["query"], re.I) for c in calls)
    return {"path_queries": path, "multi_hop_queries": hops}


def summarise(directory: Path) -> dict:
    arms: dict[str, list[dict]] = {}
    for meta_path in sorted(directory.glob("*/meta.json")):
        run = meta_path.parent
        meta = json.loads(meta_path.read_text())
        scored = json.loads((run / "score.json").read_text())
        arms.setdefault(meta["arm"], []).append({
            "run": run.name,
            "status": meta["status"],
            "models_served": meta["models_served"],
            "fallback_used": meta["fallback_used"],
            "correctness": scored["correctness"],
            "claims": scored["claims"],
            "unsupported_claims": scored["unsupported"],
            "reference_validity": scored["reference_validity"],
            "findings_citing_unsupported_claims": scored["findings_citing_unsupported_claims"],
            "tool_calls": scored["effort"]["tool_calls"],
            "tool_errors": scored["effort"]["tool_errors"],
            "truncated_results": scored["effort"].get("truncated_results"),
            "stopped_queries": scored["effort"].get("stopped_queries"),
            **traversal(run, meta["arm"]),
            "requests": scored["effort"]["requests"],
            "input_tokens_total": _total_input(scored["effort"]),
            "output_tokens": scored["effort"]["output_tokens"],
            "wall_seconds": scored["effort"]["wall_seconds"],
        })
    summary = {}
    for arm, runs in sorted(arms.items()):
        def avg(name: str):
            values = [r[name] for r in runs if r[name] is not None]
            return round(mean(values), 4) if values else None
        summary[arm] = {
            "runs": len(runs),
            "completed": sum(r["status"] == "completed" for r in runs),
            "served_by_a_fallback_model": sum(r["fallback_used"] for r in runs),
            "mean": {name: avg(name) for name in ("correctness", "claims", "unsupported_claims", "reference_validity",
                                                    "tool_calls", "tool_errors", "truncated_results", "stopped_queries",
                                                    "path_queries", "multi_hop_queries", "requests",
                                                    "input_tokens_total", "output_tokens", "wall_seconds")},
            "per_run": runs,
        }
    return summary
