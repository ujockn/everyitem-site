#!/usr/bin/env python3
"""Generate the Every Item brand assets ("Receipt E" icon on charcoal with a Sunset halo).

    python3 scripts/make_brand.py          SVGs only (no extra dependencies besides fontTools)
    python3 scripts/make_brand.py --png    also renders the PNGs (needs `pip install playwright pillow`
                                           and Google Chrome or `playwright install chromium`)

Writes:
  brand/icon.svg                     rounded-square icon (transparent corners), master vector
  static/favicon.svg                 same as brand/icon.svg (used on the website)
  brand/app-icon-full-bleed.svg      square, no rounded corners, no transparency
  brand/app-icon-1024.png            App Store icon: 1024x1024 RGB, no alpha (iOS rounds corners itself)
  brand/wordmark.svg                 "Every Item" in Inter Bold, outlined, dark (#1C1D21)
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

# Sunset gradient endpoints (sampled from the original concept art, now in brand/archive/).
SUNSET_ORANGE = "#FD6404"
SUNSET_CORAL = "#FD4237"
SUNSET_PINK = "#FD1F69"
CHARCOAL = "#1C1D21"   # icon background and the site's dark surfaces
INK = "#1C1D21"        # wordmark ink (same as the charcoal)
RECEIPT_LINE = "#D3D3D3"
RECEIPT_TOTAL = "#B9B9B9"
INTER = Path("/usr/share/fonts/truetype/sand-box/google/Inter/Inter-VariableFont_opsz,wght.ttf")

# Icon geometry on a 1024 grid.
RX = 229  # ~22.4%, close to the iOS corner shape; only used for the web/brand icon


def receipt_e_path():
    """The receipt cut into an E: two notches from the right, zigzag torn bottom edge."""
    x0, x1, xm, sx = 262, 762, 692, 432       # paper left/right, middle-arm right, spine right
    y0, n1a, n1b, n2a, n2b, yb = 196, 362, 450, 574, 662, 828
    teeth, depth = 7, 40
    d = [f"M{x0} {y0 + 30}", f"Q{x0} {y0} {x0 + 30} {y0}", f"H{x1 - 30}", f"Q{x1} {y0} {x1} {y0 + 30}",
         f"V{n1a}", f"H{sx}", f"V{n1b}", f"H{xm}", f"V{n2a}", f"H{sx}", f"V{n2b}", f"H{x1}", f"V{yb}"]
    tw = (x1 - x0) / teeth
    for i in range(teeth):  # torn edge, right to left
        xr = x1 - i * tw
        d += [f"L{xr - tw / 2:.1f} {yb - depth}", f"L{xr - tw:.1f} {yb}"]
    d.append("Z")
    return " ".join(d)


def icon_svg(full_bleed=False, size=None):
    """'Receipt E' on charcoal with a tight Sunset halo (concept A3, chosen Oct 2026)."""
    rx = 0 if full_bleed else RX
    dims = f' width="{size}" height="{size}"' if size else ""
    d = receipt_e_path()
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1024 1024"{dims}>
  <title>Every Item</title>
  <defs>
    <linearGradient id="ei-sunset" x1="0" y1="0" x2="1024" y2="1024" gradientUnits="userSpaceOnUse">
      <stop offset=".1" stop-color="{SUNSET_ORANGE}"/>
      <stop offset=".9" stop-color="{SUNSET_PINK}"/>
    </linearGradient>
    <filter id="ei-halo" x="-30%" y="-30%" width="160%" height="160%">
      <feMorphology in="SourceGraphic" operator="dilate" radius="10" result="d"/>
      <feGaussianBlur in="d" stdDeviation="40" result="wide"/>
      <feGaussianBlur in="d" stdDeviation="12" result="tight"/>
      <feMerge><feMergeNode in="wide"/><feMergeNode in="wide"/><feMergeNode in="tight"/></feMerge>
    </filter>
    <clipPath id="ei-tile"><rect width="1024" height="1024" rx="{rx}"/></clipPath>
  </defs>
  <g clip-path="url(#ei-tile)">
    <rect width="1024" height="1024" fill="{CHARCOAL}"/>
    <path d="{d}" fill="url(#ei-sunset)" stroke="url(#ei-sunset)" stroke-width="14" stroke-linejoin="round" filter="url(#ei-halo)"/>
    <path d="{d}" fill="#fff" stroke="#fff" stroke-width="14" stroke-linejoin="round"/>
    <path d="M328 280H642M328 512H542" stroke="{RECEIPT_LINE}" stroke-width="30" stroke-linecap="round"/>
    <path d="M328 722H432" stroke="{RECEIPT_TOTAL}" stroke-width="30" stroke-linecap="round"/>
    <path d="M552 722H696" stroke="url(#ei-sunset)" stroke-width="44" stroke-linecap="round"/>
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
