---
name: macos-telemetry-probe
description: Add and verify lightweight macOS runtime telemetry with `Logger`/`os.Logger`, `log stream`, Console filters, signposts, and build-run checks.
---

# macOS Telemetry Probe

Add high-signal app instrumentation without leaving noisy permanent logs. Prefer Apple's unified logging and verify events after build/run.

## Rules

- Use `Logger` from `OSLog`.
- Give each feature a clear subsystem/category.
- Log meaningful lifecycle/user events: windows, sidebar/inspector selection, commands, menu bar actions, sync/load milestones, fallback/error paths.
- Keep info logs stable; use debug for noisy state.
- Never log secrets, tokens, personal data, or raw document contents.
- Add signposts only for timing/performance spans.

```swift
import OSLog

private let logger = Logger(
  subsystem: Bundle.main.bundleIdentifier ?? "SampleApp",
  category: "Sidebar"
)

@MainActor
func selectItem(_ item: SidebarItem) {
  logger.info("Selected sidebar item: \(item.id, privacy: .public)")
  selection = item.id
}
```

Use feature categories like `Windowing`, `Commands`, `MenuBar`, `Sidebar`, `Sync`, or `Import`.

## Workflow

1. Identify the behavior needing observability.
2. Add one useful log per action boundary or key state transition.
3. Build/run with `macos-runtime-debugger`; if present, prefer `./script/build_and_run.sh --telemetry` or `--logs`.
4. Exercise the UI/command path.
5. Verify through Console or:

   ```bash
   log stream --style compact --predicate 'process == "AppName"'
   log stream --style compact --predicate 'subsystem == "com.example.app" && category == "Sidebar"'
   ```

6. Keep useful logs; remove or demote temporary noise.

## Verification

Confirm the app builds, the relevant action emits exactly one clear line or bounded sequence, logs filter by process/subsystem/category, no sensitive payloads are written, and temporary debug noise is gone. If the task is mainly crash/backtrace work, switch to `macos-runtime-debugger`.
