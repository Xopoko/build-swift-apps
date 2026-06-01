---
name: appstore-screenshot-studio
description: Create, revise, translate, scrape, crop, validate, and prepare App Store marketing screenshots and `.appstore-screenshots` workspaces. Not for general image generation.
---

# App Store Screenshot Studio

Build App Store screenshots from product reality: inspect the app, choose install promises, write concise panel copy, assemble visuals, crop panels, and prepare App Store Connect assets.

Pair simulator capture/upload work with `appstore-screenshot-pipeline`, `appstore-screenshot-validator`, and `appstore-review-readiness`.

## Workflow

1. Resolve context: repo, README, onboarding, paywall, root screens, existing screenshots/listings, and brand rules. If given an App Store URL, run `scripts/scrape.mjs` and save JSON under `.appstore-screenshots/scraped/`. Ask only for missing facts that change direction: app name, devices, locales, panel count.
2. Initialize:

   ```bash
   node <skill-dir>/scripts/scaffold.mjs --output-dir .appstore-screenshots
   ```

   Work from `.appstore-screenshots/config.json`; keep composites in `.appstore-screenshots/composites/` and final panels in `.appstore-screenshots/panels/`.

3. Plan 3-5 install-focused benefits. Put the clearest value in panel 1. Keep captions readable in search results, concrete, truthful, localizable, and useful as standalone panels.
4. Generate or assemble visuals. Use real app screenshots when accuracy matters; use image generation only for marketing composites. Keep important text/device edges crop-safe. Do not fake store badges, download buttons, nonexistent features, or misleading UI.
5. Crop:

   ```bash
   node <skill-dir>/scripts/crop.mjs \
     --input .appstore-screenshots/composites/iphone-en.png \
     --device iphone \
     --output-dir .appstore-screenshots/panels/iphone/en
   ```

6. Validate dimensions, file count, and small thumbnails. For ASC upload, use `appstore-screenshot-pipeline` or `asc screenshots validate/upload` after IDs/localizations are known.

## Workspace

- `.appstore-screenshots/config.json`: app, App Store URL, devices, locales, panel count, colors, benefits.
- `.appstore-screenshots/manifest.json`: generated/cropped inventory.
- `.appstore-screenshots/scraped/`: optional public App Store metadata.
- `.appstore-screenshots/composites/`: source composites.
- `.appstore-screenshots/panels/`: upload-ready panels.

## Presets

| Device | Composite | Panel | Key |
| --- | --- | --- | --- |
| iPhone | `3456x2400` | `1284x2778` | `iphone` |
| iPad | `6144x2732` | `2048x2732` | `ipad` |

The crop helper treats a composite as three horizontal panels. For other layouts, crop manually with `sharp`, `sips`, or the app's asset pipeline.

## Quality Bar

Use real product language, high-contrast short headlines, truthful UI, meaning-based localization, and repeated crop/size validation. Do not upload until the user approves final panels or explicitly asks for automated upload.
