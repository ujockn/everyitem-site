# Every Item brand guide: "Receipt E"

## Icon

**"Receipt E"** (adopted October 2026). A white paper receipt cut into the shape of a capital
**E** (two notches from the right edge), with a zigzag torn bottom edge, two grey item lines,
a grey "total" label and a Sunset-gradient amount. It sits on a **charcoal** (`#1C1D21`)
square with a tight Sunset halo (orange to pink) that hugs the E outline and fades quickly
to charcoal. The receipt is the product and the E is the name: **E**very Item. No text.

The previous icon (receipt with a checkmark on the Sunset gradient) is archived in
`brand/archive/*-checkmark.*`, and the earlier corner-bracket concept in
`brand/archive/*brackets*`. Concept explorations live in `brand/mockups/` (local only, not committed).

| File | Use |
| --- | --- |
| `brand/icon.svg` | Master vector with rounded corners and transparent corners (website, docs, press) |
| `static/favicon.svg` | Same file, used as the site favicon and header logo |
| `brand/app-icon-full-bleed.svg` | Square, no rounded corners, no transparency (source for the App Store icon) |
| `brand/app-icon-1024.png` | **App Store icon**: 1024x1024 PNG, RGB with no alpha channel. iOS rounds the corners itself, so don't add them |
| `static/apple-touch-icon.png` | 180x180, full-bleed (iOS home-screen bookmark) |
| `static/favicon-32.png` | 32x32 PNG favicon fallback |
| `static/og-image.png` | 1200x630 social-share image on charcoal (icon + white wordmark + tagline), source `scripts/og-image.html` |
| `brand/archive/*-checkmark.*` | Retired checkmark icon and its original AI concept art (reference only; don't ship) |

Regenerate everything with `bash scripts/make_images.sh` (which runs `scripts/make_brand.py --png`).

> **Originality check before trademark use.** In October 2026 we compared the App Store
> icons of Sortly, Encircle, HomeZada, Nest Egg, Itemtopia, Under My Roof, Warranty Keeper,
> Expensify, Smart Receipts, Shoeboxed and Receipt Hog. They lean on houses, boxes, plain
> receipts, shields and bare single letters on blue, green, purple or orange tiles; none uses
> a receipt shaped like a letter, or charcoal with a glow. That is a quick visual check, not
> legal clearance. Before you file a
> trademark or rely on the icon as a distinctive mark, run a reverse-image search and
> a USPTO design-mark search, and compare it with other receipt and warranty apps in the
> App Store. If it's too close to an existing mark, change it.

**Icon usage**
- Keep clear space around the icon of at least 1/8 of its width.
- Minimum size: 16 px (favicon). Below 24 px the receipt lines and halo get soft; the E shape still reads.
- Only use the supplied files. Don't recolour, rotate, stretch or outline it. The halo is part of
  the icon; on the website a soft coral glow *around the tile* (box-shadow) is allowed, nothing else.
- Use it on white, `--bg` (#FBFAF7), charcoal (#1C1D21) or dark-mode backgrounds. Don't put it on busy photos or on the Sunset gradient.

## Wordmark

"Every Item" set in **Inter Bold** (weight 700, optical size 32) with -0.02em tracking,
converted to outlines so no font install is needed. Ink is charcoal `#1C1D21`. On the site
header, hero and footer (charcoal) the wordmark is white. Inter is free under the SIL Open Font License.

| File | Use |
| --- | --- |
| `brand/wordmark.svg` | Charcoal ink (#1C1D21) on light backgrounds |
| `brand/wordmark-white.svg` | White, for dark or photo backgrounds |
| `brand/wordmark-on-gradient.svg` | White wordmark on the Sunset gradient tile |
| `static/wordmark.svg` | Copy used by the site header and footer (a CSS mask, so it follows light and dark mode) |

Lockup: icon on the left, wordmark to the right, wordmark cap height about 45% of the icon height, gap about 30% of the icon height.

## Colours

| Name | Hex | Use |
| --- | --- | --- |
| **Charcoal** | `#1C1D21` | Icon background; site header, hero, guide CTA box and footer; wordmark and body-text ink |
| Charcoal raised | `#26282E` | Raised surfaces on charcoal |
| On-charcoal text | `#FFFFFF` / `#B9BDC6` | Headings / secondary text on charcoal (16.8:1 / 8.9:1) |
| Sunset Orange | `#FD6404` | Gradient start. Icon, halo and decoration only |
| Sunset Coral | `#FD4237` | Gradient midpoint (site gradient rules and glows). Decoration only |
| Sunset Pink | `#FD1F69` | Gradient end. Icon, halo and decoration only |
| Deep Orange | `#B93D00` | Start of the text-safe "deep" gradient |
| Deep Pink | `#C8104F` | End of the text-safe "deep" gradient |
| Raspberry (primary solid) | `#BE1250` | Links, eyebrows, solid fallback for the gradient |
| Raspberry Dark | `#9F1239` | Hover, strong accent text |
| Blush | `#FFF1EA` | Soft accent background (quick-answer box, icon tiles) |
| Ink | `#1C1D21` | Body text (same as Charcoal) |
| Muted | `#555B63` | Secondary text |
| Paper | `#FBFAF7` / `#F1EFE8` | Page / alternate section background (body content stays on paper for readability) |
| Dark-mode page | `#131417` / `#18191D` / `#222328` | Dark-mode background / alternate / card surface |
| Coral (accent on dark) | `#FF8A6B` | Links, eyebrows and accents on charcoal and in dark mode (7.3:1 on charcoal) |
| Dark mode accent strong: Peach | `#FFB59A` | Hover and strong accent on dark |
| Dark mode soft | `#3A1A1F` | Soft accent background on dark |

**Gradients**
- Vivid: `linear-gradient(135deg, #FD6404, #FD4237, #FD1F69)` for the icon halo, the 3px rules under the header and over the footer, the featured price-card border and the og-image bar. **Never put text on it.** White on `#FD6404` is only 3.0:1.
- Sunrise glow: a radial coral-to-pink glow (about 30% opacity) fading to charcoal, used behind the hero phone, in the guide CTA box and behind the og-image icon. It echoes the icon's halo. Keep it subtle and never put body text over the bright part.
- Deep: `linear-gradient(135deg, #B93D00, #C8104F)` (solid fallback `#BE1250`) for the "Coming soon" badge, `.button`, checklist bullets and the guide CTA box. It is safe for white text: 5.6:1 at the orange end, 5.9:1 in the middle and 5.8:1 at the pink end.

**Contrast (WCAG 2.1 AA, 4.5:1 for body text)**

| Pair | Ratio |
| --- | --- |
| White on Deep Orange `#B93D00` / Deep Pink `#C8104F` | 5.63 / 5.76 |
| White on `#BE1250` (solid fallback) | 6.19 |
| White / `#B9BDC6` / Coral `#FF8A6B` on Charcoal `#1C1D21` | 16.84 / 8.95 / 7.30 |
| Body ink `#1C1D21` on Paper `#FBFAF7` | 16.13 |
| Raspberry `#BE1250` on `#FBFAF7` / `#F1EFE8` / `#FFF1EA` | 5.93 / 5.38 / 5.61 |
| Coral `#FF8A6B` on `#131417` / `#222328` / `#3A1A1F` | 7.98 / 6.80 / 6.75 |
| White on `#FD6404` / `#FD1F69` (vivid) | 3.00 / 3.77: **fails**, so don't use it for text |

## Typography

The website uses the system font stack: `-apple-system, BlinkMacSystemFont, "SF Pro Text", "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif`.
That's SF Pro on Apple devices. There are no web-font downloads and no paid fonts.
The wordmark is Inter (OFL), outlined.

## Do

- Keep it calm: charcoal frames the page (header, hero, footer), content sits on paper, and the Sunset gradient is an accent. One glow per view is plenty.
- Say what the app actually does: on-device storage, return and warranty reminders, no account.
- Use "Coming soon to the App Store" as plain text until the app is live.

## Don't

- Don't use Apple's App Store badge, the Apple logo, or other store or retailer logos, unless the app is live and you follow Apple's marketing guidelines.
- **Never claim end-to-end encryption**, "military-grade" security, or anything the app doesn't do. Describe protections accurately: data stays on the iPhone, protected by iOS Data Protection, with an optional Face ID lock.
- Don't put text on the vivid gradient, recolour the icon, or use the gradient or a glow as a full-page background.
- Don't mix in other bright accent colours, such as the old teal (#0F766E).
