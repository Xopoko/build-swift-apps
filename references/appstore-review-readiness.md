# App Store Review Readiness Command Reference

Use this reference only after `appstore-review-readiness` is selected and the
agent needs concrete `asc` commands for repair, submission, monitoring, or
retry work.

## Readiness Checks

```bash
asc builds info --build-id "BUILD_ID"
asc validate --app "APP_ID" --version "1.2.3" --platform IOS --output table
asc validate --app "APP_ID" --version "1.2.3" --platform IOS --strict --output table
asc validate --app "APP_ID" --version-id "VERSION_ID" --platform IOS --output table
```

Check `processingState=VALID`, encryption, content rights, localizations,
screenshots, app-info/privacy URL, digital goods, IAP/subscriptions, and App
Privacy.

## Common Repairs

```bash
asc encryption declarations list --app "APP_ID"
asc encryption declarations create --app "APP_ID" --app-description "Uses standard HTTPS/TLS" \
  --contains-proprietary-cryptography=false --contains-third-party-cryptography=true \
  --available-on-french-store=true
asc encryption declarations assign-builds --id "DECLARATION_ID" --build "BUILD_ID"
asc encryption declarations exempt-declare --plist "./Info.plist"

asc apps content-rights view --app "APP_ID"
asc apps content-rights edit --app "APP_ID" --uses-third-party-content=false

asc metadata pull --app "APP_ID" --version "1.2.3" --platform IOS --dir "./metadata"
asc metadata validate --dir "./metadata" --output table
asc metadata push --app "APP_ID" --version "1.2.3" --platform IOS --dir "./metadata" --dry-run --output table

asc screenshots list --version-localization "LOC_ID" --output table
asc screenshots validate --path "./screenshots" --device-type "IPHONE_65" --output table
asc validate iap --app "APP_ID" --output table
asc validate subscriptions --app "APP_ID" --output table
```

App Privacy publish state is not fully verifiable through the public API. Use
the experimental web flow or confirm manually:

```bash
asc web privacy pull --app "APP_ID" --out "./privacy.json"
asc web privacy plan --app "APP_ID" --file "./privacy.json"
asc web privacy apply --app "APP_ID" --file "./privacy.json"
asc web privacy publish --app "APP_ID" --confirm
```

## Submit

```bash
asc review submit --app "APP_ID" --version "1.2.3" --build "BUILD_ID" --dry-run --output table
asc review submit --app "APP_ID" --version "1.2.3" --build "BUILD_ID" --confirm

asc publish appstore --app "APP_ID" --ipa "./App.ipa" --version "1.2.3" --submit --dry-run --output table
asc publish appstore --app "APP_ID" --ipa "./App.ipa" --version "1.2.3" --submit --confirm
```

Add `--wait` when build processing should be awaited.

## Multi-Item Submissions

```bash
asc review submissions-create --app "APP_ID" --platform IOS
asc review items-add --submission "SUBMISSION_ID" --item-type appStoreVersions --item-id "VERSION_ID"
asc review items-add --submission "SUBMISSION_ID" --item-type gameCenterChallengeVersions --item-id "GC_CHALLENGE_VERSION_ID"
asc review submissions-submit --id "SUBMISSION_ID" --confirm
```

For non-renewing IAPs that must be selected with the next version and public
APIs reject the path, use the web fallback and document that it is unofficial:

```bash
asc web review iaps attach --app "APP_ID" --iap-id "IAP_ID" --confirm
```

## Monitor And Retry

```bash
asc status --app "APP_ID"
asc submit status --id "SUBMISSION_ID"
asc submit status --version-id "VERSION_ID"
asc review submissions-list --app "APP_ID" --paginate
asc submit cancel --id "SUBMISSION_ID" --confirm
asc review submissions-cancel --id "SUBMISSION_ID" --confirm
```

For state errors, re-check valid build attachment, export compliance, content
rights, localizations/screenshots, review details, pricing/availability, and
App Privacy. macOS uses the same review flow with `--platform MAC_OS`.
