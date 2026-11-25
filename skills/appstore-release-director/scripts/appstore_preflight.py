#!/usr/bin/env python3
"""Run local App Store release preflight checks and print a JSON report."""

from __future__ import annotations

import argparse
import hashlib
import json
import plistlib
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit
from xml.parsers.expat import ExpatError
from zipfile import BadZipFile, ZipFile


IDENTITY_FIELDS = {
    "bundle_id": "CFBundleIdentifier",
    "version": "CFBundleShortVersionString",
    "build": "CFBundleVersion",
}


def app_properties(data: bytes) -> tuple[dict[str, str], bool | None]:
    value = plistlib.loads(data)
    if not isinstance(value, dict):
        raise ValueError("expected a plist dictionary")
    identity = {}
    for name, key in IDENTITY_FIELDS.items():
        field = value.get(key)
        if not isinstance(field, str) or not field.strip():
            raise ValueError(f"{key} must be a nonempty string")
        identity[name] = field
    encryption = value.get("ITSAppUsesNonExemptEncryption")
    if encryption is not None and not isinstance(encryption, bool):
        raise ValueError("ITSAppUsesNonExemptEncryption must be a boolean")
    return identity, encryption


def ipa_identity(path: Path) -> dict[str, str]:
    with ZipFile(path) as archive:
        app_plists = []
        for name in archive.namelist():
            parts = name.split("/")
            if (
                len(parts) == 3
                and parts[0] == "Payload"
                and parts[1].endswith(".app")
                and parts[2] == "Info.plist"
            ):
                app_plists.append(name)
        if len(app_plists) != 1:
            raise ValueError("expected exactly one Payload/<app>.app/Info.plist")
        identity, _ = app_properties(archive.read(app_plists[0]))
        return identity


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def check_url(url: str, timeout: float, allow_http: bool) -> dict[str, Any]:
    result: dict[str, Any] = {"url": url, "ok": False}
    schemes = {"https", "http"} if allow_http else {"https"}
    try:
        if urlsplit(url).scheme not in schemes:
            raise ValueError("legal URL must use HTTPS" if not allow_http else "legal URL must use HTTP or HTTPS")
        request = urllib.request.Request(url, headers={"User-Agent": "appstore-preflight/1.0"})
        with urllib.request.urlopen(request, timeout=timeout) as response:
            status = response.getcode()
            final_url = response.geturl()
            result.update({"status": status, "final_url": final_url})
            if urlsplit(final_url).scheme not in schemes:
                raise ValueError("redirect ended on a URL with a disallowed scheme")
            result["ok"] = 200 <= status < 300
    except urllib.error.HTTPError as exc:
        result.update({"status": exc.code, "final_url": exc.geturl(), "error": str(exc)})
    except (OSError, ValueError) as exc:
        result["error"] = str(exc)
    return result


def add_check(checks: list[dict[str, Any]], name: str, ok: bool, **details: Any) -> None:
    checks.append({"name": name, "ok": ok, **details})


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--app-plist", required=True, help="Archived app Info.plist path")
    parser.add_argument("--expected-bundle-id", help="Expected CFBundleIdentifier")
    parser.add_argument("--expected-version", help="Expected CFBundleShortVersionString")
    parser.add_argument("--expected-build", help="Expected CFBundleVersion")
    parser.add_argument("--require-encryption-false", action="store_true", help="Require ITSAppUsesNonExemptEncryption=false")
    parser.add_argument("--ipa", help="Exported IPA to match against the archive and checksum")
    parser.add_argument("--legal-url", action="append", default=[], help="Legal/support URL to verify; repeatable")
    parser.add_argument("--allow-http-legal", action="store_true", help="Allow non-HTTPS legal URLs")
    parser.add_argument("--timeout", type=float, default=12.0, help="HTTP timeout in seconds")
    args = parser.parse_args()

    checks: list[dict[str, Any]] = []
    report: dict[str, Any] = {"checks": checks, "ok": False}

    app_plist_path = Path(args.app_plist).expanduser()
    try:
        identity, encryption = app_properties(app_plist_path.read_bytes())
    except (OSError, ValueError, TypeError, ExpatError, plistlib.InvalidFileException) as exc:
        add_check(checks, "app_plist_identity", False, path=str(app_plist_path), error=str(exc))
        print(json.dumps(report, indent=2, sort_keys=True))
        return 1

    add_check(checks, "app_plist_identity", True)
    report["app_plist"] = {
        "path": str(app_plist_path),
        **identity,
        "uses_non_exempt_encryption": encryption,
    }
    expected_fields = {
        "bundle_id": args.expected_bundle_id,
        "version": args.expected_version,
        "build": args.expected_build,
    }
    for name, expected in expected_fields.items():
        if expected is not None:
            actual = identity[name]
            add_check(checks, f"expected_{name}", actual == expected, expected=expected, actual=actual)

    if args.require_encryption_false:
        add_check(checks, "uses_non_exempt_encryption_false", encryption is False, actual=encryption)

    if args.ipa:
        ipa_path = Path(args.ipa).expanduser()
        try:
            exported_identity = ipa_identity(ipa_path)
            report["ipa"] = {
                "path": str(ipa_path),
                **exported_identity,
                "sha256": sha256(ipa_path),
                "bytes": ipa_path.stat().st_size,
            }
            add_check(checks, "ipa_matches_archive", exported_identity == identity)
        except (OSError, ValueError, TypeError, BadZipFile, RuntimeError, ExpatError, plistlib.InvalidFileException) as exc:
            add_check(checks, "ipa_matches_archive", False, path=str(ipa_path), error=str(exc))

    url_results = []
    for url in args.legal_url:
        result = check_url(url, args.timeout, args.allow_http_legal)
        url_results.append(result)
        check_details = {key: value for key, value in result.items() if key != "ok"}
        add_check(checks, "legal_url_reachable", bool(result.get("ok")), **check_details)
    if url_results:
        report["legal_urls"] = url_results

    ok = all(item["ok"] for item in checks)
    report["ok"] = ok
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
