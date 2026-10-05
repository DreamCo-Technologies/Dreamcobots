import assert from "node:assert/strict";
import { createHmac } from "node:crypto";
import { readFileSync } from "node:fs";
import { createServer, type Server } from "node:http";
import type { AddressInfo } from "node:net";
import test, { after, before } from "node:test";

// Local-test boot of the real registerRoutes: no database, no provider key, no network.
const SESSION_SECRET = "route-gate-test-secret-not-a-real-credential";
process.env.AUTH_SESSION_SECRET = SESSION_SECRET;
process.env.DATABASE_URL ||= "postgres://placeholder:placeholder@127.0.0.1:1/placeholder";
process.env.DREAMCO_DATABASE_PLACEHOLDER = "1";
process.env.DREAMCO_ENABLE_LOCAL_TEST_ACCOUNT = "1";
process.env.DREAMCO_DISABLE_AUTO_SYNC = "1";
process.env.OPENAI_API_KEY ||= "sk-local-test-placeholder";
process.env.AI_INTEGRATIONS_OPENAI_API_KEY ||= "sk-local-test-placeholder";
process.env.BUDDY_MODEL_OWNER_SUBJECTS = "google:owner-subject";

const { default: express } = await import("express");
const { BUDDY_MODEL_ROUTES, buddyModelAccessFrom, buddyModelOwnerSubjects, buddyModelRouteGate } = await import("../server/buddy-model-route-gate");
const {
  BuddyModelAccessError,
  buddyModelSelectionRequestSchema,
  getBuddyModelAllowlist,
  selectBuddyModelsForTask,
} = await import("../server/buddy-model-policy");
const { demandModelMatchRequestSchema, matchDemandReasonToModels } = await import("../server/demand-model-policy");

// Full boot of server/routes.ts is attempted; on main it currently throws at import time
// ("Bot seeds contain duplicate canonical/supplemental identities"), which is unrelated to this patch.
let registerRoutes: undefined | ((server: Server, app: ReturnType<typeof express>) => Promise<Server>);
let fullBootError = "";
try {
  const { storage } = await import("../server/storage");
  // Kill-switch reads hit Postgres; stub only that read so handlers run without a database.
  (storage as unknown as { getSetting: () => Promise<undefined> }).getSetting = async () => undefined;
  ({ registerRoutes } = await import("../server/routes"));
} catch (error) {
  fullBootError = error instanceof Error ? error.message : String(error);
}

function sessionCookie(sub: string, provider = "google") {
  const value = Buffer.from(JSON.stringify({
    provider,
    sub,
    email: `${sub}@example.test`,
    exp: Math.floor(Date.now() / 1000) + 600,
  })).toString("base64url");
  const signature = createHmac("sha256", SESSION_SECRET).update(value).digest("base64url");
  return `buddy_auth_session=${value}.${signature}`;
}

const USER = sessionCookie("normal-user");
const OWNER = sessionCookie("owner-subject");
const FORGED = `buddy_auth_session=${Buffer.from(JSON.stringify({ provider: "google", sub: "owner-subject", exp: 9999999999 })).toString("base64url")}.forged`;

const SAMPLE_BODIES: Record<string, unknown> = {
  "/api/buddy/models/select": { objective: "Debug my repository and run tests", requiredCapabilities: ["coding"] },
  "/api/buddy/models/demand-match": { reasonId: "ai_usage-014", preferredTier: "any" },
};

/**
 * Gate harness: each BUDDY_MODEL_ROUTES path is mounted with the same buddyModelRouteGate(kind) used in
 * server/routes.ts. Selection handlers call the real policy functions exactly as routes.ts does; the other
 * handlers are stubs because the gate (not the handler) is what is under test for identity and policy.
 */
function gateHarness() {
  const app = express();
  app.use(express.json());
  for (const route of BUDDY_MODEL_ROUTES) {
    const method = route.method === "GET" ? "get" : "post";
    app[method](route.path, buddyModelRouteGate(route.kind), (req, res) => {
      try {
        if (route.path === "/api/buddy/models/select") {
          const parsed = buddyModelSelectionRequestSchema.parse(req.body);
          return res.status(201).json(selectBuddyModelsForTask(parsed, process.env, buddyModelAccessFrom(res)));
        }
        if (route.path === "/api/buddy/models/demand-match") {
          const parsed = demandModelMatchRequestSchema.parse(req.body);
          return res.status(201).json(matchDemandReasonToModels(parsed, process.env, buddyModelAccessFrom(res)));
        }
        return res.status(200).json({ handlerReached: true, providerCallExecuted: false });
      } catch (error) {
        if (error instanceof BuddyModelAccessError) return res.status(403).json({ error: error.message, code: error.code });
        return res.status(400).json({ error: error instanceof Error ? error.message : "invalid" });
      }
    });
  }
  return app;
}

let server: Server;
let fullServer: Server | undefined;
let base = "";
let fullBase = "";

async function listen(target: Server) {
  await new Promise<void>((resolve) => target.listen(0, "127.0.0.1", resolve));
  return `http://127.0.0.1:${(target.address() as AddressInfo).port}`;
}

before(async () => {
  server = createServer(gateHarness());
  base = await listen(server);
  if (registerRoutes) {
    const app = express();
    app.use(express.json());
    fullServer = createServer(app);
    await registerRoutes(fullServer, app);
    fullBase = await listen(fullServer);
  }
});

after(async () => {
  await new Promise<void>((resolve) => server.close(() => resolve()));
  if (fullServer) await new Promise<void>((resolve) => fullServer!.close(() => resolve()));
});

async function call(method: string, path: string, cookie?: string, body?: unknown, root = base) {
  const url = method === "GET" && path.endsWith("/council") ? `${root}${path}?taskCategory=Coding` : `${root}${path}`;
  const response = await fetch(url, {
    method,
    headers: { "Content-Type": "application/json", ...(cookie ? { Cookie: cookie } : {}) },
    body: method === "GET" ? undefined : JSON.stringify(body ?? SAMPLE_BODIES[path] ?? {}),
  });
  const text = await response.text();
  let json: any;
  try { json = JSON.parse(text); } catch { json = undefined; }
  return { status: response.status, json, headers: response.headers };
}

test("routes.ts gates every model route listed in BUDDY_MODEL_ROUTES and no model route is left out", () => {
  const routes = readFileSync("server/routes.ts", "utf8");
  for (const route of BUDDY_MODEL_ROUTES) {
    const pattern = new RegExp(`app\\.${route.method.toLowerCase()}\\("${route.path.replace(/[/.-]/g, "\\$&")}", buddyModelRouteGate\\("${route.kind}"\\)`);
    assert.match(routes, pattern, `${route.method} ${route.path} is not gated as ${route.kind}`);
  }
  const listed = new Set(BUDDY_MODEL_ROUTES.map((route) => `${route.method} ${route.path}`));
  const modelRoute = /app\.(get|post|put|patch|delete)\("(\/api\/[^"]*(?:model|route-capability)[^"]*)"/g;
  for (const match of routes.matchAll(modelRoute)) {
    assert.ok(listed.has(`${match[1].toUpperCase()} ${match[2]}`), `ungated model route: ${match[1].toUpperCase()} ${match[2]}`);
  }
});

test("every model route rejects an unauthenticated or forged caller before any handler runs", async () => {
  for (const route of BUDDY_MODEL_ROUTES) {
    for (const cookie of [undefined, FORGED]) {
      const result = await call(route.method, route.path, cookie);
      assert.equal(result.status, 401, `${route.method} ${route.path} returned ${result.status} with ${cookie ? "forged" : "no"} session`);
      assert.equal(result.json?.code, "caller_identity_required");
      assert.equal(result.json?.providerCallExecuted, false);
    }
  }
});

test("a signed-in caller passes the gate and the model policy runs on every route", async () => {
  for (const route of BUDDY_MODEL_ROUTES) {
    const result = await call(route.method, route.path, route.kind === "discovery_plan" ? OWNER : USER);
    assert.notEqual(result.status, 401, `${route.method} ${route.path}`);
    assert.equal(result.headers.get("x-buddy-model-policy"), "dreamco.buddy_model_route_gate.v1", `${route.method} ${route.path}`);
    assert.ok(result.headers.get("x-buddy-model-plan-status"), `${route.method} ${route.path}`);
  }
});

test("normal callers never receive a non-allowlisted model from selection routes", async () => {
  const allowlisted = new Set(getBuddyModelAllowlist().entries.map((entry) => entry.targetId));
  for (const preferredTier of ["free", "premium", "any"]) {
    const selection = await call("POST", "/api/buddy/models/select", USER, {
      objective: "Generate a video, translate a document, write code, and search the web",
      requiredCapabilities: ["coding", "video", "translation"],
      preferredTier,
      maxCandidates: 20,
    });
    assert.equal(selection.status, 201);
    assert.equal(selection.json.access.allowlistOnly, true);
    assert.equal(selection.json.providerCallExecuted, false);
    assert.ok(selection.json.candidates.every((candidate: any) => allowlisted.has(candidate.targetId) && candidate.allowlisted));
    assert.ok(selection.json.candidates.every((candidate: any) => !candidate.discoveryTarget));
  }
  const demand = await call("POST", "/api/buddy/models/demand-match", USER);
  assert.equal(demand.status, 201);
  assert.ok(demand.json.modelOptions.length > 0);
  assert.ok(demand.json.modelOptions.every((option: any) => allowlisted.has(option.targetId)));
  assert.equal(demand.json.access.discoveryEnabled, false);
});

test("discovery is owner-only and is never executed", async () => {
  const body = { objective: "Find the best coding model", requiredCapabilities: ["coding"], allowDiscovery: true, maxCandidates: 20 };
  const denied = await call("POST", "/api/buddy/models/select", USER, body);
  assert.equal(denied.status, 403);
  assert.equal(denied.json.code, "discovery_owner_only");
  const deniedPlan = await call("POST", "/api/buddy/open-secure-ai-defense/model-discovery-plan", USER);
  assert.equal(deniedPlan.status, 403);
  assert.equal(deniedPlan.json.code, "discovery_owner_only");

  const owner = await call("POST", "/api/buddy/models/select", OWNER, body);
  assert.equal(owner.status, 201);
  assert.equal(owner.json.access.callerRole, "owner");
  assert.equal(owner.json.access.discoveryEnabled, true);
  assert.equal(owner.json.access.discoveryExecuted, false);
  assert.equal(owner.json.providerCallExecuted, false);
  const nonAllowlisted = owner.json.candidates.filter((candidate: any) => !candidate.allowlisted);
  assert.ok(nonAllowlisted.length > 0);
  assert.ok(nonAllowlisted.every((candidate: any) => ["official_catalog_discovery_required", "allowlist_evidence_required"].includes(candidate.readiness)));

  const ownerDemand = await call("POST", "/api/buddy/models/demand-match", OWNER);
  assert.equal(ownerDemand.status, 201);
  assert.equal(ownerDemand.json.optionCount, 20);
  assert.equal(ownerDemand.json.providerCallExecuted, false);
});

test("premium selection still requires per-request approval through the gated route", async () => {
  const unapproved = await call("POST", "/api/buddy/models/select", USER, {
    objective: "Write and review production code",
    requiredCapabilities: ["coding"],
    preferredTier: "premium",
    approvePaidModelForThisRequest: false,
  });
  assert.equal(unapproved.status, 201);
  assert.equal(unapproved.headers.get("x-buddy-model-plan-status"), "paid_approval_required");
  const paid = unapproved.json.candidates.filter((candidate: any) => ["paid", "freemium"].includes(candidate.tier));
  assert.ok(paid.length > 0);
  assert.ok(paid.every((candidate: any) => candidate.readiness === "paid_approval_required"));
  assert.equal(unapproved.json.automaticPaidUpgrade, false);
  assert.equal(unapproved.json.providerCallExecuted, false);

  const approved = await call("POST", "/api/buddy/models/select", USER, {
    objective: "Write and review production code",
    requiredCapabilities: ["coding"],
    preferredTier: "premium",
    approvePaidModelForThisRequest: true,
  });
  assert.equal(approved.status, 201);
  assert.ok(approved.json.candidates.every((candidate: any) => candidate.readiness !== "local_route_ready"));
  assert.equal(approved.json.providerCallExecuted, false);
});

test("full server/routes.ts boot: every model route rejects an unauthenticated caller", { skip: fullBootError ? `server/routes.ts cannot be imported on this base commit: ${fullBootError}` : false }, async () => {
  for (const route of BUDDY_MODEL_ROUTES) {
    const result = await call(route.method, route.path, undefined, undefined, fullBase);
    assert.equal(result.status, 401, `${route.method} ${route.path}`);
    assert.equal(result.json?.code, "caller_identity_required");
  }
});

test("BUDDY_MODEL_OWNER_SUBJECTS unset means no owners; discovery stays closed", () => {
  assert.equal(buddyModelOwnerSubjects({}).size, 0);
  assert.equal(buddyModelOwnerSubjects({ BUDDY_MODEL_OWNER_SUBJECTS: "" }).size, 0);
  assert.equal(buddyModelOwnerSubjects({ BUDDY_MODEL_OWNER_SUBJECTS: "  ,  " }).size, 0);
  assert.deepEqual(
    [...buddyModelOwnerSubjects({ BUDDY_MODEL_OWNER_SUBJECTS: "google:abc, apple:xyz, bad, GOOGLE:skip" })].sort(),
    ["apple:xyz", "google:abc"],
  );
});
