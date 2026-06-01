---
name: macos-window-architect
description: "Customize macOS 15+ SwiftUI windows and scene behavior: toolbar/title visibility, drag regions, window materials, minimize/restoration, default/ideal placement, launch behavior, and borderless windows."
---

# macOS Window Architect

Use SwiftUI scene/window modifiers first; switch to `macos-appkit-bridge` only when SwiftUI cannot express the behavior.

## Workflow

1. Classify the window role: main navigation, inspector/detail, About/support, media, welcome, or borderless custom surface.
2. Adjust toolbar/title/background for that role.
3. If toolbar chrome is hidden, add a reliable drag region.
4. Set minimize, restoration, resize, launch, default placement, and ideal zoom behavior.
5. Build/launch with `macos-runtime-debugger`.

## Patterns

- Hidden title but meaningful logical title:
  ```swift
  WindowGroup("Destination Video") {
    CatalogView()
      .toolbar(removing: .title)
      .toolbarBackgroundVisibility(.hidden, for: .windowToolbar)
  }
  ```
- Utility/About material window:
  ```swift
  Window("About", id: "about") {
    AboutView()
      .toolbar(removing: .title)
      .toolbarBackgroundVisibility(.hidden, for: .windowToolbar)
      .containerBackground(.thickMaterial, for: .window)
  }
  .windowMinimizeBehavior(.disabled)
  .restorationBehavior(.disabled)
  ```
- Placement from content/display:
  ```swift
  WindowGroup("Player", for: Video.self) { $video in
    PlayerView(video: video)
  }
  .defaultWindowPlacement { content, context in
    WindowPlacement(size: clampToDisplay(content.sizeThatFits(.unspecified),
                                         displayBounds: context.defaultDisplay.visibleRect))
  }
  .windowIdealPlacement { content, context in
    let size = zoomToFit(content.sizeThatFits(.unspecified),
                         displayBounds: context.defaultDisplay.visibleRect)
    return WindowPlacement(centeredPosition(for: size, in: context.defaultDisplay.visibleRect), size: size)
  }
  ```
- Drag region after hidden toolbar:
  ```swift
  Color.clear
    .frame(height: 48)
    .contentShape(Rectangle())
    .gesture(WindowDragGesture())
    .allowsWindowActivationEvents(true)
  ```
- Borderless/welcome:
  ```swift
  Window("Welcome", id: "welcome") { WelcomeView() }
    .windowStyle(.plain)
    .defaultLaunchBehavior(.presented)
  ```

## Rules

- Use `.toolbar(removing: .title)` for visual title removal, not semantic title removal.
- Use `.toolbarBackgroundVisibility(.hidden, for: .windowToolbar)` for top-edge content; `.toolbarVisibility(.hidden, for: .windowToolbar)` only when the toolbar disappears entirely.
- Add `WindowDragGesture()` on a non-control overlay when toolbar drag affordance is lost.
- Use `.containerBackground(.thickMaterial, for: .window)` for utility/About glass-like backdrops instead of hardcoded translucency.
- Disable minimize/restoration only for windows where reopening/minimizing is undesirable; keep primary document/navigation restoration by default.
- Use `content.sizeThatFits(.unspecified)` plus `context.defaultDisplay.visibleRect`; consider external, small, and rotated displays.
- Borderless `.windowStyle(.plain)` windows need obvious move/close affordances.

## Guardrails

- Do not hide toolbar/title chrome without preserving drag and accessibility.
- Do not disable restoration on main windows unless explicitly requested.
- Do not hardcode one monitor size.
- Do not mutate `NSWindow` before checking SwiftUI modifiers: `.windowMinimizeBehavior`, `.restorationBehavior`, `.defaultWindowPlacement`, `.windowIdealPlacement`, `.windowStyle`, `.defaultLaunchBehavior`.

Use `macos-swiftui-architect` for broader scene architecture, `macos-liquid-glass-designer` for visual material adoption, and `macos-appkit-bridge` for true `NSWindow`/`NSPanel` needs.
