# Instagram Carousel on Latest Page — Design

## Purpose
The Latest page (`docs/Latest.html`) currently only links out to Instagram via a static
"follow" card — no actual post content is visible on-site. Add a horizontally
auto-scrolling carousel of real Instagram post embeds so visitors can see recent posts
without leaving the site.

## Data source
New file: `docs/instagram-posts.js`

```js
window.IG_POSTS = [
  "https://www.instagram.com/p/DaZf5nLsFTN/",
  "https://www.instagram.com/p/DQVjZu5jHIb/",
  "https://www.instagram.com/p/DRkkkbLgiPG/",
  "https://www.instagram.com/p/DQiEEnhgZrV/",
  "https://www.instagram.com/p/DSjGQtriKpm/",
  "https://www.instagram.com/p/DURS_Tjitrz/",
  "https://www.instagram.com/p/DYac70IBMf3/",
  "https://www.instagram.com/p/DYln5vigsgL/",
  "https://www.instagram.com/p/DSNhSINAYVZ/",
  "https://www.instagram.com/p/DSDVhu9mHfd/"
];
```

To add/remove posts later: edit this array and push. No rebuild step, no other file changes.
Future additions can be sourced either by the user pasting new links, or by Claude browsing
the user's Instagram account (via the claude-in-chrome skill, in a future session) to pull
recent post URLs on request — this design doesn't build that automation, just leaves the
data format compatible with it (plain array of permalink URLs).

## Placement
New section "Latest from Instagram" inserted into `docs/Latest.html`, between the existing
YouTube player section and the existing 3-card follow-grid section (Instagram/TikTok/YouTube
links). The follow-grid section is unchanged and stays.

## Markup / rendering
- Section contains a viewport `div.ig-carousel` (`overflow:hidden`) wrapping a flex track
  `div.ig-track`.
- On page load, JS reads `window.IG_POSTS`, builds one
  `<blockquote class="instagram-media" data-instgrm-permalink="{url}">` per URL, appends
  each into `.ig-track`, **then duplicates the full set once more** (same blockquotes,
  cloned) so the track has two consecutive copies of the list back-to-back — this is what
  makes the loop seamless (see Looping below).
- After building the blockquotes, load Instagram's official embed script
  (`https://www.instagram.com/embed.js`) once. It scans the page for `.instagram-media`
  blockquotes and replaces each with a real embed iframe. No `instgrm.Embeds.process()`
  call is needed for the initial load since the script auto-runs on load; if it doesn't
  pick up dynamically-inserted blockquotes reliably, we call
  `window.instgrm.Embeds.process()` explicitly after the script loads as a fallback.

## Motion / carousel behavior
- A `requestAnimationFrame` loop shifts `.ig-track`'s `transform: translateX()` a small
  amount every frame (slow constant drift, e.g. ~30px/sec), moving right-to-left.
- **Looping**: once the track has scrolled past the width of one full set of posts (the
  first copy), snap `translateX` back by exactly that width with no visible jump (since the
  second copy is already sitting where the first was) — this reads as an infinite loop.
- **Pause on hover**: `mouseenter` on `.ig-carousel` stops the RAF loop; `mouseleave`
  resumes it.
- **Pause on touch**: `touchstart` stops the RAF loop (so mobile users can freely scroll/tap
  into a post without the track fighting them); `touchend` resumes it after a short delay
  (~1.5s) rather than instantly, so a tap doesn't immediately yank the view.
- The track itself does not use native scroll-snap; the motion is entirely JS-driven
  transform, matching the "it just stops moving" pause behavior requested.

## Styling
- Instagram's embed widget is a fixed white card design controlled by Instagram's CSS —
  it will NOT be reskinned to the site's dark/editorial theme. This is a known, accepted
  tradeoff (confirmed with user).
- Each slide gets consistent spacing/margins in the track and is top-aligned
  (`align-items:flex-start`) so posts with different caption lengths (different embed
  heights) don't look jarring next to each other.
- `.ig-carousel` sits inside the existing `.wrap` container padding, consistent with other
  sections on the page.

## Performance note
10 posts × 2 (duplicated for looping) = 20 iframes loaded on page visit. This is on the
higher end for embed-heavy pages; acceptable for now per user's post list, but worth
knowing if more posts get added later — could switch to lazy-loading offscreen slides in a
future iteration if it becomes a problem. Not building that now (YAGNI).

## Out of scope
- No live Instagram API/scraping integration — the post list is manually maintained.
- No reskinning of Instagram's embed widget internals.
- No lazy-loading/virtualization of offscreen carousel slides.
