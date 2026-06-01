---
name: appstore-notary-runner
description: Archive, export, sign, notarize, staple, and troubleshoot macOS Developer ID distribution with xcodebuild and `asc notarization`.
---

# App Store Notary Runner

Use for macOS apps distributed outside the App Store with Developer ID signing and Apple notarization.

## Preconditions

- Xcode/CLT configured.
- `asc auth login` or `ASC_*`.
- Developer ID Application certificate in keychain.
- App builds for macOS.

## Preflight

```bash
security find-identity -v -p codesigning | grep "Developer ID Application"
```

If missing, create the cert in Apple Developer; ASC API cannot create Developer ID certs.

For trust errors such as `Invalid trust settings` or `errSecInternalComponent`:

```bash
security dump-trust-settings 2>&1 | grep -A1 "Developer ID"
security find-certificate -c "Developer ID Application" -p ~/Library/Keychains/login.keychain-db > /tmp/devid-cert.pem
security remove-trusted-cert /tmp/devid-cert.pem
```

Verify chain/timestamp after export:

```bash
codesign -dvvv "/tmp/YourAppExport/YourApp.app" 2>&1 | grep -E "Authority|Timestamp"
```

## Archive, Export, Submit

```bash
xcodebuild archive -scheme "YourMacScheme" -configuration Release \
  -archivePath /tmp/YourApp.xcarchive -destination "generic/platform=macOS"
```

ExportOptions must use `method=developer-id`, `signingStyle=automatic`, and your `teamID`.

```bash
xcodebuild -exportArchive -archivePath /tmp/YourApp.xcarchive \
  -exportPath /tmp/YourAppExport -exportOptionsPlist ExportOptions.plist
ditto -c -k --keepParent "/tmp/YourAppExport/YourApp.app" "/tmp/YourAppExport/YourApp.zip"
asc notarization submit --file "/tmp/YourAppExport/YourApp.zip" --wait
```

Custom polling:

```bash
asc notarization submit --file "/tmp/YourAppExport/YourApp.zip" --wait --poll-interval 30s --timeout 1h
```

## Status, Logs, Stapling

```bash
asc notarization status --id "SUBMISSION_ID" --output table
asc notarization log --id "SUBMISSION_ID"
asc notarization list --limit 5 --output table
xcrun stapler staple "/tmp/YourAppExport/YourApp.app"
```

For DMG:

```bash
hdiutil create -volname "YourApp" -srcfolder "/tmp/YourAppExport/YourApp.app" -ov -format UDZO "/tmp/YourApp.dmg"
xcrun stapler staple "/tmp/YourApp.dmg"
```

For PKG, use a separate Developer ID Installer certificate:

```bash
productsign --sign "Developer ID Installer: YOUR NAME (TEAM_ID)" unsigned.pkg signed.pkg
asc notarization submit --file signed.pkg --wait
```

## Troubleshooting

- Invalid trust settings: remove custom trust overrides as above.
- Not Developer ID signed: re-export with `method=developer-id`.
- Missing secure timestamp: use `xcodebuild -exportArchive` or manual `codesign --timestamp`.
- Large upload timeout: `ASC_UPLOAD_TIMEOUT=5m asc notarization submit --file ./LargeApp.zip --wait`.
- Invalid result: fetch `asc notarization log --id ...`; common causes are unsigned nested binaries, missing hardened runtime, or embedded libraries without timestamps.

Notes: `asc notarization` uses Apple Notary API v2, streams uploads to Apple's S3 bucket, supports multipart over 5 GB, and should be checked with `asc notarization submit --help`.
