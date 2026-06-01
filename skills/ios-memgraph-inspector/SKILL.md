---
name: ios-memgraph-inspector
description: Capture, inspect, compare, and prove iOS leaks with Apple's `leaks`, simulator memgraphs, retain-cycle evidence, and before/after leak summaries.
---

# iOS Memgraph Inspector

Use for leaks from a live simulator process or existing `.memgraph`. Pair with `../ios-simulator-debugger/SKILL.md` when build, launch, UI driving, logs, or screenshots are needed.

## Workflow

1. Build, launch, and drive the exact flow that should release objects.
2. Capture with `scripts/capture_sim_memgraph.sh`.
3. Summarize with `scripts/summarize_memgraph_leaks.py`.
4. For app-owned leaked types, inspect ownership with `leaks --traceTree=<address> <file.memgraph>` and grouped leak evidence.
5. Patch the smallest retaining edge, then recapture the same flow/simulator when possible.
6. Report before/after counts, disappeared root types or paths, remaining leaks, memgraph paths, and build/test proof.

Do not claim a fix from a smaller memgraph alone; prove the specific type or ownership path disappeared.

## Capture

`SKILL_DIR` is the loaded skill folder, not the app repo.

```bash
SKILL_DIR="<absolute path to this loaded skill folder>"
SIM="<simulator-udid>"
BUNDLE_ID="<app.bundle.identifier>"
MEMGRAPH_DIR="$(mktemp -d "${TMPDIR:-/tmp}/codex-ios-memgraph.XXXXXX")"

"$SKILL_DIR/scripts/capture_sim_memgraph.sh" \
  --udid "$SIM" \
  --bundle-id "$BUNDLE_ID" \
  --out-dir "$MEMGRAPH_DIR"
```

If the process is missing, verify the bundle id and inspect running labels:

```bash
xcrun simctl spawn "$SIM" launchctl list
```

Summarize:

```bash
"$SKILL_DIR/scripts/summarize_memgraph_leaks.py" \
  /path/to/app.memgraph \
  --trace-limit 5 \
  --out /path/to/leak-summary.md
```

Use `--trace-limit` sparingly. If `traceTree` says `Found 0 roots referencing`, treat it as an unreachable/self-retained candidate and inspect `leaks --groupByType <file.memgraph>` plus source.

## Root-Cause Rules

- Identify the first app-owned leaked type.
- Determine intended lifetime: process, session, account, view, request, or task.
- Lazy allocation is scope reduction, not proof of a fixed leak.
- Prove retain cycles with `traceTree` or an isolated repro.
- Separate framework/runtime noise from app-owned branches.
- Prefer removing the retaining edge over broad cleanup code.

## Report

Include flow, simulator/app build, memgraph and summary paths, leaked app types/counts, ownership path or grouped evidence, applied/proposed fix, and before/after evidence. If only framework noise appears, say so and recommend a narrower capture.
