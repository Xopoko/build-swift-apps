---
name: macos-view-architect
description: Refactor macOS SwiftUI root views while preserving window-scoped state, focused commands, toolbars, and AppKit boundaries.
---

# macOS View Architect

Use [SwiftUI view refactoring](../swiftui-view-architect/SKILL.md) for extraction and state ownership. Apply these macOS checks when splitting a root view:

- Keep sidebar selection and inspector state with the window that owns them so opening a second window does not change the first.
- Trace which window or focused view handles each menu command and toolbar action. Verify shortcuts and inactive-window behavior after moving their code.
- Keep Settings, utility windows, and menu bar extras at their scene boundaries. See [macOS SwiftUI scenes](../macos-swiftui-architect/SKILL.md) when changing how those scenes are presented.
- Keep AppKit objects with the code that needs them. See [AppKit bridges](../macos-appkit-bridge/SKILL.md) when the responsibility belongs to an AppKit API.
