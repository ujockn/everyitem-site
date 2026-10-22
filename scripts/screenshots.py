#!/usr/bin/env python3
"""Take screenshots of the built site (optional; needs `pip install playwright`
and either `playwright install chromium` or Google Chrome installed).

    python3 build.py && python3 build.py --drafts && python3 scripts/screenshots.py

Saves PNGs into screenshots/. The guide screenshot uses the draft template from
preview/ because no real guides are published yet.
"""
import functools
import http.server
import shutil
import threading
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
SHOTS = ROOT / "screenshots"
SHOTS.mkdir(exist_ok=True)


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


def serve(directory, port):
    handler = functools.partial(QuietHandler, directory=str(directory))
    server = http.server.ThreadingHTTPServer(("127.0.0.1", port), handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server


SHOTS_TO_TAKE = [
    # (file name, server, path, viewport)
    ("home-desktop.png", "dist", "/", (1280, 800)),
    ("home-mobile.png", "dist", "/", (390, 844)),
    ("guide-template-desktop.png", "preview", "/guides/template/", (1280, 800)),
    ("guide-template-mobile.png", "preview", "/guides/template/", (390, 844)),
    ("guides-index-desktop.png", "dist", "/guides/", (1280, 800)),
    ("privacy-desktop.png", "dist", "/privacy/", (1280, 800)),
]

if __name__ == "__main__":
    servers = {"dist": serve(ROOT / "dist", 8701), "preview": serve(ROOT / "preview", 8702)}
    chrome = shutil.which("google-chrome") or shutil.which("chromium")
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=chrome) if chrome else p.chromium.launch()
        for name, which, path, (w, h) in SHOTS_TO_TAKE:
            page = browser.new_page(viewport={"width": w, "height": h},
                                    device_scale_factor=2 if w < 500 else 1)
            port = servers[which].server_address[1]
            page.goto(f"http://127.0.0.1:{port}{path}", wait_until="networkidle")
            page.screenshot(path=str(SHOTS / name), full_page=True)
            page.close()
            print("saved", SHOTS / name)
        browser.close()
