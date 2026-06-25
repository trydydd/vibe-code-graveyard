---
name: "Vibe Code Graveyard"
description: "A living memorial to startups built with AI that are already breaking."
colors:
  void: "#0a0a0a"
  surface: "#141414"
  surface-2: "#1e1e1e"
  border: "#2a2a2a"
  text: "#c8c8c8"
  text-dim: "#999999"
  fine-print: "#888888"
  accent: "#dc2626"
  accent-dim: "#7f1d1d"
  accent-hover: "#b91c1c"
  white: "#ffffff"
  status-active-bg: "#451a03"
  status-active-text: "#fbbf24"
  status-abandoned-bg: "#1e1b4b"
  status-abandoned-text: "#818cf8"
  status-fixing-bg: "#14532d"
  status-fixing-text: "#4ade80"
  status-fixed-bg: "#064e3b"
  status-fixed-text: "#2dd4bf"
typography:
  display:
    fontFamily: "JetBrains Mono, Fira Code, SF Mono, monospace"
    fontSize: "clamp(1.75rem, 5vw, 3rem)"
    fontWeight: 700
    lineHeight: 1.2
    letterSpacing: "-0.02em"
  title:
    fontFamily: "JetBrains Mono, Fira Code, SF Mono, monospace"
    fontSize: "1.25rem"
    fontWeight: 700
    lineHeight: 1.3
  body:
    fontFamily: "-apple-system, BlinkMacSystemFont, Segoe UI, sans-serif"
    fontSize: "0.95rem"
    fontWeight: 400
    lineHeight: 1.6
  caption:
    fontFamily: "-apple-system, BlinkMacSystemFont, Segoe UI, sans-serif"
    fontSize: "0.85rem"
    fontWeight: 400
    lineHeight: 1.5
  mono:
    fontFamily: "JetBrains Mono, Fira Code, SF Mono, monospace"
    fontSize: "0.9rem"
    fontWeight: 400
    lineHeight: 1.5
  label:
    fontFamily: "JetBrains Mono, Fira Code, SF Mono, monospace"
    fontSize: "0.75rem"
    fontWeight: 400
    lineHeight: 1.4
    letterSpacing: "0.03em"
  meta:
    fontFamily: "JetBrains Mono, Fira Code, SF Mono, monospace"
    fontSize: "0.7rem"
    fontWeight: 400
    lineHeight: 1.4
rounded:
  xs: "3px"
  sm: "4px"
  md: "6px"
spacing:
  xs: "0.25rem"
  sm: "0.5rem"
  md: "1rem"
  lg: "1.5rem"
  xl: "2rem"
  xxl: "3rem"
components:
  btn:
    backgroundColor: "{colors.accent}"
    textColor: "{colors.white}"
    typography: "{typography.mono}"
    rounded: "{rounded.sm}"
    padding: "0.6rem 1.5rem"
  btn-hover:
    backgroundColor: "{colors.accent-hover}"
    textColor: "{colors.white}"
    rounded: "{rounded.sm}"
  filter-btn:
    backgroundColor: "transparent"
    textColor: "{colors.text-dim}"
    rounded: "{rounded.sm}"
    padding: "0.4rem 1rem"
  filter-btn-active:
    backgroundColor: "{colors.accent}"
    textColor: "{colors.white}"
    rounded: "{rounded.sm}"
  entry-card:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.text}"
    rounded: "{rounded.md}"
    padding: "1.25rem"
  entry-name:
    backgroundColor: "transparent"
    textColor: "{colors.white}"
    typography: "{typography.mono}"
    rounded: "{rounded.xs}"
  entry-status:
    backgroundColor: "{colors.status-active-bg}"
    textColor: "{colors.status-active-text}"
    typography: "{typography.label}"
    rounded: "{rounded.xs}"
---

# Design System: Vibe Code Graveyard

## 1. Overview

**Creative North Star: "The Digital Coroner"**

A clinical memorial to AI-generated technical debt. The graveyard is a forensic record disguised as a website — obituary aesthetics for an absurd modern phenomenon. The design is deliberately deadpan: monospace fonts, flat dark surfaces, a single red accent that reads like a warning label. The humor exists entirely in the gap between the serious format and the ridiculous content. It's not a blog, not a SaaS page, not a tool. It's a mirror.

The system explicitly rejects: corporate SaaS patterns (gradient blobs, trust badges, "book a demo"), tech blog aesthetics (prose-heavy layouts, author headshots, newsletter signups), aggressive shaming energy (hate posts, condescension), and anything that looks like it was built with AI (the irony would be unbearable).

**Key Characteristics:**
- Monospace-first typography — the interface reads like a terminal report, not a webpage
- Flat, zero-shadow surfaces — depth is communicated through tonal layering, not elevation
- One accent color, ruthlessly constrained — red appears on ≤15% of any screen
- Generous negative space — each entry breathes; the graveyard is sparse by design
- Responsive but never fluid — breaks happen at defined columns, not gradual morphing

## 2. Colors

A forensic palette: void-black backgrounds, neutral gray surfaces, and one clinical red accent.

### Primary
- **Morgue Red** (`#dc2626`): The only accent. Used for links, active filters, CTAs, the entry counter, and tool labels. Its rarity is the point — every red element signals action or emphasis.
- **Dried Blood** (`#7f1d1d`): Dim variant of the accent. Used for subtle borders around accent elements (counter pill, filter hover states).
- **Fresh Wound** (`#b91c1c`): Hover state for primary buttons. Slightly darker, never brighter.

### Secondary (status tags)
- **Amber Alert** (`#fbbf24` on `#451a03`): Active — still running, still breaking
- **Ghost Purple** (`#818cf8` on `#1e1b4b`): Abandoned — shut down or forgotten
- **Green Hope** (`#4ade80` on `#14532d`): Fixing — currently being cleaned up
- **Teal Resurrection** (`#2dd4bf` on `#064e3b`): Fixed — survived the cleanup

### Neutral
- **Void** (`#0a0a0a`): Page background. Not pure black — barely perceptible warmth to reduce eye strain on dark screens.
- **Surface** (`#141414`): Card and section backgrounds. One step above void.
- **Surface 2** (`#1e1e1e`): Elevated surfaces (unused in current layout, reserved for modals).
- **Border** (`#2a2a2a`): Section dividers, card borders. The only visible line in the system.
- **Text** (`#c8c8c8`): Primary body copy. High contrast against void, never pure white.
- **Text Dim** (`#999999`): Secondary copy, dates, metadata. Visible but deprioritized.
- **Fine Print** (`#888888`): Footer disclaimers, the absolute quietest text.
- **White** (`#ffffff`): Headings and card titles only. Reserved for maximum hierarchy.

**The Morgue Red Rule.** The accent appears on ≤15% of any given screen. Links, active states, and CTAs are the only permitted uses. If a screen feels "red," the design is wrong.

## 3. Typography

**Display Font:** JetBrains Mono (with Fira Code, SF Mono, monospace fallback)
**Body Font:** System sans-serif stack (with Segoe UI fallback)
**Label/Mono Font:** JetBrains Mono (system-wide monospace for all metadata, dates, tags)

**Character:** Monospace carries the authority of a terminal report — clinical, unemotional, precise. Sans-serif handles body copy where readability matters more than atmosphere. The pairing creates a document that reads like evidence, not opinion.

### Hierarchy
- **Display** (700, `clamp(1.75rem, 5vw, 3rem)`, 1.2 line-height): Page titles only. Monospace. White. Tight letter-spacing (-0.02em). Appears once per page.
- **Title** (700, 1.25rem, 1.3 line-height): Section headings. Monospace. White. Used for "What is this?" and similar headers.
- **Body** (400, 0.95rem, 1.6 line-height): Paragraph copy. Sans-serif. Text gray. Max 65ch line length.
- **Mono** (400, 0.9rem, 1.5 line-height): Entry cards, counters, filter buttons. Monospace. The workhorse type scale.
- **Label** (400, 0.75rem, 1.4 line-height, 0.03em letter-spacing, UPPERCASE): Tool labels, status tags. Monospace.
- **Meta** (400, 0.7rem, 1.4 line-height): Dates, source links, footer. Monospace. The quietest text above fine print.

**The Monospace Majority Rule.** At least 70% of visible text is monospace. Sans-serif exists only for paragraph-length body copy. Headers, metadata, buttons, tags, and counters are always mono.

## 4. Elevation

**Flat by default. No shadows anywhere.**

Depth is communicated exclusively through tonal layering: void → surface → surface 2. Cards sit on the surface layer (`#141414`) and are distinguished from the background by a 1px border (`#2a2a2a`), never by a shadow. There is no hover elevation on any component — only border-color shifts toward the accent.

**The Flat-By-Default Rule.** `box-shadow` does not exist in this design system. If a surface needs to feel elevated, make it lighter, not lifted.

## 5. Components

### Buttons
- **Character:** Clinical and urgent. Monospace text, flat red background, minimal radius.
- **Shape:** Gently curved edges (4px radius)
- **Primary:** Morgue Red background, white text, 0.6rem × 1.5rem padding, 0.85rem mono
- **Hover:** Fresh Wound background (`#b91c1c`), no transform, no scale — only color shift
- **Transition:** 0.15s, background only

### Filter Buttons
- **Character:** Terminal-style toggle pills. Transparent at rest, red when active.
- **Shape:** Gently curved edges (4px radius)
- **Default:** Transparent background, dim text, 1px border
- **Hover:** Accent border + accent text
- **Active:** Accent background + white text + accent border

### Entry Cards
- **Character:** Obituary entries. Flat, bordered, spacious.
- **Shape:** Slightly rounded (6px radius)
- **Background:** Surface (`#141414`)
- **Border:** 1px border (`#2a2a2a`)
- **Hover:** Border shifts to Dried Blood (`#7f1d1d`) — the only interaction state
- **Internal Padding:** 1.25rem
- **Fade-in:** 0.3s ease-out on mount (opacity 0→1, translateY 8px→0)

### Status Tags
- **Character:** Case file labels. Uppercase, monospace, tiny.
- **Shape:** Tight radius (3px)
- **Typography:** 0.65rem mono, 0.05em letter-spacing, uppercase
- **Four variants:** Active (amber), Abandoned (purple), Fixing (green), Fixed (teal)

### Form Inputs (Removal Page)
- **Character:** Minimal and functional. Monospace text, dark background matching page.
- **Style:** 1px border, void background, 4px radius
- **Focus:** Border shifts to accent
- **Padding:** 0.6rem × 0.75rem
- **Font:** 0.9rem monospace

### Links
- **Style:** Morgue Red, no underline, monospace
- **Hover:** Underline appears
- **Source links:** Include `↗` suffix

## 6. Do's and Don'ts

### Do:
- **Do** use monospace for all headings, labels, metadata, buttons, and UI chrome.
- **Do** keep the accent red at ≤15% of any screen — its rarity is its power.
- **Do** use tonal layering (void → surface → border) for depth, never shadows.
- **Do** write entry descriptions in neutral, clinical language — document, don't editorialize.
- **Do** keep cards spacious: 1.25rem padding, 0.75rem gaps between elements.
- **Do** use uppercase + monospace for all labels and tags — they read like case file stamps.
- **Do** maintain the obituary aesthetic: sparse, serious, data-like.

### Don't:
- **Don't** use shadows, gradients, glassmorphism, or any decorative elevation technique.
- **Don't** add a second accent color — the status tags are the only exception, and they're contextual.
- **Don't** make it look like a SaaS landing page (no trust badges, no "book a demo", no hero sections with CTAs).
- **Don't** make it look like a tech blog (no author bios, no newsletter signup, no prose-heavy opinion pieces).
- **Don't** use aggressive or mocking language — we're the coroner, not the murderer.
- **Don't** add gratuitous animation beyond the card fade-in and button transitions.
- **Don't** use sans-serif for headings or metadata — monospace is the authority.
- **Don't** make it look like it was built with AI — the irony would be unbearable.
