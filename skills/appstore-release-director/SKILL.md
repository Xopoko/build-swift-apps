---
name: appstore-release-director
description: End-to-end iOS App Store publishing from local repo to App Store Connect readiness, upload, TestFlight, App Review submission/resubmission, or review issue triage, including signing, metadata, privacy, icons, screenshots, subscriptions, and release evidence.
---

# App Store Release Director

Broad release orchestration. For focused `asc` work, delegate to `appstore-connect-cli`, `appstore-id-resolver`, `appstore-archive-uploader`, `appstore-release-planner`, `appstore-review-readiness`, `appstore-metadata-sync`, `appstore-metadata-localizer`, `appstore-screenshot-pipeline`, and `appstore-signing-setup`.

## Workflow

1. Discover release truth:
   - git root, workspace/project, scheme, bundle ID, version/build, deployment target, entitlements, generator ownership;
   - existing handoff/docs: `apple-publishing-handoff.md`, manifest JSON, `release`, `appstore`, `testflight`, `fastlane`, `ExportOptions.plist`.
2. Verify Apple account/signing:
   - team, Team ID, API key, identities, Bundle ID resource/capabilities, distribution cert, provisioning profile;
   - keep `.p8`, `.p12`, profiles, passwords, and decoded plists out of git; prefer `.codex-private/apple/` or a secret store.
3. Prepare App Store Connect:
   - app record, platform, bundle, app info, categories, pricing/availability, age rating, privacy/support URLs, screenshots, App Privacy, review details, release option;
   - for subscriptions, verify products and Terms/EULA link. Standard EULA: `https://www.apple.com/legal/internet-services/itunes/dev/stdeula/`.
4. Compliance preflight:
   - production runtime config, legal URLs return 2xx/3xx, encryption/export compliance, privacy/tracking claims match code/SDKs.
5. Build/test/archive/export/upload:
   - choose unique build number from live ASC state;
   - run required tests/smoke checks;
   - archive for `generic/platform=iOS`, export App Store IPA, validate, upload, wait for processing.
6. Link build and submit/readiness:
   - attach processed build, resolve metadata-only issues before new binaries, cancel/complete old submissions if blocking.
7. Finish evidence:
   - handoff/manifest: version/build, archive/IPA paths, SHA-256, delivery UUID, ASC build state, review submission ID, legal URLs, screenshots, remaining risks.

## References

Load only the current stage:

- `references/end-to-end-workflow.md`
- `references/signing-and-provisioning.md`
- `references/app-store-connect-api.md`
- `references/metadata-compliance.md`
- `references/build-upload-submit.md`
- `references/troubleshooting.md`

Helpers:

- `scripts/make_export_options.py`
- `scripts/appstore_preflight.py`

Run helper scripts with `python3` and inspect `--help`.

## Rules

- Operate from live repo/ASC/App Review state, not memory.
- Never commit Apple secrets/profiles unless explicitly requested and the repo is intended for them.
- Do not overwrite user changes or release docs without reading them.
- Apple requirements change; verify current screenshots, privacy, subscriptions, and review behavior.
- For legal text, draft only practical copy and state which business/legal facts need owner confirmation.
- If blocked by Apple web-only UI, permissions, legal answers, or 2FA, stop with evidence and the smallest required user action.

## Final Report

Report build/version, validation/upload status and delivery UUID, ASC build/review status, legal/privacy/screenshot/subscription/encryption state, files/artifacts changed, tests run, and anything not verified.
