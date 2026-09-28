import assert from "node:assert/strict";
import test from "node:test";
import express from "express";
import { once } from "node:events";

import { productionReadinessSnapshot, checkProductionReadiness, setRuntimeReadiness, requireRuntime, sendReadiness } from "../server/observability";

async function withEnv(env: Record<string, string | undefined>, fn: () => void | Promise<void>) {
  const keys = Object.keys(env);
  const previous = new Map(keys.map((key) => [key, process.env[key]]));
  try {
    for (const [key, value] of Object.entries(env)) {
      if (value === undefined) {
        delete process.env[key];
      } else {
        process.env[key] = value;
      }
    }
    await fn();
  } finally {
    setRuntimeReadiness();
    for (const key of keys) {
      const value = previous.get(key);
      if (value === undefined) {
        delete process.env[key];
      } else {
        process.env[key] = value;
      }
    }
  }
}

test("readiness is false until customer-critical production services are configured", async () => {
  await withEnv(
    {
      DATABASE_URL: undefined,
      STRIPE_SECRET_KEY: undefined,
      STRIPE_LIVE_SECRET_KEY: undefined,
      STRIPE_WEBHOOK_SECRET: undefined,
    },
    async () => {
      const snapshot = productionReadinessSnapshot();
      assert.equal(snapshot.ready, false);
      assert.equal(snapshot.checks.databaseConfigured, false);
      assert.equal(snapshot.checks.stripeConfigured, false);
      assert.equal(snapshot.checks.stripeWebhookConfigured, false);
    },
  );
});

test("readiness requires initialized routes and a responding database", async () => {
  await withEnv(
    {
      DATABASE_URL: "postgresql://user:pass@example.test:5432/dreamco",
      STRIPE_SECRET_KEY: undefined,
      STRIPE_LIVE_SECRET_KEY: "sk_live_test",
      STRIPE_WEBHOOK_SECRET: "whsec_test",
    },
    async () => {
      assert.equal(productionReadinessSnapshot().ready, false);
      setRuntimeReadiness(async () => ({ rows: [{ result: 1 }] }));
      const snapshot = await checkProductionReadiness();
      assert.equal(snapshot.ready, true);
      assert.equal(snapshot.checks.runtimeInitialized, true);
      assert.equal(snapshot.checks.databaseReachable, true);
      assert.equal(snapshot.checks.databaseConfigured, true);
      assert.equal(snapshot.checks.stripeConfigured, true);
      assert.equal(snapshot.checks.stripeWebhookConfigured, true);
    },
  );
});


test("a database outage makes configured routes unready without exposing errors", async () => {
  await withEnv({ DATABASE_URL: "postgresql://synthetic.invalid/db", STRIPE_SECRET_KEY: "synthetic", STRIPE_WEBHOOK_SECRET: "synthetic" }, async () => {
    setRuntimeReadiness(async () => { throw new Error("private connection details"); });
    const snapshot = await checkProductionReadiness();
    assert.equal(snapshot.ready, false);
    assert.equal(snapshot.checks.runtimeInitialized, true);
    assert.equal(snapshot.checks.databaseReachable, false);
    assert.doesNotMatch(JSON.stringify(snapshot), /private connection details/);
  });
});

test("readiness times out a hung database probe", async () => {
  await withEnv({ DATABASE_URL: "postgresql://synthetic.invalid/db", STRIPE_SECRET_KEY: "synthetic", STRIPE_WEBHOOK_SECRET: "synthetic" }, async () => {
    setRuntimeReadiness(() => new Promise(() => {}));
    const snapshot = await checkProductionReadiness();
    assert.equal(snapshot.ready, false);
    assert.equal(snapshot.checks.databaseReachable, false);
  });
});


test("HTTP readiness and application requests fail closed until runtime initialization", async () => {
  const app = express();
  app.get("/api/ready", async (_req, res) => { await sendReadiness(res); });
  app.use("/api", requireRuntime());
  app.get("/api/bots", (_req, res) => { res.json({ bots: [] }); });
  const server = app.listen(0, "127.0.0.1");
  await once(server, "listening");
  const address = server.address();
  assert.ok(address && typeof address !== "string");
  const base = `http://127.0.0.1:${address.port}`;
  try {
    setRuntimeReadiness();
    assert.equal((await fetch(`${base}/api/ready`)).status, 503);
    const unavailable = await fetch(`${base}/api/bots`);
    assert.equal(unavailable.status, 503);
    assert.deepEqual(await unavailable.json(), { error: "Application runtime is unavailable" });
    setRuntimeReadiness(async () => ({}));
    assert.equal((await fetch(`${base}/api/bots`)).status, 200);
  } finally {
    setRuntimeReadiness();
    await new Promise<void>((resolve, reject) => server.close(error => error ? reject(error) : resolve()));
  }
});
