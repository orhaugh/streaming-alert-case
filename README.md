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

Not used: the `relate` command line, Relate's MCP server, WebAssembly, Bolt,
HTTP and vector search.

## Setup and run

Needs Python 3.11 or later. Rebuilding a store also needs Docker, and a live
agent run needs model credentials. Nothing else needs them.

```bash
git clone <this repository> streaming-alert-case && cd streaming-alert-case
python3 -m venv .venv
.venv/bin/pip install --require-hashes -r requirements.txt

.venv/bin/python verify.py          # both datasets, the checker and every recorded run; no model, no API key
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

## Where the data lives

| Path | What |
|---|---|
| `store/case.rl` | The Relate store: one file, written by clink, published by `scripts/publish_run.py` |
| `data/events.ndjson` | The 55 transfers in arrival order: what clink reads |
| `data/scenario.json` | The designed facts, read by the verifier only |
| `tables/case.sqlite` | The same records as tables, for the comparison only |
| `data/large/` | The large case: 50,000 transfers and its designed facts |
| `store/large.rl.gz`, `tables/large.sqlite.gz` | The large case's store and tables, gzipped; unpacked byte for byte on first use |
| `claims/planted.json`, `claims/planted-large.json` | Deliberately unsupported claims the checker must reject |
| `runs/recorded/` | Recorded agent runs: transcript, submitted case note, verdicts, score, rendered `case_note.md` |
| `runs/superseded/` | Runs recorded with an earlier prompt revision, kept and still verified |
| `runs/shakedown/` | Live runs that checked the harness before recording; part of no result, still verified |

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

Each run is labelled with the prompt revision that made it. The checker's
rules have not changed across revisions; the agent's wording and guidance have.

| Revision | Commit | What changed | Runs |
|---|---|---|---|
| r1 | b5f9799 | the case note submitted through a tool | `runs/shakedown/small-graph-r1` |
| r2 | d9a9d16 | path accounts defined exactly | `runs/superseded/small-*-r2` |
| r3 | 27f96d0 | path end accounts defined exactly | `runs/recorded/small-*-r3`, `runs/shakedown/large-*-r3` |
| r4 | 9caefc0 | onward links described as timing; both arms given equivalent traversal guidance | `runs/recorded/small-case-note-r4`, `runs/recorded/large-comparison-r4` |

The r1 shakedown counted an alert's senders among its path accounts, a fair
reading of wording that did not say whether senders count. In the r2 set, five
of six comparison runs listed an alerted account among its path ends because
some of its contributing transfers had no onward link. Each time the wording
was made exact to match what the checker had always computed, and both arms
were given the same words. r3 and earlier runs keep their transcripts as
recorded, including wording such as "comes to rest" that r4 replaced.

`verify.py` checks every claim of every recorded, superseded and shakedown run
again, and fails if a verdict or a recorded score differs.

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

## What ran

On macOS 26.3.1, arm64, on 13 November 2026:

- `./rebuild.sh` built `store/case.rl`, and `./rebuild.sh large` built
  `store/large.rl`, from `ghcr.io/orhaugh/clink-runtime:sha-c134524d8674`,
  index digest
  `sha256:f19c890c747e8a6e097568e0003cd83c303599a4bfbb0095751045909124802f`.
  They ran as linux/arm64, with Docker Desktop (engine 29.8.2) and no network.
  clink exited 0 both times: 55 of 55 and 50,000 of 50,000 records reconciled.
  For the large case clink took about six seconds and publishing 28.
- `investigate.py --provider bedrock --smoke`, for each case: one request
  through Bedrock from ap-south-1, accepted and answered by `claude-opus-5-5`.
- The recorded, superseded and shakedown runs listed under "Agent runs and
  prompt revisions", all through Bedrock.
- `verify.py`: 57 of 57 checks passed. For each dataset: 9 on the store, 5 on
  the checker (its answer key and four planted claims) and 1 on the tables.
  Then every recorded, superseded and shakedown run, and each comparison's
  summary.
- `python -m unittest`: 18 tests passed.
- Python 3.12.3, `relate-db` 1.0.1, `anthropic` 2.8.0, boto3 and botocore
  1.44.2, installed with `--require-hashes` from `requirements-bedrock.txt`.
- A fresh clone, set up exactly as in "Setup and run", with Python 3.11.9 and
  `requirements.txt` only. The large store and tables unpacked from their
  gzipped copies on first use. `verify.py` passed 57 of 57 in under ten
  seconds, 18 tests passed, and `explore.py --case large` ran. `./rebuild.sh`
  and `./rebuild.sh large` then exited 0, and each verified its dataset again,
  recorded runs included, against the rebuilt store.

The same pipeline, from the same image, was also run on scratch copies of the
case during the spike this repository grew from: five fresh runs on
linux/arm64 and five on linux/amd64, under emulation on the same Mac. Each
passed the spike's nine store checks.

## Not done, and not verified

- **Model and dataset variety:** the comparisons use one model, two synthetic
  datasets and three runs per arm. They are observations, not statistically
  tested differences.
- **The Claude API path:** the recorded runs went through Amazon Bedrock. The
  Claude API path is tested only with a scripted stand-in client.
- The `relate` command line and Relate's MCP server were not run. The stores
  were reopened through the Python library only.
- The pipeline has run only in Docker on a Mac: never on a Linux host or an
  x86_64 machine.
- clink's Relate connector is in no clink release. The image is a build of
  clink's main branch.
- Rebuilt stores are not byte-identical to each other. Every check compares
  content.

## Reused work, tools and disclosures

- **clink** is the author's own stream engine, a project started before this
  contest (its git history begins in June 2026; latest release v0.15.0, 3
  November 2026). It is not in this repository. Its Relate connector,
  `connector='relate'`, was written during the contest period. It landed in
  clink's repository on 13 November 2026 in commits b862cd62, b5f0f2c5,
  b2e73a69, 85bdd6a6 and c134524d, and was published in the runtime image this
  repository pins.
- **This repository** was started on 13 November 2026. Its first event
  generator, reference rules, store checks and pipeline come from a spike
  written on 12 and 13 November 2026, also during the contest period.
- **Relate by Neo4j:** `relate-db` 1.0.1 from PyPI, and Relate's C library
  1.0.1 inside clink's image.
- **Third-party tools:** Docker, to run the clink image. The Anthropic Python
  SDK 2.8.0 and the model Claude Opus 5.5, for the agent, reached through
  Amazon Bedrock for the recorded runs (boto3 and botocore 1.44.2 for its
  credentials).
- **AI tools:** Claude Code, with Claude Opus 5.5, wrote much of the code and
  documentation in this repository and in clink's Relate connector, under the
  author's direction and review.

## Licence

Apache License 2.0. See [LICENSE](LICENSE) and [NOTICE](NOTICE).
