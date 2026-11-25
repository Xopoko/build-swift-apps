---
name: macos-test-diagnoser
description: "macOS Xcode and SwiftPM tests: run focused scopes and diagnose build, assertion, crash, async-flake, fixture, entitlement, and host-app failures; separate regressions from setup issues."
---

# macOS Test Diagnoser

Before invoking Apple-only binaries, confirm the execution context is macOS. From Windows or Linux, run those steps in a Mac SSH project or through an already configured remote transport; do not retry missing Apple binaries locally.

## Workflow

1. Use `xcodebuild test` for an Xcode scheme or `swift test` for a SwiftPM
   package. Apply the requested target or filter, or start with the smallest
   scope that can reproduce the failure.
2. Check whether tests executed. Separate build failures from assertions and
   crashes, then inspect fixtures, host app, entitlements, and simulator-only
   assumptions when the failure points to setup.
3. Rerun the failing case when timing or order could matter. Treat a passing
   rerun as evidence of intermittent behavior and keep the original failure.
4. Report the command, failed cases or failed build step, result bundle if
   produced, and the evidence for the likely cause.

## Result Bundle Inspection

When console output alone is not enough, read the `.xcresult` bundle instead
of rerunning:

- Pass `-resultBundlePath ./Tests.xcresult` to `xcodebuild test` using a new path on each rerun.
- Run summary: `xcrun xcresulttool get test-results summary --path Tests.xcresult`
- Per-test outcomes: `xcrun xcresulttool get test-results tests --path Tests.xcresult`
- One failure in depth: `xcrun xcresulttool get test-results test-details --test-id <id> --path Tests.xcresult`
- Attachments such as screenshots and logs: `xcrun xcresulttool export attachments --path Tests.xcresult --output-path ./attachments`
- Older bundles or full object graph: `xcrun xcresulttool get --legacy --format json --path Tests.xcresult` (drop `--legacy` on pre-Xcode 16 toolchains).

For `swift test`, use console output, `--filter` reruns, and `--xunit-output`
when a machine-readable report is needed.
