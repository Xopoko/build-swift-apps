---
name: xcode-ui-test-stabilizer
description: Create, stabilize, and run UI end-to-end tests with Xcode (XCUIApplication/xcodebuild), including environment setup, focus/input stabilization, logging/attachments, and flakiness triage. Use when adding or debugging UI automation, writing new UI tests, or making them reliable.
---

# Xcode UI Test Stabilizer

## Overview

Build deterministic UI end-to-end tests and debug flaky runs. Prefer stable accessibility identifiers, environment-driven setup, and explicit wait conditions. Always attach logs and screenshots on failure.

## Workflow

1. Define the flow and success signals.
   - Identify the UI state that proves success (accessibility identifiers, log markers, or system-visible views).
   - Decide which logs to capture (app log, build log, UI test log).

2. Add or update the UI test.
   - Use stable identifiers (avoid labels that can change or be localized).
   - Avoid typing into complex text components when possible; prefer injecting text via test-only defaults.
   - Gate test-only behavior behind env flags so production behavior is unchanged.

3. Stabilize the app for UI tests.
   - Ensure the app activates and brings windows to front in UI test mode.
   - Disable modal blockers or auto-approve when tests run.
   - Use in-memory persistence for tests if persistent stores are fragile.

4. Run the test with the provided script or your own command.
   - Use `scripts/run_ui_test.sh` (from this skill) or run `xcodebuild test` with `-only-testing`.

5. Triage failures.
   - Attach logs and screenshots.
   - Search logs for build/preview errors and unexpected user-stop messages.
   - Iterate until the test is deterministic.

## Stability checklist (quick wins)

- Use `waitForExistence` for every critical element.
- Assert the app is running foreground before input.
- Avoid `typeText` for long text; prefer env-injected defaults.
- Click the window before interacting.
- Keep timeouts explicit and generous for CI machines.
- Attach logs and screenshots on failure.

## References

- Read `references/ui-e2e-playbook.md` for generic flags, focus fixes, typing workarounds, and debugging patterns.

## Resources

### scripts/

- `scripts/run_ui_test.sh` — run a single UI test with optional .env loading and xcodebuild args.

### references/

- `references/ui-e2e-playbook.md` — general UI E2E playbook, flags, and troubleshooting.
