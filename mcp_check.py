#!/usr/bin/env python3
"""Check Relate's own MCP server on this repository's stores, started the way
an agent host starts it. No model and no API key.

Needs the relate command line 1.0.1 (scripts/fetch-relate-cli.sh) and the MCP
Python SDK (pip install --require-hashes -r requirements-mcp.txt).

The host configurations first: .mcp.json starts scripts/serve-mcp.sh from the
repository's root, and `sh scripts/serve-mcp.sh --config`, run from another directory,
prints this checkout's absolute paths, which serve from there too. Then, for
each dataset, through the MCP Python SDK, against the command .mcp.json gives:
  1. the handshake: relate-mcp answers initialize, at the pinned version;
  2. the tools: read_cypher and get_schema, both marked read-only, and no
     write tool;
  3. the schema: get_schema's labels and counts equal those the independent
     reference rules derive from the event file;
  4. the evidence: transfers, alerts with their contributing transfers, onward
     links and each alert's paths, read over MCP with the verifier's own
     Cypher, equal the reference's, record for record;
  5. a multi-hop query: the worked example the agent is given, a
     variable-length pattern from an alert's contributing transfers, returns
     exactly the candidate paths the reference computes, for every alert;
  6. writes refused: CREATE, MERGE, SET, DELETE and a schema change sent to
     read_cypher, and a call to write_cypher, each answered as a failed call;
  7. a clean shutdown: with stdin closed the server exits 0, having written
     nothing but JSON-RPC to stdout, and no server process is left behind;
  8. the store unchanged: the same bytes, and no file added beside it.

What it does not check is what an agent concludes from these answers. An
investigation in your own agent host is not a checked case note: only the
case notes investigate.py records go through the claim checker.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

from alertcase import facts
from alertcase.agent import GRAPH_DESCRIPTION
from alertcase.cases import CASES, Case
from alertcase.mcp_store import ROOT, SERVE, McpGraph, McpStore, client_missing, host_command, process_exists
from verify import Report

PINNED = "relate-mcp 1.0.1"
HOST_NAMES = {"small": "streaming-alert-case", "large": "streaming-alert-case-large"}
WRITES = {
    "CREATE": "CREATE (:Account {id: 'A-0000'})",
    "MERGE": "MERGE (:Device {id: 'D-000'})",
    "SET": "MATCH (a:Account) SET a.flag = true",
    "DELETE": "MATCH (t:Transfer) DETACH DELETE t",
    "a schema change": "CREATE INDEX FOR (a:Account) ON (a.id)",
}
WORKED_EXAMPLE = re.search(r"  MATCH \(i:Indicator.*?AS ends", GRAPH_DESCRIPTION, re.S).group(0)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def fingerprint(store: Path) -> tuple[str, list[str]]:
    return sha256(store), sorted(p.name for p in store.parent.iterdir())


def reference_paths(events: facts.Facts, indicator: str, most_links: int = 10) -> set[tuple]:
    """Every candidate path of 1 to most_links onward links from the alert's
    contributing transfers, computed from the reference's onward links."""
    onward: dict[str, list[str]] = {}
    for link in events.links.values():
        onward.setdefault(link["in_id"], []).append(link["out_id"])
    found: set[tuple] = set()

    def walk(trail: list[str]) -> None:
        for step in onward.get(trail[-1], []):
            path = [*trail, step]
            found.add((tuple(path), len(path) - 1, step not in onward))
            if len(path) - 1 < most_links:
                walk(path)

    for start in events.indicators[indicator]["transfer_ids"]:
        walk([start])
    return found


def check_hosts(report: Report) -> dict[str, list[str]]:
    """The two configurations, and the absolute command --config prints."""
    report.section("Host configurations")
    servers = json.loads((ROOT / ".mcp.json").read_text())["mcpServers"]
    project = all([servers[HOST_NAMES[c]]["command"], *servers[HOST_NAMES[c]]["args"]] == host_command(c)
                  for c in HOST_NAMES)
    report.record(".mcp.json", project, "starts `sh scripts/serve-mcp.sh small|large` from the repository's root, "
                  "where Claude Code starts a project's servers")
    with tempfile.TemporaryDirectory() as elsewhere:
        printed = subprocess.run(["/bin/sh", str(SERVE), "--config"], cwd=elsewhere, capture_output=True,
                                 text=True, check=True).stdout
    block = json.loads(printed)["mcpServers"]
    absolute = {c: [block[HOST_NAMES[c]]["command"], *block[HOST_NAMES[c]]["args"]] for c in HOST_NAMES}
    report.record("serve.sh --config", all(absolute[c] == ["/bin/sh", str(SERVE), c] for c in HOST_NAMES),
                  "printed from another directory: /bin/sh and this checkout's absolute launcher path, for hosts "
                  "that need absolute paths")
    return absolute


def check_case(case: Case, absolute: list[str], report: Report) -> None:
    case.unpack()
    store = case.store.resolve()
    events = facts.from_events(case.events)
    before = fingerprint(store)

    report.section(f"The {case.name} case, {case.store}, from another directory with the --config command")
    sessions = []
    with tempfile.TemporaryDirectory() as elsewhere, McpStore(case.name, command=absolute, cwd=Path(elsewhere)) as s:
        sessions.append(s)
        count = s.read("MATCH (t:Transfer) RETURN count(t) AS n")["rows"][0]["n"]
        report.record("absolute paths", count == len(events.transfers),
                      f"served {count} transfers, started from a temporary directory outside the checkout")

    report.section(f"The {case.name} case, through the MCP Python SDK, as .mcp.json starts it")
    with McpStore(case.name) as s:
        sessions.append(s)
        seen_alive = s.pid is not None and process_exists(s.pid)
        server = f"{s.info.server_info.name} {s.info.server_info.version}"
        offered = s.info.capabilities
        tools_only = offered.tools is not None and offered.resources is None and offered.prompts is None
        report.record("handshake", server == PINNED and tools_only,
                      f"{server}, protocol {s.info.protocol_version}, capabilities: tools only")

        tools = {t.name: t.annotations for t in s.tools}
        read_only = all(a is not None and a.read_only_hint and not a.destructive_hint for a in tools.values())
        report.record("tools", set(tools) == {"read_cypher", "get_schema"} and read_only,
                      f"{', '.join(sorted(tools))}, each marked read-only and not destructive; no write tool listed")

        schema = s.schema(-1)
        want = {"Account": len(events.accounts), "Device": len(events.devices), "Indicator": len(events.indicators),
                "Run": 1, "Transfer": len(events.transfers)}
        held = {label: entry["count"] for label, entry in schema.items()}
        report.record("schema", held == want,
                      ", ".join(f"{k} {v}" for k, v in sorted(held.items())) + ": the reference's counts"
                      if held == want else f"{held}, not {want}")

        over = facts.from_graph(McpGraph(s))
        same = {name: getattr(over, name) == getattr(events, name)
                for name in ("transfers", "indicators", "links", "investigation", "device_senders")}
        same["run"] = bool(over.run) and all(over.run[k] == events.run[k] for k in events.run)
        report.record("evidence over MCP", all(same.values()),
                      f"{len(over.transfers)} transfers, {len(over.indicators)} alerts, {len(over.links)} onward "
                      "links, each alert's paths, path ends and shared devices, and the run's dataset hash equal "
                      "the reference's" if all(same.values()) else f"differ: {[k for k, ok in same.items() if not ok]}")

        mismatched, paths = [], 0
        for indicator in sorted(events.indicators):
            rows = s.read(WORKED_EXAMPLE.replace("<indicator id>", indicator))["rows"]
            got = {(tuple(r["path"]), r["links"], bool(r["ends"])) for r in rows}
            paths += len(got)
            if got != reference_paths(events, indicator) or len(rows) != len(got):
                mismatched.append(indicator)
        longest = max((len(p) - 1 for i in events.indicators for p, _, _ in reference_paths(events, i)), default=0)
        report.record("multi-hop query", not mismatched,
                      f"the worked example's variable-length pattern returned {paths} candidate paths, up to "
                      f"{longest} onward links, for {len(events.indicators)} alerts: exactly the reference's"
                      if not mismatched else f"paths differ for {mismatched}")

        refused = {}
        for name, statement in WRITES.items():
            answer = s.call("read_cypher", {"statement": statement})
            refused[name] = answer.is_error and "Only MATCH queries are allowed" in answer.text
        answer = s.call("write_cypher", {"statement": WRITES["CREATE"]})
        refused["write_cypher"] = answer.is_error and "unknown tool" in answer.text
        report.record("writes refused", all(refused.values()),
                      f"{', '.join(WRITES)} through read_cypher, and write_cypher: each a failed call"
                      if all(refused.values()) else f"accepted: {[k for k, ok in refused.items() if not ok]}")
    # Each session's server, followed by the id its launcher announced: seen
    # running while its session was open, and gone once the session closed.
    left = [pid for session in sessions for pid in session.pids if process_exists(pid)]
    followed = all(session.pids for session in sessions) and seen_alive

    exchange = [
        {"jsonrpc": "2.0", "id": 1, "method": "initialize",
         "params": {"protocolVersion": "2025-06-18", "capabilities": {}, "clientInfo": {"name": "check", "version": "0"}}},
        {"jsonrpc": "2.0", "method": "notifications/initialized"},
        {"jsonrpc": "2.0", "id": 2, "method": "ping"},
    ]
    server = subprocess.Popen(host_command(case.name), cwd=ROOT, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE, text=True)
    out, _ = server.communicate("".join(json.dumps(m) + "\n" for m in exchange), timeout=120)
    try:
        replies = [json.loads(line) for line in out.splitlines()]
        rpc_only = [r.get("jsonrpc") for r in replies] == ["2.0", "2.0"] and [r.get("id") for r in replies] == [1, 2]
    except ValueError:
        rpc_only = False
    report.record("clean shutdown", server.returncode == 0 and rpc_only and followed and not left,
                  "stdin closed: exit status 0, stdout held only the two JSON-RPC replies; each SDK session's "
                  "server, followed by its process id, ran while open and was gone once closed"
                  if followed and not left else
                  "a server's process id was not announced, or not seen while running" if not followed else
                  f"server processes left: {left}")

    after = fingerprint(store)
    report.record("store unchanged", after == before,
                  f"sha256 {after[0][:16]}... before and after, and no file added beside it"
                  if after == before else "the store or its directory changed")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--case", choices=["all", *sorted(CASES)], default="all")
    args = parser.parse_args()
    if client_missing():
        raise SystemExit(client_missing())

    report = Report()
    absolute = check_hosts(report)
    for name in (sorted(CASES, key=lambda n: n != "small") if args.case == "all" else [args.case]):
        check_case(CASES[name], absolute[name], report)
    passed = sum(report.results)
    print(f"\n{passed} of {len(report.results)} checks passed")
    return 0 if passed == len(report.results) else 1


if __name__ == "__main__":
    sys.exit(main())
