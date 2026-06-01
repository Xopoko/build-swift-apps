---
name: appstore-subscription-localizer
description: Bulk-create or update App Store subscription, subscription group, and in-app purchase display-name localizations with `asc`. Use to fill missing locales without clicking through App Store Connect.
---

# App Store Subscription Localizer

Use for subscription/IAP display names and descriptions, not general App Store metadata (`appstore-metadata-localizer` owns that).

## Preconditions

- `asc auth login` or `ASC_*` env vars.
- `APP_ID`, group/subscription/IAP IDs resolved.
- Products already exist.

Supported locales: `ar-SA, ca, cs, da, de-DE, el, en-AU, en-CA, en-GB, en-US, es-ES, es-MX, fi, fr-CA, fr-FR, he, hi, hr, hu, id, it, ja, ko, ms, nl-NL, no, pl, pt-BR, pt-PT, ro, ru, sk, sv, th, tr, uk, vi, zh-Hans, zh-Hant`.

## Commands

Resolve:

```bash
asc subscriptions groups list --app "APP_ID" --output table
asc subscriptions list --group-id "GROUP_ID" --output table
asc iap list --app "APP_ID" --output table
```

List existing localizations before creating anything:

```bash
asc subscriptions localizations list --subscription-id "SUB_ID" --paginate --output table
asc subscriptions groups localizations list --group-id "GROUP_ID" --paginate --output table
asc iap localizations list --iap-id "IAP_ID" --paginate --output table
```

Create missing locales:

```bash
asc subscriptions localizations create --subscription-id "SUB_ID" --locale "LOCALE" --name "Display Name"
asc subscriptions groups localizations create --group-id "GROUP_ID" --locale "LOCALE" --name "Group Display Name"
asc iap localizations create --iap-id "IAP_ID" --locale "LOCALE" --name "Display Name"
```

Optional fields:

```bash
asc subscriptions groups localizations create --group-id "GROUP_ID" --locale "LOCALE" --name "Group Display Name" --custom-app-name "My App"
asc iap localizations create --iap-id "IAP_ID" --locale "LOCALE" --name "Unlock All Features" --description "One-time purchase..."
```

Update existing:

```bash
asc subscriptions localizations update --id "LOC_ID" --name "New Name"
asc subscriptions groups localizations update --id "LOC_ID" --name "New Group Name"
asc iap localizations update --localization-id "LOC_ID" --name "New Name"
```

For full-app coverage: list groups, localize each group, list each group's subscriptions, localize each subscription, then localize IAPs.

## Agent Rules

- Never create before listing; duplicate locale creates fail.
- Skip locales that already exist unless the user asked to update.
- If the user gives one display name, use it for all locales; if they provide per-locale names, honor them.
- Pass `--description` only when supplied.
- Use table output for verification, JSON for automation.
- Process many products sequentially by group for readable output.
- On per-locale failure, record the locale/error, continue, and report all failures together.
- Verify with the matching list command after the batch.
