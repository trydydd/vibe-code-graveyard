#!/usr/bin/env python3
"""
Vibe Code Graveyard — Entry Scraper

Scrapes Reddit, IndieHackers RSS, and HN for public confessions of
AI-generated codebase problems. Outputs markdown entry files and
a JSON index for the frontend.

Usage:
  python3 scrape_graveyard.py          # Run all scrapers
  python3 scrape_graveyard.py reddit   # Reddit only
  python3 scrape_graveyard.py indiehackers  # IndieHackers only
  python3 scrape_graveyard.py hn      # Hacker News only
  python3 scrape_graveyard.py build   # Just rebuild _entries.json from existing .md files
"""

import json
import os
import re
import sys
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import urlopen, Request
from xml.etree import ElementTree as ET

GRAVEYARD_DIR = Path(__file__).parent / "graveyard"
ENTRIES_JSON = GRAVEYARD_DIR / "_entries.json"

# Keywords that signal a vibe-coded confession or problem
KEYWORDS = [
    "vibe coded", "vibe-coded", "vibe coded",
    "cursor", "claude code", "copilot",
    "bolt.new", "bolt new", "lovable", "v0",
    "ai generated code", "ai codebase",
    "codebase is a mess", "can't maintain",
    "technical debt", "spaghetti code",
    "need a developer", "need engineer",
    "app is breaking", "app keeps crashing",
    "ai wrote this", "built with ai",
    "cursor generated", "claude generated",
]

# AI tool detection patterns
TOOL_PATTERNS = {
    "Cursor": [r"\bcursor\b"],
    "Claude Code": [r"\bclaude\s*code\b"],
    "Bolt": [r"\bbolt\.new\b", r"\bbolt\b"],
    "Lovable": [r"\blovable\b"],
    "v0": [r"\bv0\b", r"\bv0\.dev\b"],
    "Copilot": [r"\bcopilot\b"],
    "AI": [r"\bai\s*(generated|wrote|built|coded)\b", r"\bvibe\s*cod"],
}


def detect_tool(text):
    """Detect which AI tool is mentioned in the text."""
    text_lower = text.lower()
    for tool, patterns in TOOL_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, text_lower):
                return tool
    return "AI"


def make_entry_id(url, title):
    """Generate a stable ID for deduplication."""
    raw = f"{url}:{title}"
    return hashlib.md5(raw.encode()).hexdigest()[:12]


def matches_keywords(text):
    """Check if text contains any of our keywords."""
    text_lower = text.lower()
    return any(kw.lower() in text_lower for kw in KEYWORDS)


def extract_keywords_hit(text):
    """Return which keywords matched."""
    text_lower = text.lower()
    return [kw for kw in KEYWORDS if kw.lower() in text_lower]


def scrape_reddit():
    """Scrape Reddit via RSSHub for vibe-coded confessions."""
    print("🔍 Scraping Reddit...")
    entries = []

    # RSSHub RSS feeds for subreddit searches
    feeds = [
        ("r/EntrepreneurRideAlong", "https://rsshub.app/reddit/search/EntrepreneurRideAlong/30/day"),
        ("r/indiehackers", "https://rsshub.app/reddit/search/indiehackers/30/day"),
        ("r/SaaS", "https://rsshub.app/reddit/search/SaaS/30/day"),
        ("r/startups", "https://rsshub.app/reddit/search/startups/30/day"),
        ("r/SideProject", "https://rsshub.app/reddit/search/SideProject/30/day"),
    ]

    for subreddit, feed_url in feeds:
        try:
            req = Request(feed_url, headers={"User-Agent": "VibeCodeGraveyard/1.0"})
            with urlopen(req, timeout=10) as response:
                xml = response.read().decode("utf-8")
            root = ET.fromstring(xml)

            for item in root.iter("item"):
                title_el = item.find("title")
                link_el = item.find("link")
                desc_el = item.find("description")
                pubdate_el = item.find("pubDate")

                if not title_el is None and not link_el is None:
                    title = title_el.text or ""
                    link = link_el.text or ""
                    description = desc_el.text or "" if desc_el is not None else ""
                    pubdate = pubdate_el.text or "" if pubdate_el is not None else ""

                    text = f"{title} {description}"
                    if matches_keywords(text):
                        entries.append({
                            "source_subreddit": subreddit,
                            "title": title.strip(),
                            "description": description.strip()[:500] if description.strip() else "AI-generated codebase issues reported publicly.",
                            "url": link.strip(),
                            "date": pubdate.strip() if pubdate.strip() else datetime.now(timezone.utc).strftime("%Y-%m-%d"),
                        })
        except Exception as e:
            print(f"  ⚠ Could not fetch {subreddit}: {e}")

    print(f"  Found {len(entries)} potential entries from Reddit")
    return entries


def scrape_indiehackers():
    """Scrape IndieHackers RSS feed."""
    print("🔍 Scraping IndieHackers...")
    entries = []

    try:
        req = Request("https://www.indiehackers.com/feed", headers={"User-Agent": "VibeCodeGraveyard/1.0"})
        with urlopen(req, timeout=10) as response:
            xml = response.read().decode("utf-8")
        root = ET.fromstring(xml)

        for item in root.iter("item"):
            title_el = item.find("title")
            link_el = item.find("link")
            desc_el = item.find("description")
            pubdate_el = item.find("pubDate")

            if title_el is not None and link_el is not None:
                title = title_el.text or ""
                link = link_el.text or ""
                description = desc_el.text or "" if desc_el is not None else ""
                pubdate = pubdate_el.text or "" if pubdate_el is not None else ""

                text = f"{title} {description}"
                if matches_keywords(text):
                    entries.append({
                        "source_subreddit": "IndieHackers",
                        "title": title.strip(),
                        "description": description.strip()[:500] if description.strip() else "AI-generated codebase issues reported publicly.",
                        "url": link.strip(),
                        "date": pubdate.strip() if pubdate.strip() else datetime.now(timezone.utc).strftime("%Y-%m-%d"),
                    })
    except Exception as e:
        print(f"  ⚠ Could not fetch IndieHackers: {e}")

    print(f"  Found {len(entries)} potential entries from IndieHackers")
    return entries


def scrape_hn():
    """Scrape Hacker News via Algolia API."""
    print("🔍 Scraping Hacker News...")
    entries = []

    # Search HN via Algolia (free, public API)
    search_terms = ["vibe coded", "AI generated code", "cursor codebase", "technical debt AI"]

    for term in search_terms:
        try:
            url = f"https://hn.algolia.com/api/v1/search?query={term.replace(' ', '+')}&tags=story&hitsPerPage=10"
            req = Request(url, headers={"User-Agent": "VibeCodeGraveyard/1.0"})
            with urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode("utf-8"))

            for hit in data.get("hits", []):
                if matches_keywords(hit.get("title", "") + " " + hit.get("story_text", "")):
                    entries.append({
                        "source_subreddit": "Hacker News",
                        "title": hit.get("title", "").strip(),
                        "description": (hit.get("story_text") or "Discussed on Hacker News.").strip()[:500],
                        "url": hit.get("url") or f"https://news.ycombinator.com/item?id={hit.get('objectID')}",
                        "date": datetime.fromtimestamp(hit.get("created_at_i", 0), tz=timezone.utc).strftime("%Y-%m-%d"),
                    })
        except Exception as e:
            print(f"  ⚠ Could not search HN for '{term}': {e}")

    # Deduplicate by URL
    seen = set()
    unique = []
    for e in entries:
        if e["url"] not in seen:
            seen.add(e["url"])
            unique.append(e)

    print(f"  Found {len(unique)} unique entries from HN")
    return unique


def write_entry(entry, entry_id):
    """Write a single entry as a markdown file."""
    GRAVEYARD_DIR.mkdir(parents=True, exist_ok=True)

    # Check if already exists
    existing_files = list(GRAVEYARD_DIR.glob("entry-*.md"))
    for f in existing_files:
        if entry_id in f.name:
            return False  # Already exists

    filename = f"entry-{entry_id}.md"
    filepath = GRAVEYARD_DIR / filename

    safe_title = entry['title'].replace('"', "'")
    md = f"""---
id: {entry_id}
name: "{safe_title}"
tool: {entry.get('tool', 'AI')}
status: Active
date: {entry['date']}
source: {entry.get('url', '')}
source_site: {entry.get('source_subreddit', 'Unknown')}
founder_handle: ""
---

{entry.get('description', '')}

"""

    filepath.write_text(md)
    return True


def build_entries_json():
    """Scan graveyard/*.md files and build _entries.json for the frontend."""
    print("🔨 Building _entries.json...")
    entries = []

    for md_file in sorted(GRAVEYARD_DIR.glob("entry-*.md")):
        content = md_file.read_text()

        # Parse YAML frontmatter (simple parser)
        if not content.startswith("---"):
            continue

        parts = content.split("---", 2)
        if len(parts) < 3:
            continue

        frontmatter_text = parts[1].strip()
        body = parts[2].strip()

        frontmatter = {}
        for line in frontmatter_text.split("\n"):
            if ":" in line:
                key, _, value = line.partition(":")
                frontmatter[key.strip()] = value.strip().strip('"')

        entries.append({
            "id": frontmatter.get("id", ""),
            "name": frontmatter.get("name", "Unknown"),
            "tool": frontmatter.get("tool", "AI"),
            "status": frontmatter.get("status", "Active"),
            "date": frontmatter.get("date", ""),
            "description": body[:300] if body else "",
            "source": frontmatter.get("source", ""),
        })

    ENTRIES_JSON.write_text(json.dumps(entries, indent=2))
    print(f"  Wrote {len(entries)} entries to _entries.json")
    return entries


def main():
    GRAVEYARD_DIR.mkdir(parents=True, exist_ok=True)

    mode = sys.argv[1].lower() if len(sys.argv) > 1 else "all"

    if mode == "build":
        build_entries_json()
        return

    all_raw = []

    if mode in ("all", "reddit"):
        all_raw.extend(scrape_reddit())
    if mode in ("all", "indiehackers"):
        all_raw.extend(scrape_indiehackers())
    if mode in ("all", "hn"):
        all_raw.extend(scrape_hn())

    # Deduplicate by URL
    seen_urls = set()
    unique_raw = []
    for e in all_raw:
        if e["url"] not in seen_urls:
            seen_urls.add(e["url"])
            unique_raw.append(e)

    print(f"\n📊 Total unique entries found: {len(unique_raw)}")

    # Write entries that don't exist yet
    new_count = 0
    for raw in unique_raw:
        entry_id = make_entry_id(raw["url"], raw["title"])
        raw["tool"] = detect_tool(raw["title"] + " " + raw["description"])
        raw["date"] = raw.get("date", datetime.now(timezone.utc).strftime("%Y-%m-%d"))

        if write_entry(raw, entry_id):
            new_count += 1
            print(f"  ✍ {raw['title'][:60]}... [{raw['tool']}]")

    print(f"\n✅ {new_count} new entries written to graveyard/")

    # Rebuild JSON index
    build_entries_json()


if __name__ == "__main__":
    main()
