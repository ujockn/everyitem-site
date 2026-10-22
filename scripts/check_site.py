#!/usr/bin/env python3
"""
Quick health check for the built site. Run AFTER building:

    python3 build.py && python3 scripts/check_site.py          (checks dist/)
    python3 build.py --drafts && python3 scripts/check_site.py preview

It checks that:
  - every internal link and image points to a file that exists (including #anchors)
  - every page has exactly one <h1>, a <title>, a meta description and a canonical URL
  - titles and descriptions are unique
  - HTML tags are properly opened/closed and ids are not duplicated
  - JSON-LD structured data is valid JSON
  - every URL in sitemap.xml exists
Exits with an error code if anything is wrong.
"""
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse, unquote

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / (sys.argv[1] if len(sys.argv) > 1 else "dist")
SITE_URL = "https://everyitem.app"
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta",
        "source", "track", "wbr", "path", "circle", "rect"}  # svg shapes are self-closed


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack, self.errors, self.ids, self.links = [], [], [], []
        self.h1 = 0
        self.title = self.description = self.canonical = None
        self.jsonld, self._in_title, self._in_ld = [], False, False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag not in VOID:
            self.stack.append((tag, self.getpos()[0]))
        if "id" in a:
            self.ids.append(a["id"])
        for key in ("href", "src"):
            if a.get(key):
                self.links.append(a[key])
        if tag == "h1":
            self.h1 += 1
        if tag == "title":
            self._in_title = True
            self.title = ""
        if tag == "meta" and a.get("name") == "description":
            self.description = a.get("content")
        if tag == "link" and a.get("rel") == "canonical":
            self.canonical = a.get("href")
        if tag == "script" and a.get("type") == "application/ld+json":
            self._in_ld = True
            self.jsonld.append("")

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID and self.stack and self.stack[-1][0] == tag:
            self.stack.pop()

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        if tag == "title":
            self._in_title = False
        if tag == "script":
            self._in_ld = False
        if not self.stack or self.stack[-1][0] != tag:
            self.errors.append(f"line {self.getpos()[0]}: unexpected </{tag}> "
                               f"(open: {self.stack[-1][0] if self.stack else 'nothing'})")
            for i in range(len(self.stack) - 1, -1, -1):
                if self.stack[i][0] == tag:
                    del self.stack[i:]
                    break
        else:
            self.stack.pop()

    def handle_data(self, data):
        if self._in_title:
            self.title += data
        if self._in_ld:
            self.jsonld[-1] += data


def target_for(path):
    p = OUT / unquote(path).lstrip("/")
    if path.endswith("/"):
        p = p / "index.html"
    return p


def main():
    if not OUT.exists():
        sys.exit(f"{OUT} does not exist - run python3 build.py first.")
    problems, pages = [], {}
    for f in sorted(OUT.rglob("*.html")):
        # Google Search Console verification files are not real pages.
        if f.parent == OUT and f.name.startswith("google") and f.read_text(encoding="utf-8").startswith("google-site-verification:"):
            continue
        parser = Page()
        parser.feed(f.read_text(encoding="utf-8"))
        parser.close()
        rel = "/" + str(f.relative_to(OUT)).replace("index.html", "")
        pages[rel] = parser
        for e in parser.errors:
            problems.append(f"{rel}: {e}")
        if parser.stack:
            problems.append(f"{rel}: unclosed tags {[t for t, _ in parser.stack]}")
        dupes = {i for i in parser.ids if parser.ids.count(i) > 1}
        if dupes:
            problems.append(f"{rel}: duplicate ids {sorted(dupes)}")
        if parser.h1 != 1:
            problems.append(f"{rel}: has {parser.h1} <h1> elements (should be 1)")
        if not parser.title or not parser.description:
            problems.append(f"{rel}: missing <title> or meta description")
        if not (parser.canonical or "").startswith(SITE_URL + "/"):
            problems.append(f"{rel}: canonical URL missing or not on {SITE_URL}")
        for block in parser.jsonld:
            try:
                json.loads(block)
            except json.JSONDecodeError as err:
                problems.append(f"{rel}: invalid JSON-LD ({err})")

    for rel, parser in pages.items():
        for link in parser.links:
            u = urlparse(link)
            if u.scheme in ("http", "https", "mailto", "tel") or link.startswith("//"):
                continue
            path = u.path or rel
            if not path.startswith("/"):
                problems.append(f"{rel}: relative link '{link}' (use links starting with /)")
                continue
            target = target_for(path)
            if not target.exists():
                problems.append(f"{rel}: broken link '{link}'")
                continue
            if u.fragment:
                key = "/" + str(target.relative_to(OUT)).replace("index.html", "")
                if key in pages and u.fragment not in pages[key].ids:
                    problems.append(f"{rel}: link '{link}' points to a missing #{u.fragment}")

    for kind in ("title", "description"):
        seen = {}
        for rel, p in pages.items():
            seen.setdefault(getattr(p, kind), []).append(rel)
        for value, rels in seen.items():
            if len(rels) > 1:
                problems.append(f"duplicate {kind} on {rels}: {value!r}")

    sitemap = OUT / "sitemap.xml"
    if not sitemap.exists():
        problems.append("sitemap.xml is missing")
    else:
        for loc in re.findall(r"<loc>(.*?)</loc>", sitemap.read_text()):
            if not target_for(urlparse(loc).path).exists():
                problems.append(f"sitemap.xml lists a missing page: {loc}")
    if not (OUT / "robots.txt").exists():
        problems.append("robots.txt is missing")

    print(f"Checked {len(pages)} HTML pages in {OUT.name}/")
    if problems:
        print("\n".join("  PROBLEM: " + p for p in problems))
        sys.exit(1)
    print("  All good: links, anchors, headings, meta tags, JSON-LD and sitemap check out.")


if __name__ == "__main__":
    main()
