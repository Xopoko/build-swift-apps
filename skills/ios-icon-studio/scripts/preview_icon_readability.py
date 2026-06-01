#!/usr/bin/env python3
import argparse
import html
import shutil
from pathlib import Path


SIZES = [180, 120, 80, 60, 40, 29]


def parse_args():
    parser = argparse.ArgumentParser(
        description="Create an HTML preview that shows an iOS icon at practical small sizes."
    )
    parser.add_argument("source_png", type=Path, help="Source icon PNG.")
    parser.add_argument("output_dir", type=Path, help="Directory for preview.html and copied source image.")
    parser.add_argument("--title", default="iOS App Icon Preview", help="Preview page title.")
    return parser.parse_args()


def write_preview(source: Path, output_dir: Path, title: str):
    output_dir.mkdir(parents=True, exist_ok=True)
    preview_image = output_dir / "icon-source.png"
    shutil.copy2(source, preview_image)

    size_blocks = "\n".join(
        f"""
        <div class="sample">
          <div class="icon-frame" style="width:{size}px;height:{size}px">
            <img src="icon-source.png" alt="" />
          </div>
          <div class="label">{size}px</div>
        </div>
        """
        for size in SIZES
    )

    html_doc = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{html.escape(title)}</title>
  <style>
    :root {{
      color-scheme: light dark;
      font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", Helvetica, Arial, sans-serif;
    }}
    body {{
      margin: 0;
      padding: 32px;
      background: #f5f5f7;
      color: #1d1d1f;
    }}
    h1 {{
      margin: 0 0 20px;
      font-size: 22px;
      letter-spacing: 0;
    }}
    .row {{
      display: flex;
      flex-wrap: wrap;
      align-items: flex-end;
      gap: 22px;
      padding: 24px;
      margin-bottom: 20px;
      border: 1px solid rgba(0,0,0,.08);
      background: white;
    }}
    .row.dark {{
      background: #121214;
      color: #f5f5f7;
      border-color: rgba(255,255,255,.12);
    }}
    .sample {{
      display: grid;
      justify-items: center;
      gap: 8px;
    }}
    .icon-frame {{
      overflow: hidden;
      border-radius: 22.37%;
      box-shadow: 0 2px 8px rgba(0,0,0,.18);
      background: #ddd;
    }}
    .icon-frame img {{
      display: block;
      width: 100%;
      height: 100%;
      object-fit: cover;
    }}
    .label {{
      font-size: 12px;
      opacity: .7;
    }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(8, 60px);
      gap: 16px;
      padding: 24px;
      background: #ececf0;
      border: 1px solid rgba(0,0,0,.08);
    }}
    .grid .icon-frame {{
      width: 60px;
      height: 60px;
    }}
  </style>
</head>
<body>
  <h1>{html.escape(title)}</h1>
  <section class="row">{size_blocks}</section>
  <section class="row dark">{size_blocks}</section>
  <section class="grid" aria-label="Home screen shelf test">
    {''.join('<div class="icon-frame"><img src="icon-source.png" alt="" /></div>' for _ in range(32))}
  </section>
</body>
</html>
"""
    (output_dir / "preview.html").write_text(html_doc)
    return output_dir / "preview.html"


def main() -> int:
    args = parse_args()
    source = args.source_png.expanduser().resolve()
    if not source.exists():
        raise SystemExit(f"error: source file does not exist: {source}")
    preview = write_preview(source, args.output_dir.expanduser().resolve(), args.title)
    print(preview)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
