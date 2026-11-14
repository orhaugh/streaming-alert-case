#!/usr/bin/env bash
# fetch-relate-cli.sh - install the relate command line that serve-mcp.sh runs,
# at .relate/bin/relate in this repository (git ignores it).
#
# Optional: only Relate's MCP server needs it. verify.py, explore.py and the
# agent use the Python library, relate-db, from requirements.txt.
#
# Relate publishes its command line as one binary per platform, listed in the
# release's SHA256SUMS, which is signed with Relate's release key. The sha256
# values below were copied from the v1.0.1 SHA256SUMS after its signature was
# verified with `ssh-keygen -Y verify`, against the key Relate pins in its
# install.sh and publishes on relatedb.ai. The pins decide what is installed:
# the release hosts the bytes, this repository decides what it trusts.
#
#   scripts/fetch-relate-cli.sh              download the pinned binary
#   RELATE_CLI_BINARY=/path/to/relate scripts/fetch-relate-cli.sh
#                                            install a binary already on disk;
#                                            it must match the pin
#
# Exit codes: 0 installed, or already installed; 3 Relate publishes no binary
# for this platform; 1 anything else (download failed, checksum mismatch).
set -euo pipefail

VERSION=1.0.1
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DEST="${ROOT}/.relate/bin/relate"
URL="https://github.com/relatedb/relate/releases/download/v${VERSION}"

case "$(uname -s)/$(uname -m)" in
    Darwin/arm64)              asset=relate-darwin-arm64 pin=31c02deb4c577b84e060e3ea51e0c96a54ef8e94dcb05559dc126432e6bc864c ;;
    Darwin/x86_64)             asset=relate-darwin-amd64 pin=71b161136572a32db175c4ef61f7f9299868a30b7ec356a57d006841ccd84137 ;;
    Linux/aarch64|Linux/arm64) asset=relate-linux-arm64 pin=6d8d37530070f238ac5578c1a6c69c737d7bd919b89e43ce2b631b612e8f9303 ;;
    Linux/x86_64)              asset=relate-linux-amd64 pin=2ca69bd6440d25b78c1677d11c0e3f2f5722601a4984475b331abc0a4f9fed2a ;;
    *)
        echo "fetch-relate-cli: Relate publishes no command line for $(uname -s)/$(uname -m)" >&2
        exit 3
        ;;
esac

sha256() {
    if command -v sha256sum >/dev/null 2>&1; then
        sha256sum "$1" | awk '{print $1}'
    else
        shasum -a 256 "$1" | awk '{print $1}'
    fi
}

if [ -x "${DEST}" ] && [ "$(sha256 "${DEST}")" = "${pin}" ]; then
    echo "fetch-relate-cli: relate ${VERSION} (${asset}) is already at ${DEST}"
    exit 0
fi

tmp="$(mktemp -d)"
trap 'rm -rf "${tmp}"' EXIT
if [ -n "${RELATE_CLI_BINARY:-}" ]; then
    cp "${RELATE_CLI_BINARY}" "${tmp}/relate"
else
    curl -fsSL --retry 3 -o "${tmp}/relate" "${URL}/${asset}"
fi
got="$(sha256 "${tmp}/relate")"
if [ "${got}" != "${pin}" ]; then
    echo "fetch-relate-cli: ${asset} has sha256 ${got}, not the pinned ${pin}; installing nothing" >&2
    exit 1
fi
chmod 755 "${tmp}/relate"
mkdir -p "$(dirname "${DEST}")"
mv "${tmp}/relate" "${DEST}"
echo "fetch-relate-cli: installed relate ${VERSION} (${asset}) at ${DEST}"
