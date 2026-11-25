---
name: swiftui-view-architect
description: Refactor SwiftUI views by splitting independent sections, clarifying state ownership, and moving domain logic out of view bodies while preserving behavior.
---

# SwiftUI View Architect

1. Identify sections with separate responsibilities and record the current layout, navigation, and state behavior.
2. Extract those sections into views with explicit values, bindings, or actions. Follow local file organization.
3. Keep state with the nearest owner that needs its lifetime. Use `@State` for local values and owned `@Observable` references on supported platforms. For `ObservableObject`, use `@StateObject` for ownership and `@ObservedObject` for injection.
4. Keep domain logic in the project's models or services. Use a presentation model when the feature needs shared presentation state or an adapter with a separate lifetime. Keep one source of truth when refactoring existing state.
5. Build and check that the extracted views preserve parent state, navigation, and selection. Keep local conditions inside the subtree they affect when replacing a whole branch would reset unrelated state.

See [async state and task lifecycle](../../shared/swiftui/async-state.md) for view-owned loads and searches.
