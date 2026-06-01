---
name: ios-rocketsim-operator
description: Use RocketSim for iOS Simulator UI inspection and interaction, including visible accessibility state, taps, long-presses, swipes, typing, hardware buttons, and RocketSim CLI automation.
---

# iOS RocketSim Operator

Use the installed RocketSim app as the versioned Simulator automation layer. Always resolve the matching app bundle, bundled skill, and CLI before interacting with a simulator.

## Discovery

Prefer a running RocketSim bundle:

```bash
ROCKETSIM_PID="$(pgrep -x RocketSim | head -1)"
APP_PATH=""
if [ -n "$ROCKETSIM_PID" ]; then
  APP_PATH="$(ps -o command= -p "$ROCKETSIM_PID" | sed 's#/Contents/MacOS/RocketSim$##')"
fi
printf '%s\n' "$APP_PATH"
```

If not running, enumerate candidates with:

```bash
mdfind "kMDItemCFBundleIdentifier == 'com.swiftLee.RocketSim'"
```

Also check `/Applications/RocketSim.app`, `/Applications/RocketSim 2.app`, `~/Applications/RocketSim.app`, and `~/Applications/RocketSim 2.app`.

For each candidate, validate both files:

```bash
test -f "$APP_PATH/Contents/Resources/Agent-Skill/SKILL.md" && \
test -x "$APP_PATH/Contents/Helpers/rocketsim"
```

Use the first valid candidate. If RocketSim is running, use the running bundle only if it validates; otherwise rediscover or stop.

If no candidate validates, tell the user to launch or install a current RocketSim build from the Mac App Store:
`https://apps.apple.com/us/app/rocketsim-for-xcode-simulator/id1504940162`

## Required Paths

After discovery, set:

- Bundled skill: `$APP_PATH/Contents/Resources/Agent-Skill/SKILL.md`
- CLI: `$APP_PATH/Contents/Helpers/rocketsim`

Before any CLI call:

```bash
pgrep -x RocketSim >/dev/null && echo "Running" || echo "Not running"
```

If RocketSim is not running, ask the user to launch it. If it is running from a different bundle than `APP_PATH`, restart discovery and prefer the running bundle.

## Handoff

Read the bundled `Agent-Skill/SKILL.md` and follow it. Wherever it refers to `rocketsim`, use the resolved absolute CLI path. Do not use ad hoc simulator automation until discovery, validation, and the running-app check pass.
