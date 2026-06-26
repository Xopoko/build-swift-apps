# Build Swift Apps Skill Portfolio Audit

Date: 2026-06-26

## Scope

This audit reviews all 61 current `Build Swift Apps` skills after adding
`ios-simulator-browser` and the plugin router. It uses the local portfolio
audit, context-density audit, plugin README/AGENTS skill catalog, and the
public Agent Skills best practices page as inputs.

## External Best-Practice Input

The Agent Skills best-practices page emphasizes real execution traces,
context-efficient hot paths, coherent units, progressive disclosure, and adding
the domain-specific details an agent would not already know. Applied here, that
means:

- do not collapse adjacent skills only because they share words like
  `simulator`, `SwiftUI`, or `App Store`;
- prefer a router when the first-hop choice is ambiguous but downstream
  workflows have different tools or proof artifacts;
- move bulky rarely used detail into references or scripts instead of growing
  hot `SKILL.md` files;
- refine metadata and routing after real misfires.

Source: https://agentskills.io/skill-creation/best-practices

## Measurements

- Skills: 61 after `ios-simulator-browser` and the plugin router.
- Skill tokens: 38,877 after review-readiness, metadata-sync, metadata-localizer, notary-runner, pricing-planner, subscription-localizer, and screenshot-validator script/reference extraction.
- Average skill size: 637.3 tokens.
- References discovered from skills: 85.
- Plugin-level reference files: 8.
- Skill-local scripts: 30 after review-readiness, metadata-sync, metadata-localizer, notary-runner, pricing-planner, subscription-localizer, and screenshot-validator script extraction.
- Automatic overlap threshold: no direct merge candidate triggered.
- Structural recommendation: `plugin-split-review` because the plugin has many
  skills across many name families; the plugin-named router addresses first-hop
  routing without splitting the installable plugin yet.
- Family spread: 29 name families, with the largest groups being `macos`,
  `ios`, `xcode`, `tuist`, and `appstore-*`.

## Decision Ledger

| Subject | Action | Status | Rationale | Validation |
| --- | --- | --- | --- | --- |
| `build-swift-apps` router skill | `router-review` | adopted | The plugin is large and adjacent skills compete for first-hop routing. A router preserves narrow skills while reducing misrouting. | Package validator, repository validator, token report, install visibility. |
| `ios-simulator-browser`, `ios-simulator-debugger`, `ios-rocketsim-operator` | `metadata-review` | adopted | These share the Simulator surface but have different user outcomes: browser-visible proof, XcodeBuildMCP build/log/headless control, and RocketSim-specific automation. Keep separate and route browser-first for user-visible app work. | Router probes plus package validation. |
| `ios-ettrace-profiler`, `ios-memgraph-inspector` | `keep` | adopted | Both use simulator runtime evidence, but proof artifacts and tools differ: ETTrace CPU/performance versus memgraphs/leaks. | Existing scripts and proof outputs stay isolated. |
| `xcode-build-strategist`, `xcode-build-baseline`, `xcode-compile-profiler`, `xcode-project-auditor`, `xcode-build-tuner`, `swiftpm-build-inspector` | `keep` | adopted | This is a coherent specialist suite with an orchestrator. Merge would hide approval gates and distinct evidence types. | Router points broad build-speed asks to strategist, narrow asks to specialists. |
| `ios-swiftui-architect`, `macos-swiftui-architect`, `swiftui-view-architect`, `macos-view-architect`, `swiftui-performance-inspector` | `keep` | adopted | Lexical overlap is high, but platform surfaces and task modes differ: iOS product screens, macOS scenes, platform-neutral refactor, macOS scene refactor, and runtime performance. | Router separates platform and task intent. |
| `ios-liquid-glass-designer`, `macos-liquid-glass-designer` | `keep` | adopted | Same Apple design language, but OS availability, APIs, and platform conventions differ. | Keep platform split; review only if Apple APIs converge enough to share one reference. |
| `appstore-release-director` and focused `appstore-*` skills | `router-review` | adopted through router | The release family is large but not duplicate: director is end-to-end orchestration, focused skills own CLI surfaces and proof details. | Router directs broad release asks to director and focused asks to specialists. |
| `appstore-release-planner`, `appstore-review-readiness` | `merge-review` | adopted as router/body compaction | Lexical overlap was high around readiness, validation, submit, and monitor. Kept both entrypoints for compatibility, but made `appstore-release-planner` the go/no-go decision front door and left concrete validate/stage/submit/monitor/cancel/repair commands in `appstore-review-readiness`. | Package validator, token report, and focused trigger probes. |
| `appstore-metadata-sync`, `appstore-metadata-localizer`, `appstore-release-notes-writer`, `appstore-subscription-localizer` | `metadata-review` | adopted | These all edit localized ASC text, but artifact ownership differs: canonical `./metadata` JSON, listing translation/adaptation, What's New/promotional copy, and subscription/group/IAP display names. Descriptions and top-of-body boundaries now separate the trigger surfaces. | Package validator, token report, and metadata-family trigger probes. |
| `appstore-screenshot-pipeline`, `appstore-screenshot-studio`, `appstore-screenshot-validator` | `keep` | adopted | Automation capture, marketing composition, and ASC validation/upload are separate workflows with different dependencies and artifacts. | Existing dependency profiles and scripts remain separate. |
| `macos-runtime-debugger`, `macos-swiftpm-runner`, `macos-test-diagnoser`, `macos-telemetry-probe` | `keep` | adopted | Runtime, package-first builds, tests, and telemetry are adjacent but independently triggered. | Router separates by task. |
| `macos-signing-inspector`, `macos-notarization-packager`, `appstore-notary-runner` | `metadata-review` | adopted | Signing and notarization boundaries are close. Descriptions and router text now separate existing-artifact signing/trust diagnosis, Developer ID package readiness, and concrete `asc notarization` command execution. | Package validator, token report, and signing/notarization trigger probes. |
| `tuist-migration-planner`, `tuist-workspace-navigator`, `tuist-generation-doctor`, `tuist-flaky-test-stabilizer` | `keep` | adopted | Lifecycle stages are distinct: migration, daily navigation, failure triage, and flaky-test stabilization. | Router separates stage and symptom. |
| `appstore-review-readiness` command plan | `script-extract` | adopted | Repeated ASC validate/submit/monitor command planning is now handled by a deterministic dry-run helper. The hot skill keeps the routing and safety rules. | `review_readiness_plan.py` direct CLI checks plus package validation. |
| `appstore-review-readiness` detailed commands | `reference-extract` | adopted | Repair, submit, multi-item submission, monitor, and retry commands moved out of the hot skill and into a plugin reference. | Portfolio audit no longer flags this skill for `reference-extract`. |
| `appstore-metadata-sync` command plan and detailed commands | `script-extract` / `reference-extract` | adopted | Canonical pull/validate/dry-run push, keyword, `.strings`, and fastlane command planning is now handled by a deterministic helper, with detailed command examples moved to a plugin reference. | `metadata_sync_plan.py` direct CLI checks plus portfolio audit. |
| `appstore-metadata-localizer` field-limit lint and detailed commands | `script-extract` / `reference-extract` | adopted | App Store localization field limits for `.strings` and metadata JSON are now checked by a deterministic helper, with locale lists, ASC commands, and translation rules moved to a plugin reference. | `metadata_localization_lint.py` direct CLI checks plus portfolio audit. |
| `appstore-notary-runner` command plan and detailed commands | `script-extract` / `reference-extract` | adopted | Developer ID notarization archive/export/package/submit/status/staple planning is now handled by a deterministic helper, with detailed commands moved to a plugin reference. | `notary_plan.py` direct CLI checks plus portfolio audit. |
| `appstore-pricing-planner` command plan and detailed commands | `script-extract` / `reference-extract` | adopted | Subscription and IAP setup, inspection, CSV dry-run/apply, manual overrides, availability, and schedules now route through a deterministic helper, with detailed commands moved to a plugin reference. | `pricing_plan.py` direct CLI checks plus portfolio audit. |
| `appstore-subscription-localizer` command plan and detailed commands | `script-extract` / `reference-extract` | adopted | Subscription group, subscription, and IAP localization resolve/list/create/update planning is now handled by a deterministic helper, with supported locales and detailed commands moved to a plugin reference. | `subscription_localization_plan.py` direct CLI checks plus portfolio audit. |
| `appstore-screenshot-validator` local audit and detailed commands | `script-extract` / `reference-extract` | adopted | PNG/JPEG size, alpha, and hidden-space checks are now handled by a deterministic local helper, with `asc`/`sips` commands moved to a plugin reference. | `screenshot_audit.py` direct CLI checks plus portfolio audit. |
| `apple-firmware-inspector` command examples | `script-extract` | deferred | The skill is a research command palette over `ipsw` with six dedicated reference files already linked. A generic planner would mostly echo commands and risk encouraging stale device/build assumptions; extract only after real traces show repeated safe parameters. | Portfolio audit notes code fences, but current references are the right progressive-disclosure surface. |
| `macos-window-architect` SwiftUI examples | `script-extract` | rejected | The code fences are SwiftUI design patterns, not deterministic shell procedures. A script would add noise and could not validate scene/window intent without project context. | Keep examples in hot path because they are the core API guidance for this skill. |

## Adopted Architecture

The immediate change is a plugin-named router skill: `build-swift-apps`. It
does not replace narrow skills. It makes the first-hop decision explicit and
records that `ios-simulator-browser` is preferred for user-visible Simulator
proof while `ios-simulator-debugger` stays focused on build/run/log/headless
work.

## Deferred Work Queue

1. Add a focused App Store release-family router only if real traces show the
   plugin-level router is still too broad.
2. Extract additional command sequences only after real traces show repeated,
   safe parameters. `appstore-review-readiness`,
   `appstore-metadata-sync`, `appstore-metadata-localizer`,
   `appstore-notary-runner`,
   `appstore-pricing-planner`, `appstore-subscription-localizer`, and
   `appstore-screenshot-validator` now have deterministic helpers. The current
   `apple-firmware-inspector` and `macos-window-architect` script-extract
   recommendations are not actionable without evidence from real runs.

## Preserved Invariants

- Public-safe, generic wording.
- No private project names, credentials, or machine-specific assumptions.
- Existing skill directories remain installed and backwards-compatible.
- The new router avoids deleting or renaming any skill.
- Validation remains the repository source of truth before cache refresh.
