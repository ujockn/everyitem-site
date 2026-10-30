#!/usr/bin/env python3
"""Generate the Every Item brand assets ("Checked stack" icon, concept F3, on charcoal).

    python3 scripts/make_brand.py          SVGs only (no extra dependencies besides fontTools)
    python3 scripts/make_brand.py --png    also renders the PNGs (needs `pip install playwright pillow`
                                           and Google Chrome or `playwright install chromium`)

Writes:
  brand/icon.svg                     rounded-square icon (transparent corners), master vector, full detail
  static/icon.svg                    same as brand/icon.svg (large uses on the website: hero, og-image)
  static/favicon.svg                 simplified small-size version (favicon, header and footer logo)
  brand/app-icon-full-bleed.svg      square, no rounded corners, no transparency, full detail
  brand/app-icon-1024.png            App Store icon: 1024x1024 RGB, no alpha (iOS rounds corners itself)
  brand/wordmark.svg                 "Every Item" in Inter Bold, outlined, dark (#1C1D21)
  brand/wordmark-white.svg           same, white (for dark or gradient backgrounds)
  brand/wordmark-on-gradient.svg     white wordmark on the Sunset gradient
  static/wordmark.svg                copy of brand/wordmark.svg for the site header (CSS mask)
  static/favicon-32.png (from the simplified icon), static/apple-touch-icon.png (180x180, full-bleed,
  full detail), static/og-image.png (1200x630, source scripts/og-image.html)

The wordmark is set in Inter (SIL Open Font License) and converted to outlines, so no font
needs to be installed to display it.
"""
import argparse
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BRAND = ROOT / "brand"
STATIC = ROOT / "static"

# Sunset gradient endpoints (sampled from the original concept art, now in brand/archive/).
SUNSET_ORANGE = "#FD6404"
SUNSET_CORAL = "#FD4237"
SUNSET_PINK = "#FD1F69"
CHARCOAL = "#1C1D21"   # icon background and the site's dark surfaces
INK = "#1C1D21"        # wordmark ink (same as the charcoal)
ITEM_LINE = "#D3D3D3"  # grey item line on the white tiles
CHECK_DONE = "#C9CCD2" # small outlined checks on the white tiles
STRIP_LINE = "#E2E3E6" # faint lines at the top of the receipt strip
INTER = Path("/usr/share/fonts/truetype/sand-box/google/Inter/Inter-VariableFont_opsz,wght.ttf")

# Icon geometry on a 1024 grid (concept F3 "Checked stack", chosen Oct 2026).
RX = 229  # ~22.4%, close to the iOS corner shape; only used for the web/brand icon
STRIP = (224, 388, 200, 832)        # receipt strip (the E's upright): x0, x1, top, torn bottom
TILE_X, TILE_W, TILE_H, TILE_R = 408, 392, 168, 34
TILE_TOP_Y, TILE_MID_Y, TILE_BOT_Y = 200, 432, 664
MID_W = 300                         # the middle arm is shorter, like an E


def teeth(x0, x1, yb, n, depth):
    """Zigzag torn edge, right to left."""
    tw = (x1 - x0) / n
    d = []
    for i in range(n):
        xr = x1 - i * tw
        d += [f"L{xr - tw / 2:.1f} {yb - depth}", f"L{xr - tw:.1f} {yb}"]
    return " ".join(d)


def strip_path():
    x0, x1, y0, yb = STRIP
    return f"M{x0} {y0 + 36} Q{x0} {y0} {x0 + 36} {y0} H{x1 - 20} Q{x1} {y0} {x1} {y0 + 20} V{yb} {teeth(x0, x1, yb, 3, 30)} Z"


def icon_body(simple=False):
    """F3: a torn receipt strip is the E's upright, three item tiles are its arms, and the
    middle tile is a Sunset check (claim-ready: every item checked).

    simple=True is the small-size (favicon) version: no glow, no grey item lines, no tiny
    outlined checks on the white tiles, no lines on the strip, and a heavier white check.
    """
    mid = f'<rect x="{TILE_X}" y="{TILE_MID_Y}" width="{MID_W}" height="{TILE_H}" rx="{TILE_R}" fill="url(#ei-sunset)"'
    out = []
    if not simple:
        out.append(mid + ' filter="url(#ei-glow)" opacity=".7"/>')
    out.append(f'<path d="{strip_path()}" fill="#fff"/>')
    out.append(f'<rect x="{TILE_X}" y="{TILE_TOP_Y}" width="{TILE_W}" height="{TILE_H}" rx="{TILE_R}" fill="#fff"/>')
    out.append(f'<rect x="{TILE_X}" y="{TILE_BOT_Y}" width="{TILE_W}" height="{TILE_H}" rx="{TILE_R}" fill="#fff"/>')
    out.append(mid + "/>")
    if simple:
        out.append('<path d="M494 518 L546 566 L632 474" fill="none" stroke="#fff" stroke-width="52" '
                   'stroke-linecap="round" stroke-linejoin="round"/>')
    else:
        out.append(f'<path d="M456 284H608M456 748H580" stroke="{ITEM_LINE}" stroke-width="26" stroke-linecap="round"/>')
        for y in (306, 770):
            out.append(f'<path d="M690 {y} L716 {y + 26} L764 {y - 22}" fill="none" stroke="{CHECK_DONE}" '
                       'stroke-width="20" stroke-linecap="round" stroke-linejoin="round"/>')
        out.append(f'<path d="M276 270H336M276 330H320" stroke="{STRIP_LINE}" stroke-width="20" stroke-linecap="round"/>')
        out.append('<path d="M500 516 L548 562 L630 476" fill="none" stroke="#fff" stroke-width="40" '
                   'stroke-linecap="round" stroke-linejoin="round"/>')
    return "\n    ".join(out)


def icon_svg(full_bleed=False, size=None, simple=False):
    """'Checked stack' on charcoal (concept F3, chosen Oct 2026; replaces A3 'Receipt E')."""
    rx = 0 if full_bleed else RX
    dims = f' width="{size}" height="{size}"' if size else ""
    # The small-size version is drawn 18% larger (around the E's centre) so it fills more of a 16 px tile.
    zoom = ' transform="translate(512 516) scale(1.18) translate(-512 -516)"' if simple else ""
    glow = "" if simple else """
    <filter id="ei-glow" x="-30%" y="-30%" width="160%" height="160%">
      <feGaussianBlur in="SourceGraphic" stdDeviation="30"/>
    </filter>"""
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1024 1024"{dims}>
  <title>Every Item</title>
  <defs>
    <linearGradient id="ei-sunset" x1="0" y1="0" x2="1024" y2="1024" gradientUnits="userSpaceOnUse">
      <stop offset=".1" stop-color="{SUNSET_ORANGE}"/>
      <stop offset=".5" stop-color="{SUNSET_CORAL}"/>
      <stop offset=".9" stop-color="{SUNSET_PINK}"/>
    </linearGradient>{glow}
    <clipPath id="ei-tile"><rect width="1024" height="1024" rx="{rx}"/></clipPath>
  </defs>
  <g clip-path="url(#ei-tile)">
    <rect width="1024" height="1024" fill="{CHARCOAL}"/>
    <g{zoom}>
    {icon_body(simple)}
    </g>
  </g>
</svg>
"""


def wordmark_paths(text="Every Item", weight=700, tracking=-0.02):
    from fontTools.pens.svgPathPen import SVGPathPen
    from fontTools.pens.transformPen import TransformPen
    from fontTools.ttLib import TTFont
    from fontTools.varLib.instancer import instantiateVariableFont

    font = instantiateVariableFont(TTFont(INTER), {"wght": weight, "opsz": 32})
    upm = font["head"].unitsPerEm
    cmap, gs, hmtx = font.getBestCmap(), font.getGlyphSet(), font["hmtx"]
    asc = font["OS/2"].sCapHeight
    x, parts = 0, []
    for ch in text:
        g = cmap[ord(ch)]
        pen = SVGPathPen(gs)
        gs[g].draw(TransformPen(pen, (1, 0, 0, -1, x, asc)))
        if pen.getCommands():
            parts.append(pen.getCommands())
        x += hmtx[g][0] + tracking * upm
    x -= tracking * upm
    return " ".join(parts), x, asc, upm, font


def wordmark_svg(fill, bg=None):
    d, width, cap, upm, font = wordmark_paths()
    # vertical box: from cap height (y=0) to the bottom of "y" descender
    from fontTools.pens.boundsPen import BoundsPen
    gs = font.getGlyphSet()
    bp = BoundsPen(gs)
    gs[font.getBestCmap()[ord("y")]].draw(bp)
    descent = -bp.bounds[1]
    pad = 0 if bg is None else int(cap * 0.6)
    w, h = width + 2 * pad, cap + descent + 2 * pad
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w:.0f} {h:.0f}">', "  <title>Every Item</title>"]
    if bg:
        out += ["  <defs>",
                f'    <linearGradient id="ei-sunset" x1="0" y1="0" x2="1" y2="1">'
                f'<stop offset="0" stop-color="{SUNSET_ORANGE}"/><stop offset="1" stop-color="{SUNSET_PINK}"/></linearGradient>',
                "  </defs>",
                f'  <rect width="{w:.0f}" height="{h:.0f}" rx="{int(h * 0.22)}" fill="url(#ei-sunset)"/>']
    out.append(f'  <path transform="translate({pad} {pad})" fill="{fill}" d="{d}"/>')
    out.append("</svg>\n")
    return "\n".join(out), (w, h)


def write_svgs():
    BRAND.mkdir(exist_ok=True)
    (BRAND / "icon.svg").write_text(icon_svg())
    (STATIC / "icon.svg").write_text(icon_svg())
    (STATIC / "favicon.svg").write_text(icon_svg(simple=True))
    (BRAND / "app-icon-full-bleed.svg").write_text(icon_svg(full_bleed=True))
    (BRAND / "wordmark.svg").write_text(wordmark_svg(INK)[0])
    (STATIC / "wordmark.svg").write_text(wordmark_svg(INK)[0])  # used as a CSS mask in the header
    (BRAND / "wordmark-white.svg").write_text(wordmark_svg("#FFFFFF")[0])
    (BRAND / "wordmark-on-gradient.svg").write_text(wordmark_svg("#FFFFFF", bg=True)[0])
    print("wrote brand/*.svg, static/icon.svg and static/favicon.svg")


def render_pngs():
    from PIL import Image
    from playwright.sync_api import sync_playwright

    tmp = ROOT / ".brand-tmp"
    tmp.mkdir(exist_ok=True)
    chrome = shutil.which("google-chrome") or shutil.which("chromium")
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=chrome) if chrome else p.chromium.launch()

        def shot(svg_or_url, size, out, transparent):
            page = browser.new_page(viewport={"width": size[0], "height": size[1]})
            if svg_or_url.startswith("file://"):
                page.goto(svg_or_url, wait_until="networkidle")
            else:
                page.set_content(f"<html><body style='margin:0'>{svg_or_url}</body></html>")
            page.screenshot(path=str(out), omit_background=transparent)
            page.close()

        full = icon_svg(full_bleed=True, size=1024)
        rounded = icon_svg(size=1024, simple=True)  # favicon-32 uses the small-size version
        shot(full, (1024, 1024), tmp / "full.png", False)
        shot(rounded, (1024, 1024), tmp / "rounded.png", True)
        shot((ROOT / "scripts" / "og-image.html").as_uri(), (1200, 630), STATIC / "og-image.png", False)
        browser.close()

    full_img = Image.open(tmp / "full.png").convert("RGB")  # App Store: no alpha channel
    full_img.save(BRAND / "app-icon-1024.png", optimize=True)
    full_img.resize((180, 180), Image.LANCZOS).save(STATIC / "apple-touch-icon.png", optimize=True)
    Image.open(tmp / "rounded.png").convert("RGBA").resize((32, 32), Image.LANCZOS).save(
        STATIC / "favicon-32.png", optimize=True)
    shutil.rmtree(tmp)
    print("wrote brand/app-icon-1024.png, static/apple-touch-icon.png, static/favicon-32.png, static/og-image.png")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--png", action="store_true")
    args = ap.parse_args()
    write_svgs()
    if args.png:
        render_pngs()
