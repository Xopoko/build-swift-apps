---
name: xcode-build-tuner
description: Apply and re-benchmark approved Xcode build-speed fixes in build settings, script phases, Swift code, or SwiftPM graphs.
---

# Xcode Build Tuner

Before invoking Apple-only binaries, confirm the execution context is macOS. From Windows or Linux, run those steps in a Mac SSH project or through an already configured remote transport; do not retry missing Apple binaries locally.

Bundled commands use `$PLUGIN_ROOT` for the plugin root. Use the host's plugin-root variable when defined; otherwise set it to the absolute path of this plugin before running a helper from the app repository.

Implement only approved build optimization changes, verify compilation, and prove the result with the same benchmark contract.

## Rules

- Apply changes covered by the user's request or approval.
- Apply one logical fix at a time; keep edits reviewable and reversible.
- Re-benchmark after changes and report wall-clock deltas.
- If a speculative change regresses or shows no useful benefit, flag it and recommend revert when appropriate.

## Fix Types

- Build settings: `DEBUG_INFORMATION_FORMAT=dwarf` for Debug, `SWIFT_COMPILATION_MODE=singlefile`, `COMPILATION_CACHE_ENABLE_CACHING=YES`, `EAGER_LINKING=YES`, `SWIFT_USE_INTEGRATED_DRIVER=YES`, `ONLY_ACTIVE_ARCH=YES`, and cross-target setting alignment. Verify with `xcodebuild -showBuildSettings`.
- Script phases: declare inputs/outputs, add configuration guards, move long lists to `.xcfilelist`, and enable dependency analysis when possible.
- Source compilation: add types, break generic/chained expressions, mark non-subclassed classes `final`, tighten access control, extract huge SwiftUI builders, and add explicit closure return types. Read `references/fix-patterns.md` for examples.
- SwiftPM graph: split oversized modules, remove upward/circular dependencies, extract interface modules, remove unnecessary `@_exported import`, align options, and pin branch dependencies to tags or revisions. Confirm tags with `git ls-remote --tags`; verify with `xcodebuild -resolvePackageDependencies`.

## Workflow

1. Read the approved plan or user instruction.
2. Identify exact files/settings for each approved item.
3. Apply the change.
4. Run a quick build to catch compiler/linker errors.
5. Re-run the original baseline command, usually:
   ```bash
   python3 "$PLUGIN_ROOT/shared/build-optimization/scripts/benchmark_builds.py" \
     --project App.xcodeproj --scheme MyApp --configuration Debug \
     --destination "platform=iOS Simulator,name=<latest available iPhone simulator>,OS=latest" \
     --output-dir .build-benchmark
   ```
6. Compare clean, cached clean when present, and incremental medians.

## Regression Policy

- Evaluate wall-clock time first; cumulative task time is supporting evidence.
- A slower standard clean build can still be acceptable when cached clean or incremental builds improve.
- Repeat inconclusive measurements when practical. If a change shows no measurable benefit, keep it only when it has a separate, documented benefit within the user's request.
- Distinguish "outlier reduction only" from true median improvement.

## Report

Lead with plain wall-clock impact:

```text
Clean build: X.Xs (was Y.Ys) - Z.Zs faster/slower.
Incremental build: X.Xs (was Y.Ys) - Z.Zs faster/slower.
```

Include changed files, any reverted changes, and uncertainty that affects the comparison. If cumulative task time fell while elapsed time stayed the same, report both observations.

## References

- `references/fix-patterns.md`
- `../../shared/build-optimization/references/build-settings-best-practices.md`
- `../../shared/build-optimization/references/recommendation-format.md`
