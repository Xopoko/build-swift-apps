#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime
from typing import Any
from urllib.parse import urlencode
from urllib.request import Request, urlopen

BASE_URL = "https://appledevsearch.com"
API_BASE_URL = f"{BASE_URL}/api"
USER_AGENT = "build-swift-apps-apple-dev-research/1.0"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Query Apple Dev Search without using the browser UI."
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--query", help="Search query to send to /api/search.")
    mode.add_argument(
        "--recent",
        action="store_true",
        help="Fetch recent articles from /api/recent.",
    )
    mode.add_argument(
        "--counts",
        action="store_true",
        help="Fetch live counts from /api/counts.",
    )
    parser.add_argument(
        "--title-only",
        action="store_true",
        help="Search only article titles.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=5,
        help="Maximum number of results to print.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print structured JSON instead of text.",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=20.0,
        help="HTTP timeout in seconds.",
    )
    args = parser.parse_args()
    if args.limit < 1:
        parser.error("--limit must be >= 1")
    if args.query is not None and not args.query.strip():
        parser.error("--query cannot be blank")
    return args


def fetch_json(path: str, timeout: float, params: dict[str, Any] | None = None) -> Any:
    url = f"{API_BASE_URL}{path}"
    if params:
        url = f"{url}?{urlencode(params)}"
    request = Request(
        url,
        headers={
            "Accept": "application/json",
            "User-Agent": USER_AGENT,
        },
    )
    with urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def collapse_whitespace(value: str | None) -> str:
    if not value:
        return ""
    return re.sub(r"\s+", " ", value).strip()


def format_date(value: str | None) -> str:
    if not value:
        return ""
    normalized = value.strip()
    if normalized.endswith("Z"):
        normalized = normalized[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        return value
    return parsed.date().isoformat()


def build_search_url(query: str, title_only: bool) -> str:
    fragment = urlencode({"q": query, "titleOnly": str(title_only).lower()})
    return f"{BASE_URL}/#{fragment}"


def simplify_hit(hit: dict[str, Any]) -> dict[str, str]:
    source = hit.get("_source", {})
    highlight = hit.get("highlight", {}).get("body")
    if isinstance(highlight, list):
        snippet = " // ".join(collapse_whitespace(item) for item in highlight if item)
    elif isinstance(highlight, str):
        snippet = collapse_whitespace(highlight)
    else:
        snippet = collapse_whitespace(source.get("start"))

    return {
        "url": hit.get("_id", ""),
        "title": collapse_whitespace(source.get("title")),
        "blog": collapse_whitespace(source.get("blogTitle")),
        "date": format_date(source.get("postDate")),
        "snippet": collapse_whitespace(snippet),
    }


def render_text_results(
    *,
    mode: str,
    hits: list[dict[str, str]],
    total: dict[str, Any] | None = None,
    query: str | None = None,
    title_only: bool = False,
) -> None:
    if mode == "search":
        relation = total.get("relation") if isinstance(total, dict) else None
        value = total.get("value") if isinstance(total, dict) else None
        if value is not None:
            suffix = "+" if relation == "gte" else ""
            print(f"Results: {value}{suffix}")
        print(f"Mode: {'title-only' if title_only else 'full-text'}")
        print(f"Query: {query}")
        print(f"Search URL: {build_search_url(query or '', title_only)}")
    elif mode == "recent":
        relation = total.get("relation") if isinstance(total, dict) else None
        value = total.get("value") if isinstance(total, dict) else None
        if value is not None:
            suffix = "+" if relation == "gte" else ""
            print(f"Recent articles available: {value}{suffix}")

    if not hits:
        print("No results.")
        return

    for index, item in enumerate(hits, start=1):
        prefix = f"{index}. "
        header_parts = [part for part in (item["date"], item["blog"], item["title"]) if part]
        print(f"{prefix}{' | '.join(header_parts)}")
        print(f"   URL: {item['url']}")
        if item["snippet"]:
            print(f"   Snippet: {item['snippet']}")


def main() -> int:
    args = parse_args()

    try:
        if args.counts:
            counts = fetch_json("/counts", args.timeout)
            if args.json:
                print(json.dumps(counts, ensure_ascii=False, indent=2))
            else:
                print(f"Articles: {counts.get('articleCount', 'unknown')}")
                print(f"Blogs: {counts.get('blogCount', 'unknown')}")
            return 0

        if args.recent:
            payload = fetch_json("/recent", args.timeout)
            raw_hits = payload.get("hits", {}).get("hits", [])
            items = [simplify_hit(hit) for hit in raw_hits[: args.limit]]
            if args.json:
                print(
                    json.dumps(
                        {
                            "mode": "recent",
                            "total": payload.get("hits", {}).get("total"),
                            "results": items,
                        },
                        ensure_ascii=False,
                        indent=2,
                    )
                )
            else:
                render_text_results(
                    mode="recent",
                    hits=items,
                    total=payload.get("hits", {}).get("total"),
                )
            return 0

        payload = fetch_json(
            "/search",
            args.timeout,
            params={
                "q": args.query.strip(),
                "titleOnly": str(args.title_only).lower(),
            },
        )
        raw_hits = payload.get("hits", {}).get("hits", [])
        items = [simplify_hit(hit) for hit in raw_hits[: args.limit]]
        if args.json:
            print(
                json.dumps(
                    {
                        "mode": "search",
                        "query": args.query.strip(),
                        "titleOnly": args.title_only,
                        "searchUrl": build_search_url(args.query.strip(), args.title_only),
                        "total": payload.get("hits", {}).get("total"),
                        "results": items,
                    },
                    ensure_ascii=False,
                    indent=2,
                )
            )
        else:
            render_text_results(
                mode="search",
                hits=items,
                total=payload.get("hits", {}).get("total"),
                query=args.query.strip(),
                title_only=args.title_only,
            )
        return 0
    except Exception as exc:
        print(f"appledevsearch.py failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
