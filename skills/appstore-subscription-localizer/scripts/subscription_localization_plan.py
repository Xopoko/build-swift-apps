#!/usr/bin/env python3
"""Print a deterministic App Store subscription/IAP localization command plan.

The script renders `asc` commands only. It does not call App Store Connect,
read credentials, create localizations, or update product text.
"""

from __future__ import annotations

import argparse
import json
import shlex
from dataclasses import asdict, dataclass
from typing import Iterable


TARGETS = ("subscription", "group", "iap")


@dataclass(frozen=True)
class PlannedCommand:
    phase: str
    intent: str
    argv: list[str]
    mutating: bool = False


def add(plan: list[PlannedCommand], phase: str, intent: str, argv: Iterable[str], mutating: bool = False) -> None:
    plan.append(PlannedCommand(phase=phase, intent=intent, argv=list(argv), mutating=mutating))


def parse_locales(values: list[str] | None) -> list[str]:
    if not values:
        return []
    locales: list[str] = []
    for value in values:
        for item in value.split(","):
            normalized = item.strip()
            if normalized:
                locales.append(normalized)
    return locales


def selected_targets(values: list[str] | None) -> list[str]:
    return values if values else list(TARGETS)


def validate_args(parser: argparse.ArgumentParser, args: argparse.Namespace) -> None:
    locales = parse_locales(args.locale)
    target_ids = {
        "subscription": args.subscription_id,
        "group": args.group_id,
        "iap": args.iap_id,
    }
    targets_with_ids = [target for target in selected_targets(args.target) if target_ids[target]]

    if args.include_create and not args.confirming_actions:
        parser.error("--include-create requires --confirming-actions")
    if args.include_update and not args.confirming_actions:
        parser.error("--include-update requires --confirming-actions")
    if args.include_create and not targets_with_ids:
        parser.error("--include-create requires an ID for at least one selected --target")
    if args.include_create and not locales:
        parser.error("--include-create requires --locale")
    if args.include_create and not args.name:
        parser.error("--include-create requires --name")
    if args.include_update and not args.localization_id:
        parser.error("--include-update requires --localization-id")
    if args.include_update and not args.update_target:
        parser.error("--include-update requires --update-target")
    if args.include_update and not args.name:
        parser.error("--include-update requires --name")


def target_ids(args: argparse.Namespace) -> dict[str, str | None]:
    return {
        "subscription": args.subscription_id,
        "group": args.group_id,
        "iap": args.iap_id,
    }


def build_plan(args: argparse.Namespace) -> list[PlannedCommand]:
    plan: list[PlannedCommand] = []
    ids = target_ids(args)
    locales = parse_locales(args.locale)

    if args.app:
        add(plan, "resolve", "List subscription groups", ["asc", "subscriptions", "groups", "list", "--app", args.app, "--output", "table"])
        add(plan, "resolve", "List in-app purchases", ["asc", "iap", "list", "--app", args.app, "--output", "table"])

    if args.group_id:
        add(plan, "resolve", "List subscriptions in group", ["asc", "subscriptions", "list", "--group-id", args.group_id, "--output", "table"])

    if args.subscription_id:
        add(
            plan,
            "list",
            "List existing subscription localizations",
            ["asc", "subscriptions", "localizations", "list", "--subscription-id", args.subscription_id, "--paginate", "--output", "table"],
        )

    if args.group_id:
        add(
            plan,
            "list",
            "List existing subscription-group localizations",
            ["asc", "subscriptions", "groups", "localizations", "list", "--group-id", args.group_id, "--paginate", "--output", "table"],
        )

    if args.iap_id:
        add(
            plan,
            "list",
            "List existing IAP localizations",
            ["asc", "iap", "localizations", "list", "--iap-id", args.iap_id, "--paginate", "--output", "table"],
        )

    if args.include_create:
        for target in selected_targets(args.target):
            current_id = ids[target]
            if current_id is None:
                continue
            for locale in locales:
                if target == "subscription":
                    add(
                        plan,
                        "create",
                        f"Create subscription localization for {locale}",
                        [
                            "asc",
                            "subscriptions",
                            "localizations",
                            "create",
                            "--subscription-id",
                            current_id,
                            "--locale",
                            locale,
                            "--name",
                            args.name,
                        ],
                        mutating=True,
                    )
                elif target == "group":
                    command = [
                        "asc",
                        "subscriptions",
                        "groups",
                        "localizations",
                        "create",
                        "--group-id",
                        current_id,
                        "--locale",
                        locale,
                        "--name",
                        args.name,
                    ]
                    if args.custom_app_name:
                        command.extend(["--custom-app-name", args.custom_app_name])
                    add(plan, "create", f"Create subscription-group localization for {locale}", command, mutating=True)
                elif target == "iap":
                    command = [
                        "asc",
                        "iap",
                        "localizations",
                        "create",
                        "--iap-id",
                        current_id,
                        "--locale",
                        locale,
                        "--name",
                        args.name,
                    ]
                    if args.description:
                        command.extend(["--description", args.description])
                    add(plan, "create", f"Create IAP localization for {locale}", command, mutating=True)

    if args.include_update:
        if args.update_target == "subscription":
            add(
                plan,
                "update",
                "Update subscription localization",
                ["asc", "subscriptions", "localizations", "update", "--id", args.localization_id, "--name", args.name],
                mutating=True,
            )
        elif args.update_target == "group":
            command = ["asc", "subscriptions", "groups", "localizations", "update", "--id", args.localization_id, "--name", args.name]
            if args.custom_app_name:
                command.extend(["--custom-app-name", args.custom_app_name])
            add(plan, "update", "Update subscription-group localization", command, mutating=True)
        elif args.update_target == "iap":
            command = ["asc", "iap", "localizations", "update", "--localization-id", args.localization_id, "--name", args.name]
            if args.description:
                command.extend(["--description", args.description])
            add(plan, "update", "Update IAP localization", command, mutating=True)

    return plan


def render_shell(plan: list[PlannedCommand]) -> str:
    lines = [
        "# App Store subscription/IAP localization command plan",
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
    parser.add_argument("--app", help="App Store Connect app ID or known asc app identifier")
    parser.add_argument("--group-id", help="Subscription group ID")
    parser.add_argument("--subscription-id", help="Subscription ID")
    parser.add_argument("--iap-id", help="In-app purchase ID")
    parser.add_argument("--target", choices=TARGETS, action="append", help="Target surface; repeatable; defaults to all targets with IDs")
    parser.add_argument("--locale", action="append", help="Locale or comma-separated locales; repeatable")
    parser.add_argument("--name", help="Localized display name")
    parser.add_argument("--description", help="Localized IAP description")
    parser.add_argument("--custom-app-name", help="Subscription-group custom app name")
    parser.add_argument("--localization-id", help="Existing localization ID for update")
    parser.add_argument("--update-target", choices=TARGETS, help="Target surface for --include-update")
    parser.add_argument("--include-create", action="store_true", help="Include create commands")
    parser.add_argument("--include-update", action="store_true", help="Include update command")
    parser.add_argument(
        "--confirming-actions",
        action="store_true",
        help="Required before printing localization create or update commands",
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
