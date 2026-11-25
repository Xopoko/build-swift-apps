---
name: xcode-ui-test-stabilizer
description: Build and stabilize Xcode UI end-to-end tests with XCUIApplication/xcodebuild for new or unreliable automation, covering environment setup, focus/input reliability, waits, logs, attachments, and flakiness triage.
---

# Xcode UI Test Stabilizer

Before invoking Apple-only binaries, confirm the execution context is macOS. From Windows or Linux, run those steps in a Mac SSH project or through an already configured remote transport; do not retry missing Apple binaries locally.

## Workflow

1. Identify the user-visible state that proves the flow worked. Match on stable
   accessibility identifiers and wait for a state change with a bounded timeout.
2. Reproduce the failing test on its scheme and destination. Keep the result
   bundle and use failure screenshots and app logs to distinguish focus, input,
   and app failures.
3. Use test fixtures for prerequisites outside the flow. Exercise input,
   approvals, persistence, or window behavior when the test is meant to cover it.
4. Rerun under the conditions that exposed the failure. Report the run count and
   any remaining failures.

See [the UI test playbook](references/ui-e2e-playbook.md) for the focused
`xcodebuild` command and common XCTest failure modes.
