#!/usr/bin/env python3
"""
Build the deployable static site in docs/ from the Claude Design export in
"Dans_logs Portfolio/site/".

What it does to each page:
  - rewrites ../assets/  ->  assets/   (flat docs/ layout)
  - drops the <image-slot> web component (it only works inside Claude's
    design tool) and turns those boxes into ordinary <img> elements
  - fills the previously-empty photo frames with real Lightroom photos
  - renames Home.html -> index.html and repoints links
  - adds a "Gallery" item to the nav + footer

Re-run after re-exporting the design:  python scripts/build_site.py
(The Gallery page itself is authored by hand in docs/Gallery.html.)
"""

import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "Dans_logs Portfolio", "site")
OUT = os.path.join(ROOT, "docs")

PAGES = ["Home", "Photography", "Film", "About", "Services", "Contact",
         "Project", "Links", "Latest"]

# Which gallery photos fill the empty design frames. Filled from gallery.json:
# portrait frames get tall photos, landscape frames get wide ones.
with open(os.path.join(OUT, "assets", "gallery.json"), encoding="utf-8") as f:
    _data = json.load(f)
# gallery.json now groups photos into albums; flatten to one pool for the
# slot-fills below (older single-album manifests used a flat "photos" list).
if "albums" in _data:
    GALLERY = [p for a in _data["albums"] for p in a.get("photos", [])]
else:
    GALLERY = _data.get("photos", [])
PORTRAIT = [p["file"] for p in GALLERY if (p["h"] or 0) >= (p["w"] or 1)]
LANDSCAPE = [p["file"] for p in GALLERY if (p["w"] or 0) > (p["h"] or 1)]

# id -> (image file, alt, prefer orientation). None => use a local asset.
SLOT_FILLS = {
    "w2": (PORTRAIT[0], "Portrait in available light"),
    "w3": (PORTRAIT[1], "Wedding photography"),
    "w4": (PORTRAIT[2], "Brand campaign"),
    "w6": (PORTRAIT[3], "Portrait"),
    "bts1": (LANDSCAPE[0], "Behind the scenes"),
    "bts2": (LANDSCAPE[1], "Film still"),
    "portrait": ("assets/pfp.png", "Dan behind the lens"),
}


# Which top-level nav item is "active" for each page.
NAV_GROUP = {
    "Home": "home",
    "Photography": "gallery", "Film": "gallery", "Latest": "gallery",
    "Project": "gallery",
    "About": "about", "Services": "about", "Contact": "about",
}

# The @dans_logs button target. TODO: swap for Dan's standalone bio-site link.
BIOSITE_URL = "https://www.instagram.com/dans_logs/"


def nav_html(active):
    def a(group):
        return ' class="active"' if active == group else ''
    return (
        '<nav>\n'
        f'    <a{a("home")} href="index.html">Home</a>\n'
        '    <span class="menu">\n'
        f'      <a{a("gallery")} href="Gallery.html">Gallery <i class="caret">▾</i></a>\n'
        '      <span class="submenu">\n'
        '        <a href="Photography.html">Photography</a>\n'
        '        <a href="Film.html">Film</a>\n'
        '        <a href="Latest.html">Latest</a>\n'
        '      </span>\n'
        '    </span>\n'
        '    <span class="menu">\n'
        f'      <a{a("about")} href="About.html">About <i class="caret">▾</i></a>\n'
        '      <span class="submenu">\n'
        '        <a href="Contact.html">Contact</a>\n'
        '        <a href="Services.html">Services</a>\n'
        '      </span>\n'
        '    </span>\n'
        '    <span class="menu ig-menu">\n'
        f'      <a class="ig" href="{BIOSITE_URL}" target="_blank" rel="noopener">@dans_logs <i class="caret">▾</i></a>\n'
        '      <span class="submenu">\n'
        '        <a href="https://www.instagram.com/dans_logs/" target="_blank" rel="noopener">Instagram</a>\n'
        '        <a href="https://www.tiktok.com/@dans_logs" target="_blank" rel="noopener">TikTok</a>\n'
        '        <a href="https://www.youtube.com/@Dans_Logs" target="_blank" rel="noopener">YouTube</a>\n'
        '      </span>\n'
        '    </span>\n'
        '  </nav>'
    )


FOOTER_PAGES = (
    '<div class="pages">\n'
    '    <a href="Photography.html">Photography</a>\n'
    '    <a href="Gallery.html">Gallery</a>\n'
    '    <a href="Film.html">Film</a>\n'
    '    <a href="Latest.html">Latest</a>\n'
    '    <a href="About.html">About</a>\n'
    '    <a href="Services.html">Services</a>\n'
    '    <a href="Contact.html">Contact</a>\n'
    '  </div>'
)


def transform(name, html):
    # 1) remove the image-slot script include (before token swap below)
    html = re.sub(r'\s*<script src="\.\./lib/image-slot\.js"></script>', "", html)

    # 2) image-slot -> img  (covers both CSS selectors and element tags)
    html = html.replace("image-slot", "img")

    # 3) flatten asset paths
    html = html.replace("../assets/", "assets/")

    # 4) Home.html -> index.html (nav, footer, CTA anchors, #work)
    html = html.replace("Home.html", "index.html")

    # 5) fill the empty photo frames (former slots) with real images
    for sid, (src, alt) in SLOT_FILLS.items():
        pattern = re.compile(r'<img id="' + re.escape(sid) + r'"[^>]*>(?:\s*</img>)?')
        repl = f'<img id="{sid}" src="{src}" alt="{alt}" loading="lazy">'
        html = pattern.sub(repl, html)

    # 5b) strip leftover design-tool attributes from plain <img> tags
    #     (placeholder=/shape= only mean something inside Claude Design)
    html = re.sub(r'(<img\b[^>]*?)\s+placeholder="[^"]*"', r"\1", html)
    html = re.sub(r'(<img\b[^>]*?)\s+shape="[^"]*"', r"\1", html)
    html = html.replace("></img>", " />")

    # 6) drop the "drag & drop your photos" hint (does nothing on a live site)
    html = re.sub(r'\s*<span class="hint">.*?</span>\s*</span>', "", html,
                  flags=re.DOTALL)

    # 7) replace the flat header nav with the dropdown nav, and the footer
    #    page list with the full flat list. (Links.html is the standalone
    #    bio-site page - it has no site header, so leave it untouched.)
    if name != "Links":
        html = re.sub(r"<nav>.*?</nav>", nav_html(NAV_GROUP.get(name, "")),
                      html, count=1, flags=re.DOTALL)
        html = re.sub(r'<div class="pages">.*?</div>', FOOTER_PAGES,
                      html, count=1, flags=re.DOTALL)

    return html


def transform_projects_js(js):
    js = js.replace("../assets/", "assets/").replace("Home.html", "index.html")
    # Project detail galleries: skip the empty drop-slots, keep real media.
    js = js.replace(
        "return '<figure class=\"g-item slot\"><img id=\"' + p.slug + '-' + m.id + '\" placeholder=\"Drop a ' + p.title + ' frame\"></img></figure>';",
        "return '';")
    # (source still says image-slot here; handle that spelling too)
    js = re.sub(r"return '<figure class=\"g-item slot\">.*?</figure>';",
                "return '';", js)
    return js


def main():
    for name in PAGES:
        with open(os.path.join(SRC, f"{name}.html"), encoding="utf-8") as f:
            html = f.read()
        out_name = "index.html" if name == "Home" else f"{name}.html"
        with open(os.path.join(OUT, out_name), "w", encoding="utf-8") as f:
            f.write(transform(name, html))
        print(f"  built docs/{out_name}")

    # projects.js (shared data + renderers)
    with open(os.path.join(SRC, "projects.js"), encoding="utf-8") as f:
        js = f.read()
    js = transform_projects_js(js)
    js = js.replace("Photography</a>", "Photography</a>")  # no-op safety
    with open(os.path.join(OUT, "projects.js"), "w", encoding="utf-8") as f:
        f.write(js)
    print("  built docs/projects.js")


if __name__ == "__main__":
    main()
