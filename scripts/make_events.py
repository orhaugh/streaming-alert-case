#!/usr/bin/env python3
"""Seeded synthetic transfers for the spike.

One suspicious case, one benign lookalike and background traffic, written in
ARRIVAL order, which differs from event-time order. Two inversions are placed
deliberately, because each one changes an answer if events are processed in
the order they arrive:

  1. a credit that belongs to the 09:00 window arrives after an event from the
     10:00 window;
  2. the debit that passes a credit on arrives before that credit.

Everything is derived from SEED; there is no wall clock. Writes

  data/events.ndjson   what clink reads
  data/scenario.json   the designed facts, for the verifier only; clink and
                       the loader never read it

Account and device ids carry no role: the roles live in scenario.json.
"""

from __future__ import annotations

import hashlib
import json
import random
import sys
from datetime import datetime, timezone
from pathlib import Path

SEED = 20261112
BASE_MS = int(datetime(2026, 11, 10, 9, 0, tzinfo=timezone.utc).timestamp() * 1000)
MAX_DELAY_S = 200   # the longest an event may arrive behind its event time
LAG_MS = 300_000    # the watermark lag the pipeline declares; must exceed every disorder
HOUR_MS = 3_600_000


def at(hour: int, minute: int, second: int = 0) -> int:
    """Event time as epoch milliseconds, hh:mm:ss UTC on the scenario's day."""
    return BASE_MS + ((hour - 9) * 3600 + minute * 60 + second) * 1000


def build() -> tuple[list[dict], dict]:
    rng = random.Random(SEED)
    account_numbers = iter(rng.sample(range(1000, 10000), 120))
    device_numbers = iter(rng.sample(range(100, 1000), 120))
    accounts: dict[str, str] = {}
    devices: dict[str, str] = {}
    # Roles that operate from a device another role also uses.
    device_role = {"s_collect": "s_shared", "s_hop1": "s_shared", "s_hop2": "s_shared",
                   "f1": "family", "f2": "family"}

    def account(role: str) -> str:
        if role not in accounts:
            accounts[role] = f"A-{next(account_numbers)}"
        return accounts[role]

    def device(role: str) -> str:
        key = device_role.get(role, role)
        if key not in devices:
            devices[key] = f"D-{next(device_numbers)}"
        return devices[key]

    rows: list[dict] = []

    def transfer(src: str, dst: str, amount_minor: int, ts: int, delay_s: int | None = None, tag: str = "") -> None:
        rows.append({"src_role": src, "dst_role": dst, "src": account(src), "dst": account(dst),
                     "amount_minor": amount_minor, "ts": ts, "device": device(src),
                     "delay_s": delay_s, "tag": tag})

    # Suspicious: six unrelated senders pay one account inside the 09:00 hour;
    # it is passed on in two tranches through two further accounts.
    transfer("s_send1", "s_collect", 42000, at(9, 5, 10))
    transfer("s_send2", "s_collect", 61500, at(9, 10, 40))
    transfer("s_send3", "s_collect", 38000, at(9, 18, 5))
    transfer("s_collect", "s_hop1", 138000, at(9, 24, 0), delay_s=200, tag="forwarding_credit")
    transfer("s_hop1", "s_hop2", 135000, at(9, 26, 30), delay_s=5, tag="forwarding_debit")
    transfer("s_hop2", "s_cashout", 132000, at(9, 29, 45))
    transfer("s_send4", "s_collect", 89000, at(9, 37, 30))
    transfer("s_send5", "s_collect", 50500, at(9, 44, 15))
    transfer("s_send6", "s_collect", 76000, at(9, 58, 40), delay_s=200, tag="boundary_credit")
    transfer("s_collect", "s_hop1", 210000, at(10, 3, 20))
    transfer("s_hop1", "s_hop2", 206000, at(10, 5, 50))
    transfer("s_hop2", "s_cashout", 202000, at(10, 8, 10))

    # Benign lookalike: six members pay a collection account inside the 14:00
    # hour; it pays a supplier within half an hour and the money stops there.
    for n, (minute, second) in enumerate([(2, 20), (9, 5), (15, 40), (22, 10), (30, 30), (41, 0)], start=1):
        transfer(f"b_pay{n}", "b_collect", 2500, at(14, minute, second))
    transfer("b_collect", "b_supplier", 14000, at(14, 50, 0))
    transfer("b_supplier", "b_staff", 90000, at(18, 5, 0))

    # Background.
    transfer("n10", "n11", 1999, at(10, 0, 30), delay_s=10, tag="boundary_next_window")
    transfer("f1", "shop1", 2350, at(10, 15, 0))          # two accounts, one device,
    transfer("f2", "shop1", 4120, at(11, 40, 0))          # no alert anywhere near them
    for n, minute in enumerate([5, 15, 25, 35], start=1):  # four senders: below the threshold
        transfer(f"n{n}", "g", 5000 + 100 * n, at(11, minute, 0))
    transfer("n5", "k", 30000, at(12, 0, 0))               # passed on after 45 minutes:
    transfer("k", "n6", 29000, at(12, 45, 0))              # outside the 30 minute rule
    for n, (minute, sender) in enumerate([(5, "n7"), (12, "n8"), (20, "n9"), (31, "n7"), (44, "n8"), (52, "n9")]):
        transfer(sender, "q", 1200 + 10 * n, at(15, minute, 0))  # six credits, three senders
    for _ in range(20):
        a, b = rng.sample([f"r{n}" for n in range(1, 13)], 2)
        transfer(a, b, rng.randrange(500, 60000), at(9, 0, 0) + rng.randrange(0, 9 * 3600) * 1000)

    # Stable ids in event-time order; the file is written in arrival order.
    rows.sort(key=lambda r: (r["ts"], r["src"], r["dst"]))
    for n, r in enumerate(rows, start=1):
        r["transfer_id"] = f"T{n:04d}"
        if r["delay_s"] is None:
            r["delay_s"] = rng.randrange(0, MAX_DELAY_S + 1)
        r["arrival"] = r["ts"] + r["delay_s"] * 1000
    rows.sort(key=lambda r: (r["arrival"], r["transfer_id"]))

    tagged = {r["tag"]: r["transfer_id"] for r in rows if r["tag"]}
    s_route = [account(r) for r in ("s_collect", "s_hop1", "s_hop2", "s_cashout")]
    scenario = {
        "seed": SEED,
        "lag_ms": LAG_MS,
        "designed": {
            "suspicious": {
                "account": account("s_collect"),
                "window_start": at(9, 0, 0),
                "senders": sorted(account(f"s_send{n}") for n in range(1, 7)),
                "route": s_route,
                "onward_depth": 3,
                "shared_device": {"device": device("s_collect"), "accounts": sorted(s_route[:3])},
            },
            "benign": {
                "account": account("b_collect"),
                "window_start": at(14, 0, 0),
                "senders": sorted(account(f"b_pay{n}") for n in range(1, 7)),
                "route": [account("b_collect"), account("b_supplier")],
                "onward_depth": 1,
                "shared_device": None,
            },
            "shared_device_off_route": {"device": device("f1"), "accounts": sorted([account("f1"), account("f2")])},
            "inversions": {
                "window_boundary": {"credit": tagged["boundary_credit"], "arrives_after": tagged["boundary_next_window"]},
                "forwarding": {"credit": tagged["forwarding_credit"], "debit_arrives_first": tagged["forwarding_debit"]},
            },
        },
    }
    events = [{k: r[k] for k in ("transfer_id", "src", "dst", "amount_minor", "ts", "device")} for r in rows]
    return events, scenario


def max_disorder_ms(events: list[dict]) -> int:
    """How far behind the greatest event time already written an event sits."""
    worst, seen = 0, None
    for e in events:
        if seen is not None:
            worst = max(worst, seen - e["ts"])
        seen = e["ts"] if seen is None else max(seen, e["ts"])
    return worst


def main() -> int:
    out = Path(sys.argv[1] if len(sys.argv) > 1 else "data")
    out.mkdir(parents=True, exist_ok=True)
    events, scenario = build()
    body = "".join(json.dumps(e, separators=(",", ":")) + "\n" for e in events)
    (out / "events.ndjson").write_text(body)
    disorder = max_disorder_ms(events)
    if disorder >= LAG_MS:
        print(f"disorder {disorder} ms is not below the declared lag {LAG_MS} ms", file=sys.stderr)
        return 1
    scenario.update(events=len(events), sha256=hashlib.sha256(body.encode()).hexdigest(), max_disorder_ms=disorder)
    (out / "scenario.json").write_text(json.dumps(scenario, indent=2) + "\n")
    print(f"events          {len(events)}")
    print(f"sha256          {scenario['sha256']}")
    print(f"max disorder    {disorder} ms (declared lag {LAG_MS} ms)")
    print(f"out of order    {sum(1 for a, b in zip(events, events[1:]) if b['ts'] < a['ts'])} adjacent inversions")
    return 0


if __name__ == "__main__":
    sys.exit(main())
