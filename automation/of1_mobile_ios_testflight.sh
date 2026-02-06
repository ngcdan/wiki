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
# - fastlane auth (App Store Connect API Key):
#     Set ONE of:
#       1) ASC_API_KEY_JSON=/absolute/path/to/asc_api_key.json
#          (recommended; easiest)
#       2) ASC_API_KEY_ID=XXXXXX
#          ASC_API_ISSUER_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
#          ASC_API_KEY_PATH=/absolute/path/to/AuthKey_XXXXXX.p8
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

# Require ASC API key env
if [[ -z "${ASC_API_KEY_JSON:-}" ]]; then
  if [[ -z "${ASC_API_KEY_ID:-}" || -z "${ASC_API_ISSUER_ID:-}" || -z "${ASC_API_KEY_PATH:-}" ]]; then
    die "Missing ASC API key env. Set ASC_API_KEY_JSON or (ASC_API_KEY_ID, ASC_API_ISSUER_ID, ASC_API_KEY_PATH)"
  fi
fi

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
