# Every Item brand guide: "Sunset"

## Icon

A white paper receipt framed by four white camera-viewfinder corner brackets, like scanning a
document with the iPhone camera, on a rounded square filled with the Sunset gradient (orange
top-left to hot pink bottom-right). Flat, no shadows, no text.

- **Receipt:** rounded top corners and a zigzag torn bottom edge (6 teeth), scaled to 72% of
  the original concept and nudged slightly below centre so it looks optically centred.
- **Receipt content:** three grey item lines (`#D3D3D3`), a faint dotted rule, then a
  **total line**: a short grey label (`#B9B9B9`) on the left and a bold bar in the Sunset
  gradient on the right. The gradient total bar is the icon's one colour accent.
- **Brackets:** four L-shaped corners, stroke 50 on the 1024 grid (about 3 px at 60 px),
  round caps and softly rounded elbows. Keep clear space between the receipt and the brackets.
- **Small-size variant** (`static/favicon.svg`, `favicon-32.png`, site header and footer
  logo): at 16-32 px the item lines and total row turn to mush, so this variant drops them.
  It has a bigger receipt, heavier brackets (stroke 88), three deep teeth and a single
  gradient total bar. Use the full icon at 48 px and above.
- The previous receipt-and-checkmark icon (used until Oct 2026) is archived in `brand/archive/` for
  reference only. Don't use it.

| File | Use |
| --- | --- |
| `brand/icon.svg` | Master vector with rounded corners and transparent corners (website, docs, press) |
| `static/favicon.svg` | Simplified small-size variant, used as the site favicon and the header and footer logo |
| `brand/app-icon-full-bleed.svg` | Square, no rounded corners, no transparency (source for the App Store icon) |
| `brand/app-icon-1024.png` | **App Store icon**: 1024x1024 PNG, RGB with no alpha channel. iOS rounds the corners itself, so don't add them |
| `static/apple-touch-icon.png` | 180x180, full-bleed (iOS home-screen bookmark) |
| `static/favicon-32.png` | 32x32 PNG favicon fallback (small-size variant) |
| `static/og-image.png` | 1200x630 social-share image (icon + wordmark + tagline) |
| `brand/icon_concept_sunset.jpg` | Original AI-generated concept (reference only; don't ship it) |
| `brand/archive/` | Old checkmark icon (`icon-checkmark.svg`, `app-icon-checkmark-full-bleed.svg`, `app-icon-checkmark-1024.png`), retired |

Regenerate everything with `bash scripts/make_images.sh` (which runs `scripts/make_brand.py --png`).

> **Originality check before trademark use.** The receipt was recreated from an
> **AI-generated concept**, and receipt and scan-viewfinder icons are common. Before you file a
> trademark or rely on the icon as a distinctive mark, run a reverse-image search and
> a USPTO design-mark search, and compare it with other receipt and warranty apps in the
> App Store. If it's too close to an existing mark, change it.

**Icon usage**
- Keep clear space around the icon of at least 1/8 of its width.
- Minimum size: 16 px (favicon). Below 48 px use the small-size variant (`static/favicon.svg`).
- Only use the supplied files. Don't recolour, rotate, stretch, outline or add effects or shadows.
- Use it on white, `--bg` (#FBFAF7) or dark (#111416) backgrounds. Don't put it on busy photos or on the Sunset gradient itself.

## Wordmark

"Every Item" set in **Inter Bold** (weight 700, optical size 32) with -0.02em tracking,
converted to outlines so no font install is needed. Inter is free under the SIL Open Font License.

| File | Use |
| --- | --- |
| `brand/wordmark.svg` | Dark ink (#1C1F23) on light backgrounds |
| `brand/wordmark-white.svg` | White, for dark or photo backgrounds |
| `brand/wordmark-on-gradient.svg` | White wordmark on the Sunset gradient tile |
| `static/wordmark.svg` | Copy used by the site header and footer (a CSS mask, so it follows light and dark mode) |

Lockup: icon on the left, wordmark to the right, wordmark cap height about 45% of the icon height, gap about 30% of the icon height.

## Colours

| Name | Hex | Use |
| --- | --- | --- |
| Sunset Orange | `#FD6404` | Gradient start, sampled from the concept. Icon and decoration only |
| Sunset Pink | `#FD1F69` | Gradient end, sampled from the concept. Icon and decoration only |
| Deep Orange | `#B93D00` | Start of the text-safe "deep" gradient |
| Deep Pink | `#C8104F` | End of the text-safe "deep" gradient |
| Raspberry (primary solid) | `#BE1250` | Links, eyebrows, solid fallback for the gradient |
| Raspberry Dark | `#9F1239` | Hover, strong accent text |
| Blush | `#FFF1EA` | Soft accent background (quick-answer box, icon tiles) |
| Ink | `#1C1F23` | Body text |
| Muted | `#555B63` | Secondary text |
| Paper | `#FBFAF7` / `#F1EFE8` | Page / alternate section background |
| Dark mode accent: Coral | `#FF8A6B` | Links and accents on dark backgrounds |
| Dark mode accent strong: Peach | `#FFB59A` | Hover and strong accent on dark |
| Dark mode soft | `#3A1A1F` | Soft accent background on dark |

**Gradients**
- Vivid: `linear-gradient(135deg, #FD6404, #FD1F69)` for the icon, the 3px header rule, the featured price-card border and the og-image bar. **Never put text on it.** White on `#FD6404` is only 3.0:1.
- Deep: `linear-gradient(135deg, #B93D00, #C8104F)` (solid fallback `#BE1250`) for the "Coming soon" badge, `.button`, checklist bullets and the guide CTA box. It is safe for white text: 5.6:1 at the orange end, 5.9:1 in the middle and 5.8:1 at the pink end.

**Contrast (WCAG 2.1 AA, 4.5:1 for body text)**

| Pair | Ratio |
| --- | --- |
| White on Deep Orange `#B93D00` / Deep Pink `#C8104F` | 5.63 / 5.76 |
| White on `#BE1250` (solid fallback) | 6.19 |
| Raspberry `#BE1250` on `#FBFAF7` / `#F1EFE8` / `#FFF1EA` | 5.93 / 5.38 / 5.61 |
| Coral `#FF8A6B` on `#111416` / `#1C2125` / `#3A1A1F` | 8.01 / 7.03 / 6.75 |
| White on `#FD6404` / `#FD1F69` (vivid) | 3.00 / 3.77: **fails**, so don't use it for text |

## Typography

The website uses the system font stack: `-apple-system, BlinkMacSystemFont, "SF Pro Text", "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif`.
That's SF Pro on Apple devices. There are no web-font downloads and no paid fonts.
The wordmark is Inter (OFL), outlined.

## Do

- Keep it calm: mostly paper and ink, with the gradient as an accent. One gradient element per view is plenty.
- Say what the app actually does: on-device storage, return and warranty reminders, no account.
- Use "Coming soon to the App Store" as plain text until the app is live.

## Don't

- Don't use Apple's App Store badge, the Apple logo, or other store or retailer logos, unless the app is live and you follow Apple's marketing guidelines.
- **Never claim end-to-end encryption**, "military-grade" security, or anything the app doesn't do. Describe protections accurately: data stays on the iPhone, protected by iOS Data Protection, with an optional Face ID lock.
- Don't put text on the vivid gradient, recolour the icon, or use the gradient as a full-page background.
- Don't mix in other bright accent colours, such as the old teal (#0F766E).
