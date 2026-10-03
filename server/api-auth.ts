import type { NextFunction, Request, RequestHandler, Response } from "express";
import { billingOwnerAuthorized } from "./billing-auth";
import { readAuthSession } from "./oauth-login";

/**
 * Global inbound authentication for `/api`.
 *
 * Reuses the two credentials the server already issues and verifies:
 * - the HMAC-sealed `buddy_auth_session` cookie set by the Google/Apple OAuth callback
 *   (`server/oauth-login.ts`, signed with AUTH_SESSION_SECRET), and
 * - the owner bearer token (`server/billing-auth.ts`, OWNER_BILLING_TOKEN).
 *
 * This is authentication only (who is calling), not per-route authorization (what they may do).
 * Routes that need owner-only or per-customer checks must keep or add their own checks.
 * Fails closed: if neither secret is configured, every non-allowlisted `/api` request is rejected.
 */

export type PublicApiRoute = {
  methods: readonly string[];
  pattern: RegExp;
  reason: string;
};

const READ = ["GET", "HEAD"] as const;

/** Small, explicit public allowlist. Matching is exact and case-sensitive so look-alike paths fail closed. */
export const API_PUBLIC_ALLOWLIST: readonly PublicApiRoute[] = [
  { methods: READ, pattern: /^\/api\/health$/, reason: "Liveness probe for the host/load balancer; returns no secrets." },
  { methods: READ, pattern: /^\/api\/ready$/, reason: "Readiness probe; reports configured/not-configured booleans only." },
  {
    methods: ["POST"],
    pattern: /^\/api\/stripe\/webhook$/,
    reason: "Called server-to-server by Stripe; authenticated by stripe-signature verification over the raw body (registered before express.json).",
  },
  { methods: READ, pattern: /^\/api\/auth\/providers$/, reason: "Sign-in page must list configured providers before a session exists." },
  { methods: READ, pattern: /^\/api\/auth\/[a-z]+\/start$/, reason: "Starts OAuth sign-in (rate limited, state+nonce cookie)." },
  { methods: READ, pattern: /^\/api\/auth\/[a-z]+\/callback$/, reason: "OAuth provider redirect target that creates the session (rate limited, verified state)." },
  { methods: READ, pattern: /^\/api\/auth\/session$/, reason: "Lets the UI learn whether the caller is signed in; returns {authenticated:false} without a session." },
  { methods: ["POST"], pattern: /^\/api\/auth\/sign-out$/, reason: "Only clears the caller's own session cookie." },
];

function fullPath(req: Request): string {
  return `${req.baseUrl || ""}${req.path || ""}`;
}

export function isPublicApiRequest(req: Request): boolean {
  const path = fullPath(req);
  const method = req.method.toUpperCase();
  return API_PUBLIC_ALLOWLIST.some((route) => route.methods.includes(method) && route.pattern.test(path));
}

export function apiRequestAuthenticated(req: Request): boolean {
  return Boolean(readAuthSession(req)) || billingOwnerAuthorized(req);
}

/** Mount with `app.use("/api", requireApiAuth())` before any `/api` route handlers. */
export function requireApiAuth(): RequestHandler {
  return (req: Request, res: Response, next: NextFunction) => {
    if (isPublicApiRequest(req) || apiRequestAuthenticated(req)) return next();
    res.setHeader("WWW-Authenticate", 'Bearer realm="dreamco-api"');
    return res.status(401).json({ error: "Authentication required" });
  };
}
