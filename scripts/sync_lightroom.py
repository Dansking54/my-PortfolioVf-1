#!/usr/bin/env python3
"""
Sync photos from public Lightroom "Share to Web" albums into the site.

Each album becomes a named PROJECT on the Gallery wall. For every album it
downloads the photos (2048px long edge) plus the album cover and writes:

  docs/assets/gallery/<slug>/*.jpg   - the images for that project
  docs/assets/gallery/<slug>/cover.jpg
  docs/assets/gallery.json           - a manifest the gallery pages read

No Adobe developer account, OAuth, or secrets required - it uses the same
public data the shared album web page itself uses.

Run it any time you add photos or a new album:
    python scripts/sync_lightroom.py

To add a project: share the Lightroom album to web, paste the share link into
a browser to get its /shares/<id> URL (that id is the "space"), then add a row
to ALBUMS below with a slug + display title. Or just hand Claude Code the
share link and ask it to add it.
"""

import http.client
import json
import os
import re
import shutil
import sys
import urllib.request
import urllib.error

# ---------------------------------------------------------------------------
# The projects, in the order they appear on the Gallery wall.
#   slug   - url-safe id, also the folder name under docs/assets/gallery/
#   title  - the project name shown on the site (rename freely)
#   space  - the /shares/<id> id from the public share link
#   album  - the album id inside that space (found via the space "resources")
# ---------------------------------------------------------------------------
ALBUMS = [
    {"slug": "after-the-rain", "title": "After the Rain",
     "space": "781c9bf33c1e4d038e2a9aad0d8e8729",
     "album": "5431219a3eff41089cd3b061a493fe40"},   # was "Day 59"
    {"slug": "suburban-skies", "title": "Suburban Skies",
     "space": "345af5f7fb8d4aefa99ef7a15319b5c4",
     "album": "de9db80ff6ed4390a8be6838c487e209"},   # was "Day 3 posting"
    {"slug": "snow-and-gold", "title": "Snow & Gold",
     "space": "d8c741e18f074626a691fbddbbd7b480",
     "album": "e3261afb5b504cbfa0932322fbc96dec"},   # was "Day 17"
    {"slug": "on-film", "title": "On Film",
     "space": "74d60c39eb894a88bc29f8e0788a9bd6",
     "album": "ef778fa134914f6599f3fa851708dc0e"},   # was "15 Image on Film"
]

API_KEY = "LightroomMobileWeb1"   # public web key
SIZE = "2048"                      # rendition: 2048 | 1280 | 640
API_BASE = "https://photos.adobe.io/v2"

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GALLERY_DIR = os.path.join(ROOT, "docs", "assets", "gallery")
MANIFEST = os.path.join(ROOT, "docs", "assets", "gallery.json")
UA = "Mozilla/5.0 (portfolio-sync)"


def fetch(url, binary=False, tries=3):
    """GET a URL, retrying on transient network errors. Adobe JSON responses
    are prefixed with `while (1) {}` as an anti-hijacking guard - stripped
    before parsing."""
    last = None
    for attempt in range(1, tries + 1):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=90) as r:
                data = r.read()
            break
        except (urllib.error.URLError, http.client.IncompleteRead,
                TimeoutError) as e:
            last = e
            if attempt == tries:
                raise
    if binary:
        return data
    text = data.decode("utf-8", "replace")
    text = re.sub(r"^while\s*\(1\)\s*\{\}", "", text).lstrip()
    return json.loads(text)


def space_base(space):
    return f"{API_BASE}/spaces/{space}"


def list_assets(space, album):
    """Return every image resource in the album (follows pagination)."""
    assets = []
    url = (f"{space_base(space)}/albums/{album}/assets"
           f"?embed=asset&subtype=image&limit=100&api_key={API_KEY}")
    while url:
        data = fetch(url)
        assets.extend(data.get("resources", []))
        nxt = data.get("links", {}).get("next", {}).get("href")
        url = (f"{API_BASE}/{nxt}" if nxt and not nxt.startswith("http")
               else nxt) if nxt else None
        if url and "api_key" not in url:
            url += ("&" if "?" in url else "?") + "api_key=" + API_KEY
    return assets


def album_cover_href(space, album):
    """The album's chosen cover rendition href (relative to the space)."""
    data = fetch(f"{space_base(space)}/resources?api_key={API_KEY}")
    for r in data.get("resources", []):
        if r.get("id") == album:
            links = r.get("links", {}) or {}
            rel = links.get(f"/rels/rendition_type/{SIZE}") \
                or links.get("/rels/rendition_type/1280") or {}
            return rel.get("href")
    return None


def jpeg_size(data):
    """Read (width, height) from JPEG bytes without any image library."""
    i, n = 2, len(data)
    while i < n:
        if data[i] != 0xFF:
            i += 1
            continue
        marker = data[i + 1]
        if 0xC0 <= marker <= 0xCF and marker not in (0xC4, 0xC8, 0xCC):
            h = (data[i + 5] << 8) | data[i + 6]
            w = (data[i + 7] << 8) | data[i + 8]
            return w, h
        seg = (data[i + 2] << 8) | data[i + 3]
        i += 2 + seg
    return None, None


def safe_name(filename, asset_id):
    stem = os.path.splitext(filename or "")[0]
    stem = re.sub(r"[^A-Za-z0-9_-]+", "-", stem).strip("-").lower()
    return stem or asset_id[:10]


def sync_album(meta):
    space, album, slug = meta["space"], meta["album"], meta["slug"]
    out_dir = os.path.join(GALLERY_DIR, slug)
    os.makedirs(out_dir, exist_ok=True)

    print(f"\n[{meta['title']}]  ({slug})")
    resources = list_assets(space, album)
    print(f"  {len(resources)} photos")

    photos, used = [], set()
    for idx, res in enumerate(resources, 1):
        asset = res.get("asset", res)
        aid = asset.get("id", "")
        payload = asset.get("payload", {}) or {}
        imp = payload.get("importSource", {}) or {}
        rel = (asset.get("links", {}) or {}).get(f"/rels/rendition_type/{SIZE}") or {}
        href = rel.get("href")
        if not href:
            print(f"    [{idx}] {aid[:8]} - no {SIZE}px rendition, skipped")
            continue

        name = safe_name(imp.get("fileName", ""), aid)
        while name in used:
            name += "-2"
        used.add(name)
        fname = f"{name}.jpg"

        try:
            blob = fetch(f"{space_base(space)}/{href}?api_key={API_KEY}", binary=True)
        except urllib.error.HTTPError as e:
            print(f"    [{idx}] {name} - download failed (HTTP {e.code})")
            continue

        with open(os.path.join(out_dir, fname), "wb") as f:
            f.write(blob)
        w, h = jpeg_size(blob)
        photos.append({
            "file": f"assets/gallery/{slug}/{fname}",
            "name": imp.get("fileName", fname),
            "date": payload.get("captureDate", ""),
            "w": w, "h": h,
        })

    # Newest first (falls back to album order when capture dates are missing).
    photos.sort(key=lambda p: p["date"], reverse=True)

    # Album cover: the Lightroom-chosen cover, else the first photo.
    cover = photos[0]["file"] if photos else ""
    href = album_cover_href(space, album)
    if href:
        try:
            blob = fetch(f"{space_base(space)}/{href}?api_key={API_KEY}", binary=True)
            with open(os.path.join(out_dir, "cover.jpg"), "wb") as f:
                f.write(blob)
            cover = f"assets/gallery/{slug}/cover.jpg"
        except urllib.error.HTTPError as e:
            print(f"    cover download failed (HTTP {e.code}), using first photo")

    print(f"  -> {len(photos)} photos saved")
    return {
        "slug": slug,
        "title": meta["title"],
        "cover": cover,
        "count": len(photos),
        "photos": photos,
    }


def clean_gallery_dir():
    """Empty docs/assets/gallery/ without removing the folder itself.
    (OneDrive holds a lock on synced directories, so rmtree on the parent
    fails on Windows - delete the contents instead.)"""
    os.makedirs(GALLERY_DIR, exist_ok=True)
    for entry in os.listdir(GALLERY_DIR):
        path = os.path.join(GALLERY_DIR, entry)
        if os.path.isdir(path):
            shutil.rmtree(path, ignore_errors=True)
        else:
            try:
                os.remove(path)
            except OSError:
                pass


def main():
    # Start clean so removed photos/albums don't linger.
    clean_gallery_dir()

    albums = []
    for meta in ALBUMS:
        try:
            albums.append(sync_album(meta))
        except urllib.error.HTTPError as e:
            sys.exit(f"ERROR on '{meta['title']}': HTTP {e.code} - the share "
                     f"link may be private or expired. Re-share and update the "
                     f"space/album ids in ALBUMS.")

    manifest = {"size": SIZE, "albums": albums}
    with open(MANIFEST, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    total = sum(a["count"] for a in albums)
    print(f"\nDone: {len(albums)} projects, {total} photos -> docs/assets/gallery/")
    print("Manifest: docs/assets/gallery.json")


if __name__ == "__main__":
    main()
