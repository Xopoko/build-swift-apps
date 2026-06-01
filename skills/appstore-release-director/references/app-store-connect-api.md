# App Store Connect API

Use this reference when operating App Store Connect from Codex or a terminal.

## Tool Preference

Use project-provided scripts or Fastlane first when they exist and are current. Otherwise:

- Use the public `asc` CLI for App Store Connect workflows when available.
- Use `xcrun altool` for IPA validation, upload, and build-status checks when it is reliable in the environment.
- Use App Store Connect web UI only for operations not available through API tooling or when Apple requires interactive authentication.

## asc Pattern

Check availability:

```bash
command -v asc
asc --help
asc auth status
```

Discover command paths and schemas instead of guessing:

```bash
asc search "submit app for review"
asc search "upload build"
asc capabilities --area release --output table
asc schema --pretty "GET /v1/apps"
```

Run reads without mutation first. For mutations, prefer `--dry-run` when available and use `--confirm` only after inspecting the planned request:

```bash
asc apps list --bundle-id "com.example.app" --output json
asc versions list --app "APP_ID" --paginate --output json
asc release stage --app "APP_ID" --version "1.2.3" --build "BUILD_ID" --dry-run --output table
asc release stage --app "APP_ID" --version "1.2.3" --build "BUILD_ID" --confirm
```

Pipe JSON through `jq empty` before sending it:

```bash
jq empty body.json
```

## Common API Work

App discovery:

- Locate app by app Apple ID or bundle ID.
- List App Store versions for the app.
- Find the editable or inflight App Store version.
- List builds for the marketing version.

Metadata:

- Update app info categories.
- Update version localization fields such as description, keywords, marketing URL, support URL, and "What's New".
- Update App Store version release type.
- Update review details and review notes.
- Upload or verify screenshot sets if the project has API support for media uploads.

Build linking:

- Wait until build processing is valid and App Store eligible.
- Update the App Store version relationship to point at the processed build.
- Verify the version now includes that build relationship.

Review submission:

- Create a review submission for the app.
- Add a review submission item pointing at the App Store version.
- Submit the review submission.
- Verify state such as `WAITING_FOR_REVIEW`, `IN_REVIEW`, `ACCEPTED`, `REJECTED`, `CANCELED`, or `COMPLETE`.

Subscriptions and IAP:

- Create subscription groups and products.
- Add localizations.
- Set prices and availability.
- Add introductory offers.
- Attach review screenshots.
- Verify product state is ready to submit.

## Description Terms/EULA Update Pattern

Auto-renewable subscription apps commonly require a functional Terms of Use or EULA link in app metadata. A practical metadata footer is:

```text
Terms of Use: https://example.com/terms
Apple Standard EULA: https://www.apple.com/legal/internet-services/itunes/dev/stdeula/
Privacy Policy: https://example.com/privacy
```

Before submitting review, verify each link:

```bash
curl -I https://example.com/terms
curl -I https://www.apple.com/legal/internet-services/itunes/dev/stdeula/
curl -I https://example.com/privacy
```

If using a custom EULA, configure it in App Store Connect instead of only linking it in text.

## Old Submission Blocks New Submission

If a previous rejected or incomplete review submission blocks a new one:

1. Query current review submissions for the app.
2. Cancel the old active submission if the API and state allow it.
3. Poll until the old submission reaches a terminal state such as `COMPLETE` or `CANCELED`.
4. Create a new review submission.
5. Add the current App Store version item.
6. Submit the new review submission.

Do not keep adding new review items to an obsolete submission unless that is exactly what Apple expects for the current state.

## Resolution Center

App Review messages and Resolution Center threads may not be fully available through API-key tooling. If the user asks to read the issue:

- Check App Store Connect API state first.
- Check email text if provided.
- If API does not expose the message, state that web UI or Apple ID auth is required.
- Preserve the exact issue text in the release handoff.
