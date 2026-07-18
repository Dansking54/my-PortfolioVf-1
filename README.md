# Dan's Logs — Portfolio + Booking Website

Photography / filmmaking portfolio with a Lightroom-powered project gallery.
Static site hosted on **GitHub Pages** (served from the `docs/` folder).

---

## 📂 What's in this project (plain-language map)

| Folder / file | What it is | Do I touch it? |
|---|---|---|
| **`docs/`** | 🌐 **The actual live website.** This is what visitors see on GitHub Pages. | Don't hand-edit — it's generated (see below). |
| **`Dans_logs Portfolio/`** | 🎨 **The build source** — the design pages (`site/`) + original images (`assets/`) that the website is built from. | Edit here, then rebuild. |
| **`scripts/`** | ⚙️ Two helper scripts (see below). | Run them; edit only to change behavior. |
| **`_archive/`** | 📦 Old drafts, screenshots, uploads — **not used by the live site.** Kept just in case. | Ignore. |
| `CLAUDE.md` | Notes/instructions for Claude Code. | — |
| `Read my notes.txt` | Your personal notes. | Yours. |

---

## 🔁 How an update works (nothing is ever "replaced")

The live site in `docs/` is **generated** from the source in `Dans_logs Portfolio/site/`.
Two scripts do the work:

```bash
# 1. Pull the latest photos from your Lightroom albums into docs/
python scripts/sync_lightroom.py

# 2. Rebuild the site pages in docs/ from the design source
python scripts/build_site.py
```

Then it goes to GitHub as a normal commit (adds to history — never wipes it):

```bash
git add -A
git commit -m "describe what changed"
git push
```

### Preview it locally before pushing
```bash
python -m http.server 8000 --directory docs
# then open http://localhost:8000  (tip: Ctrl+Shift+R for a fresh load)
```

---

## 🖼️ The Gallery (projects)

Each Lightroom shared album = one **project** on the Gallery wall.
They're listed in the `ALBUMS` block at the top of `scripts/sync_lightroom.py`
(name + share link ids). To add a project: share a Lightroom album, add a row,
re-run `sync_lightroom.py`, then `build_site.py`.

Current projects: **After the Rain · Suburban Skies · Snow & Gold · On Film**.

---

## ✅ Handy notes

- **Pages built by `build_site.py`:** Home, Photography, Film, About, Services,
  Contact, Project, Latest (nav + footer are injected automatically).
- **Pages authored by hand in `docs/`:** `Gallery.html` (the project wall) and
  `Album.html` (a single project's photos). Edit these directly.
- **After changing `site.css` or the JS,** bump `ASSET_VERSION` in
  `build_site.py` so browsers load the fresh file instead of a cached copy.
- **GitHub Pages setting:** Settings → Pages → deploy from `main` branch,
  `/docs` folder.
