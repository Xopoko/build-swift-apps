---
name: swiftui-performance-inspector
description: Audit SwiftUI runtime performance from code and profiling evidence for slow rendering, janky scrolling, high CPU or memory, excessive updates, hangs, and layout thrash.
---

# SwiftUI Performance Inspector

Diagnose from code first, then request profiling evidence when code review cannot explain the symptom.

## Workflow

1. Classify the symptom: slow rendering, scrolling jank, high CPU, memory growth, hangs, broad updates, or layout thrash.
2. If code is available, review with `references/code-smells.md`.
3. If code is missing, ask for the smallest useful slice: target view, data flow, reproduction steps, device/simulator, build config, and deployment target.
4. If runtime evidence is needed, use `references/profiling-intake.md` for the exact Instruments checklist.
5. Report likely causes, evidence, fixes, and validation steps using `references/report-template.md` when useful.

## Code Review Focus

- invalidation storms from broad observation or environment reads
- unstable identity in `List`/`ForEach`
- heavy derived work in `body` or view builders
- layout thrash from complex hierarchy, `GeometryReader`, or preferences
- main-thread image decode/resize or other expensive work
- animation and transition work applied too broadly

## Profiling Evidence

Ask for SwiftUI timeline or Time Profiler export/screenshots, device/OS/build configuration, exact profiled interaction, and before/after metrics when comparing changes.

Map evidence to invalidation, identity churn, layout, main-thread work, image cost, animation cost, or hangs. Distinguish trace-backed findings from code-level suspicion and state what evidence would reduce uncertainty.

## Fix Defaults

- narrow state scope and observation fan-out
- stabilize list identities
- move heavy work out of `body` into model/service precomputation, memoized helpers, background preprocessing, or input-driven derived state
- use `@State` only for view-owned state, not arbitrary caches
- use `equatable()` only when equality is cheaper than recomputing and inputs are value-semantic
- downsample images before rendering
- reduce layout complexity or add stable sizing where appropriate

## Output

Provide a short metrics table when available, top issues ordered by impact, proposed fixes with effort, and verification steps.

## References

- `references/profiling-intake.md`
- `references/code-smells.md`
- `references/report-template.md`
- `references/optimizing-swiftui-performance-instruments.md`
- `references/understanding-improving-swiftui-performance.md`
- `references/understanding-hangs-in-your-app.md`
- `references/demystify-swiftui-performance-wwdc23.md`

Use current Apple Developer docs when Instruments or SwiftUI performance guidance may have changed.
