# Demo video script

The video has five short sections and runs about 1 minute 50; the limit is
two minutes. `./scripts/demo.sh` puts each section on screen and waits for
you to press Enter before the next. While a section is showing, read its
quoted lines.

Everything on screen runs live and offline, with no AI model and no API key,
except the case note in section 4. An AI agent wrote that on 13 November, and
the narration says so.

An optional sixth section, outside the two-minute cut, shows a finding revised
when new evidence arrives. `./scripts/demo.sh --revision` runs it on its own,
so it can be recorded separately or shown live.

## Before you record

1. Use a clone set up as the README describes, with Docker running and the
   MCP extras installed: `./scripts/fetch-relate-cli.sh`, then
   `.venv/bin/pip install --require-hashes -r requirements-mcp.txt`.
2. Run `./scripts/demo.sh --rehearse`, then `git checkout -- store tables`.
   The rehearsal warms Docker up and checks every section. The checkout puts
   back the database file that section 1 rebuilds.
3. Set the terminal to 120 columns with a large font (about 18 pt), and run
   `clear`.
4. Read the script aloud once against a timer. It should take 1:45 to 1:55.

## 1. clink replays 55 transfers into a Relate database (0:00 to 0:20)

> clink, my stream-processing engine, replays 55 synthetic transfers, some
> arriving out of order. Three SQL jobs find the alerts and the links between
> transfers, using when each happened, not when it arrived. They write the
> results into a Relate database file, published only because every job
> finished cleanly.

On screen: 55 of 55 records reconciled, the file published, and the run
record showing 3 jobs completed and exit status 0.

## 2. Two alerts that look alike, and what tells them apart (0:20 to 0:51)

> Both are fan-in alerts: five or more senders paying one account within an
> hour. As alerts, only their totals differ. Relate stores links too: a
> payment out of an account within 30 minutes of one coming in. A lead, not
> proof the money moved on. From A-9278 the links run three steps deep, and
> three accounts along them share device D-568. From A-9895, one step and no
> shared device.

On screen: the two alerts side by side, headed by the accounts they're about,
A-9278 and A-9895. Then one chain of linked transfers, T0002 to T0009.

## 3. The same database, read-only, over MCP (0:51 to 1:08)

> Relate can also serve this file over MCP, the standard way AI assistants
> connect to data, so your own assistant can question it. This check connects
> the same way. It can only read, and every path matches an independent
> calculation.

On screen: the MCP checks passing, including only read-only tools offered,
writes refused, and the file unchanged.

## 4. Recorded on 13 November 2026: an AI agent's case note (1:08 to 1:27)

> This part was recorded on 13 November. An AI agent, Claude, investigated the
> same data and wrote this case note. Every finding cites claims the checker
> confirmed. It keeps findings and hypotheses apart, and lists what the data
> can't answer, like who controls device D-568.

On screen: the note's header with its recording date, one finding with the
checker's verdict on each claim, a hypothesis, and an open question.

## 5. Wrong claims the checker rejects (1:27 to 1:50)

> The checker needs no AI and no API key. It tests every claim against the
> original events and the database. These two claims were planted. They're
> what you'd get by processing transfers as they arrived: one misses a late
> transfer, the other ends a chain too early. Both are rejected. This holds
> for these 55 transfers only.

On screen: the two planted claims, each rejected, and 34 of 34 checks passed.

## 6. Optional: new evidence, the affected finding, a verified amendment (about 40 seconds)

Not part of the two-minute video. Run `./scripts/demo.sh --revision`.

> Investigations change when evidence turns up late. In the first replay, the
> trail from A-9895 ends at A-1415: nothing qualifying leaves it within 30
> minutes. Then a transfer arrives that was not there before: A-1415 paid on
> eleven minutes after it was credited. A finished replay can't take it, and
> by event time it's three hours late, so clink recomputes from both files,
> merged by event time, and links the two transfers. Relate holds what each
> claim depends on, and one query finds the two claims this transfer touches.
> The checker confirms they held for the first revision and not the second.
> The old finding is superseded by an amendment, not rewritten, and the
> findings it didn't touch stand.

On screen: before, F4 with its absence at A-1415; the change, T0056, why it
is late, the new link onward:T0041:T0056 and the two claims selected; after,
F4 superseded by F5, with the path T0038, T0041, T0056, and F1 to F3
unchanged. Then the query in Relate that finds the claims T0056 falls into.
It needs no clean-up: revise.py publishes into `build/revision/`, which git
does not track.

## Record and upload (macOS)

1. Press Shift-Command-5, choose Record Selected Portion around the terminal,
   pick your microphone under Options, and click Record.
2. Run `./scripts/demo.sh`. Press Enter for each section and read its lines.
3. Stop the recording from the menu bar. If it runs over two minutes, trim it
   in QuickTime Player (Edit, Trim).
4. Run `git checkout -- store tables`.
5. Upload the video where judges can watch without logging in, for example
   YouTube as Unlisted, and put the link in `SUBMISSION.md`.

## What each section runs

`scripts/demo.sh` shows each command before it runs it.

1. ```bash
   ./rebuild.sh | grep -E '^(reconciled|published)|checks passed'
   .venv/bin/python explore.py --cypher "MATCH (r:Run) RETURN r.jobs_completed AS jobs_completed, r.clink_exit_status AS clink_exit_status, r.cancelled AS cancelled, r.dataset_events AS events"
   ```
2. ```bash
   .venv/bin/python explore.py | sed -n '/WHERE THE TWO ALERTS DIFFER/,/device shared/p'
   .venv/bin/python explore.py --cypher "MATCH p = (:Transfer {id: 'T0002'})-[:PASSED_ON*]->(t:Transfer) WHERE NOT (t)-[:PASSED_ON]->() RETURN [n IN nodes(p) | n.id] AS path"
   ```
3. ```bash
   .venv/bin/python mcp_check.py --case small | sed -n '/as .mcp.json starts it/,/store unchanged/p' | cut -c1-118
   ```
4. ```bash
   grep -E -A1 '^Agent output|^- \*\*(f5|h1|u1)\*\*' runs/recorded/small-case-note-r4/case_note.md | grep -v -E '^(--)?$' | cut -c1-118
   ```
5. ```bash
   .venv/bin/python verify.py --case small | grep -E 'planted P[23]|checks passed' | cut -c1-118
   ```
6. Optional, with `--revision`:
   ```bash
   .venv/bin/python revise.py | grep -v -E '^(Bounded replays|  Case note|  Ledger)' | cut -c1-118
   .venv/bin/python explore.py --revision r2 --cypher "MATCH (:Revision {id: 'r2'})-[:ADDED]->(t:Transfer)<-[:SENT]-(a:Account)<-[s:SCOPE {revision: 'r1', role: 'debit'}]-(c:Claim) WHERE s.start_ms <= t.ts AND t.ts <= s.end_ms RETURN c.id AS claim, c.type AS type, t.id AS new_transfer, a.id AS account"
   ```
