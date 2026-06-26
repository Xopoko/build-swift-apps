#!/usr/bin/env python3
"""Lint App Store metadata localization files for field length limits.

The script reads `.strings` and `.json` files with App Store metadata fields.
It does not translate, rewrite files, upload to App Store Connect, or call ASC.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable


FIELD_LIMITS = {
    "name": 30,
    "subtitle": 30,
    "keywords": 100,
    "description": 4000,
    "whatsNew": 4000,
    "promotionalText": 170,
}
STRING_PAIR_RE = re.compile(r'^\s*"((?:\\.|[^"\\])*)"\s*=\s*"((?:\\.|[^"\\])*)";\s*$')


@dataclass(frozen=True)
class FieldAudit:
    path: str
    field: str
    length: int | None
    limit: int | None
    ok: bool
    notes: list[str]


def iter_metadata_paths(paths: Iterable[Path], recursive: bool) -> list[Path]:
    result: list[Path] = []
    for path in paths:
        expanded = path.expanduser()
        if expanded.is_dir():
            iterator = expanded.rglob("*") if recursive else expanded.iterdir()
            result.extend(item for item in iterator if item.is_file() and item.suffix.lower() in {".strings", ".json"})
        elif expanded.is_file() and expanded.suffix.lower() in {".strings", ".json"}:
            result.append(expanded)
        elif expanded.exists():
            result.append(expanded)
    return sorted(result, key=lambda item: str(item))


def unescape_strings_value(value: str) -> str:
    # Apple .strings escaping is close enough to JSON string escaping for the
    # common metadata fields this linter checks.
    try:
        return json.loads(f'"{value}"')
    except json.JSONDecodeError:
        return value.replace(r"\"", '"').replace(r"\\", "\\")


def read_strings(path: Path) -> tuple[dict[str, str], list[str]]:
    values: dict[str, str] = {}
    notes: list[str] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        stripped = line.strip()
        if not stripped or stripped.startswith("//") or stripped.startswith("/*") or stripped.endswith("*/"):
            continue
        match = STRING_PAIR_RE.match(line)
        if not match:
            notes.append(f"line {line_number}: unsupported .strings syntax")
            continue
        key, value = match.groups()
        values[unescape_strings_value(key)] = unescape_strings_value(value)
    return values, notes


def read_json(path: Path) -> tuple[dict[str, str], list[str]]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        return {}, ["JSON root is not an object"]
    values: dict[str, str] = {}
    notes: list[str] = []
    for key, value in raw.items():
        if isinstance(value, str):
            values[key] = value
        elif key in FIELD_LIMITS and value is not None:
            notes.append(f"{key}: expected string, got {type(value).__name__}")
    return values, notes


def audit_file(path: Path) -> list[FieldAudit]:
    audits: list[FieldAudit] = []
    try:
        if path.suffix.lower() == ".strings":
            values, file_notes = read_strings(path)
        elif path.suffix.lower() == ".json":
            values, file_notes = read_json(path)
        else:
            return [
                FieldAudit(
                    path=str(path),
                    field="",
                    length=None,
                    limit=None,
                    ok=False,
                    notes=["unsupported file type"],
                )
            ]
    except Exception as exc:  # noqa: BLE001 - report exact parse failure.
        return [
            FieldAudit(
                path=str(path),
                field="",
                length=None,
                limit=None,
                ok=False,
                notes=[str(exc)],
            )
        ]

    for note in file_notes:
        audits.append(FieldAudit(path=str(path), field="", length=None, limit=None, ok=False, notes=[note]))

    for field, value in sorted(values.items()):
        if field not in FIELD_LIMITS:
            continue
        limit = FIELD_LIMITS[field]
        length = len(value)
        notes: list[str] = []
        if field == "keywords":
            if "\n" in value:
                notes.append("keywords contain newline")
            if ",," in value:
                notes.append("keywords contain empty item")
        ok = length <= limit and not notes
        if length > limit:
            notes.append(f"{field} length {length} exceeds limit {limit}")
        audits.append(FieldAudit(path=str(path), field=field, length=length, limit=limit, ok=ok, notes=notes))

    if not audits:
        audits.append(FieldAudit(path=str(path), field="", length=None, limit=None, ok=True, notes=["no known metadata fields found"]))
    return audits


def render_table(items: list[FieldAudit]) -> str:
    lines = ["ok\tfield\tlength\tlimit\tpath\tnotes"]
    for item in items:
        lines.append(
            "\t".join(
                [
                    "yes" if item.ok else "no",
                    item.field,
                    "" if item.length is None else str(item.length),
                    "" if item.limit is None else str(item.limit),
                    item.path,
                    "; ".join(item.notes),
                ]
            )
        )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", help=".strings/.json file or directory paths")
    parser.add_argument("--recursive", action="store_true", help="Recurse into directories")
    parser.add_argument("--json", action="store_true", help="Print JSON instead of a tab-separated table")
    args = parser.parse_args()

    paths = iter_metadata_paths([Path(path) for path in args.paths], recursive=args.recursive)
    items = [audit for path in paths for audit in audit_file(path)]
    payload = {
        "ok": bool(items) and all(item.ok for item in items),
        "count": len(items),
        "limits": FIELD_LIMITS,
        "fields": [asdict(item) for item in items],
    }

    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(render_table(items))
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
