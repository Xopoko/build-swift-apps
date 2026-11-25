# App Store Notary Runner Command Reference

## Preflight

```bash
security find-identity -v -p codesigning | grep "Developer ID Application"
```

If missing, create the certificate in Apple Developer. ASC API cannot create
Developer ID certificates.

For trust errors such as `Invalid trust settings` or `errSecInternalComponent`,
inspect the trust settings. Identify the specific certificate and override before
changing trust settings.

```bash
security dump-trust-settings
```

## Archive And Export

```bash
xcodebuild archive -scheme "YourMacScheme" -configuration Release \
  -archivePath /tmp/YourApp.xcarchive -destination "generic/platform=macOS"
```

ExportOptions must use `method=developer-id`, `signingStyle=automatic`, and
your `teamID`.

```bash
xcodebuild -exportArchive -archivePath /tmp/YourApp.xcarchive \
  -exportPath /tmp/YourAppExport -exportOptionsPlist ExportOptions.plist
```

Verify the code signature and check the reported authority and timestamp after
export:

```bash
app="/tmp/YourAppExport/YourApp.app"
codesign --verify --deep --strict --verbose=2 "$app"
codesign -dvvv "$app"
```

## Submit The Distribution Artifact

For ZIP distribution:

```bash
artifact="/tmp/YourAppExport/YourApp.zip"
ditto -c -k --keepParent "$app" "$artifact"
```

For DMG distribution, build the final disk image before submission:

```bash
artifact="/tmp/YourApp.dmg"
hdiutil create -volname "YourApp" -srcfolder "$app" -format UDZO "$artifact"
```

For an unsigned flat installer, use a separate Developer ID Installer certificate:

```bash
artifact="/tmp/YourApp-signed.pkg"
productsign --sign "Developer ID Installer: YOUR NAME (TEAM_ID)" unsigned.pkg "$artifact"
```

Once the chosen artifact exists, confirm the flags with `asc notarization submit --help` and submit it:

```bash
asc notarization submit --file "$artifact" --wait
```

## Status And Stapling

```bash
asc notarization status --id "SUBMISSION_ID" --output table
asc notarization log --id "SUBMISSION_ID"
asc notarization list --limit 5 --output table
```

After the submission reaches `Accepted`, staple and verify the exact DMG or PKG
that was submitted:

```bash
xcrun stapler staple "$artifact"
xcrun stapler validate "$artifact"
```

For ZIP distribution, staple and verify the app, then create a new ZIP containing
that stapled app:

```bash
xcrun stapler staple "$app"
xcrun stapler validate "$app"
ditto -c -k --keepParent "$app" "/tmp/YourAppExport/YourApp-stapled.zip"
```

## Troubleshooting

- Not Developer ID signed: re-export with `method=developer-id`.
- Missing secure timestamp: use `xcodebuild -exportArchive` or manual `codesign --timestamp`.
- Large upload timeout: `ASC_UPLOAD_TIMEOUT=5m asc notarization submit --file ./LargeApp.zip --wait`.
- Invalid result: fetch `asc notarization log --id ...`; common causes are unsigned nested binaries, missing hardened runtime, or embedded libraries without timestamps.

See Apple's [notarization workflow](https://developer.apple.com/documentation/security/customizing-the-notarization-workflow) for accepted archive types and stapling rules.
