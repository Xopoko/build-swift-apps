#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
cd "$repo_root"

echo "Checking JSON manifests"
json_files=(
  ".codex-plugin/plugin.json"
  ".mcp.json"
  ".claude-plugin/plugin.json"
  ".claude-plugin/marketplace.json"
  ".cursor-plugin/plugin.json"
  "package.json"
)

for file in "${json_files[@]}"; do
  python3 -m json.tool "$file" >/dev/null
done

echo "Checking shell scripts"
bash -n scripts/doctor.sh scripts/install-deps.sh scripts/install-local-plugin.sh scripts/validate-package.sh

echo "Checking skill frontmatter and multi-agent coverage"
python3 - <<'PY'
from __future__ import annotations

import json
import re
from pathlib import Path

root = Path(".")
skill_dirs = sorted(path.parent for path in root.glob("skills/*/SKILL.md"))
skill_names = [path.name for path in skill_dirs]

if not skill_names:
    raise SystemExit("No skills found.")

for skill_dir in skill_dirs:
    skill_file = skill_dir / "SKILL.md"
    text = skill_file.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise SystemExit(f"{skill_file} is missing YAML frontmatter.")
    frontmatter = text.split("---", 2)[1]
    name_match = re.search(r"^name:\s*['\"]?([^'\"\n]+)['\"]?\s*$", frontmatter, re.MULTILINE)
    desc_match = re.search(r"^description:\s*(.+)$", frontmatter, re.MULTILINE)
    if not name_match:
        raise SystemExit(f"{skill_file} is missing frontmatter name.")
    if name_match.group(1).strip() != skill_dir.name:
        raise SystemExit(f"{skill_file} name does not match directory {skill_dir.name}.")
    if not desc_match or len(desc_match.group(1).strip().strip('"')) < 24:
        raise SystemExit(f"{skill_file} needs a useful description.")

cursor = json.loads(Path(".cursor-plugin/plugin.json").read_text(encoding="utf-8"))
cursor_skills = sorted(Path(path).name for path in cursor.get("skills", []))
if cursor_skills != skill_names:
    raise SystemExit(".cursor-plugin/plugin.json skills are out of sync with skills/.")

package = json.loads(Path("package.json").read_text(encoding="utf-8"))
pi_skills = sorted(Path(path).name for path in package.get("pi", {}).get("skills", []))
if pi_skills != skill_names:
    raise SystemExit("package.json pi.skills are out of sync with skills/.")

readme = Path("README.md").read_text(encoding="utf-8")
missing_from_readme = [name for name in skill_names if f"`{name}`" not in readme]
if missing_from_readme:
    raise SystemExit(f"README.md is missing skills: {', '.join(missing_from_readme)}")
PY

echo "Checking for private or work-specific terms"
private_pattern="$(python3 - <<'PY'
terms = [
    "7765626c617465",
    "776c63746c",
    "6232636f7265",
    "623262726f6b6572",
    "62327472616e736c617465",
    "50414e2d",
    "6a697261",
    "6c6f63616c697a6174696f6e7353657276696365",
    "4c6f63616c697a6174696f6e426f6f747374726170",
    "61736363746c",
    "6f70656e6170692d636c69",
    "6f7065726174696f6e4964",
    "50726f6a656374732f576f726b",
    "2f55736572732f",
]
print("|".join(bytes.fromhex(term).decode("utf-8") for term in terms))
PY
)"
if rg -uu -n -i --glob '!**/.git/**' --glob '!**/node_modules/**' "$private_pattern" .; then
  echo "Private/work-specific term check failed." >&2
  exit 1
fi

echo "Package validation passed"
