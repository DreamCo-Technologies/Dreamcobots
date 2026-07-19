/**
 * Integration test: Stripe Checkout End-to-End Pipeline
 *
 * Verifies the full flow:
 *   GET /api/stripe/products  → returns products or graceful not-configured response
 *   POST /api/stripe/checkout → returns { url } or meaningful { error }, never silent
 *
 * Gracefully skips Stripe-specific assertions when STRIPE_SECRET_KEY is absent
 * (e.g. in CI). The test still runs all API-shape assertions.
 *
 * Run with:
 *   npx tsx tests/stripe-checkout.test.ts
 *
 * Requires: DATABASE_URL env var (STRIPE_SECRET_KEY optional).
 */

import { spawn, type ChildProcess } from "child_process";
import { setTimeout as sleep } from "timers/promises";

const TEST_PORT = 5098;
const BASE_URL = `http://localhost:${TEST_PORT}`;
const SERVER_STARTUP_TIMEOUT_MS = 40_000;

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function assert(condition: boolean, message: string): void {
  if (!condition) throw new Error(`ASSERTION FAILED: ${message}`);
}

function skip(message: string): never {
  console.log(`\n  ⚠  SKIPPED — ${message}`);
  process.exit(0);
}

async function waitForServer(url: string, timeoutMs: number): Promise<void> {
  const deadline = Date.now() + timeoutMs;
  while (Date.now() < deadline) {
    try {
      const res = await fetch(`${url}/api/stripe/products`);
      if (res.ok || res.status === 500) return; // server is up
    } catch {
      // not ready yet
    }
    await sleep(500);
  }
  throw new Error(`Server at ${url} did not become ready within ${timeoutMs}ms`);
}

// ---------------------------------------------------------------------------
// Server lifecycle
// ---------------------------------------------------------------------------

function startServer(): ChildProcess {
  const server = spawn("npx", ["tsx", "server/index.ts"], {
    env: { ...process.env, PORT: String(TEST_PORT), NODE_ENV: "test" },
    stdio: ["ignore", "pipe", "pipe"],
  });
  server.stdout?.on("data", (d: Buffer) => process.stdout.write(`[server] ${d}`));
  server.stderr?.on("data", (d: Buffer) => process.stderr.write(`[server:err] ${d}`));
  return server;
}

// ---------------------------------------------------------------------------
// Test
// ---------------------------------------------------------------------------

async function runCheckoutTest(): Promise<void> {
  console.log("\nStripe Checkout Integration Test");
  console.log("=================================");

  const stripeConfigured = Boolean(process.env.STRIPE_SECRET_KEY);
  console.log(`  Stripe keys present: ${stripeConfigured ? "yes (live assertions enabled)" : "no (skip-redirect path)"}`);

  let server: ChildProcess | null = null;

  // Detect if a server is already running (e.g. local dev on default port 5000)
  let serverAlreadyRunning = false;
  let effectiveBase = BASE_URL;
  try {
    await waitForServer("http://localhost:5000", 1_000);
    serverAlreadyRunning = true;
    effectiveBase = "http://localhost:5000";
    console.log("  Using existing server at http://localhost:5000");
  } catch {
    console.log(`  Starting server on port ${TEST_PORT}...`);
    server = startServer();
    await waitForServer(effectiveBase, SERVER_STARTUP_TIMEOUT_MS);
    console.log("  ✓ Server is ready");
  }

  try {
    // ------------------------------------------------------------------
    // Step 1: GET /api/stripe/products — shape assertions
    // ------------------------------------------------------------------
    console.log("\nStep 1: GET /api/stripe/products — verify response shape...");
    const productsRes = await fetch(`${effectiveBase}/api/stripe/products`);

    assert(
      productsRes.status === 200,
      `Expected 200 from /api/stripe/products, got ${productsRes.status}`
    );

    const productsData = (await productsRes.json()) as {
      products: any[];
      syncing?: boolean;
      source?: string;
    };

    assert(
      Array.isArray(productsData.products),
      `Expected products to be an array, got: ${typeof productsData.products}`
    );

    console.log(`  ✓ Status: 200  products.length: ${productsData.products.length}  syncing: ${productsData.syncing ?? false}`);

    if (productsData.products.length > 0) {
      const first = productsData.products[0];
      assert(typeof first.id === "string", "Product must have a string id");
      assert(typeof first.name === "string", "Product must have a string name");
      assert(Array.isArray(first.prices), "Product must have a prices array");
      console.log("  ✓ Product shape validated (id, name, prices[])");
    }

    // ------------------------------------------------------------------
    // Step 2: POST /api/stripe/checkout — missing priceId → 400 + error
    // ------------------------------------------------------------------
    console.log("\nStep 2: POST /api/stripe/checkout without priceId → expect 400 + error body...");
    const noIdRes = await fetch(`${effectiveBase}/api/stripe/checkout`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({}),
    });

    assert(
      noIdRes.status === 400,
      `Expected 400 for missing priceId, got ${noIdRes.status}`
    );

    const noIdBody = (await noIdRes.json()) as { error: string };
    assert(
      typeof noIdBody.error === "string" && noIdBody.error.length > 0,
      `Expected a non-empty error string, got: ${JSON.stringify(noIdBody)}`
    );

    console.log(`  ✓ Status: 400  error: "${noIdBody.error}"`);

    // ------------------------------------------------------------------
    // Step 3: POST /api/stripe/checkout — valid priceId
    //   When Stripe is configured  → expect { url: "https://checkout.stripe.com/..." }
    //   When Stripe is NOT configured → expect HTTP 500 + { error: "..." } (never silent)
    // ------------------------------------------------------------------
    const testPriceId = productsData.products.length > 0
      ? (() => {
          for (const p of productsData.products) {
            if (p.prices && p.prices.length > 0 && p.prices[0].unit_amount > 0) {
              return p.prices[0].id as string;
            }
          }
          return null;
        })()
      : null;

    if (!testPriceId) {
      console.log("\nStep 3: No paid price found — skipping checkout call (no paid plans seeded).");
    } else {
      console.log(`\nStep 3: POST /api/stripe/checkout with priceId=${testPriceId}...`);

      const checkoutRes = await fetch(`${effectiveBase}/api/stripe/checkout`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          priceId: testPriceId,
          successUrl: `${effectiveBase}/?checkout=success`,
          cancelUrl: `${effectiveBase}/?checkout=canceled`,
        }),
      });

      const checkoutBody = (await checkoutRes.json()) as { url?: string; error?: string };

      if (stripeConfigured) {
        // Full Stripe environment: expect a real checkout URL
        assert(
          checkoutRes.status === 200,
          `Expected 200 from checkout with Stripe configured, got ${checkoutRes.status}. Body: ${JSON.stringify(checkoutBody)}`
        );
        assert(
          typeof checkoutBody.url === "string" && checkoutBody.url.startsWith("https://checkout.stripe.com"),
          `Expected a Stripe checkout URL, got: ${JSON.stringify(checkoutBody)}`
        );
        console.log(`  ✓ Stripe checkout URL returned: ${checkoutBody.url!.slice(0, 60)}...`);
      } else {
        // No Stripe key: must fail with a meaningful error, not silently
        assert(
          checkoutRes.status === 500,
          `Expected 500 when Stripe not configured, got ${checkoutRes.status}. Body: ${JSON.stringify(checkoutBody)}`
        );
        assert(
          typeof checkoutBody.error === "string" && checkoutBody.error.length > 0,
          `Expected a non-empty error message from unconfigured Stripe, got: ${JSON.stringify(checkoutBody)}`
        );
        // Most critically: no silent empty fallback — the response must NOT contain an empty url
        assert(
          !("url" in checkoutBody) || typeof checkoutBody.url !== "string",
          `Checkout must not return a url when Stripe is unconfigured — got: ${JSON.stringify(checkoutBody)}`
        );
        console.log(`  ✓ Meaningful error returned (not a silent fallback): "${checkoutBody.error}"`);
      }
    }

    // ------------------------------------------------------------------
    // Step 4: POST /api/stripe/checkout — fake priceId → meaningful error
    // ------------------------------------------------------------------
    console.log("\nStep 4: POST /api/stripe/checkout with fake priceId → expect meaningful error...");
    const fakeRes = await fetch(`${effectiveBase}/api/stripe/checkout`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        priceId: "price_this_does_not_exist",
        successUrl: `${effectiveBase}/?checkout=success`,
        cancelUrl: `${effectiveBase}/?checkout=canceled`,
      }),
    });

    const fakeBody = (await fakeRes.json()) as { url?: string; error?: string };

    // Must never be 200 with an empty URL (silent fallback)
    const isSilentFallback =
      fakeRes.status === 200 &&
      (!fakeBody.url || fakeBody.url.trim() === "");

    assert(
      !isSilentFallback,
      `Checkout returned a silent empty fallback for a fake priceId — this is the regression we guard against!`
    );

    // Must be either an error response (4xx/5xx) or a valid URL (if Stripe auto-rejects)
    const hasError = typeof fakeBody.error === "string" && fakeBody.error.length > 0;
    const hasUrl = typeof fakeBody.url === "string" && fakeBody.url.startsWith("https://");
    assert(
      hasError || hasUrl,
      `Expected either an error message or a Stripe URL, got: ${JSON.stringify(fakeBody)}`
    );

    if (hasError) {
      console.log(`  ✓ Fake priceId returns meaningful error: "${fakeBody.error}"`);
    } else {
      console.log(`  ✓ Fake priceId returned a URL (Stripe validated it): ${fakeBody.url}`);
    }

  } finally {
    if (server && !serverAlreadyRunning) {
      console.log("\nStopping test server...");
      server.kill("SIGTERM");
      await sleep(1000);
      if (!server.killed) server.kill("SIGKILL");
      console.log("  ✓ Server stopped");
    }
  }

  console.log("\n✅ PASSED — Stripe checkout pipeline works end-to-end (no silent empty fallbacks).\n");
}

runCheckoutTest().catch((err) => {
  console.error(`\n❌ FAILED — ${err.message}\n`);
  process.exit(1);
});
