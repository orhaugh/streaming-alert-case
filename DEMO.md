# Demo script, 1 minute 50 seconds

This is the script for the demo video, not the video. The video is to be
recorded from it: one terminal in the repository, with the venv installed,
and for section 3 the relate command line (`scripts/fetch-relate-cli.sh`) and
`requirements-mcp.txt`. Every command runs offline and needs no model or API
key. Each section gives the time, what to run and what to say.

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

## 2. The relationships, from the store (0:25 to 0:45)

```bash
.venv/bin/python explore.py --cypher "MATCH p = (:Transfer {id: 'T0002'})-[:PASSED_ON*]->(t:Transfer) WHERE NOT (t)-[:PASSED_ON]->() RETURN [n IN nodes(p) | n.id] AS path"
```

Say: "clink derived these onward links by event time and wrote them into one
Relate file. One path query follows a candidate path from a contributing
transfer to where it ends: T0002, T0007, T0008, T0009. An onward link records
timing, a debit within 30 minutes of a credit, not proof that funds moved."

## 3. The same file, through Relate's MCP server (0:45 to 1:00)

```bash
.venv/bin/python mcp_check.py --case small | sed -n '/as .mcp.json starts it/,/store unchanged/p' | cut -c1-150
```

Say: "Any MCP host can open the same file through Relate's own MCP server,
read-only. This check talks to it as an agent host does: two read-only tools,
every path equal to the reference, writes refused, the store unchanged."

## 4. The case note (1:00 to 1:25)

```bash
sed -n '/^## Findings/,/^## Unresolved/p' runs/recorded/small-case-note-r4/case_note.md | cut -c1-160
```

Say: "An agent queried the same store and wrote this case note: findings,
hypotheses and unresolved questions kept apart. Every finding cites
structured claims, and the checker's verdict sits beside each one."

## 5. A claim the checker rejects (1:25 to 1:50)

```bash
.venv/bin/python verify.py | grep -E 'planted P[23]|checks passed' | cut -c1-150
```

Say: "No model and no API key: every claim is checked against the original
events and the graph. These planted claims are what arrival-order processing
would have concluded: late transfer T0012 missing from the alert, and a path
ended too early at A-5092. Both are rejected. This holds for this bounded
dataset only, and a relationship is evidence, not proof of fraud."
