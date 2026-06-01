---
name: appstore-ads-operator
description: "Manage Apple Ads with `asc ads`: separate auth, org lookup, campaigns, ad groups, ads, keywords, reports, raw API requests, and safe live testing."
---

# App Store Ads Operator

Apple Ads auth is separate from App Store Connect auth. Start read-only and require approval before live mutations.

## Ground Rules

- Check `asc ads --help` or subgroup help before scripting.
- Use `--output json` for automation.
- Most commands need an org ID; prefer `--org`, or set `ASC_ADS_ORG_ID`.
- Never guess payload fields. Put Apple Ads JSON in files and pass `--file`.
- Do not mutate until the user names the org and approves the resource type.

## Auth And Org

```bash
asc ads auth login --name "Marketing" --client-id "$ASC_ADS_CLIENT_ID" \
  --team-id "$ASC_ADS_TEAM_ID" --key-id "$ASC_ADS_KEY_ID" \
  --private-key "$ASC_ADS_PRIVATE_KEY_PATH" --org "$ASC_ADS_ORG_ID" --network

export ASC_ADS_CLIENT_ID="SEARCHADS_CLIENT_ID"
export ASC_ADS_TEAM_ID="SEARCHADS_TEAM_ID"
export ASC_ADS_KEY_ID="KEY_ID"
export ASC_ADS_PRIVATE_KEY_PATH="$HOME/.asc/apple-ads-private-key.pem"
export ASC_ADS_ORG_ID="123456"

asc ads auth status --validate --output json
asc ads auth doctor --output json
asc ads me view --output json
asc ads acls --output json
```

Org precedence: `--org`, `ASC_ADS_ORG_ID`, stored profile `org_id`, config `ads.org_id`.

## Reads

```bash
asc ads campaigns --org "123456" --paginate --output json
asc ads campaigns view --org "123456" --campaign 987654321 --output json
asc ads ad-groups list --org "123456" --campaign 987654321 --output json
asc ads apps search --org "123456" --query "My App" --limit 10 --output json
asc ads product-pages list --org "123456" --adam-id 1234567890 --states VISIBLE --output json
asc ads creatives list --org "123456" --limit 100 --output json
asc ads geo search --org "123456" --query "San Francisco" --country-code US --limit 10 --output json
asc ads reports campaigns --org "123456" --file reporting-request.json --output json
asc ads reports keywords --org "123456" --campaign 987654321 --file reporting-request.json --output json
```

Reporting/find endpoints keep pagination in the JSON body.

## Mutations

```bash
asc ads campaigns create --org "123456" --file campaign.json --output json
asc ads campaigns update --org "123456" --campaign 987654321 --file campaign-update.json --output json
asc ads ad-groups create --org "123456" --campaign 987654321 --file ad-group.json --output json
asc ads targeting-keywords create-bulk --org "123456" --campaign 987654321 --ad-group 123456789 --file keywords.json --output json
asc ads targeting-keywords delete-bulk --org "123456" --campaign 987654321 --ad-group 123456789 --file keyword-ids.json --confirm --output json
asc ads campaigns delete --org "123456" --campaign 987654321 --confirm
```

For raw API gaps:

```bash
asc ads api request --method POST --path v5/campaigns/find --org "123456" --file selector.json --output json
```

Raw paths must be Apple Ads v5 paths or full `https://api.searchads.apple.com/api/v5/...` URLs. `DELETE` still requires `--confirm`.

## Live Test Checklist

Start with `me view` and `acls`; print org ID; create paused/future-dated resources named `ASC CLI Live Test <timestamp>`; save IDs; delete only the test parent campaign/ad group; list again to confirm cleanup. Apple may reject direct deletion for default product page creative ads.
