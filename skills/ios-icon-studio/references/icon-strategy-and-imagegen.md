# Icon Strategy And ImageGen

## Product Understanding

Before generating, reduce the app to a clear icon brief:

- App name and category.
- Target user and the moment they notice the icon.
- Core job: what the app helps the user do.
- Emotional promise: fast, calm, powerful, safe, playful, premium, social, creative, etc.
- Main differentiator: why this app is not just another app in the category.
- Existing visual language: brand colors, screenshots, typography, logo, product metaphors.
- Competitive shelf: what common icons in the category look like and what to avoid copying.

Do not let the icon become a feature list. A good app icon usually represents one of these:

- the app's core object;
- the transformation/outcome the user wants;
- the user's role or relationship to the app;
- a symbolic metaphor that is easier to remember than the literal product;
- a distinctive brand mark that can survive without text.

## Marketing Qualities

Optimize for these qualities in this order:

1. Instant recognition: one dominant silhouette, readable at home-screen size.
2. Memorability: a shape/color relationship that is easy to recall.
3. Category fit: enough cues that the app does not feel random.
4. Differentiation: a twist that prevents it from blending into the category.
5. Desire: visual polish that makes the app feel useful and worth opening.
6. Trust: no cheap stock look, no confusing symbolism, no accidental negative associations.

Prefer a slightly unusual but clear icon over a beautiful generic one.

## Choosing What Should Be On The Icon

Use this decision path:

1. If the app has a concrete object users already associate with it, start there.
2. If the product is a workflow/tool, show the outcome rather than the interface.
3. If the product is communication/social/translation, show relationship, exchange, voice, or understanding, not a generic chat bubble alone.
4. If the product is productivity/finance/security, use a simple symbolic object plus a distinctive color/material treatment.
5. If the product is emotional or habit-based, use a character, mascot, or tactile object only if it stays recognizable at small size.
6. If all literal options are generic, design an abstract mark from the product's core motion or transformation.

Reject concepts that need explanation. The icon can be metaphorical, but it should not be a puzzle.

## ImageGen Prompt Patterns

Generate distinct directions first, then refine one direction. Avoid asking for "many options in one image"; separate prompts produce cleaner candidates.

### Literal Product Metaphor

```text
Use case: logo-brand
Asset type: iOS app icon, square 1024x1024 master artwork
Primary request: create a polished iOS app icon for <app name>, a <category> app that helps <target user> <core job>
Subject: one simplified <object/metaphor> representing <core value>
Style/medium: premium modern app icon, tactile bitmap illustration, simple bold silhouette, no text
Composition/framing: centered subject, large readable shape, generous safe margin for iOS rounded mask
Color palette: <brand colors or 2-4 high-contrast colors>
Constraints: no words, no UI screenshot, no watermark, no flags, no tiny details, no baked rounded corners, no transparent background
```

### Abstract Brand Mark

```text
Use case: logo-brand
Asset type: iOS app icon, square 1024x1024 master artwork
Primary request: create a distinctive abstract app icon mark for <app name>, expressing <core motion/transformation>
Subject: one bold geometric symbol based on <metaphor>
Style/medium: clean premium iOS icon, memorable silhouette, subtle depth, vector-friendly but rendered as polished bitmap
Composition/framing: centered, simple, readable at 60 px
Color palette: <palette>
Constraints: no letters, no words, no UI, no tiny lines, no generic gradient blob, no baked rounded corners
```

### Human Communication / Voice / Translation

```text
Use case: logo-brand
Asset type: iOS app icon, square 1024x1024 master artwork
Primary request: create a memorable app icon for a live voice translation app
Subject: two clearly human side-profile heads facing each other with a simple flowing voice wave between them
Style/medium: minimal premium iOS app icon, tactile paper or soft 3D shapes, strong silhouette, warm and trustworthy
Composition/framing: heads large, faces unmistakably head-like with forehead/nose/mouth/chin cues, wave centered, safe margin for iOS mask
Color palette: light neutral background, one dark cool head, one warm coral head, small purple/orange voice wave accent
Constraints: no kidney/bean-shaped heads, no text, no flags, no UI screenshot, no tiny waveform lines, no baked rounded corners, no transparent background
```

## Refinement Prompts

Use a single targeted change per iteration:

- "Keep the composition, but make the silhouette readable at 60 px by simplifying the inner details."
- "Keep the colors and subject, but make the human profiles less bean-shaped and more clearly head-like."
- "Keep the metaphor, but remove all text-like marks and thin lines."
- "Make the icon feel more premium and less stock-like, preserving the same main shape."
- "Increase contrast between subject and background while keeping the palette restrained."

## Candidate Review Checklist

Review every candidate as if it is already on the App Store and home screen:

- Can I describe it in five words?
- Would I recognize it in a grid of 30 apps?
- Is the main symbol still visible at `60x60`?
- Does it avoid accidental meanings, such as body organs, flags, political symbols, or medical cues?
- Does it communicate benefit or identity, not only functionality?
- Does it look like an app icon, not a poster, sticker, screenshot, or logo mockup?

## Official References

- Apple Human Interface Guidelines: App icons: https://developer.apple.com/design/human-interface-guidelines/app-icons
- Apple App Store Connect Help: Add an app icon: https://developer.apple.com/help/app-store-connect/manage-app-information/add-an-app-icon
