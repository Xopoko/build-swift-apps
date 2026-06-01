# Build, Upload, And Submit

Use this reference for the concrete local build and upload flow.

## Variables

Set project-specific variables before running commands:

```bash
project_path="$PWD/MyApp.xcodeproj"
workspace_path="$PWD/MyApp.xcworkspace"
scheme="MyApp"
configuration="Release"
team_id="ABCDE12345"
bundle_id="com.example.myapp"
profile_name="MyApp App Store"
release_dir="$PWD/.codex/release/appstore-YYYY-MM-DD-buildN"
api_key="$ASC_KEY_ID"
api_issuer="$ASC_ISSUER_ID"
api_key_path="$ASC_PRIVATE_KEY_PATH"
```

Use either `-project "$project_path"` or `-workspace "$workspace_path"`, not both.

## Bump Build Number

Find the source of truth before editing. Examples:

- Tuist: `Project.swift`
- Xcode project: `project.pbxproj`
- Generated Info.plist: only edit if it is the true source
- Expo: `app.json`, `app.config.*`, or native project after prebuild
- Flutter: `pubspec.yaml`
- Fastlane: `fastlane/Appfile`, `Fastfile`, or lane variables

Confirm the next build number against App Store Connect live state.

## Regenerate Project If Needed

Examples:

```bash
tuist generate --no-open
npx expo prebuild --platform ios
pod install
```

Use the repository's documented commands. Do not run a generator blindly if the repo does not use one.

## Test

Run the project's release-relevant tests:

```bash
# Resolve the newest available iPhone simulator and iOS runtime first.
# If local runtime inspection is unavailable, use the current fallback family:
# platform=iOS Simulator,name=iPhone 17,OS=latest (iOS 26 family).
xcodebuild test \
  -project "$project_path" \
  -scheme "$scheme" \
  -destination 'platform=iOS Simulator,name=<latest available iPhone simulator>,OS=latest'
```

If tests are not available or a simulator is unavailable, record that explicitly in the final report.

## Archive

```bash
mkdir -p "$release_dir"

xcodebuild archive \
  -project "$project_path" \
  -scheme "$scheme" \
  -configuration "$configuration" \
  -destination 'generic/platform=iOS' \
  -archivePath "$release_dir/$scheme.xcarchive" \
  CODE_SIGN_STYLE=Manual \
  DEVELOPMENT_TEAM="$team_id" \
  CODE_SIGN_IDENTITY='iOS Distribution' \
  PROVISIONING_PROFILE_SPECIFIER="$profile_name" \
  | tee "$release_dir/archive.log"
```

For a workspace, replace `-project "$project_path"` with `-workspace "$workspace_path"`.

## Generate ExportOptions.plist

Use the helper script:

```bash
python3 <skill-dir>/scripts/make_export_options.py \
  --bundle-id "$bundle_id" \
  --profile-name "$profile_name" \
  --team-id "$team_id" \
  --output "$release_dir/ExportOptions.plist"
```

Inspect it:

```bash
plutil -p "$release_dir/ExportOptions.plist"
```

## Export IPA

```bash
export_dir="$release_dir/export"
rm -rf "$export_dir"
mkdir -p "$export_dir"

xcodebuild -exportArchive \
  -archivePath "$release_dir/$scheme.xcarchive" \
  -exportPath "$export_dir" \
  -exportOptionsPlist "$release_dir/ExportOptions.plist" \
  | tee "$release_dir/export.log"
```

Find the IPA:

```bash
find "$export_dir" -maxdepth 1 -name '*.ipa' -print
shasum -a 256 "$export_dir/$scheme.ipa" | tee "$release_dir/ipa.sha256"
```

## Preflight

Run the helper against the archived app Info.plist:

```bash
python3 <skill-dir>/scripts/appstore_preflight.py \
  --app-plist "$release_dir/$scheme.xcarchive/Products/Applications/$scheme.app/Info.plist" \
  --expected-bundle-id "$bundle_id" \
  --expected-version "1.0" \
  --expected-build "42" \
  --require-encryption-false \
  --ipa "$export_dir/$scheme.ipa" \
  --legal-url "https://example.com/privacy" \
  --legal-url "https://example.com/terms"
```

Add project-specific checks for runtime configuration. For example, inspect a runtime plist in the archive and fail if it points to localhost or staging.

## Validate IPA

```bash
xcrun altool --validate-app \
  -f "$export_dir/$scheme.ipa" \
  --type ios \
  --api-key "$api_key" \
  --api-issuer "$api_issuer" \
  --p8-file-path "$api_key_path" \
  2>&1 | tee "$release_dir/altool-validate.log"
```

## Upload IPA

```bash
xcrun altool --upload-app \
  -f "$export_dir/$scheme.ipa" \
  --type ios \
  --api-key "$api_key" \
  --api-issuer "$api_issuer" \
  --p8-file-path "$api_key_path" \
  2>&1 | tee "$release_dir/altool-upload.log"
```

Extract and record the delivery UUID from the upload output.

## Poll Build Processing

```bash
xcrun altool --build-status \
  --delivery-id "$delivery_uuid" \
  --api-key "$api_key" \
  --api-issuer "$api_issuer" \
  --p8-file-path "$api_key_path" \
  --output-format json \
  | tee "$release_dir/altool-build-status.json"
```

Wait until the build is valid and App Store eligible before linking it to a version.

## Link And Submit

Use App Store Connect API tooling or the project release script to:

1. Find the App Store version resource.
2. Find the processed build resource.
3. Update the App Store version build relationship.
4. Verify the relationship.
5. Create or update review submission.
6. Add the App Store version item.
7. Submit for review.
8. Verify final state.

If only metadata changed after a rejection, a new binary is not always necessary. If local code changed or the user explicitly asks for a fresh build, upload a new build and link it.
