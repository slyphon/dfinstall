#!/bin/bash

set -euo pipefail

die() { echo "fatal: $*" >&2; exit 1; }

TEMP="$(mktemp -d 2>/dev/null || mktemp -d -t tempdir)" || die "failed to make tmpdir"
cleanup() { [[ -n "${TEMP:-}" ]] && rm -rf "${TEMP}"; }
trap cleanup EXIT

TOPLEVEL=$(git -C "$(cd "$(dirname "$0")" >/dev/null || exit 1; pwd)" rev-parse --show-toplevel) || die "TOPLEVEL fail"

unset PIP_REQUIRE_VIRTUALENV VIRTUAL_ENV

mk_shiv() {
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

  req_file="${TEMP}/requirements.txt"

  pipenv lock -r > "${req_file}"

  dist_dir="${TEMP}/dist"
  pip install . -r "${req_file}" --target "${dist_dir}"
  shiv --site-packages "${dist_dir}" --compressed \
    -p '/usr/bin/env python' \
    -o "${dest_path}" \
    -e "${module_entry_point}"
}

mk_shiv "$@"
