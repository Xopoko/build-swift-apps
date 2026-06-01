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
  --repo-url URL          Git repository URL to clone or update.
  --plugin-dir DIR        Local plugin checkout path under marketplace root.
  --branch NAME           Clone or update a specific branch.
  --marketplace-file FILE Marketplace JSON path.
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

mkdir -p "$(dirname "$plugin_dir")" "$(dirname "$marketplace_file")"

if [[ -d "$plugin_dir/.git" ]]; then
  current_checkout="$(cd "$script_dir/.." && pwd -P)"
  selected_checkout="$(cd "$plugin_dir" && pwd -P)"
  if [[ "$selected_checkout" == "$current_checkout" && -z "$branch" ]]; then
    echo "Using current plugin checkout at $plugin_dir"
  else
    echo "Updating plugin checkout at $plugin_dir"
  fi
  if [[ -n "$branch" ]]; then
    git -C "$plugin_dir" fetch origin "$branch"
    git -C "$plugin_dir" checkout "$branch"
  fi
  if [[ "$selected_checkout" != "$current_checkout" || -n "$branch" ]]; then
    git -C "$plugin_dir" pull --ff-only
  fi
elif [[ -e "$plugin_dir" ]]; then
  echo "Plugin path exists but is not a git checkout: $plugin_dir" >&2
  exit 1
else
  echo "Cloning $repo_url into $plugin_dir"
  clone_args=()
  if [[ -n "$branch" ]]; then
    clone_args+=(--branch "$branch")
  fi
  git clone "${clone_args[@]}" "$repo_url" "$plugin_dir"
fi

codex_marketplace_root="$(cd "$(dirname "$marketplace_file")/../.." && pwd -P)"
codex_plugin_link="$codex_marketplace_root/plugins/$plugin_name"
if [[ "$(cd "$(dirname "$plugin_dir")" && pwd -P)" != "$codex_marketplace_root/plugins" ]]; then
  mkdir -p "$(dirname "$codex_plugin_link")"
  if [[ -L "$codex_plugin_link" ]]; then
    current_link="$(readlink "$codex_plugin_link")"
    if [[ "$current_link" != "$plugin_dir" ]]; then
      ln -sfn "$plugin_dir" "$codex_plugin_link"
    fi
  elif [[ -e "$codex_plugin_link" ]]; then
    echo "Codex plugin path exists and is not a symlink: $codex_plugin_link" >&2
    echo "Move it aside or pass --plugin-dir inside $codex_marketplace_root/plugins." >&2
    exit 1
  else
    ln -s "$plugin_dir" "$codex_plugin_link"
  fi
fi

echo "Updating marketplace entry in $marketplace_file"
MARKETPLACE_FILE="$marketplace_file" \
MARKETPLACE_NAME="$marketplace_name" \
PLUGIN_DIR="$plugin_dir" \
PLUGIN_NAME="$plugin_name" \
python3 - <<'PY'
from __future__ import annotations

import json
import os
from pathlib import Path

marketplace_file = Path(os.environ["MARKETPLACE_FILE"]).expanduser().resolve()
marketplace_name = os.environ["MARKETPLACE_NAME"]
plugin_dir = Path(os.environ["PLUGIN_DIR"]).expanduser().resolve()
plugin_name = os.environ["PLUGIN_NAME"]
marketplace_root = marketplace_file.parent

if marketplace_file.exists():
    data = json.loads(marketplace_file.read_text())
else:
    data = {}

try:
    rel_path = plugin_dir.relative_to(marketplace_root)
except ValueError as error:
    raise SystemExit(
        f"Plugin dir must be inside the marketplace root ({marketplace_root}) "
        "so marketplace source.path can stay relative."
    ) from error

source_path = f"./{rel_path.as_posix()}"

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

if [[ "$skip_codex" == true ]]; then
  echo "Skipped Codex registration."
elif command -v codex >/dev/null 2>&1; then
  echo "Registering marketplace in Codex"
  codex plugin marketplace add "$codex_marketplace_root"

  echo "Enabling $plugin_name@$marketplace_name in Codex config"
  CODEX_CONFIG_FILE="$HOME/.codex/config.toml" \
  PLUGIN_ID="$plugin_name@$marketplace_name" \
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
else
  echo "Codex CLI not found. Run this after installing Codex CLI:"
  echo "  codex plugin marketplace add $HOME"
  echo "Then enable [plugins.\"$plugin_name@$marketplace_name\"] in ~/.codex/config.toml."
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

echo "Done. Start a new Codex thread before using newly installed skills."
