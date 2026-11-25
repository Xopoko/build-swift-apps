---
name: xcode-build-strategist
description: "Coordinate end-to-end Xcode build optimization audits with recommend-first, approval-gated fixes, specialist analysis, wall-clock priorities, and re-benchmark proof."
---

# Xcode Build Strategist

Before invoking Apple-only binaries, confirm the execution context is macOS. From Windows or Linux, run those steps in a Mac SSH project or through an already configured remote transport; do not retry missing Apple binaries locally.

Bundled commands use `$PLUGIN_ROOT` (`$env:PLUGIN_ROOT` in PowerShell; same path suffix) for the plugin root. Set it once: use the host's plugin-root variable when defined (Claude Code: `PLUGIN_ROOT="$CLAUDE_PLUGIN_ROOT"`), otherwise the absolute path of this plugin's root directory.

Entry point for end-to-end Xcode build optimization. Phase 1 recommends only; Phase 2 executes only after explicit approval.

## Non-Negotiables

- Wall-clock wait time is the primary metric.
- Benchmark before changing project/source/package/script files.
- Preserve evidence in `.build-benchmark/`.
- Do not implement without explicit developer approval.
- Re-benchmark approved changes and report deltas.

## Phase 1: Analyze

1. Resolve project/workspace, scheme, configuration, destination, and pain point. If both workspace and project exist, prefer the project unless the workspace is required.
2. Run or reuse a fresh baseline:
   ```bash
   python3 "$PLUGIN_ROOT/shared/build-optimization/scripts/benchmark_builds.py" \
     --project App.xcodeproj --scheme MyApp --configuration Debug \
     --destination "platform=iOS Simulator,name=<latest available iPhone simulator>,OS=latest" \
     --output-dir .build-benchmark
   ```
   Add `--touch-file path/to/File.swift` for real incremental rebuilds.
3. Check the exit status, run counts, and spread before comparing medians. If build categories are missing, inspect the raw logs. Use the build timeline to distinguish work that delays completion from concurrent work.
4. Use the specialists that match the evidence:
   - `xcode-compile-profiler`
   - `xcode-project-auditor`
   - `swiftpm-build-inspector`
5. Present the baseline command, artifact, and prioritized findings for approval. Include the specific change, evidence, risk, and measurement that would verify each finding. If a bottleneck is uncertain, describe the missing evidence.

## Phase 2: Execute

Apply approved changes with `xcode-build-tuner` and compare the same measurements before and after.

## Prioritization

- Rank by likely wall-clock savings for the user's primary pain: clean, cached clean, incremental, or CI.
- Serial bottlenecks such as `PhaseScriptExecution`, `CompileAssetCatalog`, `CodeSign`, planning, or emit-module work can outrank individual Swift file hotspots.
- Source-level compile fixes should not outrank project/graph/config fixes unless evidence says they block wall-clock.
- Every recommendation must include expected wait-time impact, evidence, affected files/settings, and risk.

## Destination Notes

For iOS simulator benchmarks, resolve an installed iPhone/iOS pair first and prefer `OS=latest` when accepted. For macOS use `--destination "platform=macOS"`. For watchOS/tvOS use an installed simulator. If local runtime inspection fails, ask or note the fallback.

## Report

Lead with wall-clock before/after. Include baseline/post medians, absolute and percentage deltas, changes made or intentionally skipped, confidence/noise notes, and a plain warning when workload improved but wait time did not.

References:

- [Benchmark artifacts](../../shared/build-optimization/references/benchmark-artifacts.md)
- [Recommendations](../../shared/build-optimization/references/recommendation-format.md)
