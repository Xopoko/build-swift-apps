---
name: appstore-pricing-planner
description: App Store subscription and IAP pricing by territory with `asc`, including price points, PPP/localized CSV imports, availability, summaries, and schedules; mutating actions require confirmation.
---

# App Store Pricing Planner

Use current `asc` pricing families to inspect, dry-run, apply, and verify regional subscription/IAP prices.

## Preconditions

- `asc auth login` or `ASC_*`.
- App/product IDs resolved; pass `--app` or use `ASC_APP_ID`.
- Base territory chosen, usually `USA`.
- Run `asc pricing territories list --paginate` if territory IDs are unknown.

## Workflow

1. Resolve app, subscription, IAP, territory, and price point IDs before planning mutations.
2. Inspect summaries and price lists first, especially the base territory and high-revenue localized territories.
3. For PPP or regional bulk changes, prepare CSV with required `territory` and `price`; optional fields include `currency_code`, `start_date`, `preserved`, `preserve_current_price`, and `price_point_id`.
4. Dry-run broad subscription CSV imports before applying.
5. Confirm intended prices, territories, and effective dates before applying, then verify summaries.
6. Expect propagation delay in App Store Connect/storefronts. Older `asc subscriptions prices ...` paths may exist, but the `pricing` family is canonical.

## References

- `references/appstore-pricing-planner.md` for detailed subscription setup, IAP setup, CSV import, manual override, availability, and schedule commands.
