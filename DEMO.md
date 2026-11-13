# Demo script, 1 minute 50 seconds

A screen recording of one terminal in the repository, with the venv
installed and the store already built. Each section gives the time, what to
run and what to say. Commands are typed live; nothing needs the network
except section 4's recorded output, which is a file.

## 1. The question (0:00 to 0:20)

```bash
.venv/bin/python explore.py | sed -n '/WHERE THE TWO ALERTS DIFFER/,/device shared/p'
```

Say: "Two fan-in alerts from a bounded replay of 55 synthetic transfers. Six
senders into one account inside an hour, money passed on within 30 minutes:
as indicators they fire on the same rules. The question is which one matters,
and why, with every statement traceable to its events."

Point at the four rows marked "relationships, read from Relate": three onward
links against one, a resting account, and D-568 shared by three accounts on
one route only.

## 2. clink writes the evidence (0:20 to 0:45)

```bash
./rebuild.sh 2>&1 | sed -n '1,4p'
```

Say: "clink runs three SQL jobs over the event file by event time, and each
writes straight into one Relate file through its Relate connector. It is
published only if every job succeeded and every record reconciles."

Point at `published store/case.rl` and, if it appears, the write-write
conflict line: "three jobs wrote the same nodes at once; Relate refused one
transaction at commit and the sink retried it".

## 3. Relate answers the relationship questions (0:45 to 1:05)

```bash
.venv/bin/python explore.py --cypher "MATCH p = (:Transfer {id: 'T0002'})-[:PASSED_ON*]->(t:Transfer) WHERE NOT (t)-[:PASSED_ON]->() RETURN [n IN nodes(p) | n.id] AS route"
```

Say: "The store opens read-only in another process. One path query follows
the money from a contributing transfer to where it came to rest:
T0002, T0007, T0008, T0009."

## 4. The agent's case note (1:05 to 1:25)

Needs the recorded run in `runs/recorded/` (see the README's status).

```bash
sed -n '1,40p' runs/recorded/case-note/case_note.md
```

Say: "An agent queried the same store and wrote this case note: findings,
hypotheses and unresolved questions kept apart. Every finding cites
structured claims, and the checker's verdict sits beside each claim."

## 5. The checker refuses what is not true (1:25 to 1:50)

```bash
.venv/bin/python verify.py | grep -E 'planted|checks passed'
```

Say: "No model and no API key: every claim is checked against the original
events and against the graph. Two of these planted claims are what
arrival-order processing would have concluded: the late transfer T0012
missing from the alert, and a false resting point at A-5092. Both are
rejected. The conclusions hold for this bounded dataset only, and a recorded
relationship is evidence for an analyst, not proof of fraud."
