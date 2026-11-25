---
name: appstore-metadata-sync
description: "App Store metadata JSON: edit, validate, push, or sync canonical `./metadata`, plus legacy fastlane migration via `asc migrate`. Excludes translation-first work, standalone release notes, and IAP/subscription names."
---

# App Store Metadata Sync

Prefer canonical `asc metadata` JSON for app-info and version fields. Use `.strings` or fastlane flows only when specifically needed.

Use `appstore-metadata-localizer` when the main work is translation/adaptation across locales. Use `appstore-release-notes-writer` for What's New copy. Use `appstore-subscription-localizer` for subscription, group, or IAP display-name localizations.

## Workflow

1. Pull canonical metadata JSON into `./metadata` before editing unless the user already provided a fresh metadata tree.
2. Resolve `APP_INFO_ID` when multiple app-info records exist.
3. Edit the owning JSON fields: app-info fields for name/subtitle/privacy text and version fields for description, keywords, marketing URL, promotional text, support URL, and What's New.
4. Validate locally, then run `push --dry-run`; apply/push without dry-run only after the diff and target app/version are confirmed.
5. Use alternate `.strings` or fastlane migration flows only for legacy repos or explicit user requests.

## References

- `references/appstore-metadata-sync.md` for detailed canonical JSON, keyword, quick-edit, `.strings`, and fastlane commands.
