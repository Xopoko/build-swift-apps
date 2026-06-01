---
name: appstore-screenshot-pipeline
description: Orchestrate iOS screenshot automation with xcodebuild/simctl, AXe plans, Koubou framing, review artifacts, and `asc screenshots` upload.
---

# App Store Screenshot Pipeline

Build/run the app, capture deterministic screenshots, frame them, review them, then upload through `asc`.

Defaults: settings `.asc/screenshot.settings.json`, plan `.asc/screenshots.json`, raw `./screenshots/raw`, framed `./screenshots/framed`, frame device `iphone-air`, Koubou `0.18.1`.

## Workflow

1. Verify the current CLI surface with `asc screenshots --help` and subcommand help.
2. Create/update settings with bundle id, project/scheme, UDID, paths, `frame_enabled`, `upload_enabled`, and upload target.
3. Build/install/launch:

   ```bash
   xcrun simctl boot "$UDID" || true
   xcodebuild -project "App.xcodeproj" -scheme "App" -configuration Debug \
     -destination "platform=iOS Simulator,id=$UDID" -derivedDataPath ".build/DerivedData" build
   xcrun simctl install "$UDID" ".build/DerivedData/Build/Products/Debug-iphonesimulator/App.app"
   xcrun simctl launch "$UDID" "com.example.app"
   ```

   Use `xcodebuild -showBuildSettings` if the bundle path differs.

4. Capture with plan:

   ```bash
   asc screenshots run --plan ".asc/screenshots.json" --udid "$UDID" --output json
   ```

   During plan authoring use AXe primitives: `axe describe-ui`, `axe tap`, `axe type`, `axe screenshot`.

5. Frame with pinned Koubou:

   ```bash
   pip install koubou==0.18.1
   kou --version
   asc screenshots list-frame-devices --output json
   asc screenshots frame --input "./screenshots/raw/home.png" --output-dir "./screenshots/framed" --device "iphone-air" --output json
   ```

   If frames are missing, run `kou setup-frames` once with network access.

6. Review:

   ```bash
   asc screenshots review-generate --framed-dir "./screenshots/framed" --output-dir "./screenshots/review"
   asc screenshots review-open --output-dir "./screenshots/review"
   asc screenshots review-approve --all-ready --output-dir "./screenshots/review"
   ```

7. Prefer plan/apply for reviewed batches so existing remote screenshots are considered:

   ```bash
   asc screenshots plan --app "APP_ID" --version "1.2.3" --review-output-dir "./screenshots/review" --output json
   asc screenshots apply --app "APP_ID" --version "1.2.3" --review-output-dir "./screenshots/review" --confirm --output json
   ```

   Direct upload:

   ```bash
   asc screenshots upload --version-localization "LOC_ID" --path "./screenshots/framed" --device-type "IPHONE_65" --output json
   ```

## Locale Capture

Do not rely on `xcrun simctl launch ... -e AppleLanguages`; it does not reliably switch app language. Prefer one simulator UDID per locale, set simulator-wide defaults, then capture:

```bash
set_simulator_locale() {
  UDID="$1"; LOCALE="$2"; LANG="${LOCALE%%-*}"; APPLE_LOCALE="${LOCALE/-/_}"
  xcrun simctl boot "$UDID" || true
  xcrun simctl spawn "$UDID" defaults write NSGlobalDomain AppleLanguages -array "$LANG"
  xcrun simctl spawn "$UDID" defaults write NSGlobalDomain AppleLocale -string "$APPLE_LOCALE"
}

set_simulator_locale "$UDID" "de-DE"
xcrun simctl terminate "$UDID" "com.example.app" || true
asc screenshots capture --bundle-id "com.example.app" --name "home" --udid "$UDID" --output-dir "./screenshots/raw/de-DE" --output json
```

For manual launches: `xcrun simctl launch "$UDID" "com.example.app" -AppleLanguages "(de)" -AppleLocale "de_DE"`. Parallelize locales with distinct UDIDs and frame/review after `wait`.

## Rules

Use explicit long flags and JSON for machine steps. Ensure files exist before upload. Treat local screenshot automation as experimental in user-facing notes. Use plan/apply for append-limit guardrails. If framing checks fail, reinstall `koubou==0.18.1`. Validate with `asc screenshots sizes --output table` and `asc screenshots list --version-localization "LOC_ID" --output table`.
