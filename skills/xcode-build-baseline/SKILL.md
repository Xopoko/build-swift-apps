---
name: xcode-build-baseline
description: Benchmark Xcode clean, cached-clean, zero-change, and incremental builds with repeatable inputs, timing summaries, and `.build-benchmark/` artifacts.
---

# Xcode Build Baseline

Measure before recommending build-time changes. Do not edit project files while benchmarking.

## Rules

- Keep workspace/project, scheme, configuration, destination, DerivedData path, and warm-up rules consistent.
- Capture clean and incremental behavior separately.
- Write timestamped JSON artifacts under `.build-benchmark/`.
- Report medians and spread, not only the fastest run.
- For iOS Simulator, resolve an installed iPhone/iOS pair; prefer `OS=latest` only when Xcode accepts it.
- In git worktrees, create missing package `exclude:` directories such as `__Snapshots__` before dependency resolution, or SPM can crash.

## Inputs

Infer or ask for workspace/project, scheme, configuration, destination, simulator/device preference, custom DerivedData needs, and a representative Swift file for incremental touch tests.

## Default Run

1. Normalize the build command and record every cache-affecting flag.
2. Warm up once only if needed to prove the command succeeds.
3. Run 3 clean builds.
4. If `COMPILATION_CACHE_ENABLE_CACHING = YES`, run 3 cached-clean builds; use `--no-cached-clean` only when intentionally skipped.
5. Run 3 zero-change builds with no `--touch-file`; this measures fixed overhead from dependency planning, scripts, codesign, validation, and related phases.
6. Optionally run 3 incremental builds with `--touch-file path/to/SomeFile.swift`.
7. Preserve raw logs, summaries, and JSON artifacts.

Preferred helper:

```bash
python3 ../../shared/build-optimization/scripts/benchmark_builds.py \
  --workspace App.xcworkspace \
  --scheme MyApp \
  --configuration Debug \
  --destination "platform=iOS Simulator,name=<latest available iPhone simulator>,OS=latest" \
  --output-dir .build-benchmark
```

If the helper is unavailable, run equivalent `xcodebuild` commands with `-showBuildTimingSummary` and keep raw output.

## Output

Return clean, cached-clean when enabled, zero-change, and touched-incremental medians/min/max; biggest timing categories; environment details; artifact path; and noise caveats.

If the user only requested measurement, stop there. For optimization, hand the artifact to the relevant skill: `xcode-compile-profiler`, `xcode-project-auditor`, `swiftpm-build-inspector`, or `xcode-build-strategist`.

## Resources

- `references/benchmarking-workflow.md`
- `../../shared/build-optimization/references/benchmark-artifacts.md`
- `../../shared/build-optimization/schemas/build-benchmark.schema.json`
