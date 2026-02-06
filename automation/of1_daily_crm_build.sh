#!/usr/bin/env bash
set -euo pipefail

# OF1 - Daily CRM fetch+merge + clean build
#
# Usage (run anywhere):
#   /Users/nqcdan/dev/wiki/automation/of1_daily_crm_build.sh
#
# Notes:
# - Expects of1-build repo at: /Users/nqcdan/OF1/forgejo/of1-platform/of1-build
# - Uses git.sh conventions:
#     ./git.sh fetch origin crm
#     ./git.sh merge --no-edit origin/crm
# - One-time setting recommended:
#     git config --global merge.autoEdit no

ROOT_DIR="/Users/nqcdan/OF1/forgejo/of1-platform/of1-build"
CLEAN_TARGET_REL="../working/release-platform/server"

log() { printf "[%s] %s\n" "$(date '+%Y-%m-%d %H:%M:%S')" "$*"; }
run() { log "+ $*"; "$@"; }

die() { echo "ERROR: $*" >&2; exit 1; }

cd "$ROOT_DIR" || die "Cannot cd to $ROOT_DIR"

[[ -x ./git.sh ]] || die "Missing or non-executable: $ROOT_DIR/git.sh"
[[ -x ./tools.sh ]] || die "Missing or non-executable: $ROOT_DIR/tools.sh"

log "=== OF1 DAILY CRM BUILD: start ==="

# 0) Ensure branch
run ./git.sh checkout crm

# 1) Visibility + commit staged work if any
run ./git.sh status
run ./git.sh working:commit "review code"

# 2) Update code (fetch ONLY crm, then merge)
run ./git.sh fetch origin crm
run ./git.sh merge --no-edit origin/crm

# 3) Clean build output (guard path)
CLEAN_TARGET_ABS="$(cd "$ROOT_DIR" && cd "$(dirname "$CLEAN_TARGET_REL")" && pwd)/$(basename "$CLEAN_TARGET_REL")"
EXPECTED_SUFFIX="/working/release-platform/server"
[[ "$CLEAN_TARGET_ABS" == *"$EXPECTED_SUFFIX" ]] || die "Refusing to delete unexpected path: $CLEAN_TARGET_ABS"

log "Cleaning: $CLEAN_TARGET_ABS"
rm -rf "$CLEAN_TARGET_ABS"

# 4) Build
run ./tools.sh build -clean -code -ui

log "=== OF1 DAILY CRM BUILD: success ==="
