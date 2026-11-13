"""Render an agent's structured output as a case note.

The rendering is deterministic: the agent's sections stay apart, every
finding shows the claims it cites, and every claim shows the checker's verdict
beside it. Nothing is reworded.
"""

from __future__ import annotations

import json

from .claims import flatten_claims


def _claim_text(claim: dict) -> str:
    fields = {k: v for k, v in claim.items() if k not in ("id", "type") and v is not None}
    return ", ".join(f"{k}={json.dumps(v)}" for k, v in fields.items())


def render(output: dict | None, verdicts: list[dict], meta: dict, score: dict, title: str) -> str:
    lines = [f"# {title}", ""]
    lines.append(f"Agent output, {'recorded' if meta.get('recorded') else 'live'} run of {meta['started']}: "
                 f"{meta['arm']} arm, model {', '.join(meta['models_served']) or meta['model_requested']} "
                 f"(requested {meta['model_requested']}, effort {meta['effort_setting']}), status {meta['status']}.")
    lines.append("")
    lines.append("Scope: one bounded replay of a synthetic event file, as processed by the run its evidence records. "
                 "Nothing here is a conclusion about data outside it. Recorded relationships are not proof of fraud, "
                 "ownership, identity or causation. The checker validates the structured claims below against the "
                 "original events and the graph; it does not validate the wording of findings.")
    if output is None:
        lines += ["", "The run produced no case note."]
        return "\n".join(lines) + "\n"
    status = {v["claim"]: v["status"] for v in verdicts if v["claim"] is not None}

    lines += ["", "## Findings", ""]
    for f in output["findings"]:
        cited = ", ".join(f"{c} ({status.get(c, 'no such claim')})" for c in f["claim_ids"]) or "no claims cited"
        lines.append(f"- **{f['id']}** {f['statement']}  ")
        lines.append(f"  Claims: {cited}")
    lines += ["", "## Hypotheses", "", "Interpretations the data does not establish.", ""]
    for h in output["hypotheses"]:
        refs = ", ".join(h["references"]) or "none"
        lines.append(f"- **{h['id']}** {h['statement']}  ")
        lines.append(f"  References: {refs}")
    lines += ["", "## Unresolved questions", ""]
    for u in output["unresolved"]:
        refs = ", ".join(u["references"]) or "none"
        lines.append(f"- **{u['id']}** {u['question']}  ")
        lines.append(f"  References: {refs}")
    lines += ["", "## Claims, as checked", "", "| Claim | Type | Asserts | Checker |", "|---|---|---|---|"]
    by_id = {v["claim"]: v for v in verdicts}
    for claim in flatten_claims(output["claims"]):
        v = by_id.get(claim.get("id")) if isinstance(claim, dict) else None
        verdict = v["status"] if v else "malformed"
        if v and v["status"] != "supported":
            verdict += f": {v.get('reason') or v['events']}"
        lines.append(f"| {claim.get('id')} | {claim.get('type')} | {_claim_text(claim).replace('|', '/')} | {verdict} |")
    effort = score["effort"]
    total_in = effort["input_tokens"] + effort["cache_creation_input_tokens"] + effort["cache_read_input_tokens"]
    lines += ["", "## Score", ""]
    lines.append(f"Correctness {score['correctness']:.2f} ({sum(score['key'].values())} of {len(score['key'])} "
                 f"required facts covered by supported claims); {score['supported']} of {score['claims']} claims "
                 f"supported; reference validity {score['reference_validity']} ({score['valid_references']} of "
                 f"{score['references']} distinct ids resolve); {effort['tool_calls']} queries "
                 f"({effort['tool_errors']} failed), {effort['requests']} model requests, {total_in} input tokens "
                 f"(cache included) and {effort['output_tokens']} output tokens, {effort['wall_seconds']} s.")
    return "\n".join(lines) + "\n"
