"""The answer key: what a complete investigation of this bounded dataset must
establish, derived from the original events alone (facts.from_events).

It is used to score outputs, never shown to an agent. Each item is covered
only by a claim the checker finds supported, so the checker decides what is
true and the key decides what was required.
"""

from __future__ import annotations

from .facts import Facts


def expected_claims(events: Facts) -> list[dict]:
    """A complete, supported claim set: the reference answer, as claims."""
    claims: list[dict] = []

    def add(claim_type: str, **fields) -> None:
        claims.append({"id": f"K{len(claims) + 1}", "type": claim_type, **fields})

    add("count", pattern="fan_in_alerts", value=len(events.indicators))
    for ident, i in sorted(events.indicators.items()):
        add("indicator", indicator=ident, account=i["account"], window_start_ms=i["window_start"],
            window_end_ms=i["window_end"], senders=i["senders"], transfers=i["transfers"],
            total_minor=i["total_minor"], contributing=list(i["transfer_ids"]))
        inv = events.investigation[ident]
        add("onward_reach", indicator=ident, max_depth=inv["onward_depth"],
            terminal_accounts=list(inv["terminal_accounts"]), route_accounts=list(inv["route_accounts"]))
        if inv["shared_devices"]:
            for device, accounts in inv["shared_devices"].items():
                add("shared_device", device=device, accounts=list(accounts), on_route_of=ident)
        else:
            add("absence", kind="no_shared_device_on_route", subject=ident)
    return claims


def key_items(events: Facts) -> list[dict]:
    """The required facts, one item each."""
    items = [{"key": "alerts:count", "what": f"there are exactly {len(events.indicators)} fan-in alerts"}]
    for ident, i in sorted(events.indicators.items()):
        inv = events.investigation[ident]
        items.append({"key": f"alert:{ident}",
                      "what": f"{ident}: {i['senders']} senders, total {i['total_minor']}, contributing {i['transfer_ids']}"})
        items.append({"key": f"reach:{ident}",
                      "what": f"{ident}: at most {inv['onward_depth']} onward link(s), coming to rest at {inv['terminal_accounts']}"})
        if inv["shared_devices"]:
            for device, accounts in inv["shared_devices"].items():
                items.append({"key": f"device:{ident}:{device}", "what": f"{ident}: {device} sent from {accounts}"})
        else:
            items.append({"key": f"nodevice:{ident}", "what": f"{ident}: no device shared on its routes"})
    return items


def covered(events: Facts, claims: list, verdicts: list[dict]) -> dict[str, bool]:
    """Which key items a set of claims covers. A claim counts only if it is
    well formed and the checker found it supported, and only when it states
    the values the item requires (a claim that leaves them null covers nothing)."""
    supported = [c for c, v in zip(claims, verdicts) if v["status"] == "supported"]
    result = {item["key"]: False for item in key_items(events)}

    for c in supported:
        kind = c["type"]
        if kind == "count" and c["pattern"] == "fan_in_alerts":
            result["alerts:count"] = True
        elif kind == "indicator" and None not in (c["senders"], c["total_minor"], c["contributing"]):
            result[f"alert:{c['indicator']}"] = True
        elif kind == "onward_reach" and c["max_depth"] is not None and c["terminal_accounts"] is not None:
            result[f"reach:{c['indicator']}"] = True
        elif kind == "onward_path" and c["from_indicator"] is not None and c["comes_to_rest_at"] is not None:
            inv = events.investigation.get(c["from_indicator"])
            if inv and len(c["transfers"]) - 1 == inv["onward_depth"] and inv["terminal_accounts"] == [c["comes_to_rest_at"]]:
                result[f"reach:{c['from_indicator']}"] = True
        elif kind == "shared_device" and c["on_route_of"] is not None:
            result[f"device:{c['on_route_of']}:{c['device']}"] = True
        elif kind == "absence" and c["kind"] == "no_shared_device_on_route":
            result[f"nodevice:{c['subject']}"] = True
    return {k: result[k] for k in sorted(result)}
