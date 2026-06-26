#!/usr/bin/env python3
"""Print a deterministic App Store review-readiness command plan.

The script does not call App Store Connect and does not execute the printed
commands. It only validates inputs and renders the current `asc` commands that
an agent can review before running them deliberately.
"""

from __future__ import annotations

import argparse
import json
import shlex
from dataclasses import dataclass, asdict
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
    if args.include_submit and not args.build:
        parser.error("--include-submit requires --build")
    if args.include_publish and not args.ipa:
        parser.error("--include-publish requires --ipa")
    if args.include_cancel and not args.submission_id:
        parser.error("--include-cancel requires --submission-id")
    if args.include_cancel and not args.confirming_actions:
        parser.error("--include-cancel requires --confirming-actions")


def build_plan(args: argparse.Namespace) -> list[PlannedCommand]:
    plan: list[PlannedCommand] = []

    if args.build:
        add(plan, "readiness", "Inspect processed build state", ["asc", "builds", "info", "--build-id", args.build])

    add(
        plan,
        "readiness",
        "Validate version readiness",
        [
            "asc",
            "validate",
            "--app",
            args.app,
            "--version",
            args.version,
            "--platform",
            args.platform,
            "--output",
            "table",
        ],
    )
    add(
        plan,
        "readiness",
        "Validate strict version readiness",
        [
            "asc",
            "validate",
            "--app",
            args.app,
            "--version",
            args.version,
            "--platform",
            args.platform,
            "--strict",
            "--output",
            "table",
        ],
    )

    if args.version_id:
        add(
            plan,
            "readiness",
            "Validate readiness by App Store version ID",
            [
                "asc",
                "validate",
                "--app",
                args.app,
                "--version-id",
                args.version_id,
                "--platform",
                args.platform,
                "--output",
                "table",
            ],
        )

    add(plan, "commerce", "Validate in-app purchases", ["asc", "validate", "iap", "--app", args.app, "--output", "table"])
    add(
        plan,
        "commerce",
        "Validate subscriptions",
        ["asc", "validate", "subscriptions", "--app", args.app, "--output", "table"],
    )

    if args.metadata_dir:
        metadata_dir = str(Path(args.metadata_dir))
        add(
            plan,
            "metadata",
            "Validate local metadata payload",
            ["asc", "metadata", "validate", "--dir", metadata_dir, "--output", "table"],
        )
        add(
            plan,
            "metadata",
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

    if args.privacy_file:
        privacy_file = str(Path(args.privacy_file))
        add(plan, "privacy", "Pull App Privacy state for manual review", ["asc", "web", "privacy", "pull", "--app", args.app, "--out", privacy_file])
        add(plan, "privacy", "Plan App Privacy web changes", ["asc", "web", "privacy", "plan", "--app", args.app, "--file", privacy_file])

    if args.include_submit:
        submit_dry_run = [
            "asc",
            "review",
            "submit",
            "--app",
            args.app,
            "--version",
            args.version,
            "--build",
            args.build,
            "--dry-run",
            "--output",
            "table",
        ]
        if args.wait:
            submit_dry_run.append("--wait")
        add(plan, "submit", "Dry-run review submission", submit_dry_run)

        if args.confirming_actions:
            submit_confirm = [
                "asc",
                "review",
                "submit",
                "--app",
                args.app,
                "--version",
                args.version,
                "--build",
                args.build,
                "--confirm",
            ]
            if args.wait:
                submit_confirm.append("--wait")
            add(plan, "submit", "Submit app version for review", submit_confirm, mutating=True)

    if args.include_publish:
        publish_dry_run = [
            "asc",
            "publish",
            "appstore",
            "--app",
            args.app,
            "--ipa",
            args.ipa,
            "--version",
            args.version,
            "--submit",
            "--dry-run",
            "--output",
            "table",
        ]
        if args.wait:
            publish_dry_run.append("--wait")
        add(plan, "publish", "Dry-run upload and review submission", publish_dry_run)

        if args.confirming_actions:
            publish_confirm = [
                "asc",
                "publish",
                "appstore",
                "--app",
                args.app,
                "--ipa",
                args.ipa,
                "--version",
                args.version,
                "--submit",
                "--confirm",
            ]
            if args.wait:
                publish_confirm.append("--wait")
            add(plan, "publish", "Upload IPA and submit app version", publish_confirm, mutating=True)

    add(plan, "monitor", "Inspect app release status", ["asc", "status", "--app", args.app])
    if args.version_id:
        add(plan, "monitor", "Inspect submission status by version ID", ["asc", "submit", "status", "--version-id", args.version_id])
    if args.submission_id:
        add(plan, "monitor", "Inspect submission status by submission ID", ["asc", "submit", "status", "--id", args.submission_id])
        add(plan, "monitor", "List review submission items", ["asc", "review", "submissions-list", "--app", args.app, "--paginate"])

    if args.include_cancel:
        add(plan, "cancel", "Cancel active submission", ["asc", "submit", "cancel", "--id", args.submission_id, "--confirm"], mutating=True)
        add(
            plan,
            "cancel",
            "Cancel review submission through review namespace",
            ["asc", "review", "submissions-cancel", "--id", args.submission_id, "--confirm"],
            mutating=True,
        )

    return plan


def render_shell(plan: list[PlannedCommand], include_mutating: bool) -> str:
    lines = [
        "# App Store review-readiness command plan",
        "# Generated only; this script did not execute any command.",
        f"# Mutating commands included: {'yes' if include_mutating else 'no'}",
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
    parser.add_argument("--build", help="Processed App Store Connect build ID")
    parser.add_argument("--version-id", help="App Store version ID, when already resolved")
    parser.add_argument("--submission-id", help="Review submission ID, when monitoring or canceling")
    parser.add_argument("--metadata-dir", help="Local asc metadata directory to validate and dry-run push")
    parser.add_argument("--privacy-file", help="Local App Privacy JSON path for web privacy pull/plan commands")
    parser.add_argument("--ipa", help="IPA path for publish appstore planning")
    parser.add_argument("--wait", action="store_true", help="Add --wait to submit or publish commands")
    parser.add_argument("--include-submit", action="store_true", help="Include review submit dry-run commands")
    parser.add_argument("--include-publish", action="store_true", help="Include publish appstore dry-run commands")
    parser.add_argument("--include-cancel", action="store_true", help="Include cancel commands; requires --confirming-actions")
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
        print(render_shell(plan, include_mutating=any(command.mutating for command in plan)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
