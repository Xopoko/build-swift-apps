# Xcode Build Benchmark Artifacts

Use the same project/workspace, scheme, configuration, destination, Xcode version, and build inputs for before/after measurements. Record the benchmark command, including any `DEVELOPER_DIR` override and extra arguments.

The benchmark helper records three phases in a JSON artifact with adjacent raw logs:

- `clean` runs `xcodebuild clean` before each timed build. This clears build products. The compilation cache may still be warm.
- `incremental` starts from the last successful clean build. In this array, `build_type: "zero-change"` measures a rebuild without source edits, and `"incremental"` measures a rebuild after touching the file supplied with `--touch-file`. Run the helper with each input separately when comparing both workflows.
- `cached_clean` uses temporary DerivedData and a separate temporary compilation cache when resolved settings report caching enabled. The helper warms that cache with an untimed build, then clears its DerivedData before each timed run. Inspect cache-hit messages to establish how much was reused. Pass `--no-cached-clean` to omit this phase.

Check the return status and run counts before using an artifact. Failures exit nonzero, and recorded runs and logs can still explain what happened. A phase with zero successful runs has no meaningful median. Compare wall-clock medians and spread across equivalent phases.

The `timing_summary_categories` represent cumulative task times from Xcode's Build Timing Summary. Xcode runs tasks in parallel. Use the build timeline when you need to know which tasks delayed completion.

See the [JSON schema](../schemas/build-benchmark.schema.json).
