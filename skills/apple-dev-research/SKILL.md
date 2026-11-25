---
name: apple-dev-research
description: "Apple developer articles: search Swift, SwiftUI, Xcode, iOS, and macOS community blogs, tutorials, and write-ups, not official docs."
---

# Apple Developer Research

Bundled commands use `$PLUGIN_ROOT` (`$env:PLUGIN_ROOT` in PowerShell; same path suffix) for the plugin root. Set it once: use the host's plugin-root variable when defined (Claude Code: `PLUGIN_ROOT="$CLAUDE_PLUGIN_ROOT"`), otherwise the absolute path of this plugin's root directory.

Use Apple Dev Search for Apple-platform community content when the user wants articles, tutorials, or reading material rather than official docs or generic web results. Do not hard-code service counts; query `--counts` when counts matter.

## Workflow

1. Start with a focused query using the user's wording. Narrow broad results
   with `--title-only` and use `--recent` for a recent-articles feed.
2. Open promising articles when the search snippet cannot establish relevance.
3. Give the direct article links with a short reason for each selection. If the
   service request fails, report the error and use another available search source.

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
