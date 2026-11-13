"""Structured claims about the bounded dataset, and the checker that judges them.

A claim is one of a closed set of types. Each type has one rule, and the
checker applies that rule twice: to the facts derived from the original event
file and to the facts read from the Relate graph (facts.py). A claim is

  supported     when it holds in both,
  unsupported   when it holds in neither,
  inconsistent  when the two sources disagree (a damaged or foreign store),
  malformed     when it is not a well-formed claim of a known type.

The checker is deterministic and uses no model. It validates references and
structured values. It does not read, and cannot validate, prose: a finding's
wording is only as good as the claims it cites.
"""

from __future__ import annotations

import re
from typing import Any

from .facts import Facts

# ---------------------------------------------------------------------------
# The schema the agent's structured output must follow. Every object is
# closed and every property required; a value the claim does not assert is
# null.

_STR = {"type": "string"}
_INT = {"type": "integer"}
_STR_LIST = {"type": "array", "items": _STR}


def _nullable(schema: dict) -> dict:
    return {"anyOf": [schema, {"type": "null"}]}


ABSENCE_KINDS = ("no_shared_device_on_route", "no_onward_link_from_transfer", "no_fan_in_alert_for_account")
COUNT_PATTERNS = ("fan_in_alerts", "transfers", "onward_links", "accounts", "devices")

# A claim states every value of its type. Only three links are optional (null
# when not asserted): where a path starts and where it rests, and the route a
# shared device is judged on. Structured outputs also limit how many
# nullable fields a schema may have.
CLAIM_FIELDS: dict[str, dict[str, dict]] = {
    "event": {
        "transfer": _STR, "sender": _STR, "receiver": _STR, "amount_minor": _INT, "event_time_ms": _INT,
        "device": _STR,
    },
    "indicator": {
        "indicator": _STR, "account": _STR, "window_start_ms": _INT, "window_end_ms": _INT, "senders": _INT,
        "transfers": _INT, "total_minor": _INT, "contributing": _STR_LIST,
    },
    "onward_path": {
        "transfers": _STR_LIST, "from_indicator": _nullable(_STR), "comes_to_rest_at": _nullable(_STR),
    },
    "onward_reach": {
        "indicator": _STR, "max_depth": _INT, "terminal_accounts": _STR_LIST, "route_accounts": _STR_LIST,
    },
    "shared_device": {
        "device": _STR, "accounts": _STR_LIST, "on_route_of": _nullable(_STR),
    },
    "absence": {
        "kind": {"type": "string", "enum": list(ABSENCE_KINDS)}, "subject": _STR,
    },
    "count": {
        "pattern": {"type": "string", "enum": list(COUNT_PATTERNS)}, "value": _INT,
    },
}

CLAIM_MEANINGS = {
    "event": "the transfer exists with exactly this sender, receiver, amount, event time and device",
    "indicator": "the fan-in indicator exists with exactly these values; contributing is the complete set of its "
                 "contributing transfers",
    "onward_path": "each consecutive pair of transfers is a recorded onward link; from_indicator: the first transfer "
                   "contributes to that indicator; comes_to_rest_at: the last transfer was paid to that account and "
                   "was not passed on",
    "onward_reach": "for the indicator, the longest chain of onward links from its contributing transfers, the "
                    "accounts where its routes come to rest, and every account on its routes, each as a complete set",
    "shared_device": "the device was used to send from every listed account (two or more); on_route_of: the listed "
                     "accounts are exactly the accounts on that indicator's routes that sent from the device",
    "absence": "no_shared_device_on_route: no device was used by two or more accounts on the indicator's routes; "
               "no_onward_link_from_transfer: the transfer was not passed on; no_fan_in_alert_for_account: the "
               "account has no fan-in indicator",
    "count": "the number of fan-in alerts, transfers, onward links, accounts or devices in the bounded dataset",
}


def claim_schema(kind: str) -> dict:
    fields = CLAIM_FIELDS[kind]
    return {
        "type": "object",
        "properties": {"id": _STR, "type": {"type": "string", "const": kind}, **fields},
        "required": ["id", "type", *fields],
        "additionalProperties": False,
    }


def _item(props: dict) -> dict:
    return {"type": "array", "items": {"type": "object", "properties": props, "required": list(props),
                                        "additionalProperties": False}}


# The agent's output groups its claims by type, one array each: a union over
# the seven claim shapes compiles to a grammar too large for structured
# outputs. flatten_claims() turns the groups back into one list of typed claims.
OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "findings": _item({"id": _STR, "statement": _STR, "claim_ids": _STR_LIST}),
        "hypotheses": _item({"id": _STR, "statement": _STR, "references": _STR_LIST}),
        "unresolved": _item({"id": _STR, "question": _STR, "references": _STR_LIST}),
        "claims": {
            "type": "object",
            "properties": {kind: _item({"id": _STR, **fields}) for kind, fields in CLAIM_FIELDS.items()},
            "required": list(CLAIM_FIELDS),
            "additionalProperties": False,
        },
    },
    "required": ["findings", "hypotheses", "unresolved", "claims"],
    "additionalProperties": False,
}


def flatten_claims(claims: Any) -> list:
    """The agent's claims as one list, each with its type. Grouped claims
    ({"event": [...], ...}) gain a "type"; a list is returned as it is."""
    if isinstance(claims, dict):
        return [{"id": c.get("id"), "type": kind, **{k: v for k, v in c.items() if k != "id"}}
                if isinstance(c, dict) else c
                for kind, group in claims.items() for c in (group if isinstance(group, list) else [group])]
    return claims if isinstance(claims, list) else []


_SECTIONS = {"findings": ("id", "statement", "claim_ids"), "hypotheses": ("id", "statement", "references"),
             "unresolved": ("id", "question", "references")}


def case_note_error(note: Any) -> str | None:
    """Why a submitted case note is not one, or None. Checks its envelope:
    the three sections and the claim groups. Each claim's own shape is judged
    by the checker, which counts a bad one as malformed."""
    if not isinstance(note, dict):
        return "the case note is not an object"
    if set(note) != set(OUTPUT_SCHEMA["properties"]):
        return f"the case note has the fields {sorted(note)}, not {sorted(OUTPUT_SCHEMA['properties'])}"
    for section, fields in _SECTIONS.items():
        items = note[section]
        if not isinstance(items, list):
            return f"{section} is not a list"
        for item in items:
            if not isinstance(item, dict) or set(item) != set(fields):
                return f"an entry in {section} does not have exactly the fields {list(fields)}"
            if not all(isinstance(item[f], str) for f in fields[:2]):
                return f"an entry in {section} has a field that is not text"
            if not isinstance(item[fields[2]], list) or not all(isinstance(r, str) for r in item[fields[2]]):
                return f"an entry in {section} has {fields[2]} that is not a list of ids"
    claims = note["claims"]
    if not isinstance(claims, dict) or not set(claims) <= set(CLAIM_FIELDS):
        return f"claims must be grouped by the types {list(CLAIM_FIELDS)}"
    if not all(isinstance(group, list) for group in claims.values()):
        return "each claim group must be a list"
    return None


# ---------------------------------------------------------------------------
# Shape: a claim that does not match its type's fields is malformed, whatever
# it says.

def _conforms(value: Any, schema: dict) -> bool:
    if "anyOf" in schema:
        return any(_conforms(value, s) for s in schema["anyOf"])
    kind = schema.get("type")
    if kind == "null":
        return value is None
    if kind == "string":
        return isinstance(value, str) and ("enum" not in schema or value in schema["enum"])
    if kind == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if kind == "array":
        return isinstance(value, list) and all(_conforms(v, schema["items"]) for v in value)
    return False


def shape_error(claim: Any) -> str | None:
    if not isinstance(claim, dict):
        return "not an object"
    kind = claim.get("type")
    if kind not in CLAIM_FIELDS:
        return f"unknown claim type {kind!r}"
    fields = CLAIM_FIELDS[kind]
    expected = {"id", "type", *fields}
    if set(claim) != expected:
        missing, extra = sorted(expected - set(claim)), sorted(set(claim) - expected)
        return f"fields differ from a {kind} claim: missing {missing}, unexpected {extra}"
    if not isinstance(claim["id"], str) or not claim["id"]:
        return "id is not a non-empty string"
    for name, schema in fields.items():
        if not _conforms(claim[name], schema):
            return f"{name} has the wrong type for a {kind} claim"
    return None


# ---------------------------------------------------------------------------
# The rules. Each returns (holds, reason) for one source's facts.

def _differences(stated: dict, recorded: dict) -> list[str]:
    return [f"{name} is {recorded[name]!r}, not {value!r}" for name, value in stated.items()
            if value is not None and recorded.get(name) != value]


def _event(c: dict, f: Facts) -> tuple[bool, str]:
    t = f.transfers.get(c["transfer"])
    if t is None:
        return False, f"{c['transfer']} is not a transfer in the dataset"
    stated = {"src": c["sender"], "dst": c["receiver"], "amount_minor": c["amount_minor"],
              "ts": c["event_time_ms"], "device": c["device"]}
    wrong = _differences(stated, t)
    return (not wrong), ("; ".join(wrong) if wrong else f"{c['transfer']} as recorded")


def _indicator(c: dict, f: Facts) -> tuple[bool, str]:
    i = f.indicators.get(c["indicator"])
    if i is None:
        return False, f"there is no fan-in indicator {c['indicator']}"
    stated = {"account": c["account"], "window_start": c["window_start_ms"], "window_end": c["window_end_ms"],
              "senders": c["senders"], "transfers": c["transfers"], "total_minor": c["total_minor"]}
    wrong = _differences(stated, i)
    if c["contributing"] is not None and sorted(c["contributing"]) != i["transfer_ids"]:
        extra = sorted(set(c["contributing"]) - set(i["transfer_ids"]))
        missing = sorted(set(i["transfer_ids"]) - set(c["contributing"]))
        repeated = len(c["contributing"]) != len(set(c["contributing"]))
        wrong.append(f"contributing transfers differ: not contributing {extra}, missing {missing}"
                     + (", a transfer listed twice" if repeated else ""))
    return (not wrong), ("; ".join(wrong) if wrong else f"{c['indicator']} as recorded")


def _onward_path(c: dict, f: Facts) -> tuple[bool, str]:
    path = c["transfers"]
    if len(path) < 2:
        return False, "a path needs at least two transfers"
    unknown = [t for t in path if t not in f.transfers]
    if unknown:
        return False, f"not transfers in the dataset: {unknown}"
    for a, b in zip(path, path[1:]):
        if f"onward:{a}:{b}" not in f.links:
            return False, f"no recorded onward link from {a} to {b}"
    if c["from_indicator"] is not None:
        i = f.indicators.get(c["from_indicator"])
        if i is None:
            return False, f"there is no fan-in indicator {c['from_indicator']}"
        if path[0] not in i["transfer_ids"]:
            return False, f"{path[0]} does not contribute to {c['from_indicator']}"
    if c["comes_to_rest_at"] is not None:
        last = f.transfers[path[-1]]
        if last["dst"] != c["comes_to_rest_at"]:
            return False, f"{path[-1]} was paid to {last['dst']}, not {c['comes_to_rest_at']}"
        onward = f.links_from(path[-1])
        if onward:
            return False, f"{path[-1]} was passed on: {sorted(link_id for link_id, link in f.links.items() if link['in_id'] == path[-1])}"
    return True, f"{len(path) - 1} recorded onward link(s)"


def _onward_reach(c: dict, f: Facts) -> tuple[bool, str]:
    inv = f.investigation.get(c["indicator"])
    if inv is None:
        return False, f"there is no fan-in indicator {c['indicator']}"
    wrong = []
    if c["max_depth"] is not None and c["max_depth"] != inv["onward_depth"]:
        wrong.append(f"the longest chain is {inv['onward_depth']} onward link(s), not {c['max_depth']}")
    for name, key in (("terminal_accounts", "terminal_accounts"), ("route_accounts", "route_accounts")):
        if c[name] is not None and sorted(set(c[name])) != inv[key]:
            wrong.append(f"{name} are {inv[key]}, not {sorted(set(c[name]))}")
    return (not wrong), ("; ".join(wrong) if wrong else f"{c['indicator']}'s routes as recorded")


def _shared_device(c: dict, f: Facts) -> tuple[bool, str]:
    users = f.device_senders.get(c["device"])
    if users is None:
        return False, f"{c['device']} is not a device in the dataset"
    accounts = set(c["accounts"])
    if len(accounts) < 2:
        return False, "a shared device needs two or more accounts"
    strangers = sorted(accounts - users)
    if strangers:
        return False, f"{c['device']} was not used to send from {strangers}"
    if c["on_route_of"] is not None:
        inv = f.investigation.get(c["on_route_of"])
        if inv is None:
            return False, f"there is no fan-in indicator {c['on_route_of']}"
        on_route = set(inv["route_accounts"])
        off = sorted(accounts - on_route)
        if off:
            return False, f"not on {c['on_route_of']}'s routes: {off}"
        complete = sorted(users & on_route)
        if sorted(accounts) != complete:
            return False, f"the route accounts that sent from {c['device']} are {complete}"
    return True, f"{c['device']} sent from {sorted(accounts)}"


def _absence(c: dict, f: Facts) -> tuple[bool, str]:
    subject = c["subject"]
    if c["kind"] == "no_shared_device_on_route":
        inv = f.investigation.get(subject)
        if inv is None:
            return False, f"there is no fan-in indicator {subject}"
        if inv["shared_devices"]:
            return False, f"shared on {subject}'s routes: {inv['shared_devices']}"
        return True, f"no device is shared between accounts on {subject}'s routes"
    if c["kind"] == "no_onward_link_from_transfer":
        if subject not in f.transfers:
            return False, f"{subject} is not a transfer in the dataset"
        onward = sorted(link_id for link_id, link in f.links.items() if link["in_id"] == subject)
        return (not onward), (f"{subject} was passed on: {onward}" if onward else f"{subject} was not passed on")
    if c["kind"] == "no_fan_in_alert_for_account":
        if subject not in f.accounts:
            return False, f"{subject} is not an account in the dataset"
        alerts = sorted(i for i, rec in f.indicators.items() if rec["account"] == subject)
        return (not alerts), (f"{subject} has {alerts}" if alerts else f"{subject} has no fan-in indicator")
    return False, f"unknown absence kind {c['kind']!r}"


def _count(c: dict, f: Facts) -> tuple[bool, str]:
    actual = {"fan_in_alerts": len(f.indicators), "transfers": len(f.transfers), "onward_links": len(f.links),
              "accounts": len(f.accounts), "devices": len(f.devices)}[c["pattern"]]
    return (actual == c["value"]), (f"{c['pattern']} is {actual}" + ("" if actual == c["value"] else f", not {c['value']}"))


RULES = {"event": _event, "indicator": _indicator, "onward_path": _onward_path, "onward_reach": _onward_reach,
         "shared_device": _shared_device, "absence": _absence, "count": _count}


def check_claim(claim: Any, events: Facts, graph: Facts) -> dict:
    error = shape_error(claim)
    if error:
        ident = claim.get("id") if isinstance(claim, dict) else None
        return {"claim": ident, "type": claim.get("type") if isinstance(claim, dict) else None,
                "status": "malformed", "reason": error}
    rule = RULES[claim["type"]]
    in_events, why_events = rule(claim, events)
    in_graph, why_graph = rule(claim, graph)
    status = ("supported" if in_events and in_graph else
              "unsupported" if not in_events and not in_graph else "inconsistent")
    return {"claim": claim["id"], "type": claim["type"], "status": status,
            "events": why_events, "graph": why_graph}


def check_claims(claims: list, events: Facts, graph: Facts) -> list[dict]:
    verdicts = [check_claim(c, events, graph) for c in claims]
    seen: dict[str, int] = {}
    for v in verdicts:
        if v["claim"] is not None:
            seen[v["claim"]] = seen.get(v["claim"], 0) + 1
    for v in verdicts:
        if v["claim"] is not None and seen[v["claim"]] > 1 and v["status"] != "malformed":
            v["status"], v["reason"] = "malformed", f"claim id {v['claim']} is used more than once"
    return verdicts


# ---------------------------------------------------------------------------
# References: the stable ids cited anywhere in an output, prose included.
# Validating that a reference resolves says nothing about the sentence around it.

_COMPOUND = [
    ("path", re.compile(r"\bpath:T\d{4}(?:>T\d{4})+")),
    ("indicator", re.compile(r"\bfan_in:A-\d{4}:\d{13}\b")),
    ("link", re.compile(r"\bonward:T\d{4}:T\d{4}\b")),
    ("run", re.compile(r"\brun:[0-9a-f]{12}\b")),
]
_SIMPLE = [
    ("transfer", re.compile(r"\bT\d{4}\b")),
    ("account", re.compile(r"\bA-\d{4}\b")),
    ("device", re.compile(r"\bD-\d{3}\b")),
]


def _strings(value: Any):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for v in value.values():
            yield from _strings(v)
    elif isinstance(value, list):
        for v in value:
            yield from _strings(v)


def references_in(value: Any) -> list[tuple[str, str]]:
    """Every distinct (kind, id) cited in any string of a JSON value."""
    found: set[tuple[str, str]] = set()
    for text in _strings(value):
        for kind, pattern in _COMPOUND:
            found |= {(kind, m) for m in pattern.findall(text)}
            text = pattern.sub(" ", text)
        for kind, pattern in _SIMPLE:
            found |= {(kind, m) for m in pattern.findall(text)}
    return sorted(found)


def resolves(kind: str, ident: str, f: Facts) -> bool:
    if kind == "transfer":
        return ident in f.transfers
    if kind == "account":
        return ident in f.accounts
    if kind == "device":
        return ident in f.devices
    if kind == "indicator":
        return ident in f.indicators
    if kind == "link":
        return ident in f.links
    if kind == "run":
        return f.run is not None and ident == f"run:{f.run['dataset_sha256'][:12]}"
    if kind == "path":
        hops = ident[len("path:"):].split(">")
        return all(f"onward:{a}:{b}" in f.links for a, b in zip(hops, hops[1:]))
    return False
