# /macos-runtime-debug

Explicitly bootstrap or refresh a reusable project-local macOS
`script/build_and_run.sh` loop. For a one-shot build, launch, log, or debug task,
use `macos-runtime-debugger` directly instead of invoking this bootstrap
command.

## Arguments

- `scheme`: Xcode scheme name (optional)
- `workspace`: path to `.xcworkspace` (optional)
- `project`: path to `.xcodeproj` (optional)
- `product`: SwiftPM executable product name (optional)
- `mode`: `run`, `debug`, `logs`, `macos-telemetry-probe`, or `verify` (optional, default: `run`)
- `app_name`: process/app name to stop before relaunching (optional)
- `run_action`: add or update a Codex Run action after the script exists (optional, default: false)

## Workflow

1. Detect whether the repo uses an Xcode workspace, Xcode project, or SwiftPM package.
2. Inspect and preserve existing run scripts, schemes, arguments, and host actions; reuse their working project-specific details instead of replacing them blindly.
3. Create or update `script/build_and_run.sh` so it stops the current app, builds the macOS target, and launches the fresh result.
4. For SwiftPM, keep raw executable launch only for true CLI tools; for AppKit/SwiftUI GUI apps, create a project-local `.app` bundle and launch it with `/usr/bin/open -n`.
5. Support optional script flags for `--debug`, `--logs`, `--telemetry`, and `--verify`.
6. Follow the canonical bootstrap contract in `../skills/macos-runtime-debugger/references/run-button-bootstrap.md` for the exact script shape.
7. When `run_action` is true, add or update the Codex Run action after the script exists; otherwise leave Codex environment configuration unchanged.
8. Run the script in the requested mode and summarize any build, script, or launch failure.

## Guardrails

- Do not initialize source control as part of this bootstrap.
- Preserve an established entrypoint unless the user explicitly asks to replace it.
- Do not leave stale `Run` actions pointing at old script paths.
- Keep the no-flag script path simple: kill, build, run.
- Use `--debug`, `--logs`, `--telemetry`, or `--verify` only when the user asks for those modes.
