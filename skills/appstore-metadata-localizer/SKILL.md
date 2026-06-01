---
name: appstore-metadata-localizer
description: Translate and sync App Store metadata across locales with LLM assistance and `asc localizations`. Use for app descriptions, keywords, what's new, subtitles, app names, privacy URLs/text, and adding App Store Connect languages.
---

# App Store Metadata Localizer

Pull source metadata, translate/adapt it, validate limits, get approval, then upload version or app-info localizations.

## ASC Rules

- Confirm flags first: `asc localizations --help`, `download --help`, `upload --help`, `asc apps info edit --help`.
- Use explicit long flags and JSON for automation; table output is for human selection.
- Prefer deterministic IDs. Do not pick the first row with `head -1`; use `appstore-id-resolver` when needed.
- Do not upload translations without user approval.

## Scope

- Version fields: `description`, `keywords`, `whatsNew`, `supportUrl`, `marketingUrl`, `promotionalText`.
- App-info fields: `name`, `subtitle`, `privacyPolicyUrl`, `privacyChoicesUrl`, `privacyPolicyText`.
- App Store locales: `ar-SA, ca, cs, da, de-DE, el, en-AU, en-CA, en-GB, en-US, es-ES, es-MX, fi, fr-CA, fr-FR, he, hi, hr, hu, id, it, ja, ko, ms, nl-NL, no, pl, pt-BR, pt-PT, ro, ru, sk, sv, th, tr, uk, vi, zh-Hans, zh-Hant`.

## Workflow

1. Resolve IDs:
   ```bash
   asc apps list --output table
   asc versions list --app "APP_ID" --state PREPARE_FOR_SUBMISSION --output table
   asc apps info list --app "APP_ID" --output table
   ```
2. Download source and existing localizations:
   ```bash
   asc localizations download --version "VERSION_ID" --path "./localizations"
   asc localizations download --app "APP_ID" --type app-info --app-info "APP_INFO_ID" --path "./app-info-localizations"
   ```
   If download is unavailable, inspect with `asc localizations list ...`.
3. Translate one target locale at a time from the source locale. Preserve formatting and meaning; do not translate from memory.
4. Enforce limits before upload:
   - `name`: 30
   - `subtitle`: 30
   - `keywords`: 100 comma-separated chars
   - `description`: 4000
   - `whatsNew`: 4000
   - `promotionalText`: 170
5. Write `.strings` files:
   ```text
   "description" = "...";
   "keywords" = "native,search,terms";
   "whatsNew" = "...";
   "promotionalText" = "...";
   "subtitle" = "...";
   ```
6. Show a field-by-locale summary table and wait for approval.
7. Upload:
   ```bash
   asc localizations upload --version "VERSION_ID" --path "./localizations"
   asc localizations upload --app "APP_ID" --type app-info --app-info "APP_INFO_ID" --path "./app-info-localizations"
   ```
8. Verify:
   ```bash
   asc localizations list --version "VERSION_ID" --output table
   asc localizations list --app "APP_ID" --type app-info --app-info "APP_INFO_ID" --output table
   ```

## Translation Rules

- Use formal, professional App Store register. Use formal "you" forms where the language distinguishes them.
- `description`: natural local-market copy, same formatting, <= 4000 chars.
- `keywords`: do not literally translate; choose native App Store search terms, comma-separated, no app name, <= 100 chars.
- `whatsNew`: concise release-note translation.
- `promotionalText`: localized hook, <= 170 chars.
- `subtitle`: creative adaptation, <= 30 chars.
- `name`: keep original unless the user explicitly asks to translate.
- For updates, download current localization, show a diff, get approval, then upload.

## Related Skills

- Use `appstore-id-resolver` when only app/version names are known.
- Use `appstore-metadata-sync` for non-translation metadata operations.
- Use `appstore-subscription-localizer` for subscription/IAP display names.
