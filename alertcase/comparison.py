"""The comparison's summary, computed from the scores recorded beside each run.

compare.py writes summary.json with it, and verify.py computes it again from
the same files and fails if the two differ. Every number in the summary comes
from a recorded run; none is entered by hand.
"""

from __future__ import annotations

import json
from pathlib import Path
from statistics import mean


def _total_input(effort: dict) -> int:
    return effort["input_tokens"] + effort["cache_creation_input_tokens"] + effort["cache_read_input_tokens"]


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
                                                    "tool_calls", "tool_errors", "requests", "input_tokens_total",
                                                    "output_tokens", "wall_seconds")},
            "per_run": runs,
        }
    return summary
