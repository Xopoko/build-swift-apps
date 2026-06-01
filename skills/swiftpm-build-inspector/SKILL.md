---
name: swiftpm-build-inspector
description: Analyze Swift Package Manager dependencies, plugins, module variants, branch pins, package graph shape, macros, binary targets, and CI/local build overhead that slow Xcode builds.
---

# SwiftPM Build Inspector

Gather evidence before recommending package changes. Do not edit manifests/dependencies without explicit approval.

## Inspect

- `Package.swift`, `Package.resolved`
- local vs remote packages
- build-tool/package plugins
- binary targets
- dependency layering, imports, cycles, oversized modules
- timing summaries/logs showing package work

Before recommending a local package, prove it is in the project graph: check `XCLocalSwiftPackageReference` and `XCSwiftPackageProductDependency` in `project.pbxproj`. Ignore on-disk packages that are not linked.

For branch-pinned dependencies:

```bash
python3 scripts/check_spm_pins.py --project App.xcodeproj
```

If tags exist, recommend tag pins when appropriate; otherwise recommend a revision hash for determinism. Distinguish intentional branch tracking from missing-tag upstreams.

## Focus Areas

- graph shape and downstream rebuild scope
- plugin overhead in local/CI builds
- clean-environment checkout/fetch cost
- config drift causing duplicate module variants
- dependency direction violations and cycles; extract shared contracts into protocol/interface modules
- oversized modules (~200+ files)
- umbrella modules with `@_exported import`
- test targets depending on the app target instead of the module under test
- Swift macro or `swift-syntax` cascades
- multi-platform build multiplication (iOS/watchOS/tvOS/macOS variants)

Modular SDK migrations do not automatically speed builds. Compare `SwiftCompile`, `SwiftEmitModule`, and `ScanDependencies` task counts and benchmark before recommending for performance; note when the benefit is import hygiene/API surface rather than wait time.

If the same module appears multiple times in timing output, investigate option/variant drift before source shaving.

## Report

For each finding include evidence, affected package/plugin, clean vs incremental impact, CI impact, estimated wait-time impact, and approval requirement. If the bottleneck is not package-related, hand off to `xcode-project-auditor` or `xcode-compile-profiler`.

References: `references/spm-analysis-checks.md`, `../../shared/build-optimization/references/recommendation-format.md`, `build-optimization-sources.md`.
