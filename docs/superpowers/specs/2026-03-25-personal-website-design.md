# Personal Website — Design Spec

> Nicolas Kogane — Surgeon · Scientist · Engineer
> Astro static site on GitHub Pages

## Overview

Transform the existing PhD Dashboard Jekyll site into a full personal website. The site presents Nicolas's triple identity (CMF surgeon, PhD researcher, engineer) through an editorial, minimalist aesthetic with a warm terracotta accent. Built with Astro, deployed on GitHub Pages, architected for bilingual (EN/FR) from day one.

## Visual Identity

### Typography
- **Headings**: Instrument Serif — warm, distinctive, editorial
- **Body + UI**: Inter — clean, modern, excellent readability
- **Monospace** (data, code, stack labels): JetBrains Mono

### Color Palette
- Background: `#fafaf9` (warm off-white)
- Text primary: `#1c1917` (near-black, warm)
- Text secondary: `#78716c` (warm gray)
- Text tertiary: `#a8a29e` (muted stone)
- Borders: `#e7e5e4` (light stone)
- Accent: `#b05e3a` (terracotta) — used sparingly for links, hover states, one bold element per page
- Surface: `#ffffff` (cards, elevated elements)

No multi-color coding system on the public site. Terracotta is the single signature color.

### Atmospheric Motif
A faint SVG line drawing of a skull base sagittal cross-section rendered as thin geometric contour lines. Placed in the hero, right-aligned, ~6% opacity. Reads as texture, not illustration. Optional subtle parallax drift on scroll.

### Design Principles
- Generous whitespace — every element earns its place
- No emojis or icons in navigation or headings
- Restrained use of accent color
- Scandinavian-design-studio meets Nature-editorial feel

## Navigation

### Desktop
- Minimal top bar, transparent over the hero
- Transitions to frosted-glass (`backdrop-filter: blur`) on scroll
- Left: name as wordmark (Instrument Serif, no logo)
- Right: **PhD** · **Projects** · **CV** · **Stack** · **Labs** · **Misc**
- Far right: language toggle (EN / FR), understated

### Mobile
- Collapses to hamburger menu
- Slide-down panel with frosted-glass background, matching the desktop nav aesthetic

## Page Architecture

### Landing Page (`/`)
Full-viewport hero, then section previews.

**Hero**:
- Full viewport height
- Off-white background with the skull-base SVG motif (right-aligned, ~6% opacity)
- Left-aligned, vertically centered content:
  - Name in Instrument Serif (~2.5rem)
  - *"Surgeon · Scientist · Engineer"* in spaced small-caps, terracotta
  - Two lines of context in body font, muted: CMF surgeon at Necker, PhD at Arts et Métiers, research summary
  - Subtle scroll indicator at bottom edge

**Below the fold** — section previews:
- Each section gets a compact block: heading, 1-2 sentences, "explore" link
- Generous spacing between blocks
- Terracotta accent: thin left-border on each preview or on the explore links
- No icons or emojis — typography and whitespace do the work

### CV (`/cv`)
- Vertical timeline layout
- Two interleaved tracks on desktop (clinical / academic-research), single column on mobile
- Each entry: year, title, institution, one-line description
- Sections: Education, Clinical Experience, Research, Skills & Certifications
- "Download PDF" link at top
- Data source: `src/data/cv.yaml`

### PhD (`/phd`)
**Public layer**:
- Editorial narrative: context, multiscale approach, current progress, key findings
- Refined progress overview: overall advancement + 3-4 key metrics as elegant typography + thin progress bars
- Data source: `src/data/phd-progress.yaml` (migrated from `_data/collecte.yml`)

**Newsletter** (`/phd/newsletter`):
- Chronological weekly digest posts
- Each entry: date, title, summary, "read more" link
- Built from Astro content collections (`src/content/newsletter/*.md`)
- RSS feed via `@astrojs/rss`

**Private backend** (not publicly linked):
- Lab notebook: `/phd/lab/` — migrated from `_lab-entries/`
- Meetings: `/phd/meetings/` — migrated from `_meetings/`
- Both get `<meta name="robots" content="noindex">`, excluded from sitemap and navigation
- Serve as source material for writing newsletter digests

### Projects (`/projects`)
- Card grid layout
- Each card: title, one-line description, status badge (ongoing / completed / upcoming), domain tags (research / clinical / engineering)
- Click through to dedicated project page with context, methods, collaborators, outputs
- Content source: `src/content/projects/*.md`
- Designed to look intentional even with 1-2 entries

### Stack (`/stack`)
- Pipeline visualization — vertical flow showing integrated method+tool layers:
  - Molecular → RNAscope, IF — confocal, image analysis
  - 3D Imaging → LightSheet — clearing protocols, Imaris/Fiji
  - Biomechanics → ex vivo stimulation — custom rigs, analysis software
  - Clinical → Human atlas — CT/CBCT, 3D Slicer, statistical frameworks
- Each layer is a row/card: method on one side, tooling on the other
- Terracotta accent connects the flow
- Data source: `src/data/stack.yaml`

### Labs (`/labs`)
- Card per affiliation
- Each card: lab name, PI, institution, your role, what you do there
- Optional visual marker (institution logo/crest)
- Links to lab website
- Data source: `src/data/labs.yaml`

### Misc (`/misc`)
- Flexible grid of categorized entries
- Each entry: compact card with category tag (teaching, talks, conferences, interests, etc.)
- Low-friction to add — just drop a markdown file
- Content source: `src/content/misc/*.md`

## Technical Architecture

### Framework & Deployment
- **Astro** (latest stable) — static site generator
- **GitHub Pages** deployment via `@astrojs/github-pages` adapter
- Same `git push` workflow as current setup
- Zero client-side JS by default; interactive islands only where needed (nav toggle, scroll transitions)

### Project Structure
```
src/
├── layouts/
│   ├── BaseLayout.astro
│   └── PostLayout.astro
├── components/
│   ├── Nav.astro
│   ├── Hero.astro
│   ├── SectionPreview.astro
│   ├── TimelineEntry.astro
│   ├── ProjectCard.astro
│   ├── StackLayer.astro
│   ├── LabCard.astro
│   ├── MiscCard.astro
│   └── ProgressBar.astro
├── pages/
│   ├── index.astro
│   ├── cv.astro
│   ├── phd/
│   │   ├── index.astro
│   │   ├── newsletter/[...slug].astro
│   │   ├── lab/
│   │   └── meetings/
│   ├── projects/
│   │   ├── index.astro
│   │   └── [slug].astro
│   ├── stack.astro
│   ├── labs.astro
│   └── misc.astro
├── content/
│   ├── newsletter/
│   ├── projects/
│   ├── misc/
│   ├── lab-entries/     (private, migrated)
│   └── meetings/        (private, migrated)
├── data/
│   ├── cv.yaml
│   ├── stack.yaml
│   ├── labs.yaml
│   └── phd-progress.yaml
├── styles/
│   └── global.css
├── assets/
│   └── skull-base-motif.svg
└── i18n/
    ├── en.yaml
    └── fr.yaml
```

### Content Collections
Astro content collections with typed schemas for:
- `newsletter` — date, title, tags, summary
- `projects` — title, status, domain tags, collaborators, description
- `misc` — title, category, date
- `lab-entries` — date, title, tags (private)
- `meetings` — date, title, attendees, decisions, actions (private)

### i18n Strategy
- Folder-based routing: `/en/...` and `/fr/...` (future)
- Shared `i18n/` directory for UI strings (navigation labels, button text, section titles)
- Content translations as separate files in content collections (e.g. `newsletter/en/`, `newsletter/fr/`)
- Build English only for MVP; French layer plugs in without restructuring

### Data Migration
- `_data/collecte.yml` → `src/data/phd-progress.yaml`
- `_data/thesis.yml` → merged into PhD page narrative
- `_lab-entries/*.md` → `src/content/lab-entries/`
- `_meetings/*.md` → `src/content/meetings/`
- `_posts/*.md` → `src/content/newsletter/` (reframed as newsletter digests)
- `assets/css/style.css` → `src/styles/global.css` (rewritten to match new identity)

## Future Features (Not in MVP)
- **Bilingual content**: French translations of all pages and content
- **Web-based editor**: Headless CMS integration (Decap CMS or similar git-based editor) for adding/editing private markdown content from a browser — especially lab notebook and meeting notes
- **Publications & Communications**: Dedicated section for papers, talks, posters, invited lectures
- **Search**: Site-wide search across public content
- **Dark mode**: Optional, respecting `prefers-color-scheme`
