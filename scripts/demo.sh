#!/usr/bin/env bash
# demo.sh - run the demo video's five sections in order, for recording or for a
# timed rehearsal. DEMO.md is the script to read alongside: what to say, and
# when. Every command runs offline and needs no model or API key.
#
#   ./scripts/demo.sh              wait for Enter before each section
#   ./scripts/demo.sh --rehearse   no waiting; print each section's time
#   ./scripts/demo.sh --revision   the optional sixth section alone, outside the
#                                  two-minute cut: new evidence, the affected
#                                  finding, a verified amendment
#
# Run it in a fresh clone set up as the README describes, with Docker and the
# MCP extras (scripts/fetch-relate-cli.sh, requirements-mcp.txt). Section 1
# rebuilds store/case.rl and tables/case.sqlite from the event file: the same
# records, not the same bytes, so git shows them changed afterwards.
set -euo pipefail
cd "$(dirname "$0")/.."
REHEARSE=0
REVISION=0
[ "${1:-}" = "--rehearse" ] && REHEARSE=1
[ "${1:-}" = "--revision" ] && REVISION=1

clock() { .venv/bin/python -c 'import time; print(time.time())'; }

section() {  # a title, then the commands to show and run, one per argument
    local title=$1 began command
    shift
    if [ "${REHEARSE}" -eq 0 ]; then
        read -r -p $'\n'"[Enter: ${title}] " _
    fi
    printf '\n\033[1m%s\033[0m\n' "${title}"
    began=$(clock)
    for command in "$@"; do
        printf '\n$ %s\n' "${command}"
        eval "${command}"
    done
    if [ "${REHEARSE}" -eq 1 ]; then
        .venv/bin/python -c 'import sys, time; print(f"[{sys.argv[1]}: {time.time() - float(sys.argv[2]):.1f} s]")' \
            "${title}" "${began}"
    fi
}

if [ "${REVISION}" -eq 1 ]; then
    # revise.py publishes into build/revision/, which is not tracked: nothing to put back afterwards.
    section "6. Optional: new evidence, the affected finding, a verified amendment" \
        ".venv/bin/python revise.py | grep -v -E '^(Bounded replays|  Case note|  Ledger)' | cut -c1-118" \
        ".venv/bin/python explore.py --revision r2 --cypher \"MATCH (:Revision {id: 'r2'})-[:ADDED]->(t:Transfer)<-[:SENT]-(a:Account)<-[s:SCOPE {revision: 'r1', role: 'debit'}]-(c:Claim) WHERE s.start_ms <= t.ts AND t.ts <= s.end_ms RETURN c.id AS claim, c.type AS type, t.id AS new_transfer, a.id AS account\""
    exit 0
fi

section "1. clink replays 55 transfers into a Relate database" \
    "./rebuild.sh | grep -E '^(reconciled|published)|checks passed'" \
    ".venv/bin/python explore.py --cypher \"MATCH (r:Run) RETURN r.jobs_completed AS jobs_completed, r.clink_exit_status AS clink_exit_status, r.cancelled AS cancelled, r.dataset_events AS events\""

section "2. Two alerts that look alike, and what tells them apart" \
    ".venv/bin/python explore.py | sed -n '/WHERE THE TWO ALERTS DIFFER/,/device shared/p'" \
    ".venv/bin/python explore.py --cypher \"MATCH p = (:Transfer {id: 'T0002'})-[:PASSED_ON*]->(t:Transfer) WHERE NOT (t)-[:PASSED_ON]->() RETURN [n IN nodes(p) | n.id] AS path\""

section "3. The same database, read-only, over MCP" \
    ".venv/bin/python mcp_check.py --case small | sed -n '/as .mcp.json starts it/,/store unchanged/p' | cut -c1-118"

section "4. Recorded on 13 November 2026: an AI agent's case note" \
    "grep -E -A1 '^Agent output|^- \*\*(f5|h1|u1)\*\*' runs/recorded/small-case-note-r4/case_note.md | grep -v -E '^(--)?$' | cut -c1-118"

section "5. Wrong claims the checker rejects" \
    ".venv/bin/python verify.py --case small | grep -E 'planted P[23]|checks passed' | cut -c1-118"
