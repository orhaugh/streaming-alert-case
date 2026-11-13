"""Strict reader for the event file. Imports neither clink nor Relate."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

FIELDS = {"transfer_id": str, "src": str, "dst": str, "amount_minor": int, "ts": int, "device": str}


def load_events(path: str | Path) -> list[dict]:
    """Every line must be a JSON object with exactly the six typed fields.

    Returns the records in file order, which is arrival order. Anything else
    in the file is an error: this is the record of what the dataset contains,
    so it must not skip or coerce.
    """
    events: list[dict] = []
    for number, line in enumerate(Path(path).read_text().splitlines(), start=1):
        try:
            record = json.loads(line)
        except json.JSONDecodeError as error:
            raise ValueError(f"{path}:{number}: not JSON: {error}") from None
        if not isinstance(record, dict) or set(record) != set(FIELDS):
            raise ValueError(f"{path}:{number}: expected exactly the fields {sorted(FIELDS)}")
        for name, kind in FIELDS.items():
            if type(record[name]) is not kind:
                raise ValueError(f"{path}:{number}: {name} is not {kind.__name__}")
        if record["src"] == record["dst"]:
            raise ValueError(f"{path}:{number}: a transfer from an account to itself")
        events.append(record)
    ids = [e["transfer_id"] for e in events]
    if len(set(ids)) != len(ids):
        raise ValueError(f"{path}: transfer_id is not unique")
    return events


def sha256_of(path: str | Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()
