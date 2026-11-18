# streaming-alert-case

An evidence-backed investigation of a streaming fraud alert. clink derives
event-time indicators from out-of-order transfers and writes them, linked to
the transfers behind them, into one Relate file. An agent investigates through
Relate, and a deterministic checker tests every structured claim it makes
against the graph and against the original events.

## Two alerts that look alike

A fraud analyst is handed two fan-in alerts from a bounded replay of 55
synthetic transfers. Each fires on the same rule: six distinct senders paid one
account inside an hour, and a debit followed within 30 minutes. The analyst
needs to know which deserves attention, and to trace every statement back to
the transfers behind it. `explore.py` reads this from the store:

```text
                                 A-9278               A-9895               from
  distinct senders in one hour   6                    6                    fan-in indicator
  transfers in the window        6                    6                    fan-in indicator
  total received                 3,570.00             150.00               fan-in indicator
  onward link within 30 minutes  yes                  yes                  onward-transfer indicator
  onward links, at most          3                    1                    relationships, read from Relate
  candidate paths end at         A-4989               A-1415               relationships, read from Relate
  accounts on the paths          4                    2                    relationships, read from Relate
  device shared on the paths     D-568 (3 accounts)   none                 relationships, read from Relate
```

The alert rows differ only in their totals. The recorded relationships are
what change the investigation:

- **How far the candidate paths run.** From A-9278, candidate onward-transfer
  paths run three onward links, through A-5092 and A-2897, and end at A-4989.
  From A-9895 they run one link and end at A-1415.
- **A device along the way.** D-568 sent transfers from A-9278, A-5092 and
  A-2897, all on the first alert's paths. No device is shared on the second's.

An onward link records timing only: a debit from an account within 30 minutes
after a credit to it, by event time. It is a candidate onward-transfer
relationship, not evidence that the same funds moved. A path ends where no
further qualifying transfer exists in this dataset, which is not a real-world
resting point. A shared device is context, not proof of ownership or fraud.
Every conclusion here is about this bounded replay only.

## The case note, and a claim the checker rejects

An agent queried the store and wrote a case note: findings, hypotheses and
unresolved questions kept apart, every finding citing structured claims, and
the checker's verdict beside each claim. The recorded note is
[`runs/recorded/small-case-note-r4/case_note.md`](runs/recorded/small-case-note-r4/case_note.md).

It is from prompt revision r4, made through Amazon Bedrock on 13 November
2026 with `investigate.py --provider bedrock --case small --record
small-case-note-r4`. The agent made 13 queries in 7 model requests, over 123
seconds, and submitted 8 findings, 3 hypotheses and 4 unresolved questions.
The checker supported all 54 of its claims. They cover all seven required
facts, and all 63 distinct ids it cites resolve. From the note, as recorded:

> **f4** Onward paths for A-9895: only T0038, T0039 and T0040 have an onward
> link, each to T0041 (A-9895→A-1415, 14,000). T0035, T0036 and T0037 have no
> onward link, so they start no path. [...] every path ends at A-1415 because
> T0041 has no onward link in this dataset.

> **h3** In arithmetic, T0007 (138,000) is close to the sum of
> T0002+T0003+T0006 (141,500) [...]. This could suggest aggregation at A-9278,
> but the dataset records only timing links, not the movement of funds.

> **u2** What happens at A-4989 and A-1415 after the paths end? The paths end
> only because no qualifying transfer exists in this bounded dataset; activity
> outside it is unknown.

The checker judges structured claims, not prose. It rejects a claim when the
original events and the graph do not both bear it out.
`claims/planted.json` holds four claims that must be rejected. Two are what
processing in arrival order would have concluded:

```text
PASS  planted P2 rejected        unsupported: events: senders is 6, not 5; transfers is 6, not 5; total_minor is 357000, not 281000; contributing transfers differ: not contributing [], missing ['T0012']; ...
PASS  planted P3 rejected        unsupported: events: T0007 has an onward link: ['onward:T0007:T0008']; graph: T0007 has an onward link: ['onward:T0007:T0008']
```

## Why it takes both clink and Relate

clink keeps the evidence right when events arrive out of order. It processes
the transfers by event time, with five minutes allowed for lateness. Taken in
arrival order instead, this dataset gives two wrong answers:

- T0012 arrives after an event from the next hour. A window with no allowance
  for late events has closed by then, and the alert reads five senders and
  2,810.00 instead of six and 3,570.00.
- T0008, a debit, arrives before T0007, the credit it follows. A lookup made
  as events arrive misses the onward link `onward:T0007:T0008`, and ends a
  path at A-5092 too early.

`verify.py` checks both, and the planted claims P2 and P3 state them.

Relate holds the recorded relationships and answers questions over them in
Cypher: how many onward links the candidate paths run to, where they end, and
which accounts along them sent from the same device. It keeps them in one file
that clink writes and anyone can reopen. The comparisons below give the same
agent the same records as tables; read them for what the graph did and did not
change.

## How it uses Relate

- **Mode:** single file. `store/case.rl` (81,920 bytes) for the case, and
  `store/large.rl` (33.5 MB, shipped gzipped) for the same pipeline at scale.
- **Why this mode:** the whole case is one file that ships in this repository.
  You can open, copy and inspect it with nothing else running. Three clink
  jobs write it at once through one in-process handle. The verifier, the
  explorer and the agent each reopen it read-only, in another process.
- **What the graph models:** accounts, transfers, devices, the indicators clink
  derived, and the run that wrote it.

```mermaid
flowchart LR
    A["Account"] -- "SENT" --> T["Transfer"]
    T -- "TO" --> A
    T -- "FROM_DEVICE" --> D["Device"]
    I["Indicator (fan_in)"] -- "ABOUT" --> A
    I -- "CONTRIBUTING" --> T
    T -- "PASSED_ON (onward link, derived by clink)" --> T
    R["Run (bounded replay, dataset hash, job status, versions)"]
```

`PASSED_ON` is the pipeline's name for an onward link. Like the link itself,
it records timing, not that funds moved.

Relate capabilities used:

- **Embedded writes from clink:** clink's `connector='relate'` links Relate's C
  library. Each of the three SQL jobs in `pipeline/case.sql` writes its rows
  with a Cypher statement that MERGEs by stable ids under uniqueness
  constraints, one transaction per batch.
- **Transactions shared by concurrent writers:** the three jobs write some of
  the same nodes at once. Relate refuses the later conflicting transaction at
  commit, and the sink rolls back and retries it.
- **Read-only reopening from Python:** `relate-db` 1.0.1 opens the published
  store read-only for the verifier, the explorer and the agent's query tool.
  Writes are refused there.
- **Variable-length traversal:** the candidate paths, where they end and the
  devices shared along them come from Cypher path queries
  (`alertcase/graph.py`).
- **Claim dependencies, optional:** in the evolving investigation, each
  revision's store also holds the claims, the windows each depends on and
  every verdict so far, and one Cypher pattern finds the claims a new transfer
  bears on. See "Evidence-driven revision of investigative findings".
- **Relate's own MCP server, optional:** `relate serve --mcp stdio
  --read-only` serves the same file to any MCP host, so you can question the
  case from your own agent. The investigator can use it as its query backend
  too. See "Open the case in your own agent".

Not used: MCP over HTTP, WebAssembly, Bolt, the HTTP Query API and vector
search.

## Setup and run

Needs Python 3.11 or later. Rebuilding a store also needs Docker, and a live
agent run needs model credentials. Nothing else needs them.

```bash
git clone https://github.com/orhaugh/streaming-alert-case.git && cd streaming-alert-case
python3 -m venv .venv
.venv/bin/pip install --require-hashes -r requirements.txt

.venv/bin/python verify.py          # both datasets, the checker, every recorded run and revision/; no model, no API key
.venv/bin/python explore.py         # the investigation, read from the store
.venv/bin/python -m unittest        # the checker and the agent harness
```

Explore the store yourself, read-only:

```bash
.venv/bin/python explore.py --cypher "MATCH p = (:Transfer {id: 'T0002'})-[:PASSED_ON*]->(t:Transfer) WHERE NOT (t)-[:PASSED_ON]->() RETURN [n IN nodes(p) | n.id] AS path"
.venv/bin/python explore.py --sql "SELECT * FROM fan_in_alerts"
.venv/bin/python explore.py --case large    # the same investigation at 50,000 transfers
```

Rebuild a store from its event file. clink runs the three jobs from the
runtime image, pinned by digest; the store is published only if every job
succeeded, and then verified:

```bash
./rebuild.sh            # the case: 55 transfers
./rebuild.sh large      # 50,000 transfers
```

Optional, with Docker: a finding revised when new evidence arrives, with no
model (see "Evidence-driven revision of investigative findings"):

```bash
.venv/bin/python revise.py
```

Optional, with Claude API credentials (`ANTHROPIC_API_KEY`, or an `ant auth
login` profile):

```bash
.venv/bin/python investigate.py                          # one live agent run, written to runs/live/
.venv/bin/python compare.py --case large --runs 3        # the table and graph comparison, live
```

Or through Amazon Bedrock, with AWS credentials for an account that can use
Claude Opus 5.5:

```bash
.venv/bin/pip install --require-hashes -r requirements-bedrock.txt   # adds boto3 and botocore
export AWS_PROFILE=<your profile> AWS_REGION=<your region>
.venv/bin/python investigate.py --provider bedrock --smoke   # one request: does Bedrock accept it?
.venv/bin/python investigate.py --provider bedrock
.venv/bin/python compare.py --provider bedrock --case large --runs 3
```

On Bedrock the model is `global.anthropic.claude-opus-5-5`, the global
cross-region inference profile, which can serve a request from another region.
In some regions, ap-south-1 among them, Claude Opus 5.5 is offered only through
an inference profile. Set `BEDROCK_MODEL_ID=anthropic.claude-opus-5-5` where
the model runs in your region itself.

## Open the case in your own agent (MCP, optional)

Relate's own MCP server can serve either store to an MCP host, so you can ask
your own agent why the two alerts deserve different follow-up and inspect the
paths yourself. The server lists two tools, `read_cypher` and `get_schema`,
and every write fails. Install the `relate` command line it runs from (1.0.1,
checked against a pinned sha256), then check it:

```bash
./scripts/fetch-relate-cli.sh                                        # relate 1.0.1, at .relate/bin/relate
.venv/bin/pip install --require-hashes -r requirements-mcp.txt       # the MCP Python SDK, for the check
.venv/bin/python mcp_check.py                                        # no model, no API key
```

- **Claude Code:** run `claude` in the checkout. It reads `.mcp.json` and asks
  you to approve three servers, `streaming-alert-case` (55 transfers),
  `streaming-alert-case-large` (50,000) and `streaming-alert-case-revision`
  (the published revision of the evolving investigation).
- **Claude Desktop, Cursor and other hosts:** `sh scripts/serve-mcp.sh
  --config` prints the configuration block with this checkout's absolute
  paths.

`scripts/serve-mcp.sh` is what each configuration starts. It accepts only
relate 1.0.1, unpacks the large store on first use and whenever the shipped
copy changes, and serves a store only if
its Run record shows a completed replay. It then runs `relate serve --mcp stdio
--database <store> --read-only`, with Relate's anonymous usage metrics turned
off.

Three prompts to start with:

1. "Two fan-in alerts in this store fire on the same rule. Using only the
   relate tools, find the recorded relationships that distinguish them, and
   cite the transfer, account, device and indicator ids behind each statement.
   An onward link records timing only, not that funds moved."
2. "For each alert, list the candidate onward-transfer paths that start at its
   contributing transfers, the accounts along them, and where each path ends
   with no further qualifying transfer in this dataset. Show the Cypher you
   ran."
3. "Which devices sent transfers from more than one account on an alert's
   paths? Name the accounts and transfers, and say what this does and does not
   establish."

On the large store, ask the same questions of its six alerts: at 50,000
transfers the agent has to query the data, not read it.

`mcp_check.py` starts the server as `.mcp.json` does and talks to it through
the MCP Python SDK. For each dataset it checks the handshake, that only the
two read-only tools are listed, and the schema's counts. It reads the evidence
over MCP and requires it to equal the reference's, record for record. It runs
the agent's worked path query for every alert and requires exactly the
reference's paths. It checks that a CREATE, MERGE, SET, DELETE, schema change
and `write_cypher` are each refused, that the server exits 0 when stdin closes,
and that the store is byte for byte unchanged. On the revision store it checks
that the claims a new transfer selects, and the amendment, read over MCP,
equal the ledger's.

What it does not check is your agent's answer. An investigation in your own
host is not a checked case note: only the case notes `investigate.py`
records go through the claim checker. The server gives an agent the evidence,
not the checker, and not this repository's ground rules.

## Where the data lives

| Path | What |
|---|---|
| `store/case.rl` | The Relate store: one file, written by clink, published by `scripts/publish_run.py` |
| `data/events.ndjson` | The 55 transfers in arrival order: what clink reads |
| `data/scenario.json` | The designed facts, read by the verifier only |
| `tables/case.sqlite` | The same records as tables, for the comparison only |
| `data/large/` | The large case: 50,000 transfers and its designed facts |
| `store/large.rl.gz`, `tables/large.sqlite.gz` | The large case's store and tables, gzipped; unpacked byte for byte on first use, and again whenever the shipped copy changes |
| `claims/planted.json`, `claims/planted-large.json` | Deliberately unsupported claims the checker must reject |
| `runs/recorded/` | Recorded agent runs: transcript, submitted case note, verdicts, score, rendered `case_note.md` |
| `runs/superseded/` | Runs recorded with an earlier prompt revision, kept and still verified |
| `runs/shakedown/` | Live runs that checked the harness before recording; part of no result, still verified |
| `.mcp.json`, `scripts/serve-mcp.sh` | The MCP host configuration, and the launcher it starts: Relate's MCP server, read-only |
| `pipeline/revision.sql`, `data/arrival.ndjson` | The evolving investigation's recomputation, and the transfer that arrives |
| `revision/` | The evolving investigation as published: the ledger, each revision's store, the arrival as applied, the case note and the amendment |

## The pipeline

`pipeline/case.sql` declares the event file as a table with event time and a
five-minute watermark lag, and runs three jobs into the same store:

1. every transfer, with its sender, receiver and device;
2. fan-in: at least five distinct senders into one account inside a one-hour
   event-time window, written as an Indicator linked to each contributing
   transfer;
3. onward link: an event-time interval join of a credit to an account with a
   debit from that account up to 30 minutes later, written as a `PASSED_ON`
   relationship between the two transfers.

`rebuild.sh` publishes a store only when clink exited 0 without being
cancelled. clink's embedded runner returns 0 only when every job reached
completion and none reported an error. `scripts/publish_run.py` then checks
that the store's transfers equal the file, record for record. Only after that
does it write the Run record, with the dataset's hash, the pipeline's hash, the
jobs completed, the image and the versions. The conclusions are relative to
that run and that file. The replay is bounded, and nothing here claims a
completeness frontier for a live stream.

## The checker

The agent submits its case note as the input of a tool, `submit_case_note`,
whose input schema is the case note: findings, hypotheses and unresolved
questions kept apart, and claims grouped by type. Every finding cites claim
ids. Every claim is one of seven types, states every value of its type, and is
judged by one rule (`alertcase/claims.py`):

| Type | Asserts |
|---|---|
| `event` | a transfer exists with the stated sender, receiver, amount, time and device |
| `indicator` | a fan-in indicator has the stated values and exactly the stated contributing transfers |
| `onward_path` | each step is a recorded onward link; the path starts at an alert and ends where stated, with no further onward link |
| `onward_reach` | an alert's candidate paths: the most onward links in one, the accounts where they end, and the accounts along them |
| `shared_device` | a device sent from exactly the stated accounts on an alert's paths |
| `absence` | no shared device on an alert's paths, no onward link from a transfer, no alert for an account |
| `count` | the number of alerts, transfers, onward links, accounts or devices |

The checker applies each rule twice: to the facts derived from the original
event file by independent reference rules (`alertcase/reference.py`), and to
the facts read from the graph. A claim is supported only when both agree. It
is unsupported when neither does, and inconsistent when the two disagree,
which happens with a damaged store or a changed file. The checker needs no
model. It validates references and structured values; it does not validate
prose. Reference validity, reported beside it, only says whether a cited id
exists. A finding is only as good as the claims it cites.

## Agent runs and prompt revisions

The agent is Claude Opus 5.5 at effort `high`, with one read-only query tool
and the tool it submits the case note with, through the Anthropic SDK's
tool-use loop (`alertcase/agent.py`). Its budgets: 20 queries, 30 model
requests, 16,000 tokens per response (32,000 for the large case), at most 200
rows and 30,000 characters per query result, and 30 seconds per query; a
result over a limit says it was truncated. Every recorded run so far went
through Amazon Bedrock (the global inference profile, from ap-south-1). A
recorded run keeps the provider and the region, never the account.

The graph arm reaches the store through the Python library, unless
`investigate.py --backend mcp` sends its queries to Relate's MCP server, through
`scripts/serve-mcp.sh` and the MCP Python SDK. The model gets the same tools,
prompt and limits either way. The server has no per-call timeout and no row
cap, so the client applies both. It stops the server and starts it again when a
query passes its 30 seconds, and it counts every row before keeping 200. A run
records which backend it used, and for MCP the transport, server, protocol and
client versions.

Runs recorded from 14 November also time each model request: its seconds, its
outcome, and the retries the SDK took to answer it (`request_timings` in
`meta.json`; no headers or request ids). Earlier recordings, the MCP one
included, predate this and are kept as they were. Each attempt at a request is
allowed 1,800 seconds and the SDK retries twice, so one stalled request can
hold a run for an hour or more. For a live demonstration, bound it:

```bash
.venv/bin/python investigate.py --provider bedrock --request-timeout 300 --max-retries 1
```

Each run is labelled with the prompt revision that made it. The checker's
rules have not changed across revisions; the agent's wording and guidance have.

| Revision | Commit | What changed | Runs |
|---|---|---|---|
| r1 | b5f9799 | the case note submitted through a tool | `runs/shakedown/small-graph-r1` |
| r2 | d9a9d16 | path accounts defined exactly | `runs/superseded/small-*-r2` |
| r3 | 27f96d0 | path end accounts defined exactly | `runs/recorded/small-*-r3`, `runs/shakedown/large-*-r3` |
| r4 | 9caefc0 | onward links described as timing; both arms given equivalent traversal guidance | `runs/recorded/small-case-note-r4`, `runs/recorded/large-comparison-r4`, and through MCP `runs/recorded/large-case-note-r4-mcp` |

The r1 shakedown counted an alert's senders among its path accounts, a fair
reading of wording that did not say whether senders count. In the r2 set, five
of six comparison runs listed an alerted account among its path ends because
some of its contributing transfers had no onward link. Each time the wording
was made exact to match what the checker had always computed, and both arms
were given the same words. r3 and earlier runs keep their transcripts as
recorded, including wording such as "comes to rest" that r4 replaced.

`verify.py` checks every claim of every recorded, superseded and shakedown run
again, and fails if a verdict or a recorded score differs.

### One investigation through Relate's MCP server (r4)

One investigation of the large case sent its queries to Relate's MCP server
instead of the library. It ran on 14 November 2026 with `investigate.py
--provider bedrock --case large --backend mcp --record
large-case-note-r4-mcp`, and is in
[`runs/recorded/large-case-note-r4-mcp/`](runs/recorded/large-case-note-r4-mcp/case_note.md).
Its `meta.json` records the transport (stdio), the launcher, the server
(`relate-mcp 1.0.1`), the protocol (2025-11-25) and the client (`mcp 2.3.0`).
Its prompt is r4's, byte for byte: its hashes equal those of the r4
comparison's graph runs.

- **Checked:** completed, correctness 1.00. All 74 claims are supported and
  cover all 19 required facts, and all 112 cited ids resolve. The note has 13
  findings, 4 hypotheses and 4 unresolved questions.
- **How it queried:** 16 queries in 8 model requests. Two were path queries,
  each a variable-length pattern over every alert at once. No result was
  truncated, no query was stopped, and the server started once.
- **One query refused, where the library would have run it:** a read built
  from `CALL { }` subqueries. Relate's MCP server 1.0.1 answers even a single
  `CALL { MATCH ... RETURN count(*) }` read with "Only MATCH queries are allowed
  for read-query". The library runs the same statement. The agent counted with
  four separate queries instead.
- **Slow, for a reason not recorded:** 118,239 input tokens, cache included,
  and 15,092 output tokens, about the model work of the r4 graph runs. Its wall
  time was 1,990 seconds, against at most 183 for every earlier recorded run.
  The 16 queries took 0.28 seconds in all, so the rest was spent waiting on
  the model. The extra is close to the 1,800-second request timeout, which
  fits one request that stalled and was retried by the SDK. The harness did
  not yet time each request, so that is not established.

It is one run, kept apart from the comparison below. It shows the MCP backend
working end to end, not that the transport leaves results unchanged.

## Comparison: table-based or Relate-based investigation

`compare.py` runs the same agent on the same evidence two ways, alternating
arms. The graph arm queries the Relate store in Cypher. The table arm queries
the same records as SQLite tables, exported from the store, in SQL. Everything
else is the same: model, effort, budgets, the system prompt apart from the
paragraph describing the evidence, the task, the tools, and the checker.

Each run is scored the same way (`alertcase/scoring.py`): **correctness**, the
share of the required facts covered by supported claims (seven in the case, 19
at scale, derived from the events); **unsupported claims**; **reference
validity**, the share of cited ids that exist; and **effort**: queries,
truncated results, stopped queries, model requests, tokens and seconds. The
summary also counts each run's **path queries** (a variable-length pattern or a
recursive query) and **multi-hop queries** (two or more onward links written
out), to show whether the agent traversed in the database.

### The case, 55 transfers (r3)

Three runs per arm, `runs/recorded/small-comparison-r3/`.

| | Graph arm: Relate, Cypher | Table arm: SQLite, SQL |
|---|---|---|
| Correctness, each run | 1.00, 1.00, 1.00 | 1.00, 1.00, 1.00 |
| Claims not supported, each run | 0, 0, 0 | 0, 0, 0 |
| Reference validity, each run | 1.0, 0.984, 1.0 | 1.0, 1.0, 1.0 |
| Queries, mean | 9.7 | 5.3 |
| Path queries | 0 in every run | 0 in every run |
| Input tokens, mean, cache included | 38,357 | 23,044 |
| Output tokens, mean | 8,432 | 5,991 |
| Seconds, mean | 99 | 71 |

No difference in correctness, and the table arm used fewer queries and tokens.
Neither arm traversed in the database: the graph agent asked for single onward
links and joined them itself, and the table agent selected two whole tables in
each run. At 55 transfers the whole case fits in the model's context. One id
cited in prose did not resolve: an unresolved question in graph run 2 names
device D-585 and corrects itself to D-785 in the same sentence.

### At scale, 50,000 transfers (r4)

Three runs per arm, arms alternating, recorded on 13 November 2026 with
`compare.py --provider bedrock --case large --runs 3 --record
large-comparison-r4`, in `runs/recorded/large-comparison-r4/`. Every response
came from `claude-opus-5-5`, and no run was served by a fallback. No result was
truncated and no query was stopped at the time limit.

| | Graph arm: Relate, Cypher | Table arm: SQLite, SQL |
|---|---|---|
| Runs completed | 3 of 3 | 2 of 3 |
| Correctness, each run | 1.00, 1.00, 1.00 | 1.00, 1.00, 0.00 |
| Claims made, each run | 76, 75, 81 | 63, 87, none kept |
| Claims not supported | 0 in every run | 0 in every completed run |
| Reference validity | 1.0 in every run | 1.0 in every completed run |
| Path queries, each run | 1, 4, 2 | 1, 1, 1 |
| Queries, mean (none failed) | 12.7 | 9 |
| Model requests, mean | 9 | 6 |
| Input tokens, mean, cache included | 123,025 | 91,338 |
| Output tokens, mean | 14,184 | 12,315 |
| Seconds, mean | 172 | 144 |

What it shows, and what it does not:

- **Both arms traversed in the database, in every run.** Each wrote at least
  one path query over every alert at once, adapted from the worked example it
  was given. Graph run 1's:

  ```cypher
  MATCH (i:Indicator)-[:CONTRIBUTING]->(c:Transfer)
  MATCH p = (c)-[:PASSED_ON*1..12]->(t:Transfer)
  WHERE NOT (t)-[:PASSED_ON]->()
  MATCH (t)-[:TO]->(e:Account)
  WITH i, [n IN tail(nodes(p)) | n.id] AS onward, length(p) AS links, e.id AS endacct
  RETURN i.id, onward, links, endacct, count(*) AS n_starts ORDER BY i.id, links DESC
  ```

  Table run 1's was a recursive common table expression over
  `alert_contributions` and `onward_links`, joined to `transfers`.
- **The graph did not make the agent more correct.** Every completed run, in
  both arms, covered all 19 required facts with every claim supported. The
  table arm again used fewer queries and fewer tokens.
- **One table run failed on format, not on evidence.** Table run 3 submitted a
  case note with an extra, empty field (`statement`) in one unresolved
  question. The harness keeps only a case note that matches its schema, a rule
  set before any run, so that run scores 0 and is kept as recorded. Checked
  separately, as a diagnostic and not a score: all 69 of its claims are
  supported, and they cover all 19 required facts.
- **Guidance was not what made them traverse.** Two live shakedown runs at r3,
  before the worked examples were added, traversed too: the graph run with two
  variable-length queries, the table run with one recursive query. Both were
  fully correct (`runs/shakedown/large-*-r3`).
- **The sample is small:** three runs per arm, one model, one synthetic
  dataset.

On these datasets the graph made no measurable difference to the agent's
correctness. What Relate contributes here is the persistent, connected
evidence itself: native writes from clink's jobs, one file that reopens
anywhere, and path queries that the verifier, the explorer and either agent
can run against it.

## The same pipeline at scale

`scripts/make_large_events.py` writes a seeded week of 50,000 transfers among
12,000 background accounts, capped so the background raises no alert, with
six designed alerts on accounts the background never touches:

```text
  account    label                              senders        total  depth  paths end at           shared on paths
  A-10859    designed as suspicious                   6     2,040.00      3  A-85287, A-92332       D-79802 (2)
  A-20636    designed as a benign lookalike           6       360.00      1  A-36729                none
  A-28137    designed as a benign lookalike           7       295.00      0  -                      none
  A-37573    designed as suspicious                   7     3,795.00      4  A-54215                D-45880 (4)
  A-83577    designed as suspicious                   8     1,745.00      5  A-39382                D-40018 (2)
  A-85921    designed as a benign lookalike           6       150.00      1  A-10758                none
```

Decoys: a six-link chain of onward links on one shared device, tied to no
alert; devices on a path that an account off the path also uses; an account
where a path ends that sends again hours later. Inversions: a credit at a
window's edge that arrives after the next hour's events, and a debit that
arrives before the credit it follows. Taken in arrival order, a lookup misses 8
of the 691 onward links, the designed one among them.

At 5.8 MB the event file is beyond what the agent can read through its query
tool and beyond a model's context: investigating it means querying it. clink
writes it into one Relate store in about six seconds. `verify.py` checks that
store against the reference, an answer key of 19 claims, and four planted
claims, all rejected; two are again the arrival-order answers.

## Evidence-driven revision of investigative findings (optional)

An optional demonstration beside the case, apart from its comparison and its
recorded runs. It is a staged evolving investigation: two bounded replays,
each an evidence revision, and a finding revised between them because new
evidence arrived. It is not continuous streaming.

```bash
.venv/bin/python revise.py     # needs Docker; no model, no API key; publishes into build/revision/
```

It prints what the investigation said, what arrived and what that changed,
and what it says now (abridged):

```text
BEFORE  r1: 55 transfers from data/events.ndjson. clink exited 0, 3 of 3 jobs; 55 of 55 records reconciled; derived
        evidence equals the independent reference.
  ...
  F4  its paths: at most 1 onward link, ending at A-1415; no qualifying onward transfer from A-1415 at
      14:50:00-15:20:00  [C6 C7: supported at r1]

CHANGE  data/arrival.ndjson: 1 new transfer
  T0056  A-1415 -> A-6630  130.00  15:01:00 UTC 10 November 2026  D-785
  ...
  New relationship, derived by clink: onward:T0041:T0056
  Selected by the dependency query in Relate, and by the same rule over the ledger:
    C6  T0056 is a debit from A-1415 inside 14:50:00-15:20:00, the 30 minutes after T0041
    C7  T0056 is a debit from A-1415 inside 14:50:00-15:20:00, C7's search scope
  Not selected: C1 C2 C3 C4 C5. Incremental revalidation equals a full recheck: 7 of 7 verdicts.

AFTER   r2 published, with amendment A1 (r1 -> r2).
  F4  superseded at r2. Its claims stay supported relative to r1; at r2:
      C6 unsupported: the longest chain is 2 onward link(s), not 1; terminal_accounts are ['A-6630'], not ...
      C7 unsupported: qualifying onward transfer(s) from A-1415: onward:T0041:T0056 (T0056 at 15:01:00)
  F5  its paths: at most 2 onward links, ending at A-6630; no qualifying onward transfer from A-6630 at
      15:01:00-15:31:00; path T0038 > T0041 > T0056  [C8 C9 C10 C11: supported at r2]
  Unchanged: F1, F2, F3. Not selected, so carried: C1 C2 C3 C4 C5. A full recheck agrees with each.
```

The record this repository ships is in `revision/`: the ledger, each
revision's store, revision 1's case note
([`revision/r1-case-note.md`](revision/r1-case-note.md)) and the amendment
([`revision/r2-amendment.md`](revision/r2-amendment.md)). `verify.py` checks
it with no Docker.

### Step by step

1. **Revision r1.** clink replays the 55 transfers through
   `pipeline/revision.sql`, with nothing arrived yet, into a Relate store. As
   for the case itself, the store is published only when clink exited 0,
   every record is in it as written, and its indicators and onward links equal
   the independent reference. `revise.py` then writes a case note from the
   evidence in Relate, with no model: four findings resting on seven claims,
   each checked against the events and the graph.
2. **The absence.** F4 says the candidate paths from A-9895's alert end at
   A-1415: in evidence revision r1 there is no qualifying onward transfer from
   A-1415 between 14:50:00 and 15:20:00 UTC on 10 November 2026, the 30 minutes
   after T0041 paid it.
3. **The arrival.** `data/arrival.ndjson` delivers a transfer that was not
   available before: T0056, A-1415 to A-6630, 130.00 at 15:01:00, inside that
   interval.
4. **Event time.** Revision 1's replay has completed, and its jobs' state
   with it, so nothing can be appended to it. By the pipeline's lateness rule,
   T0056 is also 2 h 59 min behind the watermark that replay reached, far
   beyond its five-minute allowance. So revision r2 is a bounded
   recomputation: clink replays revision 1's file and the arrival as two
   inputs, merged by event time, and judges T0056 by the same allowance as
   every other transfer. It derives `onward:T0041:T0056` and writes it through
   the Relate connector.
5. **Selection.** Each claim's dependencies are windows on accounts, held in
   Relate. One Cypher pattern finds the claims a new transfer falls into: C6,
   the alert's reach, and C7, the absence. The same rule run over the ledger
   must agree. Both are checked again; the other five carry their verdicts, and
   a full recheck of all seven must give the same verdicts.
6. **The amendment.** C6 and C7 no longer hold at r2, so amendment A1
   supersedes F4 with F5: the paths now run two onward links, through T0056,
   and end at A-6630, from which no qualifying onward transfer follows in r2.
   F5's four claims, the new transfer and a path through the new link among
   them, are supported at r2. F1, F2 and F3, about the alert's own indicator
   and about A-9278's alert, are unchanged.

### Who does what

- **clink** derives every indicator and onward link, in both revisions.
  `pipeline/revision.sql` runs the three jobs of `pipeline/case.sql`,
  statement for statement (a test holds them equal), over two inputs.
- **Relate** holds, in each revision's store, clink's evidence and, beside it,
  the investigation as of that revision: the revisions, each claim with what it
  cites and its dependency windows, every validation so far, the findings and
  the amendment. The selection is a query over it.
- **The checker** decides deterministically whether each claim holds for a
  revision, against that revision's graph and against the reference rules
  applied to its original events, as for the case note.
- **No model** runs in it. An agent could explain an amendment; none is used.

### Claims, and what they depend on

A claim has a stable id, a structured predicate, the evidence revision it was
asserted at, and a validation history that is only ever appended to. Five
claim types support revision:

| Type | Asserts | Depends on |
|---|---|---|
| `event` | a transfer exists with exactly these values | nothing: an existing transfer never changes |
| `indicator` | a fan-in indicator's values and contributing transfers | credits to its account inside its window |
| `onward_path` | each step is a recorded onward link, and none leaves the last transfer | debits from the account the last transfer paid, in the 30 minutes after it |
| `onward_reach` | an alert's candidate paths: how deep, where they end, the accounts along them | debits from each account a path transfer paid, in the 30 minutes after it, and credits to the alerted account in its window |
| `no_onward_transfer` | no qualifying onward transfer from an account, its debit inside an event-time interval | debits from the account inside the interval, and credits to it from 30 minutes before it |

An absence records its search scope, not a list of ids: the account, the
relationship pattern (an onward link into a debit the account sent), the
interval with both ends included, and the dataset it covered (the revision,
its digest and its number of transfers). C7 cites no transfer at all, and
T0056 did not exist when C7 was asserted: only its scope can show that T0056
bears on it.

Selection misses nothing because every onward link a new transfer creates has
that transfer at one end, inside a window of each claim the link can affect.
That holds while evidence is only added and a claim is asserted only when the
checker supports it at its revision, and `revise.py` keeps both. Selecting a
claim that turns out unchanged is allowed. `tests/test_revision.py` tries 400
seeded random arrivals aimed at the windows and their edges, one and two
revisions deep: no claim whose verdict changed went unselected, and the
incremental verdicts equalled a full recheck every time.

### Update semantics

- **What publishes a revision.** In order: clink exited 0 and was not
  cancelled; every record of the revision's dataset is in the store as
  written; its indicators, onward links and paths equal the reference; the
  dependency query in Relate selects exactly what the rule over the ledger
  selects; incremental revalidation equals the full recheck; every claim of a
  replacement finding is supported; and, with the investigation written beside
  the evidence, both are checked once more. Only then does the store move into
  place and the ledger gain its records, the publication last. The ledger's
  last publication names the published revision; no checkpoint id stands for
  one.
- **A failed update** publishes nothing. The ledger is untouched, and the
  previous revision stays the published one, whole and checkable.
- **Replays.** A transfer delivered again unchanged adds nothing; an arrival
  that adds nothing new causes no recomputation and no amendment. A different
  transfer under a known id is a correction, and is refused.
- **Historical meaning.** C7 was supported by revision 1 and stays supported
  relative to revision 1. Its r1 validation is never rewritten, and neither is
  revision 1's case note, whose sha256 the ledger keeps. What changed is its
  applicability: at r2 it does not hold, and the amendment says so.
- **The ledger**, `revision/ledger.jsonl`, holds one JSON record per line, each
  naming the sha256 of the line before, so a rewritten line breaks the chain.
  Each revision's store holds the investigation up to that revision, and
  `verify.py` checks that the two agree.

### Inspect it through Relate

```bash
.venv/bin/python explore.py --revision r2 --cypher "MATCH (:Revision {id: 'r2'})-[:ADDED]->(t:Transfer)<-[:SENT]-(a:Account)<-[s:SCOPE {revision: 'r1', role: 'debit'}]-(c:Claim) WHERE s.start_ms <= t.ts AND t.ts <= s.end_ms RETURN c.id AS claim, c.type AS type, t.id AS new_transfer, a.id AS account"
.venv/bin/python explore.py --revision r2 --cypher "MATCH (v:Validation)-[:OF]->(:Claim {id: 'C7'}) RETURN v.revision AS revision, v.status AS status, v.method AS method"
.venv/bin/python explore.py --revision r2 --cypher "MATCH (a:Amendment)-[r]->(x) RETURN type(r) AS link, labels(x)[0] AS kind, x.id AS id"
```

Relate's MCP server serves the published revision as well: `.mcp.json` lists a
third server, `streaming-alert-case-revision`, and `mcp_check.py` checks that
the dependency query and the amendment, read over MCP, equal the ledger.

### What ran

On 18 November 2026, on macOS 26.3.1 arm64 with Docker Desktop (engine
29.8.2) and clink's runtime image `0.16.2`, pinned by digest as in
`rebuild.sh`:

- `revise.py --out revision` wrote the shipped record, with the output above.
- Twelve recomputations of r2, each with a fresh clink run, all derived
  `onward:T0041:T0056` and published. With the arrival appended after revision
  1's transfers in one input instead, as a continuing stream would read it,
  clink paired T0056 with T0041 in 7 runs of 12 and not in the other 5, and
  the gates refused all 5. A transfer that late has no guarantee: whether
  clink's self-join still holds T0041 when T0056 reaches it depends on how far
  the join's other read has got. This is why each revision is a recomputation.
- With clink, other arrivals: an unrelated transfer, and one from A-1415 at
  15:35:00, after the interval, each published r2 with no claim selected and
  no amendment; one at 15:20:00, the interval's last millisecond, superseded F4
  as above; the same arrival twice added nothing the second time.
- `verify.py` passed 67 of 67 checks, 9 of them on `revision/`; `mcp_check.py`
  passed 24 of 24, 4 of them on the revision store; and 57 tests passed, 22 of
  them new, the ones that run clink in Docker included.

### Limits

- A staged scenario: two bounded replays, one arrival between them. Not
  continuous streaming, and no live watermark frontier: the lateness check is
  arithmetic over the replay's own last transfer and the pipeline's allowance.
- Every revision recomputes the whole dataset, which is cheap at 56
  transfers. Only the revalidation of claims is incremental.
- Evidence is only added. Corrections, deletions and retractions are refused,
  not handled.
- Five claim types. Shared-device and count claims, and the claims the agent
  writes, are not supported for revision, and the staged case note does not
  use them.
- New alerts that an arrival creates are recorded in the revision, not
  investigated: no finding is written for them.
- The findings' and the amendment's wording comes from templates in
  `alertcase/revision.py`. The checker validates the structured claims, not
  the prose. No agent wrote or explained an amendment.
- One synthetic scenario, run only in Docker on macOS arm64.
- Rebuilt stores are not byte-identical; the ledger records the hash of the
  store each revision published.

## What ran

On macOS 26.3.1, arm64, on 13 November 2026, and on 14, 17 and 18 November
where stated:

- `./rebuild.sh` built `store/case.rl`, and `./rebuild.sh large` built
  `store/large.rl`, from `ghcr.io/orhaugh/clink-runtime:sha-c134524d8674`,
  index digest
  `sha256:f19c890c747e8a6e097568e0003cd83c303599a4bfbb0095751045909124802f`,
  a build of clink's main branch at commit c134524d.
  They ran as linux/arm64, with Docker Desktop (engine 29.8.2) and no network.
  clink exited 0 both times: 55 of 55 and 50,000 of 50,000 records reconciled.
  For the large case clink took about six seconds and publishing 28. The
  recorded agent runs read stores built from this image, so their transcripts
  name it.
- On 17 November both stores were rebuilt the same way from clink's release
  v0.16.1, `ghcr.io/orhaugh/clink-runtime:0.16.1`, index digest
  `sha256:d688ef7ddf6694532076bce7d12eb85a6d80ca4218385e44dfc3315657b52bf4`.
  clink exited 0 both times, and 55 of 55 and 50,000 of 50,000 records
  reconciled. Every table exported from them equals the one exported from the
  earlier stores, row for row, except that the Run record names the new image.
  `verify.py` passed 58 of 58 against them, every recorded run included, and
  `python -m unittest` passed 29 of 29.
- Also on 17 November, checked separately: the image tag `0.16.1` resolves to
  that digest, and both its platform images carry the revision label of
  v0.16.1's commit, 9da1f7c7. Read from both sets of stores, every fact the
  checker uses is the same, and the Run record differs only in the image it
  names. A scratch clone rebuilt both stores from the pinned image again:
  clink exited 0, all records reconciled, and each case verified. A clone
  made before the rebuild and then updated with `git pull` kept its old
  unpacked large store and checked that. The large case's copies are now
  unpacked again whenever the shipped copy changes. With that, `verify.py`
  passed 58 of 58, `mcp_check.py` 20 of 20, and 35 tests passed.
- On 18 November both stores were rebuilt again, from clink's release v0.16.2,
  `ghcr.io/orhaugh/clink-runtime:0.16.2`, index digest
  `sha256:da007cf3f288497a05447ae6d9d65914d0a31471b929cc38af02e297971b1fd8`,
  which `rebuild.sh` now pins. These are the stores the repository ships.
  v0.16.2 fixes a failure this repository's rebuild ran into: a sink applying
  its schema statements while another sink on the same store committed could
  meet a write conflict, and its job then failed, so `rebuild.sh` stopped with
  clink's exit status 1. Run a hundred times, four at a time, the small case's
  pipeline failed twice on v0.16.1 and never on v0.16.2. clink exited 0 for
  both stores, 55 of 55 and 50,000 of 50,000 records reconciled, and every
  exported table equals the previous one row for row, except that the Run
  record names the new image. `verify.py` passed 58 of 58, `mcp_check.py` 20
  of 20, and 35 tests passed.
- `investigate.py --provider bedrock --smoke`, for each case: one request
  through Bedrock from ap-south-1, accepted and answered by `claude-opus-5-5`.
- The recorded, superseded and shakedown runs listed under "Agent runs and
  prompt revisions", all through Bedrock. The one through MCP ran on 14
  November.
- On 14 November, for MCP: `scripts/fetch-relate-cli.sh` installed relate
  1.0.1 (`relate-darwin-arm64`). Its sha256 matches the release's
  `SHA256SUMS`, whose SSH signature verified against the key in Relate's
  `install.sh`, the same key relatedb.ai publishes. `mcp_check.py` passed 20
  of 20 checks on both datasets in about six seconds. In the checkout, Claude
  Code 2.1.325 listed the two `.mcp.json` servers as pending approval. From a
  throwaway configuration with the commands `scripts/serve-mcp.sh --config`
  prints, it reported both connected.
- `verify.py` on 14 November: 58 of 58 checks passed. For each dataset: 9 on
  the store, 5 on the checker (its answer key and four planted claims) and 1
  on the tables. Then every recorded, superseded and shakedown run, and each
  comparison's summary.
- `python -m unittest` on 14 November: 29 tests passed. Seven of them test
  the MCP backend and how it follows its server processes, and they are
  skipped without the relate command line or the MCP client.
- Python 3.12.3, `relate-db` 1.0.1, `anthropic` 2.8.0, boto3 and botocore
  1.44.2 and `mcp` 2.3.0, installed with `--require-hashes` from
  `requirements-bedrock.txt` and `requirements-mcp.txt`.
- A fresh clone on 13 November, set up exactly as in "Setup and run", with
  Python 3.11.9 and `requirements.txt` only. The large store and tables
  unpacked from their gzipped copies on first use. `./rebuild.sh` and
  `./rebuild.sh large` exited 0, and each verified its dataset again, recorded
  runs included, against the rebuilt store.
- A fresh clone of commit d94cd00 on 14 November, with Python 3.11.9. With
  `requirements.txt` only, `verify.py` passed 58 of 58 in about ten seconds,
  `explore.py --case large` ran, and `mcp_check.py` stopped, naming the
  command that installs the MCP client. Then `scripts/fetch-relate-cli.sh`
  downloaded relate 1.0.1 and installed it against its pin. With
  `requirements-mcp.txt` added, `mcp_check.py` passed 20 of 20. Neither left
  an untracked file.
- A fresh clone of commit bd672a2 on 14 November, with Python 3.11.9. With
  `requirements.txt` only, `verify.py` passed 58 of 58, and the tests passed
  with the seven MCP tests skipped. With the MCP extras, the relate binary
  copied from the download above and checked against its pin,
  `mcp_check.py` passed 20 of 20 and all 29 tests passed.
  `./scripts/demo.sh --rehearse` ran all five sections with Docker. Once
  warm, their commands took 6.3 seconds in all, the replay 3.1 of them, so
  the video's length is set by its narration.

The same pipeline, from the same image, was also run on scratch copies of the
case during the spike this repository grew from: five fresh runs on
linux/arm64 and five on linux/amd64, under emulation on the same Mac. Each
passed the spike's nine store checks.

## Not done, and not verified

- **The evolving investigation** has limits of its own, listed with it under
  "Evidence-driven revision of investigative findings".
- **Model and dataset variety:** the comparisons use one model, two synthetic
  datasets and three runs per arm. They are observations, not statistically
  tested differences.
- **The Claude API path:** the recorded runs went through Amazon Bedrock. The
  Claude API path is tested only with a scripted stand-in client.
- **Where MCP was tried:** Relate's MCP server ran over stdio on macOS arm64
  only. Claude Code was checked connecting to it with `claude mcp list`, from
  a throwaway configuration. Claude Desktop, Cursor and the other hosts were
  not tried, and MCP over HTTP was not used. `scripts/serve-mcp.sh` needs a
  POSIX shell, so on Windows it runs only under WSL.
- **The MCP backend ran once:** one recorded investigation, which is not a
  comparison with the library backend. It shows that the backend works end to
  end, not that the transport leaves results unchanged.
- **Request timing, live:** it is tested against the SDK's own clients for
  both providers, with their HTTP transport replaced, but no live request has
  gone through it: when it was added the AWS session had expired, and no paid
  run was made to try it.
- The pipeline has run only in Docker on a Mac: never on a Linux host or an
  x86_64 machine.
- The recorded agent runs read stores built by a main-branch build of clink,
  before the connector was in a release, so their transcripts name that image.
  The shipped stores were rebuilt from v0.16.2 with the same content, and the
  runs were not recorded again.
- Rebuilt stores are not byte-identical to each other. Every check compares
  content.

## Reused work, tools and disclosures

- **clink** is the author's own stream engine, a project started before this
  contest (its git history begins in June 2026; its last release before the
  contest was v0.15.0, 3 November 2026). It is not in this repository. Its
  Relate connector, `connector='relate'`, was written during the contest
  period. It landed in clink's repository on 13 November 2026 in commits
  b862cd62, b5f0f2c5, b2e73a69, 85bdd6a6 and c134524d, and was first published
  in a runtime image built from c134524d. It shipped in clink's releases
  v0.16.0 (15 November), v0.16.1 (16 November) and v0.16.2 (17 November) with
  two fixes: 4fe76f37 (15 November), so that on Linux a value Relate refuses
  carries Relate's own reason, and c36742c7 (17 November), so that a sink
  retries a schema statement that meets a write conflict as it opens, as it
  already retried a batch. This repository pins v0.16.2.
- **This repository** was started on 13 November 2026. Its first event
  generator, reference rules, store checks and pipeline come from a spike
  written on 12 and 13 November 2026, also during the contest period.
- **Relate by Neo4j:** `relate-db` 1.0.1 from PyPI, Relate's C library 1.0.1
  inside clink's image, and, optionally, Relate's command line 1.0.1 for its
  MCP server, downloaded from Relate's GitHub release by
  `scripts/fetch-relate-cli.sh`.
- **MCP Python SDK** 2.3.0 (`mcp`, optional, `requirements-mcp.txt`): the
  client `mcp_check.py` and the investigator's MCP backend use.
- **Third-party tools:** Docker, to run the clink image. The Anthropic Python
  SDK 2.8.0 and the model Claude Opus 5.5, for the agent, reached through
  Amazon Bedrock for the recorded runs (boto3 and botocore 1.44.2 for its
  credentials).
- **AI tools:** Claude Code, with Claude Opus 5.5, wrote much of the code and
  documentation in this repository and in clink's Relate connector, under the
  author's direction and review.

## Licence

Apache License 2.0. See [LICENSE](LICENSE) and [NOTICE](NOTICE).
