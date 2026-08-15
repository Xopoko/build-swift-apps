# App Store Pricing Planner Command Reference

Use this reference only after `appstore-pricing-planner` is selected and the
agent needs concrete `asc` commands for subscription or IAP pricing.

## Subscriptions

New product setup:

```bash
asc subscriptions setup --app "APP_ID" --group-reference-name "Pro" \
  --reference-name "Pro Monthly" --product-id "com.example.pro.monthly" \
  --subscription-period ONE_MONTH --locale "en-US" --display-name "Pro Monthly" \
  --description "Unlock everything" --price "9.99" --price-territory "USA" \
  --territories "USA,CAN,GBR" --output json
```

Inspect first:

```bash
asc subscriptions pricing summary --subscription-id "SUB_ID" --territory "USA"
asc subscriptions pricing prices list --subscription-id "SUB_ID" --paginate
```

Bulk PPP update via CSV:

```csv
territory,price,start_date,preserved
IND,2.99,2026-04-01,false
BRA,4.99,2026-04-01,false
```

```bash
asc subscriptions pricing prices import --subscription-id "SUB_ID" --input "./ppp-prices.csv" --dry-run --output table
asc subscriptions pricing prices import --subscription-id "SUB_ID" --input "./ppp-prices.csv" --output table
```

Required CSV: `territory`, `price`. Optional: `currency_code`, `start_date`,
`preserved`, `preserve_current_price`, `price_point_id`. When omitted, price
points are resolved automatically.

Small manual overrides:

```bash
asc subscriptions pricing prices set --subscription-id "SUB_ID" --price "2.99" --territory "IND"
asc subscriptions pricing prices set --subscription-id "SUB_ID" --tier 5 --territory "BRA"
asc subscriptions pricing prices set --subscription-id "SUB_ID" --price-point "PRICE_POINT_ID" --territory "DEU"
```

Use `--start-date` for scheduled changes and `--preserved` to preserve current
price relationship.

Enable territories when needed:

```bash
asc subscriptions pricing availability edit --subscription-id "SUB_ID" --territories "USA,CAN,IND,BRA"
asc subscriptions pricing availability view --subscription-id "SUB_ID"
```

## IAP

New product setup:

```bash
asc iap setup --app "APP_ID" --type NON_CONSUMABLE \
  --reference-name "Pro Lifetime" --product-id "com.example.pro.lifetime" \
  --locale "en-US" --display-name "Pro Lifetime" --description "Unlock everything" \
  --price "9.99" --base-territory "USA" --output json
```

Inspect and schedule:

```bash
asc iap pricing summary --iap-id "IAP_ID" --territory "USA"
asc iap pricing price-points list --iap-id "IAP_ID" --territory "USA" --paginate --price "9.99"
asc iap pricing schedules create --iap-id "IAP_ID" --base-territory "USA" --price "4.99" --start-date "2026-04-01"
asc iap pricing schedules view --iap-id "IAP_ID"
```

Use `--tier` or `--price-point-id`/`--prices` when deterministic tier/ID setup
matters.

## Rules

- Prefer `asc subscriptions setup`, `asc iap setup`, `asc subscriptions pricing ...`, and `asc iap pricing ...`.
- Dry-run broad subscription CSV imports before applying.
- Verify summaries before and after for important territories.
- Price changes may take time to propagate in App Store Connect/storefronts.
- Older `asc subscriptions prices ...` paths may exist, but the `pricing` family is canonical.
