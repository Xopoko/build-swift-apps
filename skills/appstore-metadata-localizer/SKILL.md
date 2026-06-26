---
name: appstore-metadata-localizer
description: Use when App Store listing text must be translated or market-adapted across locales, including descriptions, keywords, What's New, subtitles, names, privacy text, and App Store Connect languages. Not for non-translation metadata edits, release-note drafting, or subscription/IAP display-name localization.
---

# App Store Metadata Localizer

Pull source metadata, translate/adapt it, validate limits, get approval, then upload version or app-info localizations.

Use `appstore-metadata-sync` for canonical JSON field edits that are not translation-first. Use `appstore-release-notes-writer` when the requested artifact is only What's New or promotional text. Use `appstore-subscription-localizer` for subscription, group, or IAP display names.

## Local Lint Helper

After writing or editing localized `.strings` or metadata JSON, run the bundled limit checker:

```bash
python3 "$PLUGIN_ROOT/skills/appstore-metadata-localizer/scripts/metadata_localization_lint.py" \
  "./localizations" "./app-info-localizations" --recursive
```

The helper checks App Store field limits for `name`, `subtitle`, `keywords`, `description`, `whatsNew`, and `promotionalText`. It does not translate, rewrite files, upload, or call ASC. Pass `--json` for machine-readable output.

## Workflow

1. Confirm current `asc localizations` flags, then resolve app, version, and app-info IDs deterministically.
2. Download source and existing localizations; if download is unavailable, inspect with `asc localizations list`.
3. Translate one target locale at a time from the source locale. Preserve formatting and meaning; do not translate from memory.
4. Adapt keywords for native App Store search behavior instead of literal translation.
5. Run `metadata_localization_lint.py`, then show a field-by-locale summary table and wait for approval.
6. Upload only after approval, then verify with the matching `asc localizations list` command.

## Translation Rules

Use formal, professional App Store register. Keep the app name unchanged unless the user explicitly asks to translate it. For updates, download current localization, show a diff, get approval, then upload.

## References

- `references/appstore-metadata-localizer.md` for supported locales, detailed ASC commands, field scope, `.strings` format, and translation rules.
