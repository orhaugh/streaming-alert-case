"""Relate's own MCP server on one of this repository's stores, through the MCP
Python SDK (the `mcp` package, in requirements-mcp.txt).

The server is started the way an agent host starts it: scripts/serve-mcp.sh, over
stdio, read-only. The SDK runs it in a process group of its own; when the
session ends it closes the server's stdin, waits, then stops the group
(SIGTERM, then SIGKILL). The server has no per-call timeout and no row cap
(Relate's MCP server reference, "Limits"), so a caller that needs a deadline
gives one to call(), which stops the server and starts it again when the
deadline passes, and a caller that needs a row limit applies it.

The session runs on an event loop in a thread of its own, so synchronous code,
the agent's tool loop and the checks, can call it.
"""

from __future__ import annotations

import asyncio
import concurrent.futures
import importlib.metadata
import importlib.util
import json
import tempfile
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .graph import Graph

ROOT = Path(__file__).resolve().parent.parent
SERVE = ROOT / "scripts" / "serve-mcp.sh"
START_SECONDS = 120   # to start the server and complete the handshake; the large store loads in under one
STOP_SECONDS = 30     # for the SDK to stop the server: stdin closed, 2 s, SIGTERM, 2 s, SIGKILL


class McpError(Exception):
    """The server could not be started, or answered with a protocol error."""


class Stopped(McpError):
    """A call ran past its deadline. The server was stopped and started again."""


@dataclass
class Answer:
    is_error: bool
    text: str


def client_missing() -> str | None:
    """Why the MCP client cannot be used, or None. Looks for the SDK's stdio
    client itself, not just a package named mcp."""
    try:
        found = importlib.util.find_spec("mcp.client.stdio") is not None
    except ImportError:
        found = False
    return None if found else ("the MCP client is not installed: .venv/bin/pip install --require-hashes "
                               "-r requirements-mcp.txt")


def host_command(case: str) -> list[str]:
    """What .mcp.json makes an agent host run, from the repository's root."""
    return ["sh", "scripts/serve-mcp.sh", case]


class McpStore:
    """One MCP session with the server on one store, restartable."""

    def __init__(self, case: str = "small", command: list[str] | None = None, cwd: Path | None = None,
                 env: dict[str, str] | None = None) -> None:
        missing = client_missing()
        if missing:
            raise McpError(missing)
        self.command = command or host_command(case)
        self.cwd = Path(cwd or ROOT)
        self.env = env
        self.loop = asyncio.new_event_loop()
        self.thread = threading.Thread(target=self.loop.run_forever, name="mcp-session", daemon=True)
        self.thread.start()
        self.task: asyncio.Task | None = None
        self.requests: asyncio.Queue | None = None
        self.info: Any = None        # the server's answer to initialize
        self.tools: list[Any] = []   # the server's answer to tools/list
        self.starts = 0
        try:
            self._start()
        except BaseException:
            self._shutdown_loop()
            raise

    # -- life cycle ---------------------------------------------------------

    def _on_loop(self, coroutine, timeout: float) -> Any:
        return asyncio.run_coroutine_threadsafe(coroutine, self.loop).result(timeout)

    def _start(self) -> None:
        ready: concurrent.futures.Future = concurrent.futures.Future()

        async def begin() -> None:
            self.requests = asyncio.Queue()
            self.task = asyncio.ensure_future(self._session(ready))

        self._on_loop(begin(), 10)
        try:
            self.info, self.tools = ready.result(START_SECONDS)
        except concurrent.futures.TimeoutError:
            self._stop()
            raise McpError(f"the MCP server did not answer the handshake within {START_SECONDS} s") from None
        except BaseException:
            self._stop()
            raise
        self.starts += 1

    async def _session(self, ready: concurrent.futures.Future) -> None:
        with tempfile.TemporaryFile("w+") as errlog:
            try:
                from mcp import ClientSession, StdioServerParameters
                from mcp.client.stdio import stdio_client

                params = StdioServerParameters(command=self.command[0], args=self.command[1:], cwd=str(self.cwd),
                                               env=self.env)
                async with stdio_client(params, errlog=errlog) as (read, write):
                    async with ClientSession(read, write) as session:
                        info = await session.initialize()
                        listed = await session.list_tools()
                        ready.set_result((info, listed.tools))
                        while True:
                            item = await self.requests.get()
                            if item is None:
                                return
                            name, arguments, answer = item
                            try:
                                answer.set_result(await session.call_tool(name, arguments))
                            except Exception as error:
                                answer.set_exception(McpError(f"{type(error).__name__}: {error}"))
            except BaseException as error:
                if not ready.done():
                    errlog.seek(0)
                    said = errlog.read().strip()
                    ready.set_exception(McpError(f"the MCP server did not start: {said or error}"))
                if not isinstance(error, Exception):
                    raise

    def _stop(self) -> None:
        """Ends the session the hard way: the call in progress is cancelled
        and the SDK stops the server's process group."""
        task, self.task = self.task, None
        if task is None:
            return

        async def end() -> None:
            task.cancel()
            await asyncio.wait({task})

        self._on_loop(end(), STOP_SECONDS)

    def restart(self) -> None:
        self._stop()
        self._start()

    def close(self) -> None:
        """Ends the session the way a host does: the SDK closes the server's
        stdin, and the server exits."""
        task, self.task = self.task, None
        if task is not None:
            async def end() -> None:
                self.requests.put_nowait(None)
                await asyncio.wait({task})

            try:
                self._on_loop(end(), STOP_SECONDS)
            except concurrent.futures.TimeoutError:
                self.task = task
                self._stop()
        self._shutdown_loop()

    def _shutdown_loop(self) -> None:
        if self.loop.is_running():
            self.loop.call_soon_threadsafe(self.loop.stop)
            self.thread.join(10)
        if not self.loop.is_running() and not self.loop.is_closed():
            self.loop.close()

    def __enter__(self) -> "McpStore":
        return self

    def __exit__(self, *exc) -> None:
        self.close()

    # -- calls --------------------------------------------------------------

    def call(self, name: str, arguments: dict, timeout: float | None = None) -> Answer:
        """One tools/call. Past the deadline, the server is stopped, started
        again, and Stopped is raised."""
        if self.task is None:
            raise McpError("the session is closed")
        answer: concurrent.futures.Future = concurrent.futures.Future()
        self.loop.call_soon_threadsafe(self.requests.put_nowait, (name, arguments, answer))
        try:
            result = answer.result(timeout)
        except concurrent.futures.TimeoutError:
            self.restart()
            raise Stopped(f"{name} ran longer than {timeout} s; the server was stopped and started again") from None
        text = "".join(getattr(item, "text", "") for item in result.content)
        return Answer(is_error=bool(result.is_error), text=text)

    def read(self, statement: str, parameters: dict | None = None, timeout: float | None = None) -> dict:
        """read_cypher, as its result envelope: columns, rows (every row), stats, timings."""
        answer = self.call("read_cypher", {"statement": statement, "parameters": parameters or {}}, timeout)
        if answer.is_error:
            raise McpError(answer.text)
        envelope = json.loads(answer.text)
        if envelope.get("error"):
            raise McpError(str(envelope["error"]))
        return envelope

    def schema(self, sample_size: int = -1) -> dict:
        answer = self.call("get_schema", {"sample_size": sample_size})
        if answer.is_error:
            raise McpError(answer.text)
        return json.loads(answer.text)

    # -- what ran -------------------------------------------------------------

    def describe(self) -> dict:
        """The transport, the server and the client, for a run's meta.json."""
        server = self.info.server_info
        return {"transport": "stdio", "launcher": "scripts/serve-mcp.sh", "server": f"{server.name} {server.version}",
                "protocol_version": self.info.protocol_version, "mcp_client": f"mcp {importlib.metadata.version('mcp')}",
                "tools": sorted(t.name for t in self.tools), "server_starts": self.starts}


class McpGraph(Graph):
    """The verifier's own Cypher (graph.py), answered by Relate's MCP server
    instead of the Python library."""

    def __init__(self, store: McpStore) -> None:  # opens nothing: the server holds the store
        self.session = store

    def close(self) -> None:
        pass

    def rows(self, cypher: str, **params) -> list[dict]:
        return self.session.read(cypher, params)["rows"]
