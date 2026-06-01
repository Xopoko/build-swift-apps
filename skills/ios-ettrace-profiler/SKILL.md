---
name: ios-ettrace-profiler
description: Capture and interpret symbolicated ETTrace profiles for iOS simulator startup, scrolling, navigation, rendering, runtime flows, before/after comparisons, and CPU hotspots.
---

# iOS ETTrace Profiler

Capture one focused, symbolicated ETTrace profile from an iOS simulator app. Pair with `ios-simulator-debugger` for build/install/launch/UI/log work.

## Workflow

1. Define one flow with clear start/stop points; avoid broad "use the app for a while" traces.
2. Build the exact simulator app.
3. Temporarily link `ETTrace.xcframework` into the app target, then remove it unless the user wants to keep it.
4. Collect UUID-matched app and first-party framework dSYMs.
5. Capture launch or runtime trace with a TTY.
6. Preserve fresh processed `output_<thread>.json` files immediately.
7. Analyze processed JSON only; report artifacts, hotspots, symbols, and caveats.

## Setup

```bash
RUN_DIR="${RUN_DIR:-$(mktemp -d "${TMPDIR:-/tmp}/codex-ios-ettrace.XXXXXX")}"
mkdir -p "$RUN_DIR"
brew install emergetools/homebrew-tap/ettrace
```

The host runner is `ettrace`; the app must link an iOS Simulator `ETTrace.xcframework`. Expect ETTrace v1.1.0-style processed JSON with top-level `nodes`.

Prefer a repo-vendored simulator xcframework. Otherwise build one into `RUN_DIR` from `EmergeTools/ETTrace` using the runner-matching tag. Link the app target, not tests/resources/launcher targets. Confirm launch logs include `Starting ETTrace`. Profile one instrumented simulator app at a time because simulator mode uses a fixed localhost port.

Bazel: `apple_dynamic_xcframework_import`. Xcode: temporary Link Binary With Libraries / Embed Frameworks for the debug simulator build.

## dSYM Gate

Do not interpret unsymbolicated traces.

```bash
SKILL_DIR="<absolute skill dir>"
APP="<built simulator App.app>"
DSYMS="$RUN_DIR/dsyms"
"$SKILL_DIR/scripts/collect_ios_dsyms.sh" \
  --app "$APP" --out-dir "$DSYMS" \
  --search-root "$(dirname "$APP")" --search-root "$PWD" \
  --extra-dsym "$RUN_DIR/ETTrace-iphonesimulator.xcarchive/dSYMs/ETTrace.framework.dSYM"
```

Add `--require-framework <Name>` for app-owned dynamic frameworks. Use `--require-all-frameworks` only when every embedded framework should have symbols. If required dSYMs are missing, rebuild that exact app with dSYM generation or add the right build output as a search root. Use `dwarfdump --uuid` when symbolication looks suspicious. Meaningful first-party "have library but no symbol" lines fail the trace; small system/ETTrace buckets are usually acceptable.

## Capture

Run with a TTY and answer prompts with `write_stdin`.

```bash
cd "$RUN_DIR"
CAPTURE_MARKER="$RUN_DIR/.ettrace-capture-start"; : > "$CAPTURE_MARKER"
find "$RUN_DIR" -maxdepth 1 \( -name 'output.json' -o -name 'output_*.json' \) -delete
ettrace --simulator --launch --verbose --dsyms "$DSYMS"
```

For runtime flow, omit `--launch`:

```bash
cd "$RUN_DIR"
CAPTURE_MARKER="$RUN_DIR/.ettrace-capture-start"; : > "$CAPTURE_MARKER"
find "$RUN_DIR" -maxdepth 1 \( -name 'output.json' -o -name 'output_*.json' \) -delete
ettrace --simulator --verbose --dsyms "$DSYMS"
```

Use `--launch` only for startup/first render. For first launch after install, set `ETTraceRunAtStartup=YES`, run `ettrace --simulator`, then launch from the home screen. Add `--multi-thread` only when needed.

## Preserve And Report

```bash
PRESERVED_DIR="$(mktemp -d "$RUN_DIR/run-$(date +%Y%m%d-%H%M%S).XXXXXX")"
: > "$PRESERVED_DIR/summary.txt"
find "$RUN_DIR" -maxdepth 1 -name 'output_*.json' -newer "$CAPTURE_MARKER" -print | while read -r json; do
  cp "$json" "$PRESERVED_DIR/${json##*/}"
  python3 "$SKILL_DIR/scripts/analyze_flamegraph_json.py" "$PRESERVED_DIR/${json##*/}" >> "$PRESERVED_DIR/summary.txt"
done
test -s "$PRESERVED_DIR/summary.txt"
```

Do not analyze `output.json` or raw `emerge-output/output.json`. Report flow, build, simulator/runtime, run count, preserved JSON paths, top active leaves/inclusive first-party stacks, symbolication completeness, caveats, and comparable before/after deltas.
