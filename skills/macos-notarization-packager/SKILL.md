---
name: macos-notarization-packager
description: "macOS distribution artifacts: inspect Developer ID archives, app bundles, hardened runtime, nested signing, and notarization readiness; exclude local signing-only diagnosis and direct `asc notarization` execution."
---

# macOS Notarization Packager

Before invoking Apple-only binaries, confirm the execution context is macOS. From Windows or Linux, run those steps in a Mac SSH project or through an already configured remote transport; do not retry missing Apple binaries locally.

## Quick Start

Use this skill when the work is about shipping the app rather than merely
running it locally: archives, exported app bundles, notarization readiness,
hardened runtime, or distribution validation.

Use `macos-signing-inspector` for local signing/trust diagnosis on an existing artifact. Use `appstore-notary-runner` when the artifact is ready and the task is to run `asc notarization` submit/status/log/staple commands. For raw `pkgbuild`/`productbuild`/`notarytool` command forms, see `../macos-signing-inspector/references/binary-tools.md`.

## Workflow

1. Confirm the distribution goal.
   - Local archive validation
   - Signed distributable app
   - Notarization troubleshooting

2. Inspect the artifact.
   - Validate app bundle structure.
   - Check nested frameworks, helper tools, and entitlements.

3. Inspect signing and runtime prerequisites.
   - Hardened runtime
   - Signing identity
   - Nested code signatures
   - Required entitlements

4. Explain notarization readiness or failure.
   - Separate packaging issues from trust-policy symptoms.
   - Point to the minimum follow-up validation commands.

## Guardrails

- Do not present notarization as required for ordinary local debug runs.
- Call out when you lack the actual exported artifact and are inferring from project settings.
- Keep advice concrete and verifiable.

## Output Expectations

Provide:
- what artifact or settings were inspected
- whether the app looks distribution-ready
- the top missing prerequisite or failure mode
- the next validation or repair step
