---
name: appstore-metadata-sync
description: Use when App Store listing metadata in canonical `./metadata` JSON needs field edits, validation, push, keyword sync, or legacy fastlane migration. Not for translation-first localization, release-note drafting, or subscription/IAP display-name localizations.
---

# App Store Metadata Sync

Prefer canonical `asc metadata` JSON for app-info and version fields. Use `.strings` or fastlane flows only when specifically needed.

Use `appstore-metadata-localizer` when the main work is translation/adaptation across locales. Use `appstore-release-notes-writer` for What's New copy. Use `appstore-subscription-localizer` for subscription, group, or IAP display-name localizations.

## Command Plan Helper

For a deterministic dry-run command plan, run the helper from the plugin root:

```bash
python3 "$PLUGIN_ROOT/skills/appstore-metadata-sync/scripts/metadata_sync_plan.py" \
  --app "APP_ID" --version "1.2.3" --platform IOS --dir "./metadata" \
  --app-info "APP_INFO_ID" --version-id "VERSION_ID" \
  --include-keywords --keywords-csv "./keywords.csv"
```

The helper prints commands only; it does not call ASC, mutate metadata, or read credentials. Pass `--json` for machine-readable output. Pass `--confirming-actions` only after manually verifying generated `--confirm` commands.

## Workflow

1. Pull canonical metadata JSON into `./metadata` before editing unless the user already provided a fresh metadata tree.
2. Resolve `APP_INFO_ID` when multiple app-info records exist.
3. Edit the owning JSON fields: app-info fields for name/subtitle/privacy text and version fields for description, keywords, marketing URL, promotional text, support URL, and What's New.
4. Validate locally, then run `push --dry-run`; apply/push without dry-run only after the diff and target app/version are confirmed.
5. Use alternate `.strings` or fastlane migration flows only for legacy repos or explicit user requests.

Limits: name/subtitle 30, keywords 100, description/What's New 4000, promotional text 170. Use table output for human verification and JSON for automation.

## References

- `references/appstore-metadata-sync.md` for detailed canonical JSON, keyword, quick-edit, `.strings`, and fastlane commands.
