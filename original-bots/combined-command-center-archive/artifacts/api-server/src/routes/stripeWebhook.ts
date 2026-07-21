import { Router, type IRouter, raw } from "express";
import { db, botEarningsTable, eventsTable } from "@workspace/db";
import { getStripeClient } from "../lib/stripeClient";

const router: IRouter = Router();

router.post(
  "/stripe/webhook",
  raw({ type: "application/json" }),
  async (req, res): Promise<void> => {
    const stripe = await getStripeClient();
    const sig = req.headers["stripe-signature"];
    const whSecret = process.env.STRIPE_WEBHOOK_SECRET;

    if (!stripe || !whSecret || typeof sig !== "string") {
      res.status(503).json({ error: "Stripe webhook not configured" });
      return;
    }

    let event: import("stripe").Stripe.Event;
    try {
      event = stripe.webhooks.constructEvent(req.body as Buffer, sig, whSecret);
    } catch (err) {
      req.log.warn({ err }, "stripe webhook signature failed");
      res.status(400).send("invalid signature");
      return;
    }

    try {
      if (event.type === "charge.succeeded" || event.type === "payment_intent.succeeded") {
        const obj = event.data.object as unknown as Record<string, unknown>;
        const amount = Number((obj.amount_received ?? obj.amount) ?? 0) / 100;
        const currency = String(obj.currency ?? "usd");
        const md = (obj.metadata ?? {}) as Record<string, string>;
        const botSlug = md.bot_slug ?? md.bot ?? "unknown";
        await db.insert(botEarningsTable).values({
          botSlug,
          source: event.type,
          amountUsd: amount,
          currency,
          stripeChargeId: String(obj.id ?? ""),
          stripeCustomerId: typeof obj.customer === "string" ? obj.customer : null,
          metadata: md,
        });
        await db.insert(eventsTable).values({
          eventType: "revenue.generated",
          source: "stripe",
          severity: "info",
          payload: { botSlug, amount, currency, stripeId: obj.id },
        });
      } else if (event.type === "customer.subscription.created") {
        const obj = event.data.object as unknown as Record<string, unknown>;
        await db.insert(eventsTable).values({
          eventType: "subscription.created",
          source: "stripe",
          severity: "info",
          payload: obj,
        });
      }
      res.json({ received: true });
    } catch (err) {
      req.log.error({ err, type: event.type }, "stripe webhook handler failed");
      res.status(500).json({ error: "handler failed" });
    }
  },
);

export default router;
