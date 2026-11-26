---
description: Build, run, debug, or inspect logs for a macOS app.
---

# /macos-runtime-debug

Use [macos-runtime-debugger](../skills/macos-runtime-debugger/SKILL.md) and its
[bootstrap procedure](../skills/macos-runtime-debugger/references/run-button-bootstrap.md)
to set up or refresh a reusable macOS run loop.

Pass through any supplied `scheme`, `workspace`, `project`, `product`, or
`app_name`. Run the supplied `mode` (`run`, `debug`, `logs`, `telemetry`, or
`verify`), defaulting to `run`. Treat `run_action=true` as a request to
configure the Codex Run action.
