#!/bin/bash

set -euo pipefail

die() { echo "fatal: $*" >&2; exit 1; }

TEMP="$(mktemp -d -t TEMP.XXXXXXX)" || die "failed to make tmpdir"
cleanup() { [[ -n "${TEMP:-}" ]] && rm -rf "${TEMP}"; }
trap cleanup EXIT

TOPLEVEL=$(git -C "$(cd "$(dirname "$0")" >/dev/null || exit 1; pwd)" rev-parse --show-toplevel) || die "TOPLEVEL fail"

unset PIP_REQUIRE_VIRTUALENV

set -x

export PATH="$(pwd)/.venv/bin:/usr/bin:/usr/sbin:/bin:/sbin"

mk_pex() {
  cd "$TOPLEVEL"

  local module_entry_point dest_path

  module_entry_point="${DFI_PEX_ENTRY_POINT:-}"
  dest_path="${DFI_PEX_DEST_PATH:-}"

  if [[ -z "$module_entry_point" || -z "$dest_path" ]]; then
    if [[ $# -lt 2 ]]; then
      die "requires 2 args: the module entry point and the output file name"
    fi

    module_entry_point="$1"
    shift
    dest_path="$1"
    shift
  fi

  mkdir -p "$(dirname "$dest_path")"

  temp_utils_pex="$TEMP/out.pex"
  req_txt="$TEMP/requirements.txt"

  pipenv lock -r > "${req_txt}"

  args=(
    .
    -r "${req_txt}"
    -m "${module_entry_point}"
    -o "${temp_utils_pex}"
    --interpreter-constraint 'CPython>=3.7'
  )

  pex "${args[@]}"

  mv "${temp_utils_pex}" "${dest_path}"
}

mk_pex "$@"
