# Troubleshooting

Use this reference when a release or review submission fails.

## Automated App Review Message: Missing Terms Of Use

Symptom:

```text
The submission offers auto-renewable subscriptions but does not include a functional link to the Terms of Use (EULA) in the app's metadata.
```

Fix:

1. Add a functional Terms of Use link to app metadata.
2. If using Apple's standard EULA, include `https://www.apple.com/legal/internet-services/itunes/dev/stdeula/`.
3. If using a custom EULA, configure it in App Store Connect.
4. Verify links return HTTP 2xx or 3xx.
5. Resubmit review. A new binary is not required unless app code changed or Apple asks for one.

## Missing Compliance / Export Encryption

Symptom:

- TestFlight or App Store Connect asks for export compliance on each upload.
- Build cannot be used until compliance is answered.

Fix:

- If accurate, set `ITSAppUsesNonExemptEncryption = false` in the app Info.plist source of truth.
- Verify the archived app contains the key.
- If the app uses non-exempt encryption, answer compliance correctly in App Store Connect.

## App Privacy Required

Symptom:

- API or UI reports app data usage or privacy answers are required.
- Submission cannot proceed.

Fix:

- Complete App Privacy nutrition label in App Store Connect.
- Ensure answers match SDKs and backend behavior.
- Record final answers in handoff if API cannot read/write them cleanly.

## Old Review Submission Blocks New One

Symptom:

- API refuses to create or submit a new review item because the version is part of another submission.
- UI shows a rejected or stale submission.

Fix:

1. Query review submissions.
2. Cancel the stale active submission if possible.
3. Wait for terminal state.
4. Create a new submission and add the current App Store version.
5. Submit and verify state.

## Build Processing Stuck

Symptom:

- Upload succeeded but build is not available for selection.
- `altool --build-status` remains pending.

Fix:

- Poll by delivery UUID.
- Check App Store Connect build list.
- Wait; processing can take time.
- If processing ends in invalid state, inspect email and App Store Connect build errors.

## Invalid Provisioning Profile Or Signing

Symptom:

- Archive or export fails with signing errors.
- Export says profile does not include an entitlement.
- App Store Connect rejects invalid signature.

Fix:

- Verify `CFBundleIdentifier`, Team ID, profile App ID, and entitlements.
- Ensure the distribution certificate private key is installed.
- Recreate the App Store profile after enabling capabilities on the Bundle ID.
- Use manual signing values that match the profile.

## Wrong Runtime Configuration

Symptom:

- IPA uploads, but the app points to localhost, staging, or missing backend config.

Fix:

- Inspect archived resources, not only source.
- Open runtime plists or generated config files inside the `.xcarchive`.
- Add a preflight check for required production values.
- Upload a replacement build if the binary contains wrong config.

## App Store Connect API Gap

Symptom:

- API key tooling cannot perform a required operation.
- Operation requires Apple ID session, 2FA, or web UI.

Fix:

- Document the exact blocking operation.
- Use App Store Connect web UI if available.
- Do not claim completion until the live state is verified after the manual step.

## Screenshot Or Media Problems

Symptom:

- Screenshot set incomplete.
- Upload state is not `COMPLETE`.
- Device type missing.

Fix:

- Verify current required device types in App Store Connect.
- Re-render screenshots at valid dimensions.
- Upload missing assets.
- Confirm each screenshot set is complete before review submission.

## Metadata Changed But Binary Did Not

If App Review rejected only metadata, prefer fixing metadata and resubmitting the same valid build. Upload a new build when:

- User explicitly asks for a new build.
- Local app code changed and should be included.
- Apple specifically requires a new binary.
- The old binary contains wrong runtime config, privacy behavior, entitlement, or compliance issue.
