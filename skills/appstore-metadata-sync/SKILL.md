---
name: appstore-metadata-sync
description: Pull, edit, validate, dry-run, and push App Store metadata with the current canonical `asc metadata` JSON workflow. Use for metadata, localizations, keywords, quick field edits, or legacy fastlane migration.
---

# App Store Metadata Sync

Prefer canonical `asc metadata` JSON for app-info and version fields. Use `.strings` or fastlane flows only when specifically needed.

## Canonical Workflow

```bash
asc metadata pull --app "APP_ID" --version "1.2.3" --platform IOS --dir "./metadata"
```

If multiple app-info records exist:

```bash
asc apps info list --app "APP_ID" --output table
asc metadata pull --app "APP_ID" --app-info "APP_INFO_ID" --version "1.2.3" --platform IOS --dir "./metadata"
```

Edit:

- `metadata/app-info/<locale>.json`: `name`, `subtitle`, `privacyPolicyUrl`, `privacyChoicesUrl`, `privacyPolicyText`
- `metadata/version/<version>/<locale>.json`: `description`, `keywords`, `marketingUrl`, `promotionalText`, `supportUrl`, `whatsNew`

Copyright is not localized:

```bash
asc versions update --version-id "VERSION_ID" --copyright "2026 Your Company"
```

Validate and apply:

```bash
asc metadata validate --dir "./metadata" --output table
asc metadata validate --dir "./metadata" --subscription-app --output table
asc metadata push --app "APP_ID" --version "1.2.3" --platform IOS --dir "./metadata" --dry-run --output table
asc metadata push --app "APP_ID" --version "1.2.3" --platform IOS --dir "./metadata"
```

`asc metadata apply` is equivalent when the user wants that command shape.

## Keywords

```bash
asc metadata keywords diff --app "APP_ID" --version "1.2.3" --platform IOS --dir "./metadata"
asc metadata keywords apply --app "APP_ID" --version "1.2.3" --platform IOS --dir "./metadata" --confirm
asc metadata keywords import --dir "./metadata" --version "1.2.3" --locale "en-US" --input "./keywords.csv"
asc metadata keywords sync --app "APP_ID" --version "1.2.3" --platform IOS --dir "./metadata" --input "./keywords.csv"
```

## Quick Edits

Always pass `--version-id` or `--version` plus `--platform` for version fields:

```bash
asc apps info edit --app "APP_ID" --version-id "VERSION_ID" --locale "en-US" --whats-new "Bug fixes"
asc apps info edit --app "APP_ID" --version "1.2.3" --platform IOS --locale "en-US" --description "..."
asc apps info edit --app "APP_ID" --version "1.2.3" --platform IOS --locale "en-US" --keywords "keyword1,keyword2"
```

For app-info setup:

```bash
asc app-setup info set --app "APP_ID" --primary-locale "en-US" --privacy-policy-url "https://example.com/privacy"
asc app-setup info set --app "APP_ID" --locale "en-US" --name "Your App" --subtitle "Your subtitle"
```

## Alternate Formats

`.strings`:

```bash
asc localizations download --version "VERSION_ID" --path "./localizations"
asc localizations upload --version "VERSION_ID" --path "./localizations" --dry-run
asc localizations upload --app "APP_ID" --type app-info --app-info "APP_INFO_ID" --path "./app-info-localizations" --dry-run
```

Fastlane legacy:

```bash
asc migrate export --app "APP_ID" --version-id "VERSION_ID" --output-dir "./fastlane"
asc migrate validate --fastlane-dir "./fastlane"
asc migrate import --app "APP_ID" --version-id "VERSION_ID" --fastlane-dir "./fastlane" --dry-run
```

Limits: name/subtitle 30, keywords 100, description/What's New 4000, promotional text 170. Use table output for human verification and JSON for automation.
