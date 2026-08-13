---
name: appstore-subscription-localizer
description: "App Store subscription localization: create or update localized display names and descriptions for groups, subscriptions, and IAPs with `asc`; exclude app listing metadata, release notes, keywords, screenshots, and pricing."
---

# App Store Subscription Localizer

Use for subscription/IAP display names and descriptions, not general App Store metadata (`appstore-metadata-localizer` owns that).

Use `appstore-pricing-planner` for price points, availability, or schedules. Use `appstore-revenuecat-sync` when the work also maps ASC products to RevenueCat offerings or entitlements.

## Preconditions

- `asc auth login` or `ASC_*` env vars.
- `APP_ID`, group/subscription/IAP IDs resolved.
- Products already exist.

## Command Plan Helper

For a deterministic command plan, run the helper from the plugin root:

```bash
python3 "$PLUGIN_ROOT/skills/appstore-subscription-localizer/scripts/subscription_localization_plan.py" \
  --app "APP_ID" --group-id "GROUP_ID" --subscription-id "SUB_ID" --iap-id "IAP_ID" \
  --locale "en-US,fr-FR" --name "Display Name"
```

The helper prints commands only; it does not call ASC or change localizations. Create/update commands require `--confirming-actions`. Pass `--json` for machine-readable output.

## Workflow

1. Resolve `APP_ID`, group IDs, subscription IDs, IAP IDs, and existing localization IDs before mutation.
2. List existing localizations before creating anything; duplicate locale creates fail.
3. Skip locales that already exist unless the user asked to update.
4. If the user gives one display name, use it for all locales; if they provide per-locale names, honor them.
5. Pass `--description` only when supplied, usually for IAP localizations.
6. Process many products sequentially by group for readable output, record per-locale failures, and verify with the matching list command after the batch.

## References

- `references/appstore-subscription-localizer.md` for supported locales and detailed resolve, list, create, update, and batch rules.
