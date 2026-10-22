#!/usr/bin/env python3
"""
Every Item website builder
==========================

This one small script turns the files in this folder into a finished website
inside the `dist/` folder. You never edit `dist/` by hand - it is deleted and
re-created every time you build.

    python3 build.py            Build the real site into dist/
    python3 build.py --serve    Build, then preview at http://localhost:8000
    python3 build.py --drafts   Build INCLUDING drafts into preview/ (never upload preview/)

What goes where:
    pages/*.html            Home, privacy, terms, support, 404 (HTML + a small header)
    content/guides/*.md     One Markdown file per guide -> /guides/<file-name>/
    templates/*.html        The shared page layout and the guide layout
    static/                 Copied as-is (CSS, favicon, images, robots.txt is generated)

A guide is skipped (treated as a draft) if its file name starts with "_"
or its header says `draft: true`.

The only dependency is the `markdown` package (see requirements.txt).
"""

import argparse
import hashlib
import html
import http.server
import json
import re
import shutil
import sys
from datetime import date
from pathlib import Path

try:
    import markdown
except ImportError:
    sys.exit("The 'markdown' package is missing. Run:  python3 -m pip install -r requirements.txt")

# ---------------------------------------------------------------------------
# Site settings - change these in one place
# ---------------------------------------------------------------------------
SITE = {
    "name": "Every Item",
    "url": "https://everyitem.app",          # no trailing slash
    "tagline": "Keep every receipt, warranty and return deadline.",
    "subtitle": "Receipts, Warranties & Returns",
    "owner": "Every Item",  # Real name removed for now (Oct 22, 2026); restore the owner's real name when the App Store listing goes live.
    "support_email": "support@everyitem.app",
    # TODO: set to True once the support@everyitem.app mailbox actually exists
    # and you have sent it a test email. While False, the build prints a warning
    # and the support page tells visitors the inbox opens at launch.
    "support_email_ready": True,
    "og_image": "/og-image.png",
}

ROOT = Path(__file__).parent
PAGES_DIR = ROOT / "pages"
GUIDES_DIR = ROOT / "content" / "guides"
TEMPLATES_DIR = ROOT / "templates"
STATIC_DIR = ROOT / "static"

# Order of categories on the /guides/ page. A guide's `category:` should match one.
GUIDE_CATEGORIES = [
    "Store return policies",
    "Warranty guides",
    "Organizing receipts",
    "Home inventory for insurance",
]

CTA_TITLE = "Get reminded before your return window closes"


# ---------------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------------
def read_front_matter(text, source):
    """Split a file into (settings dict, body).

    The file must start with a header like:
        ---
        title: My page
        description: One sentence for Google.
        ---
    Indented lines continue the previous value (for long text).
    """
    if not text.startswith("---"):
        sys.exit(f"ERROR: {source} must start with a '---' header block.")
    try:
        _, header, body = text.split("---", 2)
    except ValueError:
        sys.exit(f"ERROR: {source} has an opening '---' but no closing '---'.")
    meta, last_key = {}, None
    for raw in header.strip("\n").splitlines():
        if not raw.strip() or raw.strip().startswith("#"):
            continue
        if raw.startswith((" ", "\t")) and last_key:
            meta[last_key] += " " + raw.strip()
            continue
        if ":" not in raw:
            sys.exit(f"ERROR: {source}: header line '{raw}' needs a 'key: value' format.")
        key, value = raw.split(":", 1)
        last_key = key.strip().lower()
        meta[last_key] = value.strip()
    return meta, body.lstrip("\n")


def render(template_text, **values):
    """Replace {{name}} placeholders. Stops the build if one is left unfilled."""
    def swap(match):
        key = match.group(1)
        if key not in values:
            sys.exit(f"ERROR: template placeholder {{{{{key}}}}} has no value.")
        return str(values[key])
    return re.sub(r"\{\{\s*([a-z_]+)\s*\}\}", swap, template_text)


def esc(value):
    return html.escape(str(value), quote=True)


def nice_date(iso):
    d = date.fromisoformat(iso)
    return f"{d.strftime('%B')} {d.day}, {d.year}"


def json_ld(*objects):
    blocks = []
    for obj in objects:
        data = json.dumps(obj, indent=2, ensure_ascii=False).replace("</", "<\\/")
        blocks.append(f'<script type="application/ld+json">\n{data}\n</script>')
    return "\n".join(blocks)


def check_length(kind, text, low, high, source):
    if not (low <= len(text) <= high):
        print(f"  note: {source}: {kind} is {len(text)} characters (aim for {low}-{high}).")


def write(out_dir, url_path, content):
    """Write /privacy/ to out_dir/privacy/index.html (clean URLs)."""
    if url_path.endswith("/"):
        target = out_dir / url_path.lstrip("/") / "index.html"
    else:
        target = out_dir / url_path.lstrip("/")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")


# ---------------------------------------------------------------------------
# Building pages
# ---------------------------------------------------------------------------
def page_html(base, *, title, description, path, body, css_href, schema="",
              noindex=False, og_type="website", draft=False):
    canonical = SITE["url"] + path
    robots = '<meta name="robots" content="noindex">' if (noindex or draft) else ""
    banner = ('<aside class="draft-banner" aria-label="Draft notice">DRAFT PREVIEW - not '
              'part of the published site</aside>') if draft else ""
    return render(
        base,
        title=esc(title),
        description=esc(description),
        canonical=esc(canonical),
        og_type=og_type,
        og_image=esc(SITE["url"] + SITE["og_image"]),
        site_name=esc(SITE["name"]),
        robots=robots,
        css_href=css_href,
        schema=schema,
        draft_banner=banner,
        body=body,
        year=date.today().year,
        owner=esc(SITE["owner"]),
    )


def build_static_pages(base, css_href, out_dir):
    built = []
    for src in sorted(PAGES_DIR.glob("*.html")):
        meta, body = read_front_matter(src.read_text(encoding="utf-8"), src)
        for key in ("title", "description", "path"):
            if key not in meta:
                sys.exit(f"ERROR: {src} is missing '{key}:' in its header.")
        body = render(body,
                      support_email=SITE["support_email"],
                      support_notice=support_notice(),
                      tagline=esc(SITE["tagline"]),
                      subtitle=esc(SITE["subtitle"]))
        schema = ""
        if meta.get("schema") == "home":
            schema = json_ld(home_schema())
        noindex = meta.get("noindex", "false").lower() == "true"
        check_length("title", meta["title"], 20, 65, src.name)
        check_length("description", meta["description"], 70, 160, src.name)
        write(out_dir, meta["path"], page_html(
            base, title=meta["title"], description=meta["description"],
            path=meta["path"], body=body, css_href=css_href,
            schema=schema, noindex=noindex))
        built.append({"path": meta["path"], "noindex": noindex,
                      "updated": meta.get("updated", date.today().isoformat())})
    return built


def support_notice():
    if SITE["support_email_ready"]:
        return ""
    # TODO: remove by setting support_email_ready = True above once the mailbox works.
    return ('<p class="notice" role="note">Heads-up: the support inbox opens when '
            'Every Item launches on the App Store. Until then, messages may not be '
            'received.</p>')


def home_schema():
    return {
        "@context": "https://schema.org",
        "@type": "SoftwareApplication",
        "name": SITE["name"],
        "operatingSystem": "iOS",
        "applicationCategory": "LifestyleApplication",
        "description": SITE["tagline"],
        "url": SITE["url"] + "/",
        "author": {"@type": "Organization", "name": SITE["owner"], "url": SITE["base_url"] if "base_url" in SITE else "https://everyitem.app/"},
        "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"},
    }


# ---------------------------------------------------------------------------
# Guides
# ---------------------------------------------------------------------------
FAQ_HEADING = re.compile(r"^##\s+(faq|faqs|frequently asked questions)\b.*$",
                         re.IGNORECASE | re.MULTILINE)
REQUIRED_GUIDE_KEYS = ("title", "description", "updated", "quick_answer", "category")


def md_to_html(text):
    md = markdown.Markdown(
        extensions=["toc", "tables", "fenced_code", "attr_list", "sane_lists"],
        extension_configs={"toc": {"toc_depth": "2-3", "permalink": False}},
    )
    return md.convert(text), md.toc_tokens


def split_faq(body):
    """Everything after a '## FAQ' / '## Frequently asked questions' heading is the FAQ.
    Each '### Question?' inside it starts a question; the text below is the answer."""
    match = FAQ_HEADING.search(body)
    if not match:
        return body, []
    main, faq_text = body[:match.start()], body[match.end():]
    faqs = []
    for chunk in re.split(r"^###\s+", faq_text, flags=re.MULTILINE)[1:]:
        question, _, answer = chunk.partition("\n")
        if question.strip() and answer.strip():
            faqs.append((question.strip(), answer.strip()))
    return main, faqs


def load_guides(include_drafts):
    guides = []
    for src in sorted(GUIDES_DIR.glob("*.md")):
        meta, body = read_front_matter(src.read_text(encoding="utf-8"), src)
        is_draft = src.name.startswith("_") or meta.get("draft", "").lower() == "true"
        if is_draft and not include_drafts:
            print(f"  skip draft: {src.name}")
            continue
        missing = [k for k in REQUIRED_GUIDE_KEYS if not meta.get(k)]
        if missing:
            sys.exit(f"ERROR: {src.name} is missing: {', '.join(missing)}")
        try:
            date.fromisoformat(meta["updated"])
        except ValueError:
            sys.exit(f"ERROR: {src.name}: 'updated' must look like 2026-10-21")
        if not is_draft and "TODO" in (body + " ".join(meta.values())):
            sys.exit(f"ERROR: {src.name} still contains 'TODO'. Finish it or mark it draft: true.")
        slug = meta.get("slug") or src.stem.lstrip("_")
        if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", slug):
            sys.exit(f"ERROR: {src.name}: slug '{slug}' must be lowercase-words-with-dashes.")
        meta.update(slug=slug, body=body, draft=is_draft, source=src.name,
                    path=f"/guides/{slug}/")
        guides.append(meta)
    slugs = [g["slug"] for g in guides]
    dupes = {s for s in slugs if slugs.count(s) > 1}
    if dupes:
        sys.exit(f"ERROR: two guides share the slug(s): {', '.join(sorted(dupes))}")
    return sorted(guides, key=lambda g: g["updated"], reverse=True)


def build_guide(guide, base, guide_tpl, css_href, out_dir):
    main_md, faqs = split_faq(guide["body"])
    body_html, toc_tokens = md_to_html(main_md)

    toc_items = "\n".join(
        f'<li><a href="#{esc(t["id"])}">{t["name"]}</a></li>' for t in toc_tokens
        if t["level"] == 2)
    if faqs:
        toc_items += '\n<li><a href="#faq">FAQ</a></li>'
    toc_html = ('<nav class="toc" aria-labelledby="toc-title">'
                '<h2 id="toc-title">On this page</h2><ol>' + toc_items + '</ol></nav>'
                if toc_items else "")

    faq_html, faq_schema = "", []
    if faqs:
        parts = []
        for i, (q, a) in enumerate(faqs, 1):
            answer_html, _ = md_to_html(a)
            parts.append(f'<div class="faq-item"><h3 id="faq-{i}">{esc(q)}</h3>{answer_html}</div>')
            faq_schema.append({
                "@type": "Question", "name": q,
                "acceptedAnswer": {"@type": "Answer",
                                   "text": re.sub(r"<[^>]+>", "", answer_html).strip()},
            })
        faq_html = ('<section class="faq" aria-labelledby="faq">'
                    '<h2 id="faq">Frequently asked questions</h2>' + "".join(parts) + "</section>")

    url = SITE["url"] + guide["path"]
    published = guide.get("published") or guide["updated"]
    schemas = [{
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": guide["title"],
        "description": guide["description"],
        "datePublished": published,
        "dateModified": guide["updated"],
        "author": {"@type": "Organization", "name": SITE["owner"], "url": SITE["base_url"] if "base_url" in SITE else "https://everyitem.app/"},
        "publisher": {"@type": "Organization", "name": SITE["name"],
                      "logo": {"@type": "ImageObject",
                               "url": SITE["url"] + "/apple-touch-icon.png"}},
        "image": SITE["url"] + SITE["og_image"],
        "mainEntityOfPage": url,
    }, {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE["url"] + "/"},
            {"@type": "ListItem", "position": 2, "name": "Guides", "item": SITE["url"] + "/guides/"},
            {"@type": "ListItem", "position": 3, "name": guide["title"], "item": url},
        ],
    }]
    if faq_schema:
        schemas.append({"@context": "https://schema.org", "@type": "FAQPage",
                        "mainEntity": faq_schema})

    body = render(
        guide_tpl,
        title=esc(guide["title"]),
        category=esc(guide["category"]),
        updated_iso=guide["updated"],
        updated_nice=nice_date(guide["updated"]),
        quick_answer=esc(guide["quick_answer"]),
        toc=toc_html,
        content=body_html,
        cta_title=CTA_TITLE,
        faq=faq_html,
    )
    page_title = guide.get("seo_title") or f'{guide["title"]} | Every Item'
    check_length("title", page_title, 20, 65, guide["source"])
    check_length("description", guide["description"], 70, 160, guide["source"])
    write(out_dir, guide["path"], page_html(
        base, title=page_title, description=guide["description"], path=guide["path"],
        body=body, css_href=css_href, schema=json_ld(*schemas), og_type="article",
        draft=guide["draft"]))


def build_guides_index(guides, base, css_href, out_dir):
    if guides:
        sections = []
        categories = GUIDE_CATEGORIES + sorted(
            {g["category"] for g in guides} - set(GUIDE_CATEGORIES))
        for cat in categories:
            items = [g for g in guides if g["category"] == cat]
            if not items:
                continue
            cards = "\n".join(
                f'<li class="card guide-card"><a href="{g["path"]}"><h3>{esc(g["title"])}</h3>'
                f'<p>{esc(g["description"])}</p>'
                f'<p class="meta">Updated <time datetime="{g["updated"]}">'
                f'{nice_date(g["updated"])}</time></p></a></li>' for g in items)
            sections.append(f'<section><h2>{esc(cat)}</h2><ul class="guide-list">{cards}</ul></section>')
        listing = "\n".join(sections)
    else:
        listing = ('<p class="empty">The first guides are being written now. Check back soon '
                   'for plain-English guides to store return policies, warranties, organizing '
                   'receipts and home inventories for insurance.</p>')
    body = f"""
<section class="page-head container">
  <p class="eyebrow">Guides</p>
  <h1>Returns, warranties and receipts, explained</h1>
  <p class="lede">Practical, plain-English guides to store return windows, warranty coverage,
  keeping receipts organized and building a home inventory for insurance.</p>
</section>
<div class="container guides">
{listing}
</div>"""
    write(out_dir, "/guides/", page_html(
        base, title="Guides: Returns, Warranties & Receipts | Every Item",
        description=("Plain-English guides to store return policies, warranty coverage, "
                     "organizing receipts and making a home inventory for insurance."),
        path="/guides/", body=body, css_href=css_href))


# ---------------------------------------------------------------------------
# sitemap.xml and robots.txt
# ---------------------------------------------------------------------------
def build_sitemap(entries, out_dir):
    rows = []
    for e in entries:
        rows.append(f"  <url>\n    <loc>{esc(SITE['url'] + e['path'])}</loc>\n"
                    f"    <lastmod>{e['updated']}</lastmod>\n  </url>")
    xml = ('<?xml version="1.0" encoding="UTF-8"?>\n'
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
           + "\n".join(rows) + "\n</urlset>\n")
    (out_dir / "sitemap.xml").write_text(xml, encoding="utf-8")
    (out_dir / "robots.txt").write_text(
        f"User-agent: *\nAllow: /\n\nSitemap: {SITE['url']}/sitemap.xml\n", encoding="utf-8")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def build(include_drafts=False):
    out_dir = ROOT / ("preview" if include_drafts else "dist")
    print(f"Building into {out_dir.name}/ ...")
    guides = load_guides(include_drafts)   # checked first, so a bad guide never wipes dist/
    if out_dir.exists():
        shutil.rmtree(out_dir)
    shutil.copytree(STATIC_DIR, out_dir)

    css = (STATIC_DIR / "styles.css").read_bytes()
    css_href = "/styles.css?v=" + hashlib.sha1(css).hexdigest()[:8]  # cache-busting

    base = (TEMPLATES_DIR / "base.html").read_text(encoding="utf-8")
    guide_tpl = (TEMPLATES_DIR / "guide.html").read_text(encoding="utf-8")

    pages = build_static_pages(base, css_href, out_dir)
    for g in guides:
        build_guide(g, base, guide_tpl, css_href, out_dir)
        print(f"  guide: {g['path']}{'  (draft)' if g['draft'] else ''}")
    build_guides_index(guides, base, css_href, out_dir)

    newest = max([g["updated"] for g in guides] or [date.today().isoformat()])
    entries = [p for p in pages if not p["noindex"]]
    entries.append({"path": "/guides/", "updated": newest})
    entries += [g for g in guides if not g["draft"]]
    entries.sort(key=lambda e: (e["path"] != "/", e["path"]))
    build_sitemap(entries, out_dir)

    if not SITE["support_email_ready"]:
        print(f"  TODO: {SITE['support_email']} mailbox is not set up yet "
              "(set support_email_ready = True in build.py when it is).")
    print(f"Done: {len(pages)} pages + {len(guides)} guide(s) + guides index.")
    return out_dir


class Handler(http.server.SimpleHTTPRequestHandler):
    """Local preview server that shows 404.html for missing pages, like real hosts do."""
    def send_error(self, code, message=None, explain=None):
        page = Path(self.directory) / "404.html"
        if code == 404 and page.exists():
            data = page.read_bytes()
            self.send_response(404)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
        else:
            super().send_error(code, message, explain)


def main():
    parser = argparse.ArgumentParser(description="Build the Every Item website.")
    parser.add_argument("--serve", action="store_true", help="preview at http://localhost:PORT")
    parser.add_argument("--drafts", action="store_true", help="include drafts, output to preview/")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    out_dir = build(include_drafts=args.drafts)
    if args.serve:
        def handler(*a, **kw):
            return Handler(*a, directory=str(out_dir), **kw)
        print(f"Preview: http://localhost:{args.port}/   (press Ctrl+C to stop)")
        with http.server.ThreadingHTTPServer(("127.0.0.1", args.port), handler) as server:
            try:
                server.serve_forever()
            except KeyboardInterrupt:
                print("\nStopped.")


if __name__ == "__main__":
    main()
