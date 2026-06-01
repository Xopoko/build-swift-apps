---
name: appstore-aso-auditor
description: Run an offline ASO audit on canonical App Store metadata under `./metadata` and, when available, add Astro MCP keyword-gap analysis and Apple app-tag context. Use after `asc metadata pull`.
---

# App Store ASO Auditor

Audit the latest local metadata version first; Astro keyword gaps and Apple-generated tags are additive signals.

## Preconditions

- Canonical metadata from `asc metadata pull --app "APP_ID" --version "1.2.3" --dir "./metadata"`.
- Normalize `asc migrate export` or `asc localizations download` output before auditing.
- Read `references/aso_rules.md` for rule details.
- Use highest semantic version under `metadata/version/`.
- Primary locale is `en-US` unless the user specifies another.

Paths:

- App-info fields: `metadata/app-info/{locale}.json`
- Version fields: `metadata/version/{latest-version}/{locale}.json`
- App name may be absent; fetch with `asc apps info list` or ask before flagging it.

## Offline Checks

1. Keyword waste: tokens in `subtitle` or `name` also present in `keywords`. For Arabic also compare variants without `ال`; for CJK split by punctuation/character groups.
2. Underused fields: keywords below 90/100 or subtitle below 20/30 chars.
3. Missing fields: empty `subtitle`, `keywords`, `description`, `whatsNew`; only flag `name` if present and empty.
4. Bad keyword separators: spaces after commas, semicolons, or pipes.
5. Cross-locale gaps: non-primary locale keywords identical to the primary locale.
6. Description coverage: keywords absent from description as conversion evidence, not Apple indexing evidence. Ignore Latin keywords in non-Latin descriptions when they target separate search paths.

Optional app tags:

```bash
asc app-tags list --app "APP_ID" --output json
asc app-tags view --app "APP_ID" --id "TAG_ID" --output json
```

Use tags only as classification evidence. Do not promise metadata changes will immediately alter Apple-generated tags.

## Astro Keyword Gaps

If Astro MCP is connected and the app is tracked:

- call `get_app_keywords`;
- add per-store tracking with `add_keywords` for locales/territories before querying non-US stores;
- run `extract_competitors_keywords` for 3-5 competitor app IDs;
- call `get_keyword_suggestions` and `search_rankings`;
- diff suggestions against title, subtitle, and keywords;
- rank gaps by popularity and note source.

Skip with an explicit note when Astro is unavailable, the app is not tracked, or a store is not tracked.

## Recommendations

Prioritize errors, keyword waste, utilization gaps, exact cross-locale duplicates, then Astro opportunities. Consider cross-field combos such as title/subtitle + keyword terms (for example adding a missing word that combines with an existing subtitle word).

## Output

Produce one report for the latest version directory:

```markdown
### ASO Audit Report
**App:** ... | **Primary Locale:** ...
**Metadata source:** metadata/version/<version>

#### Field Utilization
| Field | Value | Length | Limit | Usage |

#### Offline Checks
| # | Check | Severity | Field | Locale | Detail |

#### Keyword Gap Analysis
| Keyword | Popularity | Source | In Metadata? | Suggested Action |

#### Recommendations
1. ...
```

After edits, re-run the audit. For keyword-only follow-up prefer `asc metadata keywords diff/apply/sync`.
