"""The claim checker, against the committed store and the event file.

Run from the repository root: .venv/bin/python -m unittest discover -s tests
"""

from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from alertcase import answers, facts
from alertcase.claims import check_claims, flatten_claims, references_in, resolves
from alertcase.graph import Graph

SUSPECT = "fan_in:A-9278:1794301200000"
BENIGN = "fan_in:A-9895:1794319200000"


class CheckerTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.events = facts.from_events("data/events.ndjson")
        with Graph("store/case.rl") as graph:
            cls.graph = facts.from_graph(graph)

    def verdicts(self, *claims: dict) -> list[dict]:
        return check_claims(list(claims), self.events, self.graph)

    def test_the_answer_key_is_supported_and_covers_every_item(self) -> None:
        claims = answers.expected_claims(self.events)
        verdicts = self.verdicts(*claims)
        self.assertEqual({v["status"] for v in verdicts}, {"supported"})
        self.assertTrue(all(answers.covered(self.events, claims, verdicts).values()))

    def test_every_planted_claim_is_rejected_by_both_sources(self) -> None:
        planted = [p["claim"] for p in json.loads(Path("claims/planted.json").read_text())]
        for verdict in self.verdicts(*planted):
            self.assertEqual(verdict["status"], "unsupported", verdict)

    def test_a_route_claim_is_judged_link_by_link(self) -> None:
        path = {"id": "C1", "type": "onward_path", "transfers": ["T0002", "T0007", "T0008", "T0009"],
                "from_indicator": SUSPECT, "ends_at": "A-4989"}
        broken = {**path, "id": "C2", "transfers": ["T0002", "T0008", "T0009"]}
        self.assertEqual([v["status"] for v in self.verdicts(path, broken)], ["supported", "unsupported"])

    def test_a_recorded_claim_with_an_earlier_field_name_is_judged_by_the_same_rule(self) -> None:
        current = {"id": "C1", "type": "onward_path", "transfers": ["T0002", "T0007"],
                   "from_indicator": SUSPECT, "ends_at": "A-5092"}
        earlier = {k if k != "ends_at" else "comes_to_rest_at": v for k, v in current.items()}
        grouped = {"onward_path": [{k: v for k, v in earlier.items() if k != "type"}]}
        for claims in ([current], [earlier], flatten_claims(grouped)):
            flat = flatten_claims(claims)
            self.assertEqual(self.verdicts(*flat)[0]["status"], "unsupported", flat)

    def test_a_shared_device_claim_must_name_every_route_account_that_used_it(self) -> None:
        complete = {"id": "C1", "type": "shared_device", "device": "D-568",
                    "accounts": ["A-2897", "A-5092", "A-9278"], "on_route_of": SUSPECT}
        partial = {**complete, "id": "C2", "accounts": ["A-5092", "A-9278"]}
        none_on_benign = {"id": "C3", "type": "absence", "kind": "no_shared_device_on_route", "subject": BENIGN}
        self.assertEqual([v["status"] for v in self.verdicts(complete, partial, none_on_benign)],
                         ["supported", "unsupported", "supported"])

    def test_malformed_claims_are_not_judged(self) -> None:
        good = {"id": "C1", "type": "count", "pattern": "fan_in_alerts", "value": 2}
        cases = [
            {**good, "extra": 1},
            {**good, "value": "2"},
            {**good, "type": "opinion"},
            {"id": "C1", "type": "absence", "kind": "no_fraud", "subject": BENIGN},
            "not an object",
        ]
        for claim in cases:
            self.assertEqual(self.verdicts(claim)[0]["status"], "malformed", claim)
        duplicated = self.verdicts(good, {**good, "value": 2})
        self.assertEqual([v["status"] for v in duplicated], ["malformed", "malformed"])

    def test_a_claim_on_which_the_events_and_the_graph_disagree_is_inconsistent(self) -> None:
        workdir = Path(tempfile.mkdtemp())
        try:
            altered = workdir / "events.ndjson"
            lines = Path("data/events.ndjson").read_text().splitlines()
            records = [json.loads(line) for line in lines]
            for r in records:
                if r["transfer_id"] == "T0009":
                    r["amount_minor"] += 1
            altered.write_text("".join(json.dumps(r) + "\n" for r in records))
            t = self.events.transfers["T0009"]
            claim = {"id": "C1", "type": "event", "transfer": "T0009", "sender": t["src"], "receiver": t["dst"],
                     "amount_minor": t["amount_minor"], "event_time_ms": t["ts"], "device": t["device"]}
            verdict = check_claims([claim], facts.from_events(altered), self.graph)[0]
            self.assertEqual(verdict["status"], "inconsistent", verdict)
        finally:
            shutil.rmtree(workdir)

    def test_references_are_extracted_whole_and_resolved_against_the_dataset(self) -> None:
        text = (f"{SUSPECT} reached A-4989 by path:T0002>T0007>T0008>T0009, through onward:T0007:T0008; "
                "D-568 and T0099 and path:T0002>T0008")
        refs = references_in({"statement": text})
        self.assertIn(("indicator", SUSPECT), refs)
        self.assertNotIn(("account", "A-9278"), refs)  # inside the indicator id, not cited on its own
        valid = {r: resolves(*r, self.events) for r in refs}
        self.assertTrue(valid[("path", "path:T0002>T0007>T0008>T0009")])
        self.assertFalse(valid[("path", "path:T0002>T0008")])
        self.assertFalse(valid[("transfer", "T0099")])
        self.assertTrue(valid[("device", "D-568")])


if __name__ == "__main__":
    unittest.main()
