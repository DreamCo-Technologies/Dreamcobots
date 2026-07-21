import { Router, type IRouter } from "express";
import { getStripeClient } from "../lib/stripeClient";
import { requireAuth } from "../middlewares/authMiddleware";

const router: IRouter = Router();

// Profit targets from master_config.yaml
const DAILY_TARGET = 500;
const WEEKLY_TARGET = 3500;
const MONTHLY_TARGET = 15000;

router.get("/stripe/revenue", requireAuth, async (req, res): Promise<void> => {
  const stripe = await getStripeClient();

  if (!stripe) {
    // Honest: no Stripe key => no revenue data. Show real zeros, not demo numbers.
    res.json({
      totalRevenue: 0,
      dailyRevenue: 0,
      weeklyRevenue: 0,
      monthlyRevenue: 0,
      dailyTarget: DAILY_TARGET,
      weeklyTarget: WEEKLY_TARGET,
      monthlyTarget: MONTHLY_TARGET,
      currency: "usd",
      connected: false,
    });
    return;
  }

  try {
    const now = Math.floor(Date.now() / 1000);
    const dayAgo = now - 86400;
    const weekAgo = now - 604800;
    const monthAgo = now - 2592000;

    const [dayCharges, weekCharges, monthCharges, allCharges] = await Promise.all([
      stripe.charges.list({ created: { gte: dayAgo }, limit: 100 }),
      stripe.charges.list({ created: { gte: weekAgo }, limit: 100 }),
      stripe.charges.list({ created: { gte: monthAgo }, limit: 100 }),
      stripe.charges.list({ limit: 100 }),
    ]);

    const sum = (charges: typeof dayCharges) =>
      charges.data.filter((c) => c.status === "succeeded")
        .reduce((acc, c) => acc + c.amount, 0) / 100;

    res.json({
      totalRevenue: sum(allCharges),
      dailyRevenue: sum(dayCharges),
      weeklyRevenue: sum(weekCharges),
      monthlyRevenue: sum(monthCharges),
      dailyTarget: DAILY_TARGET,
      weeklyTarget: WEEKLY_TARGET,
      monthlyTarget: MONTHLY_TARGET,
      currency: "usd",
      connected: true,
    });
  } catch (err) {
    req.log.error({ err }, "Stripe revenue fetch failed");
    res.json({
      totalRevenue: 0, dailyRevenue: 0, weeklyRevenue: 0, monthlyRevenue: 0,
      dailyTarget: DAILY_TARGET, weeklyTarget: WEEKLY_TARGET,
      monthlyTarget: MONTHLY_TARGET, currency: "usd", connected: false,
    });
  }
});

router.get("/stripe/subscriptions", requireAuth, async (req, res): Promise<void> => {
  const stripe = await getStripeClient();

  if (!stripe) {
    // Honest: no Stripe key => no subscriptions to report.
    res.json([]);
    return;
  }

  try {
    const subs = await stripe.subscriptions.list({ limit: 50, status: "active" });
    const result = await Promise.all(
      subs.data.map(async (sub) => {
        let customer = sub.customer as string;
        try {
          const cust = await stripe.customers.retrieve(customer);
          if ("email" in cust && cust.email) customer = cust.email;
        } catch {}
        const item = sub.items.data[0];
        return {
          id: sub.id,
          customer,
          plan: item?.price?.nickname ?? item?.price?.id ?? "unknown",
          status: sub.status,
          amount: (item?.price?.unit_amount ?? 0) / 100,
          currency: item?.price?.currency ?? "usd",
          currentPeriodEnd: new Date(((sub as unknown as { current_period_end?: number }).current_period_end ?? (item as unknown as { current_period_end?: number })?.current_period_end ?? 0) * 1000).toISOString(),
        };
      })
    );
    res.json(result);
  } catch (err) {
    req.log.error({ err }, "Stripe subscriptions fetch failed");
    res.json([]);
  }
});

router.get("/stripe/transactions", requireAuth, async (req, res): Promise<void> => {
  const stripe = await getStripeClient();

  if (!stripe) {
    // Honest: no Stripe key => no transactions to report.
    res.json([]);
    return;
  }

  try {
    const charges = await stripe.charges.list({ limit: 25 });
    res.json(
      charges.data.map((c) => ({
        id: c.id,
        amount: c.amount / 100,
        currency: c.currency,
        status: c.status,
        description: c.description ?? "Payment",
        date: new Date(c.created * 1000).toISOString(),
      }))
    );
  } catch (err) {
    req.log.error({ err }, "Stripe transactions fetch failed");
    res.json([]);
  }
});

router.post("/stripe/checkout", requireAuth, async (req, res): Promise<void> => {
  const stripe = await getStripeClient();
  if (!stripe) {
    res.status(503).json({ error: "Stripe not configured. Add STRIPE_SECRET_KEY." });
    return;
  }
  const body = req.body as { tier?: string; botSlug?: string; successUrl?: string; cancelUrl?: string };
  const tierPrices: Record<string, number> = { FREE: 0, PRO: 4900, ENTERPRISE: 29900 };
  const tier = (body.tier ?? "PRO").toUpperCase();
  const amount = tierPrices[tier] ?? 4900;
  if (amount === 0) {
    res.status(400).json({ error: "FREE tier has no checkout" });
    return;
  }
  const origin =
    req.headers.origin ??
    (process.env.DREAMCO_DOMAINS?.split(",")[0]
      ? `https://${process.env.DREAMCO_DOMAINS.split(",")[0]}`
      : "http://localhost");
  try {
    const session = await stripe.checkout.sessions.create({
      mode: "subscription",
      line_items: [
        {
          price_data: {
            currency: "usd",
            product_data: { name: `DreamCo ${tier}` },
            unit_amount: amount,
            recurring: { interval: "month" },
          },
          quantity: 1,
        },
      ],
      metadata: { tier, bot_slug: body.botSlug ?? "platform" },
      success_url: body.successUrl ?? `${origin}/revenue?status=success`,
      cancel_url: body.cancelUrl ?? `${origin}/revenue?status=cancelled`,
    });
    res.json({ url: session.url, id: session.id });
  } catch (err) {
    req.log.error({ err }, "checkout session failed");
    res.status(500).json({ error: "checkout failed" });
  }
});

export default router;
