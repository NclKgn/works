# Sveltia CMS Integration — Design Spec

## Goal

Add a web-based content editor to the personal website so Nicolas can create and edit all site content (lab notes, meetings, newsletter, projects, CV, etc.) from any browser with GitHub authentication. No backend infrastructure beyond a free Cloudflare Worker for OAuth.

## Chosen Approach

**Sveltia CMS** — a modern, Svelte-based fork of Decap CMS (formerly Netlify CMS). Drop-in static CMS that runs entirely in the browser and commits directly to the GitHub repo via the GitHub API.

### Why Sveltia over Decap

- Faster (Svelte vs React)
- Cleaner, more modern UI
- Better i18n support (useful for future EN/FR bilingual content)
- Built-in asset management
- Same `config.yml` format — can swap back to Decap if needed
- Active development, growing community

### Why not a custom CMS

- Weeks of development vs hours
- Requires a server runtime (Vercel, Cloudflare, etc.)
- Auth, sessions, rich text editor — all built from scratch
- Ongoing maintenance burden
- Overkill for a single-user site

## Architecture

```
You (any browser / mobile)
  │
  ▼
nclkgn.github.io/works/admin/
  │
  ├─► GitHub OAuth ◄──► Cloudflare Worker (sveltia-cms-auth)
  │                      Free tier, zero maintenance
  ▼ authenticated
Sveltia CMS (client-side SPA in browser)
  │
  ▼ git commit via GitHub API
GitHub Repository (nclkgn/works, main branch)
  │
  ▼ push triggers
GitHub Actions (npm run build) ──► GitHub Pages (live in ~1-2 min)
```

**Key property:** The site stays 100% static. Sveltia CMS runs in the browser and talks directly to the GitHub API. The only external service is the Cloudflare Worker for OAuth — free, serverless, stateless.

## Files to Add

### In the repo

- `public/admin/index.html` — Single HTML file that loads Sveltia CMS from CDN
- `public/admin/config.yml` — Collection definitions, auth settings, editorial config

### External services (one-time setup)

- **GitHub OAuth App** — registered in GitHub settings (Settings > Developer settings > OAuth Apps)
  - Authorization callback URL: `https://<your-worker-name>.workers.dev/callback` (determined during Cloudflare Worker deployment)
- **Cloudflare Worker** — deploy `sveltia-cms-auth` (official Sveltia authenticator)
  - Environment variables: `GITHUB_CLIENT_ID`, `GITHUB_CLIENT_SECRET`
  - Allowed user: `nclkgn` (Nicolas's GitHub username)

## Authentication & Security

- **Method:** GitHub OAuth via Authorization Code Flow
- **OAuth proxy:** Cloudflare Worker running `sveltia-cms-auth` — handles token exchange only, never sees content
- **Access control:** CMS config restricts to a single GitHub username (`nclkgn`)
- **Content flow:** Browser → GitHub API (direct) — the Worker is only involved during login
- **Admin page:** The HTML is publicly accessible, but without GitHub auth no actions are possible
- **Private sections:** Lab entries and meetings remain `noindex` and excluded from sitemap regardless of CMS

## Collection Configuration

### Markdown Collections (folder-based)

Each entry is a `.md` file. Users can create, edit, and delete entries.

#### Lab Entries (private)
- **Path:** `src/content/lab-entries/`
- **Fields:** title (string), date (datetime), tags (list), draft (boolean), body (markdown — rich + raw)
- **Slug pattern:** `{{year}}-{{month}}-{{day}}-{{slug}}`

#### Meetings (private)
- **Path:** `src/content/meetings/`
- **Fields:** title (string), date (datetime), attendees (list), decisions (list), actions (list), draft (boolean), body (markdown)
- **Slug pattern:** `{{year}}-{{month}}-{{day}}-{{slug}}`

#### Newsletter (public)
- **Path:** `src/content/newsletter/`
- **Fields:** title (string), date (datetime), summary (text), tags (list), draft (boolean), body (markdown — rich + raw)
- **Slug pattern:** `{{year}}-{{month}}-{{day}}-{{slug}}`

#### Projects (public)
- **Path:** `src/content/projects/`
- **Fields:** title (string), status (select: ongoing/completed/planned), domain (list), collaborators (list), order (number), draft (boolean), body (markdown)
- **Slug pattern:** `{{slug}}`

#### Misc (public)
- **Path:** `src/content/misc/`
- **Fields:** title (string), category (string), date (datetime, optional), draft (boolean), body (markdown)
- **Slug pattern:** `{{slug}}`

### Data Collections (single-file YAML)

Each collection is a single YAML file edited as structured forms. No markdown body.

#### CV
- **File:** `src/data/cv.yaml`
- **Fields per entry:** id (string), section (select: education/clinical/research/teaching), year (string), title (string), institution (string), description (text)

#### Stack
- **File:** `src/data/stack.yaml`
- **Fields per entry:** id (string), layer (string), methods (list), tools (list), description (text), order (number)

#### Labs
- **File:** `src/data/labs.yaml`
- **Fields per entry:** id (string), name (string), pi (string), institution (string), role (string), work (text), url (string, optional)

#### PhD Progress
- **File:** `src/data/phd-progress.yaml`
- **Fields per entry:** id (string), label (string), value (number, 0–100), color (color picker, optional)

## Draft Workflow

Since Sveltia CMS does not yet support branch-based editorial workflow (planned for v2.0, mid-2026), drafts are handled via a frontmatter field:

- All markdown collections include a `draft` boolean field (default: `false`)
- Sveltia shows this as a toggle in the editor UI
- Astro listing pages filter out drafts in production: `entries.filter(e => !e.data.draft)`
- In dev mode, drafts are shown (with a visual indicator) for preview purposes
- Data collections (YAML) do not need drafts — they are always "live"

### Astro changes required

1. **`src/content.config.ts`** — add `draft: z.boolean().default(false)` to all markdown collection schemas
2. **Listing pages** — add `.filter(e => !e.data.draft)` to content queries on:
   - `src/pages/phd/lab/index.astro`
   - `src/pages/phd/meetings/index.astro`
   - `src/pages/phd/newsletter/index.astro`
   - `src/pages/projects/index.astro`
   - `src/pages/misc.astro`
3. **Dynamic routes** — add draft check to `[...slug].astro` pages to prevent rendering draft entries
4. **RSS feed** — filter drafts from `src/pages/rss.xml.js`

## Editor Experience

- **Layout:** Sidebar with collection list, main area shows entry list or editor
- **Markdown editing:** Rich text editor (Lexical-based) with toolbar toggle to raw markdown mode
- **YAML editing:** Structured forms with typed inputs (text, select, list, number, color picker)
- **Mobile:** Responsive — works on phone for quick notes between surgeries
- **Save:** Commits directly to `main` branch. Site rebuilds automatically via GitHub Actions (~1-2 min)
- **Media:** Sveltia has built-in asset management for images if needed in the future

## Access URL

```
https://nclkgn.github.io/works/admin/
```

## Constraints & Limitations

- **Rebuild delay:** ~1-2 minutes between saving and seeing changes live (GitHub Actions build time)
- **No real-time preview:** Sveltia shows a preview pane, but it won't match the actual site styling exactly
- **OAuth dependency:** Login requires internet + GitHub being up (not an issue in practice)
- **Cloudflare Worker:** Must stay deployed. Free tier has generous limits (100k requests/day), but it's an external dependency
- **Draft workflow:** Frontmatter-based only until Sveltia v2.0 adds branch-based editorial workflow
