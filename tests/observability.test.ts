import assert from "node:assert/strict";
import test from "node:test";

import { productionReadinessSnapshot } from "../server/observability";

function withEnv(env: Record<string, string | undefined>, fn: () => void) {
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
    fn();
  } finally {
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

test("readiness is false until customer-critical production services are configured", () => {
  withEnv(
    {
      DATABASE_URL: undefined,
      STRIPE_SECRET_KEY: undefined,
      STRIPE_LIVE_SECRET_KEY: undefined,
      STRIPE_WEBHOOK_SECRET: undefined,
    },
    () => {
      const snapshot = productionReadinessSnapshot();
      assert.equal(snapshot.ready, false);
      assert.equal(snapshot.checks.databaseConfigured, false);
      assert.equal(snapshot.checks.stripeConfigured, false);
      assert.equal(snapshot.checks.stripeWebhookConfigured, false);
    },
  );
});

test("readiness is true when database and Stripe live services are configured", () => {
  withEnv(
    {
      DATABASE_URL: "postgresql://user:pass@example.test:5432/dreamco",
      STRIPE_SECRET_KEY: undefined,
      STRIPE_LIVE_SECRET_KEY: "sk_live_test",
      STRIPE_WEBHOOK_SECRET: "whsec_test",
    },
    () => {
      const snapshot = productionReadinessSnapshot();
      assert.equal(snapshot.ready, true);
      assert.equal(snapshot.checks.databaseConfigured, true);
      assert.equal(snapshot.checks.stripeConfigured, true);
      assert.equal(snapshot.checks.stripeWebhookConfigured, true);
    },
  );
});
