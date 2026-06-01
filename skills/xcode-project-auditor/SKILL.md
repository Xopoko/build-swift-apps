---
name: xcode-project-auditor
description: Audit Xcode project configuration, schemes, build settings, target dependencies, run scripts, module maps, explicit modules, and fixed build overhead with approval gates.
---

# Xcode Project Auditor

Use for project- and target-level build inefficiencies. Recommend first and require explicit approval before changing projects, schemes, or build settings.

## Review

- scheme build order and target dependencies
- Debug vs Release performance settings from `../../shared/build-optimization/references/build-settings-best-practices.md`
- run script inputs/outputs, `.xcfilelist`, dependency analysis, and timestamp-changing tools
- DerivedData churn, custom steps, fixed no-op rebuild overhead, codesign, validation, CopySwiftLibs
- parallelization opportunities, explicit module settings, module maps, `DEFINES_MODULE`, and self-contained headers
- `Planning Swift module`, asset catalog compilation, and `ExtractAppIntentsMetadata` timing
- CocoaPods presence: if `Podfile` or `Pods.xcodeproj` exists, recommend SPM migration and avoid CocoaPods-specific optimization
- Xcode 16.4+ Task Backtraces for tasks that rerun unexpectedly

## Required Checklist

Every audit includes a build settings checklist for Debug and Release using `[x]`/`[ ]`. Scope is build performance only; do not flag language-migration settings such as `SWIFT_STRICT_CONCURRENCY` or `SWIFT_UPCOMING_FEATURE_*`.

Apple-aligned checks: accurate target dependencies, schemes in Dependency Order, scripts with declared inputs/outputs, `.xcfilelist` for many files, consistent explicit module settings, and module-map readiness.

## Typical Wins

Skip debug-time scripts that only matter in release, add script guards and dependency metadata, remove accidental serial bottlenecks, align settings that create extra module variants, stop formatters/linters from touching unchanged files, split huge asset catalogs into resource bundles, and use Task Backtraces to find the input that triggers invalidation.

## Output

For each issue include evidence, scope, whether it affects clean/incremental/both, estimated impact, and approval requirement. If evidence points to package graph or build plugins, read and hand off to `swiftpm-build-inspector`.

## Resources

- `references/project-audit-checks.md`
- `../../shared/build-optimization/references/build-settings-best-practices.md`
- `../../shared/build-optimization/references/recommendation-format.md`
- `../../shared/build-optimization/references/build-optimization-sources.md`
