#!/usr/bin/env bash
set -euo pipefail

plugin_name="build-swift-apps"
repo_url="https://github.com/Xopoko/build-swift-apps.git"
marketplace_name="local"
marketplace_file="$HOME/.agents/plugins/marketplace.json"
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
plugin_dir="$HOME/.agents/plugins/plugins/build-swift-apps"
branch=""
skip_deps=false
skip_codex=false
assume_yes=false
deps_profiles=()

usage() {
  cat <<'USAGE'
Usage: install-local-plugin.sh [options]

Installs the Build Swift Apps plugin into the default personal Codex plugin
marketplace and optionally installs/checks host dependencies.

Options:
  --repo-url URL          Git repository URL to clone.
  --plugin-dir DIR        Local plugin checkout path under marketplace root.
  --branch NAME           Clone or update a specific branch.
  --marketplace-file FILE Path ending in .agents/plugins/marketplace.json.
  --marketplace-name NAME Marketplace name used in Codex config.
  --deps-profile NAME     Dependency profile to install. Can be repeated.
  --skip-deps             Do not run install-deps.sh.
  --skip-codex            Update marketplace only; do not register/enable in Codex.
  --yes                   Pass --yes to dependency installer.
  -h, --help              Show this help.

Default paths:
  plugin dir:       ~/.agents/plugins/plugins/build-swift-apps
  marketplace file: ~/.agents/plugins/marketplace.json
  Codex config:     build-swift-apps@local enabled
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo-url)
      repo_url="${2:-}"
      [[ -n "$repo_url" ]] || { echo "--repo-url requires a value" >&2; exit 2; }
      shift 2
      ;;
    --plugin-dir)
      plugin_dir="${2:-}"
      [[ -n "$plugin_dir" ]] || { echo "--plugin-dir requires a value" >&2; exit 2; }
      shift 2
      ;;
    --branch)
      branch="${2:-}"
      [[ -n "$branch" ]] || { echo "--branch requires a value" >&2; exit 2; }
      shift 2
      ;;
    --marketplace-file)
      marketplace_file="${2:-}"
      [[ -n "$marketplace_file" ]] || { echo "--marketplace-file requires a value" >&2; exit 2; }
      shift 2
      ;;
    --marketplace-name)
      marketplace_name="${2:-}"
      [[ -n "$marketplace_name" ]] || { echo "--marketplace-name requires a value" >&2; exit 2; }
      shift 2
      ;;
    --deps-profile)
      profile="${2:-}"
      [[ -n "$profile" ]] || { echo "--deps-profile requires a value" >&2; exit 2; }
      deps_profiles+=("$profile")
      shift 2
      ;;
    --skip-deps)
      skip_deps=true
      shift
      ;;
    --skip-codex)
      skip_codex=true
      shift
      ;;
    --yes)
      assume_yes=true
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

if [[ ${#deps_profiles[@]} -eq 0 ]]; then
  deps_profiles=(core mcp)
fi

if ! command -v git >/dev/null 2>&1; then
  echo "git is required to clone or update the plugin. Install Xcode Command Line Tools or Homebrew git first." >&2
  exit 1
fi

if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 is required to update marketplace.json. Install Python 3 first, then rerun this script." >&2
  exit 1
fi

resolve_path() {
  python3 -c 'from pathlib import Path; import sys; print(Path(sys.argv[1]).expanduser().resolve())' "$1"
}

marketplace_file="$(resolve_path "$marketplace_file")"
plugin_dir="$(resolve_path "$plugin_dir")"
case "$marketplace_file" in
  */.agents/plugins/marketplace.json) ;;
  *)
    echo "Marketplace file must be at <marketplace root>/.agents/plugins/marketplace.json: $marketplace_file" >&2
    exit 2
    ;;
esac

marketplace_root="${marketplace_file%/.agents/plugins/marketplace.json}"
marketplace_root="${marketplace_root:-/}"
marketplace_prefix="${marketplace_root%/}/"
if [[ "$plugin_dir" != "$marketplace_prefix"* || "$plugin_dir" == "$marketplace_root" ]]; then
  echo "Plugin checkout must be inside the marketplace root: $marketplace_root" >&2
  exit 2
fi

if [[ -e "$plugin_dir/.git" ]]; then
  if [[ "$plugin_dir" == "$(dirname "$script_dir")" && -z "$branch" ]]; then
    echo "Using current plugin checkout at $plugin_dir"
  else
    echo "Updating plugin checkout at $plugin_dir"
    if [[ -n "$branch" ]]; then
      git -C "$plugin_dir" fetch origin "$branch"
      git -C "$plugin_dir" checkout "$branch"
    fi
    git -C "$plugin_dir" pull --ff-only
  fi
elif [[ -e "$plugin_dir" ]]; then
  echo "Plugin path exists but is not a git checkout: $plugin_dir" >&2
  exit 1
else
  mkdir -p "$(dirname "$plugin_dir")"
  echo "Cloning $repo_url into $plugin_dir"
  if [[ -n "$branch" ]]; then
    git clone --branch "$branch" "$repo_url" "$plugin_dir"
  else
    git clone "$repo_url" "$plugin_dir"
  fi
fi

echo "Updating marketplace entry in $marketplace_file"
MARKETPLACE_FILE="$marketplace_file" \
MARKETPLACE_NAME="$marketplace_name" \
SOURCE_PATH="./${plugin_dir#"$marketplace_prefix"}" \
PLUGIN_NAME="$plugin_name" \
python3 - <<'PY'
from __future__ import annotations

import json
import os
from pathlib import Path

marketplace_file = Path(os.environ["MARKETPLACE_FILE"])
marketplace_name = os.environ["MARKETPLACE_NAME"]
source_path = os.environ["SOURCE_PATH"]
plugin_name = os.environ["PLUGIN_NAME"]

if marketplace_file.exists():
    data = json.loads(marketplace_file.read_text())
else:
    data = {}

data["name"] = marketplace_name
data.setdefault("interface", {}).setdefault("displayName", "Local Plugins")
plugins = data.setdefault("plugins", [])

entry = {
    "name": plugin_name,
    "source": {
        "source": "local",
        "path": source_path,
    },
    "policy": {
        "installation": "AVAILABLE",
        "authentication": "ON_INSTALL",
    },
    "category": "Coding",
}

for index, existing in enumerate(plugins):
    if existing.get("name") == plugin_name:
        plugins[index] = entry
        break
else:
    plugins.append(entry)

marketplace_file.parent.mkdir(parents=True, exist_ok=True)
marketplace_file.write_text(json.dumps(data, indent=2) + "\n")
print(f"{plugin_name}@{marketplace_name} -> {source_path}")
PY

plugin_id="$plugin_name@$marketplace_name"
if [[ "$skip_codex" == true ]]; then
  echo "Skipped Codex registration."
elif command -v codex >/dev/null 2>&1; then
  echo "Registering marketplace in Codex"
  codex plugin marketplace add "$marketplace_root"

  if codex plugin add --help >/dev/null 2>&1; then
    echo "Installing $plugin_id with Codex CLI"
    codex plugin add "$plugin_id" --json
    echo "Start a new Codex thread before using newly installed skills."
  else
    echo "Codex CLI has no 'plugin add' command; enabling $plugin_id in config as a legacy fallback"
    CODEX_CONFIG_FILE="$HOME/.codex/config.toml" \
    PLUGIN_ID="$plugin_id" \
    python3 - <<'PY'
from __future__ import annotations

import os
import re
from pathlib import Path

config_file = Path(os.environ["CODEX_CONFIG_FILE"]).expanduser()
plugin_id = os.environ["PLUGIN_ID"]
section = f'[plugins."{plugin_id}"]\nenabled = true\n'

config_file.parent.mkdir(parents=True, exist_ok=True)
text = config_file.read_text() if config_file.exists() else ""

pattern = re.compile(
    rf'(?ms)^\[plugins\."{re.escape(plugin_id)}"\]\n.*?(?=^\[|\Z)'
)

if pattern.search(text):
    text = pattern.sub(section + "\n", text)
else:
    if text and not text.endswith("\n"):
        text += "\n"
    if text and not text.endswith("\n\n"):
        text += "\n"
    text += section

config_file.write_text(text)
print(f"{plugin_id} enabled in {config_file}")
PY
    echo "Start a new Codex thread before using newly enabled skills."
  fi
else
  echo "Codex CLI not found. Run this after installing Codex CLI:"
  printf '  codex plugin marketplace add %q\n' "$marketplace_root"
  printf '  codex plugin add %q\n' "$plugin_id"
  echo "For a legacy Codex CLI without 'plugin add', enable [plugins.\"$plugin_id\"] in ~/.codex/config.toml."
fi

if [[ "$skip_deps" == false ]]; then
  deps_args=()
  for profile in "${deps_profiles[@]}"; do
    deps_args+=(--profile "$profile")
  done
  if [[ "$assume_yes" == true ]]; then
    deps_args+=(--yes)
  fi
  echo "Checking/installing dependency profiles: ${deps_profiles[*]}"
  "$plugin_dir/scripts/install-deps.sh" "${deps_args[@]}"
else
  echo "Skipped dependency installer."
fi
