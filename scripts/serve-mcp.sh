#!/bin/sh
# serve-mcp.sh - serve one of this repository's published stores read-only through
# Relate's own MCP server, over stdio, for an MCP host (Claude Code, Claude
# Desktop, Cursor and others) to start.
#
#   sh scripts/serve-mcp.sh [small|large]   the 55-transfer case (default), or 50,000 transfers
#   sh scripts/serve-mcp.sh revision        the evolving investigation's published revision (revise.py)
#   sh scripts/serve-mcp.sh --config        print a host configuration with this checkout's absolute paths
#
# Every path is resolved from this script's own location, so a host may start
# it from any directory. stdout carries the server's JSON-RPC and nothing else:
# this script writes only to stderr.
#
# Before serving, it checks:
#   - the relate command line is 1.0.1, the version this repository is tested
#     with: RELATE_BIN if set, else .relate/bin/relate (installed by
#     scripts/fetch-relate-cli.sh), else relate on PATH;
#   - the store is there; the large case's is unpacked from its gzipped copy
#     on first use, and again whenever that copy changes, by the rule
#     alertcase/cases.py states: <store>.unpacked-from holds the sha256 of the
#     gzipped copy the store came from; for revision, the store is the one the
#     last publication in revision/ledger.jsonl names;
#   - the store's Run record shows a completed bounded replay: every job
#     completed, clink exited 0 and was not cancelled. scripts/publish_run.py
#     publishes a store only after that; this checks the store being served.
# Then it becomes: relate serve --mcp stdio --database <store> --read-only
# The server lists read_cypher and get_schema only, and every write fails.
# Relate's anonymous usage metrics are off: DO_NOT_TRACK=1, RELATE_TELEMETRY=0.
set -eu

ROOT=$(CDPATH='' cd -- "$(dirname -- "$0")/.." && pwd)
PINNED=1.0.1
export DO_NOT_TRACK=1 RELATE_TELEMETRY=0

fail() {
    echo "serve-mcp.sh: $*" >&2
    exit 1
}

if [ "${1:-}" = "--config" ]; then
    script=$(printf '%s' "${ROOT}/scripts/serve-mcp.sh" | sed 's/\\/\\\\/g; s/"/\\"/g')
    cat <<EOF
{
  "mcpServers": {
    "streaming-alert-case": {
      "command": "/bin/sh",
      "args": ["${script}", "small"]
    },
    "streaming-alert-case-large": {
      "command": "/bin/sh",
      "args": ["${script}", "large"]
    },
    "streaming-alert-case-revision": {
      "command": "/bin/sh",
      "args": ["${script}", "revision"]
    }
  }
}
EOF
    exit 0
fi

case "${1:-small}" in
    small) store="${ROOT}/store/case.rl" ;;
    large) store="${ROOT}/store/large.rl" ;;
    revision)
        ledger="${ROOT}/revision/ledger.jsonl"
        [ -f "${ledger}" ] || fail "no published investigation at ${ROOT}/revision: run revise.py --out revision"
        published=$(grep '"kind": "publication"' "${ledger}" | tail -n 1 | sed -n 's/.*"store": "\(r[0-9]*\.rl\)".*/\1/p')
        [ -n "${published}" ] || fail "${ledger} records no publication"
        store="${ROOT}/revision/${published}"
        ;;
    *)
        echo "usage: sh scripts/serve-mcp.sh [small|large|revision] | --config" >&2
        exit 2
        ;;
esac

if [ -n "${RELATE_BIN:-}" ]; then
    relate=${RELATE_BIN}
elif [ -x "${ROOT}/.relate/bin/relate" ]; then
    relate="${ROOT}/.relate/bin/relate"
elif command -v relate >/dev/null 2>&1; then
    relate=$(command -v relate)
else
    fail "no relate command line: run scripts/fetch-relate-cli.sh, or set RELATE_BIN"
fi
version=$("${relate}" --version 2>/dev/null | sed -n '1s/^Relate v//p')
[ "${version}" = "${PINNED}" ] ||
    fail "${relate} is relate ${version:-of unknown version}; this repository is tested with ${PINNED} (scripts/fetch-relate-cli.sh installs it)"

sha256() {
    if command -v sha256sum >/dev/null 2>&1; then
        sha256sum "$1" | awk '{print $1}'
    else
        shasum -a 256 "$1" | awk '{print $1}'
    fi
}
if [ -f "${store}.gz" ]; then
    digest=$(sha256 "${store}.gz")
    if [ ! -f "${store}" ] || [ "$(cat "${store}.unpacked-from" 2>/dev/null)" != "${digest}" ]; then
        partial="${store}.unpacking.$$"
        trap 'rm -f "${partial}"' EXIT
        gunzip -c "${store}.gz" >"${partial}"
        mv "${partial}" "${store}"
        trap - EXIT
        printf '%s\n' "${digest}" >"${store}.unpacked-from"
    fi
fi
[ -f "${store}" ] || fail "no store at ${store}: run ./rebuild.sh ${1:-small}"

completed='MATCH (r:Run) WITH collect(r) AS runs
RETURN size(runs) = 1 AND all(x IN runs WHERE x.jobs_completed = x.jobs AND x.clink_exit_status = 0 AND NOT x.cancelled) AS completed'
answer=$("${relate}" --database "${store}" --read-only --mode json "${completed}" 2>&1) ||
    fail "could not read the run record of ${store}: ${answer}"
case "${answer}" in
    *'"completed":true'*) ;;
    *) fail "${store} does not record a completed bounded replay; not serving it" ;;
esac

# The server keeps this process's id, so a client can follow the process it
# owns without listing other processes.
echo "serve-mcp.sh: process $$ serves ${store} read-only" >&2
exec "${relate}" serve --mcp stdio --database "${store}" --read-only
