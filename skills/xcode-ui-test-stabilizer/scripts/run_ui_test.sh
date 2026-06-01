#!/usr/bin/env bash
set -euo pipefail

TEST_NAME="${TEST_NAME:-${1:-}}"
PROJECT="${PROJECT:-${2:-}}"
SCHEME="${SCHEME:-${3:-}}"
DESTINATION="${DESTINATION:-${4:-platform=macOS}}"
ENV_FILE="${ENV_FILE:-.env}"

if [[ -f "$ENV_FILE" ]]; then
  set -a
  # shellcheck disable=SC1090
  source "$ENV_FILE"
  set +a
fi

if [[ -z "$PROJECT" || -z "$SCHEME" ]]; then
  echo "Usage: PROJECT=MyApp.xcodeproj SCHEME=MyApp [TEST_NAME=...] [DESTINATION=...] [ENV_FILE=...] ./scripts/run_ui_test.sh" >&2
  exit 2
fi

ARGS=(test -project "$PROJECT" -scheme "$SCHEME" -destination "$DESTINATION")
if [[ -n "$TEST_NAME" ]]; then
  ARGS+=("-only-testing:${TEST_NAME}")
fi

exec xcodebuild "${ARGS[@]}"
