---
name: appstore-screenshot-validator
description: Resize, strip alpha, color-convert, validate, and upload App Store screenshots using current `asc screenshots` size data and macOS `sips`.
---

# App Store Screenshot Validator

Prepare screenshots for App Store Connect. Do not hard-code Apple size tables here; `asc screenshots sizes` is the source of truth.

## Source of Truth

```bash
asc screenshots sizes --output table
asc screenshots sizes --all --output table
```

Validate locally before upload:

```bash
asc screenshots validate --path "./screenshots/iphone" --device-type "IPHONE_65" --output table
asc screenshots validate --path "./screenshots/ipad" --device-type "IPAD_PRO_3GEN_129" --output table
```

Common anchors: `IPHONE_65` and `IPAD_PRO_3GEN_129`. Use `--all` for other iPhone sizes, Apple TV, Mac, Vision Pro, iMessage, or Watch.

## Workflow

1. Sanitize filenames when screenshots contain hidden Unicode spaces:

   ```bash
   python3 -c "import os
   for f in os.listdir('.'):
       clean = f.replace('\u202f', ' ')
       if f != clean:
           os.rename(f, clean)
           print(f'Renamed: {clean}')"
   ```

2. Inspect size/alpha/color:

   ```bash
   sips -g pixelWidth -g pixelHeight -g hasAlpha -g space screenshot.png
   ```

3. Strip alpha when needed; App Store Connect rejects alpha:

   ```bash
   sips -s format jpeg input.png --out /tmp/asc-screenshot-no-alpha.jpg
   sips -s format png /tmp/asc-screenshot-no-alpha.jpg --out output.png
   rm /tmp/asc-screenshot-no-alpha.jpg
   ```

4. Resize only after choosing a target from `asc screenshots sizes --all`; `sips -z` takes height then width:

   ```bash
   mkdir -p resized
   for f in *.png; do
     sips -z 2778 1284 "$f" --out "resized/$f"
   done
   ```

5. Convert to sRGB when required:

   ```bash
   sips -m "/System/Library/ColorSync/Profiles/sRGB IEC61966-2.1.icc" input.png --out output.png
   ```

6. Validate, then upload with dry-run first:

   ```bash
   sips -g pixelWidth -g pixelHeight -g hasAlpha resized/*.png
   asc screenshots validate --path "./resized" --device-type "IPHONE_65" --output table
   asc screenshots upload --version-localization "LOC_ID" --path "./resized" --device-type "IPHONE_65" --dry-run --output table
   asc screenshots upload --version-localization "LOC_ID" --path "./resized" --device-type "IPHONE_65"
   ```

## Guardrails

Preserve originals by writing to a separate directory. Do not stretch across incompatible aspect ratios unless the user accepts the visual tradeoff. Prefer `asc screenshots validate` over visual inspection before upload.
