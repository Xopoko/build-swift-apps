

<p align="center">
  <img src="assets/icon.png" width="128" alt="Build Swift Apps logo">
</p>

<h1 align="center">Build Swift Apps</h1>

<p align="center">
  Build, debug, profile, test, refactor, and release Swift apps across iOS and macOS.
</p>

<p align="center">
  <b>Codex</b> · <b>Claude Code</b> · <b>Cursor</b> · <b>pi</b> · <b>Manual skill installs</b>
</p>

The pack covers iOS Simulator, SwiftUI and AppKit, Xcode and SwiftPM builds,
Tuist projects, and release workflows for iOS and macOS.

## Quick Start

### Easiest: Ask Your Agent

For most users, the simplest install path is to paste this prompt into the
coding agent they already use:

```text
Install the Build Swift Apps plugin from https://github.com/Xopoko/build-swift-apps on this computer. Follow the repository installation instructions for the agent you are running in, install required dependencies, ask before installing optional tools, run the doctor checks, and report what was installed.
```

### Codex

```bash
mkdir -p "$HOME/.agents/plugins/plugins"
git clone https://github.com/Xopoko/build-swift-apps.git \
  "$HOME/.agents/plugins/plugins/build-swift-apps"
cd "$HOME/.agents/plugins/plugins/build-swift-apps"

./scripts/install-local-plugin.sh
./scripts/doctor.sh --profile core --profile mcp
```

Then start a new Codex thread and ask for a focused workflow:

> Use the iOS debugger skill to build and run this app on a simulator, inspect the first screen, and summarize any runtime failures.

### Claude Code

```text
/plugin marketplace add Xopoko/build-swift-apps
/plugin install build-swift-apps@build-swift-apps
/reload-plugins
```

If you use the `appstore-screenshot-studio` skill in Claude Code, install its local Node helper
dependency after the plugin is installed:

```bash
cd "$HOME/.claude/plugins/marketplaces/build-swift-apps"
./scripts/install-deps.sh --profile screenshots --yes
```

Claude Code namespaces plugin skills, so invoke them as
`/build-swift-apps:<skill-name>` when calling skills explicitly.

See the [installation guide](docs/INSTALL.md) for Cursor, pi, manual installs,
and optional dependencies.

## Included Skills

### Build, Run, Debug, And Test

| Skill | Purpose |
| --- | --- |
| `build-swift-apps` | Route broad or ambiguous Swift and Apple-platform work to the right focused skill. |
| `macos-runtime-debugger` | Build, launch, log, and debug local macOS apps and desktop executables. |
| `macos-swiftpm-runner` | Build, run, and test SwiftPM-first macOS packages and command-line tools. |
| `macos-test-diagnoser` | Triage failing Xcode or SwiftPM test runs and separate real regressions from setup issues. |
| `xcode-ui-test-stabilizer` | Create, stabilize, and run Xcode UI tests with focused failure evidence. |
| `macos-telemetry-probe` | Add lightweight `Logger` instrumentation and verify events through runtime logs. |

### iOS Simulator, Profiling, And Runtime Evidence

| Skill | Purpose |
| --- | --- |
| `ios-simulator-browser` | Preferred user-facing Simulator surface: mirror an iOS app into the Codex browser and render SwiftUI package previews with hot reload. |
| `ios-simulator-debugger` | Use XcodeBuildMCP to build, run, inspect, and debug iOS simulator apps; hand off to `ios-simulator-browser` for visible proof. |
| `ios-rocketsim-operator` | Use RocketSim's bundled agent skill and CLI for visible simulator UI interaction. |
| `ios-ettrace-profiler` | Capture and interpret symbolicated ETTrace profiles for iOS simulator flows. |
| `ios-memgraph-inspector` | Capture, inspect, and compare simulator memory graphs with `leaks` evidence. |
| `swiftui-performance-inspector` | Audit SwiftUI performance from code structure before asking for profiling evidence. |

### SwiftUI, AppKit, And Product UI

| Skill | Purpose |
| --- | --- |
| `ios-swiftui-architect` | Build iOS SwiftUI screens with navigation, layout, state, forms, sheets, and media patterns. |
| `macos-swiftui-architect` | Build macOS SwiftUI scenes, commands, toolbars, settings, split views, and menu bar extras. |
| `swiftui-view-architect` | Refactor SwiftUI views into stable, testable, dependency-explicit components. |
| `macos-view-architect` | Refactor macOS SwiftUI scenes and sidebar/detail structures. |
| `macos-appkit-bridge` | Bridge SwiftUI to AppKit only where native macOS behavior needs it. |
| `macos-window-architect` | Tune macOS 15+ SwiftUI windows, placement, restoration, and scene behavior. |
| `ios-intents-architect` | Design App Intents, entities, queries, and shortcuts for Siri, Spotlight, widgets, and controls. |
| `macos-liquid-glass-designer` | Adopt modern macOS SwiftUI design and Liquid Glass conventions. |
| `ios-liquid-glass-designer` | Implement and review iOS 26+ Liquid Glass SwiftUI features. |

### Xcode Build Performance

| Skill | Purpose |
| --- | --- |
| `xcode-build-strategist` | End-to-end recommend-first build optimization: benchmark, analyze, prioritize, approve, fix, verify. |
| `xcode-build-baseline` | Produce repeatable clean and incremental Xcode build baselines with artifacts. |
| `xcode-compile-profiler` | Find Swift compile and type-checking hotspots with compiler diagnostics. |
| `xcode-project-auditor` | Audit build settings, schemes, target dependencies, and script phases. |
| `swiftpm-build-inspector` | Analyze Swift Package Manager graph shape, plugins, pins, and module variants. |
| `xcode-build-tuner` | Apply approved build optimizations and re-benchmark to prove impact. |

### Release, Signing, And Distribution

| Skill | Purpose |
| --- | --- |
| `macos-signing-inspector` | Diagnose existing macOS app signing, entitlements, sandboxing, hardened runtime, Gatekeeper, and trust-policy issues. |
| `macos-notarization-packager` | Prepare or diagnose Developer ID distribution artifacts, bundle structure, and notarization readiness. |
| `appstore-release-director` | Orchestrate an end-to-end iOS App Store release from local repo state through App Store Connect review readiness. |
| `app-icon-studio` | Create, evaluate, export, and install iOS AppIcon asset catalogs or macOS .icns bundle icons. |
| `appstore-screenshot-studio` | Generate, revise, translate, scrape, and crop App Store marketing screenshot panels. |

### App Store Connect (`asc` CLI)

These skills use the public `asc` command from
[`rorkai/App-Store-Connect-CLI`](https://github.com/rorkai/App-Store-Connect-CLI).
They cover auth and command discovery, ID resolution, Xcode archive/export,
TestFlight, submission readiness, metadata and localization, screenshots,
signing, notarization, subscriptions/IAP pricing, crash triage, Apple Ads, and
workflow automation.

Skills: `appstore-connect-cli`, `appstore-id-resolver`, `appstore-archive-uploader`,
`appstore-build-monitor`, `appstore-testflight-coordinator`, `appstore-release-planner`,
`appstore-review-readiness`, `appstore-metadata-sync`, `appstore-metadata-localizer`,
`appstore-release-notes-writer`, `appstore-aso-auditor`, `appstore-screenshot-validator`,
`appstore-screenshot-pipeline`, `appstore-signing-setup`, `appstore-notary-runner`,
`appstore-record-creator`, `appstore-ads-operator`, `appstore-pricing-planner`,
`appstore-subscription-localizer`, `appstore-revenuecat-sync`,
`appstore-crash-insights`, `appstore-workflow-runner`, `appstore-wall-publisher`.

### Tuist And Generated Projects

| Skill | Purpose |
| --- | --- |
| `tuist-migration-planner` | Move an existing Xcode project toward a Tuist-generated workspace. |
| `tuist-workspace-navigator` | Work effectively in Tuist-generated Xcode workspaces. |
| `tuist-generation-doctor` | Reproduce and triage generation or post-generation build failures. |
| `tuist-flaky-test-stabilizer` | Use Tuist test insights to investigate and fix flaky test cases. |

### Research And Low-Level Apple Work

| Skill | Purpose |
| --- | --- |
| `apple-dev-research` | Search Apple Dev Search for Swift, SwiftUI, Xcode, iOS, and macOS community writing. |
| `apple-firmware-inspector` | Use the `ipsw` CLI for Apple firmware, dyld shared cache, Mach-O, entitlements, and private API research. |

## Multi-Agent Packaging

The same repository is packaged for several agent ecosystems:

| Agent/tool | Files | Notes |
| --- | --- | --- |
| Codex | `.codex-plugin/plugin.json`, `.mcp.json`, `agents/openai.yaml`, `skills/*/agents/openai.yaml` | Native Codex plugin metadata, MCP server definitions, and OpenAI agent manifests. |
| Claude Code | `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json` | Claude Code plugin and marketplace metadata. Skills live at the plugin root, not inside `.claude-plugin/`. |
| Cursor | `.cursor-plugin/plugin.json` | Cursor plugin metadata with the same skill directory list. |
| pi | `package.json` | `pi.skills` points at every packaged skill. |
| Generic agents | `AGENTS.md` | Repository-level instructions for agents that support the open `AGENTS.md` convention. |

## Host Dependencies

Run the doctor profile for the tools you plan to use. The [installation guide](docs/INSTALL.md#dependency-profiles)
lists what each profile checks and installs.

## Repository Layout

```text
.
├── .codex-plugin/        # Codex plugin manifest
├── .claude-plugin/       # Claude Code plugin and marketplace manifests
├── .cursor-plugin/       # Cursor plugin manifest
├── .mcp.json             # Bundled MCP server definitions
├── agents/               # OpenAI/Codex agent metadata
├── assets/               # Plugin icon assets
├── commands/             # Short command entrypoints
├── docs/                 # Installation and operational documentation
├── NOTICE                # Required copyright and permission notices
├── scripts/              # Install, dependency, doctor, and validation helpers
├── shared/               # Shared scripts, references, schemas, and support docs
└── skills/               # Installable Agent Skills, one directory per workflow
```

## Validation

```bash
./scripts/validate-package.sh
./scripts/doctor.sh --profile core --profile mcp --strict
```

`validate-package.sh` checks JSON manifests, script syntax, skill frontmatter,
multi-agent manifest coverage, and accidental private/work-specific terms.

## License

MIT. See [LICENSE](LICENSE). Additional required notices are preserved in
[NOTICE](NOTICE).
