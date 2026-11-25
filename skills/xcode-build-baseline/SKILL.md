---
name: xcode-build-baseline
description: Benchmark Xcode clean, cached-clean, zero-change, and incremental builds with fixed inputs, timing summaries, and `.build-benchmark/` artifacts.
---

# Xcode Build Baseline

Before invoking Apple-only binaries, confirm the execution context is macOS. From Windows or Linux, run those steps in a Mac SSH project or through an already configured remote transport; do not retry missing Apple binaries locally.

Bundled commands use `$PLUGIN_ROOT` for the plugin root. Use the host's plugin-root variable when defined; otherwise set it to the absolute path of this plugin before running a helper from the app repository.

Measure before recommending build-time changes. Do not edit project files while benchmarking.

## Rules

- Keep workspace/project, scheme, configuration, destination, DerivedData path, and warm-up rules consistent.
- Keep the Xcode version fixed. Set `DEVELOPER_DIR` for the benchmark process when the project needs a different Xcode installation.
- Capture clean and incremental behavior separately.
- Write timestamped JSON artifacts under `.build-benchmark/`.
- Report medians and spread, not only the fastest run.
- For iOS Simulator, resolve an installed iPhone/iOS pair; prefer `OS=latest` only when Xcode accepts it.

## Inputs

Infer or ask for workspace/project, scheme, configuration, destination, simulator/device preference, custom DerivedData needs, and a representative Swift file for incremental touch tests.

## Default Run

1. Normalize the build command and record every cache-affecting flag.
2. Run one untimed validation build, or use `--skip-warmup` if validation is already complete.
3. Run 3 clean builds.
4. Run 3 zero-change builds, or supply `--touch-file path/to/SomeFile.swift` to measure rebuilds after touching a source file. Run the helper with each input separately if you need both results.
5. If `COMPILATION_CACHE_ENABLE_CACHING = YES` is detected, run 3 cached-clean builds using temporary DerivedData. Use `--no-cached-clean` to omit that phase.
6. Preserve raw logs and the JSON artifact.

Preferred helper:

```bash
python3 "$PLUGIN_ROOT/shared/build-optimization/scripts/benchmark_builds.py" \
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

- `../../shared/build-optimization/references/benchmark-artifacts.md`
- `../../shared/build-optimization/schemas/build-benchmark.schema.json`
