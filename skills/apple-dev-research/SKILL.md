---
name: apple-dev-research
description: Search Apple Dev Search for Swift, SwiftUI, Xcode, iOS, macOS, and Apple-platform community articles, tutorials, blogs, and write-ups.
---

# Apple Developer Research

Bundled commands use `$PLUGIN_ROOT` (`$env:PLUGIN_ROOT` in PowerShell; same path suffix) for the plugin root. Set it once: use the host's plugin-root variable when defined (Claude Code: `PLUGIN_ROOT="$CLAUDE_PLUGIN_ROOT"`), otherwise the absolute path of this plugin's root directory.

Use Apple Dev Search for Apple-platform community content when the user wants articles, tutorials, or reading material rather than official docs or generic web results. Do not hard-code service counts; query `--counts` when counts matter.

## Workflow

1. Start with one focused query using the user's wording.
2. Hard cap ordinary requests at 3 commands total: initial search plus 2 retries. Stop once 3 useful candidates are found.
3. If broad/noisy, retry with `--title-only` and tighter terms.
4. Use syntax when helpful: quotes, `|`, `-`, `*`, `~1`, parentheses.
5. For fresh reading lists, inspect `--recent`.
6. Verify selected article URLs with Crawl4AI only when snippets are insufficient or candidates are close. Avoid generic web search/Tavily/Firecrawl unless Crawl4AI fails.
7. Return 3-8 links with title, blog, date, URL, and one-line relevance.

## Commands

```bash
python3 "$PLUGIN_ROOT/skills/apple-dev-research/scripts/appledevsearch.py" --query 'build speed' --limit 5
python3 "$PLUGIN_ROOT/skills/apple-dev-research/scripts/appledevsearch.py" --query '"incremental builds" | "compile time"' --title-only --limit 5
python3 "$PLUGIN_ROOT/skills/apple-dev-research/scripts/appledevsearch.py" --query 'swift testing -uikit' --limit 5
python3 "$PLUGIN_ROOT/skills/apple-dev-research/scripts/appledevsearch.py" --recent --limit 8
python3 "$PLUGIN_ROOT/skills/apple-dev-research/scripts/appledevsearch.py" --counts
```

Use full text for errors/API/framework names; title-only for broad topics. Keep user terminology in at least one query before expanding synonyms.

Reusable search URL:

```text
https://appledevsearch.com/#q=<urlencoded query>&titleOnly=true|false
```

Mention exact queries used, separate title-only vs full-text results, prefer direct article links, and say when results are weak or empty.
