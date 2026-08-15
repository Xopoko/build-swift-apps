#!/usr/bin/env bash
# This script is pinned to LF by .gitattributes for portable POSIX execution.
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
cd "$repo_root"

echo "Checking JSON manifests"
json_files=(
  ".codex-plugin/plugin.json"
  ".mcp.json"
  ".claude-plugin/plugin.json"
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
repo_root = root.resolve()

code_reference_pattern = re.compile(
    r"`((?:(?:\.\.?/)+|references/|shared/)[^`\n]*?\.md(?:#[^`\n]*)?)`"
)
link_reference_pattern = re.compile(
    r"\]\((?![A-Za-z][A-Za-z0-9+.-]*:|#)([^)\n]*?\.md(?:#[^)\n]*)?)\)"
)
apple_command_pattern = re.compile(
    r"\b(?:xcodebuild|xcrun|simctl|codesign|notarytool|tuist)\b|"
    r"\bswift\s+(?:build|run|test)\b|\blog\s+stream\b|"
    r"\b(?:dwarfdump|mdfind|sips|iconutil|spctl|stapler|plutil|ettrace)\b|"
    r"\bsecurity\s+find-identity\b|RocketSim\.app|/usr/bin/open\b"
)
execution_locus_guard = (
    "Before invoking Apple-only binaries, confirm the execution context is macOS."
)


def relative_markdown_references(text: str) -> list[tuple[str, int]]:
    references: list[tuple[str, int]] = []
    for pattern in (code_reference_pattern, link_reference_pattern):
        for match in pattern.finditer(text):
            reference = match.group(1).strip().strip("<>")
            line = text.count("\n", 0, match.start()) + 1
            references.append((reference, line))
    return references

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

    has_execution_locus = (
        execution_locus_guard in text or "## Execution Locus" in text
    )
    if apple_command_pattern.search(text) and not has_execution_locus:
        raise SystemExit(
            f"{skill_file} invokes Apple-only tooling without an execution-locus guard."
        )

    for reference, line in relative_markdown_references(text):
        relative_path = reference.split("#", 1)[0]
        target = (skill_file.parent / relative_path).resolve()
        try:
            target.relative_to(repo_root)
        except ValueError:
            raise SystemExit(
                f"{skill_file}:{line} relative Markdown reference escapes the package: "
                f"{reference}"
            )
        if not target.is_file():
            raise SystemExit(
                f"{skill_file}:{line} has a broken relative Markdown reference: "
                f"{reference}"
            )

runtime_skill = Path("skills/macos-runtime-debugger/SKILL.md").read_text(encoding="utf-8")
runtime_reference = Path(
    "skills/macos-runtime-debugger/references/run-button-bootstrap.md"
).read_text(encoding="utf-8")
runtime_command = Path("commands/macos-runtime-debug.md").read_text(encoding="utf-8")
router_skill = Path("skills/build-swift-apps/SKILL.md").read_text(encoding="utf-8")
community_skill = Path("skills/apple-dev-research/SKILL.md").read_text(encoding="utf-8")
asc_skill = Path("skills/appstore-connect-cli/SKILL.md").read_text(encoding="utf-8")

for source, text in (
    ("macos-runtime-debugger", runtime_skill),
    ("run-button-bootstrap", runtime_reference),
    ("macos-runtime-debug command", runtime_command),
):
    if re.search(r"\bgit init\b", text):
        raise SystemExit(f"{source} must not initialize source control for runtime work.")

if "/macos-runtime-debug" not in runtime_skill or "one-shot" not in runtime_skill:
    raise SystemExit(
        "macos-runtime-debugger must preserve one-shot execution and explicit bootstrap routing."
    )
if "explicitly requests" not in runtime_reference:
    raise SystemExit("run-button-bootstrap must remain opt-in or evidence-triggered.")
if "Explicitly bootstrap" not in runtime_command or "run_action" not in runtime_command:
    raise SystemExit("macos-runtime-debug command must remain an explicit bootstrap surface.")

if "official Apple documentation" not in router_skill or "only for community" not in router_skill:
    raise SystemExit("build-swift-apps router must separate official docs from community research.")
if "not official docs" not in community_skill:
    raise SystemExit("apple-dev-research must remain community-only.")

for routed_skill in ("appstore-connect-cli", "appstore-ads-operator"):
    if f"`{routed_skill}`" not in router_skill:
        raise SystemExit(f"build-swift-apps router is missing {routed_skill} ownership.")
if "appstore-ads-operator" not in asc_skill or "Do not plan or execute Apple Ads" not in asc_skill:
    raise SystemExit("appstore-connect-cli must hand Apple Ads campaign ownership off.")

cursor = json.loads(Path(".cursor-plugin/plugin.json").read_text(encoding="utf-8"))
cursor_skills = sorted(Path(path).name for path in cursor.get("skills", []))
if cursor_skills != skill_names:
    raise SystemExit(".cursor-plugin/plugin.json skills are out of sync with skills/.")

codex = json.loads(Path(".codex-plugin/plugin.json").read_text(encoding="utf-8"))
if codex.get("interface", {}).get("websiteURL") != "https://github.com/Xopoko/plug-n-skills":
    raise SystemExit(
        ".codex-plugin/plugin.json website must point to the Plug'n Skills catalog."
    )

package = json.loads(Path("package.json").read_text(encoding="utf-8"))
pi_skills = sorted(Path(path).name for path in package.get("pi", {}).get("skills", []))
if pi_skills != skill_names:
    raise SystemExit("package.json pi.skills are out of sync with skills/.")

mcp = json.loads(Path(".mcp.json").read_text(encoding="utf-8"))
xcodebuildmcp = mcp.get("mcpServers", {}).get("xcodebuildmcp", {})
if "xcodebuildmcp@2.7.0" not in xcodebuildmcp.get("args", []):
    raise SystemExit(".mcp.json must pin the tested XcodeBuildMCP 2.7.0 release.")
workflow_text = xcodebuildmcp.get("env", {}).get("XCODEBUILDMCP_ENABLED_WORKFLOWS", "")
enabled_workflows = {
    workflow.strip()
    for workflow in workflow_text.split(",")
    if workflow.strip()
}
if enabled_workflows != {"simulator", "ui-automation", "debugging"}:
    raise SystemExit(".mcp.json XcodeBuildMCP workflows are out of sync with the tested contract.")

debugger_text = Path("skills/ios-simulator-debugger/SKILL.md").read_text(encoding="utf-8")
for tool_name in ("session_show_defaults", "session_set_defaults", "snapshot_ui"):
    if f"`{tool_name}`" not in debugger_text:
        raise SystemExit(f"ios-simulator-debugger is missing current tool {tool_name}.")
for stale_tool_name in ("session-set-defaults", "describe_ui"):
    if stale_tool_name in debugger_text:
        raise SystemExit(f"ios-simulator-debugger still references stale tool {stale_tool_name}.")

rooted_helpers = {
    "skills/xcode-build-baseline/SKILL.md": "benchmark_builds.py",
    "skills/xcode-build-strategist/SKILL.md": "benchmark_builds.py",
    "skills/xcode-build-tuner/SKILL.md": "benchmark_builds.py",
    "skills/xcode-compile-profiler/SKILL.md": "diagnose_compilation.py",
}
for skill_path, helper_name in rooted_helpers.items():
    skill_text = Path(skill_path).read_text(encoding="utf-8")
    expected = f'$PLUGIN_ROOT/shared/build-optimization/scripts/{helper_name}'
    if expected not in skill_text:
        raise SystemExit(f"{skill_path} must resolve {helper_name} through $PLUGIN_ROOT.")
    if "../../shared/build-optimization/scripts/" in skill_text:
        raise SystemExit(f"{skill_path} still has a current-directory-dependent helper path.")

claude = json.loads(Path(".claude-plugin/plugin.json").read_text(encoding="utf-8"))
marketplace = json.loads(Path(".claude-plugin/marketplace.json").read_text(encoding="utf-8"))
versions = {
    ".codex-plugin/plugin.json": codex.get("version"),
    ".claude-plugin/plugin.json": claude.get("version"),
    ".claude-plugin/marketplace.json": marketplace.get("version"),
    ".claude-plugin/marketplace.json plugins[0]": marketplace.get("plugins", [{}])[0].get("version"),
    ".cursor-plugin/plugin.json": cursor.get("version"),
    "package.json": package.get("version"),
}
expected_version = codex.get("version")
for surface, version in versions.items():
    if version != expected_version:
        raise SystemExit(
            f"{surface} version {version!r} differs from Codex version {expected_version!r}."
        )

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
