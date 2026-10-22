#!/usr/bin/env python3
"""Generate the Every Item "Sunset" brand assets.

    python3 scripts/make_brand.py          SVGs only (no extra dependencies besides fontTools)
    python3 scripts/make_brand.py --png    also renders the PNGs (needs `pip install playwright pillow`
                                           and Google Chrome or `playwright install chromium`)

Writes:
  brand/icon.svg                     rounded-square icon (transparent corners), master vector
  static/favicon.svg                 simplified small-size variant (favicon, site header/footer logo)
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
TOTAL_LABEL = "#B9B9B9"
INTER = Path("/usr/share/fonts/truetype/sand-box/google/Inter/Inter-VariableFont_opsz,wght.ttf")

# Icon geometry on a 1024 grid. "Scan" icon (version A, chosen Oct 2026): the receipt from
# the original concept, scaled to 72% and framed by four white camera-viewfinder corner
# brackets. The old checkmark icon is kept in brand/archive/.
RX = 229  # ~22.4%, close to the iOS corner shape; only used for the web/brand icon
CX = 512
BRACKET_W = 50  # stroke weight; ~3 px at 60 px home-screen size


def receipt_path(cx, top, w, h, s, teeth=6, tooth=38):
    """Receipt outline: rounded top corners, zigzag torn bottom edge (right to left)."""
    x0, x1 = cx - w / 2, cx + w / 2
    bottom, peak, r = top + h, top + h - tooth * s, 26 * s
    tw = w / teeth
    d = [f"M{x0:.1f} {top + r:.1f}", f"Q{x0:.1f} {top:.1f} {x0 + r:.1f} {top:.1f}", f"H{x1 - r:.1f}",
         f"Q{x1:.1f} {top:.1f} {x1:.1f} {top + r:.1f}", f"V{bottom:.1f}"]
    for i in range(teeth):
        xr = x1 - i * tw
        d += [f"L{xr - tw / 2:.1f} {peak:.1f}", f"L{xr - tw:.1f} {bottom:.1f}"]
    d.append("Z")
    return " ".join(d)


def corner_brackets(x0, y0, x1, y1, arm, sw, r):
    """Four L-shaped viewfinder corners with rounded elbows and round caps."""
    ps = []
    for cx, cy, dx, dy in [(x0, y0, 1, 1), (x1, y0, -1, 1), (x1, y1, -1, -1), (x0, y1, 1, -1)]:
        ps.append(f"M{cx:.1f} {cy + dy * arm:.1f}V{cy + dy * r:.1f}"
                  f"Q{cx:.1f} {cy:.1f} {cx + dx * r:.1f} {cy:.1f}H{cx + dx * arm:.1f}")
    return (f'<path d="{" ".join(ps)}" fill="none" stroke="#fff" stroke-width="{sw}" '
            f'stroke-linecap="round" stroke-linejoin="round"/>')


def icon_body():
    """Full-detail icon: receipt with three item lines, a dotted rule and a total row."""
    s = 0.72
    w, h = 464 * s, 600 * s
    top = 512 - h / 2 + 6  # optical centring (the torn edge makes the bottom look lighter)
    x0, x1 = CX - w / 2, CX + w / 2
    lx, rx = x0 + 72 * s, x1 - 72 * s
    y = lambda off: top + off * s
    sw = 26 * s
    items = (f"M{lx:.1f} {y(98):.1f}H{lx + 320 * s:.1f}M{lx:.1f} {y(158):.1f}H{lx + 272 * s:.1f}"
             f"M{lx:.1f} {y(218):.1f}H{lx + 196 * s:.1f}")
    return "\n".join([
        f'  <path d="{receipt_path(CX, top, w, h, s)}" fill="#fff" stroke="#fff" stroke-width="{10 * s:.1f}" stroke-linejoin="round"/>',
        f'  <path d="{items}" stroke="{RECEIPT_LINE}" stroke-width="{sw:.1f}" stroke-linecap="round"/>',
        f'  <path d="M{lx:.1f} {y(334):.1f}H{rx:.1f}" stroke="{RECEIPT_LINE}" stroke-width="{10 * s:.1f}" stroke-linecap="round" stroke-dasharray="{2 * s:.1f} {22 * s:.1f}"/>',
        f'  <path d="M{lx:.1f} {y(410):.1f}H{lx + 110 * s:.1f}" stroke="{TOTAL_LABEL}" stroke-width="{sw:.1f}" stroke-linecap="round"/>',
        f'  <path d="M{rx - 128 * s:.1f} {y(410):.1f}H{rx:.1f}" stroke="url(#ei-sunset)" stroke-width="{40 * s:.1f}" stroke-linecap="round"/>',
        "  " + corner_brackets(x0 - 86, top - 74, x1 + 86, top + h + 64, arm=116, sw=BRACKET_W, r=58),
    ])


def favicon_body():
    """Small-size variant (16-32 px): same brackets and receipt shape, no fine lines.
    Bigger receipt, heavier brackets, three deep teeth, and one bold gradient total bar."""
    s = 0.74
    w, h = 464 * s, 600 * s
    top = 512 - h / 2 + 4
    x0, x1 = CX - w / 2, CX + w / 2
    bar_y = top + h * 0.40
    return "\n".join([
        f'  <path d="{receipt_path(CX, top, w, h, s, teeth=3, tooth=90)}" fill="#fff" stroke="#fff" stroke-width="12" stroke-linejoin="round"/>',
        f'  <path d="M{x0 + 80:.1f} {bar_y:.1f}H{x1 - 80:.1f}" stroke="url(#ei-sunset)" stroke-width="64" stroke-linecap="round"/>',
        "  " + corner_brackets(x0 - 100, top - 84, x1 + 100, top + h + 74, arm=128, sw=88, r=64),
    ])


def icon_svg(full_bleed=False, size=None, small=False):
    rx = 0 if full_bleed else RX
    dims = f' width="{size}" height="{size}"' if size else ""
    body = favicon_body() if small else icon_body()
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1024 1024"{dims}>
  <title>Every Item</title>
  <defs>
    <linearGradient id="ei-sunset" x1="0" y1="0" x2="1024" y2="1024" gradientUnits="userSpaceOnUse">
      <stop offset=".1" stop-color="{SUNSET_ORANGE}"/>
      <stop offset=".9" stop-color="{SUNSET_PINK}"/>
    </linearGradient>
  </defs>
  <rect width="1024" height="1024" rx="{rx}" fill="url(#ei-sunset)"/>
{body}
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
    # Site favicon / header logo is shown at 16-32 px, so it uses the simplified variant.
    (STATIC / "favicon.svg").write_text(icon_svg(small=True))
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
        small = icon_svg(size=1024, small=True)
        shot(full, (1024, 1024), tmp / "full.png", False)
        shot(small, (1024, 1024), tmp / "small.png", True)
        shot((ROOT / "scripts" / "og-image.html").as_uri(), (1200, 630), STATIC / "og-image.png", False)
        browser.close()

    full_img = Image.open(tmp / "full.png").convert("RGB")  # App Store: no alpha channel
    full_img.save(BRAND / "app-icon-1024.png", optimize=True)
    full_img.resize((180, 180), Image.LANCZOS).save(STATIC / "apple-touch-icon.png", optimize=True)
    Image.open(tmp / "small.png").convert("RGBA").resize((32, 32), Image.LANCZOS).save(
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
