---
name: appstore-revenuecat-sync
description: Reconcile App Store Connect subscriptions/IAPs with RevenueCat products, entitlements, offerings, and packages using `asc` plus RevenueCat MCP. Use for catalog bootstrap, drift audits, and deterministic product mapping.
---

# App Store RevenueCat Sync

Start read-only, build a diff, then create/update only after explicit confirmation. Never delete resources in this workflow.

## Preconditions

- `asc` auth configured.
- RevenueCat MCP configured/authenticated; write-enabled API v2 key for apply.
- Known `APP_ID`, RevenueCat `project_id`, target app type (`app_store` or `mac_app_store`), and bundle ID for create flows.

Canonical key: ASC `productId` == RevenueCat `store_identifier`. Never use display names as unique IDs.

## Modes

- Audit: read ASC + RevenueCat, find missing resources and conflicts, present plan.
- Apply: after approval, ensure ASC items, RevenueCat app/products, entitlements/attachments, offerings/packages, then verify.

## Read Sources

```bash
asc subscriptions groups list --app "APP_ID" --paginate --output json
asc iap list --app "APP_ID" --paginate --output json
asc subscriptions list --group-id "GROUP_ID" --paginate --output json
```

RevenueCat MCP tools: `mcp_RC_get_project`, `mcp_RC_list_apps`, `mcp_RC_list_products`, `mcp_RC_list_entitlements`, `mcp_RC_list_offerings`, `mcp_RC_list_packages` with pagination.

Type mapping:

- subscription -> `subscription`
- `CONSUMABLE` -> `consumable`
- `NON_CONSUMABLE` -> `non_consumable`
- `NON_RENEWING_SUBSCRIPTION` -> `non_renewing_subscription`

Entitlement defaults: one per subscription group, one per non-consumable, none for consumables unless requested.

## Apply Order

1. Create missing ASC resources, then re-read ASC to get canonical IDs:
   ```bash
   asc subscriptions groups create --app "APP_ID" --reference-name "Premium"
   asc subscriptions create --group-id "GROUP_ID" --reference-name "Monthly" --product-id "com.example.premium.monthly" --subscription-period ONE_MONTH
   asc iap create --app "APP_ID" --type NON_CONSUMABLE --ref-name "Lifetime" --product-id "com.example.lifetime"
   ```
2. Ensure RevenueCat app/products with `mcp_RC_create_app` and `mcp_RC_create_product`; set `store_identifier` to ASC `productId`.
3. Ensure entitlements and product attachments with `mcp_RC_create_entitlement`, `mcp_RC_attach_products_to_entitlement`, and verify with `mcp_RC_get_products_from_entitlement`.
4. Optional offerings/packages: `mcp_RC_create_offering`, `mcp_RC_update_offering`, `mcp_RC_create_package`, `mcp_RC_attach_products_to_package` using `eligibility_criteria: "all"`.

Recommended package keys: weekly `$rc_weekly`, monthly `$rc_monthly`, two-month `$rc_two_month`, three-month `$rc_three_month`, six-month `$rc_six_month`, annual `$rc_annual`, lifetime `$rc_lifetime`, custom `$rc_custom_<name>`.

## Agent Rules

- Always audit first, even when the user asks to apply.
- Ask before create/update operations.
- Match by `store_identifier` first.
- Use full pagination (`--paginate`, `starting_after`).
- Continue after per-item failures and report all together.
- RevenueCat MCP does not create ASC products; use `asc` for ASC resources first.
- Watch for wrong RevenueCat project/app, wrong platform app, consumables attached to entitlements, skipped ASC re-read, and unverified package/offering attachments.

## Output

Summarize ASC created/skipped/failed counts, RevenueCat created/skipped/failed counts, attachment counts, and actionable failures.

References: `examples.md`, `references.md`.
