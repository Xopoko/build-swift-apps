---
name: ios-swiftui-architect
description: "Build or refactor iOS SwiftUI views/components: navigation, TabView, sheets, async state, responsive stacks/grids, state ownership, environment injection, previews, and performance-aware declarative UI."
---

# iOS SwiftUI Architect

Use for iOS SwiftUI UI structure and component choices. Read the nearest local example before introducing a new pattern.

## Start

- Existing project: identify screen model (list/detail/editor/settings/tab), search for nearby examples (`rg "TabView\\("`, etc.), then read `references/components-index.md`.
- New app: start with `references/app-wiring.md` for TabView + NavigationStack + sheets, then expand route/sheet enums as screens appear.
- For scroll-driven reveals, read `references/scroll-reveal.md` before hand-rolling gestures.

## Rules

- Prefer `@State`, `@Binding`, `@Observable`, and `@Environment`; avoid unnecessary view models.
- If iOS 16 or earlier is supported, use `ObservableObject` with `@StateObject` at the owner and `@ObservedObject` for injection.
- Keep views small, composed, and project-formatted.
- Use `.task`/`.task(id:)` with loading/error states; read `references/async-state.md` for cancellation/debouncing.
- Put shared app services in `@Environment`; keep feature-local dependencies as explicit inputs.
- Prefer newest SwiftUI APIs that match deployment target and call out minimum OS.
- Maintain legacy patterns only inside legacy files.
- Sheets: prefer `.sheet(item:)`, avoid `if let` inside sheet bodies, let sheets call `dismiss()` internally.
- Scroll reveals: derive one normalized progress value from scroll offset instead of parallel gesture state machines when possible.

## State Ownership

| Scenario | Pattern |
| --- | --- |
| Local UI state | `@State` |
| Child mutates parent value | `@Binding` |
| Root-owned iOS 17+ reference model | `@State` with `@Observable` |
| Injected iOS 17+ observable | explicit stored property |
| Shared service/config | `@Environment(Type.self)` |
| iOS 16 legacy model | `@StateObject` owner, `@ObservedObject` injected |

Choose ownership first; do not introduce a reference model when value state is enough.

## New View Workflow

1. Define state ownership, dependencies, and minimum OS.
2. Sketch hierarchy, routing, and presentation; read navigation/sheet/deeplink refs when complex.
3. Build and verify before widening call-site changes.
4. Add async loading and explicit error/loading UI when needed.
5. Add previews for primary/secondary states and accessibility IDs/labels for interactive UI.
6. Validate build/previews/state propagation/list identity/observation scope. If build fails, fix the exact error before continuing.

## Anti-Patterns

- Giant views mixing layout, business logic, networking, routing, and formatting.
- Multiple booleans for exclusive sheets/alerts/destinations.
- Live service calls from `body`.
- `AnyView` as a composition escape hatch.
- Defaulting every shared dependency to `@EnvironmentObject` or a global router.

## References

- `references/components-index.md`
- `references/navigationstack.md`
- `references/sheets.md`
- `references/deeplinks.md`
- `references/app-wiring.md`
- `references/async-state.md`
- `references/previews.md`
- `references/performance.md`

Use current Apple docs when API availability or platform guidance may have changed. New component refs should be short, actionable, and listed in `components-index.md`.
