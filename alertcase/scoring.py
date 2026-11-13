"""How one investigation output is scored. The same function scores both arms
of the comparison, with the same checker and the same answer key.

  correctness         share of the answer key's items covered by supported claims
  unsupported claims  claims the checker did not find supported (unsupported,
                      inconsistent or malformed)
  reference validity  share of the distinct ids cited anywhere in the output,
                      prose included, that exist in the bounded dataset; a valid
                      reference says nothing about the sentence around it
  effort              tool calls, model requests, tokens and wall time, from the run

Findings are also checked for structure: a finding must cite claims, and the
claims it cites must exist and be supported.
"""

from __future__ import annotations

from . import answers
from .claims import check_claims, references_in, resolves
from .facts import Facts


def score(output: dict | None, events: Facts, graph: Facts, effort: dict) -> dict:
    if output is None:
        return {"completed": False, "correctness": 0.0, "key": answers.covered(events, [], []),
                "claims": 0, "supported": 0, "unsupported": 0, "references": 0, "valid_references": 0,
                "reference_validity": None, "findings": 0, "findings_without_claims": 0,
                "findings_citing_missing_claims": 0, "findings_citing_unsupported_claims": 0, "effort": effort}
    claims = output.get("claims", [])
    verdicts = check_claims(claims, events, graph)
    key = answers.covered(events, claims, verdicts)
    status = {v["claim"]: v["status"] for v in verdicts if v["claim"] is not None}
    refs = references_in(output)
    valid = [r for r in refs if resolves(*r, events) and resolves(*r, graph)]
    findings = output.get("findings", [])
    return {
        "completed": True,
        "correctness": round(sum(key.values()) / len(key), 4),
        "key": key,
        "claims": len(claims),
        "supported": sum(v["status"] == "supported" for v in verdicts),
        "unsupported": sum(v["status"] != "supported" for v in verdicts),
        "references": len(refs),
        "valid_references": len(valid),
        "reference_validity": round(len(valid) / len(refs), 4) if refs else None,
        "invalid_references": [f"{kind}:{ident}" if kind not in ("indicator", "link", "path", "run") else ident
                               for kind, ident in refs if (kind, ident) not in valid],
        "findings": len(findings),
        "findings_without_claims": sum(not f["claim_ids"] for f in findings),
        "findings_citing_missing_claims": sum(any(c not in status for c in f["claim_ids"]) for f in findings),
        "findings_citing_unsupported_claims": sum(
            any(status.get(c) not in (None, "supported") for c in f["claim_ids"]) for f in findings),
        "effort": effort,
    }
