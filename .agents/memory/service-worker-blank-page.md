---
name: Service Worker blank page trap
description: How a stale service worker causes a permanent blank white page in Vite dev mode, and how to fix it.
---

## The Rule
In dev mode (`import.meta.env.DEV`), always **unregister** any existing service workers on load instead of registering them. A stale service worker will intercept ALL requests and serve a broken cached copy of the app, making every code change appear to have no effect.

**Why:** The service worker (sw.js) caches the root HTML and JS bundles. When the app breaks at a module level (e.g. a bad import), the service worker caches that broken state. Bumping the CACHE_NAME version in sw.js alone is NOT enough — the old SW intercepts the sw.js fetch too, so the new version never loads. The only reliable fix is to unregister in dev mode.

**How to apply:**
```ts
// client/src/main.tsx
if ("serviceWorker" in navigator) {
  if (import.meta.env.DEV) {
    navigator.serviceWorker.getRegistrations().then(rs => rs.forEach(r => r.unregister()));
  } else {
    window.addEventListener("load", () => navigator.serviceWorker.register("/sw.js").catch(() => {}));
  }
}
```

**Symptoms of this bug:**
- Completely blank white page with no visible content
- Browser logs show only Vite HMR WebSocket errors
- Even trivially different code in main.tsx shows no effect
- `document.getElementById("root").innerHTML` would be empty if you could check it
- Server logs show very few GET requests (no API calls) confirming React never mounted
