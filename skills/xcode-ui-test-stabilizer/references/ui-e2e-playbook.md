# UI E2E Playbook (Generic)

## Quick start

Run a single UI test (use the script bundled with this skill):

```
ENV_FILE=.env \
PROJECT="MyApp.xcodeproj" \
SCHEME="MyApp" \
DESTINATION="platform=macOS" \
TEST_NAME="MyAppUITests/MyAppUITests/testHappyPath" \
./scripts/run_ui_test.sh
```

Or run directly:

```
xcodebuild test -project "MyApp.xcodeproj" -scheme "MyApp" -destination "platform=macOS" -only-testing:"MyAppUITests/MyAppUITests/testHappyPath"
```

## Environment-driven stability (project-defined)

These are patterns, not fixed names. Add flags that your app understands:

- `UI_TEST=1` to enable test-only behavior.
- `UI_TEST_PROMPT=<text>` to prefill a TextEditor and avoid typing flakiness.
- `UI_TEST_AUTO_APPROVE=1` to bypass blocking approvals.
- `UI_TEST_WINDOW_TWEAKS=1` to force focus and prevent miniaturization.
- `TEST_LOG_PATH`, `BUILD_LOG_PATH` to capture app/build logs.

## Focus and window activation

Symptoms:
- App launches without a key window.
- Window exists but is not focused, causing keystrokes to misroute.

Mitigations:
- App-level: on UI-test flag, call `NSApp.activate(ignoringOtherApps: true)` and `makeKeyAndOrderFront`.
- View-level: use a window accessor to deminiaturize and bring to front.
- Test-level: call `app.activate()` and wait for `.runningForeground` before interactions.

## Input stability (TextEditor/custom inputs)

Symptoms:
- Typing causes focus loss, weird sounds, or missing characters.

Fixes:
- Prefer env-injected defaults over `typeText`.
- If typing is unavoidable: click field, wait briefly, type in small chunks, assert field value.

## Deterministic wait conditions

Preferred UI markers:
- `*.ready` for success
- `*.error` for failure

Fallbacks:
- parse app logs for state transitions (e.g. `ready`, `error`)
- enforce timeouts on every wait

## Attachments on failure

Always attach:
- UI test log
- app log
- build log
- screenshot

## Common failure modes (generic)

- Backgrounded app or missing window: fix activation logic and add retries.
- Persistent store mismatch: use in-memory store for UI tests.
- Long-running operations: add a polling loop with a deadline.
- CI-only failures: increase timeouts and reduce animation or background work under UI-test flags.
