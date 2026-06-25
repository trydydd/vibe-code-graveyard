# The Vibe Code Graveyard

Startups built with AI coding tools that are already breaking. A living memorial to technical debt.

**Live:** [vibegraveyard.com](https://vibegraveyard.com)

## What is this?

A curated public index of startups and apps built with AI coding tools — Cursor, Claude Code, Bolt.new, Lovable, v0 — that are experiencing public failures: crashes, security breaches, scaling issues, abandoned projects, or founder confessions of regret.

Entries are sourced from public confessions on Reddit, Hacker News, IndieHackers, and Twitter/X. Removal is frictionless. See [about](about.html).

## Project structure

```
├── index.html          # Homepage: entry grid with filters
├── about.html          # What this is and how it works
├── remove.html         # Removal request form
├── style.css           # Global styles (dark, clinical, monospace)
├── script.js           # Entry renderer, filters, URL state
├── favicon.svg         # Skull icon
├── DESIGN.md           # Design system tokens + component specs
│
├── graveyard/          # Entry data
│   ├── _entries.json   # Frontend index (generated)
│   ├── entry-*.md      # Individual entries (YAML frontmatter)
│
├── scrape_graveyard.py # Scraper: Reddit, HN, IndieHackers → .md + _entries.json
│
├── PRODUCT.md          # Product spec, positioning, brand voice
├── README.md           # This file
```

## Adding entries

Each entry is a markdown file in `graveyard/entry-<ID>.md` with YAML frontmatter:

```markdown
---
id: abc123def456
name: "Your entry title"
tool: Cursor
status: Active
date: 2025-11-25
source: https://example.com/source
source_site: r/EntrepreneurRideAlong
founder_handle: ""
---

Description of the failure, confession, or issue. Clinical tone.
```

**Statuses:** `Active`, `Abandoned`, `Fixing`, `Fixed`
**Tools:** `Cursor`, `Claude Code`, `Bolt`, `Lovable`, `v0`, `Copilot`, `AI` (generic)

After adding or modifying `.md` files, rebuild the JSON index:

```bash
python3 scrape_graveyard.py build
```

## The scraper

`scrape_graveyard.py` scans public feeds for posts matching vibe-coding keywords, then writes entry files and rebuilds the frontend index.

**Usage:**

```bash
python3 scrape_graveyard.py             # Run all scrapers
python3 scrape_graveyard.py reddit      # Reddit only (RSSHub)
python3 scrape_graveyard.py hn          # Hacker News (Algolia API)
python3 scrape_graveyard.py indiehackers # IndieHackers RSS
python3 scrape_graveyard.py build       # Rebuild _entries.json from existing .md files
```

**How it works:**

1. **Scrape** — Pulls RSS feeds from Reddit (via RSSHub), Hacker News (Algolia API), and IndieHackers
2. **Filter** — Matches titles/descriptions against a keyword list (`vibe coded`, `cursor`, `claude code`, `technical debt`, etc.)
3. **Detect** — Identifies which AI tool is mentioned (Cursor, Claude Code, Bolt, etc.)
4. **Deduplicate** — Stable IDs based on `url:md5(title)` — same source, same entry
5. **Write** — Outputs `graveyard/entry-<ID>.md` files with YAML frontmatter
6. **Index** — Rebuilds `graveyard/_entries.json` from all `.md` files for the frontend

**No dependencies required** — runs on Python 3 stdlib only (`urllib`, `json`, `xml.etree`, `hashlib`).

## Serving locally

```bash
cd vibe-code-graveyard
python3 -m http.server 8765
# → http://localhost:8765
```

## Design

Dark, clinical, obituary aesthetic. Monospace-first typography. Single red accent, ruthlessly constrained. No shadows, no gradients, no SaaS patterns.

See [DESIGN.md](DESIGN.md) for the full design system: color tokens, typography scale, component specs, and do/don't rules.

## Contact

matteo@trydydd.com
