---
name: macos-swiftpm-runner
description: "macOS SwiftPM packages: build, run, and test package-first repositories and executables when `Package.swift` is primary or no Xcode project exists; not for Xcode-only app bundles."
---

# macOS SwiftPM Runner

Before invoking Apple-only binaries, confirm the execution context is macOS. From Windows or Linux, run those steps in a Mac SSH project or through an already configured remote transport; do not retry missing Apple binaries locally.

## Quick Start

Use this skill when `Package.swift` is the primary entrypoint or when SwiftPM is
the fastest path to a reproducible result.

## Workflow

1. Inspect the package.
   - Read `Package.swift`.
   - Identify executable, library, and test products.

2. Build with SwiftPM.
   - Use `swift build` by default.
   - Use release mode only when the user explicitly needs it.

3. Run the right product.
   - Use `swift run <product>` when an executable exists.
   - If multiple executables exist, explain the default choice.

4. Test narrowly.
   - Use `swift test`.
   - Apply filters when a specific test target or case is known.

5. Summarize failures.
   - Module/import resolution
   - Package graph or dependency issue
   - Linker failure
   - Runtime failure
   - Test regression

## Guardrails

- Prefer SwiftPM over Xcode when both exist and the package path is clearly simpler.
- Do not assume an app bundle exists in a pure package workflow.
- Explain when the package is library-only and therefore not directly runnable.

## Output Expectations

Provide:
- the package products you found
- the command you ran
- whether build, run, or test succeeded
- the top blocker if not
