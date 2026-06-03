# App Icon Checklist

## Source Artwork

- Use a square master PNG, preferably `1024x1024`.
- Remove alpha/transparency for iOS and shared App Store readiness. macOS `.icns`
  can use transparency when the icon is intentionally silhouette-based.
- Do not include baked iOS rounded corners; iOS applies the mask.
- Keep important content away from the outer edge.
- Avoid tiny details that disappear below `80` px.
- Avoid text unless it is a single brand glyph that remains readable at
  `40-60` px.

## Readability Tests

Preview the icon at these sizes before replacing assets:

- `180x180`: iPhone home screen `60pt @3x`.
- `120x120`: iPhone home screen `60pt @2x` and spotlight sizes.
- `80x80` and `64x64`: iPad, Finder, Dock, and toolbar-like contexts.
- `60x60` and `40x40`: small App Store/TestFlight and settings-like contexts.
- `32x32` and `16x16`: macOS Finder/Dock stress checks.

Useful checks:

- Squint or blur the icon slightly. The main symbol should still be obvious.
- Convert mentally to grayscale. Shape contrast should carry the idea.
- Place it on both light and dark backgrounds.
- Compare beside common app icons. If it looks busy, reduce objects and details.

## Visual Direction

- Use one primary metaphor and one supporting detail at most.
- Give the silhouette a distinctive outline. This matters more than rendering
  detail.
- Use a limited palette with clear contrast between subject and background.
- Favor broad shapes, clean profiles, and readable negative space.
- For macOS, depth and perspective can help shelf appeal, but the icon still
  needs a simple outline at `32` and `16` px.
- If showing people speaking, make heads unmistakably human with profile cues:
  forehead, nose, lips/chin, and neck or speech-bubble treatment.
- Avoid ambiguous organic silhouettes by making the outline specific and
  category-relevant.

## iOS Asset Catalog Notes

Standard generated slots usually include:

- iPhone: `20@2x`, `20@3x`, `29@2x`, `29@3x`, `40@2x`, `40@3x`, `60@2x`,
  `60@3x`.
- iPad: `20@1x`, `20@2x`, `29@1x`, `29@2x`, `40@1x`, `40@2x`, `76@1x`,
  `76@2x`, `83.5@2x`.
- Marketing: `1024@1x`.

Xcode may accept simpler modern app icon sets, but a full set is safer for
existing projects and older deployment targets.

## macOS Icon Notes

Standard generated macOS asset catalog slots usually include:

- `16@1x`, `16@2x`, `32@1x`, `32@2x`, `128@1x`, `128@2x`, `256@1x`,
  `256@2x`, `512@1x`, and `512@2x`.

For manually packaged apps:

- Put the `.icns` file under `Contents/Resources`.
- Set `CFBundleIconFile` to the icon resource name without a path. The `.icns`
  extension is accepted but commonly omitted.
- Rebuild or relaunch the bundle after changing `Info.plist`; Finder and Dock
  can cache old icons.

## Project Replacement Procedure

1. Search for existing icon assets:

   ```bash
   rg --files | rg 'AppIcon\.appiconset|Assets\.xcassets|\.icns$|Info\.plist'
   ```

2. Confirm the configured app icon name:

   ```bash
   rg 'ASSETCATALOG_COMPILER_APPICON_NAME|CFBundleIconFile|CFBundleIconName|AppIcon'
   ```

3. Generate the replacement set:

   ```bash
   python3 <skill-dir>/scripts/generate_appiconset.py master-icon.png path/to/AppIcon.appiconset --platform ios --replace
   python3 <skill-dir>/scripts/generate_appiconset.py master-icon.png path/to/AppIcon.appiconset --platform macos --replace
   python3 <skill-dir>/scripts/generate_appiconset.py master-icon.png path/to/AppIcon.icns --platform macos --format icns --replace
   ```

4. Build the app. If the old icon remains visible, reinstall the iOS app or
   restart Finder/Dock only after confirming the built bundle contains the new
   icon metadata.

## Common Failure Modes

- Source has alpha where iOS or App Store marketing disallows it.
- Artwork includes rounded corners: the iOS mask doubles the corner radius and
  makes the icon look inset.
- Main object is too small: it looks like a texture at small sizes.
- Fine gradients/audio waves dominate: they vanish at small sizes.
- Multiple concepts compete: users cannot remember the icon.
- Replaced the wrong asset catalog or bundle resource: build succeeds but the
  app still shows the old icon.
- macOS bundle copies the `.icns` but `Info.plist` does not set
  `CFBundleIconFile`.
