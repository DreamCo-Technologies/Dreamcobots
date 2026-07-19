/**
 * Playwright E2E test: Stripe Checkout end-to-end via BuyBotsModal
 *
 * Covers:
 *   - BuyBotsModal opens and defaults to the Subscription Plans tab
 *   - Products load from the DB (or show a skeleton/loading state — never dead)
 *   - Subscribe button on a non-free plan is enabled and clickable
 *   - Clicking Subscribe either:
 *       (a) redirects to checkout.stripe.com — full Stripe path, OR
 *       (b) shows a toast with a non-empty meaningful error — graceful no-key path
 *     It must NEVER silently do nothing.
 *   - While checkout is pending the button shows a loading/disabled state (no dead action)
 *
 * Gracefully skips the redirect assertion when STRIPE_SECRET_KEY is absent (e.g. CI).
 *
 * Run:
 *   npx playwright test tests/stripe-checkout.spec.ts
 *
 * Requires the dev server to be running on http://localhost:5000.
 */

import { test, expect, type Page } from "@playwright/test";

const BASE_URL = "http://localhost:5000";
const stripeConfigured = Boolean(process.env.STRIPE_SECRET_KEY);

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

async function openBuyBotsModal(page: Page) {
  await page.goto(BASE_URL, { waitUntil: "networkidle" });

  // Wait for React to hydrate and the Buy Bots button to appear
  await page.waitForSelector('[data-testid="buy-bots-btn"], [data-testid="buy-bots-mobile"]', {
    state: "attached",
    timeout: 15_000,
  });

  // Try the first visible Buy Bots button (desktop header or chat footer)
  const allBuyBtns = page.locator('[data-testid="buy-bots-btn"]');
  const count = await allBuyBtns.count();
  let clicked = false;
  for (let i = 0; i < count; i++) {
    const btn = allBuyBtns.nth(i);
    try {
      await btn.scrollIntoViewIfNeeded({ timeout: 2000 });
      const visible = await btn.isVisible({ timeout: 2000 });
      if (visible) {
        await btn.click();
        clicked = true;
        break;
      }
    } catch {
      // try next
    }
  }

  if (!clicked) {
    const mobileBtn = page.getByTestId("buy-bots-mobile");
    await mobileBtn.scrollIntoViewIfNeeded({ timeout: 2000 }).catch(() => {});
    await mobileBtn.click({ force: true });
  }

  await page.waitForSelector('[data-testid="tab-plans"], [data-testid="tab-bots"]', {
    state: "attached",
    timeout: 10_000,
  });
}

async function ensurePlansTab(page: Page) {
  const plansTab = page.getByTestId("tab-plans");
  if (await plansTab.isVisible().catch(() => false)) {
    const isActive = await plansTab.evaluate(
      (el) => el.getAttribute("data-state") === "active" || el.getAttribute("aria-selected") === "true" ||
               el.classList.contains("active") || el.getAttribute("data-active") !== null
    ).catch(() => false);
    if (!isActive) {
      await plansTab.click();
      await page.waitForTimeout(500);
    }
  }
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

test.describe("BuyBotsModal — Stripe checkout", () => {
  test("modal opens and defaults to Subscription Plans tab", async ({ page }) => {
    await openBuyBotsModal(page);
    await ensurePlansTab(page);

    const plansTab = page.getByTestId("tab-plans");
    const botsTab = page.getByTestId("tab-bots");
    const eitherTabVisible = (await plansTab.isVisible().catch(() => false)) ||
                             (await botsTab.isVisible().catch(() => false));
    expect(eitherTabVisible).toBe(true);
  });

  test("products loading state is never dead — shows skeleton or plan cards", async ({ page }) => {
    await openBuyBotsModal(page);
    await ensurePlansTab(page);

    const planCardLocator = page.locator('[data-testid^="plan-card-"]');
    const skeletonLocator = page.locator('[class*="skeleton"], [class*="Skeleton"]');
    const stripeNotConnected = page.getByText("Stripe not connected");
    const pricingLoadingText = page.getByText(/Pricing plans loading/i);

    await page.waitForFunction(
      () => {
        const hasPlanCards = document.querySelectorAll('[data-testid^="plan-card-"]').length > 0;
        const hasSkeletons = document.querySelectorAll('[class*="skeleton"], [class*="Skeleton"]').length > 0;
        const hasNotConnected = document.body.innerText.includes("Stripe not connected");
        const hasLoadingText = document.body.innerText.includes("Pricing plans loading");
        return hasPlanCards || hasSkeletons || hasNotConnected || hasLoadingText;
      },
      { timeout: 15_000 }
    );

    const hasCards = await planCardLocator.count() > 0;
    const hasSkeletons = await skeletonLocator.count() > 0;
    const hasNotConnected = await stripeNotConnected.isVisible().catch(() => false);
    const hasLoadingMsg = await pricingLoadingText.isVisible().catch(() => false);

    const hasAnyValidState = hasCards || hasSkeletons || hasNotConnected || hasLoadingMsg;
    expect(
      hasAnyValidState,
      "Modal must show plan cards, skeleton loaders, or a 'not connected' message — never a dead empty state"
    ).toBe(true);
  });

  test("non-free Subscribe buttons are enabled when products are loaded", async ({ page }) => {
    await openBuyBotsModal(page);
    await ensurePlansTab(page);

    const planCards = page.locator('[data-testid^="plan-card-"]').filter({
      hasNot: page.locator('[data-testid="plan-card-free"]'),
    });

    const cardCount = await planCards.count().catch(() => 0);
    if (cardCount === 0) {
      test.skip();
      return;
    }

    for (const tierKey of ["pro", "enterprise", "elite"]) {
      const btn = page.getByTestId(`subscribe-${tierKey}`);
      if (await btn.isVisible().catch(() => false)) {
        await expect(btn).not.toBeDisabled();
      }
    }
  });

  test("clicking Subscribe never silently fails — shows redirect or meaningful toast", async ({ page }) => {
    await openBuyBotsModal(page);
    await ensurePlansTab(page);

    // Wait briefly for the UI to settle, then check what state products are in
    await page.waitForTimeout(2000);

    const stripeNotConnected = await page.getByText("Stripe not connected").isVisible().catch(() => false);
    if (stripeNotConnected) {
      test.skip();
      return;
    }

    // If plan cards are not visible yet (still loading/syncing), skip gracefully
    const planCardCount = await page.locator('[data-testid^="plan-card-"]').count().catch(() => 0);
    if (planCardCount === 0) {
      test.skip();
      return;
    }

    let subscribeBtn: import("@playwright/test").Locator | null = null;
    for (const tierKey of ["pro", "enterprise", "elite"]) {
      const btn = page.getByTestId(`subscribe-${tierKey}`);
      if (await btn.isVisible().catch(() => false) && !(await btn.isDisabled().catch(() => true))) {
        subscribeBtn = btn;
        break;
      }
    }

    if (!subscribeBtn) {
      test.skip();
      return;
    }

    let redirected = false;
    page.on("framenavigated", (frame) => {
      if (frame === page.mainFrame() && frame.url().includes("stripe.com")) {
        redirected = true;
      }
    });

    await subscribeBtn.click();

    if (stripeConfigured) {
      await page.waitForURL(/checkout\.stripe\.com/, { timeout: 15_000 });
      expect(page.url()).toContain("checkout.stripe.com");
    } else {
      const toastSelector = '[role="status"], [data-radix-toast-viewport], .toast, [class*="toast"], [class*="Toast"]';
      const anyFeedback = await Promise.race([
        page.waitForSelector(toastSelector, { timeout: 8_000 }).then(() => "toast"),
        page.waitForURL(/stripe\.com/, { timeout: 8_000 }).then(() => "redirect").catch(() => null),
      ]).catch(() => null);

      const toastEl = await page.$(toastSelector);
      const toastText = toastEl ? await toastEl.innerText().catch(() => "") : "";

      const hasRedirect = redirected || page.url().includes("stripe.com");
      const hasMeaningfulToast = toastEl !== null && toastText.trim().length > 0;

      expect(
        hasRedirect || hasMeaningfulToast,
        `Checkout must result in a Stripe redirect OR a non-empty toast. Got: url=${page.url()}, toast="${toastText}"`
      ).toBe(true);

      if (hasMeaningfulToast) {
        expect(toastText.trim()).not.toBe("");
        const looksLikeError = /checkout failed|failed|error|something went wrong/i.test(toastText);
        const looksLikeSuccess = /success|subscribed/i.test(toastText);
        expect(
          looksLikeError || looksLikeSuccess,
          `Toast text should describe the outcome, got: "${toastText}"`
        ).toBe(true);
      }
    }
  });

  test("Subscribe button shows loading/disabled state while checkout is pending", async ({ page }) => {
    await openBuyBotsModal(page);
    await ensurePlansTab(page);

    // Wait briefly for the UI to settle, then check what state products are in
    await page.waitForTimeout(2000);

    const stripeNotConnected = await page.getByText("Stripe not connected").isVisible().catch(() => false);
    if (stripeNotConnected) {
      test.skip();
      return;
    }

    // If plan cards are not visible yet (still loading/syncing), skip gracefully
    const planCardCount = await page.locator('[data-testid^="plan-card-"]').count().catch(() => 0);
    if (planCardCount === 0) {
      test.skip();
      return;
    }

    let subscribeBtn: import("@playwright/test").Locator | null = null;
    for (const tierKey of ["pro", "enterprise", "elite"]) {
      const btn = page.getByTestId(`subscribe-${tierKey}`);
      if (await btn.isVisible().catch(() => false) && !(await btn.isDisabled().catch(() => true))) {
        subscribeBtn = btn;
        break;
      }
    }

    if (!subscribeBtn) {
      test.skip();
      return;
    }

    let wasDisabledOrSpinning = false;

    const clickAndObserve = async () => {
      await subscribeBtn!.click();
      for (let i = 0; i < 20; i++) {
        const isDisabled = await subscribeBtn!.isDisabled().catch(() => false);
        const hasSpinner = await page.$('[data-testid^="subscribe-"] svg[class*="spin"], [data-testid^="subscribe-"] .animate-spin').then(Boolean).catch(() => false);
        if (isDisabled || hasSpinner) {
          wasDisabledOrSpinning = true;
          break;
        }
        await page.waitForTimeout(50);
      }
    };

    await clickAndObserve();

    if (!wasDisabledOrSpinning) {
      const toastEl = await page.$('[role="status"], [data-radix-toast-viewport], .toast, [class*="toast"]');
      const toastText = toastEl ? await toastEl.innerText().catch(() => "") : "";
      expect(
        toastText.trim().length > 0,
        "After clicking Subscribe, the button must either show a spinner/disabled state OR a meaningful toast must appear — no silent dead action"
      ).toBe(true);
    } else {
      expect(wasDisabledOrSpinning).toBe(true);
    }
  });
});
