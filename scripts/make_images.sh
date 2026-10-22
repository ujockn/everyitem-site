#!/usr/bin/env bash
# Re-create the PNG images in static/ from static/favicon.svg and scripts/og-image.html.
# Only needed if you change the logo or the social-share image. Requires Google Chrome.
# Run from the project folder:  bash scripts/make_images.sh
set -euo pipefail
cd "$(dirname "$0")/.."
ROOT="$(pwd)"
CHROME="${CHROME:-$(command -v google-chrome || command -v chromium || echo '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome')}"
TMP="$(mktemp -d)"
sed "s#file:///workspace/everyitem-site#file://$ROOT#g" scripts/og-image.html > "$TMP/og.html"
cat > "$TMP/icon.html" <<HTML
<!DOCTYPE html><html><head><style>html,body{margin:0;background:#0f766e;overflow:hidden}img{display:block;width:100vw;height:100vh}</style></head><body><img src="file://$ROOT/static/favicon.svg"></body></html>
HTML
run() { "$CHROME" --headless=new --no-sandbox --disable-gpu --hide-scrollbars --allow-file-access-from-files "$@" 2>/dev/null; }
run --window-size=1200,630 --screenshot="$ROOT/static/og-image.png" "file://$TMP/og.html"
run --window-size=180,180 --screenshot="$ROOT/static/apple-touch-icon.png" "file://$TMP/icon.html"
run --window-size=32,32 --screenshot="$ROOT/static/favicon-32.png" "file://$TMP/icon.html"
echo "Updated static/og-image.png, static/apple-touch-icon.png, static/favicon-32.png"
