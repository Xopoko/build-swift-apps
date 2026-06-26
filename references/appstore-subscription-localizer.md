# App Store Subscription Localizer Command Reference

Use this reference only after `appstore-subscription-localizer` is selected and
the agent needs concrete `asc` commands for subscription groups, subscriptions,
or IAP display-name/description localization.

## Supported Locales

`ar-SA, ca, cs, da, de-DE, el, en-AU, en-CA, en-GB, en-US, es-ES, es-MX, fi,
fr-CA, fr-FR, he, hi, hr, hu, id, it, ja, ko, ms, nl-NL, no, pl, pt-BR, pt-PT,
ro, ru, sk, sv, th, tr, uk, vi, zh-Hans, zh-Hant`.

## Resolve IDs

```bash
asc subscriptions groups list --app "APP_ID" --output table
asc subscriptions list --group-id "GROUP_ID" --output table
asc iap list --app "APP_ID" --output table
```

## List Existing Localizations

List before creating anything:

```bash
asc subscriptions localizations list --subscription-id "SUB_ID" --paginate --output table
asc subscriptions groups localizations list --group-id "GROUP_ID" --paginate --output table
asc iap localizations list --iap-id "IAP_ID" --paginate --output table
```

## Create Missing Locales

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

## Update Existing Locales

```bash
asc subscriptions localizations update --id "LOC_ID" --name "New Name"
asc subscriptions groups localizations update --id "LOC_ID" --name "New Group Name"
asc iap localizations update --localization-id "LOC_ID" --name "New Name"
```

For full-app coverage: list groups, localize each group, list each group's
subscriptions, localize each subscription, then localize IAPs.

## Rules

- Never create before listing; duplicate locale creates fail.
- Skip locales that already exist unless the user asked to update.
- If the user gives one display name, use it for all locales; if they provide per-locale names, honor them.
- Pass `--description` only when supplied.
- Use table output for verification, JSON for automation.
- Process many products sequentially by group for readable output.
- On per-locale failure, record the locale/error, continue, and report all failures together.
- Verify with the matching list command after the batch.
