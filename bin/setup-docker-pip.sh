#!/bin/bash

set -euo pipefail
die() { echo "fatal: $*" >&2; exit 1; }

TEMP="$(mktemp -d 2>/dev/null || mktemp -d -t tempdir)" || die "failed to make tmpdir"

cleanup() { [[ -n "${TEMP:-}" ]] && rm -rf "${TEMP}"; }
trap cleanup EXIT


[[ "$(uname -s)" == "Linux" ]] || die "this should only be run in docker"

export PATH="$HOME/.local/bin:$PATH"

curl --fail -q https://bootstrap.pypa.io/get-pip.py -o "$TEMP/get-pip.py"
/usr/bin/python3 "$TEMP/get-pip.py"
pip install --no-cache-dir pipenv pex

