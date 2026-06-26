---
name: appstore-notary-runner
description: Use for the concrete macOS Developer ID notarization command path with xcodebuild export plus `asc notarization` submit, status, log, and stapling. Not for broad packaging readiness review or signing-only diagnosis.
---

# App Store Notary Runner

Use for macOS apps distributed outside the App Store with Developer ID signing and Apple notarization.

Use `macos-notarization-packager` first when the artifact is not clearly distribution-ready. Use `macos-signing-inspector` for local code-signing, entitlement, Gatekeeper, or trust-policy diagnosis.

## Preconditions

- Xcode/CLT configured.
- `asc auth login` or `ASC_*`.
- Developer ID Application certificate in keychain.
- App builds for macOS.

## Command Plan Helper

For a deterministic command plan, run the helper from the plugin root:

```bash
python3 "$PLUGIN_ROOT/skills/appstore-notary-runner/scripts/notary_plan.py" \
  --app-name "YourApp" --scheme "YourMacScheme" \
  --archive-path "/tmp/YourApp.xcarchive" \
  --export-path "/tmp/YourAppExport" \
  --app-path "/tmp/YourAppExport/YourApp.app" \
  --zip-path "/tmp/YourAppExport/YourApp.zip" \
  --file "/tmp/YourAppExport/YourApp.zip" \
  --include-archive --include-export --include-zip --include-submit \
  --wait --confirming-actions
```

The helper prints commands only; it does not build, export, upload, staple, or change trust settings. Commands that write local files or submit to Apple require `--confirming-actions`. Pass `--json` for machine-readable output.

## Workflow

1. Run read-only preflight first: signing identities, trust settings, recent notarization submissions, and existing submission status/log when an ID is known.
2. If the artifact is not clearly Developer ID ready, route to `macos-notarization-packager` before exporting or submitting.
3. Archive, export with Developer ID options, verify code-signing authority/timestamp, package as zip/DMG/PKG, then submit.
4. Fetch status/log output and repair signed nested binaries, hardened runtime, timestamp, or trust issues before retrying.
5. Staple only after Apple accepts the notarization submission.

## References

- `references/appstore-notary-runner.md` for detailed preflight, archive, export, submit, status, stapling, DMG, PKG, and troubleshooting commands.
