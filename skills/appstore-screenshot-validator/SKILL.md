---
name: appstore-screenshot-validator
description: App Store screenshot validation and upload with live `asc` size data and macOS `sips` to resize, strip alpha, and color-convert copies.
---

# App Store Screenshot Validator

Before invoking Apple-only binaries, confirm the execution context is macOS. From Windows or Linux, run those steps in a Mac SSH project or through an already configured remote transport; do not retry missing Apple binaries locally.

Prepare screenshots for App Store Connect. Do not hard-code Apple size tables here; `asc screenshots sizes` is the source of truth.

## Source Of Truth

```bash
asc screenshots sizes --output table
asc screenshots sizes --all --output table
```

For apps that run on each device family, the current required anchors are the
iPhone 6.9-inch slot (`IPHONE_69`) and iPad 13-inch slot
(`IPAD_PRO_3GEN_129`). Apple accepts the iPhone 6.5-inch slot when 6.9-inch
screenshots are not provided. Use `--all` for every accepted iPhone size, Apple
TV, Mac, Vision Pro, iMessage, or Watch slot.

## Local Audit Helper

After choosing target dimensions from ASC, inspect local screenshots with the bundled helper:

```bash
python3 "$PLUGIN_ROOT/skills/appstore-screenshot-validator/scripts/screenshot_audit.py" \
  "./screenshots/iphone" --recursive --allow-size 1290x2796 --allow-rotated --fail-on-alpha
```

The helper reads PNG/JPEG headers only. It does not resize, rewrite, strip alpha, upload, or call ASC. Pass `--json` for machine-readable output.

## Workflow

1. Query current screenshot size requirements with `asc screenshots sizes --all`.
2. Run `screenshot_audit.py` against candidate PNG/JPEG files; fail on alpha and hidden Unicode filename spaces before upload.
3. Preserve originals. Write sanitized, alpha-stripped, resized, or color-converted images to a separate directory.
4. Use `sips` for macOS image rewrites only after selecting an ASC target size; `sips -z` takes height then width.
5. Run `asc screenshots validate` on the final directory, then `asc screenshots upload --dry-run`, then upload only after the dry-run is clean.

## Guardrails

Preserve originals by writing to a separate directory. Do not stretch across incompatible aspect ratios unless the user accepts the visual tradeoff. Prefer `asc screenshots validate` over visual inspection before upload.

## References

- `references/appstore-screenshot-validator.md` for detailed `asc`, `sips`, filename cleanup, validate, and upload commands.
