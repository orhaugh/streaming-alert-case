#!/usr/bin/env python3
"""Seeded synthetic transfers at scale: 50,000 transfers over one week.

Six designed fan-in alerts sit in background traffic that raises none: three
designed as suspicious (deep onward chains, one branching, devices shared
along the way) and three as benign lookalikes (one onward link, none at all,
or a device shared only off the route). Decoys: a six-link onward chain tied
to no alert, devices on a route that an account off the route also uses, and
an account where a path ends that sends again hours later. Two inversions are placed as
in the small case: a credit at a window's edge that arrives after the next
hour's events, and a debit that arrives before the credit it follows.

The file is far larger than an agent can read through its query tool, and
than a model's context: investigating it means querying it.

Everything is derived from SEED; there is no wall clock. Writes
  <dir>/events.ndjson   what clink reads, in arrival order
  <dir>/scenario.json   the designed facts, for the verifier only
Account and device ids carry no role: they are drawn from shuffled pools.
"""

from __future__ import annotations

import json
import random
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

SEED = 20261116
BASE_MS = int(datetime(2026, 11, 16, 0, 0, tzinfo=timezone.utc).timestamp() * 1000)
DAYS = 7
HOUR_MS = 3_600_000
TOTAL = 50_000
BACKGROUND_ACCOUNTS = 12_000
HOUSEHOLD_DEVICES = 250          # background devices two accounts send from
MAX_BACKGROUND_SENDERS = 3       # per account and hour: the fan-in rule needs 5
MAX_DELAY_S = 200                # the longest ordinary arrival delay
LAG_MS = 300_000                 # the watermark lag the pipeline declares

rng = random.Random(SEED)
account_pool = [f"A-{n}" for n in range(10000, 100000)]
device_pool = [f"D-{n}" for n in range(10000, 100000)]
rng.shuffle(account_pool)
rng.shuffle(device_pool)


def new_account() -> str:
    return account_pool.pop()


def new_device() -> str:
    return device_pool.pop()


def at(day: int, hour: int, minute: int, second: int = 0) -> int:
    return BASE_MS + (((day * 24 + hour) * 60 + minute) * 60 + second) * 1000


events: list[dict] = []          # without ids yet: assigned in event-time order at the end
delay_ms: dict[int, int] = {}    # deliberate arrival delays, by index into events


def send(src: str, dst: str, amount: int, ts: int, device: str, delay_s: int | None = None) -> int:
    events.append({"src": src, "dst": dst, "amount_minor": amount, "ts": ts, "device": device})
    if delay_s is not None:
        delay_ms[len(events) - 1] = delay_s * 1000
    return len(events) - 1


def fan_in(account: str, times: list[int], amounts: list[int], late_index: int | None = None) -> tuple[list[str], list[int]]:
    """Distinct new senders, each on its own device, paying the account."""
    senders, idx = [], []
    for k, (ts, amount) in enumerate(zip(times, amounts)):
        sender = new_account()
        senders.append(sender)
        idx.append(send(sender, account, amount, ts, new_device(), 280 if k == late_index else None))
    return senders, idx


designed: list[dict] = []
marks: dict[str, int] = {}

# S1: suspicious. Seven senders, every credit followed by a debit, two waves,
# four onward links each to one end account; the four accounts that send on all
# send from one device. The last credit is late at the window's edge, and one
# debit arrives before the credit it follows.
V1, I1, I2, I3, R1 = (new_account() for _ in range(5))
d1 = new_device()
times = [at(0, 10, m) for m in (2, 9, 17, 23, 44, 52)] + [at(0, 10, 59)]
senders, credits = fan_in(V1, times, [61000, 38500, 52000, 47500, 66000, 41000, 73500], late_index=6)
marks["s1_late_credit"] = credits[6]
send(V1, I1, 196000, at(0, 10, 26), d1)
marks["s1_forward_credit"] = send(I1, I2, 191000, at(0, 10, 29), d1, delay_s=250)
marks["s1_forward_debit"] = send(I2, I3, 187500, at(0, 10, 33), d1, delay_s=0)
send(I3, R1, 184000, at(0, 10, 38), d1)
send(V1, I1, 176000, at(0, 11, 12), d1)
send(I1, I2, 172500, at(0, 11, 15), d1)
send(I2, I3, 169000, at(0, 11, 19), d1)
send(I3, R1, 166000, at(0, 11, 24), d1)
designed.append({"label": "suspicious", "account": V1, "window_start": at(0, 10, 0), "senders": sorted(senders),
                 "onward_depth": 4, "terminal": [R1], "route": sorted([V1, I1, I2, I3, R1]),
                 "shared_devices": {d1: sorted([V1, I1, I2, I3])}})

# S2: suspicious, branching. Six senders; the paths split after the first
# intermediary, three links deep to one end account and two to another;
# the alerted account and the first intermediary send from one device.
V2, J1, K1, R2a, R2b = (new_account() for _ in range(5))
d2 = new_device()
senders, _ = fan_in(V2, [at(1, 14, m) for m in (5, 11, 18, 24, 31, 37)], [28000, 35500, 31000, 44000, 26500, 39000])
send(V2, J1, 150000, at(1, 14, 33), d2)
send(V2, J1, 95000, at(1, 14, 50), d2)
send(J1, K1, 120000, at(1, 14, 36), d2)
send(K1, R2a, 117500, at(1, 14, 41), new_device())
send(J1, R2b, 118000, at(1, 14, 55), d2)
designed.append({"label": "suspicious", "account": V2, "window_start": at(1, 14, 0), "senders": sorted(senders),
                 "onward_depth": 3, "terminal": sorted([R2a, R2b]), "route": sorted([V2, J1, K1, R2a, R2b]),
                 "shared_devices": {d2: sorted([V2, J1])}})

# S3: suspicious, a long chain. Eight senders, five onward links to one end
# account; two intermediaries send from one device that an account off the
# route also uses.
V3, L1, L2, L3, L4, R3 = (new_account() for _ in range(6))
d3 = new_device()
senders, _ = fan_in(V3, [at(3, 3, m) for m in (1, 5, 8, 12, 16, 20, 24, 28)],
                    [19000, 23500, 21000, 26000, 18500, 24000, 22500, 20000])
send(V3, L1, 172000, at(3, 3, 30), new_device())
send(L1, L2, 169500, at(3, 3, 33), new_device())
send(L2, L3, 167000, at(3, 3, 36), d3)
send(L3, L4, 164000, at(3, 3, 40), new_device())
send(L4, R3, 161500, at(3, 3, 45), d3)
off_route_s3 = new_account()
send(off_route_s3, new_account(), 12000, at(5, 9, 14), d3)
designed.append({"label": "suspicious", "account": V3, "window_start": at(3, 3, 0), "senders": sorted(senders),
                 "onward_depth": 5, "terminal": [R3], "route": sorted([V3, L1, L2, L3, L4, R3]),
                 "shared_devices": {d3: sorted([L2, L4])}})

# B1: benign lookalike. Six equal credits, one onward link from four of them.
W1, Q1 = new_account(), new_account()
senders, _ = fan_in(W1, [at(0, 19, m) for m in (5, 12, 20, 27, 41, 50)], [2500] * 6)
send(W1, Q1, 9500, at(0, 19, 30), new_device())
designed.append({"label": "benign", "account": W1, "window_start": at(0, 19, 0), "senders": sorted(senders),
                 "onward_depth": 1, "terminal": [Q1], "route": sorted([W1, Q1]), "shared_devices": {}})

# B2: benign lookalike. Seven credits and no debit within 30 minutes of any:
# the account's one payment comes two hours later.
W2 = new_account()
senders, _ = fan_in(W2, [at(2, 12, m) for m in (3, 9, 16, 22, 35, 44, 51)], [4000, 3500, 5000, 4500, 3000, 4000, 5500])
send(W2, new_account(), 21000, at(2, 14, 55), new_device())
designed.append({"label": "benign", "account": W2, "window_start": at(2, 12, 0), "senders": sorted(senders),
                 "onward_depth": 0, "terminal": [], "route": [W2], "shared_devices": {}})

# B3: benign lookalike. One onward link; the account where it ends pays someone two
# hours later from a device an account off the route also uses.
W3, Q3, Z3 = new_account(), new_account(), new_account()
db3 = new_device()
senders, _ = fan_in(W3, [at(4, 16, m) for m in (3, 12, 19, 26, 33, 38)], [6000, 5500, 7000, 6500, 5000, 6000])
send(W3, Q3, 30000, at(4, 16, 40), new_device())
send(Q3, new_account(), 28000, at(4, 18, 50), db3)
send(Z3, new_account(), 15000, at(4, 20, 5), db3)
designed.append({"label": "benign", "account": W3, "window_start": at(4, 16, 0), "senders": sorted(senders),
                 "onward_depth": 1, "terminal": [Q3], "route": sorted([W3, Q3]), "shared_devices": {}})

# Decoy: a six-link onward chain on one shared device, tied to no alert.
chain = [new_account() for _ in range(7)]
dx = new_device()
send(new_account(), chain[0], 88000, at(5, 9, 1), new_device())
for k in range(6):
    send(chain[k], chain[k + 1], 87000 - 1500 * k, at(5, 9, 4 + 3 * k), dx)
decoys = {"chain": {"accounts": chain, "device": dx, "onward_links": 6},
          "devices_used_off_route": {d3: off_route_s3, db3: Z3}}

designed_accounts = {e[k] for e in events for k in ("src", "dst")}

# Background: everyone else, capped so that no account and hour sees more than
# three distinct senders, and never touching a designed account.
background = [new_account() for _ in range(BACKGROUND_ACCOUNTS)]
devices = {a: [new_device()] for a in background}
for a in rng.sample(background, BACKGROUND_ACCOUNTS // 20):
    devices[a].append(new_device())
for _ in range(HOUSEHOLD_DEVICES):
    shared = new_device()
    for a in rng.sample(background, 2):
        devices[a].append(shared)
senders_per_hour: dict[tuple[str, int], set[str]] = defaultdict(set)
span_ms = DAYS * 24 * HOUR_MS
while len(events) < TOTAL:
    src, dst = rng.sample(background, 2)
    ts = BASE_MS + rng.randrange(span_ms // 1000) * 1000
    hour = ts - ts % HOUR_MS
    seen = senders_per_hour[(dst, hour)]
    if src not in seen and len(seen) >= MAX_BACKGROUND_SENDERS:
        continue
    seen.add(src)
    amount = int(rng.lognormvariate(9.2, 1.0)) // 50 * 50 + 50
    device = devices[src][0] if rng.random() < 0.85 or len(devices[src]) == 1 else rng.choice(devices[src][1:])
    send(src, dst, amount, ts, device)

# Ids in event-time order; event times are unique to the second so that no two
# transfers tie.
order = sorted(range(len(events)), key=lambda i: (events[i]["ts"], i))
seen_ts: set[int] = set()
for i in order:
    while events[i]["ts"] in seen_ts:
        events[i]["ts"] += 1000
    seen_ts.add(events[i]["ts"])
order = sorted(range(len(events)), key=lambda i: (events[i]["ts"], i))
for n, i in enumerate(order, start=1):
    events[i] = {"transfer_id": f"T{n:06d}", **events[i]}

# Arrival order: each transfer arrives up to MAX_DELAY_S after its event time,
# apart from the two deliberate inversions.
arrival = {i: events[i]["ts"] + delay_ms.get(i, rng.randrange(MAX_DELAY_S + 1) * 1000) for i in range(len(events))}
written = sorted(range(len(events)), key=lambda i: (arrival[i], events[i]["ts"]))
assert max(arrival[i] - events[i]["ts"] for i in arrival) < LAG_MS


def tid(i: int) -> str:
    return events[i]["transfer_id"]


scenario = {
    "format": "cases",
    "seed": SEED,
    "transfers": len(events),
    "designed": {
        "alerts": designed,
        "decoys": decoys,
        "inversions": {
            "window_boundary": {"credit": tid(marks["s1_late_credit"]), "account": V1},
            "forwarding": {"credit": tid(marks["s1_forward_credit"]), "debit_arrives_first": tid(marks["s1_forward_debit"])},
        },
    },
}
assert not designed_accounts & set(background)

out = Path(sys.argv[1] if len(sys.argv) > 1 else "data/large")
out.mkdir(parents=True, exist_ok=True)
with (out / "events.ndjson").open("w") as f:
    for i in written:
        f.write(json.dumps(events[i], separators=(",", ":")) + "\n")
(out / "scenario.json").write_text(json.dumps(scenario, indent=1) + "\n")
print(f"wrote {len(events)} transfers to {out}/events.ndjson and the designed facts to {out}/scenario.json")
