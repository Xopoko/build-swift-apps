---
name: appstore-archive-uploader
description: Manage Xcode version/build numbers, archive, export, upload, and publish IPA/PKG artifacts with `asc xcode` helpers before TestFlight or App Store submission.
---

# App Store Archive Uploader

Prefer `asc xcode archive` and `asc xcode export` over raw `xcodebuild` when they fit.

## Preconditions

Xcode/CLT installed; signing identity/profiles or automatic signing available; ASC auth configured for upload/build lookup.

## Version And Build

```bash
asc xcode version view
asc xcode version edit --version "1.3.0" --build-number "42"
asc xcode version bump --type build
asc xcode version bump --type patch
asc builds next-build-number --app "APP_ID" --version "1.2.3" --platform IOS --output json
asc xcode version edit --build-number "NEXT_BUILD"
```

Use `--project-dir`, `--project`, and `--target` for multi-project/target determinism.

## iOS/tvOS/visionOS

```bash
asc xcode archive --workspace "App.xcworkspace" --scheme "App" --configuration Release \
  --clean --archive-path ".asc/artifacts/App.xcarchive" \
  --xcodebuild-flag=-destination --xcodebuild-flag=generic/platform=iOS --output json

asc xcode export --archive-path ".asc/artifacts/App.xcarchive" \
  --export-options "ExportOptions.plist" --ipa-path ".asc/artifacts/App.ipa" \
  --xcodebuild-flag=-allowProvisioningUpdates --output json
```

Use `--project "App.xcodeproj"` for project-only apps. Add `--wait` to export/upload/publish when the next step depends on processed builds.

Upload/distribute:

```bash
asc builds upload --app "APP_ID" --ipa ".asc/artifacts/App.ipa" --wait
asc publish testflight --app "APP_ID" --ipa ".asc/artifacts/App.ipa" --group "GROUP_ID" --wait
asc publish appstore --app "APP_ID" --ipa ".asc/artifacts/App.ipa" --version "1.2.3" --wait
asc publish appstore --app "APP_ID" --ipa ".asc/artifacts/App.ipa" --version "1.2.3" --wait --submit --confirm
```

## macOS App Store

```bash
asc xcode archive --project "MacApp.xcodeproj" --scheme "MacApp" --configuration Release \
  --clean --archive-path ".asc/artifacts/MacApp.xcarchive" \
  --xcodebuild-flag=-destination --xcodebuild-flag=generic/platform=macOS --output json

xcodebuild -exportArchive -archivePath ".asc/artifacts/MacApp.xcarchive" \
  -exportPath ".asc/artifacts/MacAppExport" -exportOptionsPlist "ExportOptions.plist" \
  -allowProvisioningUpdates

asc builds upload --app "APP_ID" --pkg ".asc/artifacts/MacAppExport/MacApp.pkg" \
  --version "1.0.0" --build-number "123" --wait
```

PKG uploads require explicit `--version` and `--build-number`.

## Fallback And Troubleshooting

- Use raw `xcodebuild` only when `asc xcode archive/export --help` cannot cover an option; try `--xcodebuild-flag` first.
- No profiles: add `--xcodebuild-flag=-allowProvisioningUpdates`, verify Xcode account/profiles, or use `appstore-signing-setup`.
- Build number too low: resolve `asc builds next-build-number`, edit, rebuild, upload.
- Missing macOS icon: fix ICNS/asset catalog sizes, rebuild, export/upload.
- Use `--overwrite` only when intentionally replacing local artifacts.
- For submission readiness, use `appstore-review-readiness`.
