#!/usr/bin/env python3
"""
Sync photos from a public Lightroom "Share to Web" album into the site.

Downloads each photo from the shared album and writes:
  docs/assets/gallery/<name>.jpg   - the images (2048px long edge)
  docs/assets/gallery.json         - a manifest the gallery pages read

No Adobe developer account, OAuth, or secrets required - it uses the same
public data the shared album web page itself uses.

Run it any time you add photos to the album:
    python scripts/sync_lightroom.py

Config below: to point at a different album, paste a new Share-to-Web link's
id into SHARE_ID and update ALBUM_ID (find it by opening the album JSON, or
just ask Claude Code to refresh these).
"""

import json
import os
import re
import sys
import urllib.request
import urllib.error

# ---------------------------------------------------------------------------
# Config  (from Dan's public Lightroom share: https://adobe.ly/457KokU)
# ---------------------------------------------------------------------------
SHARE_ID = "781c9bf33c1e4d038e2a9aad0d8e8729"   # = the "space" id
ALBUM_ID = "5431219a3eff41089cd3b061a493fe40"
API_KEY  = "LightroomMobileWeb1"                 # public web key
SIZE     = "2048"                                # rendition: 2048 | 1280 | 640

API_BASE = "https://photos.adobe.io/v2"
SPACE_BASE = f"{API_BASE}/spaces/{SHARE_ID}"

# Output locations (relative to repo root)
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "docs", "assets", "gallery")
MANIFEST = os.path.join(ROOT, "docs", "assets", "gallery.json")

UA = "Mozilla/5.0 (portfolio-sync)"


def fetch(url, binary=False):
    """GET a URL. Adobe JSON responses are prefixed with `while (1) {}` as an
    anti-hijacking guard - strip it before parsing."""
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        data = r.read()
    if binary:
        return data
    text = data.decode("utf-8", "replace")
    text = re.sub(r"^while\s*\(1\)\s*\{\}", "", text).lstrip()
    return json.loads(text)


def list_assets():
    """Return every image resource in the album (follows pagination)."""
    assets = []
    url = (f"{SPACE_BASE}/albums/{ALBUM_ID}/assets"
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


def jpeg_size(data):
    """Read (width, height) from JPEG bytes without any image library."""
    i, n = 2, len(data)
    while i < n:
        if data[i] != 0xFF:
            i += 1
            continue
        marker = data[i + 1]
        # Start-Of-Frame markers carry the real dimensions.
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
    if not stem:
        stem = asset_id[:10]
    return stem


def main():
    print(f"Fetching album {ALBUM_ID} from shared space {SHARE_ID} ...")
    try:
        resources = list_assets()
    except urllib.error.HTTPError as e:
        sys.exit(f"ERROR listing album: HTTP {e.code} - the share link may be "
                 f"private or expired. Re-share the album and update SHARE_ID.")
    print(f"  album has {len(resources)} photos\n")

    os.makedirs(OUT_DIR, exist_ok=True)
    photos, used = [], set()

    for idx, res in enumerate(resources, 1):
        asset = res.get("asset", res)
        aid = asset.get("id", "")
        payload = asset.get("payload", {}) or {}
        imp = payload.get("importSource", {}) or {}
        links = asset.get("links", {}) or {}

        rel = links.get(f"/rels/rendition_type/{SIZE}") or {}
        href = rel.get("href")
        if not href:
            print(f"  [{idx}] {aid[:8]} - no {SIZE}px rendition, skipped")
            continue

        url = f"{SPACE_BASE}/{href}?api_key={API_KEY}"
        name = safe_name(imp.get("fileName", ""), aid)
        while name in used:
            name += "-2"
        used.add(name)
        fname = f"{name}.jpg"

        try:
            blob = fetch(url, binary=True)
        except urllib.error.HTTPError as e:
            print(f"  [{idx}] {name} - download failed (HTTP {e.code})")
            continue

        with open(os.path.join(OUT_DIR, fname), "wb") as f:
            f.write(blob)
        w, h = jpeg_size(blob)

        photos.append({
            "file": f"assets/gallery/{fname}",
            "name": imp.get("fileName", fname),
            "date": payload.get("captureDate", ""),
            "w": w, "h": h,
            "score": (payload.get("aesthetics", {}) or {}).get("score"),
        })
        print(f"  [{idx}] {fname}  ({w}x{h}, {len(blob)//1024} KB)")

    # Newest first (falls back to keeping album order when dates are missing).
    photos.sort(key=lambda p: p["date"], reverse=True)

    manifest = {
        "album": ALBUM_ID,
        "count": len(photos),
        "size": SIZE,
        "photos": photos,
    }
    with open(MANIFEST, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    print(f"\nDone: {len(photos)} photos -> docs/assets/gallery/")
    print(f"Manifest: docs/assets/gallery.json")


if __name__ == "__main__":
    main()
