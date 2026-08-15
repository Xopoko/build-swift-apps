---
name: macos-runtime-debugger
description: "macOS app runtimes: build, launch, and debug Xcode or SwiftPM GUI/CLI targets with shell-first workflows; diagnose compiler, linker, startup, log, and telemetry failures; exclude iOS Simulator work."
---

# macOS Runtime Debugger

Before invoking Apple-only binaries, confirm the execution context is macOS. From Windows or Linux, run those steps in a Mac SSH project or through an already configured remote transport; do not retry missing Apple binaries locally.

Reuse the project's existing build/run entrypoint first. For one-shot build,
launch, log, or debug tasks, use the smallest existing command that proves the
requested outcome without adding durable project files. Bootstrap
`script/build_and_run.sh` through `/macos-runtime-debug` only when the user asks
for a reusable run loop or no adequate entrypoint exists and repeated use makes
one worthwhile.

## Workflow

1. Discover project shape and existing entrypoints:
   ```bash
   git rev-parse --show-toplevel 2>/dev/null || pwd
   find . -name '*.xcworkspace' -o -name '*.xcodeproj' -o -name 'Package.swift'
   ```
   Read repository guidance and inspect existing scripts, schemes, package
   products, and host actions before introducing another entrypoint.
2. Resolve and prefer the established runnable target/process:
   - Xcode: list schemes and prefer the app-producing scheme unless named.
   - SwiftPM CLI: run the executable.
   - SwiftPM AppKit/SwiftUI GUI: stage a project-local `.app` bundle and launch with `/usr/bin/open -n`; do not run as a raw executable.
3. For a one-shot task, run that entrypoint directly and avoid changing project
   structure merely to make the command repeatable.
4. If a durable loop is explicitly requested or clearly useful because no
   adequate entrypoint exists, invoke `/macos-runtime-debug` and follow
   `references/run-button-bootstrap.md`. Do not duplicate its full snippets.
5. Add or update `.codex/environments/environment.toml` only when the user asks
   for a Codex Run action. Preserve unrelated existing actions.
6. When the bootstrap script is the selected entrypoint, run the requested mode:
   ```bash
   ./script/build_and_run.sh
   ./script/build_and_run.sh --debug
   ./script/build_and_run.sh --logs
   ./script/build_and_run.sh --telemetry
   ./script/build_and_run.sh --verify
   ```
7. Classify failures as compiler, linker, signing, build settings, missing SDK/toolchain, entrypoint/script bug, or runtime launch. Quote the smallest useful error.

## Bootstrap Script Requirements

- Apply these requirements only when `/macos-runtime-debug` bootstraps or
  refreshes `script/build_and_run.sh`.
- Keep the script outside app source in `script/build_and_run.sh`.
- Xcode projects use `xcodebuild`.
- SwiftPM command-line tools use `swift build` then executable launch.
- SwiftPM GUI apps create `dist/<AppName>.app`, copy the binary to `Contents/MacOS/`, generate minimal `Info.plist` (`APPL`, executable, identifier, name, minimum system version, `NSApplication`), then launch with `/usr/bin/open -n`.
- For GUI logs/telemetry, launch the bundle first, then stream unified logs.
- `--verify` should confirm process existence with `pgrep -x <AppName>`.

## Debugging

- Use `--logs`/`--telemetry` for config, entitlements, sandbox, and action-event proof.
- If a SwiftPM GUI bundle launches but does not foreground, check `NSApp.setActivationPolicy(.regular)` and `NSApp.activate(ignoringOtherApps: true)`.
- Use `--debug` or direct `lldb` for symbolized crash debugging.
- Switch to `macos-telemetry-probe` when verifying specific window/sidebar/menu/menu-bar actions.
- Use Xcode-aware MCP only when explicitly requested and it fits macOS discovery/debugging; fall back to shell when it does not.

## Guardrails

- Do not initialize source control merely to build, run, or debug an app.
- Do not replace an established project entrypoint with the bootstrap script
  unless the user explicitly requests that change.
- A bounded one-shot command is appropriate for a one-shot task; create durable
  automation only when it will be reused or the user requests it.
- Do not write Codex environment config unless the user requests a Run action
  and the target entrypoint already exists.
- Do not describe mobile/simulator workflows as macOS workflows.
- Do not claim UI state you cannot inspect.

## Output

Report detected project type, existing entrypoint selected, command run,
build/launch result, any durable artifacts explicitly created, top blocker if
failed, and the smallest next action.
