#!/usr/bin/env bash
set -Eeuo pipefail

felunyx_log() { printf '[felunyx] %s\n' "$*" >&2; }
felunyx_die() { printf '[felunyx] error: %s\n' "$*" >&2; exit 1; }
felunyx_require_command() { command -v "$1" >/dev/null 2>&1 || felunyx_die "required command missing: $1"; }
felunyx_realpath() {
  python3 - "$1" <<'PY'
import os
import sys
print(os.path.realpath(sys.argv[1]))
PY
}
felunyx_write_json_atomic() {
  local target=$1
  local parent
  parent=$(dirname -- "$target")
  mkdir -p -- "$parent"
  local tmp
  tmp=$(mktemp "${parent}/.$(basename -- "$target").XXXXXX")
  cat >"$tmp"
  chmod 0644 "$tmp"
  mv -f -- "$tmp" "$target"
}
