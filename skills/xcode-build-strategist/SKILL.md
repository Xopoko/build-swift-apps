---
name: xcode-build-strategist
description: "Recommend-first Xcode build optimization: benchmark, run specialist analyses, prioritize wall-clock findings, request approval, delegate fixes, and re-benchmark. Use for speeding up Xcode builds or full build audits."
---

# Xcode Build Strategist

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
   python3 ../../shared/build-optimization/scripts/benchmark_builds.py \
     --project App.xcodeproj --scheme MyApp --configuration Debug \
     --destination "platform=iOS Simulator,name=<latest available iPhone simulator>,OS=latest" \
     --output-dir .build-benchmark
   ```
   Add `--touch-file path/to/File.swift` for real incremental rebuilds.
3. Verify artifact quality: non-empty `timing_summary_categories`; `cached_clean` runs when `COMPILATION_CACHE_ENABLE_CACHING=YES`; variance noted when max-min exceeds 20% of median.
4. If incremental builds are the pain and Xcode 16.4+ is available, recommend Task Backtraces and include any evidence.
5. Decide whether compile work is on the critical path. If category totals are 2x+ wall-clock median, many fixes reduce CPU work but not wait time.
6. Run relevant specialists:
   - `xcode-compile-profiler`
   - `xcode-project-auditor`
   - `swiftpm-build-inspector`
7. Generate `.build-benchmark/optimization-plan.md`:
   ```bash
   python3 "$PLUGIN_ROOT/skills/xcode-build-strategist/scripts/generate_optimization_report.py" \
     --benchmark .build-benchmark/<artifact>.json \
     --project-path App.xcodeproj \
     --diagnostics .build-benchmark/<diagnostics>.json \
     --output .build-benchmark/optimization-plan.md
   ```
8. Stop and ask the developer to approve checklist items.

## Phase 2: Execute

After approval, read checked items from `.build-benchmark/optimization-plan.md`, delegate to `xcode-build-tuner`, append verification medians/deltas to the plan, and report before/after results.

## Prioritization

- Rank by likely wall-clock savings for the user's primary pain: clean, cached clean, incremental, or CI.
- Serial bottlenecks such as `PhaseScriptExecution`, `CompileAssetCatalog`, `CodeSign`, planning, or emit-module work can outrank individual Swift file hotspots.
- Source-level compile fixes should not outrank project/graph/config fixes unless evidence says they block wall-clock.
- Every recommendation must include expected wait-time impact, evidence, affected files/settings, and risk.

Use these impact phrases:

- "Expected to reduce your [clean/incremental] build by approximately X seconds."
- "Reduces parallel compile work but is unlikely to reduce build wait time because other tasks take equally long."
- "Impact on wait time is uncertain; re-benchmark after applying."
- "No wait-time improvement expected. The benefit is [deterministic builds/faster branch switching/reduced CI cost]."
- For `COMPILATION_CACHE_ENABLE_CACHING`: "Measured 5-14% faster clean builds across tested projects; benefits compound with persistent DerivedData."

## Destination Notes

For iOS simulator benchmarks, resolve an installed iPhone/iOS pair first and prefer `OS=latest` when accepted. For macOS use `--destination "platform=macOS"`. For watchOS/tvOS use an installed simulator. If local runtime inspection fails, ask or note the fallback.

## Report

Lead with wall-clock before/after. Include baseline/post medians, absolute and percentage deltas, changes made or intentionally skipped, confidence/noise notes, and a plain warning when workload improved but wait time did not.

References: `references/orchestration-report-template.md`, `../../shared/build-optimization/references/benchmark-artifacts.md`, `recommendation-format.md`, and `build-settings-best-practices.md`.
