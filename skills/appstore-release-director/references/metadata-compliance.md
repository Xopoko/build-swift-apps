# Metadata And Compliance

Use this reference before submitting an app or responding to App Review.

## App Metadata Checklist

Verify these fields in App Store Connect:

- App name and subtitle
- Bundle ID and SKU
- Primary and secondary category
- Age rating
- Copyright
- Description
- Keywords
- Support URL
- Privacy Policy URL
- Marketing URL if used
- Release type, phased release, and manual/automatic release choice
- Pricing and availability
- Content rights
- App Review contact info
- Demo account or explanation that no account is required
- Review notes for paid features, test mode, subscription flow, or hardware requirements

## Privacy Policy

A Privacy Policy URL is required for App Store submission. It must be functional, public, and relevant to the app being submitted.

It should cover:

- App name and company/legal entity.
- Contact email or postal contact.
- Data collected by the app.
- Data processed by backend services.
- Speech, audio, translation, analytics, crash logs, purchase, or account data if applicable.
- Data retention and deletion process.
- Third-party processors.
- Children's privacy if applicable.
- International data transfers if applicable.
- Effective date and update policy.

If drafting a policy from another company policy, keep the business/legal details but adapt data categories to the current app. Tell the user which facts still need legal owner confirmation.

## Terms Of Use / EULA

For auto-renewable subscriptions, App Review can block the submission if metadata lacks a functional Terms of Use or EULA link.

Use one of these approaches:

- Standard Apple EULA: include `https://www.apple.com/legal/internet-services/itunes/dev/stdeula/` in the app description or another metadata field accepted by Apple.
- Custom EULA: configure it in App Store Connect and link the public Terms page if the app has one.

The app description can include:

```text
Terms of Use: https://example.com/terms
Apple Standard EULA: https://www.apple.com/legal/internet-services/itunes/dev/stdeula/
Privacy Policy: https://example.com/privacy
```

Verify each link with `curl` and a browser if App Review complained about it.

## Subscriptions

For auto-renewable subscriptions, verify:

- Product IDs match the app code.
- Group and products have localizations.
- Prices and territories are set.
- Subscription duration is correct.
- Introductory offer or trial is configured if advertised.
- Review screenshot is uploaded.
- Paywall clearly shows price, duration, trial details, renewal, cancellation, and links to Terms and Privacy.
- Metadata includes Terms/EULA.

If a product is not available in StoreKit sandbox, confirm App Store Connect state and allow for propagation delay.

## App Privacy Nutrition Label

The App Privacy answers must match the app and SDKs:

- Data used to track users.
- Data linked to the user.
- Data not linked to the user.
- Purpose for each data type.
- Whether data is collected by third-party SDKs.
- Whether IDFA is used.

If the API cannot set or verify all privacy answers, use App Store Connect web UI and record the final answers in the handoff.

## Encryption

If the app does not use non-exempt or proprietary encryption, set:

```text
ITSAppUsesNonExemptEncryption = false
```

Verify it in the archived app's `Info.plist`, not only in source:

```bash
plutil -p "$archive_path/Products/Applications/<App>.app/Info.plist" | rg ITSAppUsesNonExemptEncryption
```

If the app uses encryption beyond exempt HTTPS/system APIs, answer export compliance accurately in App Store Connect.

## Screenshots And Icons

Requirements change, so verify current App Store Connect requirements live.

General rules:

- App icon must be readable at small size and present in the asset catalog.
- Screenshots must match the actual app experience and device family.
- Required screenshot sets must be complete before review.
- Paywall and subscription screenshots should match current products and prices.
- Avoid screenshots that imply unsupported functionality.

For generated screenshots, keep the generator inputs, output paths, and upload evidence in the release handoff.

## Review Notes

Write review notes that reduce reviewer friction:

- Explain whether login is required.
- Explain demo/trial behavior and how to reach paid screens.
- Provide test credentials only if needed.
- Mention hardware, microphone, network, or real-time backend requirements if they affect testing.
- Avoid marketing copy; be operational.

## Legal URL Hosting

If hosting legal pages on the app backend:

- Deploy pages before submitting review.
- Verify `/privacy`, `/terms`, and `/support` return 2xx without authentication.
- Prefer HTTPS.
- Keep content app-specific and current.
- Record deploy commit and HTTP verification in the handoff.
