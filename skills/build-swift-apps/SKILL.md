---
name: build-swift-apps
description: Route broad or ambiguous Swift and Apple-platform work to a focused skill; this router does not implement domain work. Covers iOS, macOS, SwiftUI, Xcode, Simulator, App Store Connect, Tuist, SwiftPM, signing, profiling, and Apple research.
---

# Build Swift Apps Router

Use this as the first hop when a request could match more than one Build Swift Apps skill. Do not complete domain work from this router alone; choose the narrow skill, read it, then act.

## Execution Locus

- Determine the execution host and project location before invoking tools. Run Xcode, Apple Simulator, Apple-target SwiftPM builds, Tuist, signing, notarization, and other Apple-toolchain commands on the macOS host that owns the project and toolchain.
- When the task UI is on Windows or Linux but a Mac SSH project or remote XcodeBuildMCP transport is configured, keep the local host as the control plane and execute Apple work in that remote Mac context. Do not retry missing Apple binaries locally.
- Do not impose a blanket macOS requirement on source-only review, deterministic offline helpers, or network/API workflows that explicitly support the current host; preflight their actual dependencies instead.

## Routing Rules

- If the user should see, inspect, or interact with a running iOS app, prefer `ios-simulator-browser`; use `ios-simulator-debugger` first only to build/run, pick a Simulator UDID, inspect UI trees, logs, bundle IDs, or handle headless automation.
- Use `ios-rocketsim-operator` only when RocketSim-specific UI automation, visible accessibility state, or its bundled CLI is required.
- Use `ios-ettrace-profiler` for CPU/startup/scrolling/runtime performance traces; use `ios-memgraph-inspector` for leaks, retain cycles, and before/after memory proof.
- For iOS SwiftUI implementation, use `ios-swiftui-architect`; for macOS SwiftUI scenes/windows/menus/settings, use `macos-swiftui-architect`; for platform-neutral SwiftUI refactors, use `swiftui-view-architect`; for runtime performance review, use `swiftui-performance-inspector`.
- For Xcode build speed, start with `xcode-build-strategist` unless the user explicitly asks only for a baseline, compile hotspot analysis, project settings audit, or approved tuning. Then route to `xcode-build-baseline`, `xcode-compile-profiler`, `xcode-project-auditor`, or `xcode-build-tuner`.
- For App Store release work, use `appstore-release-director` for end-to-end publishing, `appstore-release-planner` for go/no-go readiness planning, and `appstore-review-readiness` for concrete validate/stage/submit/monitor/cancel/repair commands. Use `appstore-connect-cli` for generic ASC command discovery, auth, schemas, pagination, output, and App Store Connect record/API work; use `appstore-ads-operator` for Apple Ads auth, orgs, campaigns, ad groups, creatives, keywords, reports, or Ads API calls. Use other focused `appstore-*` skills for ID resolution, archive/upload, build monitoring, TestFlight, metadata, screenshots, signing, pricing, subscriptions, crash feedback, or workflow automation.
- For App Store text and localization, use `appstore-metadata-sync` for canonical `./metadata` JSON field operations, `appstore-metadata-localizer` for translation/adaptation across listing locales, `appstore-release-notes-writer` for What's New or promotional text, and `appstore-subscription-localizer` for subscription/group/IAP display names.
- For macOS signing and distribution, use `macos-signing-inspector` for existing-artifact signing/entitlement/Gatekeeper diagnosis, `macos-notarization-packager` for Developer ID package readiness, and `appstore-notary-runner` for concrete `asc notarization` submit/status/log/staple command execution.
- For Tuist, use `tuist-migration-planner` for conversion, `tuist-workspace-navigator` for normal generated workspace work, `tuist-generation-doctor` for generation/build/runtime failures, and `tuist-flaky-test-stabilizer` for flaky test evidence and fixes.
- For package graph or SwiftPM overhead, use `swiftpm-build-inspector`; for package-first macOS build/run/test work, use `macos-swiftpm-runner`.
- For official Apple documentation, use Apple Developer Documentation or Xcode documentation search directly. Use `apple-dev-research` only for community articles, tutorials, and write-ups; for firmware, dyld, Mach-O, entitlements, or private API research, use `apple-firmware-inspector`.

## Complete Focused Route Map

- For app identity and store assets, use `app-icon-studio`, `appstore-screenshot-pipeline`, or `appstore-screenshot-studio`; validate screenshot sets with `appstore-screenshot-validator`.
- For archive and delivery state, use `appstore-archive-uploader`, `appstore-build-monitor`, `appstore-testflight-coordinator`, or `appstore-wall-publisher`; use `appstore-workflow-runner` only for a composed, reviewable workflow.
- For App Store record and commercial state, use `appstore-id-resolver`, `appstore-record-creator`, `appstore-pricing-planner`, `appstore-revenuecat-sync`, or `appstore-signing-setup`; use `appstore-aso-auditor` for listing optimization evidence and `appstore-crash-insights` for crash feedback.
- For iOS product integration, use `ios-intents-architect` for App Intents and `ios-liquid-glass-designer` for Liquid Glass design and implementation.
- For macOS UI architecture, use `macos-appkit-bridge`, `macos-view-architect`, `macos-window-architect`, or `macos-liquid-glass-designer` according to the owning layer.
- For macOS runtime evidence, use `macos-runtime-debugger`, `macos-telemetry-probe`, or `macos-test-diagnoser`; use `xcode-ui-test-stabilizer` for flaky or unstable Xcode UI tests.

## Portfolio Boundary

Do not merge skills just because they share a platform word. Keep separate skills when triggers, tools, proof artifacts, or safety boundaries differ. Prefer this router plus focused skills until a decision ledger proves a merge preserves trigger coverage and validation.
