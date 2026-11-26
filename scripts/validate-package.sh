#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
cd "$repo_root"

echo "Checking shell scripts, manifests, and skill paths"
python3 - <<'PY'
import json
import re
import subprocess
from pathlib import Path

repo_root = Path.cwd()
skill_dirs = sorted(path for path in Path("skills").iterdir() if path.is_dir())
if not skill_dirs:
    raise SystemExit("No skill directories found.")

for directory in ("scripts", "skills", "shared"):
    for script in sorted(Path(directory).rglob("*.sh")):
        if "node_modules" in script.parts:
            continue
        if subprocess.run(["bash", "-n", str(script)]).returncode:
            raise SystemExit(f"{script}: shell syntax check failed.")

code_reference_pattern = re.compile(
    r"`((?:(?:\.\.?/)+|references/|shared/)[^`\n]*?\.md(?:#[^`\n]*)?)`"
)
link_reference_pattern = re.compile(
    r"\]\((?![A-Za-z][A-Za-z0-9+.-]*:|#)([^)\n]*?\.md(?:#[^)\n]*)?)\)"
)


def check_markdown_references(source, text):
    for pattern in (code_reference_pattern, link_reference_pattern):
        for match in pattern.finditer(text):
            reference = match.group(1).strip().strip("<>")
            line = text.count("\n", 0, match.start()) + 1
            target = (source.parent / reference.split("#", 1)[0]).resolve()
            if repo_root not in target.parents or not target.is_file():
                raise SystemExit(f"{source}:{line}: missing or out-of-package reference: {reference}")


for skill_dir in skill_dirs:
    skill_file = skill_dir / "SKILL.md"
    if not skill_file.is_file():
        raise SystemExit(f"{skill_file} is missing.")
    text = skill_file.read_text(encoding="utf-8")
    opening, _, rest = text.partition("\n")
    frontmatter, closing, _ = rest.partition("\n---\n")
    if opening != "---" or not closing:
        raise SystemExit(f"{skill_file} needs delimited frontmatter.")
    names = re.findall(r"^name:[ \t]*(.*)$", frontmatter, re.MULTILINE)
    if [name.strip().strip("\"'") for name in names] != [skill_dir.name]:
        raise SystemExit(f"{skill_file} name does not match directory {skill_dir.name}.")
    descriptions = re.findall(r"^description:[ \t]*(.*)$", frontmatter, re.MULTILINE)
    if len(descriptions) != 1 or not descriptions[0].strip().strip("\"'").strip():
        raise SystemExit(f"{skill_file} needs a description.")

    agent_manifest = skill_dir / "agents" / "openai.yaml"
    if not agent_manifest.is_file():
        raise SystemExit(f"{agent_manifest} is required for Codex invocation policy.")
    agent_config = agent_manifest.read_text(encoding="utf-8")
    policies = re.findall(r"^policy:[ \t]*\n((?:[ \t]+.*(?:\n|$))*)", agent_config, re.MULTILINE)
    implicit = re.findall(
        r"^  allow_implicit_invocation:[ \t]*(true|false)[ \t]*$",
        policies[0] if len(policies) == 1 else "",
        re.MULTILINE,
    )
    expected_policy = "true" if skill_dir.name == "build-swift-apps" else "false"
    if implicit != [expected_policy]:
        raise SystemExit(
            f"{agent_manifest} must keep only the router implicit in Codex."
        )

    check_markdown_references(skill_file, text)

for command in Path("commands").glob("*.md"):
    check_markdown_references(command, command.read_text(encoding="utf-8"))

cursor = json.loads(Path(".cursor-plugin/plugin.json").read_text(encoding="utf-8"))
cursor_skills = sorted(Path(path) for path in cursor.get("skills", []))
if cursor_skills != skill_dirs:
    raise SystemExit(".cursor-plugin/plugin.json skills are out of sync with skills/.")

codex = json.loads(Path(".codex-plugin/plugin.json").read_text(encoding="utf-8"))
source_url = "https://github.com/Xopoko/build-swift-apps"
for field, value in (
    ("homepage", codex.get("homepage")),
    ("repository", codex.get("repository")),
    ("interface.websiteURL", codex.get("interface", {}).get("websiteURL")),
):
    if value != source_url:
        raise SystemExit(f".codex-plugin/plugin.json {field} must point to {source_url}.")
if codex.get("skills") != "./skills/" or codex.get("mcpServers") != "./.mcp.json":
    raise SystemExit(".codex-plugin/plugin.json must load skills/ and .mcp.json from the package.")

package = json.loads(Path("package.json").read_text(encoding="utf-8"))
pi_skills = sorted(Path(path) for path in package.get("pi", {}).get("skills", []))
if pi_skills != skill_dirs:
    raise SystemExit("package.json pi.skills are out of sync with skills/.")

mcp = json.loads(Path(".mcp.json").read_text(encoding="utf-8"))
mcp_servers = mcp.get("mcpServers", {})
for name, server in mcp_servers.items():
    if "url" in server and server.get("type") not in {"http", "sse", "ws"}:
        raise SystemExit(f".mcp.json: remote server {name} needs an explicit transport type.")
xcodebuildmcp = mcp_servers.get("xcodebuildmcp", {})
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

claude = json.loads(Path(".claude-plugin/plugin.json").read_text(encoding="utf-8"))
marketplace = json.loads(Path(".claude-plugin/marketplace.json").read_text(encoding="utf-8"))
entries = [entry for entry in marketplace.get("plugins", []) if entry.get("name") == "build-swift-apps"]
if len(entries) != 1 or entries[0].get("source") != "./":
    raise SystemExit(".claude-plugin/marketplace.json must load build-swift-apps from the package root.")
versions = {
    ".claude-plugin/plugin.json": claude.get("version"),
    ".claude-plugin/marketplace.json": marketplace.get("version"),
    ".claude-plugin/marketplace.json build-swift-apps entry": entries[0].get("version"),
    ".cursor-plugin/plugin.json": cursor.get("version"),
    "package.json": package.get("version"),
}
expected_version = codex.get("version")
if not isinstance(expected_version, str) or not expected_version.strip():
    raise SystemExit(".codex-plugin/plugin.json needs a version.")
for surface, version in versions.items():
    if version != expected_version:
        raise SystemExit(
            f"{surface} version {version!r} differs from Codex version {expected_version!r}."
        )

readme = Path("README.md").read_text(encoding="utf-8")
missing_from_readme = [path.name for path in skill_dirs if f"`{path.name}`" not in readme]
if missing_from_readme:
    raise SystemExit(f"README.md is missing skills: {', '.join(missing_from_readme)}")
PY

echo "Checking for absolute user home paths"
python3 - <<'PY'
from pathlib import Path
import re
import sys

home_path = re.compile(rb"(?:[a-z]:[\\/]+Users[\\/]+|/(?:Users|home)/)[a-z0-9][\w.-]*", re.IGNORECASE)
violations = []
for path in sorted(Path(".").rglob("*")):
    if not path.is_file() or {".git", "node_modules"}.intersection(path.parts):
        continue
    try:
        data = path.read_bytes()
    except OSError as error:
        raise SystemExit(
            f"{path}: could not read file during home path check "
            f"({type(error).__name__})"
        ) from error
    if b"\0" in data:
        continue
    match = home_path.search(data)
    if match:
        line_number = data.count(b"\n", 0, match.start()) + 1
        violations.append(f"{path}:{line_number}")

if violations:
    for location in violations:
        print(f"{location}: absolute user home path", file=sys.stderr)
    raise SystemExit("User home path check failed.")
PY

echo "Package validation passed"
