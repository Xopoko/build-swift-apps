#!/usr/bin/env python3
"""Audit local App Store screenshot image metadata.

This script reads PNG/JPEG headers directly with the Python standard library.
It does not resize, rewrite, strip alpha, upload, or call App Store Connect.
"""

from __future__ import annotations

import argparse
import json
import struct
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable


IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg"}
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
JPEG_SOF_MARKERS = {
    0xC0,
    0xC1,
    0xC2,
    0xC3,
    0xC5,
    0xC6,
    0xC7,
    0xC9,
    0xCA,
    0xCB,
    0xCD,
    0xCE,
    0xCF,
}
HIDDEN_SPACES = {
    "\u00a0": "NO-BREAK SPACE",
    "\u2007": "FIGURE SPACE",
    "\u202f": "NARROW NO-BREAK SPACE",
}


@dataclass(frozen=True)
class ImageAudit:
    path: str
    format: str
    width: int | None
    height: int | None
    has_alpha: bool | None
    size_allowed: bool | None
    hidden_space: bool
    ok: bool
    notes: list[str]


def parse_size(value: str) -> tuple[int, int]:
    normalized = value.lower().replace(" ", "")
    if "x" not in normalized:
        raise argparse.ArgumentTypeError(f"Expected WIDTHxHEIGHT, got {value!r}")
    width_text, height_text = normalized.split("x", 1)
    try:
        width = int(width_text)
        height = int(height_text)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"Expected WIDTHxHEIGHT, got {value!r}") from exc
    if width <= 0 or height <= 0:
        raise argparse.ArgumentTypeError(f"Image size must be positive, got {value!r}")
    return width, height


def iter_image_paths(paths: Iterable[Path], recursive: bool) -> list[Path]:
    result: list[Path] = []
    for path in paths:
        expanded = path.expanduser()
        if expanded.is_dir():
            iterator = expanded.rglob("*") if recursive else expanded.iterdir()
            result.extend(item for item in iterator if item.is_file() and item.suffix.lower() in IMAGE_SUFFIXES)
        elif expanded.is_file() and expanded.suffix.lower() in IMAGE_SUFFIXES:
            result.append(expanded)
        elif expanded.exists():
            result.append(expanded)
    return sorted(result, key=lambda item: str(item))


def has_hidden_space(path: Path) -> bool:
    return any(char in path.name for char in HIDDEN_SPACES)


def read_png(path: Path) -> tuple[int, int, bool, list[str]]:
    notes: list[str] = []
    with path.open("rb") as fh:
        if fh.read(8) != PNG_SIGNATURE:
            raise ValueError("invalid PNG signature")
        chunk_length_bytes = fh.read(4)
        chunk_type = fh.read(4)
        if len(chunk_length_bytes) != 4 or chunk_type != b"IHDR":
            raise ValueError("missing PNG IHDR")
        chunk_length = struct.unpack(">I", chunk_length_bytes)[0]
        if chunk_length < 13:
            raise ValueError("invalid PNG IHDR length")
        data = fh.read(chunk_length)
        if len(data) < 13:
            raise ValueError("truncated PNG IHDR")
        width, height, _bit_depth, color_type = struct.unpack(">IIBB", data[:10])
        fh.read(4)  # CRC
        has_alpha = color_type in {4, 6}
        if color_type == 3:
            notes.append("indexed-color PNG")
        while True:
            length_bytes = fh.read(4)
            if not length_bytes:
                break
            if len(length_bytes) != 4:
                raise ValueError("truncated PNG chunk length")
            length = struct.unpack(">I", length_bytes)[0]
            kind = fh.read(4)
            if len(kind) != 4:
                raise ValueError("truncated PNG chunk type")
            if kind == b"tRNS":
                has_alpha = True
                notes.append("PNG transparency chunk")
            fh.seek(length + 4, 1)  # payload + CRC
            if kind == b"IEND":
                break
    return width, height, has_alpha, notes


def read_jpeg(path: Path) -> tuple[int, int, bool, list[str]]:
    with path.open("rb") as fh:
        if fh.read(2) != b"\xff\xd8":
            raise ValueError("invalid JPEG signature")
        while True:
            byte = fh.read(1)
            if not byte:
                raise ValueError("missing JPEG SOF marker")
            if byte != b"\xff":
                continue
            marker_bytes = fh.read(1)
            while marker_bytes == b"\xff":
                marker_bytes = fh.read(1)
            if not marker_bytes:
                raise ValueError("truncated JPEG marker")
            marker = marker_bytes[0]
            if marker in {0xD8, 0xD9} or 0xD0 <= marker <= 0xD7:
                continue
            length_bytes = fh.read(2)
            if len(length_bytes) != 2:
                raise ValueError("truncated JPEG segment length")
            length = struct.unpack(">H", length_bytes)[0]
            if length < 2:
                raise ValueError("invalid JPEG segment length")
            if marker in JPEG_SOF_MARKERS:
                data = fh.read(length - 2)
                if len(data) < 5:
                    raise ValueError("truncated JPEG SOF segment")
                height, width = struct.unpack(">HH", data[1:5])
                return width, height, False, []
            fh.seek(length - 2, 1)


def inspect_image(path: Path, allowed_sizes: set[tuple[int, int]], allow_rotated: bool, fail_on_alpha: bool) -> ImageAudit:
    notes: list[str] = []
    hidden_space = has_hidden_space(path)
    if hidden_space:
        notes.append("filename contains hidden/non-breaking space")

    try:
        suffix = path.suffix.lower()
        if suffix == ".png":
            width, height, has_alpha, parsed_notes = read_png(path)
            image_format = "png"
            notes.extend(parsed_notes)
        elif suffix in {".jpg", ".jpeg"}:
            width, height, has_alpha, parsed_notes = read_jpeg(path)
            image_format = "jpeg"
            notes.extend(parsed_notes)
        else:
            return ImageAudit(
                path=str(path),
                format="unsupported",
                width=None,
                height=None,
                has_alpha=None,
                size_allowed=None,
                hidden_space=hidden_space,
                ok=False,
                notes=notes + ["unsupported file type"],
            )
    except Exception as exc:  # noqa: BLE001 - report exact parse failure.
        return ImageAudit(
            path=str(path),
            format="unknown",
            width=None,
            height=None,
            has_alpha=None,
            size_allowed=None,
            hidden_space=hidden_space,
            ok=False,
            notes=notes + [str(exc)],
        )

    size_allowed: bool | None = None
    if allowed_sizes:
        size_allowed = (width, height) in allowed_sizes or (allow_rotated and (height, width) in allowed_sizes)
        if not size_allowed:
            notes.append(f"size {width}x{height} is not in allowed set")

    ok = True
    if fail_on_alpha and has_alpha:
        ok = False
        notes.append("alpha channel present")
    if size_allowed is False:
        ok = False
    if hidden_space:
        ok = False

    return ImageAudit(
        path=str(path),
        format=image_format,
        width=width,
        height=height,
        has_alpha=has_alpha,
        size_allowed=size_allowed,
        hidden_space=hidden_space,
        ok=ok,
        notes=notes,
    )


def render_table(items: list[ImageAudit]) -> str:
    lines = ["ok\tformat\twidth\theight\talpha\tsize_allowed\thidden_space\tpath\tnotes"]
    for item in items:
        lines.append(
            "\t".join(
                [
                    "yes" if item.ok else "no",
                    item.format,
                    "" if item.width is None else str(item.width),
                    "" if item.height is None else str(item.height),
                    "" if item.has_alpha is None else ("yes" if item.has_alpha else "no"),
                    "" if item.size_allowed is None else ("yes" if item.size_allowed else "no"),
                    "yes" if item.hidden_space else "no",
                    item.path,
                    "; ".join(item.notes),
                ]
            )
        )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", help="Image file or directory paths")
    parser.add_argument("--allow-size", action="append", type=parse_size, default=[], help="Allowed WIDTHxHEIGHT; repeatable")
    parser.add_argument("--allow-rotated", action="store_true", help="Accept HEIGHTxWIDTH for each allowed size")
    parser.add_argument("--fail-on-alpha", action="store_true", help="Fail PNGs that contain alpha/transparency")
    parser.add_argument("--recursive", action="store_true", help="Recurse into directories")
    parser.add_argument("--json", action="store_true", help="Print JSON instead of a tab-separated table")
    args = parser.parse_args()

    image_paths = iter_image_paths([Path(path) for path in args.paths], recursive=args.recursive)
    allowed_sizes = set(args.allow_size)
    items = [inspect_image(path, allowed_sizes, args.allow_rotated, args.fail_on_alpha) for path in image_paths]
    payload = {
        "ok": bool(items) and all(item.ok for item in items),
        "count": len(items),
        "allowed_sizes": [f"{width}x{height}" for width, height in sorted(allowed_sizes)],
        "images": [asdict(item) for item in items],
    }

    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(render_table(items))
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
