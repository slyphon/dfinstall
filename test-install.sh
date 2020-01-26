#!/bin/bash

set -euo pipefail
IFS=$'\n\t'

die() { echo "fatal: $*" >&2; exit 1; }

TEMP="$(mktemp -d -t test-vscode-install.XXXXXXX)" || die "failed to make tmpdir"
cleanup() { [[ -n "${TEMP:-}" ]] && rm -rf "${TEMP}"; }

if [[ ! -d '.git' ]]; then
  die "must be run from top level of vscode-settings directory"
fi

echo "using temp: $TEMP"
mkdir -p "${TEMP}/base/vscode-settings"

tar -cf- . | tar -C "${TEMP}/base/vscode-settings" -xf-
cd "${TEMP}/base"
python vscode-settings/install.py

echo "first run results" >&2
ls -la

echo "" >&2
python vscode-settings/install.py

echo "second run results" >&2
ls -la

echo "adding a file for .bashrc and re-running" >&2

rm "${TEMP}/base/.bashrc"
touch "${TEMP}/base/.bashrc"

python vscode-settings/install.py

echo "third run results" >&2
ls -la


