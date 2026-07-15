---
name: Browser Module Cache Fix Pattern
description: How to clear stale Vite module cache that causes crashes on renamed pages
---

## Rule
When a Vite-served page crashes due to a stale JS module (e.g. "X is not defined"), the fix is:
1. Fix the bug in the component
2. Bump the service worker cache version in `client/public/sw.js` (e.g. `dreamco-empire-v5` → `v6`)

**Why:** The service worker caches all non-/api/ responses. Bumping the cache name forces a fresh fetch of ALL assets on next real-browser visit.

**How to apply:** Any time you rename a file or fix a bug in a page component, bump the SW cache version. The screenshot tool reuses a persistent browser session and may still show the old cached module — this is a tool limitation, not an app bug. Real users get fresh code.

## Current SW version
`dreamco-empire-v5` in `client/public/sw.js`
