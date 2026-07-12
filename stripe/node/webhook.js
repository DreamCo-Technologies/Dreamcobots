/**
 * Dreamcobots Stripe Webhook Handler — Node.js
 *
 * Start:  node webhook.js
 * Forward: stripe listen --forward-to localhost:4242/webhook
 */

require('dotenv').config();
const express = require('express');
const stripe = require('stripe')(process.env.STRIPE_SECRET_KEY);
const { RevenueLedger } = require('./revenue-ledger');
const { recordPaymentEmailNotice } = require('./payment-email-notifier');

const app = express();
const PORT = process.env.PORT || 4242;
const ledger = new RevenueLedger();

async function record(event) {
  const tracked = ledger.recordEvent(event);
  const emailNotice = await recordPaymentEmailNotice(tracked);
  ledger.writeMarkdownReport();
  console.log(`Tracked Stripe event ${tracked.type} for bot=${tracked.botId} amount=${tracked.amountCents} ${tracked.currency}`);
  if (emailNotice) {
    console.log(`Payment email notice ${emailNotice.status} for event=${tracked.id} recipients=${emailNotice.recipientCount}`);
  }
  return tracked;
}

// Use raw body for webhook verification
app.post('/webhook', express.raw({ type: 'application/json' }), async (req, res) => {
  const sig = req.headers['stripe-signature'];
  let event;

  try {
    event = stripe.webhooks.constructEvent(req.body, sig, process.env.STRIPE_WEBHOOK_SECRET);
  } catch (err) {
    console.error(`Webhook signature verification failed: ${err.message}`);
    return res.status(400).send('Webhook Error: signature verification failed');
  }

  switch (event.type) {
    case 'payment_intent.succeeded':
    case 'payment_intent.payment_failed':
    case 'checkout.session.completed':
    case 'customer.subscription.created':
    case 'customer.subscription.deleted':
    case 'invoice.paid':
    case 'invoice.payment_failed':
    case 'payout.paid':
      await record(event);
      break;
    default:
      console.log(`Unhandled event type: ${event.type}`);
  }

  res.json({ received: true });
});

app.get('/revenue/summary', (_req, res) => {
  const summary = ledger.writeSummaries().summary;
  res.json(summary);
});

app.listen(PORT, () => console.log(`Dreamcobots webhook server running on port ${PORT}`));
