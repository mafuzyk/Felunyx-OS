#!/usr/bin/env bash
set -Eeuo pipefail

# shellcheck source=tools/lib/common.sh
source "$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)/common.sh"

felunyx_assert_safe_workdir() {
  local raw=$1 temp_root=$2 repo_root=$3
  [[ -n $raw ]] || felunyx_die 'work directory is empty'
  local path temp repo
  path=$(felunyx_realpath "$raw")
  temp=$(felunyx_realpath "$temp_root")
  repo=$(felunyx_realpath "$repo_root")
  [[ $path != / ]] || felunyx_die 'refusing root as work directory'
  [[ $path != "$repo" ]] || felunyx_die 'refusing repository root as work directory'
  [[ $path == "$temp"/* ]] || felunyx_die "work directory must be below temporary root: $temp"
  printf '%s\n' "$path"
}

felunyx_list_workdir_mounts() {
  local path=$1
  if command -v findmnt >/dev/null 2>&1; then
    findmnt --raw --noheadings --output TARGET 2>/dev/null | awk -v p="$path" '$0 == p || index($0, p "/") == 1' || true
  fi
}

felunyx_remove_workdir() {
  local raw=$1 temp_root=$2 repo_root=$3
  local path
  path=$(felunyx_assert_safe_workdir "$raw" "$temp_root" "$repo_root")
  local mounts
  mounts=$(felunyx_list_workdir_mounts "$path")
  [[ -z $mounts ]] || felunyx_die "refusing cleanup while mounts remain under $path: ${mounts//$'\n'/, }"
  [[ -e $path ]] || return 0
  rm -rf --one-file-system -- "$path"
}
