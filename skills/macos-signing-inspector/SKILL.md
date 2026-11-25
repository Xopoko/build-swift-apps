---
name: macos-signing-inspector
description: "macOS app signing artifacts: inspect code signatures, entitlements, hardened runtime, sandbox, Gatekeeper, and trust failures; exclude distribution packaging and notarization submission."
---

# macOS Signing Inspector

Before invoking Apple-only binaries, confirm the execution context is macOS. From Windows or Linux, run those steps in a Mac SSH project or through an already configured remote transport; do not retry missing Apple binaries locally.

Use `macos-notarization-packager` when the goal is a distributable notarized artifact. Use `appstore-notary-runner` when the next step is executing `asc notarization` submit/status/log/staple commands.

## Workflow

1. Locate the `.app` or executable and identify the bundle's main executable
   in `Contents/MacOS/`.
2. Inspect the actual signature and entitlements with
   `codesign -dvvv --entitlements :- <path>`. Verify signature validity with
   `codesign --verify --strict --verbose=2 <path>`. Inspect any nested code
   named in the failure.
3. Use `spctl -a -vv <path>` for Gatekeeper assessment. Compare against
   `security find-identity -p codesigning -v` if the signer is in question.
   Read source entitlements and Info.plist with `plutil -p <path>` for
   configuration mismatches.
4. Report the inspected artifact, the observed signature or trust failure,
   and the shortest repair or validation sequence. Base any proposed
   entitlement on source configuration or the required capability.

## Resources

- `references/binary-tools.md` — Mach-O inspection (`nm`, `otool`, `llvm-objdump`, `dsymutil`), `.pkg` packaging (`pkgbuild`, `productbuild`), and raw `notarytool` command forms.
