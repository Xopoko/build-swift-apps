---
name: appstore-release-notes-writer
description: Use when the requested App Store artifact is What's New release notes or promotional text, drafted from git history, bullets, or free text and optionally localized. Not for full listing translation, canonical metadata field sync, or subscription/IAP display names.
---

# App Store Release Notes Writer

Write human-focused release notes, optionally localized to every existing metadata locale.

Use `appstore-metadata-sync` for general listing metadata edits, `appstore-metadata-localizer` for full listing translation, and `appstore-subscription-localizer` for subscription/IAP display-name localization.

## Preconditions

- Canonical metadata from `asc metadata pull --app "APP_ID" --version "1.2.3" --dir "./metadata"` or user-provided keywords.
- Auth configured for upload.
- Primary locale is `en-US` unless specified.
- Read `references/release_notes_guidelines.md`.
- Use highest semver under `metadata/version/`; locales are the JSON files there.

## Workflow

1. Gather input:
   - Git log: `git describe --tags --abbrev=0` then `git log <tag>..HEAD --oneline --no-merges`; remove merges/deps/CI/format noise.
   - User bullets or free text.
   - If absent, ask what changed.
2. Classify user-visible changes into `New`, `Improved`, `Fixed`; omit empty sections.
3. Draft primary locale notes:
   - lead with the clearest user-facing hook in the first ~170 chars;
   - describe user impact, not implementation;
   - use concrete action verbs;
   - naturally echo relevant local keywords from `metadata/version/<version>/<locale>.json` when present;
   - target 500-1500 chars, hard limit 4000.
4. If requested, draft `promotionalText` <= 170 chars.
5. Show draft with character count and wait for approval before localizing.
6. Localize approved notes:
   - formal/professional register and formal "you" where applicable;
   - adapt idioms and tone to local market;
   - echo locale-specific keywords naturally;
   - validate What's New <= 4000 and promo <= 170; shorten, never truncate mid-sentence.
7. Present a locale table with first 80 chars, counts, promo text/counts; wait for upload approval.
8. Upload:
   ```bash
   asc apps info edit --app "APP_ID" --version-id "VERSION_ID" --locale "en-US" --whats-new "..."
   asc metadata push --app "APP_ID" --version "1.2.3" --dir "./metadata" --dry-run
   asc metadata push --app "APP_ID" --version "1.2.3" --dir "./metadata"
   ```
   Include promo via `--promotional-text` or write `promotionalText` into canonical JSON before push.

## Paths

- Keywords/current notes: `metadata/version/{latest-version}/{locale}.json`
- Fields: `keywords`, `whatsNew`, optional `promotionalText`
- Canonical tree is shared with `asc metadata pull/push/keywords`.

## Rules

- What's New is not App Store search-indexed; write for conversion and clarity.
- Promotional text can update without a new submission.
- The visible 170-char preview matters most.
- On partial upload failure, report successes/failures and retry failed locales only.
- Use `appstore-metadata-localizer` for full listing translation and `appstore-aso-auditor` for keyword research.
