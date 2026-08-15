#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
installer="$script_dir/../install-deps.sh"
fixture_root="$(mktemp -d)"
trap 'rm -rf "$fixture_root"' EXIT

run_case() {
  local name="$1"
  shift
  local output="$fixture_root/$name.out"

  "$installer" "$@" >"$output"
  grep -F "Done. Run ./scripts/doctor.sh" "$output" >/dev/null
}

# Each case exercises an array while it is empty under `set -u`. Apple Bash
# 3.2 treats an unguarded "${array[@]}" expansion as an unbound variable.
run_case first-profile --profile mcp --dry-run
grep -Fx "Selected profiles: mcp" "$fixture_root/first-profile.out" >/dev/null

run_case no-skips --profile mcp --dry-run
grep -F "== node ==" "$fixture_root/no-skips.out" >/dev/null

run_case first-request --profile core --dry-run
grep -F "== xcode ==" "$fixture_root/first-request.out" >/dev/null

run_case no-requests --profile mcp --skip node --dry-run
grep -Fx "Skipped tools: node" "$fixture_root/no-requests.out" >/dev/null
if grep -F "== node ==" "$fixture_root/no-requests.out" >/dev/null; then
  echo "Skipped node was still requested" >&2
  exit 1
fi

echo "install-deps tests passed"
