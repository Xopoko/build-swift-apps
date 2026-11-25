---
name: appstore-review-readiness
description: App Store review-readiness execution with current `asc` commands to validate, stage, submit, monitor, cancel, or repair blockers after go/no-go planning. Excludes release strategy; appstore-release-planner owns it.
---

# App Store Review Readiness

Use `asc validate` and current review commands. Do not use legacy submit-preflight or submit-create shortcuts.

For go/no-go planning, first-submission strategy, or choosing which release skill owns a blocker, use `appstore-release-planner` first. This skill owns command execution once the review-readiness path is selected.

Preconditions: auth configured; app/version/build IDs resolved; build processing complete unless using `--wait`; metadata, app info, screenshots, review details, content rights, encryption, pricing, availability, and App Privacy expected complete.

## Workflow

1. Check that the intended build is processed. Run strict validation for the target version, using the version ID if available.
2. Repair the reported blockers in the relevant area: encryption, content rights, metadata, screenshots, IAP/subscriptions, or App Privacy.
3. Submit only after dry-run output is clean and the user has clearly selected the build/version to send.
4. Monitor by app, version ID, or submission ID. Cancel only when the active submission is identified and the user intends cancellation.

For macOS App Store review, use the same flow with `--platform MAC_OS`.

## References

- `references/appstore-review-readiness.md` for detailed ASC repair, submit, multi-item submission, monitor, and retry commands.
