---
name: CodeLabPage Bot Icon Bug
description: Fix for "Bot is not defined" crash in DreamCodeLabPage
---

## Rule
`DreamCodeLabPage.tsx` (the renamed `CodeLabPage.tsx`) had two bugs:
1. `Bot` icon from lucide-react used inside `VibeCodeEditor` (a module-level function) but only imported in the page component scope
2. `handleRunBot` callback passed to `VibeCodeEditor` without a prop

**Fix applied:**
- Replaced `<Bot>` with `<Sparkles>` inside VibeCodeEditor
- Added `onRunBot` prop to VibeCodeEditor, passed `handleRunBot` at call site
- `CodeLabPage.tsx` is a 1-line re-export stub

**Why:** Module-level functions can't access component-scope imports or closures. Always pass callbacks and icons as props to nested component functions defined at module level.
