"""The agent harness, driven by a scripted stand-in for the API client.

These tests exercise the loop, the read-only query tools, the budgets and the
recording. The stand-in's replies are scripted here; they are not model
output and nothing in them is reported as a result.
"""

from __future__ import annotations

import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from alertcase import agent, answers, facts
from alertcase.claims import CLAIM_FIELDS
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


def submit(output, n: int = 99) -> SimpleNamespace:
    return response([SimpleNamespace(type="tool_use", id=f"tu{n}", name=agent.SUBMIT, input=output)], "tool_use")


def text_only(words: str = "done") -> SimpleNamespace:
    return response([SimpleNamespace(type="text", text=words)], "end_turn")


class ScriptedClient:
    """Answers both request paths: client.beta.messages.create (the Claude API,
    with the fallback beta) and client.messages.create (Bedrock)."""

    def __init__(self, replies) -> None:
        self.replies = replies
        self.requests: list[dict] = []
        self.paths: list[str] = []
        self.beta = SimpleNamespace(messages=SimpleNamespace(create=lambda **kw: self.create("beta", **kw)))
        self.messages = SimpleNamespace(create=lambda **kw: self.create("messages", **kw))

    def create(self, path: str, **kwargs):
        self.paths.append(path)
        self.requests.append(kwargs)
        return self.replies(len(self.requests))


class AgentLoopTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.events = facts.from_events("data/events.ndjson")
        with Graph("store/case.rl") as graph:
            cls.graph = facts.from_graph(graph)
        claims = answers.expected_claims(cls.events)
        # Grouped by type, as the output schema has the model return them.
        grouped = {kind: [{k: v for k, v in c.items() if k != "type"} for c in claims if c["type"] == kind]
                   for kind in CLAIM_FIELDS}
        cls.output = {"findings": [{"id": "F1", "statement": "scripted", "claim_ids": [c["id"] for c in claims]}],
                      "hypotheses": [], "unresolved": [], "claims": grouped}

    def run_arm(self, arm: str, query: str):
        script = {1: tool_use(query), 2: submit(self.output)}
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
            self.assertNotIn("format", client.requests[0]["output_config"])
            self.assertTrue(client.requests[0]["tools"][0]["strict"])
            self.assertEqual(client.requests[0]["tools"][1]["name"], agent.SUBMIT)
            self.assertNotIn("strict", client.requests[0]["tools"][1])
            self.assertEqual(result.output, self.output)
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

    def test_each_provider_gets_the_same_request_but_the_fallback(self) -> None:
        sent = {}
        for provider in agent.PROVIDERS:
            script = {1: tool_use("MATCH (i:Indicator) RETURN i.id AS id"), 2: submit(self.output)}
            client = ScriptedClient(lambda n: script[n])
            result = agent.run("graph", client=client, provider=provider, log=lambda _: None)
            self.assertEqual(result.status, "completed")
            self.assertEqual(result.meta["provider"], provider)
            sent[provider] = (client.paths[0], client.requests[0])
        self.assertEqual(sent["anthropic"][0], "beta")
        self.assertEqual(sent["anthropic"][1]["betas"], agent.BETAS)
        self.assertEqual(sent["anthropic"][1]["fallbacks"], "default")
        self.assertEqual(sent["anthropic"][1]["model"], agent.MODEL)
        self.assertEqual(sent["bedrock"][0], "messages")
        self.assertEqual(sent["bedrock"][1]["model"], agent.BEDROCK_MODEL)
        self.assertNotIn("betas", sent["bedrock"][1])
        self.assertNotIn("fallbacks", sent["bedrock"][1])
        same = {k: v for k, v in sent["anthropic"][1].items() if k not in ("betas", "fallbacks", "model")}
        self.assertEqual(same, {k: v for k, v in sent["bedrock"][1].items() if k != "model"})

    def test_account_details_never_reach_a_recorded_run(self) -> None:
        profile, arn = "example-profile", "arn:aws:sts::123456789012:assumed-role/example-role/session"
        failure = type("TokenRetrievalError", (Exception,), {"__module__": "botocore.exceptions"})

        def replies(n):
            raise failure(f"profile {profile}: {arn} is not authorised in account 123456789012")

        old = os.environ.get("AWS_PROFILE")
        os.environ["AWS_PROFILE"] = profile
        workdir = Path(tempfile.mkdtemp())
        try:
            self.assertEqual(agent.redact(f"{profile} {arn} 123456789012 1794301200000"),
                             "[profile] [redacted] [redacted] 1794301200000")
            result = agent.run("graph", client=ScriptedClient(replies), provider="bedrock", log=lambda _: None)
            self.assertEqual(result.status, "provider_error:TokenRetrievalError")
            record(result, workdir / "run", recorded=False, events=self.events, graph=self.graph, title="test")
            written = "".join(p.read_text() for p in (workdir / "run").iterdir())
            for secret in (profile, "123456789012", "arn:aws"):
                self.assertNotIn(secret, written)
        finally:
            shutil.rmtree(workdir)
            if old is None:
                os.environ.pop("AWS_PROFILE", None)
            else:
                os.environ["AWS_PROFILE"] = old

    def test_a_turn_that_ends_without_a_case_note_is_reminded_once(self) -> None:
        once = ScriptedClient(lambda n: {1: text_only(), 2: submit(self.output)}[n])
        result = agent.run("graph", client=once, log=lambda _: None)
        self.assertEqual(result.status, "completed")
        reminders = [m for m in once.requests[1]["messages"]
                     if m["role"] == "user" and isinstance(m["content"], str) and agent.SUBMIT in m["content"]]
        self.assertEqual(len(reminders), 1)
        twice = ScriptedClient(lambda n: text_only())
        result = agent.run("graph", client=twice, log=lambda _: None)
        self.assertEqual((result.status, result.output, len(twice.requests)), ("ended_without_case_note", None, 2))

    def test_a_malformed_case_note_is_not_kept(self) -> None:
        bad = {**self.output, "findings": [{"id": "F1", "statement": "no claim ids"}]}
        client = ScriptedClient(lambda n: submit(bad))
        result = agent.run("graph", client=client, log=lambda _: None)
        self.assertEqual((result.status, result.output), ("malformed_case_note", None))

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
