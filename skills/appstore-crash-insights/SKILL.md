---
name: appstore-crash-insights
description: Triage TestFlight crashes, beta feedback, hangs, disk writes, launches, and performance diagnostics with `asc` crash/feedback/diagnostics commands.
---

# App Store Crash Insights

Fetch, analyze, and summarize TestFlight crash reports, beta feedback, and performance diagnostics.

## Workflow

1. Resolve app ID with `asc apps list` if missing.
2. Resolve build ID when diagnostics need one.
3. Fetch JSON with the narrowest useful command.
4. Group by severity/frequency and summarize in human terms.

## Commands

Crashes:

```bash
asc testflight crashes list --app "APP_ID" --sort -createdDate --limit 10
asc testflight crashes list --app "APP_ID" --build "BUILD_ID" --sort -createdDate --limit 10
asc testflight crashes list --app "APP_ID" --device-model "iPhone16,2" --os-version "18.0"
asc testflight crashes list --app "APP_ID" --paginate
```

Feedback:

```bash
asc testflight feedback list --app "APP_ID" --sort -createdDate --limit 10
asc testflight feedback list --app "APP_ID" --sort -createdDate --limit 10 --include-screenshots
asc testflight feedback list --app "APP_ID" --build "BUILD_ID" --sort -createdDate
asc testflight feedback list --app "APP_ID" --paginate
```

Performance diagnostics:

```bash
asc builds info --app "APP_ID" --latest --platform IOS
asc builds list --app "APP_ID" --sort -uploadedDate --limit 5
asc performance diagnostics list --build "BUILD_ID"
asc performance diagnostics list --build "BUILD_ID" --diagnostic-type "HANGS"
asc performance diagnostics view --id "SIGNATURE_ID"
asc performance download --build "BUILD_ID" --output ./metrics.json
```

Diagnostic types: `HANGS`, `DISK_WRITES`, `LAUNCHES`.

Resolve IDs with `asc apps list --name "AppName"`, `asc apps list --bundle-id "com.example.app"`, or `export ASC_APP_ID="APP_ID"`.

## Summary

Report total count, top crash signatures, affected builds, device/OS breakdown, timeline/spikes, and highest-weight performance signatures. Default output is JSON; use table/markdown for quick human review, `--paginate` for full analysis, and `--pretty` for JSON debugging. ASC crash data can lag 24-48h.
