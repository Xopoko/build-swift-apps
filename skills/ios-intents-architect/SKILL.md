---
name: ios-intents-architect
description: Design and implement App Intents, AppEntity, EntityQuery, and App Shortcuts for iOS system surfaces such as Shortcuts, Siri, Spotlight, widgets, controls, and app handoff routes.
---

# iOS Intents Architect

Expose the smallest useful action and entity surface to the system. Start with verbs and objects users need outside the app, then route cleanly back into the app when needed.

## Workflow

1. Choose 1-3 high-value actions. Prefer verbs like compose, open, find, filter, continue, inspect, or start. Do not mirror the app navigation tree.
2. Add only the `AppEntity` types the system must understand. Keep them narrower than persistence models. Add `EntityQuery` when suggestions or disambiguation are useful.
3. Decide execution mode:
   - direct system-surface action for work that can finish inline
   - `openAppWhenRun` or open-style intent when the user should land in an app workflow
   - one predictable handoff route in the scene/root router when the app must react
   - separate inline and open-app intents when one compromise would be unclear
4. Add `AppShortcutsProvider` for the first useful set. Keep titles, phrases, and symbols direct and task-oriented.
5. Reuse the same action/entity surface for widgets and controls when their parameters match.
6. Build and verify that intents compile, open or execute correctly, and route to the expected state.

## Defaults

- Prefer a dedicated intents target or module.
- Keep intent types thin; business logic stays in app services or domain models.
- Use `AppEnum` for fixed choices such as tabs, modes, or visibility before creating entities.
- Treat App Intents as system integration infrastructure, not only a Shortcuts feature.

## Avoid

- one intent per screen or tab without real user value
- mirroring the full model graph as entities
- global side-effect handoff with no clear app entry path
- vague shortcut phrases or generic titles
- broad taxonomy work in the first pass

## Resources

Read only what is needed:

- `references/first-pass-checklist.md`: choose the first intent/entity surface.
- `references/example-patterns.md`: copyable patterns.
- `references/code-templates.md`: generalized code templates.
- `references/system-surfaces.md`: Shortcuts, Siri, Spotlight, widgets, and controls.

Use current Apple Developer docs when APIs or platform behavior may have changed:

- `https://developer.apple.com/documentation/appintents/making-actions-and-content-discoverable-and-widely-available`
- `https://developer.apple.com/documentation/appintents/creating-your-first-app-intent`
- `https://developer.apple.com/documentation/appintents/adopting-app-intents-to-support-system-experiences`

Output the exposed actions, backing entities, invocation mode, app handoff path, and validation result.
