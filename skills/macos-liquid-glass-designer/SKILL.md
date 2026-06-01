---
name: macos-liquid-glass-designer
description: "Implement, refactor, or review modern macOS SwiftUI Liquid Glass UI: NavigationSplitView, toolbars, search, sheets, controls, system materials, `glassEffect`, `GlassEffectContainer`, and `glassEffectID`."
---

# macOS Liquid Glass Designer

Modernize macOS SwiftUI UI by using standard app structure and system materials first; add custom glass only for app-specific surfaces.

## Workflow

1. Inspect the scene/root view and identify the pattern: split view, tab, sheet, toolbar, inspector, custom floating controls.
2. Remove custom opaque backgrounds, scrims, and toolbar/sheet fills that fight system material unless intentionally required.
3. Update standard SwiftUI structure and controls first.
4. Add `glassEffect` only where standard controls do not cover the design.
5. Validate grouping, transitions, icon treatment, pointer/keyboard usability, and foreground activation. Use `macos-runtime-debugger` for SwiftPM GUI apps.

## Rules

- Prefer `NavigationSplitView`; let sidebars use system Liquid Glass material.
- Use `backgroundExtensionEffect` for hero/media that should extend beyond safe area near floating chrome.
- Keep inspectors visually lighter than or equal to the content they inspect.
- Keep `TabView` for persistent top-level sections; do not force iPhone tab/search patterns onto macOS.
- Remove old `presentationBackground` imitation layers when the system sheet material is enough.
- Put hierarchy-wide search on `NavigationSplitView`; use `searchToolbarBehavior` for compact secondary search.
- Assume toolbar items live on floating glass; use `ToolbarSpacer`, `sharedBackgroundVisibility`, and `badge` instead of custom chrome.
- Tint icons/glass only for semantic meaning.
- Prefer standard controls and system glass/prominent button styles before custom translucent buttons.
- Use `controlSize`, `buttonBorderShape`, slider `step`/ticks/`neutralValue`, and `Label` before custom controls.
- Use concentric rectangle/container corner configuration for custom shapes that must align with sheet/card/window corners.

## Custom Glass

- `glassEffect` defaults to a capsule-like shape and vibrant text; pass an explicit shape when needed.
- Use `.interactive()` for custom controls/containers with interactive elements.
- Put nearby custom glass in one `GlassEffectContainer`; separate containers cannot sample each other correctly.
- Use `glassEffectID` with a local `@Namespace` for collapsed/expanded morphing with stable identity.

## Guardrails

- Do not rebuild sidebars, toolbars, sheets, or controls from scratch when SwiftUI APIs provide the behavior.
- Do not leave opaque backgrounds behind `NavigationSplitView`, toolbars, or sheets by default.
- Do not scatter related glass elements across containers.
- Do not tint for decoration alone.
- Do not review Liquid Glass behavior from a bare SwiftPM executable; launch a foreground `.app` bundle.

Use `macos-swiftui-architect` for scene architecture, `macos-view-architect` for large-view structure, `macos-appkit-bridge` for AppKit-only behavior, and `macos-runtime-debugger` for launch/log verification.
