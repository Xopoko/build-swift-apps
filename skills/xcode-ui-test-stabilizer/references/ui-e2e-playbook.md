# Xcode UI Test Playbook

## Quick start

```bash
RESULT_DIR="$(mktemp -d)"
xcodebuild test -project "MyApp.xcodeproj" -scheme "MyApp" \
  -destination "platform=macOS" \
  -only-testing:"MyAppUITests/MyAppUITests/testHappyPath" \
  -resultBundlePath "$RESULT_DIR/Test.xcresult"
```

Use `-workspace` for a workspace. For iOS tests, choose the Simulator
destination by UDID. Use `XCUIApplication.launchEnvironment` for any test
fixtures already supported by the project.

## Focus and window activation

Symptoms:
- App launches without a key window.
- Window exists but is not focused, causing keystrokes to misroute.

Mitigations:
- Wait for `app.wait(for: .runningForeground, timeout: ...)` and the intended
  window or control before sending input. Use `app.activate()` when the test
  needs to bring the app back to the foreground.

## Input stability (TextEditor/custom inputs)

Symptoms:
- Typing causes focus loss, weird sounds, or missing characters.

Fixes:
- Seed long text as a fixture when typing is outside the test scope.
- For input tests, focus the specific field, type the text, and assert its value.

## Deterministic wait conditions

Preferred UI markers:
- `*.ready` for success
- `*.error` for failure

Fallbacks:
- parse app logs for state transitions (e.g. `ready`, `error`)
- enforce timeouts on every wait

On failure, retain the `.xcresult` and relevant application logs. Add an
`XCTAttachment` for a screenshot when the result bundle lacks the state needed
to diagnose the interaction.
