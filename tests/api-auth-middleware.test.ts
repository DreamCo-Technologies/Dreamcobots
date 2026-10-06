import assert from "node:assert/strict";
import { spawn, type ChildProcess } from "node:child_process";
import { createHmac } from "node:crypto";
import { readFileSync } from "node:fs";
import { createServer, type AddressInfo } from "node:net";
import { after, before, describe, test } from "node:test";
import express from "express";

import { API_OWNER_ONLY_ROUTES, API_PUBLIC_ALLOWLIST, apiAuthFailureRateLimit, requireApiAuth } from "../server/api-auth.ts";
import { registerOAuthLoginRoutes } from "../server/oauth-login.ts";

// The 27 P0 unauthenticated mutating routes from the Grok-Prod-API-Surface map (scan_routes.py on main).
const P0_ROUTES: ReadonlyArray<readonly [method: string, path: string, sample: string]> = [
  ["post", "/api/buddy/workforce/payment-plan", "/api/buddy/workforce/payment-plan"],
  ["post", "/api/github-intel/search", "/api/github-intel/search"],
  ["post", "/api/approval-notifications/plan", "/api/approval-notifications/plan"],
  ["post", "/api/buddy/deploy-config", "/api/buddy/deploy-config"],
  ["post", "/api/buddy/lead-plan", "/api/buddy/lead-plan"],
  ["post", "/api/debug/revenue-leaks", "/api/debug/revenue-leaks"],
  ["patch", "/api/debug/revenue-leaks/:id/resolve", "/api/debug/revenue-leaks/123/resolve"],
  ["post", "/api/stripe/checkout", "/api/stripe/checkout"],
  ["post", "/api/stripe/restore-subscription", "/api/stripe/restore-subscription"],
  ["post", "/api/stripe/portal", "/api/stripe/portal"],
  ["post", "/api/buddy/device-actions/plan", "/api/buddy/device-actions/plan"],
  ["post", "/api/buddy/models/demand-match", "/api/buddy/models/demand-match"],
  ["post", "/api/buddy/models/select", "/api/buddy/models/select"],
  ["post", "/api/buddy/model-benchmarks/plan", "/api/buddy/model-benchmarks/plan"],
  ["post", "/api/buddy/models/improvement-plan", "/api/buddy/models/improvement-plan"],
  ["post", "/api/buddy/open-model-lab/comparison-plan", "/api/buddy/open-model-lab/comparison-plan"],
  ["post", "/api/buddy/open-secure-ai-defense/github-profile-plan", "/api/buddy/open-secure-ai-defense/github-profile-plan"],
  ["post", "/api/buddy/open-secure-ai-defense/model-discovery-plan", "/api/buddy/open-secure-ai-defense/model-discovery-plan"],
  ["post", "/api/buddy/crypto/wallet-plan", "/api/buddy/crypto/wallet-plan"],
  ["post", "/api/buddy/crypto/mining-plan", "/api/buddy/crypto/mining-plan"],
  ["post", "/api/buddy/crypto/dreamcoin-plan", "/api/buddy/crypto/dreamcoin-plan"],
  ["post", "/api/token-transfer-plans", "/api/token-transfer-plans"],
  ["post", "/api/github/sync", "/api/github/sync"],
  ["post", "/api/github/push-all", "/api/github/push-all"],
  ["post", "/api/github/push-source", "/api/github/push-source"],
  ["post", "/api/github/auto-sync", "/api/github/auto-sync"],
  ["post", "/api/github/trigger-workflow", "/api/github/trigger-workflow"],
];

// Owner-approved (Oct 5, 2026): every mutating /api/github/* route accepts only the OWNER_BILLING_TOKEN bearer.
// These are all the mutating /api/github/* routes in server/routes.ts (checked by the first test below).
const OWNER_ONLY_GITHUB_ROUTES: ReadonlyArray<readonly [method: string, path: string]> = [
  ["post", "/api/github/sync"],
  ["post", "/api/github/push-all"],
  ["post", "/api/github/push-source"],
  ["post", "/api/github/auto-sync"],
  ["post", "/api/github/trigger-workflow"],
];
const isOwnerOnlySample = (path: string) => OWNER_ONLY_GITHUB_ROUTES.some(([, ownerPath]) => ownerPath === path);

// Read-only GitHub routes stay available to any authenticated caller (session or owner).
const GITHUB_READ_ROUTES = ["/api/github/status", "/api/github/auto-sync", "/api/github/workflows"] as const;

// Owner-approved (Oct 5, 2026) public pricing reads. GET only.
const PUBLIC_PRICING_ROUTES = ["/api/stripe/products", "/api/stripe/publishable-key"] as const;

const PUBLIC_SAMPLES: ReadonlyArray<readonly [method: string, path: string]> = [
  ["GET", "/api/health"],
  ["GET", "/api/ready"],
  ["POST", "/api/stripe/webhook"],
  ["GET", "/api/auth/providers"],
  ["GET", "/api/auth/google/start"],
  ["GET", "/api/auth/apple/callback"],
  ["GET", "/api/auth/session"],
  ["POST", "/api/auth/sign-out"],
  ["GET", "/api/stripe/products"],
  ["GET", "/api/stripe/publishable-key"],
];

const OWNER_TOKEN = "test-owner-token-for-api-auth";
const SESSION_SECRET = "test-session-secret-for-api-auth";

// Same sealing format as server/oauth-login.ts (base64url JSON + "." + HMAC-SHA256 base64url).
function sealSession(payload: object, secret = SESSION_SECRET): string {
  const value = Buffer.from(JSON.stringify(payload)).toString("base64url");
  const signature = createHmac("sha256", secret).update(value).digest("base64url");
  return `buddy_auth_session=${value}.${signature}`;
}
const validSessionCookie = () =>
  sealSession({ provider: "google", sub: "user-1", email: "owner@example.com", exp: Math.floor(Date.now() / 1000) + 3600 });

test("all 27 P0 routes are still registered in server/routes.ts with these methods", () => {
  const routes = readFileSync("server/routes.ts", "utf8");
  assert.equal(P0_ROUTES.length, 27);
  for (const [method, path] of P0_ROUTES) {
    assert.ok(routes.includes(`app.${method}("${path}"`), `${method.toUpperCase()} ${path} not found in server/routes.ts`);
  }
});

test("every mutating /api/github route in server/routes.ts is in the owner-only test list", () => {
  const routes = readFileSync("server/routes.ts", "utf8");
  const registered = [...routes.matchAll(/app\.(post|put|patch|delete|all)\("(\/api\/github\/[^"]*)"/g)].map((m) => `${m[1]} ${m[2]}`).sort();
  assert.deepEqual(registered, OWNER_ONLY_GITHUB_ROUTES.map(([method, path]) => `${method} ${path}`).sort());
});

test("server/index.ts mounts the rate limiter and /api guard after the webhook and before registerRoutes", () => {
  const index = readFileSync("server/index.ts", "utf8");
  const webhook = index.indexOf("app.post(\n  '/api/stripe/webhook'");
  const json = index.indexOf("express.json(");
  const limiter = index.indexOf('app.use("/api", apiAuthFailureRateLimit)');
  const guard = index.indexOf('app.use("/api", requireApiAuth())');
  const routes = index.indexOf("registerRoutes(httpServer, app)");
  assert.ok(webhook > 0 && json > 0 && limiter > 0 && guard > 0 && routes > 0);
  assert.ok(webhook < json, "Stripe webhook must stay before express.json() to keep the raw body");
  assert.ok(json < limiter && limiter < guard, "the auth-failure rate limiter must run right before the /api guard");
  assert.ok(json < guard && guard < routes, "the /api guard must run before every route registered by registerRoutes");
});

test("the public allowlist is exactly the approved set and every entry has a reason", () => {
  const entries = API_PUBLIC_ALLOWLIST.map((route) => `${[...route.methods].join(",")} ${route.pattern.source}`);
  assert.deepEqual(entries, [
    "GET,HEAD ^\\/api\\/health$",
    "GET,HEAD ^\\/api\\/ready$",
    "POST ^\\/api\\/stripe\\/webhook$",
    "GET,HEAD ^\\/api\\/auth\\/providers$",
    "GET,HEAD ^\\/api\\/auth\\/[a-z]+\\/start$",
    "GET,HEAD ^\\/api\\/auth\\/[a-z]+\\/callback$",
    "GET,HEAD ^\\/api\\/auth\\/session$",
    "POST ^\\/api\\/auth\\/sign-out$",
    "GET ^\\/api\\/stripe\\/products$",
    "GET ^\\/api\\/stripe\\/publishable-key$",
  ]);
  for (const route of API_PUBLIC_ALLOWLIST) assert.ok(route.reason.length > 10);
  for (const route of API_OWNER_ONLY_ROUTES) assert.ok(route.reason.length > 10);
});

test("the pricing routes are still GET handlers that return only public Stripe data", () => {
  const routes = readFileSync("server/routes.ts", "utf8");
  for (const path of PUBLIC_PRICING_ROUTES) assert.ok(routes.includes(`app.get("${path}"`), `GET ${path} not found`);
  const start = routes.indexOf('app.get("/api/stripe/publishable-key"');
  const end = routes.indexOf('app.post("/api/stripe/checkout"');
  assert.ok(start > 0 && end > start);
  const handlers = routes.slice(start, end);
  for (const forbidden of ["getStripeSecretKey", "STRIPE_SECRET_KEY", "customers.", "subscriptions.", "stripe.customers", "customer_email", "req.query", "req.body"]) {
    assert.ok(!handlers.includes(forbidden), `public pricing handlers must not reference ${forbidden}`);
  }
  const stripeClient = readFileSync("server/stripeClient.ts", "utf8");
  const publishable = stripeClient.slice(stripeClient.indexOf("export async function getStripePublishableKey"), stripeClient.indexOf("export async function getStripeSecretKey"));
  assert.match(publishable, /STRIPE_PUBLISHABLE_KEY/);
  assert.doesNotMatch(publishable, /SECRET/);
});

describe("requireApiAuth (in-process express app)", () => {
  let server: import("node:http").Server;
  let base = "";
  const previous = { owner: process.env.OWNER_BILLING_TOKEN, secret: process.env.AUTH_SESSION_SECRET };

  before(async () => {
    process.env.OWNER_BILLING_TOKEN = OWNER_TOKEN;
    process.env.AUTH_SESSION_SECRET = SESSION_SECRET;
    const app = express();
    app.use(express.json());
    apiAuthFailureRateLimit.resetKey("127.0.0.1");
    app.use("/api", apiAuthFailureRateLimit);
    app.use("/api", requireApiAuth());
    const reached = (_req: express.Request, res: express.Response) => res.status(200).json({ reached: true });
    for (const [method, path] of P0_ROUTES) (app as any)[method](path, reached);
    for (const path of GITHUB_READ_ROUTES) app.get(path, reached);
    for (const path of PUBLIC_PRICING_ROUTES) app.all(path, reached); // every method reaches a handler if the guard lets it through
    app.get("/api/health", reached);
    app.get("/api/ready", reached);
    app.post("/api/stripe/webhook", reached);
    registerOAuthLoginRoutes(app); // the real sign-in routes, behind the guard
    await new Promise<void>((resolve) => { server = app.listen(0, "127.0.0.1", () => resolve()); });
    base = `http://127.0.0.1:${(server.address() as AddressInfo).port}`;
  });

  after(async () => {
    await new Promise<void>((resolve) => server.close(() => resolve()));
    process.env.OWNER_BILLING_TOKEN = previous.owner;
    process.env.AUTH_SESSION_SECRET = previous.secret;
    if (previous.owner === undefined) delete process.env.OWNER_BILLING_TOKEN;
    if (previous.secret === undefined) delete process.env.AUTH_SESSION_SECRET;
  });

  const call = (method: string, path: string, headers: Record<string, string> = {}) =>
    fetch(`${base}${path}`, { method: method.toUpperCase(), headers: { "content-type": "application/json", ...headers }, body: method.toUpperCase() === "GET" ? undefined : "{}" });

  test("each P0 route returns 401 without credentials and never reaches the handler", async () => {
    for (const [method, , sample] of P0_ROUTES) {
      const response = await call(method, sample);
      assert.equal(response.status, 401, `${method.toUpperCase()} ${sample}`);
      assert.deepEqual(await response.json(), { error: "Authentication required" });
      assert.match(response.headers.get("www-authenticate") || "", /Bearer/);
    }
  });

  test("each P0 route returns 401 with a wrong token, a forged cookie, or an expired session", async () => {
    const forged = sealSession({ provider: "google", sub: "x", exp: Math.floor(Date.now() / 1000) + 3600 }, "wrong-secret");
    const expired = sealSession({ provider: "google", sub: "x", exp: Math.floor(Date.now() / 1000) - 1 });
    for (const [method, , sample] of P0_ROUTES) {
      assert.equal((await call(method, sample, { authorization: "Bearer wrong-token-for-api-auth" })).status, 401);
      assert.equal((await call(method, sample, { cookie: forged })).status, 401);
      assert.equal((await call(method, sample, { cookie: expired })).status, 401);
    }
  });

  test("each P0 route reaches its handler with the owner token; non-owner-only routes also with a signed-in session", async () => {
    for (const [method, , sample] of P0_ROUTES) {
      assert.equal((await call(method, sample, { authorization: `Bearer ${OWNER_TOKEN}` })).status, 200, sample);
      assert.equal((await call(method, sample, { cookie: validSessionCookie() })).status, isOwnerOnlySample(sample) ? 403 : 200, sample);
    }
  });

  test("owner-only GitHub routes: 401 without credentials, 403 with a session only, handler with the owner bearer", async () => {
    for (const [method, path] of OWNER_ONLY_GITHUB_ROUTES) {
      const anonymous = await call(method, path);
      assert.equal(anonymous.status, 401, `${method} ${path} anonymous`);
      assert.deepEqual(await anonymous.json(), { error: "Authentication required" });

      const sessionOnly = await call(method, path, { cookie: validSessionCookie() });
      assert.equal(sessionOnly.status, 403, `${method} ${path} session only`);
      assert.deepEqual(await sessionOnly.json(), { error: "Owner credential required" });

      const owner = await call(method, path, { authorization: `Bearer ${OWNER_TOKEN}` });
      assert.equal(owner.status, 200, `${method} ${path} owner bearer`);
      assert.deepEqual(await owner.json(), { reached: true });

      const ownerWithSession = await call(method, path, { authorization: `Bearer ${OWNER_TOKEN}`, cookie: validSessionCookie() });
      assert.equal(ownerWithSession.status, 200, `${method} ${path} owner bearer + session`);
    }
  });

  test("owner-only GitHub routes reject wrong tokens and look-alike spellings even with a valid session", async () => {
    for (const [method, path] of OWNER_ONLY_GITHUB_ROUTES) {
      assert.equal((await call(method, path, { authorization: "Bearer wrong-token-for-api-auth", cookie: validSessionCookie() })).status, 403, path);
      assert.equal((await call(method, path, { authorization: "Bearer wrong-token-for-api-auth" })).status, 401, path);
      assert.equal((await call(method, path, { cookie: sealSession({ provider: "google", sub: "x", exp: Math.floor(Date.now() / 1000) + 3600 }, "wrong-secret") })).status, 401, path);
      // Express matches routes case-insensitively and ignores a trailing slash, so these would reach the real handler.
      assert.equal((await call(method, path.toUpperCase(), { cookie: validSessionCookie() })).status, 403, path.toUpperCase());
      assert.equal((await call(method, path.replace("/api/github/", "/api/GitHub/"), { cookie: validSessionCookie() })).status, 403, path);
      assert.equal((await call(method, `${path}/`, { cookie: validSessionCookie() })).status, 403, `${path}/`);
      for (const other of ["put", "patch", "delete"]) {
        assert.equal((await call(other, path, { cookie: validSessionCookie() })).status, 403, `${other} ${path}`);
      }
    }
  });

  test("read-only GitHub routes stay available to a signed-in session but not anonymously", async () => {
    for (const path of GITHUB_READ_ROUTES) {
      assert.equal((await call("GET", path)).status, 401, path);
      assert.equal((await call("GET", path, { cookie: validSessionCookie() })).status, 200, path);
      assert.equal((await call("GET", path, { authorization: `Bearer ${OWNER_TOKEN}` })).status, 200, path);
    }
  });

  test("public pricing GETs pass the guard unauthenticated; other methods and look-alikes stay blocked", async () => {
    for (const path of PUBLIC_PRICING_ROUTES) {
      const response = await call("GET", path);
      assert.equal(response.status, 200, `GET ${path}`);
      assert.deepEqual(await response.json(), { reached: true });
      for (const method of ["POST", "PUT", "PATCH", "DELETE"]) {
        const blocked = await call(method, path);
        assert.equal(blocked.status, 401, `${method} ${path}`);
        assert.deepEqual(await blocked.json(), { error: "Authentication required" });
      }
      assert.equal((await fetch(`${base}${path}`, { method: "HEAD" })).status, 401, `HEAD ${path} is not allowlisted`);
      assert.equal((await call("GET", `${path}/`)).status, 401, `GET ${path}/`);
      assert.equal((await call("GET", path.toUpperCase())).status, 401, `GET ${path.toUpperCase()}`);
      assert.equal((await call("POST", path, { cookie: validSessionCookie() })).status, 200, `POST ${path} with a session reaches the route's own checks`);
    }
    assert.equal((await call("GET", "/api/stripe/subscription-status")).status, 401, "other Stripe reads stay private");
  });

  test("allowlisted routes respond without credentials (real OAuth handlers)", async () => {
    for (const [method, path] of PUBLIC_SAMPLES) {
      assert.notEqual((await call(method, path)).status, 401, `${method} ${path}`);
    }
    assert.equal((await call("GET", "/api/health")).status, 200);
    assert.equal((await call("GET", "/api/ready")).status, 200);
    assert.equal((await call("POST", "/api/stripe/webhook")).status, 200);
    const providers = await call("GET", "/api/auth/providers");
    assert.equal(providers.status, 200);
    assert.ok(Array.isArray((await providers.json()).providers));
    const session = await call("GET", "/api/auth/session");
    assert.equal(session.status, 200);
    assert.deepEqual(await session.json(), { authenticated: false });
    assert.equal((await fetch(`${base}/api/auth/google/start`, { redirect: "manual" })).status, 503); // not configured, not blocked
    assert.equal((await fetch(`${base}/api/auth/google/callback`, { redirect: "manual" })).status, 400); // no state cookie, not blocked
    assert.equal((await call("POST", "/api/auth/sign-out")).status, 204);
  });

  test("the guard accepts exactly the session cookie the real OAuth code verifies", async () => {
    const session = await call("GET", "/api/auth/session", { cookie: validSessionCookie() });
    const body = await session.json();
    assert.equal(body.authenticated, true);
    assert.equal(body.profile.subject, "user-1");
  });

  test("look-alike paths and non-allowlisted methods fail closed", async () => {
    assert.equal((await call("POST", "/API/github/trigger-workflow")).status, 401);
    assert.equal((await call("POST", "/api/github/trigger-workflow/")).status, 401);
    assert.equal((await call("POST", "/api/health")).status, 401);
    assert.equal((await call("GET", "/api/stripe/webhook")).status, 401);
    assert.equal((await call("GET", "/api/not-a-route")).status, 401);
  });

  test("fails closed when neither OWNER_BILLING_TOKEN nor AUTH_SESSION_SECRET is configured", async () => {
    delete process.env.OWNER_BILLING_TOKEN;
    delete process.env.AUTH_SESSION_SECRET;
    try {
      const sample = "/api/github/trigger-workflow";
      assert.equal((await call("post", sample)).status, 401);
      assert.equal((await call("post", sample, { authorization: "Bearer " })).status, 401);
      assert.equal((await call("post", sample, { cookie: validSessionCookie() })).status, 401);
      assert.equal((await call("GET", "/api/health")).status, 200);
    } finally {
      process.env.OWNER_BILLING_TOKEN = OWNER_TOKEN;
      process.env.AUTH_SESSION_SECRET = SESSION_SECRET;
    }
  });
});

describe("apiAuthFailureRateLimit (in-process express app)", () => {
  let server: import("node:http").Server;
  let base = "";
  const previous = { owner: process.env.OWNER_BILLING_TOKEN, secret: process.env.AUTH_SESSION_SECRET };

  before(async () => {
    process.env.OWNER_BILLING_TOKEN = OWNER_TOKEN;
    process.env.AUTH_SESSION_SECRET = SESSION_SECRET;
    apiAuthFailureRateLimit.resetKey("127.0.0.1");
    const app = express();
    app.use("/api", apiAuthFailureRateLimit);
    app.use("/api", requireApiAuth());
    const reached = (_req: express.Request, res: express.Response) => res.status(200).json({ reached: true });
    app.get("/api/health", reached);
    app.get("/api/private", reached);
    app.get("/api/stripe/products", reached);
    app.post("/api/github/trigger-workflow", reached);
    await new Promise<void>((resolve) => { server = app.listen(0, "127.0.0.1", () => resolve()); });
    base = `http://127.0.0.1:${(server.address() as AddressInfo).port}`;
  });

  after(async () => {
    apiAuthFailureRateLimit.resetKey("127.0.0.1");
    await new Promise<void>((resolve) => server.close(() => resolve()));
    process.env.OWNER_BILLING_TOKEN = previous.owner;
    process.env.AUTH_SESSION_SECRET = previous.secret;
    if (previous.owner === undefined) delete process.env.OWNER_BILLING_TOKEN;
    if (previous.secret === undefined) delete process.env.AUTH_SESSION_SECRET;
  });

  test("throttles only rejected requests: 300 anonymous 401s, then 429; owner, sessions and public routes are never throttled", async () => {
    for (let i = 0; i < 300; i += 1) {
      assert.equal((await fetch(`${base}/api/private`)).status, 401, `anonymous request ${i + 1}`);
      if (i % 100 === 0) {
        assert.equal((await fetch(`${base}/api/private`, { headers: { cookie: validSessionCookie() } })).status, 200);
        assert.equal((await fetch(`${base}/api/health`)).status, 200);
      }
    }
    const limited = await fetch(`${base}/api/private`);
    assert.equal(limited.status, 429);
    assert.match((await limited.json()).error, /Too many unauthenticated requests/);
    assert.equal((await fetch(`${base}/api/github/trigger-workflow`, { method: "POST" })).status, 429);
    assert.equal((await fetch(`${base}/api/private`, { headers: { cookie: validSessionCookie() } })).status, 200);
    assert.equal((await fetch(`${base}/api/private`, { headers: { authorization: `Bearer ${OWNER_TOKEN}` } })).status, 200);
    assert.equal((await fetch(`${base}/api/github/trigger-workflow`, { method: "POST", headers: { authorization: `Bearer ${OWNER_TOKEN}` } })).status, 200);
    assert.equal((await fetch(`${base}/api/github/trigger-workflow`, { method: "POST", headers: { cookie: validSessionCookie() } })).status, 403);
    assert.equal((await fetch(`${base}/api/health`)).status, 200);
    assert.equal((await fetch(`${base}/api/stripe/products`)).status, 200);
  });
});

// Boots the real server/index.ts (local-test mode, placeholder DB, no provider secrets, GitHub/Stripe
// credentials scrubbed from the child env) and checks the real middleware order end to end.
// If server/routes.ts fails to load, index.ts falls back to health-only mode; the guard must still
// reject every P0 path, and checks that need the full route runtime are skipped with the startup reason.
describe("real server/index.ts runtime", () => {
  let child: ChildProcess;
  let base = "";
  let output = "";
  let fullRuntime = false;

  const freePort = () =>
    new Promise<number>((resolve, reject) => {
      const probe = createServer();
      probe.once("error", reject);
      probe.listen(0, "127.0.0.1", () => {
        const { port } = probe.address() as AddressInfo;
        probe.close(() => resolve(port));
      });
    });

  before(async () => {
    const port = await freePort();
    base = `http://127.0.0.1:${port}`;
    child = spawn(process.execPath, ["--import", "tsx", "server/index.ts"], {
      cwd: process.cwd(),
      stdio: ["ignore", "pipe", "pipe"],
      env: {
        PATH: process.env.PATH || "",
        HOME: process.env.HOME || "",
        NODE_ENV: "development",
        HOST: "127.0.0.1",
        PORT: String(port),
        DATABASE_URL: "postgres://dreamco_test:unused@127.0.0.1:1/dreamco_test",
        DREAMCO_DATABASE_PLACEHOLDER: "1",
        DREAMCO_ENABLE_LOCAL_TEST_ACCOUNT: "1",
        DREAMCO_DISABLE_AUTO_SYNC: "1",
        OPENAI_API_KEY: "sk-local-test-placeholder",
        AI_INTEGRATIONS_OPENAI_API_KEY: "sk-local-test-placeholder",
        OWNER_BILLING_TOKEN: OWNER_TOKEN,
        AUTH_SESSION_SECRET: SESSION_SECRET,
      },
    });
    child.stdout?.on("data", (chunk) => { output += chunk; });
    child.stderr?.on("data", (chunk) => { output += chunk; });
    const deadline = Date.now() + 90_000;
    let up = false;
    while (Date.now() < deadline && !up) {
      if (child.exitCode !== null) throw new Error(`server exited early (${child.exitCode}):\n${output}`);
      try { up = (await fetch(`${base}/api/health`)).status === 200; } catch { /* not listening yet */ }
      if (!up) await new Promise((resolve) => setTimeout(resolve, 250));
    }
    assert.ok(up, `server did not become healthy:\n${output}`);
    fullRuntime = /DreamCo full route runtime initialized/.test(output);
    if (!fullRuntime) console.log(`# NOTE full route runtime unavailable on this checkout:\n# ${output.split("\n").filter((l) => /full route runtime unavailable/.test(l)).join("\n# ")}`);
  });

  after(() => { child?.kill("SIGTERM"); });

  const call = (method: string, path: string, headers: Record<string, string> = {}) =>
    fetch(`${base}${path}`, { method: method.toUpperCase(), redirect: "manual", headers: { "content-type": "application/json", ...headers }, body: method.toUpperCase() === "GET" ? undefined : "{}" });
  const needsFullRuntime = (t: { skip: (message?: string) => void }) => {
    if (fullRuntime) return false;
    t.skip(`full route runtime did not load: ${output.split("\n").find((l) => /full route runtime unavailable/.test(l)) ?? "unknown"}`);
    return true;
  };

  test("each P0 route returns 401 from the global guard without credentials", async () => {
    for (const [method, , sample] of P0_ROUTES) {
      const response = await call(method, sample);
      assert.equal(response.status, 401, `${method.toUpperCase()} ${sample}`);
      const body = await response.json();
      assert.equal(body.error, "Authentication required", `${sample} was not rejected by the global guard`);
      assert.ok(body.requestId, "401 responses keep the observability request id");
    }
  });

  test("owner-only GitHub routes on the real server: 401 anonymous, 403 session only, owner bearer passes the guard", async () => {
    for (const [method, path] of OWNER_ONLY_GITHUB_ROUTES) {
      const anonymous = await call(method, path);
      assert.equal(anonymous.status, 401, `${method} ${path}`);
      assert.equal((await anonymous.json()).error, "Authentication required");
      const sessionOnly = await call(method, path, { cookie: validSessionCookie() });
      assert.equal(sessionOnly.status, 403, `${method} ${path} session only`);
      assert.equal((await sessionOnly.json()).error, "Owner credential required");
      const owner = await call(method, path, { authorization: `Bearer ${OWNER_TOKEN}` });
      assert.ok(![401, 403].includes(owner.status), `${method} ${path} owner bearer was stopped by the guard (${owner.status})`);
    }
  });

  test("public pricing GETs pass the real guard unauthenticated; POSTs to them stay blocked", async () => {
    for (const path of PUBLIC_PRICING_ROUTES) {
      assert.notEqual((await call("GET", path)).status, 401, `GET ${path}`);
      const blocked = await call("POST", path);
      assert.equal(blocked.status, 401, `POST ${path}`);
      assert.equal((await blocked.json()).error, "Authentication required");
    }
  });

  test("health and readiness stay public", async () => {
    assert.equal((await call("GET", "/api/health")).status, 200);
    assert.notEqual((await call("GET", "/api/ready")).status, 401);
  });

  test("Stripe webhook keeps its raw-body handler and signature requirement (not gated by auth)", async () => {
    const unsigned = await fetch(`${base}/api/stripe/webhook`, { method: "POST", headers: { "content-type": "application/json" }, body: "{}" });
    assert.equal(unsigned.status, 400);
    assert.equal((await unsigned.json()).error, "Missing stripe-signature");
    const badSignature = await fetch(`${base}/api/stripe/webhook`, { method: "POST", headers: { "content-type": "application/json", "stripe-signature": "t=1,v1=bad" }, body: "{}" });
    assert.equal(badSignature.status, 400);
    assert.equal((await badSignature.json()).error, "Webhook processing error");
  });

  test("owner token passes the guard; anonymous calls to other /api paths do not", async () => {
    assert.equal((await call("GET", "/api/local-test/status")).status, 401);
    assert.notEqual((await call("GET", "/api/local-test/status", { authorization: `Bearer ${OWNER_TOKEN}` })).status, 401);
  });

  test("[full runtime] real sign-in routes respond and a signed-in session passes the guard", async (t) => {
    if (needsFullRuntime(t)) return;
    assert.equal((await call("GET", "/api/auth/providers")).status, 200);
    assert.deepEqual(await (await call("GET", "/api/auth/session")).json(), { authenticated: false });
    assert.equal((await call("GET", "/api/auth/session", { cookie: validSessionCookie() }).then((r) => r.json())).authenticated, true);
    assert.equal((await call("GET", "/api/local-test/status", { cookie: validSessionCookie() })).status, 200);
  });

  test("[full runtime] route-level owner check still applies behind the guard (restore-subscription)", async (t) => {
    if (needsFullRuntime(t)) return;
    const response = await call("POST", "/api/stripe/restore-subscription", { cookie: validSessionCookie() });
    assert.equal(response.status, 401);
    assert.equal((await response.json()).error, "Owner billing token required");
  });
});
