---
name: appstore-signing-setup
description: Set up App Store Connect bundle IDs, capabilities, certificates, provisioning profiles, local profile install, and encrypted signing sync with `asc`.
---

# App Store Signing Setup

Use for new signing assets, rotation, or team sharing.

## Preconditions

Auth is configured (`asc auth login` or `ASC_*` env vars), bundle id/platform are known, and certificate creation has a CSR or will use `--generate-csr`.

## Workflow

1. Bundle ID:
   - `asc bundle-ids list --paginate`
   - `asc bundle-ids create --identifier "com.example.app" --name "Example" --platform IOS`
2. Capabilities:
   - `asc bundle-ids capabilities list --bundle "BUNDLE_ID"`
   - `asc bundle-ids capabilities add --bundle "BUNDLE_ID" --capability ICLOUD`
   - use `--settings '[{"key":"ICLOUD_VERSION","options":[{"key":"XCODE_13","enabled":true}]}]'` when required
3. Certificate:
   - `asc certificates list --certificate-type IOS_DISTRIBUTION`
   - `asc certificates create --certificate-type IOS_DISTRIBUTION --csr "./cert.csr"`
   - `asc certificates create --certificate-type IOS_DISTRIBUTION --generate-csr --key-out "./signing/dist.key" --csr-out "./signing/dist.csr"`
4. Profile:
   - `asc profiles create --name "AppStore Profile" --profile-type IOS_APP_STORE --bundle "BUNDLE_ID" --certificate "CERT_ID"`
   - development/ad-hoc also pass `--device "DEVICE_ID"`
5. Download, inspect, install:
   - `asc profiles download --id "PROFILE_ID" --output "./profiles/AppStore.mobileprovision"`
   - `asc profiles inspect --path "./profiles/AppStore.mobileprovision" --output table`
   - `asc profiles inspect --path "./profiles/AppStore.mobileprovision" --entitlements --output markdown`
   - `asc profiles local install --path "./profiles/AppStore.mobileprovision"`
   - `asc profiles local list --output table`

## Rotation

- `asc certificates revoke --id "CERT_ID" --confirm`
- `asc profiles delete --id "PROFILE_ID" --confirm`
- `asc profiles local clean --expired --dry-run`
- `asc profiles local clean --expired --confirm`

## Encrypted Sync

Use `asc signing sync` as a lightweight match-style encrypted git store.

```bash
asc signing sync push \
  --bundle-id "com.example.app" \
  --profile-type IOS_APP_STORE \
  --repo "git@github.com:team/certs.git" \
  --password "$MATCH_PASSWORD"

asc signing sync pull \
  --repo "git@github.com:team/certs.git" \
  --password "$MATCH_PASSWORD" \
  --output-dir "./signing"
```

`--password` falls back to `ASC_MATCH_PASSWORD`. Pull writes files only; keychain import/profile install is separate.

## Notes

Check `--help` for enum values. Use `--paginate` for large accounts. `--certificate` accepts comma-separated IDs. Device management uses `asc devices` with UDID. Local profile commands operate on disk, not ASC API resources.
