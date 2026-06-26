---
name: appstore-release-planner
description: Answer App Store release go/no-go questions and choose the next focused release skill. Use for readiness planning, first-submission blockers, release sequencing, or deciding whether to stage or submit; use appstore-review-readiness for concrete validate, submit, monitor, cancel, and repair commands.
---

# App Store Release Planner

Use this as the decision front door for App Store release readiness. Do not duplicate the execution workflow here; after the decision, read the focused skill that owns the next action.

## Routing

- Use `appstore-release-director` when the user wants an end-to-end release from local repo through upload, TestFlight, review, and evidence.
- Use `appstore-review-readiness` for concrete validation, staging/submission, status monitoring, cancellation, and blocker repair commands.
- Use `appstore-archive-uploader` when the next unresolved step is version/build numbering, archive, export, upload, or processed build selection.
- Use `appstore-metadata-sync`, `appstore-screenshot-validator`, `appstore-signing-setup`, `appstore-pricing-planner`, `appstore-subscription-localizer`, or `appstore-testflight-coordinator` when the blocker is clearly in that narrower surface.

## Answer Order

1. Ready now or not.
2. Blocking issues.
3. Public API fixes vs experimental web-session/manual fixes.
4. Next exact command.

Resolve `APP_ID`, version, `VERSION_ID`, and `BUILD_ID`; ensure `asc auth login` or `ASC_*`; use canonical `./metadata` when staging.

## Decision Path

1. Establish release target: app, platform, version, build, submission state, and whether this is a first submission.
2. Check whether the next missing evidence belongs to metadata, screenshots, signing, pricing/availability, subscriptions/IAP, App Privacy, review details, Game Center, build processing, or review status.
3. If the version looks action-ready or needs command proof, switch to `appstore-review-readiness` and follow its current `asc` command workflow.
4. If the user only needs an executive answer, report ready/not-ready, blockers, public-API fixes versus experimental web-session/manual fixes, and the next focused skill/command owner.

## First-Submission Blockers

- Availability missing: public edit commands may work after initial availability exists; bootstrap can require an experimental web-session or manual ASC action.
- Subscriptions ready but not attached to first review: later reviews can use public subscription review paths; first review attachment can require an experimental web-session or manual ASC action.
- IAP review readiness: public IAP validation/submission paths cover most cases; selecting IAPs with the first app version can require an experimental web-session or manual ASC action.
- Game Center: create app-version records and add component versions through explicit review submission items before submit.
- App Privacy: public API cannot fully prove publish state; use `asc web privacy pull/plan/apply/publish` or manual App Store Connect confirmation.
- Review details: only set demo account fields when review truly needs them.

Call out all `asc web ...` commands as experimental web-session escape hatches.

## Ready Checklist

Ready means validation has no blockers; stage/submit dry-run is correct; build is `VALID` and attached; metadata, screenshots, app info, content rights, encryption, age rating, and review details are complete; availability exists; digital goods and Game Center review items are handled; App Privacy is confirmed/published.

## Guardrails

- Do not use legacy submit-preflight, submit-create, or release-run shortcuts.
- Do not claim ready without concrete validation evidence or a clear manual-confirmation boundary.
- Do not submit, cancel, or mutate review state from this planner; hand off to `appstore-review-readiness`.
