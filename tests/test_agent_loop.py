"""The agent harness, driven by a scripted stand-in for the API client.

These tests exercise the loop, the read-only query tools, the budgets and the
recording. The stand-in's replies are scripted here; they are not model
output and nothing in them is reported as a result.
"""

from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from alertcase import agent, answers, facts
from alertcase.graph import Graph
from alertcase.recording import record


def usage() -> SimpleNamespace:
    return SimpleNamespace(input_tokens=100, output_tokens=20, cache_creation_input_tokens=0,
                           cache_read_input_tokens=0, iterations=None)


def response(content: list, stop_reason: str) -> SimpleNamespace:
    r = SimpleNamespace(content=content, stop_reason=stop_reason, model=agent.MODEL, usage=usage())
    r.to_dict = lambda: {"stop_reason": stop_reason, "content": [vars(b) for b in content]}
    return r


def tool_use(query: str, n: int = 1) -> SimpleNamespace:
    return response([SimpleNamespace(type="tool_use", id=f"tu{n}", name="query",
                                     input={"query": query, "purpose": "scripted"})], "tool_use")


def final(output: dict) -> SimpleNamespace:
    return response([SimpleNamespace(type="text", text=json.dumps(output))], "end_turn")


class ScriptedClient:
    def __init__(self, replies) -> None:
        self.replies = replies
        self.requests: list[dict] = []
        self.beta = SimpleNamespace(messages=SimpleNamespace(create=self.create))

    def create(self, **kwargs):
        self.requests.append(kwargs)
        return self.replies(len(self.requests))


class AgentLoopTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.events = facts.from_events("data/events.ndjson")
        with Graph("store/case.rl") as graph:
            cls.graph = facts.from_graph(graph)
        claims = answers.expected_claims(cls.events)
        cls.output = {"findings": [{"id": "F1", "statement": "scripted", "claim_ids": [c["id"] for c in claims]}],
                      "hypotheses": [], "unresolved": [], "claims": claims}

    def run_arm(self, arm: str, query: str):
        script = {1: tool_use(query), 2: final(self.output)}
        client = ScriptedClient(lambda n: script[n])
        return agent.run(arm, client=client, log=lambda _: None), client

    def test_each_arm_queries_its_own_evidence_read_only(self) -> None:
        for arm, query in (("graph", "MATCH (i:Indicator) RETURN i.id AS id ORDER BY id"),
                           ("table", "SELECT indicator_id AS id FROM fan_in_alerts ORDER BY id")):
            result, client = self.run_arm(arm, query)
            self.assertEqual(result.status, "completed")
            call = next(t for t in result.transcript if "tool_call" in t)
            self.assertTrue(call["ok"], call)
            self.assertEqual([r["id"] for r in json.loads(call["result"])["rows"]], sorted(self.events.indicators))
            self.assertEqual(client.requests[0]["model"], agent.MODEL)
            self.assertEqual(client.requests[0]["output_config"]["effort"], agent.EFFORT)
            self.assertTrue(client.requests[0]["tools"][0]["strict"])
        writes = {"graph": "CREATE (:Account {id: 'X'})", "table": "DELETE FROM transfers"}
        for arm, query in writes.items():
            result, _ = self.run_arm(arm, query)
            call = next(t for t in result.transcript if "tool_call" in t)
            self.assertFalse(call["ok"], f"{arm} accepted a write")

    def test_the_arms_differ_only_in_the_evidence_they_are_told_about(self) -> None:
        graph, table = agent.system_prompt("graph"), agent.system_prompt("table")
        self.assertEqual(graph.replace(agent.ARMS["graph"]["description"], ""),
                         table.replace(agent.ARMS["table"]["description"], ""))
        def without_language(arm: str) -> str:
            return json.dumps(agent.tool(arm), sort_keys=True).replace(agent.ARMS[arm]["language"], "LANGUAGE")
        self.assertEqual(without_language("graph"), without_language("table"))

    def test_budgets_stop_a_run_that_never_answers(self) -> None:
        client = ScriptedClient(lambda n: tool_use("MATCH (n) RETURN count(n) AS n", n))
        result = agent.run("graph", client=client, log=lambda _: None)
        self.assertEqual(result.status, "request_budget_exhausted")
        self.assertEqual(result.meta["effort"]["tool_calls"], agent.MAX_TOOL_CALLS)
        self.assertEqual(result.meta["effort"]["requests"], agent.MAX_REQUESTS)

    def test_a_recorded_run_is_checked_scored_and_rendered(self) -> None:
        result, _ = self.run_arm("graph", "MATCH (i:Indicator) RETURN i.id AS id")
        workdir = Path(tempfile.mkdtemp())
        try:
            scored = record(result, workdir / "run", recorded=False, events=self.events, graph=self.graph,
                            title="test")
            self.assertEqual(scored["correctness"], 1.0)
            self.assertEqual(scored["unsupported"], 0)
            note = (workdir / "run" / "case_note.md").read_text()
            self.assertIn("## Hypotheses", note)
            self.assertIn("live run", note)
        finally:
            shutil.rmtree(workdir)


if __name__ == "__main__":
    unittest.main()
