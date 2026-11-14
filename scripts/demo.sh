#!/usr/bin/env bash
# demo.sh - run the demo video's five sections in order, for recording or for a
# timed rehearsal. DEMO.md is the script to read alongside: what to say, and
# when. Every command runs offline and needs no model or API key.
#
#   ./scripts/demo.sh              wait for Enter before each section
#   ./scripts/demo.sh --rehearse   no waiting; print each section's time
#
# Run it in a fresh clone set up as the README describes, with Docker and the
# MCP extras (scripts/fetch-relate-cli.sh, requirements-mcp.txt). Section 1
# rebuilds store/case.rl and tables/case.sqlite from the event file: the same
# records, not the same bytes, so git shows them changed afterwards.
set -euo pipefail
cd "$(dirname "$0")/.."
REHEARSE=0
[ "${1:-}" = "--rehearse" ] && REHEARSE=1

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

section "1. clink replays the events into Relate" \
    "./rebuild.sh | grep -E '^(reconciled|published)|checks passed'" \
    ".venv/bin/python explore.py --cypher \"MATCH (r:Run) RETURN r.jobs_completed AS jobs_completed, r.clink_exit_status AS clink_exit_status, r.cancelled AS cancelled, r.dataset_events AS events\""

section "2. Two alerts, and the relationships that tell them apart" \
    ".venv/bin/python explore.py | sed -n '/WHERE THE TWO ALERTS DIFFER/,/device shared/p'" \
    ".venv/bin/python explore.py --cypher \"MATCH p = (:Transfer {id: 'T0002'})-[:PASSED_ON*]->(t:Transfer) WHERE NOT (t)-[:PASSED_ON]->() RETURN [n IN nodes(p) | n.id] AS path\""

section "3. The same file, read-only, through Relate's MCP server" \
    ".venv/bin/python mcp_check.py --case small | sed -n '/as .mcp.json starts it/,/store unchanged/p' | cut -c1-150"

section "4. A case note: model output recorded on 13 November 2026, not generated now" \
    "grep -E -A1 '^Agent output|^- \*\*(f5|h1|u1)\*\*' runs/recorded/small-case-note-r4/case_note.md | grep -v -E '^(--)?$' | cut -c1-150"

section "5. A claim the checker rejects" \
    ".venv/bin/python verify.py --case small | grep -E 'planted P[23]|checks passed' | cut -c1-150"
