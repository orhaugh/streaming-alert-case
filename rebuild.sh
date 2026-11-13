#!/usr/bin/env bash
# Rebuild the published store from the event file: clink runs the three jobs
# in pipeline/case.sql, each writing into the store through connector='relate',
# then publish_run.py reconciles the store with the file and adds the Run
# record, and verify.py checks the result. Needs Docker and the venv.
#
# The clink is the runtime image built from clink's main branch at commit
# c134524d (not a release), pinned by digest. It carries the Relate connector
# for linux/amd64 and linux/arm64.
set -euo pipefail
cd "$(dirname "$0")"

IMAGE="ghcr.io/orhaugh/clink-runtime:sha-c134524d8674@sha256:f19c890c747e8a6e097568e0003cd83c303599a4bfbb0095751045909124802f"
PY="${PYTHON:-.venv/bin/python}"

mkdir -p build
rm -f store/case.building.rl
# --user: the store is written readable by its owner only, and publish_run.py
# must open it. --network none: the pipeline reads a file and writes a file.
set +e
docker run --rm --network none --user "$(id -u):$(id -g)" \
    -v "$PWD":/work -w /work "$IMAGE" run pipeline/case.sql > build/clink-run.log 2>&1
status=$?
set -e
cat build/clink-run.log
if [ "$status" -ne 0 ]; then
    echo "clink exited $status: not every job ended without error, so nothing is published" >&2
    exit 1
fi
"$PY" scripts/publish_run.py --clink "$IMAGE" --clink-exit-status "$status" --clink-log build/clink-run.log
"$PY" export_tables.py
"$PY" verify.py
