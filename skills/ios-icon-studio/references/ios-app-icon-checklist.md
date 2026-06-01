# iOS App Icon Checklist

## Source Artwork

- Use a square master PNG, preferably `1024x1024`.
- Remove alpha/transparency for App Store and TestFlight readiness.
- Do not include rounded corners; iOS applies the mask.
- Keep important content away from the outer edge.
- Avoid tiny details that disappear below `80` px.
- Avoid text unless it is a single brand glyph that remains readable at `40-60` px.

## Readability Tests

Preview the icon at these sizes before replacing assets:

- `180x180`: iPhone home screen `60pt @3x`.
- `120x120`: iPhone home screen `60pt @2x` and spotlight sizes.
- `80x80`: iPad/spotlight contexts.
- `60x60`: small App Store/TestFlight and settings-like contexts.
- `40x40`: notification/settings-scale stress test.

Useful checks:

- Squint or blur the icon slightly. The main symbol should still be obvious.
- Convert mentally to grayscale. Shape contrast should carry the idea.
- Place it on both light and dark backgrounds.
- Compare beside common app icons. If it looks busy, reduce objects and details.

## Visual Direction

- Use one primary metaphor and one supporting detail at most.
- Give the silhouette a distinctive outline. This matters more than rendering detail.
- Use a limited palette with clear contrast between subject and background.
- Favor broad shapes, clean profiles, and readable negative space.
- If showing people speaking, make heads unmistakably human with profile cues: forehead, nose, lips/chin, and neck or speech-bubble treatment.
- Avoid kidney/bean ambiguity by making the face side flatter and adding profile landmarks.

## iOS Asset Catalog Notes

Standard generated slots usually include:

- iPhone: `20@2x`, `20@3x`, `29@2x`, `29@3x`, `40@2x`, `40@3x`, `60@2x`, `60@3x`.
- iPad: `20@1x`, `20@2x`, `29@1x`, `29@2x`, `40@1x`, `40@2x`, `76@1x`, `76@2x`, `83.5@2x`.
- Marketing: `1024@1x`.

Xcode may accept simpler modern app icon sets, but a full set is safer for existing projects and older deployment targets.

## Project Replacement Procedure

1. Search for existing icon sets:

   ```bash
   rg --files | rg 'AppIcon\.appiconset|Assets\.xcassets'
   ```

2. Confirm the configured app icon name:

   ```bash
   rg 'ASSETCATALOG_COMPILER_APPICON_NAME|AppIcon'
   ```

3. Generate the replacement set:

   ```bash
   python3 <skill-dir>/scripts/generate_appiconset.py master-icon.png path/to/AppIcon.appiconset --replace
   ```

4. Build the app. If the old icon remains on a simulator, uninstall the app or reset the simulator home screen cache.

## Common Failure Modes

- Source has alpha: App Store validation can fail or the icon can render unexpectedly.
- Artwork includes rounded corners: the mask doubles the corner radius and makes the icon look inset.
- Main object is too small: it looks like a texture on the home screen.
- Fine gradients/audio waves dominate: they vanish at small sizes.
- Multiple concepts compete: users cannot remember the icon.
- Replaced the wrong asset catalog: build succeeds but the app still shows the old icon.
