---
name: appstore-connect-cli
description: Use `asc` CLI for App Store Connect command discovery, auth, output formats, pagination, schemas, canonical verbs, Apple Ads, and timeout behavior.
---

# App Store Connect CLI

Use when running or designing `asc` commands.

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

## Apple Ads

Apple Ads uses `asc ads auth`, `--ads-profile`, and `ASC_ADS_*`, not ASC API credentials. Run `asc ads --help`, resolve orgs with `asc ads acls --output json`, pass `--org` or `ASC_ADS_ORG_ID`, and use `--file` JSON payloads for body commands. Destructive/bulk deletes require `--confirm`. For live mutation tests, create paused resources with clear test names and delete the parent campaign.

## Timeouts

`ASC_TIMEOUT` / `ASC_TIMEOUT_SECONDS` control request timeouts. `ASC_UPLOAD_TIMEOUT` / `ASC_UPLOAD_TIMEOUT_SECONDS` control uploads.
