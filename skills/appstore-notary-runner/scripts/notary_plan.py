#!/usr/bin/env python3
"""Print a deterministic macOS Developer ID notarization command plan.

The script only renders commands. It does not build, export, upload, staple,
modify trust settings, or call Apple services.
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
    mutating_requested = any(
        (
            args.include_archive,
            args.include_export,
            args.include_zip,
            args.include_submit,
            args.include_staple,
            args.include_dmg,
            args.include_pkg,
            args.include_trust_repair,
        )
    )
    if mutating_requested and not args.confirming_actions:
        parser.error("local-write or upload commands require --confirming-actions")
    if args.include_archive and not args.scheme:
        parser.error("--include-archive requires --scheme")
    if args.include_export and not args.archive_path:
        parser.error("--include-export requires --archive-path")
    if args.include_zip and not args.app_path:
        parser.error("--include-zip requires --app-path")
    if args.include_submit and not args.file:
        parser.error("--include-submit requires --file")
    if args.include_staple and not args.app_path:
        parser.error("--include-staple requires --app-path")
    if args.include_dmg and not args.app_path:
        parser.error("--include-dmg requires --app-path")
    if args.include_pkg and not (args.unsigned_pkg and args.signed_pkg and args.installer_identity):
        parser.error("--include-pkg requires --unsigned-pkg, --signed-pkg, and --installer-identity")


def build_plan(args: argparse.Namespace) -> list[PlannedCommand]:
    plan: list[PlannedCommand] = []

    add(plan, "preflight", "List Developer ID Application signing identities", ["security", "find-identity", "-v", "-p", "codesigning"])
    add(plan, "preflight", "Inspect Developer ID trust settings", ["security", "dump-trust-settings"])

    if args.include_trust_repair:
        cert_path = str(Path(args.cert_pem))
        keychain_path = str(Path("~/Library/Keychains/login.keychain-db").expanduser())
        add(
            plan,
            "trust-repair",
            "Export Developer ID Application certificate from login keychain",
            [
                "sh",
                "-c",
                f"security find-certificate -c 'Developer ID Application' -p {shlex.quote(keychain_path)} > {shlex.quote(cert_path)}",
            ],
            mutating=True,
        )
        add(plan, "trust-repair", "Remove custom trust override for exported certificate", ["security", "remove-trusted-cert", cert_path], mutating=True)

    if args.include_archive:
        archive_path = args.archive_path or f"/tmp/{args.app_name}.xcarchive"
        add(
            plan,
            "archive",
            "Archive macOS app for Developer ID export",
            [
                "xcodebuild",
                "archive",
                "-scheme",
                args.scheme,
                "-configuration",
                args.configuration,
                "-archivePath",
                archive_path,
                "-destination",
                "generic/platform=macOS",
            ],
            mutating=True,
        )

    if args.include_export:
        export_path = args.export_path or f"/tmp/{args.app_name}Export"
        add(
            plan,
            "export",
            "Export Developer ID signed app",
            [
                "xcodebuild",
                "-exportArchive",
                "-archivePath",
                args.archive_path,
                "-exportPath",
                export_path,
                "-exportOptionsPlist",
                args.export_options_plist,
            ],
            mutating=True,
        )

    if args.app_path:
        add(plan, "verify", "Inspect exported code-signing chain and timestamp", ["codesign", "-dvvv", args.app_path])

    if args.include_zip:
        zip_path = args.zip_path or f"/tmp/{args.app_name}.zip"
        add(plan, "package", "Create notarization zip with parent app bundle", ["ditto", "-c", "-k", "--keepParent", args.app_path, zip_path], mutating=True)

    if args.include_submit:
        submit = ["asc", "notarization", "submit", "--file", args.file]
        if args.wait:
            submit.append("--wait")
            submit.extend(["--poll-interval", args.poll_interval, "--timeout", args.timeout])
        add(plan, "submit", "Submit file to Apple notarization", submit, mutating=True)

    if args.submission_id:
        add(plan, "status", "Inspect notarization status", ["asc", "notarization", "status", "--id", args.submission_id, "--output", "table"])
        add(plan, "status", "Fetch notarization log", ["asc", "notarization", "log", "--id", args.submission_id])

    add(plan, "status", "List recent notarization submissions", ["asc", "notarization", "list", "--limit", str(args.list_limit), "--output", "table"])

    if args.include_staple:
        add(plan, "staple", "Staple notarization ticket to app", ["xcrun", "stapler", "staple", args.app_path], mutating=True)

    if args.include_dmg:
        dmg_path = args.dmg_path or f"/tmp/{args.app_name}.dmg"
        add(
            plan,
            "dmg",
            "Create compressed DMG from app bundle",
            ["hdiutil", "create", "-volname", args.app_name, "-srcfolder", args.app_path, "-ov", "-format", "UDZO", dmg_path],
            mutating=True,
        )
        add(plan, "dmg", "Staple notarization ticket to DMG", ["xcrun", "stapler", "staple", dmg_path], mutating=True)

    if args.include_pkg:
        add(
            plan,
            "pkg",
            "Sign PKG with Developer ID Installer certificate",
            ["productsign", "--sign", args.installer_identity, args.unsigned_pkg, args.signed_pkg],
            mutating=True,
        )
        add(plan, "pkg", "Submit signed PKG to Apple notarization", ["asc", "notarization", "submit", "--file", args.signed_pkg, "--wait"], mutating=True)

    return plan


def render_shell(plan: list[PlannedCommand]) -> str:
    lines = [
        "# macOS Developer ID notarization command plan",
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
    parser.add_argument("--app-name", default="YourApp", help="Display name used for default /tmp artifact paths")
    parser.add_argument("--scheme", help="macOS scheme to archive")
    parser.add_argument("--configuration", default="Release", help="Archive configuration")
    parser.add_argument("--archive-path", help="xcarchive path")
    parser.add_argument("--export-path", help="Export directory")
    parser.add_argument("--export-options-plist", default="ExportOptions.plist", help="Developer ID ExportOptions.plist path")
    parser.add_argument("--app-path", help="Exported .app bundle path")
    parser.add_argument("--zip-path", help="Notarization zip output path")
    parser.add_argument("--file", help="File to submit for notarization")
    parser.add_argument("--submission-id", help="Notarization submission ID")
    parser.add_argument("--poll-interval", default="30s", help="Polling interval for --wait submit commands")
    parser.add_argument("--timeout", default="1h", help="Timeout for --wait submit commands")
    parser.add_argument("--list-limit", type=int, default=5, help="Recent submission list limit")
    parser.add_argument("--dmg-path", help="DMG output path")
    parser.add_argument("--unsigned-pkg", help="Unsigned PKG path")
    parser.add_argument("--signed-pkg", help="Signed PKG path")
    parser.add_argument("--installer-identity", help="Developer ID Installer signing identity")
    parser.add_argument("--cert-pem", default="/tmp/devid-cert.pem", help="Temporary Developer ID certificate PEM path")
    parser.add_argument("--wait", action="store_true", help="Add --wait, --poll-interval, and --timeout to notarization submit")
    parser.add_argument("--include-archive", action="store_true", help="Include xcodebuild archive command")
    parser.add_argument("--include-export", action="store_true", help="Include xcodebuild exportArchive command")
    parser.add_argument("--include-zip", action="store_true", help="Include ditto zip command")
    parser.add_argument("--include-submit", action="store_true", help="Include asc notarization submit command")
    parser.add_argument("--include-staple", action="store_true", help="Include app stapling command")
    parser.add_argument("--include-dmg", action="store_true", help="Include DMG creation and stapling commands")
    parser.add_argument("--include-pkg", action="store_true", help="Include PKG signing and notarization commands")
    parser.add_argument("--include-trust-repair", action="store_true", help="Include trust override repair commands")
    parser.add_argument(
        "--confirming-actions",
        action="store_true",
        help="Required before printing local-write, trust-repair, upload, or stapling commands",
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
