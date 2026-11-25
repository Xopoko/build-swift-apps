---
name: appstore-metadata-localizer
description: "App Store listing text: translate and market-adapt descriptions, keywords, What's New, names, subtitles, and privacy text across locales. Excludes non-translation edits, standalone release notes, and IAP/subscription names."
---

# App Store Metadata Localizer

Pull source metadata, translate/adapt it, validate limits, get approval, then upload version or app-info localizations.

Use `appstore-metadata-sync` for canonical JSON field edits that are not translation-first. Use `appstore-release-notes-writer` when the requested artifact is only What's New or promotional text. Use `appstore-subscription-localizer` for subscription, group, or IAP display names.

## Workflow

1. Confirm current `asc localizations` flags, then resolve app, version, and app-info IDs deterministically.
2. Download source and existing localizations; if download is unavailable, inspect with `asc localizations list`.
3. Translate one target locale at a time from the source locale. Preserve formatting and meaning; do not translate from memory.
4. Adapt keywords for native App Store search behavior instead of literal translation.
5. For `.strings`, use `asc localizations upload --dry-run` for the matching version or app-info record. It checks the file syntax, supported fields, and field limits. For canonical JSON, use `asc metadata validate` and follow `appstore-metadata-sync` for push.
6. If the CLI or required authentication is unavailable, translate from supplied source files and report which locales could be translated and what still needs validation or upload.
7. Review the diff before applying approved changes, then verify with the matching `asc localizations list` command.

## Translation Rules

Use formal, professional App Store register. Keep the app name unchanged unless the user explicitly asks to translate it.

## References

- `references/appstore-metadata-localizer.md` for supported locales, detailed ASC commands, field scope, `.strings` format, and translation rules.
