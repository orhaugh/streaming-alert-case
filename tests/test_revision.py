"""Evidence-driven revision of investigative findings (alertcase/revision.py,
alertcase/revision_store.py, revise.py).

The rules and the selection are tested against the reference facts alone, and
the publication against the shipped record in revision/, with no Docker. The
staged scenario itself, with clink, runs in DockerScenarioTest when Docker and
the pinned runtime image are there, and is skipped otherwise.

Run from the repository root: .venv/bin/python -m unittest discover -s tests
"""

from __future__ import annotations

import json
import random
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

import relate

import revise
from alertcase import facts
from alertcase import revision as rv
from alertcase import revision_store as rs
from alertcase.events import load_events

FIRST = load_events("data/events.ndjson")
SHIPPED = Path("revision")
BENIGN = "fan_in:A-9895:1794319200000"
T0041_TS = 1794322200000
MINUTE = 60_000


def transfer(tid: str, src: str, dst: str, ts: int, amount: int = 13000, device: str = "D-785") -> dict:
    return {"transfer_id": tid, "src": src, "dst": dst, "amount_minor": amount, "ts": ts, "device": device}


ARRIVAL = transfer("T0056", "A-1415", "A-6630", T0041_TS + 11 * MINUTE)


def investigation(f: facts.Facts, revision_id: str = "r1") -> tuple[dict[str, dict], list[dict]]:
    """The claims and findings revise.py writes for a revision, without a store."""
    with tempfile.TemporaryDirectory() as scratch:
        ledger = rv.Ledger(Path(scratch) / "ledger.jsonl")
        record = {"id": revision_id, "dataset_sha256": "x" * 64, "events": len(f.transfers)}
        pending, findings = [], []
        for finding, drafts in rv.investigate(f, revision_id):
            ids = rv.assert_claims(ledger, drafts, record, f, pending)
            findings.append({**finding, "claims": ids})
    return {c["id"]: c for c in pending}, findings


def revalidate(claims: dict[str, dict], before: facts.Facts, after: facts.Facts, new: list[dict]):
    """Selection by the rule, incremental revalidation and a full recheck, with
    the reference facts standing in for both sources."""
    selected = rv.select({cid: rv.windows(c, before) for cid, c in claims.items()}, new)
    was = {cid: rv.judge(c, before, before)["status"] for cid, c in claims.items()}
    incremental = {cid: rv.judge(c, after, after)["status"] if cid in selected else was[cid]
                   for cid, c in claims.items()}
    full = {cid: rv.judge(c, after, after)["status"] for cid, c in claims.items()}
    return selected, was, incremental, full


def the_absence_on(claims: dict[str, dict], account: str) -> str:
    """The absence claim about an account, found by its predicate, not its id."""
    return next(cid for cid, c in claims.items()
                if c["type"] == "no_onward_transfer" and c["predicate"]["account"] == account)


class RevisionRulesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.r1 = facts.from_records(FIRST)
        cls.claims, cls.findings = investigation(cls.r1)

    def update(self, *new: dict):
        after = facts.from_records(FIRST + list(new))
        return (after, *revalidate(self.claims, self.r1, after, list(new)))

    def test_every_claim_of_the_case_note_is_supported_where_it_is_asserted(self) -> None:
        self.assertEqual({rv.judge(c, self.r1, self.r1)["status"] for c in self.claims.values()}, {"supported"})
        self.assertEqual({c["type"] for c in self.claims.values()},
                         {"indicator", "onward_reach", "no_onward_transfer"})

    def test_an_absence_records_its_search_scope(self) -> None:
        claim = self.claims[the_absence_on(self.claims, "A-1415")]
        self.assertEqual(claim["predicate"], {"account": "A-1415", "start_ms": T0041_TS, "end_ms": T0041_TS + 30 * MINUTE})
        scope = claim["scope"]
        self.assertEqual(scope["entity"], {"account": "A-1415"})
        self.assertIn("PASSED_ON", scope["pattern"])
        self.assertEqual(scope["interval"], {"start_ms": T0041_TS, "end_ms": T0041_TS + 30 * MINUTE,
                                             "bounds": "both included"})
        self.assertEqual(scope["coverage"]["revision"], "r1")
        self.assertEqual(scope["coverage"]["events"], 55)
        self.assertNotIn("references", claim)

    def test_a_list_of_existing_ids_could_not_see_the_new_transfer(self) -> None:
        cited = {t for c in self.claims.values() for t in c.get("references", {}).get("transfers", [])}
        self.assertNotIn("T0056", cited)
        _, selected, _, _, _ = self.update(ARRIVAL)
        self.assertIn(the_absence_on(self.claims, "A-1415"), selected)

    def test_a_transfer_inside_the_interval_supersedes_the_absence_and_only_for_the_new_revision(self) -> None:
        after, selected, was, incremental, full = self.update(ARRIVAL)
        absence = the_absence_on(self.claims, "A-1415")
        reach = next(cid for cid, c in self.claims.items()
                     if c["type"] == "onward_reach" and c["predicate"]["indicator"] == BENIGN)
        self.assertEqual(sorted(selected), sorted([reach, absence]))
        self.assertEqual(incremental, full)
        self.assertEqual((was[absence], full[absence]), ("supported", "unsupported"))
        self.assertEqual((was[reach], full[reach]), ("supported", "unsupported"))
        self.assertIn("onward:T0041:T0056", rv.judge(self.claims[absence], after, after)["events"])
        # relative to revision 1 it still holds: nothing about r1 changed
        self.assertEqual(rv.judge(self.claims[absence], self.r1, self.r1)["status"], "supported")
        unchanged = [cid for cid in self.claims if cid not in selected]
        self.assertTrue(unchanged)
        self.assertTrue(all(full[cid] == was[cid] == "supported" for cid in unchanged))

    def test_an_unrelated_transfer_leaves_every_finding_as_it_was(self) -> None:
        _, selected, was, incremental, full = self.update(transfer("T0056", "A-2104", "A-4325", T0041_TS + 11 * MINUTE,
                                                                   device="D-786"))
        self.assertEqual(selected, {})
        self.assertEqual(incremental, full)
        self.assertEqual(full, was)

    def test_a_transfer_outside_the_interval_leaves_the_absence_as_it_was(self) -> None:
        absence = the_absence_on(self.claims, "A-1415")
        for minutes in (31, 45, 3 * 60):
            _, selected, _, incremental, full = self.update(transfer("T0056", "A-1415", "A-6630",
                                                                     T0041_TS + minutes * MINUTE))
            self.assertEqual(incremental, full)
            self.assertEqual(full[absence], "supported", minutes)
            self.assertNotIn(absence, selected)
        # the interval's ends are included, as the onward rule's are
        _, selected, _, _, full = self.update(transfer("T0056", "A-1415", "A-6630", T0041_TS + 30 * MINUTE))
        self.assertIn(absence, selected)
        self.assertEqual(full[absence], "unsupported")
        _, selected, _, _, full = self.update(transfer("T0056", "A-1415", "A-6630", T0041_TS + 30 * MINUTE + 1))
        self.assertEqual(full[absence], "supported")

    def test_a_credit_can_make_an_existing_debit_qualify_and_selects_the_absence(self) -> None:
        # A debit already there, 40 minutes after T0041 and so not onward from it;
        # an absence over its time; then a credit 10 minutes before it arrives.
        debit = transfer("T0057", "A-1415", "A-6630", T0041_TS + 40 * MINUTE)
        base = facts.from_records(FIRST + [debit])
        absence = {"id": "X1", "type": "no_onward_transfer",
                   "predicate": {"account": "A-1415", "start_ms": T0041_TS + 35 * MINUTE, "end_ms": T0041_TS + 45 * MINUTE}}
        self.assertEqual(rv.judge(absence, base, base)["status"], "supported")
        credit = transfer("T0058", "A-2104", "A-1415", T0041_TS + 30 * MINUTE, device="D-786")
        after = facts.from_records(FIRST + [debit, credit])
        selected, _, incremental, full = revalidate({"X1": absence}, base, after, [credit])
        self.assertIn("X1", selected)
        self.assertEqual(selected["X1"][0]["role"], "credit")
        self.assertEqual(full["X1"], "unsupported")
        self.assertEqual(incremental, full)

    def test_incremental_revalidation_equals_a_full_recheck_on_random_arrivals(self) -> None:
        """Seeded random arrivals, one and two revisions deep, aimed at the
        claims' windows and their edges. No claim whose verdict changes may go
        unselected, and the carried verdicts must equal a full recheck."""
        rng = random.Random(20261118)
        accounts = sorted(self.r1.accounts | {"A-6630", "A-7001"})
        hot = ["A-1415", "A-4989", "A-9895", "A-9278", "A-5092", "A-2897", "A-6630"]
        edges = sorted({w[k] for c in self.claims.values() for w in rv.windows(c, self.r1) for k in ("start_ms", "end_ms")})
        trials = changed_total = cycles = 0
        for trial in range(400):
            known, claims, before = list(FIRST), dict(self.claims), self.r1
            for depth in range(rng.choice((1, 2))):
                new = []
                for k in range(rng.randint(1, 3)):
                    src = rng.choice(hot if rng.random() < 0.7 else accounts)
                    dst = rng.choice([a for a in (hot if rng.random() < 0.5 else accounts) if a != src])
                    base = rng.choice(edges)
                    ts = base + rng.choice((-1, 0, 1, rng.randint(-40, 40) * MINUTE))
                    new.append(transfer(f"T{1000 + trial * 10 + depth * 4 + k}", src, dst, ts,
                                        device=rng.choice(("D-785", "D-568", "D-999"))))
                try:
                    after = facts.from_records(known + new)
                except ValueError:  # a zero-gap cycle of onward links, which the reference rules refuse
                    cycles += 1
                    break
                selected, was, incremental, full = revalidate(claims, before, after, new)
                changed = {cid for cid in claims if full[cid] != was[cid]}
                self.assertLessEqual(changed, set(selected), f"trial {trial}: missed {changed - set(selected)}")
                self.assertEqual(incremental, full, f"trial {trial}")
                changed_total += len(changed)
                trials += 1
                known, before = known + new, after
        self.assertGreater(trials, 400)        # revisions checked, one or two per trial
        self.assertGreater(changed_total, 50)  # the arrivals did change verdicts, often
        self.assertLess(cycles, 40)

    def test_a_replayed_transfer_adds_nothing_and_a_different_one_under_a_known_id_is_refused(self) -> None:
        t0041 = next(e for e in FIRST if e["transfer_id"] == "T0041")
        new, replayed, conflicting = rv.merge_arrival(FIRST, [dict(t0041)])
        self.assertEqual((new, replayed, conflicting), ([], ["T0041"], []))
        new, replayed, conflicting = rv.merge_arrival(FIRST, [ARRIVAL, dict(ARRIVAL)])
        self.assertEqual(([e["transfer_id"] for e in new], replayed, conflicting), (["T0056"], ["T0056"], []))
        new, replayed, conflicting = rv.merge_arrival(FIRST, [{**t0041, "amount_minor": 1}])
        self.assertEqual(conflicting, ["T0041"])
        self.assertEqual(rv.dataset_digest(FIRST + [ARRIVAL]), rv.dataset_digest([ARRIVAL] + FIRST))

    def test_the_lateness_check(self) -> None:
        [late] = rv.lateness(FIRST, [ARRIVAL])
        self.assertFalse(late["accepted"])
        self.assertEqual(late["watermark_ms"], max(e["ts"] for e in FIRST) - 300_000)
        self.assertEqual(rv.duration(late["behind_ms"]), "2 h 59 min")
        self.assertEqual([(p["transfer"], p["as"], p["closed"]) for p in late["partners"]], [("T0041", "credit", True)])
        [early] = rv.lateness(FIRST, [transfer("T0056", "A-1415", "A-6630", max(e["ts"] for e in FIRST) + MINUTE)])
        self.assertTrue(early["accepted"])


class PipelineTest(unittest.TestCase):
    def test_the_recomputation_runs_the_case_jobs_statement_for_statement(self) -> None:
        case, revision = Path("pipeline/case.sql").read_text(), Path("pipeline/revision.sql").read_text()
        jobs = lambda text: text[text.index("-- 1. Every transfer"):]  # noqa: E731
        self.assertEqual(jobs(revision), jobs(case).replace("store/case.building.rl", "store/evidence.building.rl"))
        self.assertEqual(re.findall(r"watermark_lag_ms\s*=\s*'(\d+)'", revision), [str(rv.LAG_MS)] * 2)
        self.assertEqual(re.findall(r"watermark_lag_ms\s*=\s*'(\d+)'", case), [str(rv.LAG_MS)])

    def test_the_same_image_as_the_rebuild(self) -> None:
        self.assertIn(f'IMAGE="{revise.IMAGE}"', Path("rebuild.sh").read_text())


class LedgerTest(unittest.TestCase):
    def test_the_ledger_is_append_only_and_tamper_evident(self) -> None:
        with tempfile.TemporaryDirectory() as scratch:
            path = Path(scratch) / "ledger.jsonl"
            ledger = rv.Ledger(path)
            ledger.append([{"kind": "claim", "id": "C1"}, {"kind": "claim", "id": "C2"}])
            first = path.read_bytes()
            ledger.append([{"kind": "claim", "id": "C3"}])
            self.assertTrue(path.read_bytes().startswith(first))
            self.assertEqual([r["seq"] for r in rv.Ledger(path).records], [1, 2, 3])
            lines = path.read_text().splitlines()
            lines[1] = lines[1].replace('"C2"', '"C9"')
            path.write_text("\n".join(lines) + "\n")
            with self.assertRaises(rv.LedgerError):
                rv.Ledger(path)


def strip_to_evidence(store: Path, into: Path) -> None:
    """A copy of a published revision store holding clink's evidence alone, as
    clink wrote it: the investigation and the run record removed."""
    shutil.copyfile(store, into)
    conn = relate.connect(str(into))
    try:
        for label in rs.LAYER:
            conn.execute(f"MATCH (n:{label}) DETACH DELETE n")
    finally:
        conn.close()


def r1_only(into: Path) -> rv.Ledger:
    """The shipped investigation as it stood when only revision 1 was published."""
    into.mkdir(parents=True, exist_ok=True)
    shipped = rv.Ledger(SHIPPED / "ledger.jsonl")
    through = len(shipped.through("r1"))
    (into / "ledger.jsonl").write_text("".join(line + "\n" for line in shipped.lines[:through]))
    for name in ("r1.rl", "r1-case-note.md"):
        shutil.copyfile(SHIPPED / name, into / name)
    return rv.Ledger(into / "ledger.jsonl")


class PublicationTest(unittest.TestCase):
    """Against the shipped record, with clink's own evidence and no Docker."""

    def setUp(self) -> None:
        self.scratch = Path(tempfile.mkdtemp())
        self.staging, revise.STAGING = revise.STAGING, self.scratch / "stage"
        self.evidence = self.scratch / "r2-evidence.rl"
        strip_to_evidence(SHIPPED / "r2.rl", self.evidence)

    def tearDown(self) -> None:
        revise.STAGING = self.staging
        shutil.rmtree(self.scratch, ignore_errors=True)

    def runner(self, store: Path | None, status: int = 0, log: str = ""):
        def run(stage: Path) -> tuple[int, str]:
            if store is not None:
                shutil.copyfile(store, stage / "store" / "evidence.building.rl")
            return status, log
        return run

    def test_the_shipped_investigation_verifies(self) -> None:
        results = []
        rs.verify_investigation(SHIPPED, lambda name, ok, detail: results.append((name, ok, detail)))
        self.assertTrue(results)
        self.assertEqual([r for r in results if not r[1]], [])

    def test_publishing_clinks_evidence_again_gives_the_shipped_record(self) -> None:
        out = self.scratch / "out"
        r1_only(out)
        result = revise.apply(out, revise.ARRIVAL, runner=self.runner(self.evidence))
        self.assertEqual(result["outcome"], "published")
        again, shipped = rv.Ledger(out / "ledger.jsonl"), rv.Ledger(SHIPPED / "ledger.jsonl")
        strip = lambda r: {k: v for k, v in r.items() if k not in ("prev", "store_sha256")}  # noqa: E731
        self.assertEqual([strip(r) for r in again.records], [strip(r) for r in shipped.records])
        for name in ("r2-amendment.md", "arrivals/r2.ndjson"):
            self.assertEqual((out / name).read_bytes(), (SHIPPED / name).read_bytes(), name)

    def test_a_failed_update_publishes_nothing(self) -> None:
        out = self.scratch / "out"
        ledger = r1_only(out)
        before = (out / "ledger.jsonl").read_bytes()
        r1_store = out / "r1-evidence.rl"
        strip_to_evidence(out / "r1.rl", r1_store)
        failures = {
            "clink exited 1": self.runner(self.evidence, status=1),
            "cancelled": self.runner(self.evidence, log="stopping: cancelling"),
            "no store": self.runner(None),
            "the new transfer missing from the store": self.runner(r1_store),
        }
        for name, runner in failures.items():
            with self.subTest(name), self.assertRaises(revise.Refused):
                revise.apply(out, revise.ARRIVAL, runner=runner)
            self.assertEqual((out / "ledger.jsonl").read_bytes(), before, name)
            self.assertEqual(rv.Ledger(out / "ledger.jsonl").published()["revision"], "r1", name)
            self.assertFalse((out / "r2.rl").exists() or (out / "r2-amendment.md").exists(), name)
        # and revision 1 is still published and whole
        results = []
        rs.verify_investigation(out, lambda name, ok, detail: results.append(ok))
        self.assertTrue(all(results))
        self.assertEqual(len(ledger.records), len(rv.Ledger(out / "ledger.jsonl").records))

    def test_the_same_arrival_again_adds_no_evidence_and_no_amendment(self) -> None:
        out = self.scratch / "out"
        shutil.copytree(SHIPPED, out)
        before = {p.relative_to(out): p.read_bytes() for p in out.rglob("*") if p.is_file()}
        result = revise.apply(out, revise.ARRIVAL, runner=self.runner(None, status=99))
        self.assertEqual((result["outcome"], result["replayed"]), ("nothing new", ["T0056"]))
        after = {p.relative_to(out): p.read_bytes() for p in out.rglob("*") if p.is_file()}
        self.assertEqual(after, before)
        ledger = rv.Ledger(out / "ledger.jsonl")
        self.assertEqual(len(ledger.of("amendment")), 1)
        with revise.Graph(out / "r2.rl") as graph:
            self.assertEqual(graph.rows("MATCH (t:Transfer {id: 'T0056'}) RETURN count(t) AS n")[0]["n"], 1)
            self.assertEqual(graph.rows("MATCH ()-[l:PASSED_ON {id: 'onward:T0041:T0056'}]->() RETURN count(l) AS n")[0]["n"], 1)

    def test_the_historical_note_and_its_evidence_remain_inspectable(self) -> None:
        ledger = rv.Ledger(SHIPPED / "ledger.jsonl")
        r1 = next(p for p in ledger.of("publication") if p["revision"] == "r1")
        self.assertEqual(rv.sha256_file(SHIPPED / "r1-case-note.md"), r1["note_sha256"])
        claims = ledger.claims()
        absence = the_absence_on({c: claims[c] for c in claims if claims[c]["revision"] == "r1"}, "A-1415")
        self.assertEqual([(v["revision"], v["status"]) for v in ledger.history(absence)],
                         [("r1", "supported"), ("r2", "unsupported")])
        for revision_id, want in (("r1", "supported"), ("r2", "unsupported")):
            dataset = rv.dataset_of(SHIPPED, ledger.revision(revision_id))
            with revise.Graph(SHIPPED / f"{revision_id}.rl") as graph:
                graph_facts = facts.from_graph(graph)
                history = graph.rows("MATCH (v:Validation)-[:OF]->(:Claim {id: $id}) RETURN v.revision AS revision, "
                                     "v.status AS status ORDER BY revision", id=absence)
            self.assertEqual(rv.judge(claims[absence], facts.from_records(dataset), graph_facts)["status"], want)
            self.assertEqual(history, [{"revision": "r1", "status": "supported"}]
                             + ([{"revision": "r2", "status": "unsupported"}] if revision_id == "r2" else []))
        [amendment] = ledger.of("amendment")
        [superseded] = amendment["superseded"]
        self.assertEqual(superseded["revision"], "r1")
        self.assertIn(absence, [c["claim"] for c in superseded["claims"]])
        self.assertEqual([e["transfer_id"] for e in amendment["new_events"]], ["T0056"])
        self.assertEqual(amendment["changes"]["links"], ["onward:T0041:T0056"])
        replacement = ledger.findings()[superseded["replacement"]]
        self.assertTrue(all(ledger.validation(c, "r2")["status"] == "supported" for c in replacement["claims"]))
        self.assertIn("T0038, T0041, T0056", replacement["statement"])


def docker_ready() -> str | None:
    if shutil.which("docker") is None:
        return "no docker command"
    if subprocess.run(["docker", "image", "inspect", revise.IMAGE], capture_output=True).returncode != 0:
        return f"the pinned image is not present locally (docker pull {revise.IMAGE})"
    return None


@unittest.skipIf(docker_ready(), docker_ready() or "")
class DockerScenarioTest(unittest.TestCase):
    """The staged scenario with clink itself: revision 1 once, then each arrival."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.scratch = Path(tempfile.mkdtemp())
        cls.staging, revise.STAGING = revise.STAGING, cls.scratch / "stage"
        cls.base = cls.scratch / "base"
        revise.initial(cls.base)

    @classmethod
    def tearDownClass(cls) -> None:
        revise.STAGING = cls.staging
        shutil.rmtree(cls.scratch, ignore_errors=True)

    def apply(self, name: str, *new: dict, append_to_stream: bool = False) -> tuple[Path, dict]:
        out = self.scratch / name
        shutil.copytree(self.base, out)
        arrival = self.scratch / f"{name}.ndjson"
        arrival.write_text("".join(json.dumps(e) + "\n" for e in new))
        return out, revise.apply(out, arrival, append_to_stream=append_to_stream)

    def verified(self, out: Path) -> list:
        results = []
        rs.verify_investigation(out, lambda name, ok, detail: results.append((name, ok, detail)))
        return [r for r in results if not r[1]]

    def test_the_arrival_supersedes_the_absence(self) -> None:
        out, result = self.apply("arrival", ARRIVAL)
        self.assertEqual(result["outcome"], "published")
        ledger = rv.Ledger(out / "ledger.jsonl")
        [amendment] = ledger.of("amendment")
        self.assertEqual([s["finding"] for s in amendment["superseded"]],
                         [f["id"] for f in ledger.of("finding")
                          if f["subject"] == BENIGN and f["about"] == "paths" and f["revision"] == "r1"])
        self.assertEqual(self.verified(out), [])

    def test_unrelated_and_outside_the_interval(self) -> None:
        for name, arrival in (("unrelated", transfer("T0056", "A-2104", "A-4325", T0041_TS + 11 * MINUTE, device="D-786")),
                              ("outside", transfer("T0056", "A-1415", "A-6630", T0041_TS + 45 * MINUTE))):
            with self.subTest(name):
                out, result = self.apply(name, arrival)
                ledger = rv.Ledger(out / "ledger.jsonl")
                self.assertEqual(result["outcome"], "published")
                self.assertEqual(ledger.of("amendment"), [])
                self.assertEqual({v["status"] for v in ledger.of("validation")}, {"supported"})
                self.assertTrue((out / "r2-revalidation.md").exists())
                self.assertEqual(self.verified(out), [])

    def test_appended_to_the_stream_nothing_unverified_is_published(self) -> None:
        """Late in one input, whether clink pairs T0056 with T0041 varies from
        run to run. Either the gates refuse and nothing changes, or the link is
        there and the published revision verifies."""
        outcomes = set()
        for attempt in range(3):
            out = self.scratch / f"appended{attempt}"
            try:
                self.apply(f"appended{attempt}", ARRIVAL, append_to_stream=True)
            except revise.Refused as refused:
                self.assertIn("missing ['onward:T0041:T0056']", str(refused))
                self.assertEqual((out / "ledger.jsonl").read_bytes(), (self.base / "ledger.jsonl").read_bytes())
                self.assertFalse((out / "r2.rl").exists())
                outcomes.add("refused")
            else:
                self.assertEqual(self.verified(out), [])
                self.assertEqual(rv.Ledger(out / "ledger.jsonl").revision("r2")["new_links"], ["onward:T0041:T0056"])
                outcomes.add("published")
        self.assertTrue(outcomes)

    def test_the_same_arrival_twice(self) -> None:
        out, first = self.apply("twice", ARRIVAL, ARRIVAL)
        self.assertEqual((first["outcome"], first["replayed"]), ("published", ["T0056"]))
        before = (out / "ledger.jsonl").read_bytes()
        again = revise.apply(out, self.scratch / "twice.ndjson")
        self.assertEqual(again["outcome"], "nothing new")
        self.assertEqual((out / "ledger.jsonl").read_bytes(), before)
        self.assertEqual(self.verified(out), [])


if __name__ == "__main__":
    unittest.main()
