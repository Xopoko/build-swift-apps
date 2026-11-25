# App Store Screenshot Validator Command Reference

## Source Of Truth

Query current ASC data for each device family the app supports:

```bash
asc screenshots sizes --output table
asc screenshots sizes --all --output table
```

## ASC Validation

Use the actual device types selected from the size list. For example:

```bash
asc screenshots validate --path "./screenshots/iphone" --device-type "IPHONE_69" --output table
asc screenshots validate --path "./screenshots/ipad" --device-type "IPAD_PRO_3GEN_129" --output table
```

## Filename Cleanup

Replace hidden spaces in output filenames when copying screenshots into the
upload directory. Check for filename collisions before writing the copies.

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
  sips -z 2796 1290 "$f" --out "resized/$f"
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
asc screenshots validate --path "./resized" --device-type "IPHONE_69" --output table
asc screenshots upload --version-localization "LOC_ID" --path "./resized" --device-type "IPHONE_69" --dry-run --output table
asc screenshots upload --version-localization "LOC_ID" --path "./resized" --device-type "IPHONE_69"
```

Open the final images after conversion to check for stretching, clipping, or
visual changes the upload validation cannot detect.
