"""The investigating agent: Claude with one read-only query tool, submitting a
case note through a second tool whose input schema is the case note's.

Two arms share everything but the evidence's shape. The graph arm queries the
Relate store in Cypher; the table arm queries the same records as SQLite
tables in SQL. The model, effort, system prompt (apart from the paragraph that
describes the evidence), task, tool name and shape, output schema and budgets
are identical, and both outputs go through the same checker.

The loop is the Anthropic SDK's manual tool-use loop, so every request,
response, tool call and token is recorded as it happens. The model is reached
either through the Claude API (provider "anthropic") or through Amazon Bedrock
(provider "bedrock"), with the same request in both cases apart from the
server-side refusal fallback, which only the Claude API offers.
"""

from __future__ import annotations

import hashlib
import json
import os
import platform
import re
import sqlite3
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

import anthropic
import relate

from . import tables
from .claims import CLAIM_MEANINGS, OUTPUT_SCHEMA, case_note_error
from .events import sha256_of
from .graph import STORE, Graph

MODEL = "claude-opus-5-5"
EFFORT = "high"
MAX_TOOL_CALLS = 20      # queries a run may make
MAX_REQUESTS = 30        # model requests a run may make
MAX_TOKENS = 16000       # per response
ROW_LIMIT = 200          # rows returned per query
RESULT_CHARS = 30000     # characters returned per query
# On a refusal, the Claude API re-runs the request on a fallback model it
# chooses. Each run records the model that served every response, so a run a
# fallback served is visible in its meta.json and in the comparison. Bedrock
# has no server-side fallback: there a refusal ends the run as refused.
BETAS = ["server-side-fallback-2026-07-01"]

PROVIDERS = ("anthropic", "bedrock")
# The same model on Bedrock, through its global cross-region inference
# profile: in some regions, ap-south-1 among them, Claude Opus 5.5 is offered
# only through an inference profile, and global routes the request to any
# region. BEDROCK_MODEL_ID overrides it, for example with
# anthropic.claude-opus-5-5 where the model runs in the region itself.
BEDROCK_MODEL = "global.anthropic.claude-opus-5-5"


def model_for(provider: str) -> str:
    return (os.environ.get("BEDROCK_MODEL_ID") or BEDROCK_MODEL) if provider == "bedrock" else MODEL


def bedrock_region() -> str | None:
    return os.environ.get("AWS_REGION") or os.environ.get("AWS_DEFAULT_REGION")


def make_client(provider: str) -> Any:
    if provider == "bedrock":
        # Bedrock's runtime endpoint, where its inference profiles are served.
        # (On 13 November 2026 the Messages-API endpoint, bedrock-mantle,
        # answered 404 for Claude Opus 5.5 in ap-south-1, under both ids.)
        # Credentials come from the AWS SDK's own chain (AWS_PROFILE, SSO, the
        # environment). Nothing about the account is recorded.
        return anthropic.AnthropicBedrock(aws_region=bedrock_region(), aws_profile=os.environ.get("AWS_PROFILE"))
    return anthropic.Anthropic()


_ACCOUNT_DETAILS = re.compile(r"arn:aws[a-z-]*:[^\s\"',)]*|\b\d{12}\b")


def redact(text: str) -> str:
    """Error text with AWS ARNs, account ids and the profile name removed, so a
    failed run can be recorded without saying whose account served it."""
    text = _ACCOUNT_DETAILS.sub("[redacted]", text)
    profile = os.environ.get("AWS_PROFILE")
    return text.replace(profile, "[profile]") if profile else text

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

You can make at most {max_tool_calls} queries. When you have what you need, call submit_case_note once with the case note. That ends the investigation."""

TASK = """Investigate every fan-in alert in this bounded replay.
1. For each alert: the account, the event-time window, the number of distinct senders and of transfers, the total, and the contributing transfers.
2. For each alert, follow the onward links from its contributing transfers: how many onward links at most, along which route, and the account or accounts where the money comes to rest.
3. For each alert, which accounts on its routes sent transfers from a device that another account on those routes also used?
4. The alerts may look alike as indicators. Say exactly which recorded relationships distinguish them, and how that changes the interpretation.
Keep findings, hypotheses and unresolved questions apart."""


NO_CREDENTIALS = ("no Anthropic API credentials: set ANTHROPIC_API_KEY, or run `ant auth login`, or use "
                  "--provider bedrock with AWS credentials. verify.py and explore.py need none of them, and the "
                  "recorded runs are in runs/recorded/.")


def missing_credentials(provider: str) -> str | None:
    """Why a live run cannot start, or None. For the Claude API: a key or token
    in the environment, or a profile `ant auth login` stored under
    ~/.config/anthropic/. For Bedrock: a region; the AWS SDK resolves the
    credentials and says what is missing."""
    if provider == "bedrock":
        return None if bedrock_region() else "Bedrock needs a region: set AWS_REGION, and AWS_PROFILE if not the default"
    if os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_AUTH_TOKEN"):
        return None
    config = Path(os.environ.get("XDG_CONFIG_HOME") or Path.home() / ".config") / "anthropic"
    return None if config.is_dir() else NO_CREDENTIALS


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


SUBMIT = "submit_case_note"


def submit_tool() -> dict:
    """The case note arrives as this tool's input. Its schema is the case
    note's, and is not strict: as a strict schema (or as structured output)
    the claim vocabulary compiles to a grammar larger than Bedrock accepts.
    claims.case_note_error() and the checker validate what arrives instead."""
    return {
        "name": SUBMIT,
        "description": ("Submit the case note, once, when the investigation is done; that ends it. Group the claims "
                        "by type, and give every finding the ids of the claims that support it."),
        "input_schema": OUTPUT_SCHEMA,
    }


def tools_for(arm: str) -> list[dict]:
    return [tool(arm), submit_tool()]


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


def send(client: Any, provider: str, system: str, tools: list[dict], messages: list) -> Any:
    """One model request, the same on both providers apart from the fallback."""
    request = dict(
        model=model_for(provider),
        max_tokens=MAX_TOKENS,
        system=system,
        tools=tools,
        messages=messages,
        output_config={"effort": EFFORT},
        cache_control={"type": "ephemeral"},
    )
    if provider == "anthropic":
        return client.beta.messages.create(**request, betas=BETAS, fallbacks="default")
    return client.messages.create(**request)


def provider_error(error: Exception) -> bool:
    """An API error, or the AWS SDK failing to find or refresh credentials."""
    return isinstance(error, anthropic.APIError) or type(error).__module__.split(".")[0] in ("botocore", "boto3")


def smoke(arm: str, provider: str, client: Any = None) -> dict:
    """Sends a run's first request once and reports how the provider answered:
    that it accepts the request's tools, output format, effort and caching.
    Writes nothing, and runs no query."""
    client = client or make_client(provider)
    response = send(client, provider, system_prompt(arm), tools_for(arm), [{"role": "user", "content": TASK}])
    usage = response.usage
    return {"provider": provider, "model_requested": model_for(provider), "model_served": response.model,
            "stop_reason": response.stop_reason, "blocks": [getattr(b, "type", None) for b in response.content],
            "input_tokens": usage.input_tokens, "output_tokens": usage.output_tokens,
            "cache_creation_input_tokens": getattr(usage, "cache_creation_input_tokens", None),
            "cache_read_input_tokens": getattr(usage, "cache_read_input_tokens", None)}


def run(arm: str, client: Any = None, provider: str = "anthropic", store: Path = STORE,
        table_path: Path = tables.TABLES, log: Callable[[str], None] = print) -> RunResult:
    """One investigation. client is the provider's SDK client; tests pass a stand-in."""
    client = client or make_client(provider)
    execute = GraphQueries(store) if arm == "graph" else TableQueries(table_path)
    system, tools = system_prompt(arm), tools_for(arm)
    messages: list[dict] = [{"role": "user", "content": TASK}]
    transcript: list[dict] = []
    totals = {"input_tokens": 0, "output_tokens": 0, "cache_creation_input_tokens": 0, "cache_read_input_tokens": 0}
    tool_calls = tool_errors = requests = 0
    served: list[str] = []
    fallback_used = reminded = False
    status, output, stop_reason = "error", None, None
    started = datetime.now(timezone.utc)
    clock = time.monotonic()
    try:
        while True:
            if requests >= MAX_REQUESTS:
                status = "request_budget_exhausted"
                break
            requests += 1
            response = send(client, provider, system, tools, messages)
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
                calls = [b for b in response.content if getattr(b, "type", None) == "tool_use"]
                submitted = [b for b in calls if b.name == SUBMIT]
                if submitted:
                    # The case note ends the run, whatever else the turn asked for.
                    problem = case_note_error(submitted[0].input)
                    if problem:
                        status = "malformed_case_note"
                        transcript.append({"case_note_error": problem})
                    else:
                        status, output = "completed", submitted[0].input
                    break
                results = []
                for block in calls:
                    given = block.input if isinstance(block.input, dict) else {}
                    query, purpose = str(given.get("query", "")), str(given.get("purpose", ""))
                    if block.name != "query":
                        ok, text = False, f"error: there is no tool {block.name!r}; use query or {SUBMIT}"
                    elif tool_calls >= MAX_TOOL_CALLS:
                        ok, text = False, (f"error: the query budget is spent; call {SUBMIT} now, claiming only "
                                           "what earlier queries showed")
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
                # The turn ended without a case note. Remind once, the same way
                # in both arms; a second time ends the run without one.
                if reminded:
                    status = "ended_without_case_note"
                    break
                reminded = True
                transcript.append({"reminder": f"asked once to call {SUBMIT}"})
                messages.append({"role": "user", "content": f"Submit the case note by calling {SUBMIT}."})
                continue
            status = f"stopped:{stop_reason}"
            break
    except Exception as error:
        if not provider_error(error):
            raise
        status = f"provider_error:{type(error).__name__}"
        transcript.append({"error": redact(str(error))})
        log(f"  provider error: {redact(str(error))}")
    finally:
        execute.close()

    evidence = store if arm == "graph" else table_path
    meta = {
        "arm": arm,
        "status": status,
        "stop_reason": stop_reason,
        "provider": provider,
        "region": bedrock_region() if provider == "bedrock" else None,
        "model_requested": model_for(provider),
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
