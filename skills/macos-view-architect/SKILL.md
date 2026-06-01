---
name: macos-view-architect
description: Refactor macOS SwiftUI views/scenes into small stable subviews, explicit scene roots, command/toolbar ownership, scene-aware state, and narrow AppKit bridges.
---

# macOS View Architect

Refactor macOS SwiftUI toward explicit scene structure and focused files. Use `macos-swiftui-architect` for missing desktop patterns and `macos-appkit-bridge` for true AppKit boundaries.

## Rules

- Model scenes explicitly: main window, settings, utility windows, inspectors, menu bar extras.
- Keep predictable order unless local style is stronger: environment, inputs, state, non-view computed vars, init, body, view helpers, actions.
- Split responsibilities:
  - `App/<AppName>App.swift`: `@main` app and minimal delegate only.
  - `Views/*`: root composition and feature UI.
  - `Models/*`: values, IDs, selection enums.
  - `Stores/*`: state stores.
  - `Services/*`: network, app-server, process clients.
  - `Support/*`: small formatters/resolvers/extensions.
- Accept one-file apps only for tiny throwaway snippets: ~50 lines, one screen, no persistence/network/process client/reusable models.
- Prefer dedicated subview types over many computed `some View` fragments; pass explicit data, bindings, and actions.
- Keep root layout stable around selection/scenes/commands; avoid top-level branch swaps.
- Extract non-trivial actions, command routing, and toolbar behavior from `body`.
- Use `@SceneStorage` for per-window ephemeral state and `@AppStorage` for durable preferences.
- Keep AppKit bridges isolated behind small wrappers/helpers.
- For modern `@Observable` owners, use `@State`; on older targets use `@StateObject`/`@ObservedObject`.

## Workflow

1. Identify scene boundary and whether the file owns too many responsibilities.
2. Reorder top-to-bottom.
3. Extract sidebar rows, detail panels, inspectors, toolbar content, and utility surfaces into subviews/files.
4. Stabilize selection/layout.
5. Move action/command/toolbar logic into named helpers or types.
6. Narrow AppKit edges.
7. Build after each major split and keep behavior intact unless requested.

## Smells

- One root view owns window scaffolding, settings, toolbar, commands, service clients, and detail layout.
- iOS push navigation forced into a Mac sidebar-detail problem.
- Several booleans for mutually exclusive inspectors/sheets/windows.
- AppKit objects passed through unrelated SwiftUI layers.
- Large computed view fragments replacing real subviews.
