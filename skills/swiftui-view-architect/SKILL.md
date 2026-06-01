---
name: swiftui-view-architect
description: Refactor SwiftUI view files toward small dedicated subviews, MV-first data flow, stable view trees, explicit dependencies, extracted actions, and correct Observation usage.
---

# SwiftUI View Architect

Default to vanilla SwiftUI: local state in views, shared dependencies in environment/services, business logic outside view bodies, and view models only when requested or already present.

## Ordering

Preserve stronger local conventions; otherwise order stored members top-to-bottom:

1. environment
2. `let` inputs
3. `@State`/other stored properties
4. non-view computed vars
5. `init`
6. `body`
7. view builders/helpers
8. actions/async helpers

## Rules

- Prefer MV over MVVM. Do not introduce a view model just to mirror local state or wrap environment dependencies.
- Split long bodies into dedicated `View` types with explicit inputs/bindings/callbacks. Keep computed `some View` helpers small and rare.
- Extract non-trivial button actions and side effects from `body`; call private methods, and move real domain logic into services/models.
- Keep a stable root view tree. Avoid top-level `if/else` swapping entire root branches; localize conditions in sections/modifiers/overlays/toolbars.
- If a view model exists, prefer non-optional state initialized in `init`:
  ```swift
  @State private var viewModel: SomeViewModel
  init(dependency: Dependency) {
    _viewModel = State(initialValue: SomeViewModel(dependency: dependency))
  }
  ```
- For `@Observable` owners on iOS 17+, store as `@State` and pass explicitly. For iOS 16 or earlier, use `@StateObject` owner and `@ObservedObject` injection.
- Keep behavior/layout intact unless the user asked for a product change.

## Workflow

1. Reorder the view.
2. Move inline actions/effects out of `body`.
3. Extract meaningful sections into dedicated subviews; move reusable/independent subviews to files.
4. Stabilize root structure.
5. Normalize view model and Observation usage.
6. Build/test the touched surface.

## Large Views

For ~300+ line files, split aggressively into section views and small private helpers. `// MARK:` extensions can organize actions/helpers but are not a substitute for extracting real subviews.

Reference: `references/mv-patterns.md`. Use current Apple docs when SwiftUI/Observation behavior may have changed.
