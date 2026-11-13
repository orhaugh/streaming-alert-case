"""Write one agent run to its directory, checked and scored.

  meta.json        what ran: arm, model requested and served, settings, budgets,
                   versions, hashes of the evidence and the prompts, effort
  transcript.json  every response and every query with its result
  output.json      the agent's structured case note (absent if it produced none)
  check.json       the checker's verdict on every claim
  score.json       the score (scoring.py)
  case_note.md     the case note rendered from output.json and check.json

verify.py recomputes check.json and score.json from output.json and meta.json
and fails if they differ.
"""

from __future__ import annotations

import json
from pathlib import Path

from . import casenote
from .agent import RunResult
from .claims import check_claims
from .facts import Facts
from .scoring import score


def _write(path: Path, value) -> None:
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")


def record(result: RunResult, directory: Path, recorded: bool, events: Facts, graph: Facts, title: str) -> dict:
    directory.mkdir(parents=True, exist_ok=False)
    meta = {**result.meta, "recorded": recorded, "name": directory.name}
    verdicts = check_claims(result.output["claims"], events, graph) if result.output else []
    scored = score(result.output, events, graph, meta["effort"])
    _write(directory / "meta.json", meta)
    _write(directory / "transcript.json", result.transcript)
    if result.output is not None:
        _write(directory / "output.json", result.output)
    _write(directory / "check.json", verdicts)
    _write(directory / "score.json", scored)
    (directory / "case_note.md").write_text(casenote.render(result.output, verdicts, meta, scored, title))
    return scored
