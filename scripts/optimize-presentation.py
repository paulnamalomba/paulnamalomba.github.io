#!/usr/bin/env python3
"""Create responsive presentation assets; retain original figures for PDF export."""

import json
from pathlib import Path
import re
import subprocess

from bs4 import BeautifulSoup
from PIL import Image


ROOT = Path(__file__).resolve().parent.parent
PAGE = ROOT / "presentations/africomp7/index.html"


def main():
    content = PAGE.read_text()
    output = PAGE.parent / "assets/responsive"
    output.mkdir(parents=True, exist_ok=True)
    manifest = {}

    def optimize(match):
        tag = BeautifulSoup(match[0], "html.parser").img
        source_path = tag.get("data-print-src", tag["src"])
        source = (PAGE.parent / source_path).resolve()
        if not source.is_file():
            return match[0]
        with Image.open(source) as image:
            width, height = image.size
        is_cover = "portrait" in source.name or source.stem in {"uct", "dresden", "seska", "nrf"}
        sizes = (240, 480) if is_cover else (640, 1280, 1920, 2400)
        variants = []
        for target_width in sorted({min(size, width) for size in sizes}):
            target = output / f"{source.stem}-{target_width}.webp"
            subprocess.run([
                "cwebp", "-quiet", "-q", "90", "-m", "6",
                "-resize", str(target_width), "0", str(source), "-o", str(target),
            ], check=True)
            variants.append({"path": target.relative_to(PAGE.parent).as_posix(),
                             "width": target_width, "bytes": target.stat().st_size})
        tag["data-print-src"] = source_path
        tag["src"] = variants[-1]["path"]
        tag["srcset"] = ", ".join(f"{v['path']} {v['width']}w" for v in variants)
        tag["sizes"] = "(max-width: 768px) 72px, 100px" if is_cover else "(max-width: 768px) calc(100vw - 64px), 1100px"
        tag["width"], tag["height"] = str(width), str(height)
        tag["loading"] = "eager" if is_cover else "lazy"
        tag["decoding"] = "async"
        manifest[source_path] = {"width": width, "height": height,
                                 "originalBytes": source.stat().st_size, "variants": variants}
        return str(tag)

    # Match tags only outside comments; leave commented scientific figures intact.
    content = re.sub(r"<!--[\s\S]*?-->|<img\b[^>]*>",
                     lambda m: m[0] if m[0].startswith("<!--") else optimize(m), content)
    PAGE.write_text(content)
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    before = sum(item["originalBytes"] for item in manifest.values())
    after = sum(item["variants"][-1]["bytes"] for item in manifest.values())
    print(f"{len(manifest)} images: {before:,} original bytes; {after:,} largest-variant bytes ({1-after/before:.1%} smaller).")


if __name__ == "__main__":
    main()
