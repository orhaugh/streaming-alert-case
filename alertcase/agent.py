"""The investigating agent: Claude with one read-only query tool, writing a
case note as structured output.

Two arms share everything but the evidence's shape. The graph arm queries the
Relate store in Cypher; the table arm queries the same records as SQLite
tables in SQL. The model, effort, system prompt (apart from the paragraph that
describes the evidence), task, tool name and shape, output schema and budgets
are identical, and both outputs go through the same checker.

The loop is the Anthropic SDK's manual tool-use loop, so every request,
response, tool call and token is recorded as it happens.
"""

from __future__ import annotations

import hashlib
import json
import os
import platform
import sqlite3
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

import anthropic
import relate

from . import tables
from .claims import CLAIM_MEANINGS, OUTPUT_SCHEMA
from .events import sha256_of
from .graph import STORE, Graph

MODEL = "claude-opus-5-5"
EFFORT = "high"
MAX_TOOL_CALLS = 20      # queries a run may make
MAX_REQUESTS = 30        # model requests a run may make
MAX_TOKENS = 16000       # per response
ROW_LIMIT = 200          # rows returned per query
RESULT_CHARS = 30000     # characters returned per query
# On a refusal, the API re-runs the request on a fallback model it chooses.
# Each run records the model that served every response, so a run a fallback
# served is visible in its meta.json and in the comparison.
BETAS = ["server-side-fallback-2026-07-01"]

GRAPH_DESCRIPTION = """Relate graph store, opened read-only; query it in Cypher. Times are epoch milliseconds (event time, UTC); amounts are in minor units (cents).
- (:Run {id, replay, dataset_sha256, dataset_events, jobs, jobs_completed, clink_exit_status, cancelled, pipeline, clink, relate, lag_ms, fan_in_min_senders, fan_in_window_ms, onward_max_gap_ms}): the bounded replay this graph holds, one node.
- (:Account {id})-[:SENT]->(:Transfer {id, ts, amount_minor})-[:TO]->(:Account {id}): every transfer, from its sender to its receiver; ts is the event time.
- (:Transfer)-[:FROM_DEVICE]->(:Device {id}): the device each transfer was sent from.
- (:Indicator {id, kind: 'fan_in', window_start, window_end, senders, transfers, total_minor})-[:ABOUT]->(:Account): fan-in indicators derived by clink: an account that received transfers from at least fan_in_min_senders distinct senders inside one event-time hour.
- (:Indicator)-[:CONTRIBUTING]->(:Transfer): the transfers that make up each fan-in indicator.
- (:Transfer)-[:PASSED_ON {id, gap_ms}]->(:Transfer): onward links derived by clink: a credit to an account followed, within onward_max_gap_ms by event time, by a debit from that same account; gap_ms is the time between them."""

ARMS = {
    "graph": {"language": "Cypher", "description": GRAPH_DESCRIPTION},
    "table": {"language": "SQLite SQL", "description": tables.DESCRIPTION},
}

SYSTEM = """You assist a fraud analyst. You examine the fan-in alerts that stream processing raised over one bounded replay of a synthetic event file, using one read-only query tool over the evidence, and you write a case note.

Ground rules:
- Conclusions hold only for this bounded dataset, as processed by the run it records. Say nothing about events outside it, and do not assume the data is complete beyond what the run record states.
- A recorded relationship (a transfer, an onward link, a device used by several accounts) is not proof of fraud, ownership, identity or causation. Anything beyond what is recorded is a hypothesis at most.
- When you describe how a conclusion can be traced back to the events, call it traceable provenance, never a chain of custody.
- Findings are facts. Every finding cites the ids of the claims that support it. A claim is a structured statement of one of the types below, using the dataset's own ids: transfers (T0001), accounts (A-1234), devices (D-123), fan-in indicators (fan_in:A-1234:<window start in ms>), onward links (onward:T0001:T0002). Claim only what your queries showed.
- Hypotheses are interpretations the data does not establish. Unresolved questions are what the data cannot answer.
- Your claims are checked automatically against the original events and the stored evidence. A claim that does not hold counts against the case note.

The evidence:
{description}

Claim types, and what each asserts:
{claim_types}

You can make at most {max_tool_calls} queries. When you have what you need, reply with the case note in the required JSON format and nothing else."""

TASK = """Investigate every fan-in alert in this bounded replay.
1. For each alert: the account, the event-time window, the number of distinct senders and of transfers, the total, and the contributing transfers.
2. For each alert, follow the onward links from its contributing transfers: how many onward links at most, along which route, and the account or accounts where the money comes to rest.
3. For each alert, which accounts on its routes sent transfers from a device that another account on those routes also used?
4. The alerts may look alike as indicators. Say exactly which recorded relationships distinguish them, and how that changes the interpretation.
Keep findings, hypotheses and unresolved questions apart."""


NO_CREDENTIALS = ("no Anthropic API credentials: set ANTHROPIC_API_KEY, or run `ant auth login`. "
                  "verify.py and explore.py need neither, and the recorded runs are in runs/recorded/.")


def have_credentials() -> bool:
    """What the SDK can authenticate with: a key or token in the environment,
    or a profile `ant auth login` stored under ~/.config/anthropic/."""
    if os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_AUTH_TOKEN"):
        return True
    config = Path(os.environ.get("XDG_CONFIG_HOME") or Path.home() / ".config") / "anthropic"
    return config.is_dir()


def system_prompt(arm: str) -> str:
    claim_types = "\n".join(f"- {kind}: {meaning}" for kind, meaning in CLAIM_MEANINGS.items())
    return SYSTEM.format(description=ARMS[arm]["description"], claim_types=claim_types, max_tool_calls=MAX_TOOL_CALLS)


def tool(arm: str) -> dict:
    language = ARMS[arm]["language"]
    return {
        "name": "query",
        "description": (f"Run one read-only {language} query against the evidence and get the rows back as JSON, at most "
                        f"{ROW_LIMIT} rows. Errors come back as text; fix the query and try again."),
        "strict": True,
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": f"the {language} query"},
                "purpose": {"type": "string", "description": "what this query is meant to establish"},
            },
            "required": ["query", "purpose"],
            "additionalProperties": False,
        },
    }


# ---------------------------------------------------------------------------
# The two query executors. Both are read-only at the connection: Relate's
# handle is opened read-only, SQLite's in mode=ro with query_only on.

def _bounded(rows: list[dict]) -> str:
    shown = rows[:ROW_LIMIT]
    text = json.dumps({"rows": shown, "row_count": len(rows), "truncated": len(rows) > ROW_LIMIT}, default=str)
    if len(text) > RESULT_CHARS:
        text = json.dumps({"error": f"the result is {len(text)} characters, over the {RESULT_CHARS} limit: "
                                    "return fewer rows or columns"})
    return text


class GraphQueries:
    def __init__(self, store: Path = STORE) -> None:
        self.graph = Graph(store)

    def __call__(self, query: str) -> tuple[bool, str]:
        try:
            return True, _bounded(self.graph.rows(query))
        except Exception as error:  # Relate explains what is wrong and how to fix it
            return False, f"error: {error}"

    def close(self) -> None:
        self.graph.close()


class TableQueries:
    def __init__(self, path: Path = tables.TABLES) -> None:
        self.db = tables.connect_read_only(path)

    def __call__(self, query: str) -> tuple[bool, str]:
        try:
            cursor = self.db.execute(query)
            names = [d[0] for d in cursor.description or []]
            return True, _bounded([dict(zip(names, row)) for row in cursor.fetchmany(ROW_LIMIT + 1)])
        except sqlite3.Error as error:
            return False, f"error: {error}"

    def close(self) -> None:
        self.db.close()


# ---------------------------------------------------------------------------

def _plain(value: Any) -> Any:
    """SDK objects to JSON-ready values, for the transcript."""
    if hasattr(value, "to_dict"):
        return value.to_dict()
    if hasattr(value, "model_dump"):
        return value.model_dump(mode="json")
    if isinstance(value, list):
        return [_plain(v) for v in value]
    if isinstance(value, dict):
        return {k: _plain(v) for k, v in value.items()}
    return value


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


@dataclass
class RunResult:
    status: str
    output: dict | None
    meta: dict
    transcript: list[dict]


def run(arm: str, client: Any = None, store: Path = STORE, table_path: Path = tables.TABLES,
        log: Callable[[str], None] = print) -> RunResult:
    """One investigation. client is an anthropic.Anthropic; tests pass a stand-in."""
    client = client or anthropic.Anthropic()
    execute = GraphQueries(store) if arm == "graph" else TableQueries(table_path)
    system, tools = system_prompt(arm), [tool(arm)]
    messages: list[dict] = [{"role": "user", "content": TASK}]
    transcript: list[dict] = []
    totals = {"input_tokens": 0, "output_tokens": 0, "cache_creation_input_tokens": 0, "cache_read_input_tokens": 0}
    tool_calls = tool_errors = requests = 0
    served: list[str] = []
    fallback_used = False
    status, output, stop_reason = "error", None, None
    started = datetime.now(timezone.utc)
    clock = time.monotonic()
    try:
        while True:
            if requests >= MAX_REQUESTS:
                status = "request_budget_exhausted"
                break
            requests += 1
            response = client.beta.messages.create(
                model=MODEL,
                max_tokens=MAX_TOKENS,
                system=system,
                tools=tools,
                messages=messages,
                output_config={"effort": EFFORT, "format": {"type": "json_schema", "schema": OUTPUT_SCHEMA}},
                cache_control={"type": "ephemeral"},
                betas=BETAS,
                fallbacks="default",
            )
            stop_reason = response.stop_reason
            served.append(response.model)
            usage = response.usage
            for name in totals:
                totals[name] += getattr(usage, name, None) or 0
            fallback_used = fallback_used or any(
                getattr(block, "type", None) == "fallback" for block in response.content) or any(
                getattr(entry, "type", None) == "fallback_message" for entry in (getattr(usage, "iterations", None) or []))
            transcript.append({"request": requests, "response": _plain(response)})
            log(f"  request {requests}: stop_reason={stop_reason}, model={response.model}, "
                f"tokens in={usage.input_tokens} out={usage.output_tokens}")

            if stop_reason == "refusal":
                status = "refused"
                break
            if stop_reason == "max_tokens":
                status = "truncated"
                break
            messages.append({"role": "assistant", "content": response.content})
            if stop_reason == "pause_turn":
                continue
            if stop_reason == "tool_use":
                results = []
                for block in response.content:
                    if getattr(block, "type", None) != "tool_use":
                        continue
                    given = block.input if isinstance(block.input, dict) else {}
                    query, purpose = str(given.get("query", "")), str(given.get("purpose", ""))
                    if tool_calls >= MAX_TOOL_CALLS:
                        ok, text = False, ("error: the query budget is spent; reply with the case note now, "
                                           "claiming only what earlier queries showed")
                    else:
                        tool_calls += 1
                        began = time.monotonic()
                        ok, text = execute(query)
                        tool_errors += not ok
                        transcript.append({"tool_call": tool_calls, "purpose": purpose, "query": query, "ok": ok,
                                           "result": text, "seconds": round(time.monotonic() - began, 3)})
                        log(f"    query {tool_calls} ({'ok' if ok else 'error'}): {purpose[:90]}")
                    results.append({"type": "tool_result", "tool_use_id": block.id, "content": text, "is_error": not ok})
                if not results:
                    status = "tool_use_without_tool_call"
                    break
                messages.append({"role": "user", "content": results})
                continue
            if stop_reason == "end_turn":
                text = next((b.text for b in response.content if getattr(b, "type", None) == "text"), None)
                try:
                    output = json.loads(text) if text is not None else None
                    status = "completed" if isinstance(output, dict) else "unparseable"
                    if status != "completed":
                        output = None
                except json.JSONDecodeError:
                    status, output = "unparseable", None
                break
            status = f"stopped:{stop_reason}"
            break
    except anthropic.APIError as error:
        status = f"api_error:{type(error).__name__}"
        transcript.append({"error": str(error)})
        log(f"  API error: {error}")
    finally:
        execute.close()

    evidence = store if arm == "graph" else table_path
    meta = {
        "arm": arm,
        "status": status,
        "stop_reason": stop_reason,
        "model_requested": MODEL,
        "models_served": sorted(set(served)),
        "fallback_used": fallback_used,
        "effort_setting": EFFORT,
        "budgets": {"max_tool_calls": MAX_TOOL_CALLS, "max_requests": MAX_REQUESTS, "max_tokens_per_response": MAX_TOKENS,
                    "row_limit": ROW_LIMIT, "result_chars": RESULT_CHARS},
        "effort": {"tool_calls": tool_calls, "tool_errors": tool_errors, "requests": requests,
                   "wall_seconds": round(time.monotonic() - clock, 1), **totals},
        "started": started.isoformat(timespec="seconds"),
        "versions": {"anthropic": anthropic.__version__, "relate-db": relate.__version__,
                     "python": platform.python_version()},
        "evidence": {"path": str(evidence), "sha256": sha256_of(evidence),
                     "dataset_sha256": sha256_of("data/events.ndjson")},
        "prompt_sha256": {"system": _sha(system), "task": _sha(TASK), "tool": _sha(json.dumps(tools, sort_keys=True)),
                          "output_schema": _sha(json.dumps(OUTPUT_SCHEMA, sort_keys=True))},
    }
    return RunResult(status=status, output=output, meta=meta, transcript=transcript)
