"""The investigator's MCP backend: the graph arm's queries sent to Relate's own
MCP server (scripts/serve-mcp.sh, over stdio) through the MCP Python SDK.

Skipped unless the relate command line (scripts/fetch-relate-cli.sh) and the
MCP client (requirements-mcp.txt) are installed. The model is the scripted
stand-in from test_agent_loop; nothing here is model output.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from alertcase import agent, mcp_store
from alertcase.cases import CASES
from alertcase.mcp_store import ROOT, McpError, McpStore, client_missing, process_exists
from alertcase.recording import record
from tests import test_agent_loop as loop  # the module, so its test class is not collected twice
from tests.test_agent_loop import ScriptedClient, submit, tool_use


def missing() -> str | None:
    if client_missing():
        return client_missing()
    if not (os.environ.get("RELATE_BIN") or (ROOT / ".relate/bin/relate").exists() or shutil.which("relate")):
        return "no relate command line (scripts/fetch-relate-cli.sh)"
    return None


def started_since(mark: int) -> list[int]:
    """The server processes started since the mark, by the ids the launcher announced."""
    return mcp_store.STARTED[mark:]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


@unittest.skipIf(missing(), missing())
class McpBackendTest(unittest.TestCase):
    store = CASES["small"].store

    @classmethod
    def setUpClass(cls) -> None:
        loop.AgentLoopTest.setUpClass.__func__(cls)  # the scripted case note and both sources of facts

    def test_the_mcp_backend_answers_as_the_embedded_one(self) -> None:
        queries = [agent.GRAPH_DESCRIPTION.split("\n  ", 1)[1].split("\nlinks counts", 1)[0]
                   .replace("\n  ", "\n").replace("<indicator id>", alert) for alert in sorted(self.events.indicators)]
        queries += [
            "MATCH (i:Indicator)-[:CONTRIBUTING]->(t:Transfer) RETURN i.id AS id, collect(t.id) AS transfers ORDER BY id",
            "MATCH (r:Run) RETURN r.jobs_completed AS done, r.cancelled AS cancelled, r.dataset_events AS events",
            "UNWIND range(1, 250) AS n RETURN n",  # over ROW_LIMIT: truncated the same way
            "MATCH (a:Account RETURN a",            # a syntax error: refused by both
        ]
        mark = len(mcp_store.STARTED)
        embedded, mcp = agent.GraphQueries(self.store), agent.McpQueries("small")
        try:
            self.assertTrue(process_exists(mcp.store.pid))  # the check sees the live server
            for query in queries:
                (ok_e, text_e), (ok_m, text_m) = embedded(query), mcp(query)
                self.assertEqual(ok_e, ok_m, (query, text_e, text_m))
                if not ok_e:
                    continue
                got_e, got_m = json.loads(text_e), json.loads(text_m)
                key = lambda r: json.dumps(r, sort_keys=True)  # noqa: E731
                self.assertEqual(sorted(got_e["rows"], key=key), sorted(got_m["rows"], key=key), query)
                self.assertEqual((got_e["row_count"], got_e["truncated"]), (got_m["row_count"], got_m["truncated"]))
            self.assertEqual((got_m["row_count"], len(got_m["rows"]), got_m["truncated"]), (250, agent.ROW_LIMIT, True))
        finally:
            embedded.close()
            mcp.close()
        started = started_since(mark)
        self.assertEqual(len(started), 1)
        self.assertFalse(any(map(process_exists, started)))

    def test_writes_are_refused_and_leave_the_store_as_it_was(self) -> None:
        before = sha256(self.store)
        mcp = agent.McpQueries("small")
        try:
            for write in ("CREATE (:Account {id: 'X'})", "MATCH (t:Transfer) DETACH DELETE t"):
                ok, text = mcp(write)
                self.assertFalse(ok, write)
                self.assertIn("Only MATCH queries are allowed", text)
        finally:
            mcp.close()
        self.assertEqual(sha256(self.store), before)

    def test_a_query_past_the_deadline_stops_the_server_and_starts_it_again(self) -> None:
        old = agent.QUERY_SECONDS
        agent.QUERY_SECONDS = 0.5
        mcp = agent.McpQueries("small")
        try:
            first = mcp.store.pid
            self.assertTrue(process_exists(first))  # the check sees the live server
            ok, text = mcp("MATCH (a:Account), (b:Account), (c:Account), (d:Account), (e:Account) RETURN count(*) AS n")
            self.assertEqual((ok, text), (False, agent.TOO_LONG))
            second = mcp.store.pid
            self.assertNotEqual(second, first)
            self.assertFalse(process_exists(first))  # the stopped server is gone, not merely unseen
            ok, text = mcp("MATCH (r:Run) RETURN r.id AS id")
            self.assertTrue(ok, text)  # the replacement answers
            self.assertTrue(process_exists(second))
            self.assertEqual((mcp.describe()["server_starts"], mcp.store.pids), (2, [first, second]))
        finally:
            agent.QUERY_SECONDS = old
            mcp.close()
        self.assertTrue(mcp.store.gone())  # closing ends the replacement too

    def test_a_run_through_mcp_sends_the_same_requests_and_records_its_transport(self) -> None:
        mark = len(mcp_store.STARTED)
        runs = {}
        for backend in agent.BACKENDS:
            script = {1: tool_use("MATCH (i:Indicator) RETURN i.id AS id ORDER BY id"), 2: submit(self.output)}
            client = ScriptedClient(lambda n: script[n])
            runs[backend] = (agent.run("graph", client=client, log=lambda _: None, backend=backend), client)
        (embedded, sent_e), (mcp, sent_m) = runs["embedded"], runs["mcp"]
        self.assertEqual((embedded.status, mcp.status), ("completed", "completed"))
        self.assertEqual(sent_e.requests, sent_m.requests)  # the model saw the same tools, prompt and results
        self.assertEqual(embedded.meta["prompt_sha256"], mcp.meta["prompt_sha256"])
        self.assertEqual(embedded.meta["backend"], {"name": "embedded"})
        reached = mcp.meta["backend"]
        self.assertEqual((reached["name"], reached["transport"], reached["server"]), ("mcp", "stdio", "relate-mcp 1.0.1"))
        self.assertEqual(reached["tools"], ["get_schema", "read_cypher"])
        self.assertTrue(reached["protocol_version"] and reached["mcp_client"].startswith("mcp "))
        workdir = Path(tempfile.mkdtemp())
        try:
            record(mcp, workdir / "run", recorded=False, events=self.events, graph=self.graph, title="test")
            self.assertIn("graph arm through Relate's MCP server (relate-mcp 1.0.1, stdio)",
                          (workdir / "run" / "case_note.md").read_text())
        finally:
            shutil.rmtree(workdir)
        started = started_since(mark)
        self.assertEqual(len(started), 1)  # one server, for the MCP run, and it is gone
        self.assertFalse(any(map(process_exists, started)))

    def test_the_launcher_replaces_a_stale_store_by_the_rule_the_library_uses(self) -> None:
        import gzip

        from alertcase.cases import Case

        relate = os.environ.get("RELATE_BIN") or str(ROOT / ".relate/bin/relate")
        root = Path(tempfile.mkdtemp())
        try:
            (root / "scripts").mkdir()
            (root / "store").mkdir()
            shutil.copy(ROOT / "scripts/serve-mcp.sh", root / "scripts/serve-mcp.sh")
            packed = root / "store/large.rl.gz"
            shutil.copy(ROOT / "store/large.rl.gz", packed)
            store = root / "store/large.rl"
            store.write_bytes(b"a store unpacked from an earlier gzipped copy")

            def serve() -> subprocess.CompletedProcess:  # stdin closed: the server starts, then exits
                return subprocess.run(["sh", str(root / "scripts/serve-mcp.sh"), "large"], stdin=subprocess.DEVNULL,
                                      capture_output=True, text=True, timeout=120, env={**os.environ, "RELATE_BIN": relate})

            served = serve()
            self.assertEqual(served.returncode, 0, served.stderr)
            with gzip.open(packed, "rb") as shipped:
                self.assertEqual(store.read_bytes(), shipped.read())
            digest = sha256(packed)
            self.assertEqual(Case.source_record(store).read_text().strip(), digest)

            unpacked = store.stat().st_ino
            self.assertEqual(serve().returncode, 0)
            library = Case("large", root / "e", root / "s", root / "p", store, root / "store/none.sqlite", root / "c",
                           max_tokens=1, table_indexes=False)
            library.unpack()
            self.assertEqual(store.stat().st_ino, unpacked)  # current by both rules: left alone
        finally:
            shutil.rmtree(root)

    def test_the_process_check_sees_a_live_process_and_not_a_reaped_one(self) -> None:
        self.assertTrue(process_exists(os.getpid()))
        child = subprocess.Popen(["true"])
        child.wait()
        self.assertFalse(process_exists(child.pid))

    def test_the_mcp_backend_is_for_the_graph_arm_only(self) -> None:
        with self.assertRaises(ValueError):
            agent.run("table", client=ScriptedClient(lambda n: submit(self.output)), log=lambda _: None, backend="mcp")

    def test_the_launcher_refuses_a_relate_it_was_not_tested_with(self) -> None:
        with self.assertRaises(McpError) as refused:
            McpStore("small", env={"RELATE_BIN": "/usr/bin/true"})
        self.assertIn("tested with 1.0.1", str(refused.exception))


if __name__ == "__main__":
    unittest.main()
