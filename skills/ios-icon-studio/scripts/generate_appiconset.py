#!/usr/bin/env python3
import argparse
import json
import shutil
import struct
import subprocess
import sys
from pathlib import Path


ICON_SPECS = [
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


def filename_for(idiom: str, size: str, scale: str) -> str:
    safe_size = size.replace(".", "_")
    return f"Icon-{idiom}-{safe_size}@{scale}.png"


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


def build_contents(images):
    return {
        "images": images,
        "info": {
            "author": "xcode",
            "version": 1,
        },
    }


def parse_args():
    parser = argparse.ArgumentParser(
        description="Generate a standard iOS AppIcon.appiconset from one square PNG."
    )
    parser.add_argument("source_png", type=Path, help="Square source PNG, ideally 1024x1024 without alpha.")
    parser.add_argument("output_appiconset", type=Path, help="Output .appiconset directory.")
    parser.add_argument("--replace", action="store_true", help="Delete an existing output directory first.")
    parser.add_argument("--strict", action="store_true", help="Fail if source is smaller than 1024 or has alpha.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    source = args.source_png.expanduser().resolve()
    output = args.output_appiconset.expanduser().resolve()

    if shutil.which("sips") is None:
        print("error: this script requires macOS 'sips' on PATH", file=sys.stderr)
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
    if width < 1024:
        warnings.append(f"source is {width}x{height}; 1024x1024 is recommended")
    if has_alpha:
        warnings.append("source PNG appears to contain alpha/transparency")

    if args.strict and warnings:
        for warning in warnings:
            print(f"error: {warning}", file=sys.stderr)
        return 2

    if output.exists():
        if not args.replace:
            print(f"error: output exists; pass --replace to overwrite: {output}", file=sys.stderr)
            return 2
        shutil.rmtree(output)
    output.mkdir(parents=True, exist_ok=True)

    images = []
    generated = {}
    for idiom, size, scale in ICON_SPECS:
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

    print(f"Generated {len(generated)} icons in {output}")
    for warning in warnings:
        print(f"warning: {warning}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
