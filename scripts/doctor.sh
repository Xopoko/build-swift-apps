#!/usr/bin/env bash
set -euo pipefail

missing_required=0
missing_optional=0
selected_profiles=()
strict=false
seen_checks="|"

usage() {
  cat <<'USAGE'
Usage: doctor.sh [--profile NAME] [--all] [--strict]

Checks host tools used by the Build Swift Apps plugin.

Profiles:
  core         Xcode, SwiftPM, simulator, signing, logging, Python helpers
  mcp          Node/npm/npx for bundled MCP servers and browser-preview helpers
  github       GitHub CLI workflows
  tuist        Tuist-generated project workflows
  app-store    App Store Connect, packaging, notarization, signing
  screenshots  Store screenshot capture/generation tools, AXe, and Node dependencies
  performance  ETTrace and build-performance tooling
  firmware     ipsw firmware analysis
  simulator    RocketSim app, bundled CLI, and serve-sim browser mirror prerequisites
  all          All profiles

Options:
  --profile NAME   Add a profile to check. Can be repeated.
  --all            Check every profile.
  --strict         Exit non-zero when required tools are missing.
  -h, --help       Show this help.
USAGE
}

contains_profile() {
  local needle="$1"
  local item
  for item in "${selected_profiles[@]}"; do
    [[ "$item" == "$needle" ]] && return 0
  done
  return 1
}

add_profile() {
  local profile="$1"
  if [[ "$profile" == "all" ]]; then
    add_profile core
    add_profile mcp
    add_profile github
    add_profile tuist
    add_profile app-store
    add_profile screenshots
    add_profile performance
    add_profile firmware
    add_profile simulator
    return
  fi

  case "$profile" in
    core|mcp|github|tuist|app-store|screenshots|performance|firmware|simulator) ;;
    *)
      echo "Unknown profile: $profile" >&2
      usage >&2
      exit 2
      ;;
  esac

  if ! contains_profile "$profile"; then
    selected_profiles+=("$profile")
  fi
}

already_checked() {
  local key="$1"
  case "$seen_checks" in
    *"|$key|"*) return 0 ;;
  esac
  seen_checks="${seen_checks}${key}|"
  return 1
}

result_ok() {
  printf '  [ok]      %-18s %s\n' "$1" "$2"
}

result_missing() {
  local level="$1"
  local name="$2"
  local hint="$3"
  printf '  [missing] %-18s %s\n' "$name" "$hint"
  if [[ "$level" == "required" ]]; then
    missing_required=$((missing_required + 1))
  else
    missing_optional=$((missing_optional + 1))
  fi
}

check_command() {
  local name="$1"
  local level="$2"
  local hint="$3"

  already_checked "cmd:$name" && return

  if command -v "$name" >/dev/null 2>&1; then
    result_ok "$name" "$(command -v "$name")"
  else
    result_missing "$level" "$name" "$hint"
  fi
}

check_executable() {
  local name="$1"
  local path="$2"
  local level="$3"
  local hint="$4"

  already_checked "exe:$path" && return

  if [[ -x "$path" ]]; then
    result_ok "$name" "$path"
  elif command -v "$name" >/dev/null 2>&1; then
    result_ok "$name" "$(command -v "$name")"
  else
    result_missing "$level" "$name" "$hint"
  fi
}

check_xcode_select() {
  already_checked "xcode-select" && return

  if command -v xcode-select >/dev/null 2>&1 && xcode-select -p >/dev/null 2>&1; then
    result_ok "xcode-select" "$(xcode-select -p)"
  else
    result_missing required "xcode-select" "Install Xcode or run: xcode-select --install"
  fi
}

check_xcrun_tool() {
  local tool="$1"
  local level="$2"
  local hint="$3"

  already_checked "xcrun-tool:$tool" && return

  if command -v xcrun >/dev/null 2>&1 && xcrun -f "$tool" >/dev/null 2>&1; then
    result_ok "$tool" "$(xcrun -f "$tool")"
  else
    result_missing "$level" "$tool" "$hint"
  fi
}

check_rocketsim() {
  already_checked "rocketsim-app" && return

  local running_app=""
  local pid=""
  pid="$(pgrep -x RocketSim 2>/dev/null | head -1 || true)"
  if [[ -n "$pid" ]]; then
    running_app="$(ps -o command= -p "$pid" 2>/dev/null | sed 's#/Contents/MacOS/RocketSim$##' || true)"
  fi

  local candidates=()
  [[ -n "$running_app" ]] && candidates+=("$running_app")
  candidates+=(
    "/Applications/RocketSim.app"
    "/Applications/RocketSim 2.app"
    "$HOME/Applications/RocketSim.app"
    "$HOME/Applications/RocketSim 2.app"
  )

  local app
  for app in "${candidates[@]}"; do
    if [[ -f "$app/Contents/Resources/Agent-Skill/SKILL.md" && -x "$app/Contents/Helpers/rocketsim" ]]; then
      result_ok "RocketSim" "$app"
      return
    fi
  done

  result_missing optional "RocketSim" "Install RocketSim.app with bundled Agent Skill and CLI for RocketSim workflows."
}

check_screenshot_deps() {
  already_checked "screenshot-deps" && return

  local scripts_dir
  scripts_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)/skills/appstore-screenshot-studio/scripts"
  if [[ ! -f "$scripts_dir/package.json" ]]; then
    result_missing optional "screenshot deps" "Missing $scripts_dir/package.json"
    return
  fi

  if command -v npm >/dev/null 2>&1 && npm list --prefix "$scripts_dir" sharp >/dev/null 2>&1; then
    result_ok "screenshot deps" "$scripts_dir/node_modules"
  else
    result_missing optional "screenshot deps" "Run: npm install --prefix $scripts_dir"
  fi
}

check_profile() {
  local profile="$1"
  printf '\n== %s ==\n' "$profile"

  case "$profile" in
    core)
      check_xcode_select
      check_command xcodebuild required "Install Xcode and select it with xcode-select."
      check_command xcrun required "Install Xcode or Command Line Tools."
      check_command swift required "Install Xcode or Swift toolchain."
      check_command git required "Install Xcode Command Line Tools or Homebrew git."
      check_command python3 required "Install Python 3, for example: brew install python."
      check_command lldb optional "Install Xcode for debugger workflows."
      check_executable log /usr/bin/log optional "macOS unified logging tool should exist at /usr/bin/log."
      check_executable codesign /usr/bin/codesign optional "Install Xcode or Command Line Tools."
      check_executable security /usr/bin/security optional "macOS keychain tool should exist at /usr/bin/security."
      check_executable plutil /usr/bin/plutil optional "macOS plist tool should exist at /usr/bin/plutil."
      check_executable sips /usr/bin/sips required "macOS image utility should exist at /usr/bin/sips."
      check_executable iconutil /usr/bin/iconutil required "macOS icon utility should exist at /usr/bin/iconutil."
      check_executable spctl /usr/sbin/spctl optional "macOS Gatekeeper tool should exist at /usr/sbin/spctl."
      ;;
    mcp)
      check_command node required "Install Node.js, for example: brew install node."
      check_command npm required "Install Node.js, for example: brew install node."
      check_command npx required "Install Node.js, for example: brew install node."
      ;;
    github)
      check_command gh optional "Install GitHub CLI: brew install gh."
      ;;
    tuist)
      check_command mise optional "Install mise: brew install mise."
      check_command tuist optional "Install with mise: mise use -g tuist@latest."
      ;;
    app-store)
      check_command asc optional "Install App Store Connect CLI: brew install asc. Configure with: asc auth login --key-id ... --issuer-id ... --private-key /path/to/AuthKey.p8"
      check_xcrun_tool notarytool optional "Install full Xcode for notarization workflows."
      check_xcrun_tool stapler optional "Install full Xcode for notarization workflows."
      check_executable codesign /usr/bin/codesign optional "Install Xcode or Command Line Tools."
      check_executable security /usr/bin/security optional "macOS keychain tool should exist at /usr/bin/security."
      check_executable plutil /usr/bin/plutil optional "macOS plist tool should exist at /usr/bin/plutil."
      check_executable spctl /usr/sbin/spctl optional "macOS Gatekeeper tool should exist at /usr/sbin/spctl."
      ;;
    screenshots)
      check_command axe required "Install AXe for asc screenshots capture/run: brew install cameroncooke/axe/axe."
      check_command node required "Install Node.js, for example: brew install node."
      check_command npm required "Install Node.js, for example: brew install node."
      check_screenshot_deps
      ;;
    performance)
      check_command ettrace optional "Install ETTrace runner: brew install emergetools/homebrew-tap/ettrace."
      check_command python3 required "Install Python 3, for example: brew install python."
      check_command xcodebuild required "Install Xcode and select it with xcode-select."
      check_command xcrun required "Install Xcode or Command Line Tools."
      check_command dwarfdump optional "Install Xcode or Command Line Tools."
      ;;
    firmware)
      check_command ipsw optional "Install ipsw: brew install blacktop/tap/ipsw."
      ;;
    simulator)
      check_rocketsim
      check_command xcrun required "Install Xcode or Command Line Tools."
      check_command node required "Install Node.js, for example: brew install node."
      check_command npx required "Install Node.js, for example: brew install node."
      ;;
  esac
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --profile)
      if [[ -z "${2:-}" ]]; then
        echo "--profile requires a value" >&2
        exit 2
      fi
      add_profile "$2"
      shift 2
      ;;
    --all)
      add_profile all
      shift
      ;;
    --strict)
      strict=true
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

if [[ ${#selected_profiles[@]} -eq 0 ]]; then
  add_profile core
fi

echo "Build Swift Apps environment check"
for profile in "${selected_profiles[@]}"; do
  check_profile "$profile"
done

printf '\nSummary: %d required missing, %d optional missing\n' "$missing_required" "$missing_optional"

if [[ "$strict" == true && "$missing_required" -gt 0 ]]; then
  exit 1
fi

exit 0
