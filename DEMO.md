# Demo script, 1 minute 50 seconds

This is the script for the demo video, not the video. The video is to be
recorded from it: one terminal in the repository, with the venv installed.
Every command runs offline and needs no model or API key. Each section gives
the time, what to run and what to say.

## 1. Two alerts that look alike (0:00 to 0:25)

```bash
.venv/bin/python explore.py | sed -n '/WHERE THE TWO ALERTS DIFFER/,/device shared/p'
```

Say: "Two fan-in alerts from a bounded replay of 55 synthetic transfers. Each
fires on the same rule: six senders into one account inside an hour, and a
debit within 30 minutes. As alert rows they differ only in their totals."

Point at the four rows read from Relate: three onward links against one,
where the candidate paths end, and device D-568 shared by three accounts on
one alert's paths only.

## 2. The relationships, from the store (0:25 to 0:50)

```bash
.venv/bin/python explore.py --cypher "MATCH p = (:Transfer {id: 'T0002'})-[:PASSED_ON*]->(t:Transfer) WHERE NOT (t)-[:PASSED_ON]->() RETURN [n IN nodes(p) | n.id] AS path"
```

Say: "clink derived these onward links by event time and wrote them into one
Relate file, which opens read-only in another process. One path query follows
a candidate onward-transfer path from a contributing transfer to where it
ends: T0002, T0007, T0008, T0009. An onward link records timing: a debit
within 30 minutes of a credit to the same account. It is a candidate, not
proof that the same funds moved."

## 3. The case note (0:50 to 1:20)

```bash
sed -n '/^## Findings/,/^## Unresolved/p' runs/recorded/small-case-note-r4/case_note.md | cut -c1-160
```

Say: "An agent queried the same store and wrote this case note: findings,
hypotheses and unresolved questions kept apart. Every finding cites
structured claims, and the checker's verdict sits beside each one. The
hypotheses say what the data does not establish."

## 4. A claim the checker rejects (1:20 to 1:50)

```bash
.venv/bin/python verify.py | grep -E 'planted P[23]|checks passed' | cut -c1-150
```

Say: "No model and no API key: every claim is checked against the original
events and against the graph. These two planted claims are what processing
transfers in arrival order would have concluded: the late transfer T0012
missing from the alert, and a path ended too early at A-5092. Both are
rejected. The conclusions hold for this bounded dataset only, and a recorded
relationship is evidence for an analyst, not proof of fraud."
