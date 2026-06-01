---
name: xcode-build-tuner
description: Apply approved Xcode build optimization changes and re-benchmark. Use after `xcode-build-strategist` approval, or for explicit build-setting, script-phase, Swift compilation, or SwiftPM graph fixes.
---

# Xcode Build Tuner

Implement only approved build optimization changes, verify compilation, and prove the result with the same benchmark contract.

## Rules

- Require either checked items in `.build-benchmark/optimization-plan.md` or an explicit user instruction.
- Apply one logical fix at a time; keep edits reviewable and reversible.
- Re-benchmark after changes and report wall-clock deltas.
- If a speculative change regresses or shows no useful benefit, flag it and recommend revert when appropriate.
- Do not revert recommended build settings only because one noisy benchmark failed to improve.

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
   python3 ../../shared/build-optimization/scripts/benchmark_builds.py \
     --project App.xcodeproj --scheme MyApp --configuration Debug \
     --destination "platform=iOS Simulator,name=<latest available iPhone simulator>,OS=latest" \
     --output-dir .build-benchmark
   ```
6. Compare clean, cached clean when present, and incremental medians.

## Regression Policy

- Evaluate wall-clock time first; cumulative task time is supporting evidence.
- A slower standard clean build can still be acceptable when cached clean or incremental builds improve.
- Keep best-practice settings even without immediate measurable improvement; they align with current Xcode direction and may compound later.
- For speculative source/script/graph changes, recommend revert if all measured build types regress or if there is no median/cached/incremental benefit.
- Distinguish "outlier reduction only" from true median improvement.

## Report

Lead with plain wall-clock impact:

```text
Clean build: X.Xs (was Y.Ys) - Z.Zs faster/slower.
Incremental build: X.Xs (was Y.Ys) - Z.Zs faster/slower.
```

Then include files changed, status per fix (`Kept`, `Kept (best practice)`, `Reverted`, `Blocked`, `No improvement`), confidence/noise notes, and any deviation from the approved plan. If task work decreased but wall-clock did not, say that parallel Xcode work hid the improvement.

## References

- `references/fix-patterns.md`
- `../../shared/build-optimization/references/build-settings-best-practices.md`
- `../../shared/build-optimization/references/recommendation-format.md`
