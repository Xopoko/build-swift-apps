#!/usr/bin/env python3

"""Scan a project.pbxproj for branch-pinned SPM dependencies and check tag availability."""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, List


_PKG_REF_RE = re.compile(
    r"(/\*\s*XCRemoteSwiftPackageReference\s+\"(?P<name>[^\"]+)\"\s*\*/\s*=\s*\{[^}]*?"
    r"repositoryURL\s*=\s*(?:\"(?P<quoted_url>[^\"]+)\"|(?P<url>[^\s;]+))[^}]*?"
    r"requirement\s*=\s*\{(?P<req>[^}]*)\})",
    re.DOTALL,
)

_KIND_RE = re.compile(r"kind\s*=\s*(\w+)\s*;")
_BRANCH_RE = re.compile(r'branch\s*=\s*(?:"([^"]+)"|([^\s;]+))\s*;')


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Check branch-pinned SPM dependencies for available tags."
    )
    parser.add_argument(
        "--project",
        required=True,
        help="Path to the .xcodeproj directory",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON",
    )
    return parser.parse_args()


def find_branch_pins(pbxproj: str) -> List[Dict[str, str]]:
    results: List[Dict[str, str]] = []
    for match in _PKG_REF_RE.finditer(pbxproj):
        name = match.group("name")
        url = match.group("quoted_url") or match.group("url")
        req = match.group("req")
        kind_match = _KIND_RE.search(req)
        if not kind_match:
            continue
        kind = kind_match.group(1)
        if kind != "branch":
            continue
        branch_match = _BRANCH_RE.search(req)
        branch = (branch_match.group(1) or branch_match.group(2)) if branch_match else "unknown"
        results.append({"name": name, "url": url, "branch": branch})
    return results


def check_tags(url: str) -> List[str]:
    try:
        result = subprocess.run(
            ["git", "ls-remote", "--tags", "--refs", "--", url],
            capture_output=True,
            text=True,
            timeout=15,
        )
    except subprocess.TimeoutExpired as error:
        raise RuntimeError("git ls-remote timed out") from error
    except OSError as error:
        raise RuntimeError(f"Could not run git ls-remote: {error.strerror}") from error
    if result.returncode != 0:
        raise RuntimeError(f"git ls-remote failed (exit {result.returncode})")

    prefix = "refs/tags/"
    return [
        ref[len(prefix):]
        for line in result.stdout.splitlines()
        if (ref := line.partition("\t")[2]).startswith(prefix)
    ]


def main() -> int:
    args = parse_args()
    pbxproj_path = Path(args.project) / "project.pbxproj"
    if not pbxproj_path.exists():
        sys.stderr.write(f"Not found: {pbxproj_path}\n")
        return 1

    pbxproj = pbxproj_path.read_text()
    pins = find_branch_pins(pbxproj)

    if not pins and not args.json:
        print("No branch-pinned SPM dependencies found.")
        return 0

    results: List[Dict] = []
    for pin in pins:
        try:
            tags = check_tags(pin["url"])
        except RuntimeError as error:
            results.append({**pin, "tags_available": None, "tags": None, "error": str(error)})
        else:
            results.append({**pin, "tags_available": bool(tags), "tags": tags})

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        for r in results:
            label = f"{r['name']}: branch={r['branch']}"
            if "error" in r:
                print(f"{label}: {r['error']}", file=sys.stderr)
            elif r["tags"]:
                print(f"{label}: {len(r['tags'])} tags (e.g. {', '.join(r['tags'][:5])})")
            else:
                print(f"{label}: no tags")

    return 1 if any("error" in r for r in results) else 0


if __name__ == "__main__":
    raise SystemExit(main())
