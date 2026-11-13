"""Expected results, calculated from the raw events alone.

Nothing here imports clink or Relate, and nothing here reads what they
produced. The verifier compares clink's indicators and Relate's answers with
these functions' output.

The rules, stated once:

  fan-in    an account that receives transfers from at least five distinct
            senders inside one hour, the hours being those of the epoch
            (ts - ts % 3 600 000), by event time
  onward    a credit c and a debit d with c.dst = d.src and
            0 <= d.ts - c.ts <= 30 minutes, by event time
"""

from __future__ import annotations

from collections import defaultdict

HOUR_MS = 3_600_000
FAN_IN_MIN_SENDERS = 5
ONWARD_MAX_GAP_MS = 30 * 60 * 1000


def fan_in(events: list[dict]) -> list[dict]:
    groups: dict[tuple[str, int], list[dict]] = defaultdict(list)
    for e in events:
        groups[(e["dst"], e["ts"] - e["ts"] % HOUR_MS)].append(e)
    found = []
    for (account, start), members in groups.items():
        senders = {e["src"] for e in members}
        if len(senders) >= FAN_IN_MIN_SENDERS:
            found.append({
                "id": f"fan_in:{account}:{start}",
                "account": account,
                "window_start": start,
                "window_end": start + HOUR_MS,
                "senders": len(senders),
                "transfers": len(members),
                "total_minor": sum(e["amount_minor"] for e in members),
                "transfer_ids": sorted(e["transfer_id"] for e in members),
            })
    return sorted(found, key=lambda i: i["id"])


def fan_in_without_tolerance(events: list[dict]) -> list[dict]:
    """Fan-in as a stream processor with no out-of-order allowance sees it.

    Events are taken in arrival order. An hour is closed once an event at or
    past its end has arrived, and an event for a closed hour is dropped.
    """
    kept, greatest = [], None
    for e in events:
        end = e["ts"] - e["ts"] % HOUR_MS + HOUR_MS
        if greatest is None or greatest < end:
            kept.append(e)
        greatest = e["ts"] if greatest is None else max(greatest, e["ts"])
    return fan_in(kept)


def _pair(credit: dict, debit: dict) -> dict:
    return {
        "id": f"onward:{credit['transfer_id']}:{debit['transfer_id']}",
        "in_id": credit["transfer_id"],
        "out_id": debit["transfer_id"],
        "account": credit["dst"],
        "gap_ms": debit["ts"] - credit["ts"],
    }


def onward(events: list[dict]) -> list[dict]:
    debits: dict[str, list[dict]] = defaultdict(list)
    for e in events:
        debits[e["src"]].append(e)
    pairs = [_pair(c, d) for c in events for d in debits.get(c["dst"], ())
             if 0 <= d["ts"] - c["ts"] <= ONWARD_MAX_GAP_MS]
    return sorted(pairs, key=lambda p: p["id"])


def onward_in_arrival_order(events: list[dict]) -> list[dict]:
    """Onward transfers as a lookup made when each debit arrives finds them:
    only the credits that have already arrived can be matched."""
    arrived: dict[str, list[dict]] = defaultdict(list)
    pairs = []
    for e in events:
        pairs += [_pair(c, e) for c in arrived.get(e["src"], ())
                  if 0 <= e["ts"] - c["ts"] <= ONWARD_MAX_GAP_MS]
        arrived[e["dst"]].append(e)
    return sorted(pairs, key=lambda p: p["id"])


def investigate(events: list[dict], indicators: list[dict], pairs: list[dict]) -> list[dict]:
    """For each fan-in indicator, over the candidate onward-transfer paths that
    start at its contributing transfers: the most onward links in a path, the
    accounts where the paths end, the accounts along them, and which of those accounts
    sent transfers from a device another of them also used."""
    by_id = {e["transfer_id"]: e for e in events}
    following: dict[str, list[str]] = defaultdict(list)
    for p in pairs:
        following[p["in_id"]].append(p["out_id"])
    senders_on: dict[str, set[str]] = defaultdict(set)
    for e in events:
        senders_on[e["device"]].add(e["src"])

    results = []
    for indicator in indicators:
        depth: dict[str, int] = {}  # onward transfer -> most links from a contributing transfer
        pending = [(tid, 0) for tid in indicator["transfer_ids"]]
        while pending:
            tid, links = pending.pop()
            if links > len(events):
                raise ValueError("onward links form a cycle")
            for nxt in following.get(tid, ()):
                if depth.get(nxt, 0) < links + 1:
                    depth[nxt] = links + 1
                    pending.append((nxt, links + 1))
        route = {indicator["account"]} | {by_id[t]["dst"] for t in depth}
        shared = {device: sorted(users & route) for device, users in senders_on.items() if len(users & route) >= 2}
        results.append({
            "indicator": indicator["id"],
            "account": indicator["account"],
            "onward_depth": max(depth.values(), default=0),
            "terminal_accounts": sorted({by_id[t]["dst"] for t in depth if not following.get(t)}),
            "route_accounts": sorted(route),
            "shared_devices": dict(sorted(shared.items())),
        })
    return sorted(results, key=lambda r: r["indicator"])


def graph_counts(events: list[dict], indicators: list[dict], pairs: list[dict]) -> dict:
    return {
        "nodes": {
            "Account": len({a for e in events for a in (e["src"], e["dst"])}),
            "Device": len({e["device"] for e in events}),
            "Indicator": len(indicators),
            "Run": 1,
            "Transfer": len(events),
        },
        "relationships": {
            "ABOUT": len(indicators),
            "CONTRIBUTING": sum(len(i["transfer_ids"]) for i in indicators),
            "FROM_DEVICE": len(events),
            "PASSED_ON": len(pairs),
            "SENT": len(events),
            "TO": len(events),
        },
    }
