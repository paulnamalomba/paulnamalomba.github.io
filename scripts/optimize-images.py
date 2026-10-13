#!/usr/bin/env python3
"""Build responsive WebP copies without changing the original portfolio assets."""

import json
from pathlib import Path
import subprocess

from PIL import Image


ROOT = Path(__file__).resolve().parent.parent
SOURCES = [
    "paul.jpg", "paul-header.png", "seska_0.jpeg", "seat_01.png",
    "ecoride_03.jpg", "ecoride_04.jpg", "ecoride_05.jpg",
    "ecoride_06.jpg", "ecoride_07.jpg",
]


def main():
    output = ROOT / "assets" / "responsive"
    output.mkdir(parents=True, exist_ok=True)
    manifest = {}
    for filename in SOURCES:
        source = ROOT / "assets" / filename
        with Image.open(source) as image:
            width, height = image.size
        widths = sorted({min(value, width) for value in (480, 960, 1440)})
        variants = []
        for target_width in widths:
            target = output / f"{source.stem}-{target_width}.webp"
            subprocess.run([
                "cwebp", "-quiet", "-q", "86", "-m", "6",
                "-resize", str(target_width), "0", str(source), "-o", str(target),
            ], check=True)
            variants.append({
                "path": target.relative_to(ROOT).as_posix(),
                "width": target_width,
                "bytes": target.stat().st_size,
            })
        manifest[f"assets/{filename}"] = {
            "width": width, "height": height,
            "originalBytes": source.stat().st_size, "variants": variants,
        }
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    before = sum(asset["originalBytes"] for asset in manifest.values())
    after = sum(asset["variants"][-1]["bytes"] for asset in manifest.values())
    print(f"Largest responsive sources: {before:,} bytes to {after:,} bytes ({1-after/before:.1%} smaller).")


if __name__ == "__main__":
    main()
