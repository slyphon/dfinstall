#!/bin/bash

set -euo pipefail

die() { echo "fatal: $*" >&2; exit 1; }

TEMP="$(mktemp -d 2>/dev/null || mktemp -d -t tempdir)" || die "failed to make tmpdir"
cleanup() { [[ -n "${TEMP:-}" ]] && rm -rf "${TEMP}"; }
trap cleanup EXIT

TOPLEVEL=$(git -C "$(cd "$(dirname "$0")" >/dev/null || exit 1; pwd)" rev-parse --show-toplevel) || die "TOPLEVEL fail"

unset PIP_REQUIRE_VIRTUALENV
export PEX_IGNORE_RCFILES=1


set -x

scrub_shims() {
  local path i path_array new_path
  declare -a path_array
  declare -a new_path
  new_path=''


  IFS=: read -ra path_array <<<"${PATH}"

  for ((i = 0; i < ${#path_array[@]}; i++)); do
    if [[ "$(basename ${path_array[i]})" != "shims" ]]; then
      new_path=(${new_path[@]} ${path_array[i]})
    fi
  done

  path=$(
    IFS=:
    echo "${new_path[*]}"
  )

  echo "export PATH=$path"
}

mk_pex() {
  cd "$TOPLEVEL"

  local module_entry_point dest_path

  module_entry_point="${DFI_PEX_ENTRY_POINT:-dfi.app:main}"
  dest_path="${DFI_PEX_DEST_PATH:-dest/dfi.pex}"
  interactive="${DFI_PEX_INTERACTIVE:-f}"

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
    -v -v # -v -v -v -v -v -v
    -r "${req_txt}"
    -m "${module_entry_point}"
    --validate-entry-point
    --python-shebang python3
    -D "$TOPLEVEL/src"
    # --interpreter-constraint 'CPython>=3.7,<4'
  )

  if [[ "${interactive}" == 'f' ]]; then
    args+=(-o "${temp_utils_pex}")
  fi

  eval "$(scrub_shims)"

  export PEX_PYTHON=$(which python)
  python -m pex "${args[@]}"

  mv "${temp_utils_pex}" "${dest_path}"
}

mk_pex "$@"
