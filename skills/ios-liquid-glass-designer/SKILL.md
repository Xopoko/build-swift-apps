---
name: ios-liquid-glass-designer
description: Implement, refactor, or review iOS 26+ SwiftUI Liquid Glass features using native `glassEffect`, `GlassEffectContainer`, glass button styles, availability gates, and fallbacks.
---

# iOS Liquid Glass Designer

Use native iOS 26+ Liquid Glass APIs first. Keep glass grouped, interactive only when appropriate, performance aware, and backed by non-glass fallback UI.

## Paths

- Review: inspect where glass belongs, modifier order, shape consistency, `GlassEffectContainer`, availability, and fallback.
- Improve: target surfaces/chips/buttons/cards, group multiple glass elements, and make only tappable/focusable elements interactive.
- New feature: design shapes/prominence/grouping first, apply glass after layout/appearance modifiers, and add morphing only for animated hierarchy changes.

## Rules

- Prefer native APIs over custom blurs.
- Use `GlassEffectContainer` for multiple glass views.
- Apply `.glassEffect(...)` after layout and visual modifiers.
- Use `.interactive()` only for interactive elements.
- Keep related shapes, tinting, spacing, and prominence consistent.
- Gate with `#available(iOS 26, *)` and provide a fallback.
- Use `.buttonStyle(.glass)` or `.buttonStyle(.glassProminent)` for actions.
- Use `glassEffectID` with `@Namespace` only for morphing transitions.

## Snippets

```swift
if #available(iOS 26, *) {
    Text("Hello")
        .padding()
        .glassEffect(.regular.interactive(), in: .rect(cornerRadius: 16))
} else {
    Text("Hello")
        .padding()
        .background(.ultraThinMaterial, in: RoundedRectangle(cornerRadius: 16))
}
```

```swift
GlassEffectContainer(spacing: 24) {
    HStack(spacing: 24) {
        Image(systemName: "scribble.variable")
            .frame(width: 72, height: 72)
            .glassEffect()
        Image(systemName: "eraser.fill")
            .frame(width: 72, height: 72)
            .glassEffect()
    }
}
```

```swift
Button("Confirm") { }
    .buttonStyle(.glassProminent)
```

## Resources

Read `references/liquid-glass.md` for details. Use current Apple docs when API details may have changed.
