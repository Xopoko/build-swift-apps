---
name: appstore-review-readiness
description: Validate App Store submission readiness and execute prepared review actions with current `asc` commands. Use after appstore-release-planner chooses the review path, or when the user directly asks to validate, stage, submit, monitor, cancel, or repair ASC review blockers.
---

# App Store Review Readiness

Use `asc validate` and current review commands. Do not use legacy submit-preflight or submit-create shortcuts.

For go/no-go planning, first-submission strategy, or choosing which release skill owns a blocker, use `appstore-release-planner` first. This skill owns command execution once the review-readiness path is selected.

Preconditions: auth configured; app/version/build IDs resolved; build processing complete unless using `--wait`; metadata, app info, screenshots, review details, content rights, encryption, pricing, availability, and App Privacy expected complete.

## Command Plan Helper

For a deterministic dry-run command plan, run the helper from the plugin root:

```bash
python3 "$PLUGIN_ROOT/skills/appstore-review-readiness/scripts/review_readiness_plan.py" \
  --app "APP_ID" --version "1.2.3" --platform IOS --build "BUILD_ID" \
  --version-id "VERSION_ID" --submission-id "SUBMISSION_ID" \
  --metadata-dir "./metadata" --include-submit
```

The helper prints commands only; it does not call ASC, mutate review state, or read credentials. Pass `--json` for machine-readable output. Pass `--confirming-actions` only after manually verifying that generated `--confirm` commands are intended.

## Workflow

1. Generate the helper plan unless the user requested one specific command.
2. Run read-only readiness checks first: processed build state, normal validate, strict validate, and version-id validate when available.
3. Repair blockers in the smallest owning surface: encryption, content rights, metadata, screenshots, IAP/subscriptions, or App Privacy.
4. Submit only after dry-run output is clean and the user has clearly selected the build/version to send.
5. Monitor by app, version ID, or submission ID; cancel only when the active submission is identified and the user intends cancellation.

For macOS App Store review, use the same flow with `--platform MAC_OS`.

## References

- `references/appstore-review-readiness.md` for detailed ASC repair, submit, multi-item submission, monitor, and retry commands.
