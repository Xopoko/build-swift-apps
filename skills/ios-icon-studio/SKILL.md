---
name: ios-icon-studio
description: Create, generate, evaluate, export, install, or debug iOS app icons and AppIcon.appiconset assets. Use for icon strategy, ImageGen prompts, small-size readability, asset catalog replacement, TestFlight/App Store prep, and icon cache issues.
---

# iOS Icon Studio

Create an iOS icon from product context, generate polished candidates, test small-size recognition, and install a valid `AppIcon.appiconset`.

## Workflow

1. Inspect product reality: README, app name, screenshots, onboarding, paywall, core screens, audience, competitors if useful.
2. Write the strategy:
   ```text
   This icon should make <target user> remember <app name> as the app for <core job/emotion>, using <simple visual metaphor>.
   ```
3. Generate 3-5 distinct directions with `$imagegen` unless the repo has a native vector/logo system that should be edited directly.
4. Evaluate at ~60 px; simplify or reject unreadable candidates.
5. Refine one square `1024x1024` PNG master: no alpha, no text, no screenshots, no tiny details, no baked rounded corners.
6. Locate existing assets and preserve the configured icon set name:
   ```bash
   rg --files | rg 'Assets\.xcassets|AppIcon\.appiconset|Contents\.json'
   rg 'ASSETCATALOG_COMPILER_APPICON_NAME|AppIcon'
   ```
7. Generate/replace:
   ```bash
   python3 <skill-dir>/scripts/generate_appiconset.py master-icon.png path/to/AppIcon.appiconset --replace
   ```
8. Build/run and inspect the installed icon on the simulator/home screen. Uninstall/reboot simulator if the old icon is cached.

## ImageGen Prompt Contract

Use `$imagegen` for raster artwork. Ask for an iOS app icon, square 1024x1024 master, one main symbol/metaphor, centered composition, generous iOS mask margin, strong contrast, 2-4 colors, no text/watermark/UI screenshot/flags/tiny details/baked mask/transparent background.

Open-ended directions:

- product metaphor;
- user outcome;
- category signal plus distinctive twist;
- abstract brand mark only when literal metaphors are weak;
- character/face only when identity, coaching, communication, or companionship is central.

## Design Rules

- iOS applies the rounded mask; do not draw it.
- Main symbol should be large, centered, and mask-safe.
- Prefer one memorable metaphor over a feature collage.
- Strong shape contrast first; color contrast second; verify grayscale/blur readability.
- Human faces/profiles need clear forehead, nose, mouth/chin cues; avoid bean/kidney silhouettes.
- Make it ownable and desirable; if it fits ten competitors unchanged, it is too generic.

## Selection Rubric

Score recognition at 60 px, memory, category fit, differentiation, shelf appeal beside real icons, brand fit, and technical readiness.

## Resources

- `scripts/generate_appiconset.py`: generate icon PNGs and `Contents.json`.
- `scripts/preview_icon_readability.py`: HTML small-size preview on light/dark.
- `references/icon-strategy-and-imagegen.md`: concept strategy and prompt patterns.
- `references/ios-app-icon-checklist.md`: detailed design/technical checklist.
