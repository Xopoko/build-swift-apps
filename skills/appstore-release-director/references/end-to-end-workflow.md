# End-to-End Workflow

This is the generic release path from a local repository to an App Store Connect build that is submitted or ready to submit for App Review.

## 1. Orient In The Repository

Run lightweight discovery first:

```bash
pwd
git rev-parse --show-toplevel
git status --short
rg --files | rg '(^|/)(Project\.swift|project\.pbxproj|Package\.swift|Podfile|Package\.resolved|fastlane|ExportOptions|Info\.plist|Privacy|appstore|testflight|release|screenshots)'
```

Find the build system and the source of truth:

- Xcode project or workspace: `.xcodeproj`, `.xcworkspace`
- Project generator: Tuist, XcodeGen, Expo prebuild, Flutter, React Native, CocoaPods, SwiftPM
- Version source: `Project.swift`, `project.pbxproj`, generated `Info.plist`, app config, Fastlane files, or CI variables
- Release docs: handoff markdown, manifest JSON, run folders, previous upload logs
- Runtime config: production API URLs, relay URLs, feature flags, entitlement files

Do not edit generated Xcode files until you know whether a generator owns them.

## 2. Create A Release Workspace

Use a dated release folder that is ignored by git unless the project already has a convention:

```bash
release_dir="$PWD/.codex/release/appstore-YYYY-MM-DD-buildN"
mkdir -p "$release_dir"
```

Save logs and generated artifacts there:

- `archive.log`
- `export.log`
- `altool-validate.log`
- `altool-upload.log`
- `altool-build-status.json`
- `ExportOptions.plist`
- `.xcarchive`
- exported `.ipa`
- screenshot upload manifests or App Store Connect response JSON

## 3. Build A Release Handoff

If none exists, create `docs/apple-publishing-handoff.md` or a project-appropriate equivalent. Keep it factual and update it during the run.

Record:

- Project root, scheme, workspace/project path, bundle ID, marketing version, latest uploaded build
- Team name, Team ID, App Store Connect app Apple ID, ASC issuer ID, ASC key ID, local API key path
- Signing identity common name and SHA-1
- Distribution certificate ID and expiry
- Provisioning profile name, UUID, App ID, Team ID, expiry, entitlements
- Archive path, IPA path, IPA SHA-256
- Delivery UUID and build processing state
- App Store version resource ID, linked build ID, review submission ID, review state
- Privacy, support, terms, and EULA URLs
- Screenshot sets and App Store device types
- Known publication issues and exact resolution

Use a machine-readable manifest too when useful:

```json
{
  "platform": "ios",
  "bundle_id": "com.example.app",
  "version": "1.0",
  "build": "42",
  "team_id": "ABCDE12345",
  "app_store_app_id": "1234567890",
  "ipa_sha256": "...",
  "delivery_uuid": "...",
  "build_status": "VALID",
  "review_submission_id": "...",
  "review_state": "WAITING_FOR_REVIEW"
}
```

## 4. Recheck Live State

Before changing version/build numbers or review submissions, query App Store Connect:

- Existing app record by bundle ID or app Apple ID
- App Store versions and current version state
- Build list for the marketing version
- Review submission state
- Subscriptions or IAP state, if applicable
- App Privacy and metadata completeness, if exposed through the API

The next build number should be greater than both local state and the latest uploaded App Store Connect build for the same marketing version.

## 5. Prepare Metadata Before Binary Work

Metadata can block review even when the IPA is valid. Verify early:

- Privacy Policy URL
- Support URL
- Terms of Use or EULA URL, especially for auto-renewable subscriptions
- App description, subtitle, keywords, categories, copyright
- Screenshots for each required device family
- App Privacy answers
- Review notes and demo access
- Age rating, content rights, pricing, availability
- Subscription products, prices, localizations, review screenshot

If the project uses a backend to serve legal pages, deploy and verify those URLs before submitting review.

## 6. Build And Upload

Follow `references/build-upload-submit.md` for concrete commands. The core sequence is:

1. Bump build number.
2. Regenerate project if needed.
3. Run tests.
4. Archive Release for generic iOS.
5. Export IPA with App Store Connect export options.
6. Preflight Info.plist, IPA, runtime config, legal URLs.
7. Validate IPA.
8. Upload IPA.
9. Poll processing.
10. Link build to App Store version.
11. Submit or resubmit review.

## 7. Close The Loop

At the end, update durable docs before reporting completion:

- Handoff markdown
- Manifest JSON
- Release run folder logs
- Screenshot inventory
- Any backend deployment evidence required for legal/support pages

Final status should state what is live-verified, what is only locally verified, and what remains blocked by Apple review or user action.
