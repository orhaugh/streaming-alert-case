# Demo script, 1 minute 50 seconds

This is the script for the demo video, not the video. `scripts/demo.sh` runs
its five sections in order, showing each command, and waits for Enter between
them; this page says what to say over each. Every command runs offline and
needs no model or API key. The case note in section 4 is model output recorded
on 13 November 2026, and the video should say so.

Record from a fresh clone set up as the README describes, with Docker running
and the MCP extras installed (`scripts/fetch-relate-cli.sh`,
`requirements-mcp.txt`). Section 1 rebuilds `store/case.rl` from the event
file. A rehearsal, `./scripts/demo.sh --rehearse`, runs it all without
pausing and times each section.

## 1. clink replays the events into Relate (0:00 to 0:20)

```bash
./rebuild.sh | grep -E '^(reconciled|published)|checks passed'
.venv/bin/python explore.py --cypher "MATCH (r:Run) RETURN r.jobs_completed AS jobs_completed, r.clink_exit_status AS clink_exit_status, r.cancelled AS cancelled, r.dataset_events AS events"
```

Say: "clink, a stream engine, replays 55 synthetic transfers that arrive out
of order. Three SQL jobs derive alerts and onward links by event time, and
write them through clink's native Relate connector into one file. It is
published only because every job completed and clink exited 0."

## 2. Two alerts, and the relationships that tell them apart (0:20 to 0:45)

```bash
.venv/bin/python explore.py | sed -n '/WHERE THE TWO ALERTS DIFFER/,/device shared/p'
.venv/bin/python explore.py --cypher "MATCH p = (:Transfer {id: 'T0002'})-[:PASSED_ON*]->(t:Transfer) WHERE NOT (t)-[:PASSED_ON]->() RETURN [n IN nodes(p) | n.id] AS path"
```

Say: "Two fan-in alerts fire on the same rule: six senders into one account
inside an hour. As alert rows they differ only in their totals. In Relate their
relationships differ: candidate paths of three onward links against one, and
device D-568 shared along one alert's paths. An onward link is timing, a debit
soon after a credit, not proof that funds moved."

## 3. The same file, read-only, through Relate's MCP server (0:45 to 1:00)

```bash
.venv/bin/python mcp_check.py --case small | sed -n '/as .mcp.json starts it/,/store unchanged/p' | cut -c1-118
```

Say: "Any MCP host can open the same file through Relate's own MCP server,
read-only. This check talks to it as an agent host does: two read-only tools,
every path equal to the reference, writes refused, the store unchanged."

## 4. A case note, recorded (1:00 to 1:25)

```bash
grep -E -A1 '^Agent output|^- \*\*(f5|h1|u1)\*\*' runs/recorded/small-case-note-r4/case_note.md | grep -v -E '^(--)?$' | cut -c1-118
```

Say: "This is model output recorded on 13 November, not generated now. An
agent queried the same store. Findings cite claims the checker supported,
interpretations stay hypotheses, and who controls D-568 stays an open
question: the data records device use, not identity."

## 5. A claim the checker rejects (1:25 to 1:50)

```bash
.venv/bin/python verify.py --case small | grep -E 'planted P[23]|checks passed' | cut -c1-118
```

Say: "No model and no API key: every claim is checked against the original
events and the graph. These planted claims are what arrival-order processing
would conclude: late transfer T0012 missing from the alert, and a path ended
too early. Both are rejected. This holds for this bounded replay only."

## Recording it

On macOS, in a fresh clone set up as above, with Docker running:

1. Run `./scripts/demo.sh --rehearse`, then `git checkout -- store tables`.
   This warms Docker and the MCP client, and puts the shipped store back.
2. Set the terminal to 120 columns with a large font (about 18 pt), and run
   `clear`. Every line of output fits in 120 columns; long commands wrap.
3. Press Shift-Command-5, choose Record Selected Portion around the terminal,
   pick your microphone under Options, and click Record.
4. Run `./scripts/demo.sh`. Press Enter for each section and read its "Say"
   text above.
5. Stop the recording from the menu bar. If it runs over two minutes, trim it
   in QuickTime Player (Edit, Trim).
6. Upload it where judges can watch without logging in, for example YouTube
   as Unlisted, and put the link in `SUBMISSION.md`.
