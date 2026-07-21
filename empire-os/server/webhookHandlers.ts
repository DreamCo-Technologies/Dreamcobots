import Stripe from "stripe";

// ---------------------------------------------------------------------------
// Stripe webhook handler
// ---------------------------------------------------------------------------

async function getStripeInstance(): Promise<Stripe> {
  const key = process.env.STRIPE_SECRET_KEY ?? "";
  return new Stripe(key, { apiVersion: "2026-02-25.clover" });
}

export class WebhookHandlers {
  static async processWebhook(payload: Buffer, signature: string): Promise<void> {
    const webhookSecret = process.env.STRIPE_WEBHOOK_SECRET;
    if (!webhookSecret) {
      console.warn("[webhook] STRIPE_WEBHOOK_SECRET not set – skipping signature verification");
    }

    const stripe = await getStripeInstance();
    let event: Stripe.Event;

    if (webhookSecret) {
      event = stripe.webhooks.constructEvent(payload, signature, webhookSecret);
    } else {
      event = JSON.parse(payload.toString()) as Stripe.Event;
    }

    switch (event.type) {
      case "checkout.session.completed":
        console.log("[webhook] checkout.session.completed", (event.data.object as any).id);
        break;
      case "customer.subscription.updated":
        console.log("[webhook] customer.subscription.updated", (event.data.object as any).id);
        break;
      case "customer.subscription.deleted":
        console.log("[webhook] customer.subscription.deleted", (event.data.object as any).id);
        break;
      case "invoice.payment_succeeded":
        console.log("[webhook] invoice.payment_succeeded", (event.data.object as any).id);
        break;
      case "invoice.payment_failed":
        console.warn("[webhook] invoice.payment_failed", (event.data.object as any).id);
        break;
      default:
        console.log(`[webhook] unhandled event type: ${event.type}`);
    }
  }
}
