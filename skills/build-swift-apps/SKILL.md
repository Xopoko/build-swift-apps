---
name: build-swift-apps
description: Route Swift and Apple-platform work to a focused skill for iOS, macOS, SwiftUI, Xcode, Simulator, App Store Connect, Tuist, SwiftPM, signing, profiling, or research.
---

# Build Swift Apps Router

Choose the skill for the requested outcome and follow its `SKILL.md`. If the
host does not expose that skill directly, open its directory next to this one
under `skills/`.

## Execution Locus

- Run Apple toolchain commands on the Mac where the project and tools are available. From Windows or Linux, use Mac SSH or a configured remote XcodeBuildMCP transport.
- For source review, offline helpers, and API work, check the dependencies of the selected skill.

## Run, Test, and Profile

- Use `ios-simulator-browser` for a visible mirror or SwiftUI previews in Codex. Use `ios-simulator-debugger` for build, launch, logs, UI trees, or headless control, and `ios-rocketsim-operator` for RocketSim-specific controls.
- Use `macos-runtime-debugger` to build, launch, or diagnose crashes in a Mac app. Use `macos-swiftpm-runner` for package-first work and `macos-telemetry-probe` to verify logging for a specific app action.
- Use `macos-test-diagnoser` for failing macOS tests and `xcode-ui-test-stabilizer` to create or stabilize Xcode UI tests.
- Use `ios-ettrace-profiler` for iOS CPU, startup, or scrolling traces, `ios-memgraph-inspector` for leaks and retain cycles, and `swiftui-performance-inspector` for SwiftUI update costs and hangs.

## Implement UI

- Use `ios-swiftui-architect` for iOS screens and `macos-swiftui-architect` for Mac scenes, menus, and settings. For view refactors, use `swiftui-view-architect` for shared SwiftUI code and `macos-view-architect` for large Mac views.
- Use `macos-window-architect` for window identity, lifecycle, or restoration and `macos-appkit-bridge` for AppKit interoperability.
- Use `ios-intents-architect` for App Intents. For Liquid Glass, choose `ios-liquid-glass-designer` or `macos-liquid-glass-designer` by platform.

## Improve or Generate Builds

- Use `xcode-build-strategist` for end-to-end Xcode build optimization. For a specific step, use `xcode-build-baseline` to measure, `xcode-compile-profiler` for compiler hotspots, `xcode-project-auditor` for settings and build phases, or `xcode-build-tuner` to implement approved changes.
- Use `swiftpm-build-inspector` for SwiftPM graph and build overhead.
- Use `tuist-migration-planner` for conversion, `tuist-workspace-navigator` for work in a generated workspace, `tuist-generation-doctor` for generation, build, or runtime failures, and `tuist-flaky-test-stabilizer` for flaky tests.

## Distribute and Manage Releases

- Use `appstore-release-director` for an end-to-end App Store release, `appstore-release-planner` for a go/no-go decision, and `appstore-review-readiness` to validate, stage, submit, monitor, or repair review submissions.
- Use `appstore-connect-cli` for general App Store Connect CLI and API work and `appstore-ads-operator` for Apple Ads campaigns, reports, and API calls.
- Use `macos-signing-inspector` for existing signatures, entitlements, and trust failures, `macos-notarization-packager` for Developer ID packaging, `appstore-notary-runner` for `asc notarization` commands, and `appstore-signing-setup` for App Store signing assets.
- Use `appstore-archive-uploader` to archive and upload and `appstore-build-monitor` to check processing. Use `appstore-testflight-coordinator` for TestFlight testers and groups, `appstore-wall-publisher` for TestFlight Wall of Apps, and `appstore-workflow-runner` to compose and run named ASC steps.
- Use `appstore-id-resolver` to find ASC IDs, `appstore-record-creator` to create app records, `appstore-pricing-planner` for pricing and availability, and `appstore-revenuecat-sync` to reconcile ASC products with RevenueCat.
- Use `appstore-metadata-sync` to sync canonical `./metadata` JSON fields, `appstore-metadata-localizer` to translate listings, `appstore-release-notes-writer` for What's New and promotional text, and `appstore-subscription-localizer` for subscription and IAP display names.
- Use `app-icon-studio` for icons, `appstore-screenshot-pipeline` for screenshot capture, `appstore-screenshot-studio` for marketing composition, and `appstore-screenshot-validator` for screenshot checks.
- Use `appstore-aso-auditor` for listing optimization and `appstore-crash-insights` for crash and feedback evidence.

## Research

- For official Apple documentation, search Apple Developer Documentation or Xcode documentation directly. Use `apple-dev-research` only for community articles, tutorials, and write-ups.
- For firmware, dyld, Mach-O, entitlements, and private API research, use `apple-firmware-inspector`.
