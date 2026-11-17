#!/usr/bin/env bash
# Rebuild a published store from its event file: clink runs the three jobs in
# the case's pipeline, each writing into the store through connector='relate';
# publish_run.py reconciles the store with the file and adds the Run record;
# export_tables.py writes the same records as tables; verify.py checks it all.
# Needs Docker and the venv.
#
#   ./rebuild.sh          the small case: 55 transfers   (store/case.rl)
#   ./rebuild.sh large    50,000 transfers              (store/large.rl, shipped gzipped)
#
# The clink is the runtime image of clink's release v0.16.1, pinned by digest.
# It carries the Relate connector for linux/amd64 and linux/arm64.
set -euo pipefail
cd "$(dirname "$0")"

CASE="${1:-small}"
IMAGE="ghcr.io/orhaugh/clink-runtime:0.16.1@sha256:d688ef7ddf6694532076bce7d12eb85a6d80ca4218385e44dfc3315657b52bf4"
PY="${PYTHON:-.venv/bin/python}"
case "$CASE" in
    small) EVENTS=data/events.ndjson PIPELINE=pipeline/case.sql STORE=store/case.rl ;;
    large) EVENTS=data/large/events.ndjson PIPELINE=pipeline/large.sql STORE=store/large.rl ;;
    *) echo "usage: $0 [small|large]" >&2; exit 2 ;;
esac
BUILDING="${STORE%.rl}.building.rl"

mkdir -p build
rm -f "$BUILDING"
# --user: the store is written readable by its owner only, and publish_run.py
# must open it. --network none: the pipeline reads a file and writes a file.
set +e
docker run --rm --network none --user "$(id -u):$(id -g)" \
    -v "$PWD":/work -w /work "$IMAGE" run "$PIPELINE" > "build/clink-run-$CASE.log" 2>&1
status=$?
set -e
cat "build/clink-run-$CASE.log"
if [ "$status" -ne 0 ]; then
    echo "clink exited $status: not every job ended without error, so nothing is published" >&2
    exit 1
fi
"$PY" scripts/publish_run.py --events "$EVENTS" --pipeline "$PIPELINE" --building "$BUILDING" --store "$STORE" \
    --clink "$IMAGE" --clink-exit-status "$status" --clink-log "build/clink-run-$CASE.log"
"$PY" export_tables.py --case "$CASE"
if [ "$CASE" = large ]; then
    "$PY" -c "from alertcase.cases import CASES; CASES['large'].pack()"
    echo "packed      store/large.rl.gz and tables/large.sqlite.gz"
fi
"$PY" verify.py --case "$CASE"
