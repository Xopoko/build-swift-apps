---
name: macos-runtime-debugger
description: "macOS app runtimes: build, launch, and debug Xcode or SwiftPM GUI/CLI targets with shell-first workflows; diagnose compiler, linker, startup, log, and telemetry failures; exclude iOS Simulator work."
---

# macOS Runtime Debugger

Before invoking Apple-only binaries, confirm the execution context is macOS. From Windows or Linux, run those steps in a Mac SSH project or through an already configured remote transport; do not retry missing Apple binaries locally.

Use the project's existing build and run entrypoint. For a one-shot build,
launch, log, or debug task, use a direct command if there is no entrypoint.
For a reusable run loop, follow the
[bootstrap procedure](references/run-button-bootstrap.md).

## Workflow

1. Read repository guidance and inspect existing scripts, run actions, Xcode
   schemes, and package products. Select the requested target or the app's
   runnable scheme or product.
2. For Xcode, build the selected macOS scheme and open the resulting `.app`.
   For a SwiftPM CLI, run the executable. For a SwiftPM AppKit or SwiftUI app,
   [stage and open a `.app` bundle](references/run-button-bootstrap.md#swiftpm-gui-bundle).
3. Verify the fresh process or the requested app state. If a step fails, report
   which command failed and quote the relevant compiler, linker, signing,
   toolchain, script, or launch error.

## Debugging

- Use unified logs to inspect startup, configuration, and sandbox failures.
- If a SwiftPM GUI bundle launches but does not foreground, check `NSApp.setActivationPolicy(.regular)` and `NSApp.activate(ignoringOtherApps: true)`.
- Use `lldb` for symbolized crash debugging.
- Switch to `macos-telemetry-probe` when verifying specific window/sidebar/menu/menu-bar actions.
- Use Xcode-aware MCP only when explicitly requested and it fits macOS discovery/debugging; fall back to shell when it does not.

Report the command, observed build or launch result, and any files created.
