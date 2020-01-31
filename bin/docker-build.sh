#!/bin/bash

set -euo pipefail
IFS=$'\n\t'

die() { echo "fatal: $*" >&2; exit 1; }

TEMP="$(mktemp -d 2>/dev/null || mktemp -d -t tempdir)" || die "failed to make tmpdir"
cleanup() { [[ -n "${TEMP:-}" ]] && rm -rf "${TEMP}"; }
trap cleanup EXIT

if [[ -n "${BUILD_IMAGE:-}" ]]; then
  DOCKER_BUILDKIT=1 docker build -t dfi-build:latest --target=system_python -f container/Dockerfile
fi

args=(
  run -it --rm
  -v "$(pwd):/workspaces/dfi:delegated"
  -u dfi
  -w /workspaces/dfi
  dfi-build:latest
  /bin/bash -c 'PYTHON=/usr/bin/python3 DOCKER_SETUP=1 /bin/bash -x bin/package.sh'
)

docker "${args[@]}"
