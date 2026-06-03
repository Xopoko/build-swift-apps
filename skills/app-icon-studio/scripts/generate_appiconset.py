#!/usr/bin/env python3
import argparse
import json
import shutil
import struct
import subprocess
import sys
import tempfile
from pathlib import Path


IOS_ICON_SPECS = [
    ("iphone", "20", "2x"),
    ("iphone", "20", "3x"),
    ("iphone", "29", "2x"),
    ("iphone", "29", "3x"),
    ("iphone", "40", "2x"),
    ("iphone", "40", "3x"),
    ("iphone", "60", "2x"),
    ("iphone", "60", "3x"),
    ("ipad", "20", "1x"),
    ("ipad", "20", "2x"),
    ("ipad", "29", "1x"),
    ("ipad", "29", "2x"),
    ("ipad", "40", "1x"),
    ("ipad", "40", "2x"),
    ("ipad", "76", "1x"),
    ("ipad", "76", "2x"),
    ("ipad", "83.5", "2x"),
    ("ios-marketing", "1024", "1x"),
]

MACOS_ICON_SPECS = [
    ("mac", "16", "1x"),
    ("mac", "16", "2x"),
    ("mac", "32", "1x"),
    ("mac", "32", "2x"),
    ("mac", "128", "1x"),
    ("mac", "128", "2x"),
    ("mac", "256", "1x"),
    ("mac", "256", "2x"),
    ("mac", "512", "1x"),
    ("mac", "512", "2x"),
]

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def read_png_info(path: Path):
    with path.open("rb") as f:
        if f.read(8) != PNG_SIGNATURE:
            raise ValueError("source is not a PNG file")

        width = height = color_type = None
        has_trns = False

        while True:
            header = f.read(8)
            if len(header) != 8:
                break
            length, chunk_type = struct.unpack(">I4s", header)
            data = f.read(length)
            f.read(4)

            if chunk_type == b"IHDR":
                width, height, _bit_depth, color_type, *_ = struct.unpack(">IIBBBBB", data)
            elif chunk_type == b"tRNS":
                has_trns = True
            elif chunk_type == b"IEND":
                break

        if width is None or height is None:
            raise ValueError("PNG is missing IHDR metadata")

        has_alpha = color_type in (4, 6) or has_trns
        return width, height, has_alpha


def pixel_size(size: str, scale: str) -> int:
    return int(round(float(size) * int(scale.removesuffix("x"))))


def appiconset_specs(platform: str):
    if platform == "ios":
        return IOS_ICON_SPECS
    if platform == "macos":
        return MACOS_ICON_SPECS
    if platform == "universal":
        return IOS_ICON_SPECS + MACOS_ICON_SPECS
    raise ValueError(f"unsupported platform: {platform}")


def filename_for(idiom: str, size: str, scale: str) -> str:
    safe_size = size.replace(".", "_")
    return f"Icon-{idiom}-{safe_size}@{scale}.png"


def iconset_filename(size: str, scale: str) -> str:
    if scale == "1x":
        return f"icon_{size}x{size}.png"
    return f"icon_{size}x{size}@{scale}.png"


def run_sips(source: Path, destination: Path, pixels: int):
    command = [
        "sips",
        "-s",
        "format",
        "png",
        "-z",
        str(pixels),
        str(pixels),
        str(source),
        "--out",
        str(destination),
    ]
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    if result.returncode != 0:
        raise RuntimeError(result.stdout.strip())


def run_iconutil(iconset: Path, output_icns: Path):
    command = ["iconutil", "-c", "icns", str(iconset), "-o", str(output_icns)]
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    if result.returncode != 0:
        raise RuntimeError(result.stdout.strip())


def build_contents(images):
    return {
        "images": images,
        "info": {
            "author": "xcode",
            "version": 1,
        },
    }


def remove_existing(path: Path):
    if path.is_dir():
        shutil.rmtree(path)
    else:
        path.unlink()


def prepare_output(path: Path, replace: bool, make_dir: bool):
    if path.exists():
        if not replace:
            print(f"error: output exists; pass --replace to overwrite: {path}", file=sys.stderr)
            return False
        remove_existing(path)
    if make_dir:
        path.mkdir(parents=True, exist_ok=True)
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
    return True


def generate_appiconset(source: Path, output: Path, platform: str, replace: bool):
    if not prepare_output(output, replace, make_dir=True):
        return 2

    images = []
    generated = {}
    for idiom, size, scale in appiconset_specs(platform):
        pixels = pixel_size(size, scale)
        filename = filename_for(idiom, size, scale)
        destination = output / filename
        run_sips(source, destination, pixels)
        generated[filename] = pixels
        images.append(
            {
                "filename": filename,
                "idiom": idiom,
                "scale": scale,
                "size": f"{size}x{size}",
            }
        )

    (output / "Contents.json").write_text(json.dumps(build_contents(images), indent=2) + "\n")
    print(f"Generated {len(generated)} app icon images in {output}")
    return 0


def generate_icns(source: Path, output: Path, replace: bool):
    if not prepare_output(output, replace, make_dir=False):
        return 2

    with tempfile.TemporaryDirectory(suffix=".iconset") as temporary:
        iconset = Path(temporary)
        for _idiom, size, scale in MACOS_ICON_SPECS:
            pixels = pixel_size(size, scale)
            destination = iconset / iconset_filename(size, scale)
            run_sips(source, destination, pixels)
        run_iconutil(iconset, output)

    print(f"Generated macOS .icns in {output}")
    return 0


def parse_args():
    parser = argparse.ArgumentParser(
        description="Generate iOS/macOS AppIcon.appiconset assets or a macOS .icns from one square PNG."
    )
    parser.add_argument("source_png", type=Path, help="Square source PNG, ideally 1024x1024.")
    parser.add_argument("output", type=Path, help="Output .appiconset directory or .icns file.")
    parser.add_argument(
        "--platform",
        choices=("ios", "macos", "universal"),
        default="ios",
        help="Icon platform slots to generate. Defaults to ios for backward compatibility.",
    )
    parser.add_argument(
        "--format",
        choices=("appiconset", "icns"),
        help="Output format. Defaults to icns for .icns outputs, otherwise appiconset.",
    )
    parser.add_argument("--replace", action="store_true", help="Delete an existing output first.")
    parser.add_argument("--strict", action="store_true", help="Fail on undersized sources or iOS alpha issues.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    source = args.source_png.expanduser().resolve()
    output = args.output.expanduser().resolve()
    output_format = args.format or ("icns" if output.suffix == ".icns" else "appiconset")

    if shutil.which("sips") is None:
        print("error: this script requires macOS 'sips' on PATH", file=sys.stderr)
        return 2

    if output_format == "icns" and shutil.which("iconutil") is None:
        print("error: this script requires macOS 'iconutil' on PATH for .icns output", file=sys.stderr)
        return 2

    if output_format == "icns" and args.platform == "ios":
        print("error: .icns output is only valid for --platform macos or universal", file=sys.stderr)
        return 2

    if not source.exists():
        print(f"error: source file does not exist: {source}", file=sys.stderr)
        return 2

    try:
        width, height, has_alpha = read_png_info(source)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if width != height:
        print(f"error: source PNG must be square, got {width}x{height}", file=sys.stderr)
        return 2

    warnings = []
    errors = []
    if width < 1024:
        message = f"source is {width}x{height}; 1024x1024 is recommended"
        warnings.append(message)
        errors.append(message)
    if has_alpha and args.platform in ("ios", "universal"):
        message = "source PNG appears to contain alpha/transparency; iOS and App Store marketing icons should not"
        warnings.append(message)
        errors.append(message)
    elif has_alpha:
        warnings.append("source PNG contains alpha/transparency; this can be valid for macOS .icns")

    if args.strict and errors:
        for error in errors:
            print(f"error: {error}", file=sys.stderr)
        return 2

    try:
        if output_format == "icns":
            status = generate_icns(source, output, args.replace)
        else:
            status = generate_appiconset(source, output, args.platform, args.replace)
    except RuntimeError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if status != 0:
        return status

    for warning in warnings:
        print(f"warning: {warning}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
