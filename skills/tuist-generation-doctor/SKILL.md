---
name: tuist-generation-doctor
description: Debug Tuist-generated project failures across generation, build, and runtime. Use when `tuist generate`, generated Xcode workspaces, or generated app launches fail or behave differently from the source project.
---

# Tuist Generation Doctor

Use this skill to determine whether a Tuist-generated workspace problem is a
project configuration issue, a dependency wiring issue, or a Tuist bug.

## Triage Route

1. Classify the failure stage:
   - generation: `tuist generate` or `tuist install`
   - build: generated `.xcworkspace` exists but `xcodebuild` fails
   - runtime: app builds but crashes or behaves incorrectly
2. Capture the exact command, Tuist version, Xcode version, platform, scheme,
   and relevant manifest snippets.
3. Reproduce on the local project first. If the issue is broad or suspicious,
   retry with the latest Tuist release through `mise`.
4. Reduce to a minimal reproduction before filing or fixing a Tuist-level bug.

## Commands

```bash
tuist version
mise exec tuist@latest -- tuist install --path "$PROJECT_DIR"
mise exec tuist@latest -- tuist generate --no-open --path "$PROJECT_DIR"
```

For build-stage failures:

```bash
xcodebuild build \
  -workspace "$PROJECT_DIR"/*.xcworkspace \
  -scheme "$SCHEME" \
  -destination "platform=iOS Simulator,name=<available iPhone simulator>,OS=latest" \
  -derivedDataPath "$PROJECT_DIR/DerivedData"
```

For runtime-stage failures, launch the generated app:

```bash
xcrun simctl boot "<available simulator name or UDID>" 2>/dev/null || true
xcrun simctl install booted "$APP_PATH"
xcrun simctl launch --console-pty booted "$BUNDLE_ID"
```

## Common Causes

- Missing `tuist install` before generation.
- Source/resource globs that omit files or include Swift files as resources.
- Package product type mismatches: static vs dynamic frameworks/libraries.
- Missing SDK dependencies, entitlements, Info.plist values, or resource bundles.
- Objective-C categories stripped from static dependencies; verify `-ObjC` or
  targeted `-force_load`.
- Generated workspace drift after manifest edits; regenerate before judging.

## When It Looks Like A Tuist Bug

Clone Tuist only after you have a small reproduction:

```bash
TUIST_SRC="$(mktemp -d)"
git clone --depth 1 https://github.com/tuist/tuist.git "$TUIST_SRC"
cd "$TUIST_SRC"
swift build --product tuist --product ProjectDescription --replace-scm-with-registry
"$TUIST_SRC/.build/debug/tuist" generate --no-open --path "$REPRO_DIR"
```

If the reproduction fails on Tuist `main`, report:

- minimal reproduction archive
- failing command and output
- Tuist/Xcode/macOS versions
- whether generation, build, or runtime fails
- what local configuration causes were ruled out

## Output

Return the failure stage, root cause, exact fix or next command, and proof from
the latest generation/build/launch attempt.
