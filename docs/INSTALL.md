# Installation

This plugin is intentionally generic: it can help with Swift apps across Apple
platforms, but many skills delegate to host tools that must exist on the
developer machine. The installer and dependency scripts keep those tools
optional, check what is already installed, and let you install only the groups
you need.

## Quick Install

The local installer itself needs `git` and `python3`. On a fresh Mac, install
Xcode Command Line Tools first if either command is missing:

```bash
xcode-select --install
```

```bash
mkdir -p "$HOME/.agents/plugins/plugins"
git clone https://github.com/Xopoko/build-swift-apps.git \
  "$HOME/.agents/plugins/plugins/build-swift-apps"
cd "$HOME/.agents/plugins/plugins/build-swift-apps"

./scripts/install-local-plugin.sh
./scripts/doctor.sh --profile core --profile mcp
```

The default installer:

- clones or updates the plugin at `~/.agents/plugins/plugins/build-swift-apps`
- writes or updates `~/.agents/plugins/marketplace.json`
- registers the local marketplace with Codex and enables
  `build-swift-apps@local` in `~/.codex/config.toml` when the `codex` CLI exists
- offers to install the default dependency profiles: `core` and `mcp`

Start a new Codex thread after installing or reinstalling the plugin so new
skills and MCP servers are loaded.

## Install From A Custom Location

Use `--plugin-dir` when you want the personal marketplace to point at a
specific managed checkout. Keep the checkout under the directory that contains
`marketplace.json`; the marketplace entry intentionally uses a relative local
path.

```bash
./scripts/install-local-plugin.sh \
  --repo-url https://github.com/Xopoko/build-swift-apps.git \
  --plugin-dir "$HOME/.agents/plugins/plugins/build-swift-apps" \
  --marketplace-file "$HOME/.agents/plugins/marketplace.json" \
  --marketplace-name local
```

If you need a repo-local or team-local marketplace, put both the marketplace
file and plugin checkout under the same root and pass both paths explicitly.
Use `--skip-codex` when you only want to update `marketplace.json`.

## Install For Other Agents

### Claude Code

This repository ships Claude Code plugin metadata in `.claude-plugin/`. The
marketplace manifest points at this repository root, while skills, commands,
MCP config, and support files stay at the plugin root.

After the repository is public or available to your GitHub account:

```text
/plugin marketplace add Xopoko/build-swift-apps
/plugin install build-swift-apps@build-swift-apps
/reload-plugins
```

Or from a terminal:

```bash
claude plugin marketplace add Xopoko/build-swift-apps
claude plugin install build-swift-apps@build-swift-apps
```

Claude stores enabled plugin versions in its own runtime cache. If you plan to
use `appstore-screenshot-studio`, run the dependency installer from the cloned marketplace checkout
after installing or updating the plugin; it will also update detected Claude and
Codex cache copies:

```bash
cd "$HOME/.claude/plugins/marketplaces/build-swift-apps"
./scripts/install-deps.sh --profile screenshots --yes
```

For local development, run Claude Code from a trusted checkout and use its
local plugin testing flow:

```bash
claude --plugin-dir .
```

Claude Code namespaces plugin skills. For example:

```text
/build-swift-apps:ios-simulator-debugger
/build-swift-apps:xcode-build-strategist
```

### Cursor

This repository ships Cursor plugin metadata in `.cursor-plugin/plugin.json`.
The manifest lists every skill under `skills/`, so the same package can be
submitted to or tested with Cursor's plugin system.

Until a marketplace listing is live, use Cursor's local plugin testing flow for
a checkout that contains `.cursor-plugin/plugin.json`, or copy the desired skill
directories into the skill location supported by your Cursor version.

### pi

The root `package.json` includes a `pi.skills` list for tools that install
Agent Skills through `pi`:

```bash
pi install https://github.com/Xopoko/build-swift-apps
```

### Manual Skill Install

Every skill is a self-contained directory under `skills/`. Agents that support
plain Agent Skills can install all skills or individual directories:

```bash
cp -R skills/* "$AGENT_SKILLS_DIR/"
```

When installing manually, also copy any referenced `shared/` files if the agent
does not preserve repository-relative paths.

## Dependency Profiles

Use `doctor.sh` to inspect the current machine without installing anything:

```bash
./scripts/doctor.sh --all
./scripts/doctor.sh --profile core --profile tuist --strict
```

Use `install-deps.sh` to install or receive manual setup instructions:

```bash
./scripts/install-deps.sh --profile core --profile mcp
./scripts/install-deps.sh --profile tuist --profile performance --dry-run
./scripts/install-deps.sh --all --skip ettrace --skip ipsw
```

Profiles:

| Profile | Covers | Install behavior |
| --- | --- | --- |
| `core` | Xcode, SwiftPM, simulator, signing, logging, Python helpers, and macOS icon export tools (`sips`, `iconutil`) | Installs `python3` and `git` with Homebrew when missing. Xcode and macOS system tools are manual. |
| `mcp` | Bundled MCP servers in `.mcp.json` and browser-preview helpers | Installs Node.js, including `node`, `npm`, and `npx`, with Homebrew when missing. |
| `github` | GitHub publishing and issue or PR workflows | Installs `gh` with Homebrew when missing. |
| `tuist` | Tuist migration, generated projects, flaky-test/debugging workflows | Installs `mise` with Homebrew when missing, then installs `tuist@latest` through `mise`. |
| `app-store` | App Store Connect, notarization, packaging, signing | Installs/checks the public `asc` CLI and checks Xcode notarization tools. |
| `screenshots` | App Store screenshot capture and generation scripts | Installs/checks AXe (`axe`) for `asc screenshots capture/run`, Node.js, and bundled `appstore-screenshot-studio` script dependencies with `npm install --prefix skills/appstore-screenshot-studio/scripts`. |
| `performance` | ETTrace and build-performance analysis | Installs `ettrace` with Homebrew when missing. Xcode tools remain manual. |
| `firmware` | Apple firmware and binary reverse engineering | Installs `ipsw` with Homebrew when missing. |
| `simulator` | RocketSim simulator interaction workflows and `serve-sim` browser mirroring | Checks for RocketSim.app, its bundled CLI, Xcode simulator tools, and Node/npx. RocketSim installation is manual through the Mac App Store or RocketSim distribution channel. |
| `all` | Every profile above | Combines all checks and install prompts. |

## Skip Or Select Tools

Every installable tool is optional. You can skip individual tools:

```bash
./scripts/install-deps.sh --all --skip gh --skip asc --skip axe --skip screenshot-deps --skip ettrace --skip ipsw
```

You can also run the plugin with partial dependencies. Skills that require a
missing tool should fail early with a clear preflight error. For example, you
can use SwiftUI refactor skills without `asc`, `axe`, `screenshot-deps`, `ipsw`, `ettrace`, or
`RocketSim`.

## Manual Setup Notes

### Xcode And Command Line Tools

Install Xcode from the Mac App Store or Apple Developer downloads, then select
the active developer directory when needed:

```bash
sudo xcode-select -s /Applications/Xcode.app/Contents/Developer
xcodebuild -version
xcrun simctl list devices available
```

If only the command line tools are needed for a machine, run:

```bash
xcode-select --install
```

Accept the Xcode license if Xcode prompts for it before builds can run.

### MCP Servers

The plugin includes MCP server definitions that use `npx`:

- `xcodebuildmcp` for simulator, UI automation, debugging, and logs
- `apple-docs` through `mcp-remote`

The first run may download npm packages. If you do not want MCP tooling on a
machine, skip the `mcp` profile and disable or ignore MCP-dependent skills.

### Tuist

Tuist-related skills use both direct `tuist` commands and `mise exec
tuist@latest -- tuist` style commands. The installer prefers `mise` so a machine
can pin or upgrade Tuist outside this plugin:

```bash
brew install mise
mise use -g tuist@latest
tuist version
```

Project-specific Tuist auth, registry, and cache configuration still belongs to
the project using Tuist.

### App Store Connect

The App Store Connect skills use the public `asc` CLI from
`rorkai/App-Store-Connect-CLI`.

Install it through the dependency installer or directly:

```bash
./scripts/install-deps.sh --profile app-store
# or:
brew install asc
asc version
```

Configure it with an App Store Connect API key:

```bash
asc auth login \
  --name "MyApp" \
  --key-id "ABC123DEFG" \
  --issuer-id "00000000-0000-0000-0000-000000000000" \
  --private-key "$HOME/AuthKey_<KEY_ID>.p8" \
  --network
```

For headless or CI machines where Keychain access is not desired:

```bash
asc auth login \
  --bypass-keychain \
  --name "CI" \
  --key-id "$ASC_KEY_ID" \
  --issuer-id "$ASC_ISSUER_ID" \
  --private-key "$ASC_PRIVATE_KEY_PATH" \
  --network
```

Notarization and packaging workflows also use Xcode-provided tools such as
`xcrun notarytool`, `xcrun stapler`, `codesign`, `spctl`, `security`, and
`plutil`.

### Store Screenshot Generation

Local capture through `asc screenshots capture` and `asc screenshots run` uses
the AXe simulator automation binary (`axe`) for iOS Simulator accessibility and
HID control. The `appstore-screenshot-studio` skill also bundles Node scripts
under `skills/appstore-screenshot-studio/scripts` for workspace scaffolding,
public App Store metadata lookup, and panel cropping. Install both through the
profile:

```bash
./scripts/install-deps.sh --profile screenshots
axe --version
```

Manual install:

```bash
brew install cameroncooke/axe/axe
npm install --prefix skills/appstore-screenshot-studio/scripts
```

Image generation is intentionally left to the active agent environment or the
project's own design pipeline. Capture uses `axe`; cropping and workspace setup
use local Node dependencies.

When runtime cache copies already exist, `install-deps.sh --profile screenshots`
also installs `sharp` into detected Codex and Claude plugin cache directories so
`<skill-dir>/scripts/*.mjs` works from the agent's actual skill path.

### ETTrace

The host runner is installable with Homebrew:

```bash
brew install emergetools/homebrew-tap/ettrace
```

Profiling an iOS simulator app also requires temporarily linking a matching
`ETTrace.xcframework` into the app target, as described in the
`ios-ettrace-profiler` skill.

### IPSW

Firmware analysis uses the `ipsw` CLI:

```bash
brew install blacktop/tap/ipsw
```

### RocketSim

The RocketSim skill requires a current RocketSim.app bundle that contains:

- `Contents/Resources/Agent-Skill/SKILL.md`
- `Contents/Helpers/rocketsim`

The doctor script checks common install paths and the currently running
RocketSim process, but installation is manual.

### Simulator Browser

The iOS Simulator browser skill uses `npx serve-sim@latest` to mirror a specific
Simulator UDID into the Codex in-app browser. SwiftUI package previews also use
the bundled Node launcher at
`skills/ios-simulator-browser/scripts/swiftui-preview-browser.mjs`, which
generates a disposable Xcode host project outside the user's source tree.

## Updating

From the plugin checkout:

```bash
git pull --ff-only
codex plugin marketplace add "$HOME"
./scripts/doctor.sh --all
```

For Claude Code:

```bash
claude plugin marketplace update build-swift-apps
claude plugin update build-swift-apps@build-swift-apps
cd "$HOME/.claude/plugins/marketplaces/build-swift-apps"
./scripts/install-deps.sh --profile screenshots --yes
```

Then ensure `~/.codex/config.toml` contains:

```toml
[plugins."build-swift-apps@local"]
enabled = true
```

Use a new Codex thread after reinstalling.
