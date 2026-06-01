# Signing And Provisioning

Use this reference when creating or verifying Apple signing assets.

## Required Objects

An App Store release normally needs:

- Apple Developer Program team membership with App Manager, Admin, or Account Holder access for the needed operations.
- Bundle ID / App ID matching the app's `CFBundleIdentifier`.
- Enabled capabilities matching the app entitlements.
- Apple Distribution certificate with private key installed in the local keychain or CI secret store.
- App Store provisioning profile for the Bundle ID and distribution certificate.
- App Store Connect API key with enough permissions for metadata, builds, and review operations.

## Local Inspection

Inspect signing identities:

```bash
security find-identity -p codesigning -v
security find-certificate -a -c 'Apple Distribution' -p > "$release_dir/distribution-certs.pem"
```

Inspect an installed provisioning profile:

```bash
profile="$HOME/Library/MobileDevice/Provisioning Profiles/<UUID>.mobileprovision"
security cms -D -i "$profile" > "$release_dir/profile.plist"
plutil -p "$release_dir/profile.plist"
```

Check the important profile fields:

- `UUID`
- `Name`
- `TeamIdentifier`
- `ApplicationIdentifierPrefix`
- `Entitlements.application-identifier`
- `Entitlements.beta-reports-active`
- enabled capabilities such as App Groups, Push, Associated Domains, Keychain Groups
- `ExpirationDate`
- `DeveloperCertificates`

The profile App ID must equal `TEAMID.bundle.id`. Entitlements in the archive must be compatible with the profile.

## Secret Handling

Recommended local layout:

```text
.codex-private/apple/
  api-keys/AuthKey_<KEY_ID>.p8
  certificates/
  provisioning-profiles/
  SHA256SUMS
```

Add `.codex-private/` to `.gitignore`. Use permissions:

```bash
chmod 700 .codex-private .codex-private/apple
chmod 600 .codex-private/apple/api-keys/AuthKey_*.p8
```

Do not commit:

- `.p8` API keys
- `.p12` exports
- private key passwords
- provisioning profiles
- decoded profile plists
- keychain exports

It is acceptable to record non-secret identifiers in the handoff: Team ID, key ID, issuer ID, certificate resource ID, profile name, profile UUID, certificate SHA-1/SHA-256, and expiry dates.

## App Store Connect API Environment

Many tools accept these variables:

```bash
export ASC_ISSUER_ID='<issuer-uuid>'
export ASC_KEY_ID='<key-id>'
export ASC_PRIVATE_KEY_PATH="$PWD/.codex-private/apple/api-keys/AuthKey_<key-id>.p8"
```

For `xcrun altool`, pass values explicitly:

```bash
--api-key "$ASC_KEY_ID" \
--api-issuer "$ASC_ISSUER_ID" \
--p8-file-path "$ASC_PRIVATE_KEY_PATH"
```

## Creating Or Recreating Assets

Prefer existing repo scripts or documented team tooling. If working manually:

1. Create or locate the Bundle ID in Apple Developer / App Store Connect.
2. Enable required capabilities on the Bundle ID.
3. Create an Apple Distribution certificate or reuse a valid one whose private key is installed locally.
4. Create an App Store provisioning profile for the Bundle ID and certificate.
5. Download and install the profile to `~/Library/MobileDevice/Provisioning Profiles/`.
6. Verify the profile UUID, expiry, Team ID, and entitlements.
7. Archive using manual signing with `DEVELOPMENT_TEAM`, `CODE_SIGN_IDENTITY`, and `PROVISIONING_PROFILE_SPECIFIER`.

If profile creation fails because capabilities are missing, fix the Bundle ID capabilities first and regenerate the profile afterwards.

## CI Notes

For CI, prefer a secret-backed setup:

- API key stored as a masked secret file or secure variable.
- `.p12` certificate stored encrypted with a passphrase secret.
- Provisioning profile stored as a secure file.
- Temporary keychain created during CI and deleted after the job.

Never print private key contents or certificate passphrases into logs.
