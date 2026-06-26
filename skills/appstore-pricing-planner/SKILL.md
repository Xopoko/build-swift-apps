---
name: appstore-pricing-planner
description: Set territory-specific subscription and IAP pricing with `asc` setup, pricing summary, CSV import, price-point, availability, and schedule commands. Use for PPP or localized pricing strategies.
---

# App Store Pricing Planner

Use current `asc` pricing families to inspect, dry-run, apply, and verify regional subscription/IAP prices.

## Preconditions

- `asc auth login` or `ASC_*`.
- App/product IDs resolved; pass `--app` or use `ASC_APP_ID`.
- Base territory chosen, usually `USA`.
- Run `asc pricing territories list --paginate` if territory IDs are unknown.

## Command Plan Helper

For a deterministic command plan, run the helper from the plugin root:

```bash
python3 "$PLUGIN_ROOT/skills/appstore-pricing-planner/scripts/pricing_plan.py" \
  --subscription-id "SUB_ID" --territory "USA" \
  --include-subscription-import --prices-csv "./ppp-prices.csv"
```

The helper prints commands only; it does not call ASC, import CSV data, or change prices. Commands that create products, apply imports, set prices, edit availability, or create schedules require `--confirming-actions`. Pass `--json` for machine-readable output.

## Workflow

1. Resolve app, subscription, IAP, territory, and price point IDs before planning mutations.
2. Inspect summaries and price lists first, especially the base territory and high-revenue localized territories.
3. For PPP or regional bulk changes, prepare CSV with required `territory` and `price`; optional fields include `currency_code`, `start_date`, `preserved`, `preserve_current_price`, and `price_point_id`.
4. Dry-run broad subscription CSV imports before applying.
5. Verify summaries after applying important price, schedule, or availability changes.
6. Expect propagation delay in App Store Connect/storefronts. Older `asc subscriptions prices ...` paths may exist, but the `pricing` family is canonical.

## References

- `references/appstore-pricing-planner.md` for detailed subscription setup, IAP setup, CSV import, manual override, availability, and schedule commands.
