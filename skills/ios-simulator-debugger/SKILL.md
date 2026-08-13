---
name: ios-simulator-debugger
description: Debug iOS Simulator apps with XcodeBuildMCP for build, run, launch, UI inspection, interaction, screenshots, and logs; route user-visible mirrors and SwiftUI previews to `ios-simulator-browser`.
---

# iOS Simulator Debugger

Use XcodeBuildMCP for simulator control, build/run, UI inspection, screenshots, interaction, and logs.

If the user should see or interact with the running app, prefer `ios-simulator-browser` after this skill has selected or launched the Simulator. Keep this skill focused on build/run, logs, bundle IDs, UI tree inspection, and headless simulator automation.

## Workflow

1. Discover a booted simulator with `mcp__XcodeBuildMCP__list_sims`. If none is booted, ask the user to boot one unless they asked you to boot it.
2. Set defaults with `mcp__XcodeBuildMCP__session-set-defaults`: `projectPath` or `workspacePath`, `scheme`, `simulatorId`, optional `configuration: "Debug"` and `useLatestOS: true`.
3. Build/run with `mcp__XcodeBuildMCP__build_run_sim` when requested. If the build fails, inspect output and retry only when justified, optionally with `preferXcodebuild: true`.
4. After a successful run, verify launch with `mcp__XcodeBuildMCP__describe_ui` or `mcp__XcodeBuildMCP__screenshot` before UI interaction.
5. If only launch is requested, use `mcp__XcodeBuildMCP__launch_app_sim`. If bundle id is unknown, call `mcp__XcodeBuildMCP__get_sim_app_path` then `mcp__XcodeBuildMCP__get_app_bundle_id`.

## Interaction

- Describe before acting: `mcp__XcodeBuildMCP__describe_ui`.
- Tap by `id` or `label` first; coordinates only when needed.
- Type after focusing a field with `mcp__XcodeBuildMCP__type_text`.
- Use `mcp__XcodeBuildMCP__gesture` for scrolls and edge swipes.
- Capture visual proof with `mcp__XcodeBuildMCP__screenshot`.

## Logs

Use `mcp__XcodeBuildMCP__build_run_sim` or
`mcp__XcodeBuildMCP__launch_app_sim`; current XcodeBuildMCP releases capture
runtime logs automatically and return the log path in the structured result.
Read that returned file and summarize important lines. Relaunch through the
same tool when fresh console output is required.

## Troubleshooting

Wrong app means verify scheme/bundle id. Non-hittable elements require fresh `describe_ui` after layout changes. Do not keep interacting after an unhandled build or launch failure.
