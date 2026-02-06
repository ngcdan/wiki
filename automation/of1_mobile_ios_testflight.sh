#!/usr/bin/env bash
set -euo pipefail

# OF1 Mobile (Flutter) - Build iOS IPA + Upload to TestFlight
#
# Usage (run anywhere):
#   of1m-tf
#   # or directly:
#   /Users/nqcdan/dev/wiki/automation/of1_mobile_ios_testflight.sh
#
# Requirements (one-time):
# - Xcode installed + signed in
# - CocoaPods installed (pod)
# - Flutter available in PATH
# - fastlane auth (SESSION):
#     export FASTLANE_USER="nqcdan1908@gmail.com"
#     export FASTLANE_SESSION="..."   # generated via: bundle exec fastlane spaceauth
#
# Repo paths:
MOBILE_DIR="/Users/nqcdan/OF1/forgejo/of1-platform/of1-mobile/apps/mobile"
IOS_DIR="$MOBILE_DIR/ios"

log() { printf "[%s] %s\n" "$(date '+%Y-%m-%d %H:%M:%S')" "$*"; }
run() { log "+ $*"; "$@"; }

die() { echo "ERROR: $*" >&2; exit 1; }

[[ -d "$MOBILE_DIR" ]] || die "Missing dir: $MOBILE_DIR"

command -v flutter >/dev/null 2>&1 || die "flutter not found in PATH"
command -v pod >/dev/null 2>&1 || die "pod (CocoaPods) not found"
command -v ruby >/dev/null 2>&1 || die "ruby not found"
command -v bundle >/dev/null 2>&1 || die "bundle (Bundler) not found"

# Require fastlane session env
: "${FASTLANE_USER:=nqcdan1908@gmail.com}"
[[ -n "${FASTLANE_SESSION:-}" ]] || die "Missing FASTLANE_SESSION. Generate via: (cd ios && bundle exec fastlane spaceauth)"

log "=== OF1 MOBILE iOS TestFlight: start ==="

cd "$IOS_DIR"

# Install fastlane (Bundler local to ios/)
if [[ ! -f Gemfile.lock ]]; then
  run bundle install
else
  run bundle install
fi

# Run the lane defined in ios/fastlane/Fastfile
run bundle exec fastlane ios testflight

log "=== OF1 MOBILE iOS TestFlight: done ==="
