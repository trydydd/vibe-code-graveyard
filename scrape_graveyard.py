#!/usr/bin/env python3
"""
Vibe Code Graveyard - Entry Scraper

Scrapes Reddit, IndieHackers, and Hacker News for public confessions of
AI-generated codebase problems.

Usage:
  python3 scrape_graveyard.py              # Run all scrapers, write new entries
  python3 scrape_graveyard.py --dry-run    # Print candidates without writing files
  python3 scrape_graveyard.py reddit       # Reddit only
  python3 scrape_graveyard.py hn           # Hacker News only
  python3 scrape_graveyard.py indiehackers # IndieHackers only
  python3 scrape_graveyard.py build        # Rebuild _entries.json from .md files

Relevance gate: a post must contain at least one AI tool signal AND at least
one failure/problem signal. Single-keyword matches are rejected as noise.
"""

import json
import re
import sys
import hashlib
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.parse import quote_plus
from urllib.error import URLError, HTTPError
from xml.etree import ElementTree as ET

GRAVEYARD_DIR = Path(__file__).parent / "graveyard"
ENTRIES_JSON = GRAVEYARD_DIR / "_entries.json"

# Reddit requires a descriptive User-Agent to avoid 429s
REDDIT_UA = "VibeCodeGraveyard/2.0 (contact: matteo@trydydd.com)"

# ---------------------------------------------------------------------------
# Two-pillar relevance gate
# A post must match >= 1 keyword from EACH group to pass.
# ---------------------------------------------------------------------------

# Group 1: evidence that an AI coding tool was used
AI_TOOL_SIGNALS = [
    "vibe cod",              # vibe code / coding / coded (all inflections)
    "claude code",
    "bolt.new",
    "bolt new",
    "lovable.dev",
    "lovable app",
    "built with lovable",
    "using lovable",
    "v0.dev",
    "built with v0",
    "github copilot",
    "cursor ai",
    "using cursor",
    "built with cursor",
    "built in cursor",
    "cursor wrote",
    "cursor built",
    "cursor generated",
    "ai generated code",
    "ai-generated code",
    "ai wrote the",
    "ai wrote my",
    "ai wrote our",
    "ai coded",
    "ai codebase",
    "built with ai",
    "ai coding tool",
]

# Group 2: evidence of a problem, failure, or regret
FAILURE_SIGNALS = [
    "broke", "broken", "breaking",
    "crash", "crashing", "crashed",
    "security breach", "security hole", "security vulnerability", "security issue",
    "got hacked", "been hacked", "was hacked",
    "can't maintain", "cannot maintain", "hard to maintain", "unmaintainable",
    "technical debt",
    "spaghetti",
    "is a mess", "complete mess", "total mess", "what a mess",
    "disaster", "nightmare",
    "regret", "big mistake", "wrong choice",
    "scaling issue", "scaling problem", "can't scale", "won't scale", "doesn't scale",
    "need a developer", "need a dev", "need an engineer", "hire a developer", "hire a dev",
    "had to rewrite", "rewrote", "rewriting from scratch", "starting over",
    "abandoned", "shut down", "shutting down",
    "data loss", "lost all data", "lost data",
    "stopped working", "not working", "doesn't work",
    "production down", "site is down", "app is down",
    "out of control", "can't debug", "impossible to debug",
]

# ---------------------------------------------------------------------------
# Tool identification (for entry metadata; runs after relevance check)
# ---------------------------------------------------------------------------

TOOL_PATTERNS = {
    "Cursor": [
        r"\bcursor\s*ai\b",
        r"\busing\s+cursor\b",
        r"\bbuilt\s+(?:in|with)\s+cursor\b",
        r"\bcursor\s+(?:wrote|built|coded|generated)\b",
    ],
    "Claude Code": [r"\bclaude\s*code\b"],
    "Bolt": [r"\bbolt\.new\b", r"\bbolt\s+new\b"],
    "Lovable": [r"\blovable\b"],
    "v0": [r"\bv0\.dev\b", r"\bv0\s+by\s+vercel\b"],
    "Copilot": [r"\bgithub\s+copilot\b"],
    "AI": [r"\bvibe\s*cod", r"\bai[\s-]generated\s+code\b", r"\bai\s+(?:wrote|coded|built)\b"],
}

# ---------------------------------------------------------------------------
# Search query sets: compound phrases for precision over recall
# ---------------------------------------------------------------------------

REDDIT_QUERIES = [
    "vibe coding broke crash",
    "vibe coded technical debt",
    "cursor ai codebase mess",
    "bolt.new app crash broke",
    "lovable app broke crash",
    "claude code maintenance disaster",
    "ai generated code regret",
    "vibe code nightmare disaster",
    "ai startup security breach hacked",
    "ai codebase can't maintain unmaintainable",
    "vibe coding abandoned shut down",
    "ai codebase rewrite starting over",
]

REDDIT_SUBREDDITS = [
    "EntrepreneurRideAlong",
    "SaaS",
    "startups",
    "SideProject",
]

MIN_REDDIT_SCORE = 3

HN_QUERIES = [
    "vibe coding disaster broke",
    "vibe coded codebase mess",
    "cursor ai broke crashed",
    "bolt.new app broke",
    "lovable app broke",
    "ai generated code maintenance nightmare",
    "vibe coding security breach",
    "ai codebase rewrite regret",
    "vibe coding abandoned",
    "ai startup technical debt disaster",
]

MIN_HN_POINTS = 3


# ---------------------------------------------------------------------------
# Utility
# ---------------------------------------------------------------------------

def is_relevant(text):
    """Two-pillar gate: must contain an AI tool signal AND a failure signal."""
    lower = text.lower()
    has_tool = any(sig in lower for sig in AI_TOOL_SIGNALS)
    has_failure = any(sig in lower for sig in FAILURE_SIGNALS)
    return has_tool and has_failure


def detect_tool(text):
    """Identify the specific AI tool mentioned; fallback to 'AI'."""
    lower = text.lower()
    for tool, patterns in TOOL_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, lower):
                return tool
    return "AI"


def make_entry_id(url, title):
    return hashlib.md5(f"{url}:{title}".encode()).hexdigest()[:12]


def entry_exists(entry_id):
    return (GRAVEYARD_DIR / f"entry-{entry_id}.md").exists()


def fetch_json(url, ua="VibeCodeGraveyard/2.0", timeout=12):
    try:
        req = Request(url, headers={"User-Agent": ua})
        with urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode("utf-8"))
    except (URLError, HTTPError) as e:
        print(f"  HTTP error {url[:70]}: {e}")
    except Exception as e:
        print(f"  Error {url[:70]}: {e}")
    return None


def fetch_xml(url, ua="VibeCodeGraveyard/2.0", timeout=12):
    try:
        req = Request(url, headers={"User-Agent": ua})
        with urlopen(req, timeout=timeout) as r:
            return ET.fromstring(r.read().decode("utf-8"))
    except (URLError, HTTPError) as e:
        print(f"  HTTP error {url[:70]}: {e}")
    except ET.ParseError as e:
        print(f"  XML parse error {url[:70]}: {e}")
    except Exception as e:
        print(f"  Error {url[:70]}: {e}")
    return None


def strip_html(text):
    return re.sub(r"<[^>]+>", "", text).strip()


# ---------------------------------------------------------------------------
# Scrapers
# ---------------------------------------------------------------------------

def _process_reddit_post(p, source, candidates, seen_ids):
    post_id = p.get("id", "")
    if not post_id or post_id in seen_ids:
        return
    if p.get("score", 0) < MIN_REDDIT_SCORE:
        return

    title = (p.get("title") or "").strip()
    selftext = (p.get("selftext") or "").strip()
    if selftext in ("[deleted]", "[removed]"):
        selftext = ""

    if not is_relevant(f"{title} {selftext}"):
        return

    seen_ids.add(post_id)
    permalink = f"https://reddit.com{p.get('permalink', '')}"
    date = datetime.fromtimestamp(
        p.get("created_utc", 0), tz=timezone.utc
    ).strftime("%Y-%m-%d")

    candidates.append({
        "title": title,
        "description": selftext[:600] or title,
        "url": permalink,
        "date": date,
        "source_site": source,
        "score": p.get("score", 0),
    })


def scrape_reddit():
    """Search Reddit via native JSON API with upvote filtering (no RSSHub)."""
    print("Scraping Reddit...")
    candidates = []
    seen_ids = set()

    # Site-wide targeted searches
    for query in REDDIT_QUERIES:
        url = (
            f"https://www.reddit.com/search.json"
            f"?q={quote_plus(query)}&sort=new&limit=25&type=link"
        )
        data = fetch_json(url, ua=REDDIT_UA)
        if data:
            for child in data.get("data", {}).get("children", []):
                _process_reddit_post(child.get("data", {}), "Reddit", candidates, seen_ids)
        time.sleep(1.5)  # Reddit rate limit

    # Subreddit-restricted searches for core signals
    sub_queries = ["vibe coding", "vibe coded", "cursor ai", "bolt.new", "lovable app"]
    for sub in REDDIT_SUBREDDITS:
        for query in sub_queries:
            url = (
                f"https://www.reddit.com/r/{sub}/search.json"
                f"?q={quote_plus(query)}&restrict_sr=1&sort=new&limit=10&type=link"
            )
            data = fetch_json(url, ua=REDDIT_UA)
            if data:
                for child in data.get("data", {}).get("children", []):
                    _process_reddit_post(child.get("data", {}), f"r/{sub}", candidates, seen_ids)
            time.sleep(1.5)

    print(f"  Found {len(candidates)} relevant Reddit posts")
    return candidates


def scrape_indiehackers():
    """Scrape IndieHackers RSS feed."""
    print("Scraping IndieHackers...")
    candidates = []

    root = fetch_xml("https://www.indiehackers.com/feed")
    if root is None:
        return candidates

    for item in root.iter("item"):
        title = strip_html((item.findtext("title") or "").strip())
        link = (item.findtext("link") or "").strip()
        description = strip_html((item.findtext("description") or "").strip())
        pubdate = (item.findtext("pubDate") or "").strip()

        if not title or not link:
            continue
        if not is_relevant(f"{title} {description}"):
            continue

        candidates.append({
            "title": title,
            "description": description[:600],
            "url": link,
            "date": pubdate or datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            "source_site": "IndieHackers",
            "score": 0,
        })

    print(f"  Found {len(candidates)} relevant IndieHackers posts")
    return candidates


def scrape_hn():
    """Search Hacker News via Algolia API with points filtering."""
    print("Scraping Hacker News...")
    candidates = []
    seen_ids = set()

    for term in HN_QUERIES:
        url = (
            f"https://hn.algolia.com/api/v1/search"
            f"?query={quote_plus(term)}&tags=story"
            f"&numericFilters=points%3E%3D{MIN_HN_POINTS}"
            f"&hitsPerPage=10"
        )
        data = fetch_json(url)
        if not data:
            continue

        for hit in data.get("hits", []):
            obj_id = hit.get("objectID", "")
            if not obj_id or obj_id in seen_ids:
                continue

            title = (hit.get("title") or "").strip()
            story_text = strip_html((hit.get("story_text") or "").strip())

            if not is_relevant(f"{title} {story_text}"):
                continue

            seen_ids.add(obj_id)
            created = hit.get("created_at_i", 0)
            date = (
                datetime.fromtimestamp(created, tz=timezone.utc).strftime("%Y-%m-%d")
                if created
                else datetime.now(timezone.utc).strftime("%Y-%m-%d")
            )
            hn_url = hit.get("url") or f"https://news.ycombinator.com/item?id={obj_id}"

            candidates.append({
                "title": title,
                "description": story_text[:600] or f"Discussed on Hacker News ({hit.get('points', 0)} points).",
                "url": hn_url,
                "date": date,
                "source_site": "Hacker News",
                "score": hit.get("points", 0),
            })

    print(f"  Found {len(candidates)} relevant HN posts")
    return candidates


# ---------------------------------------------------------------------------
# Entry writing
# ---------------------------------------------------------------------------

def write_entry(entry, entry_id):
    """Write a markdown entry file; returns True if new, False if already existed."""
    GRAVEYARD_DIR.mkdir(parents=True, exist_ok=True)
    if entry_exists(entry_id):
        return False

    tool = detect_tool(entry["title"] + " " + entry.get("description", ""))
    safe_title = entry["title"].replace('"', "'")

    content = f"""---
id: {entry_id}
name: "{safe_title}"
tool: {tool}
status: Active
date: {entry["date"]}
source: {entry.get("url", "")}
source_site: {entry.get("source_site", "Unknown")}
founder_handle: ""
---

{entry.get("description", "")}
"""
    (GRAVEYARD_DIR / f"entry-{entry_id}.md").write_text(content)
    return True


# ---------------------------------------------------------------------------
# JSON index builder
# ---------------------------------------------------------------------------

def build_entries_json():
    """Scan graveyard/*.md and rebuild _entries.json for the frontend."""
    print("Building _entries.json...")
    entries = []

    for md_file in sorted(GRAVEYARD_DIR.glob("entry-*.md")):
        content = md_file.read_text()
        if not content.startswith("---"):
            continue
        parts = content.split("---", 2)
        if len(parts) < 3:
            continue

        fm = {}
        for line in parts[1].strip().split("\n"):
            if ":" in line:
                key, _, val = line.partition(":")
                fm[key.strip()] = val.strip().strip('"')

        body = parts[2].strip()
        entries.append({
            "id": fm.get("id", ""),
            "name": fm.get("name", "Unknown"),
            "tool": fm.get("tool", "AI"),
            "status": fm.get("status", "Active"),
            "date": fm.get("date", ""),
            "description": body[:300] if body else "",
            "source": fm.get("source", ""),
        })

    ENTRIES_JSON.write_text(json.dumps(entries, indent=2))
    print(f"  Wrote {len(entries)} entries to _entries.json")
    return entries


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def deduplicate(entries):
    seen = set()
    out = []
    for e in entries:
        url = e.get("url", "")
        if url and url not in seen:
            seen.add(url)
            out.append(e)
    return out


def main():
    GRAVEYARD_DIR.mkdir(parents=True, exist_ok=True)

    raw_args = sys.argv[1:]
    flags = {a for a in raw_args if a.startswith("--")}
    args = [a for a in raw_args if not a.startswith("--")]
    dry_run = "--dry-run" in flags
    mode = args[0].lower() if args else "all"

    if mode == "build":
        build_entries_json()
        return

    all_candidates = []

    if mode in ("all", "reddit"):
        all_candidates.extend(scrape_reddit())
    if mode in ("all", "indiehackers"):
        all_candidates.extend(scrape_indiehackers())
    if mode in ("all", "hn"):
        all_candidates.extend(scrape_hn())

    candidates = deduplicate(all_candidates)
    print(f"\nRelevant candidates: {len(candidates)}")

    if dry_run:
        print("\n--- DRY RUN (not writing files) ---")
        for c in sorted(candidates, key=lambda x: -x.get("score", 0)):
            tool = detect_tool(c["title"] + " " + c.get("description", ""))
            print(f"  [{c['source_site']} score={c.get('score', '?')}] [{tool}]")
            print(f"  {c['title'][:80]}")
            print(f"  {c['url']}")
            print()
        return

    new_count = 0
    for c in candidates:
        entry_id = make_entry_id(c["url"], c["title"])
        if write_entry(c, entry_id):
            new_count += 1
            tool = detect_tool(c["title"] + " " + c.get("description", ""))
            print(f"  + [{tool}] {c['title'][:65]}")

    print(f"\n{new_count} new entries written")
    build_entries_json()


if __name__ == "__main__":
    main()
