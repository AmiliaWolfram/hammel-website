"""Capture and compare Machine Comparison screenshots on a running local Django site.

Usage:
    python tools/check_machine_comparison_visual.py baseline --url http://127.0.0.1:8000/your-comparison-url/
    python tools/check_machine_comparison_visual.py compare --url http://127.0.0.1:8000/your-comparison-url/

Requires: pip install playwright pillow && python -m playwright install chromium
"""
import argparse
from pathlib import Path

from PIL import Image, ImageChops
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent / "visual-regression" / "machine-comparison"
SIZES = {"desktop": (1440, 900), "mobile": (390, 844)}


def capture(url, destination):
    destination.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        for name, (width, height) in SIZES.items():
            page = browser.new_page(viewport={"width": width, "height": height}, device_scale_factor=1)
            page.goto(url, wait_until="networkidle")
            page.locator(".comparison-page").wait_for()
            page.screenshot(path=str(destination / f"{name}.png"), full_page=True, animations="disabled")
            page.close()
        browser.close()


def compare(reference, current):
    problems = []
    for name in SIZES:
        old_path, new_path = reference / f"{name}.png", current / f"{name}.png"
        if not old_path.exists():
            raise SystemExit(f"Missing baseline: {old_path}")
        with Image.open(old_path) as old, Image.open(new_path) as new:
            if old.size != new.size:
                problems.append(f"{name}: image sizes differ ({old.size} vs {new.size})")
                continue
            difference = ImageChops.difference(old.convert("RGB"), new.convert("RGB"))
            if difference.getbbox():
                problems.append(f"{name}: visual differences detected")
                difference.save(current / f"{name}-difference.png")
    return problems


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("baseline", "compare"))
    parser.add_argument("--url", required=True, help="Local Machine Comparison page URL")
    args = parser.parse_args()
    destination = ROOT / args.mode
    capture(args.url, destination)
    if args.mode == "compare":
        problems = compare(ROOT / "baseline", destination)
        if problems:
            raise SystemExit("\n".join(problems) + "\nReview difference images in " + str(destination))
        print("No pixel differences at desktop and mobile sizes.")
    else:
        print("Baseline saved in " + str(destination))


if __name__ == "__main__":
    main()
