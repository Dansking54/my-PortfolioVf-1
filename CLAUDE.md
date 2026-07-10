# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Portfolio + Booking Website** with dynamic media gallery, video showcase, and booking integration.

- **Purpose:** Professional portfolio showcasing photography/videography work with booking capability
- **Design:** Built from Claude Design export (HTML/CSS), converted to React/Next.js
- **Hosting:** GitHub Pages + custom domain
- **Budget:** Free (GitHub Pages, Lightroom API free tier, form integration via third-party)

---

## Tech Stack

- **Framework:** Next.js (React)
- **Deployment:** GitHub Pages (static export)
- **Styling:** CSS from Claude Design export (converted to modules or Tailwind)
- **Media APIs:**
  - **Lightroom:** Adobe Lightroom API for dynamic photo fetching
  - **YouTube/Instagram:** Embed iframes for video content
- **Forms:** External form service (Typeform, Formspree, etc.) for booking
- **Domain:** Custom domain pointing to GitHub Pages via DNS

---

## Project Structure

```
my-portfolio/
├── public/                    # Static assets
│   ├── images/               # Claude Design images (if any)
│   └── favicon.ico
├── components/               # React components
│   ├── Gallery.jsx           # Lightroom gallery (auto-sync)
│   ├── CuratedPhotos.jsx     # Selected photos sections
│   ├── VideoShowcase.jsx     # YouTube/Instagram embeds
│   ├── Header.jsx
│   ├── Footer.jsx
│   └── BookingForm.jsx       # Booking form embed
├── pages/                    # Next.js pages
│   ├── index.js             # Home
│   ├── portfolio.js         # Full gallery
│   ├── videos.js            # Video showcase
│   └── about.js             # About/contact
├── styles/                  # CSS modules (from Claude Design)
│   ├── globals.css
│   ├── gallery.module.css
│   └── ...
├── lib/                     # Utilities
│   ├── lightroomApi.js      # Lightroom API client
│   └── config.js            # API keys, constants
├── next.config.js           # GitHub Pages export config
├── package.json
└── .env.local               # API credentials (not committed)
```

---

## Key Features & Architecture

### 1. **Lightroom Integration**
- **Auto-sync gallery:** Fetches ALL photos from a specific Lightroom album
- **Curated sections:** Manually select specific photos for different pages
- **Metadata:** Pull titles, descriptions, dates from Lightroom
- **Image serving:** Lightroom hosts images (no local storage needed)

**Setup:**
1. Create Lightroom API credentials in Adobe Developer Console
2. Get Lightroom album ID (or use "favorites")
3. Store credentials in `.env.local`

### 2. **Design System**
- Based on Claude Design export (HTML/CSS)
- Convert CSS to CSS Modules or inline Tailwind
- Maintain consistent spacing, typography, colors across all components
- Responsive design for mobile/tablet/desktop

### 3. **Pages**
- **Home:** Hero, featured work, CTA to booking
- **Portfolio:** Full gallery from Lightroom + curated selections
- **Videos:** YouTube/Instagram embeds for recent uploads
- **About/Contact:** Booking form embed, social links

### 4. **Booking**
- External form service embedded (user handles via third-party)
- Options: Typeform, Calendly, Formspree, etc.
- No backend needed

---

## Development Setup

### Prerequisites
- Node.js 16+ and npm/yarn
- Adobe Lightroom API credentials (free tier)
- GitHub account for hosting

### Installation
```bash
# Clone/navigate to project
cd "C:\Users\danol\OneDrive - Champlain Regional College\1 Projects\Coding\My portfoliot Porject"

# Install dependencies
npm install

# Create .env.local with API keys
# LIGHTROOM_API_KEY=your_key
# LIGHTROOM_ALBUM_ID=your_album_id
```

### Development Commands
```bash
# Start dev server (http://localhost:3000)
npm run dev

# Build for production (static export for GitHub Pages)
npm run build

# Export static HTML
npm run export

# Preview production build
npm run start
```

### Deployment to GitHub Pages
```bash
# Push to GitHub (repo must be named: username.github.io OR my-portfolio)
git push origin main

# GitHub Actions will auto-deploy, or manually:
npm run build && npm run export
# Push /out folder contents to gh-pages branch
```

---

## Lightroom API Specifics

### Getting Credentials
1. Go to: https://developer.adobe.com/console
2. Create a new project
3. Add Lightroom API
4. Generate credentials (API key + secret)
5. Set up OAuth if using private albums

### API Endpoints Used
- `GET /v2/catalogs/{catalogId}/albums/{albumId}` — Album metadata
- `GET /v2/catalogs/{catalogId}/albums/{albumId}/assets` — Photos in album
- `GET /v2/catalogs/{catalogId}/assets/{assetId}` — Individual photo metadata

### Photo Display
- Lightroom returns CDN URLs for images (different sizes available)
- Use responsive `srcset` for different screen sizes
- Cache API responses (albums don't change constantly)

---

## Design Integration

**From Claude Design:**
- Export as HTML zip (keep updated in `/public/design-export` or convert to React components)
- Extract color palette, typography, spacing system
- Convert CSS to modules: `Header.module.css`, `Gallery.module.css`, etc.
- Maintain design consistency across dynamically generated content (Lightroom photos, videos)

---

## Environment Variables (.env.local)

```
NEXT_PUBLIC_LIGHTROOM_API_KEY=xxx
NEXT_PUBLIC_LIGHTROOM_ALBUM_ID=xxx
NEXT_PUBLIC_SITE_URL=https://yourdomain.com
NEXT_PUBLIC_BOOKING_FORM_URL=https://typeform.com/xxx
```

Note: `NEXT_PUBLIC_*` variables are exposed to browser (safe for public APIs). Sensitive secrets stay private.

---

## Common Tasks

### Add a new photo to gallery
1. Upload to Lightroom album
2. Wait for sync (manual refresh or auto-fetch on page load)
3. Photo appears automatically

### Update curated selections
1. Edit `lib/curatedPhotos.js` or CMS-like file
2. List photo IDs from Lightroom
3. Redeploy

### Add video
1. Upload to YouTube/Instagram
2. Add embed code to `pages/videos.js`
3. Redeploy

### Update booking form
1. Change `NEXT_PUBLIC_BOOKING_FORM_URL` in `.env.local`
2. Redeploy

---

## Performance Notes

- **Images:** Lightroom CDN handles serving (fast, cached globally)
- **Static export:** GitHub Pages serves pre-rendered HTML (no server needed)
- **API calls:** Cache Lightroom responses to reduce API calls
- **Build time:** Should be <1 min (mostly image optimization)

---

## Deployment Checklist

- [ ] Set up GitHub repo
- [ ] Configure custom domain DNS pointing to GitHub Pages
- [ ] Add `.env.local` with Lightroom API credentials
- [ ] Test locally (`npm run dev`)
- [ ] Build and test static export (`npm run build`)
- [ ] Push to GitHub and verify deployment
- [ ] Test on live domain
- [ ] Set up booking form URL

---

## Future Enhancements

- Analytics (Google Analytics, Plausible)
- Image lazy loading
- Lightroom album switching (if multiple albums)
- Client testimonials section
- Blog for photography tips

---

## Notes for Other Agents

- **This is a new project** — no existing code yet
- **Start with:** Next.js setup → export Claude Design → Lightroom API integration → component building
- **Design is locked in:** Don't change design from Claude Design export without user approval
- **Keep it simple:** Static site, no complex backend needed
- **User has coding knowledge:** Java, HTML/CSS, learning Python/C — can handle React/APIs
