#!/usr/bin/env python3
"""Create an App Store Connect ExportOptions.plist for xcodebuild -exportArchive."""

from __future__ import annotations

import argparse
import plistlib
from pathlib import Path


def parse_bool(value: str) -> bool:
    normalized = value.strip().lower()
    if normalized in {"1", "true", "yes", "y"}:
        return True
    if normalized in {"0", "false", "no", "n"}:
        return False
    raise argparse.ArgumentTypeError(f"Expected boolean, got {value!r}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle-id", required=True, help="App bundle identifier, e.g. com.example.app")
    parser.add_argument("--profile-name", required=True, help="App Store provisioning profile name")
    parser.add_argument("--team-id", required=True, help="Apple Developer Team ID")
    parser.add_argument("--output", required=True, help="Output ExportOptions.plist path")
    parser.add_argument("--method", default="app-store-connect", help="Export method")
    parser.add_argument("--signing-certificate", default="iOS Distribution", help="Signing certificate label")
    parser.add_argument("--upload-symbols", type=parse_bool, default=True, help="Whether to upload dSYMs")
    parser.add_argument("--strip-swift-symbols", type=parse_bool, default=True, help="Whether to strip Swift symbols")
    args = parser.parse_args()

    plist = {
        "destination": "export",
        "method": args.method,
        "provisioningProfiles": {
            args.bundle_id: args.profile_name,
        },
        "signingCertificate": args.signing_certificate,
        "signingStyle": "manual",
        "stripSwiftSymbols": args.strip_swift_symbols,
        "teamID": args.team_id,
        "uploadSymbols": args.upload_symbols,
    }

    output = Path(args.output).expanduser().resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("wb") as fh:
        plistlib.dump(plist, fh, sort_keys=True)

    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
