---
name: xcode-compile-profiler
description: Profile Swift and mixed-language compile bottlenecks from timing summaries, frontend diagnostics, type-check warnings, CompileSwiftSources, and SwiftEmitModule; recommend changes only.
---

# Xcode Compile Profiler

Before invoking Apple-only binaries, confirm the execution context is macOS. From Windows or Linux, run those steps in a Mac SSH project or through an already configured remote transport; do not retry missing Apple binaries locally.

Bundled commands use `$PLUGIN_ROOT` for the plugin root. Use the host's plugin-root variable when defined; otherwise set it to the absolute path of this plugin before running a helper from the app repository.

Use when compile time, type checking, or mixed-language compilation is the bottleneck. Recommend first; do not edit source or build settings without explicit approval.

## Rules

- Start from `.build-benchmark/` artifacts or raw build timing output.
- Prefer ad hoc diagnostic flags over persistent project edits.
- Rank by expected wall-clock impact, not cumulative parallel compiler work.
- If compile work is parallelized, label improvements as "Reduces compiler workload (parallel)" unless wait time should drop.
- Separate code-level, project-level, and module-level recommendations.

## Inspect

- clean and incremental `Build Timing Summary`
- long `CompileSwiftSources`, per-file compile tasks, `SwiftEmitModule`, and `Planning Swift module`
- mixed Swift/Objective-C boundaries, bridging headers, generated Swift-to-ObjC surfaces
- diagnostics:
  - `-Xfrontend -warn-long-expression-type-checking=<ms>`
  - `-Xfrontend -warn-long-function-bodies=<ms>`
  - `-Xfrontend -debug-time-compilation`
  - `-Xfrontend -debug-time-function-bodies`
  - `-Xswiftc -driver-time-compilation`
  - `-Xfrontend -stats-output-dir <path>`

Preferred script:

```bash
python3 "$PLUGIN_ROOT/shared/build-optimization/scripts/diagnose_compilation.py" \
  --project App.xcodeproj \
  --scheme MyApp \
  --configuration Debug \
  --destination "platform=iOS Simulator,name=<latest available iPhone simulator>,OS=latest" \
  --threshold 100 \
  --output-dir .build-benchmark
```

## Checks

Look first for missing explicit types in expensive expressions, deeply chained expressions, delegates typed as `AnyObject`, oversized bridging surfaces, unqualified header imports, non-`final` classes, broad `public/open` symbols, monolithic SwiftUI `body`, and closures without helpful type annotations.

## Output

For each recommendation include evidence, file/module, expected wait-time impact or parallel-work caveat, confidence, and whether approval is needed. If evidence points to project configuration, read and hand off to `xcode-project-auditor`.

## Resources

- `references/code-compilation-checks.md`
- `../../shared/build-optimization/references/recommendation-format.md`
- `../../shared/build-optimization/references/build-optimization-sources.md`
