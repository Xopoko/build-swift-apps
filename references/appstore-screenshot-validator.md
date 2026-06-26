# App Store Screenshot Validator Command Reference

Use this reference only after `appstore-screenshot-validator` is selected and
the agent needs concrete `asc`, `sips`, or upload commands.

## Source Of Truth

Do not hard-code Apple screenshot size tables. Query current ASC data:

```bash
asc screenshots sizes --output table
asc screenshots sizes --all --output table
```

Common anchors: `IPHONE_65` and `IPAD_PRO_3GEN_129`. Use `--all` for other
iPhone sizes, Apple TV, Mac, Vision Pro, iMessage, or Watch.

## ASC Validation

```bash
asc screenshots validate --path "./screenshots/iphone" --device-type "IPHONE_65" --output table
asc screenshots validate --path "./screenshots/ipad" --device-type "IPAD_PRO_3GEN_129" --output table
```

## Filename Cleanup

Sanitize filenames when screenshots contain hidden Unicode spaces:

```bash
python3 -c "import os
for f in os.listdir('.'):
    clean = f.replace('\u202f', ' ')
    if f != clean:
        os.rename(f, clean)
        print(f'Renamed: {clean}')"
```

## Inspect, Strip Alpha, Resize, Convert

Inspect size/alpha/color:

```bash
sips -g pixelWidth -g pixelHeight -g hasAlpha -g space screenshot.png
```

Strip alpha when needed; App Store Connect rejects alpha:

```bash
sips -s format jpeg input.png --out /tmp/asc-screenshot-no-alpha.jpg
sips -s format png /tmp/asc-screenshot-no-alpha.jpg --out output.png
rm /tmp/asc-screenshot-no-alpha.jpg
```

Resize only after choosing a target from `asc screenshots sizes --all`; `sips
-z` takes height then width:

```bash
mkdir -p resized
for f in *.png; do
  sips -z 2778 1284 "$f" --out "resized/$f"
done
```

Convert to sRGB when required:

```bash
sips -m "/System/Library/ColorSync/Profiles/sRGB IEC61966-2.1.icc" input.png --out output.png
```

## Upload

Validate and upload with dry-run first:

```bash
sips -g pixelWidth -g pixelHeight -g hasAlpha resized/*.png
asc screenshots validate --path "./resized" --device-type "IPHONE_65" --output table
asc screenshots upload --version-localization "LOC_ID" --path "./resized" --device-type "IPHONE_65" --dry-run --output table
asc screenshots upload --version-localization "LOC_ID" --path "./resized" --device-type "IPHONE_65"
```

## Guardrails

- Preserve originals by writing to a separate directory.
- Do not stretch across incompatible aspect ratios unless the user accepts the visual tradeoff.
- Prefer `asc screenshots validate` over visual inspection before upload.
