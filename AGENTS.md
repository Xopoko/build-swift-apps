# Agent Guidance

This repository is a multi-agent skill pack for Swift and Apple-platform
development. It should stay generic, public-safe, and useful across Codex,
Claude Code, Cursor, pi, and manual skill installs.

## Project Shape

- `skills/` contains installable Agent Skills. Each directory must contain one
  `SKILL.md` entrypoint and any local scripts or references that skill needs.
- `shared/` contains canonical support files used by multiple skills. Link to
  shared files instead of duplicating long guidance.
- `commands/` contains short command entrypoints that delegate to canonical
  skills.
- `.codex-plugin/`, `.claude-plugin/`, `.cursor-plugin/`, `agents/`, and
  `package.json` are packaging surfaces for different agents. Keep them in sync
  when skills are added or removed.
- `docs/INSTALL.md` is the user-facing installation and dependency guide.
- `scripts/doctor.sh`, `scripts/install-deps.sh`, and
  `scripts/validate-package.sh` are the operational checks for new machines and
  release hygiene.

## Scope

The plugin is for Swift application development across Apple platforms, with the
strongest coverage for iOS and macOS. Do not add company-specific workflows,
private service names, customer project names, or credentials. Keep examples
generic and reusable.

## Skill Catalog

| Area | Skills |
| --- | --- |
| Build, run, debug, test | `macos-runtime-debugger`, `macos-swiftpm-runner`, `macos-test-diagnoser`, `xcode-ui-test-stabilizer`, `macos-telemetry-probe` |
| iOS simulator and runtime evidence | `ios-simulator-debugger`, `ios-rocketsim-operator`, `ios-ettrace-profiler`, `ios-memgraph-inspector`, `swiftui-performance-inspector` |
| SwiftUI, AppKit, and product UI | `ios-swiftui-architect`, `macos-swiftui-architect`, `swiftui-view-architect`, `macos-view-architect`, `macos-appkit-bridge`, `macos-window-architect`, `ios-intents-architect`, `macos-liquid-glass-designer`, `ios-liquid-glass-designer` |
| Xcode build performance | `xcode-build-strategist`, `xcode-build-baseline`, `xcode-compile-profiler`, `xcode-project-auditor`, `swiftpm-build-inspector`, `xcode-build-tuner` |
| Release and distribution | `macos-signing-inspector`, `macos-notarization-packager`, and the `appstore-*` App Store Connect skills |
| Tuist and generated projects | `tuist-migration-planner`, `tuist-workspace-navigator`, `tuist-generation-doctor`, `tuist-flaky-test-stabilizer` |
| Research and low-level Apple work | `apple-dev-research`, `apple-firmware-inspector` |

## Rules For Editing

- Prefer small, focused skills over broad catch-all instructions.
- Put repeated logic in `shared/` and reference it from skills.
- Do not copy private company workflows into this repository.
- Keep skill descriptions trigger-friendly and specific.
- Use ASCII by default in repository files.
- Do not add host-tool assumptions without documenting them in
  `docs/INSTALL.md`, `scripts/doctor.sh`, and `scripts/install-deps.sh`.
- When a skill is added, removed, or renamed, update:
  - README skill tables
  - `AGENTS.md`
  - `.cursor-plugin/plugin.json`
  - `package.json`
  - dependency docs/scripts if the skill needs a CLI

## Validation

Run these before committing:

```bash
./scripts/validate-package.sh
./scripts/doctor.sh --profile core --profile mcp
```

`doctor.sh --all` can report optional missing tools on a healthy machine. Treat
missing required tools as blockers; document optional gaps clearly.

## Multi-Agent Notes

- Claude Code loads plugin components from the plugin root. Keep only manifests
  inside `.claude-plugin/`.
- Cursor packaging uses `.cursor-plugin/plugin.json` and the root `skills/`
  directory.
- Codex packaging uses `.codex-plugin/plugin.json`; do not remove it.
- Generic coding agents should be able to understand the repository through
  this `AGENTS.md` file and the README without reading every skill.
