#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
installer="$script_dir/../install-local-plugin.sh"
real_python3="$(command -v python3)"

run_case() {
  local mode="$1"
  local fixture_root="$2"
  local checkout_state="${3:-existing}"
  local fake_bin="$fixture_root/bin"
  local test_home="$fixture_root/home"
  local plugin_dir="$test_home/.agents/plugins/plugins/build-swift-apps"
  local call_log="$fixture_root/codex-calls.log"
  local git_call_log="$fixture_root/git-calls.log"

  mkdir -p "$fake_bin"
  if [[ "$checkout_state" == "existing" ]]; then
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

  cat >"$fake_bin/python3" <<SH
#!/usr/bin/env bash
exec "$real_python3" "\$@"
SH

  chmod +x "$fake_bin/git" "$fake_bin/codex" "$fake_bin/python3"

  if HOME="$test_home" \
    PATH="$fake_bin:$PATH" \
    CODEX_TEST_CALL_LOG="$call_log" \
    CODEX_TEST_MODE="$mode" \
    GIT_TEST_CALL_LOG="$git_call_log" \
      "$installer" --marketplace-name fixture --skip-deps >/dev/null; then
    install_status=0
  else
    install_status=$?
  fi

  grep -Fx "plugin marketplace add $test_home" "$call_log" >/dev/null
  grep -Fx "plugin add --help" "$call_log" >/dev/null
  if [[ "$checkout_state" == "clean" ]]; then
    grep -Fx "clone https://github.com/Xopoko/build-swift-apps.git $plugin_dir" "$git_call_log" >/dev/null
  fi

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

fixture_root="$(mktemp -d)"
trap 'rm -rf "$fixture_root"' EXIT

run_case current "$fixture_root/current"
run_case current "$fixture_root/clean" clean
run_case legacy "$fixture_root/legacy"
run_case install-failure "$fixture_root/install-failure"

echo "install-local-plugin tests passed"
