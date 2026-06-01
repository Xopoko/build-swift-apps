---
name: tuist-migration-planner
description: Migrate existing Xcode projects toward Tuist-generated workspaces. Use when converting hand-maintained Xcode projects, mapping targets/settings/dependencies, or validating generated builds and launches.
---

# Tuist Migration Planner

Use this skill to move an existing Xcode project to Tuist without losing build,
test, signing, or runtime behavior.

## Workflow

1. Baseline the current Xcode project.
2. Inventory targets, schemes, settings, scripts, resources, entitlements, and
   dependencies.
3. Create minimal Tuist manifests.
4. Generate, build, and launch.
5. Fix gaps iteratively and document every intentional divergence.

## Baseline First

Capture a known-good command before writing manifests:

```bash
xcodebuild build \
  -project App.xcodeproj \
  -scheme App \
  -configuration Debug \
  -destination "platform=iOS Simulator,name=<available iPhone simulator>,OS=latest" \
  -derivedDataPath DerivedDataBaseline
```

Record the scheme, configuration, deployment targets, bundle identifiers,
Info.plist paths, entitlements, build scripts, and package graph.

## Create Manifests

- `Tuist.swift`: keep generation options explicit.
- `Project.swift`: model targets, sources, resources, scripts, settings, and
  dependencies.
- `Tuist/Package.swift`: declare external Swift packages and product mappings.
- `.xcconfig`: move large or shared build settings out of manifests when useful.

Keep the first generated graph close to the original project. Defer cleanup
until the generated workspace builds and launches.

## Generate And Build

```bash
tuist install
tuist generate --no-open
xcodebuild build \
  -workspace App.xcworkspace \
  -scheme App \
  -configuration Debug \
  -destination "platform=iOS Simulator,name=<available iPhone simulator>,OS=latest" \
  -derivedDataPath DerivedDataTuist
```

## Validate Runtime

```bash
xcrun simctl boot "<available simulator name or UDID>" 2>/dev/null || true
xcrun simctl install booted DerivedDataTuist/Build/Products/Debug-iphonesimulator/App.app
xcrun simctl launch --console-pty booted com.example.app
```

Build success is not enough; launch catches missing resources, entitlements,
bundle identifiers, embedded frameworks, and ObjC category issues.

## Common Fixes

- Add missing Apple SDK frameworks with explicit SDK dependencies.
- Move generated Swift files into sources and generated asset/resource outputs
  into resources.
- Use package resource declarations for `Bundle.module` assets.
- Match package product types to the original linker behavior.
- Preserve signing, app groups, associated domains, and hardened runtime
  settings for app and extension targets.
- Keep build scripts ordered and declare inputs/outputs where possible.

## Output

Return the migration status, files changed, unresolved parity gaps, and the
exact baseline and generated validation commands with results.
