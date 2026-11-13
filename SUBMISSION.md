# Submission description (draft for Devpost)

Text prepared for the Devpost form. Nothing here has been submitted.

## Name

streaming-alert-case

## Elevator pitch

Two fraud alerts fire on the same rule. Event-time evidence from clink and
connected context in Relate show which deserves attention, and an independent
checker tests every structured claim the agent makes.

## Use case, and what connects to what

A fraud analyst is handed fan-in alerts: many distinct senders paying one
account inside an hour. Alerts that fire on the same rule can mean very
different things, and the analyst needs every statement traceable to the
transfers behind it.

clink, a stream engine, reads synthetic transfers in the order they arrive and
derives, by event time, fan-in indicators and onward links (a debit from an
account within 30 minutes after a credit to it). Three SQL jobs write the
transfers, accounts, devices, indicators and onward links into one Relate file
through clink's Relate connector. What connects to what: accounts send and
receive transfers; transfers come from devices; an indicator is about an
account and is made up of its contributing transfers; one transfer links to a
later one as a candidate onward transfer.

The relationships change the investigation. In the 55-transfer case, both
alerts have six senders and an onward link within 30 minutes. From one, the
candidate paths run three onward links and end at a fourth account, with one
device used to send from three accounts along them. From the other, they run
one link, and no device is shared. An onward link records timing, not that the
same funds moved; a shared device is context, not proof of ownership or fraud.

An agent (Claude Opus 5.5) queries the store read-only and writes a case note
with findings, hypotheses and unresolved questions kept apart. Every finding
cites structured claims, and a deterministic checker tests each claim against
both the graph and the original event file, with no model involved. It
rejects planted claims, including the answers arrival-order processing would
have given.

## How it uses Relate

- **Mode:** single file (`store/case.rl`), because the whole case ships in the
  repository as one file a judge can reopen and inspect with nothing running.
- **Capabilities used:** embedded writes from clink through Relate's C library
  (Cypher MERGE under uniqueness constraints, one transaction per batch);
  transactions shared by three concurrent writers, with conflicts refused at
  commit and retried; read-only reopening through `relate-db`; variable-length
  Cypher path queries.
- **Not used:** the `relate` command line, MCP, WebAssembly, Bolt, HTTP and
  vector search.

## A fair comparison, reported as it came out

The same agent investigated the same records as SQLite tables. On the
55-transfer case both arms were fully correct and the table arm used fewer
queries; neither traversed in the database, because the whole case fits in
context. At 50,000 transfers, which no agent can read whole:
both arms traversed in the database
in every run, a variable-length Cypher pattern in one and a recursive SQL query
in the other. Every completed run in both arms was fully correct, and the table
arm again needed fewer queries and tokens. One table run failed only because
its case note departed from the schema. The graph made no measurable
difference to the agent's correctness. What Relate contributes is the
persistent, connected evidence: native writes from clink, one file that
reopens anywhere, and path queries that the verifier, the explorer and either
agent can run against it.

## Try it

```bash
python3 -m venv .venv && .venv/bin/pip install --require-hashes -r requirements.txt
.venv/bin/python verify.py      # no model and no API key
.venv/bin/python explore.py
```

## Built with

clink (the runtime image, pinned by digest), Relate by Neo4j (`relate-db` 1.0.1
and its C library 1.0.1), Python, SQLite, Docker, the Anthropic Python SDK,
Claude Opus 5.5 through Amazon Bedrock.

## Third-party tools, AI tools and reused work

- Third-party: Relate (`relate-db` and its C library), Docker, the Anthropic
  Python SDK and Claude Opus 5.5 for the agent, Amazon Bedrock for the
  recorded runs.
- AI tools: Claude Code, with Claude Opus 5.5, wrote much of the code and
  documentation, under the author's direction and review.
- Reused work: clink is the author's own stream engine, started before the
  contest (June 2026) and not in this repository. Its Relate connector was
  written during the contest period, on 13 November 2026. This repository was
  started on 13 November 2026, from a spike written on 12 and 13 November.

## Links

- Repository: to add once published, with the GitHub topics `relate` (required)
  and `relate-neo4j-hackathon` (recommended).
- Demo video: to add once recorded. `DEMO.md` is its script.
