"""The two bounded datasets this repository investigates.

small  the case itself: 55 transfers, two alerts; the store ships as it is.
large  the same pipeline at scale: 50,000 transfers, six alerts and decoys,
       far more than an agent can read through its query tool or a model's
       context can hold. Its store and tables ship gzipped, and are unpacked
       byte for byte on first use.
"""

from __future__ import annotations

import gzip
import shutil
from dataclasses import dataclass
from pathlib import Path


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

    def unpack(self) -> None:
        """Unpacks the shipped store and tables if they are not there yet."""
        for path in (self.store, self.tables):
            packed = self.packed(path)
            if not path.exists() and packed.exists():
                with gzip.open(packed, "rb") as src, open(path, "wb") as dst:
                    shutil.copyfileobj(src, dst)

    def pack(self) -> None:
        """Writes the gzipped copies a rebuild ships, without a timestamp, so the
        same store always packs to the same bytes."""
        for path in (self.store, self.tables):
            with open(path, "rb") as src, open(self.packed(path), "wb") as raw, \
                    gzip.GzipFile(filename="", mode="wb", fileobj=raw, compresslevel=9, mtime=0) as dst:
                shutil.copyfileobj(src, dst)


CASES = {
    "small": Case("small", Path("data/events.ndjson"), Path("data/scenario.json"), Path("pipeline/case.sql"),
                  Path("store/case.rl"), Path("tables/case.sqlite"), Path("claims/planted.json"),
                  max_tokens=16000, table_indexes=False),
    "large": Case("large", Path("data/large/events.ndjson"), Path("data/large/scenario.json"),
                  Path("pipeline/large.sql"), Path("store/large.rl"), Path("tables/large.sqlite"),
                  Path("claims/planted-large.json"), max_tokens=32000, table_indexes=True),
}
