#!/usr/bin/env python3
"""Generate the Every Item "Sunset" brand assets.

    python3 scripts/make_brand.py          SVGs only (no extra dependencies besides fontTools)
    python3 scripts/make_brand.py --png    also renders the PNGs (needs `pip install playwright pillow`
                                           and Google Chrome or `playwright install chromium`)

Writes:
  brand/icon.svg                     rounded-square icon (transparent corners), master vector
  static/favicon.svg                 same as brand/icon.svg (used on the website)
  brand/app-icon-full-bleed.svg      square, no rounded corners, no transparency
  brand/app-icon-1024.png            App Store icon: 1024x1024 RGB, no alpha (iOS rounds corners itself)
  brand/wordmark.svg                 "Every Item" in Inter Bold, outlined, dark (#1C1F23)
  brand/wordmark-white.svg           same, white (for dark or gradient backgrounds)
  brand/wordmark-on-gradient.svg     white wordmark on the Sunset gradient
  static/wordmark.svg                copy of brand/wordmark.svg for the site header (CSS mask)
  static/favicon-32.png, static/apple-touch-icon.png (180x180, full-bleed), static/og-image.png (1200x630)

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

# Gradient endpoints sampled from brand/icon_concept_sunset.jpg (12x12 px averages in the
# flat top-left and bottom-right areas of the tile).
SUNSET_ORANGE = "#FD6404"
SUNSET_PINK = "#FD1F69"
INK = "#1C1F23"
RECEIPT_LINE = "#D3D3D3"
INTER = Path("/usr/share/fonts/truetype/sand-box/google/Inter/Inter-VariableFont_opsz,wght.ttf")

# Icon geometry on a 1024 grid (traced from the concept, shadows removed).
RX = 229  # ~22.4%, close to the iOS corner shape; only used for the web/brand icon


def receipt_path():
    x0, x1, top, bottom, peak, r = 280, 744, 196, 796, 758, 26
    teeth = 6
    w = (x1 - x0) / teeth
    d = [f"M{x0} {top + r}", f"Q{x0} {top} {x0 + r} {top}", f"H{x1 - r}",
         f"Q{x1} {top} {x1} {top + r}", f"V{bottom}"]
    for i in range(teeth):  # zigzag torn edge, right to left
        xr = x1 - i * w
        d.append(f"L{xr - w / 2:.1f} {peak}")
        d.append(f"L{xr - w:.1f} {bottom}")
    d.append("Z")
    return " ".join(d)


def icon_svg(full_bleed=False, size=None):
    rx = 0 if full_bleed else RX
    dims = f' width="{size}" height="{size}"' if size else ""
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1024 1024"{dims}>
  <title>Every Item</title>
  <defs>
    <linearGradient id="ei-sunset" x1="0" y1="0" x2="1024" y2="1024" gradientUnits="userSpaceOnUse">
      <stop offset=".1" stop-color="{SUNSET_ORANGE}"/>
      <stop offset=".9" stop-color="{SUNSET_PINK}"/>
    </linearGradient>
  </defs>
  <rect width="1024" height="1024" rx="{rx}" fill="url(#ei-sunset)"/>
  <path d="{receipt_path()}" fill="#fff" stroke="#fff" stroke-width="10" stroke-linejoin="round"/>
  <path d="M352 294H672M352 354H624M352 414H548" stroke="{RECEIPT_LINE}" stroke-width="26" stroke-linecap="round"/>
  <path d="M404 562L484 642L626 498" fill="none" stroke="url(#ei-sunset)" stroke-width="58" stroke-linecap="round" stroke-linejoin="round"/>
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
    (STATIC / "favicon.svg").write_text(icon_svg())
    (BRAND / "app-icon-full-bleed.svg").write_text(icon_svg(full_bleed=True))
    (BRAND / "wordmark.svg").write_text(wordmark_svg(INK)[0])
    (STATIC / "wordmark.svg").write_text(wordmark_svg(INK)[0])  # used as a CSS mask in the header
    (BRAND / "wordmark-white.svg").write_text(wordmark_svg("#FFFFFF")[0])
    (BRAND / "wordmark-on-gradient.svg").write_text(wordmark_svg("#FFFFFF", bg=True)[0])
    print("wrote brand/*.svg and static/favicon.svg")


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
        rounded = icon_svg(size=1024)
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
