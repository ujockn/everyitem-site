#!/usr/bin/env bash
# Re-create the brand SVGs and PNG images (favicon-32, apple-touch-icon, og-image, App Store icon).
# Only needed if you change the logo or the social-share image.
# Requires: pip install playwright pillow fonttools  (and Google Chrome or `playwright install chromium`).
# Run from the project folder:  bash scripts/make_images.sh
set -euo pipefail
cd "$(dirname "$0")/.."
python3 scripts/make_brand.py --png
