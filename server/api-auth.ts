import type { NextFunction, Request, RequestHandler, Response } from "express";
import { rateLimit } from "express-rate-limit";
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
 * This is authentication for every `/api` route plus one prefix-level authorization rule:
 * routes listed in API_OWNER_ONLY_ROUTES accept only the owner bearer token.
 * Other routes that need owner-only or per-customer checks must keep or add their own checks.
 * Fails closed: if neither secret is configured, every non-allowlisted `/api` request is rejected.
 */

export type PublicApiRoute = {
  methods: readonly string[];
  pattern: RegExp;
  reason: string;
};

export type OwnerOnlyApiRoute = {
  /** Methods that stay open to any authenticated caller (session or owner). Every other method is owner-only. */
  sessionReadableMethods: readonly string[];
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
  {
    methods: ["GET"],
    pattern: /^\/api\/stripe\/products$/,
    reason: "Public pricing page: active product names, descriptions, metadata and active prices only; no secret key or customer data.",
  },
  {
    methods: ["GET"],
    pattern: /^\/api\/stripe\/publishable-key$/,
    reason: "Stripe publishable (pk_) key that Stripe.js needs in the browser; the secret key is never returned.",
  },
];

/**
 * Owner-only prefixes. Matching is case-insensitive and covers every sub-path (Express routes
 * case-insensitively and ignores a trailing slash), so look-alike spellings stay owner-only.
 * A signed-in Google/Apple session alone gets 403; no credential gets 401.
 */
export const API_OWNER_ONLY_ROUTES: readonly OwnerOnlyApiRoute[] = [
  {
    sessionReadableMethods: READ,
    pattern: /^\/api\/github(?:\/|$)/i,
    reason:
      "Pushes commits (sync, push-all, push-source, auto-sync) and dispatches workflows (trigger-workflow) in the DreamCo GitHub repository with the server's GitHub token.",
  },
];

function fullPath(req: Request): string {
  return `${req.baseUrl || ""}${req.path || ""}`;
}

export function isPublicApiRequest(req: Request): boolean {
  const path = fullPath(req);
  const method = req.method.toUpperCase();
  return API_PUBLIC_ALLOWLIST.some((route) => route.methods.includes(method) && route.pattern.test(path));
}

export function isOwnerOnlyApiRequest(req: Request): boolean {
  const path = fullPath(req);
  const method = req.method.toUpperCase();
  return API_OWNER_ONLY_ROUTES.some((route) => !route.sessionReadableMethods.includes(method) && route.pattern.test(path));
}

export function apiRequestAuthenticated(req: Request): boolean {
  return Boolean(readAuthSession(req)) || billingOwnerAuthorized(req);
}

function rejectUnauthenticated(res: Response) {
  res.setHeader("WWW-Authenticate", 'Bearer realm="dreamco-api"');
  return res.status(401).json({ error: "Authentication required" });
}

/**
 * Throttles only requests the guard is about to reject (no valid credential, not allowlisted),
 * so credential guessing is limited without ever slowing down signed-in users or the owner.
 * Mount with `app.use("/api", apiAuthFailureRateLimit)` immediately before `requireApiAuth()`.
 */
export const apiAuthFailureRateLimit = rateLimit({
  windowMs: 15 * 60 * 1000,
  limit: 300,
  standardHeaders: "draft-8",
  legacyHeaders: false,
  skip: (req) => isPublicApiRequest(req) || apiRequestAuthenticated(req),
  message: { error: "Too many unauthenticated requests. Wait before trying again." },
});

/** Mount with `app.use("/api", requireApiAuth())` before any `/api` route handlers. */
export function requireApiAuth(): RequestHandler {
  return (req: Request, res: Response, next: NextFunction) => {
    if (isOwnerOnlyApiRequest(req)) {
      if (billingOwnerAuthorized(req)) return next();
      if (readAuthSession(req)) return res.status(403).json({ error: "Owner credential required" });
      return rejectUnauthenticated(res);
    }
    if (isPublicApiRequest(req) || apiRequestAuthenticated(req)) return next();
    return rejectUnauthenticated(res);
  };
}
