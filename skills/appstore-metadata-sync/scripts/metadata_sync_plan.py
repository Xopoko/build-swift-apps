#!/usr/bin/env python3
"""Print a deterministic App Store metadata-sync command plan.

The script validates command-plan inputs and prints `asc` commands only. It
does not call App Store Connect, read credentials, or modify local metadata.
"""

from __future__ import annotations

import argparse
import json
import shlex
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable


PLATFORMS = ("IOS", "MAC_OS", "TV_OS", "VISION_OS")


@dataclass(frozen=True)
class PlannedCommand:
    phase: str
    intent: str
    argv: list[str]
    mutating: bool = False


def add(plan: list[PlannedCommand], phase: str, intent: str, argv: Iterable[str], mutating: bool = False) -> None:
    plan.append(PlannedCommand(phase=phase, intent=intent, argv=list(argv), mutating=mutating))


def validate_args(parser: argparse.ArgumentParser, args: argparse.Namespace) -> None:
    if args.include_quick_edit and not args.locale:
        parser.error("--include-quick-edit requires --locale")
    if args.include_keywords and not args.keywords_csv:
        parser.error("--include-keywords requires --keywords-csv")
    if args.include_strings and not (args.version_id or args.app_info):
        parser.error("--include-strings requires --version-id or --app-info")
    if args.include_fastlane and not args.version_id:
        parser.error("--include-fastlane requires --version-id")
    if args.confirming_actions and not (args.include_apply or args.include_keywords):
        parser.error("--confirming-actions is only meaningful with --include-apply or --include-keywords")


def build_plan(args: argparse.Namespace) -> list[PlannedCommand]:
    plan: list[PlannedCommand] = []
    metadata_dir = str(Path(args.dir))

    pull = ["asc", "metadata", "pull", "--app", args.app]
    if args.app_info:
        pull.extend(["--app-info", args.app_info])
    pull.extend(["--version", args.version, "--platform", args.platform, "--dir", metadata_dir])
    add(plan, "pull", "Pull canonical metadata JSON", pull)

    if args.app_info is None:
        add(plan, "discover", "List app-info records when app-info ID is ambiguous", ["asc", "apps", "info", "list", "--app", args.app, "--output", "table"])

    add(plan, "validate", "Validate metadata JSON", ["asc", "metadata", "validate", "--dir", metadata_dir, "--output", "table"])
    if args.subscription_app:
        add(
            plan,
            "validate",
            "Validate subscription-app metadata shape",
            ["asc", "metadata", "validate", "--dir", metadata_dir, "--subscription-app", "--output", "table"],
        )

    add(
        plan,
        "push",
        "Dry-run metadata push",
        [
            "asc",
            "metadata",
            "push",
            "--app",
            args.app,
            "--version",
            args.version,
            "--platform",
            args.platform,
            "--dir",
            metadata_dir,
            "--dry-run",
            "--output",
            "table",
        ],
    )

    if args.include_apply:
        apply_command = [
            "asc",
            "metadata",
            "apply",
            "--app",
            args.app,
            "--version",
            args.version,
            "--platform",
            args.platform,
            "--dir",
            metadata_dir,
        ]
        add(plan, "apply", "Apply metadata changes", apply_command, mutating=True)

    if args.version_id and args.copyright:
        add(
            plan,
            "quick-edit",
            "Update non-localized copyright",
            ["asc", "versions", "update", "--version-id", args.version_id, "--copyright", args.copyright],
            mutating=True,
        )

    if args.include_quick_edit:
        add(
            plan,
            "quick-edit",
            "Prepare version-field quick edit shape",
            [
                "asc",
                "apps",
                "info",
                "edit",
                "--app",
                args.app,
                "--version",
                args.version,
                "--platform",
                args.platform,
                "--locale",
                args.locale,
                "--description",
                "...",
            ],
        )
        if args.version_id:
            add(
                plan,
                "quick-edit",
                "Prepare version-id quick edit shape",
                [
                    "asc",
                    "apps",
                    "info",
                    "edit",
                    "--app",
                    args.app,
                    "--version-id",
                    args.version_id,
                    "--locale",
                    args.locale,
                    "--whats-new",
                    "Bug fixes",
                ],
            )

    if args.include_keywords:
        add(
            plan,
            "keywords",
            "Diff keyword metadata",
            ["asc", "metadata", "keywords", "diff", "--app", args.app, "--version", args.version, "--platform", args.platform, "--dir", metadata_dir],
        )
        add(
            plan,
            "keywords",
            "Import keyword CSV into local metadata",
            [
                "asc",
                "metadata",
                "keywords",
                "import",
                "--dir",
                metadata_dir,
                "--version",
                args.version,
                "--locale",
                args.locale or "en-US",
                "--input",
                args.keywords_csv,
            ],
        )
        add(
            plan,
            "keywords",
            "Sync keyword CSV against ASC",
            [
                "asc",
                "metadata",
                "keywords",
                "sync",
                "--app",
                args.app,
                "--version",
                args.version,
                "--platform",
                args.platform,
                "--dir",
                metadata_dir,
                "--input",
                args.keywords_csv,
            ],
        )
        if args.confirming_actions:
            add(
                plan,
                "keywords",
                "Apply keyword metadata",
                [
                    "asc",
                    "metadata",
                    "keywords",
                    "apply",
                    "--app",
                    args.app,
                    "--version",
                    args.version,
                    "--platform",
                    args.platform,
                    "--dir",
                    metadata_dir,
                    "--confirm",
                ],
                mutating=True,
            )

    if args.include_strings:
        if args.version_id:
            add(
                plan,
                "strings",
                "Download version .strings localizations",
                ["asc", "localizations", "download", "--version", args.version_id, "--path", args.strings_dir],
            )
            add(
                plan,
                "strings",
                "Dry-run version .strings upload",
                ["asc", "localizations", "upload", "--version", args.version_id, "--path", args.strings_dir, "--dry-run"],
            )
        if args.app_info:
            add(
                plan,
                "strings",
                "Dry-run app-info .strings upload",
                [
                    "asc",
                    "localizations",
                    "upload",
                    "--app",
                    args.app,
                    "--type",
                    "app-info",
                    "--app-info",
                    args.app_info,
                    "--path",
                    args.app_info_strings_dir,
                    "--dry-run",
                ],
            )

    if args.include_fastlane:
        add(
            plan,
            "fastlane",
            "Export legacy fastlane metadata",
            ["asc", "migrate", "export", "--app", args.app, "--version-id", args.version_id, "--output-dir", args.fastlane_dir],
        )
        add(plan, "fastlane", "Validate legacy fastlane metadata", ["asc", "migrate", "validate", "--fastlane-dir", args.fastlane_dir])
        add(
            plan,
            "fastlane",
            "Dry-run legacy fastlane metadata import",
            ["asc", "migrate", "import", "--app", args.app, "--version-id", args.version_id, "--fastlane-dir", args.fastlane_dir, "--dry-run"],
        )

    return plan


def render_shell(plan: list[PlannedCommand]) -> str:
    lines = [
        "# App Store metadata-sync command plan",
        "# Generated only; this script did not execute any command.",
        f"# Mutating commands included: {'yes' if any(command.mutating for command in plan) else 'no'}",
    ]
    current_phase = None
    for command in plan:
        if command.phase != current_phase:
            current_phase = command.phase
            lines.append("")
            lines.append(f"# {current_phase}")
        marker = " [mutating]" if command.mutating else ""
        lines.append(f"# {command.intent}{marker}")
        lines.append(shlex.join(command.argv))
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--app", required=True, help="App Store Connect app ID or known asc app identifier")
    parser.add_argument("--version", required=True, help="Marketing version, e.g. 1.2.3")
    parser.add_argument("--platform", choices=PLATFORMS, default="IOS", help="App Store platform")
    parser.add_argument("--dir", default="./metadata", help="Canonical metadata directory")
    parser.add_argument("--app-info", help="App-info ID, when already resolved")
    parser.add_argument("--version-id", help="App Store version ID, when already resolved")
    parser.add_argument("--locale", help="Locale for quick edit or keyword import examples")
    parser.add_argument("--copyright", help="Copyright text for version-id update planning")
    parser.add_argument("--subscription-app", action="store_true", help="Include subscription-app metadata validation")
    parser.add_argument("--include-apply", action="store_true", help="Include metadata apply command")
    parser.add_argument("--include-quick-edit", action="store_true", help="Include quick edit command shapes")
    parser.add_argument("--include-keywords", action="store_true", help="Include keyword diff/import/sync commands")
    parser.add_argument("--keywords-csv", help="Keyword CSV path for keyword commands")
    parser.add_argument("--include-strings", action="store_true", help="Include .strings localization commands")
    parser.add_argument("--strings-dir", default="./localizations", help="Version .strings localization directory")
    parser.add_argument("--app-info-strings-dir", default="./app-info-localizations", help="App-info .strings localization directory")
    parser.add_argument("--include-fastlane", action="store_true", help="Include legacy fastlane migration commands")
    parser.add_argument("--fastlane-dir", default="./fastlane", help="Legacy fastlane metadata directory")
    parser.add_argument(
        "--confirming-actions",
        action="store_true",
        help="Also print commands that include --confirm and can mutate App Store Connect state",
    )
    parser.add_argument("--json", action="store_true", help="Print JSON instead of shell commands")
    args = parser.parse_args()
    validate_args(parser, args)

    plan = build_plan(args)
    if args.json:
        payload = {
            "commands": [asdict(command) for command in plan],
            "generated_only": True,
            "mutating_commands_included": any(command.mutating for command in plan),
        }
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(render_shell(plan))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
