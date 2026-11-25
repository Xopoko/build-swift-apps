#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
installer="$script_dir/../install-local-plugin.sh"
real_python3="$(python3 -c 'import sys; print(sys.executable)')"

run_case() {
  local mode="$1"
  local fixture_root="$2"
  local checkout_state="${3:-existing}"
  local fake_bin="$fixture_root/bin"
  local test_home="$fixture_root/home"
  local marketplace_root="$test_home"
  local plugin_dir="$marketplace_root/.agents/plugins/plugins/build-swift-apps"
  local call_log="$fixture_root/codex-calls.log"
  local git_call_log="$fixture_root/git-calls.log"
  local output="$fixture_root/install.out"
  local run_path="$fake_bin:/usr/bin:/bin"
  local installer_args=(--marketplace-name fixture --skip-deps)
  local install_status

  if [[ "$checkout_state" == "custom" ]]; then
    marketplace_root="$fixture_root/Team Marketplace"
    plugin_dir="$marketplace_root/checkouts/swift plugin"
    installer_args+=(
      --plugin-dir "$plugin_dir"
      --marketplace-file "$marketplace_root/.agents/plugins/marketplace.json"
    )
  fi

  mkdir -p "$fake_bin"
  if [[ "$checkout_state" != "clean" ]]; then
    mkdir -p "$plugin_dir/.git"
  else
    mkdir -p "$(dirname "$plugin_dir")"
  fi

  cat >"$fake_bin/git" <<'SH'
#!/usr/bin/env bash
set -eu
printf '%s\n' "$*" >>"$GIT_TEST_CALL_LOG"
if [[ "${1:-}" == "clone" ]]; then
  target="${!#}"
  mkdir -p "$target/.git"
fi
SH

  if [[ "$mode" != "no-codex" ]]; then
    cat >"$fake_bin/codex" <<'SH'
#!/usr/bin/env bash
set -eu
printf '%s\n' "$*" >>"$CODEX_TEST_CALL_LOG"
if [[ "$CODEX_TEST_MODE" == "legacy" && "$*" == "plugin add --help" ]]; then
  exit 2
fi
if [[ "$*" == plugin\ add\ *@*\ --json ]]; then
  if [[ "$CODEX_TEST_MODE" == "install-failure" ]]; then
    exit 9
  fi
  printf '{"installed":true}\n'
fi
SH
  fi

  cat >"$fake_bin/python3" <<SH
#!/usr/bin/env bash
exec "$real_python3" "\$@"
SH

  chmod +x "$fake_bin/git" "$fake_bin/python3"
  if [[ "$mode" != "no-codex" ]]; then
    chmod +x "$fake_bin/codex"
  else
    local tool
    for tool in bash dirname mkdir; do
      ln -s "$(command -v "$tool")" "$fake_bin/$tool"
    done
    run_path="$fake_bin"
  fi

  if HOME="$test_home" \
    PATH="$run_path" \
    CODEX_TEST_CALL_LOG="$call_log" \
    CODEX_TEST_MODE="$mode" \
    GIT_TEST_CALL_LOG="$git_call_log" \
      "$installer" "${installer_args[@]}" >"$output"; then
    install_status=0
  else
    install_status=$?
  fi

  if [[ "$checkout_state" == "clean" ]]; then
    grep -Fx "clone https://github.com/Xopoko/build-swift-apps.git $plugin_dir" "$git_call_log" >/dev/null
  fi

  python3 - "$marketplace_root" "$plugin_dir" <<'PY'
import json
import sys
from pathlib import Path

root, checkout = map(Path, sys.argv[1:])
marketplace = json.loads((root / ".agents/plugins/marketplace.json").read_text())
assert marketplace["name"] == "fixture"
source = marketplace["plugins"][0]["source"]["path"]
assert source.startswith("./"), source
assert (root / source).resolve() == checkout.resolve(), source
PY
  [[ ! -L "$marketplace_root/plugins/build-swift-apps" ]]

  if [[ "$mode" == "no-codex" ]]; then
    [[ "$install_status" -eq 0 ]]
    grep -Fx "  codex plugin marketplace add $test_home" "$output" >/dev/null
    grep -Fx "  codex plugin add build-swift-apps@fixture" "$output" >/dev/null
    grep -F '[plugins."build-swift-apps@fixture"]' "$output" >/dev/null
    [[ ! -e "$test_home/.codex/config.toml" ]]
    return
  fi

  grep -Fx "plugin marketplace add $marketplace_root" "$call_log" >/dev/null
  grep -Fx "plugin add --help" "$call_log" >/dev/null

  if [[ "$mode" == "install-failure" ]]; then
    [[ "$install_status" -eq 9 ]]
    grep -Fx "plugin add build-swift-apps@fixture --json" "$call_log" >/dev/null
    [[ ! -e "$test_home/.codex/config.toml" ]]
  elif [[ "$mode" == "current" ]]; then
    [[ "$install_status" -eq 0 ]]
    grep -Fx "plugin add build-swift-apps@fixture --json" "$call_log" >/dev/null
    [[ ! -e "$test_home/.codex/config.toml" ]]
  else
    [[ "$install_status" -eq 0 ]]
    if grep -Fx "plugin add build-swift-apps@fixture --json" "$call_log" >/dev/null; then
      echo "legacy fallback unexpectedly invoked plugin add" >&2
      return 1
    fi
    grep -F '[plugins."build-swift-apps@fixture"]' "$test_home/.codex/config.toml" >/dev/null
    grep -Fx 'enabled = true' "$test_home/.codex/config.toml" >/dev/null
  fi
}

test_root="$(mktemp -d)"
test_root="$(cd "$test_root" && pwd -P)"
trap 'rm -rf "$test_root"' EXIT

run_case current "$test_root/current"
run_case current "$test_root/clean" clean
run_case current "$test_root/custom" custom
run_case legacy "$test_root/legacy"
run_case install-failure "$test_root/install-failure"
run_case no-codex "$test_root/no-codex"

echo "install-local-plugin tests passed"
