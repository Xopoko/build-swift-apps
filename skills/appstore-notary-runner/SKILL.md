---
name: appstore-notary-runner
description: macOS Developer ID notarization commands for xcodebuild export, `asc notarization` submit/status/log, and stapling. Excludes packaging-readiness reviews and signing-only diagnosis.
---

# App Store Notary Runner

Before invoking Apple-only binaries, confirm the execution context is macOS. From Windows or Linux, run those steps in a Mac SSH project or through an already configured remote transport; do not retry missing Apple binaries locally.

Use for macOS apps distributed outside the App Store with Developer ID signing and Apple notarization.

Use `macos-notarization-packager` first when the artifact is not clearly distribution-ready. Use `macos-signing-inspector` for local code-signing, entitlement, Gatekeeper, or trust-policy diagnosis.

## Preconditions

- Xcode/CLT configured.
- `asc auth login` or `ASC_*`.
- Developer ID Application certificate in keychain.
- App builds for macOS.

## Workflow

1. Check the signing identity. If a submission ID already exists for this artifact, inspect its status and log before submitting again.
2. If the artifact is not clearly Developer ID ready, route to `macos-notarization-packager` before exporting or submitting.
3. Verify signing and the timestamp, package as ZIP, DMG, or PKG, then submit the artifact intended for distribution.
4. Check the submission status and log. Repair rejected artifacts before retrying.
5. After `Accepted`, staple and validate the ticket on the submitted DMG or PKG. For ZIP distribution, staple its app bundle and regenerate the ZIP.

## References

- `references/appstore-notary-runner.md` for detailed preflight, archive, export, submit, status, stapling, DMG, PKG, and troubleshooting commands.
