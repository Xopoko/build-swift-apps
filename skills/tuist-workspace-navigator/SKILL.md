---
name: tuist-workspace-navigator
description: Work productively in Tuist-generated Xcode workspaces. Use for `tuist generate`, generated workspace builds, focused generation, tags, buildable folders, and Xcode build/test commands after generation.
---

# Tuist Workspace Navigator

Use this skill for day-to-day development in projects where Tuist owns the
Xcode workspace.

## Defaults

- Run generation non-interactively:
  ```bash
  tuist generate --no-open
  ```
- Build and test with `xcodebuild` against the generated workspace.
- Regenerate after manifest, dependency, target graph, or resource layout
  changes.
- Run `tuist install` before generation when package dependencies changed.

## Focused Generation

Prefer smaller generated graphs when working on one feature or target:

```bash
tuist generate AppFeature AppFeatureTests --no-open
tuist generate tag:feature:payments --no-open
```

Use target tags consistently for teams, layers, and features so agents can
scope generation and testing without guessing target names.

## Manifest Guidance

- Prefer file-system-synchronized buildable folders when the project uses them;
  keep paths aligned with the real source tree.
- Do not overlap broad source/resource globs with buildable folders.
- Keep build configurations aligned between local targets and external
  dependencies.
- Treat `.intentdefinition` as source and avoid double-including localization
  files such as `.xcstrings`, `.strings`, and `.stringsdict`.
- Keep package product type overrides deliberate; making every dependency
  dynamic can hide linker problems and hurt launch time.

## Build

```bash
xcodebuild build \
  -workspace App.xcworkspace \
  -scheme App \
  -destination "platform=iOS Simulator,name=<available iPhone simulator>,OS=latest"
```

## Test

Prefer narrow `xcodebuild test` selectors for iteration:

```bash
xcodebuild test \
  -workspace App.xcworkspace \
  -scheme AppTests \
  -only-testing AppTests/MySuite/testExample
```

If a narrow selector runs zero tests, broaden to the suite or target and report
that the selector did not match.

## Troubleshooting

- Missing products: run `tuist install`, then regenerate.
- Type not found: check excluded source folders and generated files.
- Resource not found at runtime: inspect resource globs and package resources.
- Undefined symbols: verify SDK dependencies and product type overrides.
- Objective-C category crash: add `-ObjC` or targeted `-force_load` where the
  consuming target needs it.

Report the generated workspace path, scheme, command, and final build/test
result.
