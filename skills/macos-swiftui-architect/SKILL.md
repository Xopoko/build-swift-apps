---
name: macos-swiftui-architect
description: "Build or refactor native macOS SwiftUI scenes and components: windows, commands, toolbars, settings, split views, inspectors, menu bar extras, keyboard workflows, and desktop layouts."
---

# macOS SwiftUI Architect

Use for macOS SwiftUI scene/component choices. Use `macos-runtime-debugger` for build/run, `macos-view-architect` for large-file extraction, and `macos-appkit-bridge` for AppKit-only behavior.

## Start

- Existing project: read nearest scene/root view, identify interaction model, then open the relevant file from `references/components-index.md`.
- New app: choose scene model first: `WindowGroup`, `Window`, `Settings`, `MenuBarExtra`, or `DocumentGroup`.
- For menu-bar apps that should also show normal windows, use `@NSApplicationDelegateAdaptor`, `.regular` activation policy, and activate on launch.
- Use `WindowGroup(..., id:)` for a primary launched window; `Window(...)` for auxiliary/on-demand singleton windows.
- Decide state ownership before writing views: app-wide, scene/window scoped, or local.

## Desktop Rules

- Design for pointer, keyboard, menus, multiple windows, toolbars, sidebars, inspectors, context menus, and search.
- Keep scenes explicit; do not hide settings, utility windows, or menu-bar flows inside one giant `ContentView`.
- Prefer system colors/materials and semantic foreground styles; avoid hardcoded white roots and opaque custom sidebars unless requested.
- Use `@SceneStorage` for per-window ephemeral state and `@AppStorage` for preferences.
- Prefer stable sidebar selection and `NavigationSplitView` over iOS-style push navigation when persistent structure helps.
- Keep primary actions available through UI chrome and keyboard/menu paths.
- Use SwiftUI-native APIs first; switch to `macos-appkit-bridge` for responder chain, panels, low-level windows, or text system control.

## Sidebar Pattern

Native source-list rows: one leading icon, one title, and optional secondary detail line. Put dense metadata/cards in detail or inspector panes, not every sidebar row.

```swift
List(selection: $selection) {
  ForEach(items) { item in
    HStack(spacing: 10) {
      Image(systemName: item.systemImage).frame(width: 16).foregroundStyle(.secondary)
      VStack(alignment: .leading, spacing: 2) {
        Text(item.title).lineLimit(1)
        if let detail = item.detail {
          Text(detail).font(.caption).foregroundStyle(.secondary).lineLimit(1)
        }
      }
    }
    .tag(item.id)
  }
}
.listStyle(.sidebar)
```

Let `NavigationSplitView` sidebars use native materials. Apply custom surfaces only to detail cards or inspector sections.

## State Ownership

| Scenario | Pattern |
| --- | --- |
| Local control state | `@State` |
| Child mutates parent value | `@Binding` |
| Root-owned `@Observable` | `@State` |
| Injected observable/service | property or `@Environment(Type.self)` |
| Window selection/expansion | `@SceneStorage` when practical |
| Durable preference | `@AppStorage` |
| Legacy observable | `@StateObject` owner, `@ObservedObject` injected |

## Avoid

One app-sized `ContentView`; touch-first flows without desktop affordances; actions only behind gestures; menu bar labels over 30 characters; settings as a main-window destination; card sidebars inside `.sidebar` lists unless requested; opaque split-pane backgrounds by default; AppKit bridges before SwiftUI scenes/commands/windows have been tried.

## New Scene

Pick scene type/state ownership, place actions in content/toolbar/commands/inspector/settings, choose layout, split files by responsibility, add keyboard/menu/toolbar exposure, then build/run and check multiwindow behavior, settings entry points, and selection stability.

## References

- `references/components-index.md`
- `references/windowing.md`
- `references/settings.md`
- `references/commands-menus.md`
- `references/split-inspectors.md`
- `references/menu-bar-extra.md`
