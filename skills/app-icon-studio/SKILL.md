---
name: app-icon-studio
description: Create, generate, evaluate, export, install, or debug iOS and macOS app icons, including AppIcon.appiconset assets and macOS .icns bundle icons.
---

# App Icon Studio

Create Apple-platform app icons from product context, generate polished
candidates, test small-size recognition, and install valid iOS or macOS icon
assets.

## Workflow

1. Inspect product reality: README, app name, screenshots, onboarding, paywall,
   core screens, audience, competitors if useful, and the target platform.
2. Write the strategy:
   ```text
   This icon should make <target user> remember <app name> as the app for <core job/emotion>, using <simple visual metaphor>.
   ```
3. Generate 3-5 distinct directions with `$imagegen` unless the repo has a
   native vector/logo system that should be edited directly.
4. Evaluate at practical sizes: about `60` px for iOS home-screen recognition,
   and `64`, `32`, and `16` px for macOS Dock/Finder stress checks.
5. Refine one square `1024x1024` PNG master. Prefer no alpha for shared
   iOS/macOS assets and App Store readiness. Avoid text, screenshots, tiny
   details, and baked iOS rounded corners.
6. Locate existing assets and preserve configured names:
   ```bash
   rg --files | rg 'Assets\.xcassets|AppIcon\.appiconset|\.icns$|Info\.plist|Contents\.json'
   rg 'ASSETCATALOG_COMPILER_APPICON_NAME|CFBundleIconFile|CFBundleIconName|AppIcon'
   ```
7. Generate or replace the platform asset:
   ```bash
   # iOS asset catalog
   python3 <skill-dir>/scripts/generate_appiconset.py master-icon.png path/to/AppIcon.appiconset --platform ios --replace

   # macOS asset catalog
   python3 <skill-dir>/scripts/generate_appiconset.py master-icon.png path/to/AppIcon.appiconset --platform macos --replace

   # macOS bundle icon
   python3 <skill-dir>/scripts/generate_appiconset.py master-icon.png path/to/AppIcon.icns --platform macos --format icns --replace
   ```
8. Build/run and inspect the installed icon: simulator/home screen for iOS, or
   the built `.app` bundle, Dock, Finder, and `Info.plist` for macOS. Clear icon
   caches or reinstall when the old icon is cached.

## ImageGen Prompt Contract

Use `$imagegen` for raster artwork. Ask for an Apple-platform app icon, square
`1024x1024` master artwork, one main symbol/metaphor, centered composition,
strong contrast, 2-4 colors, no text/watermark/UI screenshot/flags/tiny
details/baked iOS mask/transparent background unless a macOS transparent icon
silhouette is explicitly desired.

Open-ended directions:

- product metaphor;
- user outcome;
- category signal plus distinctive twist;
- abstract brand mark only when literal metaphors are weak;
- character/face only when identity, coaching, communication, or companionship
  is central.

## Platform Notes

- iOS applies the rounded mask; do not draw rounded corners into the artwork.
- macOS icons may use dimensional objects, perspective, and `.icns` files in
  `Contents/Resources`, but the silhouette must still survive at `32` and
  `16` px.
- Xcode asset catalogs usually reference `ASSETCATALOG_COMPILER_APPICON_NAME`;
  manually packaged macOS apps usually need `CFBundleIconFile` or
  `CFBundleIconName` plus a copied resource.
- Preserve the existing icon set name unless the project configuration is being
  updated in the same change.

## Design Rules

- Keep the main symbol large, centered, and mask-safe for the target platform.
- Prefer one memorable metaphor over a feature collage.
- Strong shape contrast first; color contrast second; verify grayscale/blur
  readability.
- Human faces/profiles need clear forehead, nose, mouth/chin cues; avoid
  ambiguous bean-like silhouettes.
- Make it ownable and desirable; if it fits ten competitors unchanged, it is
  too generic.

## Selection Rubric

Score recognition at small sizes, memory, category fit, differentiation, shelf
appeal beside real icons, brand fit, and technical readiness.

## Resources

- `scripts/generate_appiconset.py`: generate iOS/macOS icon PNGs,
  `Contents.json`, or macOS `.icns`.
- `scripts/preview_icon_readability.py`: HTML small-size preview on light/dark.
- `references/icon-strategy-and-imagegen.md`: concept strategy and prompt
  patterns.
- `references/app-icon-checklist.md`: detailed design/technical checklist.
