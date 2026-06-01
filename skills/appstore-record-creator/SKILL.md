---
name: appstore-record-creator
description: Create a new App Store Connect app record through visible browser automation when no public API exists. Use for the New App web form after the bundle ID is registered.
---

# App Store Record Creator

Opt-in local browser automation for App Store Connect app creation. The user must be signed in; the bundle ID must already exist.

## Preconditions

- Playwright, Cursor browser MCP, or equivalent visible browser automation.
- User can complete login and 2FA.
- Inputs: app name (<=30 chars), registered unused bundle ID, SKU, platform(s), primary language, user access.

## Guardrails

- Never export/store cookies.
- Use a visible session only.
- Pause before final Create click in standalone scripts.
- Do not retry Create automatically.

## Workflow

1. Preflight:
   ```bash
   asc bundle-ids create --identifier "com.example.app" --name "My App" --platform IOS
   asc apps list --bundle-id "com.example.app" --output json
   ```
2. Open `https://appstoreconnect.apple.com/apps` and confirm login.
3. Click the blue `+` New App button, then the `New App` menu item. It is a dropdown first, not a direct dialog.
4. Fill fields:
   - Platform checkboxes: iOS, macOS, tvOS, visionOS; multiple allowed.
   - `Name`, max 30 chars.
   - `Primary Language` combobox/select.
   - `Bundle ID` select: wait until async loading finishes after platform selection; choose label like `My App - com.example.app`.
   - `SKU`.
   - `User Access`: required radio, `Limited Access` or `Full Access`.
5. User Access radios may have span overlays; scroll the radio input into view and click the radio ref directly if accessibility click is intercepted.
6. If Ember validation does not notice filled fields, clear/retype one text value slowly.
7. Confirm, click Create, wait for `/apps/<APP_ID>/...`.
8. Verify:
   ```bash
   asc apps view --id "APP_ID" --output json --pretty
   asc apps list --bundle-id "com.example.app" --output json
   ```
9. Hand off:
   ```bash
   asc app-setup info set --app "APP_ID" --primary-locale "en-US"
   asc app-setup categories set --app "APP_ID" --primary GAMES
   asc web apps availability create --app "APP_ID" --territory "USA,GBR" --available-in-new-territories true
   ```
   Use the web availability flow only for first bootstrap; later use `asc pricing availability edit`.

## Failure Handling

If a field/button cannot be located, stop, capture a screenshot, report the last step, and ask the user to inspect validation errors. Selectors can change; prefer role/label/text selectors over CSS.
