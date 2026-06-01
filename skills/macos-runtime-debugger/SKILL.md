---
name: macos-runtime-debugger
description: Build, run, and debug local macOS apps or desktop executables with shell-first Xcode/Swift workflows. Use for Mac app builds, launch scripts, compiler/linker/startup failures, logs, telemetry, or desktop runtime debugging.
---

# macOS Runtime Debugger

Create one project-local `script/build_and_run.sh` and use it as the default build/run/debug path. In Codex app sessions, optionally wire the same script to `.codex/environments/environment.toml`.

## Workflow

1. Discover project shape:
   ```bash
   git rev-parse --is-inside-work-tree
   find . -name '*.xcworkspace' -o -name '*.xcodeproj' -o -name 'Package.swift'
   ```
   If no git repo exists and a host tool needs one, run `git init` at the workspace root, never inside a nested repo.
2. Resolve runnable target/process:
   - Xcode: list schemes and prefer the app-producing scheme unless named.
   - SwiftPM CLI: run the executable.
   - SwiftPM AppKit/SwiftUI GUI: stage a project-local `.app` bundle and launch with `/usr/bin/open -n`; do not run as a raw executable.
3. Create/update executable `script/build_and_run.sh`. It should kill existing process, build, launch, and support optional `--debug`, `--logs`, `--telemetry`, and `--verify`.
4. Use `references/run-button-bootstrap.md` as the canonical script/environment shape; do not duplicate a second full snippet.
5. In Codex app sessions, create/update `.codex/environments/environment.toml` only after the script exists; point the Run action at `./script/build_and_run.sh`.
6. Run through the script:
   ```bash
   ./script/build_and_run.sh
   ./script/build_and_run.sh --debug
   ./script/build_and_run.sh --logs
   ./script/build_and_run.sh --telemetry
   ./script/build_and_run.sh --verify
   ```
7. Classify failures as compiler, linker, signing, build settings, missing SDK/toolchain, script bug, or runtime launch. Quote the smallest useful error.

## Script Requirements

- Keep it outside app source in `script/build_and_run.sh`.
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

- Do not leave a one-off command chain when a stable script can own the flow.
- Do not write Codex environment config before the script exists.
- Do not describe mobile/simulator workflows as macOS workflows.
- Do not claim UI state you cannot inspect.

## Output

Report detected project type, script/env path configured, command run, build/launch result, top blocker if failed, and the smallest next action.
