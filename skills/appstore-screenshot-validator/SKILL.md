---
name: appstore-screenshot-validator
description: App Store screenshot validation and upload with live `asc` size data and macOS `sips` to resize, strip alpha, and color-convert copies.
---

# App Store Screenshot Validator

Before invoking Apple-only binaries, confirm the execution context is macOS. From Windows or Linux, run those steps in a Mac SSH project or through an already configured remote transport; do not retry missing Apple binaries locally.

## Workflow

1. Query current screenshot size requirements with `asc screenshots sizes --all`.
2. Run `asc screenshots validate` with the selected `--device-type`. It checks readable PNG/JPEG files, dimensions, format, and alpha locally.
3. If changes are needed, preserve originals and aspect ratio. Write sanitized, flattened, resized, or color-converted copies to a separate directory, then validate the copies.
4. Run `asc screenshots upload --dry-run` for the target localization and device type. Upload after reviewing the dry-run output.

## References

- `references/appstore-screenshot-validator.md` for detailed `asc`, `sips`, filename cleanup, validate, and upload commands.
