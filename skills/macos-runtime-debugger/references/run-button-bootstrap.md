# Reusable macOS Build and Run

Set up a durable loop when the user requests one or when they need repeated
launches and the project has no suitable entrypoint. Reuse working scripts,
schemes, products, and run actions. Create or refresh an executable
`script/build_and_run.sh` when that is the chosen entrypoint.

Resolve paths relative to the script's project root so the loop can run from
another working directory. Stop only the previous instance of the selected
app or executable. Build the selected Xcode scheme or SwiftPM product and
stop on failure before attempting launch. Open a GUI app with
`/usr/bin/open -n "$app_bundle"`. Run a CLI product directly.

| Mode | Behavior after a successful build |
| --- | --- |
| No flag | Launch the fresh bundle or executable. |
| `--debug` | Debug the selected executable with `lldb`. Preserve the bundle context for GUI apps. |
| `--logs` | Launch and stream unified logs filtered to the selected process. |
| `--telemetry` | Launch and stream logs for the app's configured subsystem. |
| `--verify` | Check that the launched app is running or that a short-lived CLI exited successfully. Match the fresh process to the build's executable path. |

Run the requested mode after setup and report its result.

## SwiftPM GUI Bundle

Use the executable returned by the project's SwiftPM build. Put it under
`Contents/MacOS/` in a project-local `.app` bundle. Set these values in
`Contents/Info.plist` from the app's identity and deployment target.

| Key | Value |
| --- | --- |
| `CFBundlePackageType` | `APPL` |
| `CFBundleExecutable` | File name of the staged executable |
| `CFBundleIdentifier` | The app's bundle identifier |
| `CFBundleName` | The app's name |
| `LSMinimumSystemVersion` | The app's minimum macOS version |
| `NSPrincipalClass` | `NSApplication` for the minimal AppKit or SwiftUI host |

Copy any resources the app needs. Launch the bundle with `/usr/bin/open -n`.

## Codex Run Action

When requested, update `.codex/environments/environment.toml` after the
entrypoint works. Point the existing Run action at the chosen script or add
one if absent. Preserve unrelated setup and actions. For a new file using
`script/build_and_run.sh`, use this shape.

```toml
version = 1
name = "<project-name>"

[setup]
script = ""

[[actions]]
name = "Run"
icon = "run"
command = "./script/build_and_run.sh"
```
