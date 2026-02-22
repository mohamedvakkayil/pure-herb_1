#!/usr/bin/env python3
"""
Capture the app in a browser so the agent can inspect it.
Run the Django server first in another terminal:
  python manage.py runserver
Then run:
  python scripts/capture_page.py
Screenshots are saved in the project root for the agent to read.
"""
import sys
from pathlib import Path

# Project root (parent of scripts/)
ROOT = Path(__file__).resolve().parent.parent

def main():
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("Playwright not installed. Run:")
        print("  pip install playwright")
        print("  playwright install")
        sys.exit(1)

    url = "http://127.0.0.1:8000/"
    out_main = ROOT / "live_check_main.png"
    out_modal = ROOT / "live_check_modal.png"

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1280, "height": 800})
        try:
            page.goto(url, wait_until="networkidle", timeout=10000)
        except Exception as e:
            print(f"Could not load {url}. Is the Django server running?")
            print("  python manage.py runserver")
            print(f"  Error: {e}")
            browser.close()
            sys.exit(1)

        page.screenshot(path=str(out_main))
        print(f"Saved: {out_main.name}")

        # Open Sales modal and capture
        page.click("button[data-modal-type='sales']")
        page.wait_for_selector("#record-modal.is-open", timeout=2000)
        page.screenshot(path=str(out_modal))
        print(f"Saved: {out_modal.name}")

        browser.close()

    print("Done. Share these filenames with the agent so it can read the screenshots.")

if __name__ == "__main__":
    main()
