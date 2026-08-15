#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
doctor="$script_dir/../doctor.sh"

single_output="$(bash "$doctor" --profile github)"
grep -Fx "== github ==" <<<"$single_output" >/dev/null
grep -F "Summary:" <<<"$single_output" >/dev/null

duplicate_output="$(bash "$doctor" --profile github --profile github)"
[[ "$(grep -Fc "== github ==" <<<"$duplicate_output")" -eq 1 ]]

if bash "$doctor" --profile unknown >/dev/null 2>&1; then
  echo "unknown profile unexpectedly succeeded" >&2
  exit 1
else
  status=$?
  [[ "$status" -eq 2 ]]
fi

echo "doctor tests passed"
