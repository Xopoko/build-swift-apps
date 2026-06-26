---
name: build-swift-apps
description: Route broad or ambiguous Swift and Apple-platform work across the Build Swift Apps skill pack. Use before choosing among adjacent iOS, macOS, SwiftUI, Xcode, simulator, App Store Connect, Tuist, SwiftPM, signing, profiling, or Apple research skills.
---

# Build Swift Apps Router

Use this as the first hop when a request could match more than one Build Swift Apps skill. Do not complete domain work from this router alone; choose the narrow skill, read it, then act.

## Routing Rules

- If the user should see, inspect, or interact with a running iOS app, prefer `ios-simulator-browser`; use `ios-simulator-debugger` first only to build/run, pick a Simulator UDID, inspect UI trees, logs, bundle IDs, or handle headless automation.
- Use `ios-rocketsim-operator` only when RocketSim-specific UI automation, visible accessibility state, or its bundled CLI is required.
- Use `ios-ettrace-profiler` for CPU/startup/scrolling/runtime performance traces; use `ios-memgraph-inspector` for leaks, retain cycles, and before/after memory proof.
- For iOS SwiftUI implementation, use `ios-swiftui-architect`; for macOS SwiftUI scenes/windows/menus/settings, use `macos-swiftui-architect`; for platform-neutral SwiftUI refactors, use `swiftui-view-architect`; for runtime performance review, use `swiftui-performance-inspector`.
- For Xcode build speed, start with `xcode-build-strategist` unless the user explicitly asks only for a baseline, compile hotspot analysis, project settings audit, or approved tuning. Then route to `xcode-build-baseline`, `xcode-compile-profiler`, `xcode-project-auditor`, or `xcode-build-tuner`.
- For App Store release work, use `appstore-release-director` for end-to-end publishing, `appstore-release-planner` for go/no-go readiness planning, and `appstore-review-readiness` for concrete validate/stage/submit/monitor/cancel/repair commands. Use other focused `appstore-*` skills for command discovery, ID resolution, archive/upload, build monitoring, TestFlight, metadata, screenshots, signing, pricing, subscriptions, crash feedback, or workflow automation.
- For App Store text and localization, use `appstore-metadata-sync` for canonical `./metadata` JSON field operations, `appstore-metadata-localizer` for translation/adaptation across listing locales, `appstore-release-notes-writer` for What's New or promotional text, and `appstore-subscription-localizer` for subscription/group/IAP display names.
- For macOS signing and distribution, use `macos-signing-inspector` for existing-artifact signing/entitlement/Gatekeeper diagnosis, `macos-notarization-packager` for Developer ID package readiness, and `appstore-notary-runner` for concrete `asc notarization` submit/status/log/staple command execution.
- For Tuist, use `tuist-migration-planner` for conversion, `tuist-workspace-navigator` for normal generated workspace work, `tuist-generation-doctor` for generation/build/runtime failures, and `tuist-flaky-test-stabilizer` for flaky test evidence and fixes.
- For package graph or SwiftPM overhead, use `swiftpm-build-inspector`; for package-first macOS build/run/test work, use `macos-swiftpm-runner`.
- For Apple documentation or community source discovery, use `apple-dev-research`; for firmware, dyld, Mach-O, entitlements, or private API research, use `apple-firmware-inspector`.

## Portfolio Boundary

Do not merge skills just because they share a platform word. Keep separate skills when triggers, tools, proof artifacts, or safety boundaries differ. Prefer this router plus focused skills until a decision ledger proves a merge preserves trigger coverage and validation.
