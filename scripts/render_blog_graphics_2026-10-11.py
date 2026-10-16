#!/usr/bin/env python3
"""Render the blog graphics in docs/blogs/images/src/2026-10-11-cards.html to PNGs.

This renderer and its output files are namespaced to the 2026-10-11 weekly
post specifically: earlier posts' renderers (e.g. for 2026-10-10) use their
own generically-named `cards.html` / `render_blog_graphics.py` on their own
branches, and generic shared filenames here have previously collided across
posts when two post branches both touched `docs/blogs/images/hero.png` etc.
Keep this per-post naming convention for any future renderer in this
directory.

Requires Playwright with a Chromium build:
    pip install playwright && playwright install chromium
Set CHROMIUM_PATH to use an existing browser binary instead.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "docs" / "blogs" / "images" / "src" / "2026-10-11-cards.html"
OUT = ROOT / "docs" / "blogs" / "images"

# element id in cards.html -> output file name
CARDS: dict[str, str] = {
    "hero": "2026-10-11-hero.png",
    "timeline": "2026-10-11-weekly-timeline.png",
    "calibration": "2026-10-11-calibration-matrix.png",
    "teststats": "2026-10-11-test-stats.png",
}


def main() -> int:
    if not SRC.is_file():
        print(f"missing {SRC}", file=sys.stderr)
        return 1
    launch_args: dict[str, str] = {}
    if path := os.environ.get("CHROMIUM_PATH"):
        launch_args["executable_path"] = path
    with sync_playwright() as p:
        browser = p.chromium.launch(**launch_args)
        try:
            page = browser.new_page(viewport={"width": 1400, "height": 900})
            page.goto(SRC.as_uri())
            for element_id, filename in CARDS.items():
                page.locator(f"#{element_id}").screenshot(path=str(OUT / filename))
                print(f"wrote {filename}")
        finally:
            browser.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
