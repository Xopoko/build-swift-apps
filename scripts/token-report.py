#!/usr/bin/env python3
"""Generate token budget reports for packaged skills."""

from __future__ import annotations

import argparse
import json
import math
import re
from dataclasses import dataclass
from pathlib import Path


@dataclass
class SkillBudget:
    name: str
    description: str
    path: Path
    startup_tokens: int
    body_tokens: int


def load_encoder(name: str):
    try:
        import tiktoken  # type: ignore

        return tiktoken.get_encoding(name), "exact"
    except Exception:
        return None, "approx"


def count_tokens(text: str, encoder) -> int:
    if encoder is not None:
        return len(encoder.encode(text))
    return int(math.ceil(len(text) / 4))


def parse_skill(path: Path) -> tuple[str, str, str]:
    text = path.read_text(encoding="utf-8")
    normalized = text.replace("\r\n", "\n")
    if not normalized.startswith("---\n"):
        raise ValueError(f"missing frontmatter: {path}")

    lines = normalized.split("\n")
    end_index = None
    frontmatter: list[str] = []
    for index, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            end_index = index
            break
        frontmatter.append(line)
    if end_index is None:
        raise ValueError(f"unterminated frontmatter: {path}")

    metadata: dict[str, str] = {}
    for line in frontmatter:
        match = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        if match:
            metadata[match.group(1)] = match.group(2).strip().strip("\"'")

    name = metadata.get("name")
    description = metadata.get("description")
    if not name or not description:
        raise ValueError(f"missing name or description: {path}")

    body = "\n".join(lines[end_index + 1 :])
    return name, description, body


def collect(skills_dir: Path, plugin_prefix: str, encoding: str) -> tuple[str, list[SkillBudget]]:
    encoder, mode = load_encoder(encoding)
    rows: list[SkillBudget] = []

    for skill_dir in sorted(p for p in skills_dir.iterdir() if p.is_dir()):
        skill_path = skill_dir / "SKILL.md"
        if not skill_path.exists():
            continue
        name, description, body = parse_skill(skill_path)
        relative_path = skill_path.relative_to(skills_dir.parent)
        startup_line = f"- {plugin_prefix}:{name}: {description} (file: {relative_path})"
        rows.append(
            SkillBudget(
                name=name,
                description=description,
                path=relative_path,
                startup_tokens=count_tokens(startup_line, encoder),
                body_tokens=count_tokens(body, encoder),
            )
        )

    return mode, sorted(rows, key=lambda row: row.name)


def markdown(mode: str, rows: list[SkillBudget]) -> str:
    startup_total = sum(row.startup_tokens for row in rows)
    body_total = sum(row.body_tokens for row in rows)

    lines = [
        "| Metric | Tokens | Notes |",
        "| --- | ---: | --- |",
        f"| Startup metadata | {startup_total:,} | Name, description, and file pointer for all {len(rows)} skills. |",
        f"| On-demand skill bodies | {body_total:,} | Full body text loaded only when a skill is selected. |",
        "",
        "| Skill | Startup metadata | On-demand body |",
        "| --- | ---: | ---: |",
    ]
    for row in rows:
        lines.append(f"| `{row.name}` | {row.startup_tokens:,} | {row.body_tokens:,} |")
    lines.append("")
    lines.append(f"Measured with `{mode}` token counting and the `o200k_base` encoding.")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skills-dir", default="skills", help="Directory containing skill folders.")
    parser.add_argument("--plugin-prefix", default="build-swift-apps", help="Skill namespace used in startup metadata.")
    parser.add_argument("--encoding", default="o200k_base", help="tiktoken encoding name.")
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of Markdown.")
    args = parser.parse_args()

    mode, rows = collect(Path(args.skills_dir), args.plugin_prefix, args.encoding)
    if args.json:
        print(
            json.dumps(
                {
                    "mode": mode,
                    "encoding": args.encoding if mode == "exact" else None,
                    "skills": len(rows),
                    "startup_tokens": sum(row.startup_tokens for row in rows),
                    "body_tokens": sum(row.body_tokens for row in rows),
                    "rows": [row.__dict__ | {"path": str(row.path)} for row in rows],
                },
                indent=2,
            )
        )
    else:
        print(markdown(mode, rows))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
