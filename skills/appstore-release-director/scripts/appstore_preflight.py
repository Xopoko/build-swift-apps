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


def load_plist(path: Path) -> dict[str, Any]:
    with path.open("rb") as fh:
        value = plistlib.load(fh)
    if not isinstance(value, dict):
        raise ValueError(f"{path} did not contain a plist dictionary")
    return value


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def check_url(url: str, timeout: float) -> dict[str, Any]:
    result: dict[str, Any] = {"url": url, "ok": False}
    for method in ("HEAD", "GET"):
        request = urllib.request.Request(url, method=method, headers={"User-Agent": "appstore-preflight/1.0"})
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                status = response.getcode()
                result.pop("error", None)
                result.update({"method": method, "status": status, "ok": 200 <= status < 400})
                return result
        except urllib.error.HTTPError as exc:
            result.update({"method": method, "status": exc.code, "error": str(exc)})
            if method == "HEAD":
                continue
            return result
        except Exception as exc:  # noqa: BLE001 - report exact connectivity failure.
            result.update({"method": method, "error": str(exc)})
            if method == "HEAD":
                continue
            return result
    return result


def add_check(checks: list[dict[str, Any]], name: str, ok: bool, **details: Any) -> None:
    item = {"name": name, "ok": ok}
    item.update(details)
    checks.append(item)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--app-plist", required=True, help="Archived app Info.plist path")
    parser.add_argument("--expected-bundle-id", help="Expected CFBundleIdentifier")
    parser.add_argument("--expected-version", help="Expected CFBundleShortVersionString")
    parser.add_argument("--expected-build", help="Expected CFBundleVersion")
    parser.add_argument("--require-encryption-false", action="store_true", help="Require ITSAppUsesNonExemptEncryption=false")
    parser.add_argument("--ipa", help="Exported IPA path to verify and checksum")
    parser.add_argument("--legal-url", action="append", default=[], help="Legal/support URL to verify; repeatable")
    parser.add_argument("--allow-http-legal", action="store_true", help="Allow non-HTTPS legal URLs")
    parser.add_argument("--timeout", type=float, default=12.0, help="HTTP timeout in seconds")
    args = parser.parse_args()

    checks: list[dict[str, Any]] = []
    report: dict[str, Any] = {"checks": checks}

    app_plist_path = Path(args.app_plist).expanduser()
    add_check(checks, "app_plist_exists", app_plist_path.exists(), path=str(app_plist_path))
    if not app_plist_path.exists():
        print(json.dumps(report, indent=2, sort_keys=True))
        return 1

    try:
        plist = load_plist(app_plist_path)
        report["app_plist"] = {
            "path": str(app_plist_path),
            "bundle_id": plist.get("CFBundleIdentifier"),
            "version": plist.get("CFBundleShortVersionString"),
            "build": plist.get("CFBundleVersion"),
            "uses_non_exempt_encryption": plist.get("ITSAppUsesNonExemptEncryption"),
        }
        add_check(checks, "app_plist_readable", True)
    except Exception as exc:  # noqa: BLE001 - report exact plist failure.
        add_check(checks, "app_plist_readable", False, error=str(exc))
        print(json.dumps(report, indent=2, sort_keys=True))
        return 1

    expected_fields = {
        "bundle_id": ("CFBundleIdentifier", args.expected_bundle_id),
        "version": ("CFBundleShortVersionString", args.expected_version),
        "build": ("CFBundleVersion", args.expected_build),
    }
    for name, (plist_key, expected) in expected_fields.items():
        if expected is None:
            continue
        actual = plist.get(plist_key)
        add_check(checks, f"expected_{name}", actual == expected, expected=expected, actual=actual)

    if args.require_encryption_false:
        actual = plist.get("ITSAppUsesNonExemptEncryption")
        add_check(checks, "uses_non_exempt_encryption_false", actual is False, actual=actual)

    if args.ipa:
        ipa_path = Path(args.ipa).expanduser()
        exists = ipa_path.exists()
        add_check(checks, "ipa_exists", exists, path=str(ipa_path))
        if exists:
            report["ipa"] = {
                "path": str(ipa_path),
                "sha256": sha256(ipa_path),
                "bytes": ipa_path.stat().st_size,
            }

    url_results = []
    for url in args.legal_url:
        if not args.allow_http_legal:
            add_check(checks, "legal_url_https", url.startswith("https://"), url=url)
        result = check_url(url, args.timeout)
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
