import assert from "node:assert/strict";
import { spawn, type ChildProcess } from "node:child_process";
import { createHmac } from "node:crypto";
import { readFileSync } from "node:fs";
import { createServer, type AddressInfo } from "node:net";
import { after, before, describe, test } from "node:test";
import express from "express";

import { API_PUBLIC_ALLOWLIST, requireApiAuth } from "../server/api-auth.ts";
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

const PUBLIC_SAMPLES: ReadonlyArray<readonly [method: string, path: string]> = [
  ["GET", "/api/health"],
  ["GET", "/api/ready"],
  ["POST", "/api/stripe/webhook"],
  ["GET", "/api/auth/providers"],
  ["GET", "/api/auth/google/start"],
  ["GET", "/api/auth/apple/callback"],
  ["GET", "/api/auth/session"],
  ["POST", "/api/auth/sign-out"],
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

test("server/index.ts mounts the /api guard after the webhook and before registerRoutes", () => {
  const index = readFileSync("server/index.ts", "utf8");
  const webhook = index.indexOf("app.post(\n  '/api/stripe/webhook'");
  const json = index.indexOf("express.json(");
  const guard = index.indexOf('app.use("/api", requireApiAuth())');
  const routes = index.indexOf("registerRoutes(httpServer, app)");
  assert.ok(webhook > 0 && json > 0 && guard > 0 && routes > 0);
  assert.ok(webhook < json, "Stripe webhook must stay before express.json() to keep the raw body");
  assert.ok(json < guard && guard < routes, "the /api guard must run before every route registered by registerRoutes");
});

test("the public allowlist stays small and every entry has a reason", () => {
  assert.ok(API_PUBLIC_ALLOWLIST.length <= 8);
  for (const route of API_PUBLIC_ALLOWLIST) assert.ok(route.reason.length > 10);
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
    app.use("/api", requireApiAuth());
    const reached = (_req: express.Request, res: express.Response) => res.status(200).json({ reached: true });
    for (const [method, path] of P0_ROUTES) (app as any)[method](path, reached);
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

  test("each P0 route reaches its handler with the owner token or a valid signed-in session", async () => {
    for (const [method, , sample] of P0_ROUTES) {
      assert.equal((await call(method, sample, { authorization: `Bearer ${OWNER_TOKEN}` })).status, 200, sample);
      assert.equal((await call(method, sample, { cookie: validSessionCookie() })).status, 200, sample);
    }
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
