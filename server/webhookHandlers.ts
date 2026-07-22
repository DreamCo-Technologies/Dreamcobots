import type Stripe from 'stripe';

import { storage } from './storage';
import { getUncachableStripeClient } from './stripeClient';

export class WebhookHandlers {
  static async processWebhook(payload: Buffer, signature: string): Promise<Stripe.Event> {
    if (!Buffer.isBuffer(payload)) {
      throw new Error(
        'STRIPE WEBHOOK ERROR: Payload must be a Buffer. ' +
        'Received type: ' + typeof payload + '. ' +
        'Ensure webhook route is registered BEFORE app.use(express.json()).'
      );
    }

    const webhookSecret = process.env.STRIPE_WEBHOOK_SECRET;
    if (!webhookSecret) throw new Error('STRIPE_WEBHOOK_SECRET is not configured.');
    const stripe = await getUncachableStripeClient();
    const event = stripe.webhooks.constructEvent(payload, signature, webhookSecret);
    await storage.upsertSetting('stripe_last_webhook_event', {
      id: event.id,
      type: event.type,
      created: event.created,
      livemode: event.livemode,
      processedAt: new Date().toISOString(),
    });
    return event;
  }
}
