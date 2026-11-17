"""The two bounded datasets this repository investigates.

small  the case itself: 55 transfers, two alerts; the store ships as it is.
large  the same pipeline at scale: 50,000 transfers, six alerts and decoys,
       far more than an agent can read through its query tool or a model's
       context can hold. Its store and tables ship gzipped, and are unpacked
       byte for byte on first use, and again whenever the shipped copy changes.

Beside each unpacked copy, <file>.unpacked-from holds the sha256 of the
gzipped copy it came from. A copy without it, or unpacked from another
version, is unpacked again: a pull that brings rebuilt stores would otherwise
leave the old ones in place, and every check would run against them.
scripts/serve-mcp.sh applies the same rule.
"""

from __future__ import annotations

import gzip
import os
import shutil
from dataclasses import dataclass
from pathlib import Path

from .events import sha256_of


@dataclass(frozen=True)
class Case:
    name: str
    events: Path
    scenario: Path
    pipeline: Path
    store: Path
    tables: Path
    planted: Path
    max_tokens: int       # per response: the large case's case note is longer
    table_indexes: bool   # indexes on every id the tables join on

    def packed(self, path: Path) -> Path:
        return path.with_name(path.name + ".gz")

    @staticmethod
    def source_record(path: Path) -> Path:
        return path.with_name(path.name + ".unpacked-from")

    def unpack(self) -> None:
        """Unpacks the shipped store and tables unless the copies there were
        unpacked from these very gzipped copies. Replaces a copy atomically."""
        for path in (self.store, self.tables):
            packed = self.packed(path)
            if not packed.exists():
                continue
            digest, record = sha256_of(packed), self.source_record(path)
            if path.exists() and record.exists() and record.read_text().strip() == digest:
                continue
            partial = path.with_name(f"{path.name}.unpacking.{os.getpid()}")
            try:
                with gzip.open(packed, "rb") as src, open(partial, "wb") as dst:
                    shutil.copyfileobj(src, dst)
                os.replace(partial, path)
            finally:
                partial.unlink(missing_ok=True)
            record.write_text(digest + "\n")

    def pack(self) -> None:
        """Writes the gzipped copies a rebuild ships, without a timestamp, so the
        same store always packs to the same bytes, and records that the copies
        in place are the ones packed."""
        for path in (self.store, self.tables):
            with open(path, "rb") as src, open(self.packed(path), "wb") as raw, \
                    gzip.GzipFile(filename="", mode="wb", fileobj=raw, compresslevel=9, mtime=0) as dst:
                shutil.copyfileobj(src, dst)
            self.source_record(path).write_text(sha256_of(self.packed(path)) + "\n")


CASES = {
    "small": Case("small", Path("data/events.ndjson"), Path("data/scenario.json"), Path("pipeline/case.sql"),
                  Path("store/case.rl"), Path("tables/case.sqlite"), Path("claims/planted.json"),
                  max_tokens=16000, table_indexes=False),
    "large": Case("large", Path("data/large/events.ndjson"), Path("data/large/scenario.json"),
                  Path("pipeline/large.sql"), Path("store/large.rl"), Path("tables/large.sqlite"),
                  Path("claims/planted-large.json"), max_tokens=32000, table_indexes=True),
}
