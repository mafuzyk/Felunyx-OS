#!/usr/bin/env bash
set -Eeuo pipefail

felunyx_prepare_builder_private_dir() {
  local parent=$1 private_dir=$2 owner=$3 group=$4
  chmod 0711 -- "$parent"
  install -d -m0700 -o "$owner" -g "$group" -- "$private_dir"
}
