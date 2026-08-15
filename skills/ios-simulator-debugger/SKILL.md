---
name: ios-simulator-debugger
description: Debug iOS Simulator apps with XcodeBuildMCP for build, run, launch, UI inspection, interaction, screenshots, and logs; route user-visible mirrors and SwiftUI previews to `ios-simulator-browser`.
---

# iOS Simulator Debugger

Before invoking Apple-only binaries, confirm the execution context is macOS. From Windows or Linux, run those steps in a Mac SSH project or through an already configured remote transport; do not retry missing Apple binaries locally.

Use the configured XcodeBuildMCP transport for simulator control, build/run, UI inspection, screenshots, interaction, and logs. Tool namespaces vary by agent, so the names below are the canonical XcodeBuildMCP tool names.

If the user should see or interact with the running app, prefer `ios-simulator-browser` after this skill has selected or launched the Simulator. Keep this skill focused on build/run, logs, bundle IDs, UI tree inspection, and headless simulator automation.

## Workflow

1. Inspect current defaults with `session_show_defaults` before the first build, run, or test operation.
2. Discover a booted simulator with `list_sims`. If none is booted, ask the user to boot one unless they asked you to boot it.
3. Set defaults with `session_set_defaults`: `projectPath` or `workspacePath`, `scheme`, `simulatorId`, optional `configuration: "Debug"` and `useLatestOS: true`.
4. Build/run with `build_run_sim` when requested. If the build fails, inspect output and retry only when justified, optionally with `preferXcodebuild: true`.
5. After a successful run, verify launch with `snapshot_ui` or `screenshot` before UI interaction.
6. If only launch is requested, use `launch_app_sim`. If bundle id is unknown, call `get_sim_app_path` then `get_app_bundle_id`.

## Interaction

- Snapshot before acting: `snapshot_ui`.
- Tap by `id` or `label` first; coordinates only when needed.
- Type after focusing a field with `type_text`.
- Use `gesture` for scrolls and edge swipes.
- Capture visual proof with `screenshot`.

## Logs

Use `build_run_sim` or `launch_app_sim`; current XcodeBuildMCP releases capture
runtime logs automatically and return the log path in the structured result.
Read that returned file and summarize important lines. Relaunch through the
same tool when fresh console output is required.

## Troubleshooting

Wrong app means verify scheme/bundle id. Non-hittable elements require a fresh `snapshot_ui` after layout changes. Do not keep interacting after an unhandled build or launch failure.
