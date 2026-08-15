---
name: appstore-connect-cli
description: "App Store Connect commands: discover and run generic `asc` CLI auth, schemas, canonical verbs, pagination, output, records, API requests, and timeouts; exclude Apple Ads campaigns."
---

# App Store Connect CLI

Use when running or designing generic App Store Connect `asc` commands. Hand
Apple Ads auth, org, campaign, ad-group, creative, keyword, reporting, and Ads
API work to `appstore-ads-operator`.

## Discovery

- Start with `--help`: `asc --help`, `asc builds --help`, `asc builds list --help`.
- Use deterministic command search:
  - `asc search "submit app for review"`
  - `asc search --output table "upload build"`
- Inspect bundled ASC schemas before API-facing commands:
  - `asc schema --pretty "GET /v1/apps"`
  - `asc schema --method POST appStoreVersions`
- Explain workflow coverage:
  - `asc capabilities --area release --output table`
  - `asc capabilities --status not-public-api --output markdown`

## Command Rules

- Prefer current verbs shown by help: `view` for reads, `edit` for update-only availability, and `set` only where the CLI models replacement/configuration.
- Use explicit long flags in automation.
- Destructive operations require `--confirm`.
- Use `--paginate` only when all pages are needed.
- Output defaults are TTY-aware: table interactively, JSON when piped/non-interactive.
- Use `--output table`/`markdown` for humans; `--pretty` only with JSON.

Examples:

```bash
asc apps view --id "APP_ID"
asc versions view --version-id "VERSION_ID"
asc pricing availability edit --app "APP_ID" --territory "USA,GBR" --available true
asc xcode version edit --build-number "42"
```

## Auth

Prefer `asc auth login`. Env fallback: `ASC_KEY_ID`, `ASC_ISSUER_ID`, `ASC_PRIVATE_KEY_PATH`, `ASC_PRIVATE_KEY`, `ASC_PRIVATE_KEY_B64`. `ASC_APP_ID` can provide the default app. For unclear key permissions, inspect `asc web auth capabilities` or `--key-id`.

## Ownership Boundary

Keep generic CLI discovery, App Store Connect auth, schema inspection, record
operations, pagination, output formatting, raw ASC API requests, and timeout
handling here. Do not plan or execute Apple Ads campaign operations from this
skill; select `appstore-ads-operator`, which owns the separate Ads credentials,
organization context, safety gates, and campaign lifecycle.

## Timeouts

`ASC_TIMEOUT` / `ASC_TIMEOUT_SECONDS` control request timeouts. `ASC_UPLOAD_TIMEOUT` / `ASC_UPLOAD_TIMEOUT_SECONDS` control uploads.
