---
name: Express route vs Vite catch-all
description: Why POST /api routes can silently fall through to Vite's HTML catch-all and how to prevent it.
---

## The Rule
Never add new API routes via a separate file import inside `registerRoutes()` if that file uses a different OpenAI/client instance. The import silently fails (wrong env vars, different singleton), the route is never registered, and Vite's `app.use("/{*path}", ...)` in server/vite.ts catches everything — returning HTML with HTTP 200.

## Why
- `server/vite.ts` line 34: `app.use("/{*path}", ...)` matches ALL HTTP methods, not just GET.
- The express logger middleware (server/index.ts) logs ALL /api/* requests regardless of who responds — so `POST /api/generate-image 200 in 6ms` in logs does NOT confirm the Express route responded; Vite can respond with HTML + 200 too.
- A route that silently fails to register leaves no error in the log.

## How to Apply
- Always add new API routes as inline handlers directly inside `registerRoutes()` in `server/routes.ts`, using the `openai` client already declared at the top of that file.
- Never import a separate `registerXRoutes(app)` helper that creates its own client with different env var names (`AI_INTEGRATIONS_OPENAI_API_KEY` vs `OPENAI_API_KEY`).
- To verify a route is registered: test with empty/invalid input first (should return JSON error in <10ms, not HTML). If curl returns `<!DOCTYPE html>`, the route is not registered.
