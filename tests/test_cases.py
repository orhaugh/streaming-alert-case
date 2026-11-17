"""Unpacking the large case's shipped copies: on first use, and again whenever
the shipped copy changes, so a pull that brings rebuilt stores is never
checked against the stores it replaced."""

from __future__ import annotations

import gzip
import hashlib
import shutil
import tempfile
import unittest
from pathlib import Path

from alertcase.cases import Case


class UnpackTest(unittest.TestCase):
    def setUp(self) -> None:
        self.dir = Path(tempfile.mkdtemp())
        self.case = Case("test", self.dir / "events.ndjson", self.dir / "scenario.json", self.dir / "case.sql",
                         self.dir / "store.rl", self.dir / "tables.sqlite", self.dir / "planted.json",
                         max_tokens=1, table_indexes=False)

    def tearDown(self) -> None:
        shutil.rmtree(self.dir)

    def ship(self, store: bytes, tables: bytes) -> None:
        """What a pull brings: new gzipped copies, and nothing else."""
        for path, data in ((self.case.store, store), (self.case.tables, tables)):
            self.case.packed(path).write_bytes(gzip.compress(data, mtime=0))

    def held(self) -> tuple[bytes, bytes]:
        return self.case.store.read_bytes(), self.case.tables.read_bytes()

    def test_first_use_unpacks_and_records_the_source(self) -> None:
        self.ship(b"store v1", b"tables v1")
        self.case.unpack()
        self.assertEqual(self.held(), (b"store v1", b"tables v1"))
        packed = self.case.packed(self.case.store)
        self.assertEqual(Case.source_record(self.case.store).read_text().strip(),
                         hashlib.sha256(packed.read_bytes()).hexdigest())

    def test_a_pull_that_brings_new_copies_replaces_the_old_ones(self) -> None:
        self.ship(b"store v1", b"tables v1")
        self.case.unpack()
        self.ship(b"store v2", b"tables v2")
        self.case.unpack()
        self.assertEqual(self.held(), (b"store v2", b"tables v2"))

    def test_a_copy_with_no_record_of_its_source_is_unpacked_again(self) -> None:
        self.ship(b"store v2", b"tables v2")
        self.case.store.write_bytes(b"store v1, unpacked before the record existed")
        self.case.tables.write_bytes(b"tables v1")
        self.case.unpack()
        self.assertEqual(self.held(), (b"store v2", b"tables v2"))

    def test_a_current_copy_is_left_alone(self) -> None:
        self.ship(b"store v1", b"tables v1")
        self.case.unpack()
        before = self.case.store.stat().st_ino
        self.case.unpack()
        self.assertEqual(self.case.store.stat().st_ino, before)
        self.assertEqual(sorted(p.name for p in self.dir.iterdir()),
                         sorted(["store.rl", "store.rl.gz", "store.rl.unpacked-from",
                                 "tables.sqlite", "tables.sqlite.gz", "tables.sqlite.unpacked-from"]))

    def test_packing_records_that_the_copies_in_place_are_current(self) -> None:
        self.case.store.write_bytes(b"store built here")
        self.case.tables.write_bytes(b"tables built here")
        self.case.pack()
        before = self.case.store.stat().st_ino
        self.case.unpack()
        self.assertEqual(self.case.store.stat().st_ino, before)
        self.assertEqual(self.held(), (b"store built here", b"tables built here"))


if __name__ == "__main__":
    unittest.main()
