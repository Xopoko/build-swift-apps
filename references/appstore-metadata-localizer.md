# App Store Metadata Localizer Reference

Use this reference only after `appstore-metadata-localizer` is selected and the
agent needs concrete ASC localization commands, supported locale lists, or
translation rules.

## ASC Rules

- Confirm flags first: `asc localizations --help`, `download --help`, `upload --help`, `asc apps info edit --help`.
- Use explicit long flags and JSON for automation; table output is for human selection.
- Prefer deterministic IDs. Do not pick the first row with `head -1`; use `appstore-id-resolver` when needed.
- Do not upload translations without user approval.

## Scope

- Version fields: `description`, `keywords`, `whatsNew`, `supportUrl`, `marketingUrl`, `promotionalText`.
- App-info fields: `name`, `subtitle`, `privacyPolicyUrl`, `privacyChoicesUrl`, `privacyPolicyText`.
- App Store locales: `ar-SA, ca, cs, da, de-DE, el, en-AU, en-CA, en-GB, en-US, es-ES, es-MX, fi, fr-CA, fr-FR, he, hi, hr, hu, id, it, ja, ko, ms, nl-NL, no, pl, pt-BR, pt-PT, ro, ru, sk, sv, th, tr, uk, vi, zh-Hans, zh-Hant`.

## Resolve IDs

```bash
asc apps list --output table
asc versions list --app "APP_ID" --state PREPARE_FOR_SUBMISSION --output table
asc apps info list --app "APP_ID" --output table
```

## Download

Download source and existing localizations:

```bash
asc localizations download --version "VERSION_ID" --path "./localizations"
asc localizations download --app "APP_ID" --type app-info --app-info "APP_INFO_ID" --path "./app-info-localizations"
```

If download is unavailable, inspect with `asc localizations list ...`.

## Strings Format

Write `.strings` files:

```text
"description" = "...";
"keywords" = "native,search,terms";
"whatsNew" = "...";
"promotionalText" = "...";
"subtitle" = "...";
```

## Upload And Verify

Upload only after approval:

```bash
asc localizations upload --version "VERSION_ID" --path "./localizations"
asc localizations upload --app "APP_ID" --type app-info --app-info "APP_INFO_ID" --path "./app-info-localizations"
```

Verify:

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
