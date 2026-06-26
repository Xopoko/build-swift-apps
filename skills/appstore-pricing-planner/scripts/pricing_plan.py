#!/usr/bin/env python3
"""Print a deterministic App Store pricing command plan.

The script renders `asc` pricing commands only. It does not call App Store
Connect, read credentials, import CSV data, or change prices/availability.
"""

from __future__ import annotations

import argparse
import json
import shlex
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class PlannedCommand:
    phase: str
    intent: str
    argv: list[str]
    mutating: bool = False


def add(plan: list[PlannedCommand], phase: str, intent: str, argv: Iterable[str], mutating: bool = False) -> None:
    plan.append(PlannedCommand(phase=phase, intent=intent, argv=list(argv), mutating=mutating))


def validate_args(parser: argparse.ArgumentParser, args: argparse.Namespace) -> None:
    if args.include_subscription_import and not args.subscription_id:
        parser.error("--include-subscription-import requires --subscription-id")
    if args.include_subscription_import and not args.prices_csv:
        parser.error("--include-subscription-import requires --prices-csv")
    if args.include_subscription_set and not args.subscription_id:
        parser.error("--include-subscription-set requires --subscription-id")
    if args.include_subscription_set and not (args.price or args.tier or args.price_point_id):
        parser.error("--include-subscription-set requires --price, --tier, or --price-point-id")
    if args.include_subscription_availability and not args.subscription_id:
        parser.error("--include-subscription-availability requires --subscription-id")
    if args.include_iap_price_points and not args.iap_id:
        parser.error("--include-iap-price-points requires --iap-id")
    if args.include_iap_schedule and not args.iap_id:
        parser.error("--include-iap-schedule requires --iap-id")
    if args.include_iap_schedule and not (args.price or args.tier or args.price_point_id):
        parser.error("--include-iap-schedule requires --price, --tier, or --price-point-id")
    if args.include_subscription_setup and not (args.app and args.product_id):
        parser.error("--include-subscription-setup requires --app and --product-id")
    if args.include_iap_setup and not (args.app and args.product_id):
        parser.error("--include-iap-setup requires --app and --product-id")

    mutating_requested = any(
        (
            args.include_subscription_setup,
            args.include_subscription_apply,
            args.include_subscription_set,
            args.include_subscription_availability,
            args.include_iap_setup,
            args.include_iap_schedule,
        )
    )
    if mutating_requested and not args.confirming_actions:
        parser.error("pricing setup, apply, set, availability, or schedule commands require --confirming-actions")


def price_selector(args: argparse.Namespace, price_point_flag: str = "--price-point") -> list[str]:
    if args.price:
        return ["--price", args.price]
    if args.tier:
        return ["--tier", str(args.tier)]
    if args.price_point_id:
        return [price_point_flag, args.price_point_id]
    return []


def build_plan(args: argparse.Namespace) -> list[PlannedCommand]:
    plan: list[PlannedCommand] = []

    if args.include_territories:
        add(plan, "territories", "List App Store pricing territories", ["asc", "pricing", "territories", "list", "--paginate"])

    if args.include_subscription_setup:
        territories = args.territories or args.territory
        add(
            plan,
            "subscription-setup",
            "Create subscription product and initial pricing",
            [
                "asc",
                "subscriptions",
                "setup",
                "--app",
                args.app,
                "--group-reference-name",
                args.group_reference_name,
                "--reference-name",
                args.reference_name,
                "--product-id",
                args.product_id,
                "--subscription-period",
                args.subscription_period,
                "--locale",
                args.locale,
                "--display-name",
                args.display_name,
                "--description",
                args.description,
                "--price",
                args.setup_price,
                "--price-territory",
                args.base_territory,
                "--territories",
                territories,
                "--output",
                "json",
            ],
            mutating=True,
        )

    if args.subscription_id:
        add(
            plan,
            "subscription-inspect",
            "Inspect subscription pricing summary",
            ["asc", "subscriptions", "pricing", "summary", "--subscription-id", args.subscription_id, "--territory", args.territory],
        )
        add(
            plan,
            "subscription-inspect",
            "List subscription price points and schedules",
            ["asc", "subscriptions", "pricing", "prices", "list", "--subscription-id", args.subscription_id, "--paginate"],
        )

    if args.include_subscription_import:
        csv_path = str(Path(args.prices_csv))
        add(
            plan,
            "subscription-import",
            "Dry-run subscription price CSV import",
            [
                "asc",
                "subscriptions",
                "pricing",
                "prices",
                "import",
                "--subscription-id",
                args.subscription_id,
                "--input",
                csv_path,
                "--dry-run",
                "--output",
                "table",
            ],
        )
        if args.include_subscription_apply:
            add(
                plan,
                "subscription-import",
                "Apply subscription price CSV import",
                [
                    "asc",
                    "subscriptions",
                    "pricing",
                    "prices",
                    "import",
                    "--subscription-id",
                    args.subscription_id,
                    "--input",
                    csv_path,
                    "--output",
                    "table",
                ],
                mutating=True,
            )

    if args.include_subscription_set:
        command = ["asc", "subscriptions", "pricing", "prices", "set", "--subscription-id", args.subscription_id]
        command.extend(price_selector(args))
        command.extend(["--territory", args.territory])
        if args.start_date:
            command.extend(["--start-date", args.start_date])
        if args.preserved:
            command.append("--preserved")
        add(plan, "subscription-set", "Set one subscription territory price", command, mutating=True)

    if args.include_subscription_availability:
        add(
            plan,
            "subscription-availability",
            "View subscription territory availability",
            ["asc", "subscriptions", "pricing", "availability", "view", "--subscription-id", args.subscription_id],
        )
        add(
            plan,
            "subscription-availability",
            "Edit subscription territory availability",
            [
                "asc",
                "subscriptions",
                "pricing",
                "availability",
                "edit",
                "--subscription-id",
                args.subscription_id,
                "--territories",
                args.territories,
            ],
            mutating=True,
        )

    if args.include_iap_setup:
        add(
            plan,
            "iap-setup",
            "Create IAP product and initial pricing",
            [
                "asc",
                "iap",
                "setup",
                "--app",
                args.app,
                "--type",
                args.iap_type,
                "--reference-name",
                args.reference_name,
                "--product-id",
                args.product_id,
                "--locale",
                args.locale,
                "--display-name",
                args.display_name,
                "--description",
                args.description,
                "--price",
                args.setup_price,
                "--base-territory",
                args.base_territory,
                "--output",
                "json",
            ],
            mutating=True,
        )

    if args.iap_id:
        add(
            plan,
            "iap-inspect",
            "Inspect IAP pricing summary",
            ["asc", "iap", "pricing", "summary", "--iap-id", args.iap_id, "--territory", args.territory],
        )
        add(
            plan,
            "iap-inspect",
            "View IAP pricing schedules",
            ["asc", "iap", "pricing", "schedules", "view", "--iap-id", args.iap_id],
        )

    if args.include_iap_price_points:
        command = ["asc", "iap", "pricing", "price-points", "list", "--iap-id", args.iap_id, "--territory", args.territory, "--paginate"]
        if args.price:
            command.extend(["--price", args.price])
        add(plan, "iap-price-points", "List matching IAP price points", command)

    if args.include_iap_schedule:
        command = ["asc", "iap", "pricing", "schedules", "create", "--iap-id", args.iap_id, "--base-territory", args.base_territory]
        command.extend(price_selector(args, price_point_flag="--price-point-id"))
        if args.start_date:
            command.extend(["--start-date", args.start_date])
        add(plan, "iap-schedule", "Create IAP pricing schedule", command, mutating=True)

    return plan


def render_shell(plan: list[PlannedCommand]) -> str:
    lines = [
        "# App Store pricing command plan",
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
    parser.add_argument("--subscription-id", help="Subscription ID for pricing commands")
    parser.add_argument("--iap-id", help="IAP ID for pricing commands")
    parser.add_argument("--territory", default="USA", help="Primary territory code")
    parser.add_argument("--territories", default="USA,CAN,GBR", help="Comma-separated territory codes")
    parser.add_argument("--base-territory", default="USA", help="Base pricing territory")
    parser.add_argument("--prices-csv", help="Subscription price CSV path")
    parser.add_argument("--price", help="Decimal price")
    parser.add_argument("--tier", type=int, help="Pricing tier")
    parser.add_argument("--price-point-id", help="ASC price point ID")
    parser.add_argument("--start-date", help="Scheduled price change start date")
    parser.add_argument("--preserved", action="store_true", help="Preserve current price relationship when supported")
    parser.add_argument("--group-reference-name", default="Pro", help="Subscription group reference name")
    parser.add_argument("--reference-name", default="Pro Monthly", help="Product reference name")
    parser.add_argument("--product-id", help="Product identifier")
    parser.add_argument("--subscription-period", default="ONE_MONTH", help="Subscription duration")
    parser.add_argument("--iap-type", default="NON_CONSUMABLE", help="IAP product type")
    parser.add_argument("--locale", default="en-US", help="Product localization locale")
    parser.add_argument("--display-name", default="Pro Monthly", help="Product display name")
    parser.add_argument("--description", default="Unlock everything", help="Product description")
    parser.add_argument("--setup-price", default="9.99", help="Initial setup price")
    parser.add_argument("--include-territories", action="store_true", help="Include territory list command")
    parser.add_argument("--include-subscription-setup", action="store_true", help="Include subscription setup command")
    parser.add_argument("--include-subscription-import", action="store_true", help="Include subscription CSV import dry-run")
    parser.add_argument("--include-subscription-apply", action="store_true", help="Include subscription CSV import apply command")
    parser.add_argument("--include-subscription-set", action="store_true", help="Include one-territory subscription set command")
    parser.add_argument("--include-subscription-availability", action="store_true", help="Include subscription availability view/edit commands")
    parser.add_argument("--include-iap-setup", action="store_true", help="Include IAP setup command")
    parser.add_argument("--include-iap-price-points", action="store_true", help="Include IAP price point list command")
    parser.add_argument("--include-iap-schedule", action="store_true", help="Include IAP schedule create command")
    parser.add_argument(
        "--confirming-actions",
        action="store_true",
        help="Required before printing commands that change prices, products, or availability",
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
