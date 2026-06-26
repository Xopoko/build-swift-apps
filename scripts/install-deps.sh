#!/usr/bin/env bash
set -euo pipefail

selected_profiles=()
requested_tools=()
skipped_tools=()
dry_run=false
assume_yes=false
no_brew=false
repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"

usage() {
  cat <<'USAGE'
Usage: install-deps.sh [--profile NAME] [--all] [options]

Installs optional host tools used by the Build Swift Apps plugin, or prints
manual setup instructions for tools that cannot be installed safely.

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
  --profile NAME   Add a profile. Can be repeated.
  --all            Install/check every profile.
  --skip TOOL      Skip a tool. Can be repeated. Examples: gh, node, asc, axe.
  --dry-run        Print actions without running installers.
  --yes            Do not prompt before installable actions.
  --no-brew        Do not use Homebrew. Print manual instructions instead.
  --list-profiles  Print profiles and exit.
  -h, --help       Show this help.
USAGE
}

list_profiles() {
  sed -n '/^Profiles:/,/^$/p' "$0" | sed '1d'
}

contains() {
  local needle="$1"
  shift
  local item
  for item in "$@"; do
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

  if ! contains "$profile" "${selected_profiles[@]}"; then
    selected_profiles+=("$profile")
  fi
}

skip_tool() {
  local tool="$1"
  skipped_tools+=("$tool")
}

is_skipped() {
  local tool="$1"
  contains "$tool" "${skipped_tools[@]}"
}

request_tool() {
  local tool="$1"
  if is_skipped "$tool"; then
    return
  fi
  if ! contains "$tool" "${requested_tools[@]}"; then
    requested_tools+=("$tool")
  fi
}

request_profile_tools() {
  local profile="$1"
  case "$profile" in
    core)
      request_tool xcode
      request_tool git
      request_tool python3
      ;;
    mcp)
      request_tool node
      ;;
    github)
      request_tool gh
      ;;
    tuist)
      request_tool tuist
      ;;
    app-store)
      request_tool xcode
      request_tool asc
      ;;
    screenshots)
      request_tool axe
      request_tool node
      request_tool screenshot-deps
      ;;
    performance)
      request_tool xcode
      request_tool python3
      request_tool ettrace
      ;;
    firmware)
      request_tool ipsw
      ;;
    simulator)
      request_tool xcode
      request_tool node
      request_tool rocketsim
      ;;
  esac
}

run_or_print() {
  printf '+ %s\n' "$*"
  if [[ "$dry_run" == false ]]; then
    "$@"
  fi
}

confirm() {
  local prompt="$1"
  if [[ "$assume_yes" == true ]]; then
    return 0
  fi
  if [[ ! -t 0 ]]; then
    echo "Skipping because stdin is not interactive. Re-run with --yes to install: $prompt" >&2
    return 1
  fi
  local answer
  read -r -p "$prompt [y/N] " answer
  case "$answer" in
    y|Y|yes|YES|Yes) return 0 ;;
    *) return 1 ;;
  esac
}

have_brew() {
  command -v brew >/dev/null 2>&1
}

brew_install() {
  local package="$1"
  local reason="$2"

  if [[ "$no_brew" == true ]]; then
    echo "Manual: install $package. Reason: $reason"
    return
  fi

  if [[ "$dry_run" == true ]]; then
    run_or_print brew install "$package"
    return
  fi

  if ! have_brew; then
    echo "Homebrew is not installed. Install $package manually or install Homebrew first: https://brew.sh"
    return
  fi

  if confirm "Install $package with Homebrew for $reason?"; then
    run_or_print brew install "$package"
  else
    echo "Skipped $package"
  fi
}

require_manual() {
  local name="$1"
  local message="$2"
  echo "Manual setup required for $name: $message"
}

install_xcode() {
  local ok=true
  command -v xcodebuild >/dev/null 2>&1 || ok=false
  command -v xcrun >/dev/null 2>&1 || ok=false
  command -v swift >/dev/null 2>&1 || ok=false
  command -v sips >/dev/null 2>&1 || ok=false
  command -v iconutil >/dev/null 2>&1 || ok=false

  if [[ "$ok" == true ]]; then
    echo "Xcode tools already available."
    return
  fi

  require_manual xcode "Install Xcode or run xcode-select --install, then select Xcode with sudo xcode-select -s /Applications/Xcode.app/Contents/Developer when needed. macOS system tools sips and iconutil are also required for app icon export."
}

install_git() {
  if command -v git >/dev/null 2>&1; then
    echo "git already available."
    return
  fi
  brew_install git "repository cloning, SPM pin checks, and update flows"
}

install_python3() {
  if command -v python3 >/dev/null 2>&1; then
    echo "python3 already available."
    return
  fi
  brew_install python "plugin helper scripts"
}

install_node() {
  if command -v node >/dev/null 2>&1 && command -v npm >/dev/null 2>&1 && command -v npx >/dev/null 2>&1; then
    echo "node/npm/npx already available."
    return
  fi
  brew_install node "bundled MCP servers"
}

install_gh() {
  if command -v gh >/dev/null 2>&1; then
    echo "gh already available."
    return
  fi
  brew_install gh "GitHub workflows"
}

install_tuist() {
  if command -v tuist >/dev/null 2>&1; then
    echo "tuist already available."
    return
  fi

  if [[ "$dry_run" == true ]]; then
    if ! command -v mise >/dev/null 2>&1; then
      run_or_print brew install mise
    fi
    run_or_print mise use -g tuist@latest
    return
  fi

  if ! command -v mise >/dev/null 2>&1; then
    brew_install mise "Tuist version management"
  fi

  if command -v mise >/dev/null 2>&1; then
    if confirm "Install tuist@latest globally through mise?"; then
      run_or_print mise use -g tuist@latest
    else
      echo "Skipped tuist@latest"
    fi
  else
    require_manual tuist "Install mise, then run: mise use -g tuist@latest"
  fi
}

install_asc() {
  if command -v asc >/dev/null 2>&1; then
    echo "asc already available."
    return
  fi
  brew_install asc "App Store Connect CLI workflows. Configure with: asc auth login --key-id ... --issuer-id ... --private-key /path/to/AuthKey.p8"
}

install_axe() {
  if command -v axe >/dev/null 2>&1; then
    echo "axe already available."
    return
  fi
  brew_install cameroncooke/axe/axe "AXe iOS Simulator accessibility/HID automation used by asc screenshots capture/run"
}

install_screenshot_deps() {
  local scripts_dirs=()
  local seen="|"
  local candidate

  for candidate in \
    "$repo_root/skills/appstore-screenshot-studio/scripts" \
    "$HOME/.agents/plugins/plugins/build-swift-apps/skills/appstore-screenshot-studio/scripts" \
    "$HOME"/.codex/plugins/cache/local/build-swift-apps/*/skills/appstore-screenshot-studio/scripts \
    "$HOME"/.claude/plugins/cache/build-swift-apps/build-swift-apps/*/skills/appstore-screenshot-studio/scripts \
    "$HOME/.claude/plugins/marketplaces/build-swift-apps/skills/appstore-screenshot-studio/scripts"; do
    if [[ -f "$candidate/package.json" && "$seen" != *"|$candidate|"* ]]; then
      scripts_dirs+=("$candidate")
      seen+="$candidate|"
    fi
  done

  if [[ ${#scripts_dirs[@]} -eq 0 ]]; then
    require_manual screenshot-deps "Missing bundled screenshot package.json. Expected skills/appstore-screenshot-studio/scripts/package.json in a plugin checkout or runtime cache."
    return
  fi

  if [[ "$dry_run" == true ]]; then
    for candidate in "${scripts_dirs[@]}"; do
      run_or_print npm install --prefix "$candidate"
    done
    return
  fi

  if ! command -v npm >/dev/null 2>&1; then
    require_manual npm "Install Node.js first, then rerun: $0 --profile screenshots"
    return
  fi

  for candidate in "${scripts_dirs[@]}"; do
    if npm list --prefix "$candidate" sharp >/dev/null 2>&1; then
      echo "Screenshot Studio Node dependencies already available: $candidate"
      continue
    fi

    if confirm "Install bundled Screenshot Studio Node dependencies with npm at $candidate?"; then
      run_or_print npm install --prefix "$candidate"
    else
      echo "Skipped Screenshot Studio Node dependencies at $candidate"
    fi
  done
}

install_ettrace() {
  if command -v ettrace >/dev/null 2>&1; then
    echo "ettrace already available."
    return
  fi
  brew_install emergetools/homebrew-tap/ettrace "iOS simulator ETTrace profiling"
}

install_ipsw() {
  if command -v ipsw >/dev/null 2>&1; then
    echo "ipsw already available."
    return
  fi
  brew_install blacktop/tap/ipsw "Apple firmware and binary analysis"
}

install_rocketsim() {
  local candidates=(
    "/Applications/RocketSim.app"
    "/Applications/RocketSim 2.app"
    "$HOME/Applications/RocketSim.app"
    "$HOME/Applications/RocketSim 2.app"
  )
  local app
  for app in "${candidates[@]}"; do
    if [[ -f "$app/Contents/Resources/Agent-Skill/SKILL.md" && -x "$app/Contents/Helpers/rocketsim" ]]; then
      echo "RocketSim already available at $app."
      return
    fi
  done

  require_manual RocketSim "Install a current RocketSim.app build that includes Contents/Resources/Agent-Skill/SKILL.md and Contents/Helpers/rocketsim."
}

install_tool() {
  local tool="$1"
  if is_skipped "$tool"; then
    echo "Skipped $tool"
    return
  fi

  case "$tool" in
    xcode) install_xcode ;;
    git) install_git ;;
    python3) install_python3 ;;
    node) install_node ;;
    gh) install_gh ;;
    tuist) install_tuist ;;
    asc) install_asc ;;
    axe) install_axe ;;
    screenshot-deps) install_screenshot_deps ;;
    ettrace) install_ettrace ;;
    ipsw) install_ipsw ;;
    rocketsim) install_rocketsim ;;
    *)
      echo "Unknown tool: $tool" >&2
      return 2
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
    --skip)
      if [[ -z "${2:-}" ]]; then
        echo "--skip requires a value" >&2
        exit 2
      fi
      skip_tool "$2"
      shift 2
      ;;
    --dry-run)
      dry_run=true
      shift
      ;;
    --yes)
      assume_yes=true
      shift
      ;;
    --no-brew)
      no_brew=true
      shift
      ;;
    --list-profiles)
      list_profiles
      exit 0
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
  add_profile mcp
fi

for profile in "${selected_profiles[@]}"; do
  request_profile_tools "$profile"
done

echo "Selected profiles: ${selected_profiles[*]}"
if [[ ${#skipped_tools[@]} -gt 0 ]]; then
  echo "Skipped tools: ${skipped_tools[*]}"
fi

for tool in "${requested_tools[@]}"; do
  printf '\n== %s ==\n' "$tool"
  install_tool "$tool"
done

printf '\nDone. Run ./scripts/doctor.sh'
for profile in "${selected_profiles[@]}"; do
  printf ' --profile %s' "$profile"
done
printf ' to verify.\n'
