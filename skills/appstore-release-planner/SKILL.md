---
name: appstore-release-planner
description: Decide whether an App Store version is ready, then stage, validate, submit, monitor, or cancel release work with current `asc` commands, including first-submission blockers, IAP/subscriptions, Game Center, App Privacy, and review details.
---

# App Store Release Planner

Use when the user asks whether an app can be submitted now or wants to prepare/submit an App Store version.

## Answer Order

1. Ready now or not.
2. Blocking issues.
3. Public API fixes vs experimental web-session/manual fixes.
4. Next exact command.

Resolve `APP_ID`, version, `VERSION_ID`, and `BUILD_ID`; ensure `asc auth login` or `ASC_*`; use canonical `./metadata` when staging.

## Main Path

```bash
asc validate --app "APP_ID" --version "1.2.3" --platform IOS --output table
asc validate --app "APP_ID" --version "1.2.3" --platform IOS --strict --output table
asc validate iap --app "APP_ID" --output table
asc validate subscriptions --app "APP_ID" --output table
```

Stage without submit:

```bash
asc release stage --app "APP_ID" --version "1.2.3" --build "BUILD_ID" \
  --metadata-dir "./metadata/version/1.2.3" --dry-run --output table
asc release stage --app "APP_ID" --version "1.2.3" --build "BUILD_ID" \
  --metadata-dir "./metadata/version/1.2.3" --confirm
```

Use `--copy-metadata-from "1.2.2"` instead of `--metadata-dir` when carrying metadata forward.

Submit prepared version:

```bash
asc review submit --app "APP_ID" --version "1.2.3" --build "BUILD_ID" --dry-run --output table
asc review submit --app "APP_ID" --version "1.2.3" --build "BUILD_ID" --confirm
```

High-level upload/submit:

```bash
asc publish appstore --app "APP_ID" --ipa "./App.ipa" --version "1.2.3" --submit --dry-run --output table
asc publish appstore --app "APP_ID" --ipa "./App.ipa" --version "1.2.3" --submit --confirm
```

Monitor/cancel:

```bash
asc status --app "APP_ID"
asc submit status --version-id "VERSION_ID"
asc submit status --id "SUBMISSION_ID"
asc submit cancel --id "SUBMISSION_ID" --confirm
```

## First-Submission Blockers

- Availability missing: check `asc pricing availability view --app "APP_ID"`. Bootstrap with `asc web apps availability create ...`, then use public `asc pricing availability edit ...`.
- Subscriptions ready but not attached to first review: run `asc validate subscriptions`; inspect/attach with `asc web review subscriptions list`, `attach-group`, or `attach`; later reviews use `asc subscriptions review submit`.
- IAP review readiness: `asc validate iap`; upload screenshots with `asc iap review-screenshots create`; submit with `asc iap submit`; web-only first-version gap can use `asc web review iaps attach --confirm`.
- Game Center: create app-version records and add component versions through explicit review submission items before submit.
- App Privacy: public API cannot fully prove publish state; use `asc web privacy pull/plan/apply/publish` or manual App Store Connect confirmation.
- Review details: inspect `asc review details-for-version`; create/update with `asc review details-create` or `details-update`. Only set demo account fields when review truly needs them.

Call out all `asc web ...` commands as experimental web-session escape hatches.

## Ready Checklist

Ready means validation has no blockers; stage/submit dry-run is correct; build is `VALID` and attached; metadata, screenshots, app info, content rights, encryption, age rating, and review details are complete; availability exists; digital goods and Game Center review items are handled; App Privacy is confirmed/published.

## Do Not Use

Do not use legacy submit-preflight, submit-create, or release-run shortcuts. Use `asc validate`, `asc release stage`, `asc review submit`, `asc publish appstore --submit`, `asc status`, and `asc submit status`.
