/**
 * Dreamcobots Stripe Integration — Node.js
 *
 * Install: npm install
 * Configure .env (see ../../.env.example)
 *
 * Usage:
 *   node index.js
 */

require('dotenv').config();
const stripe = require('stripe')(process.env.STRIPE_SECRET_KEY);

function buildMetadata({ botId, offerId, workflowId, source } = {}) {
  return {
    bot_id: botId || 'unassigned',
    offer_id: offerId || 'unassigned',
    workflow_id: workflowId || 'unassigned',
    source: source || 'dreamcobots',
  };
}

/**
 * Create a Stripe Checkout session for a one-time payment.
 */
async function createCheckoutSession({
  amountCents,
  currency = 'usd',
  customerEmail,
  successUrl,
  cancelUrl,
  mode = 'payment',
  botId,
  offerId,
  workflowId,
}) {
  const metadata = buildMetadata({ botId, offerId, workflowId, source: 'checkout_session' });
  const session = await stripe.checkout.sessions.create({
    payment_method_types: ['card'],
    line_items: [
      {
        price_data: {
          currency: currency.toLowerCase(),
          product_data: {
            name: 'Dreamcobots Service',
            metadata,
          },
          unit_amount: amountCents,
        },
        quantity: 1,
      },
    ],
    mode,
    customer_email: customerEmail,
    success_url: successUrl,
    cancel_url: cancelUrl,
    metadata,
    payment_intent_data: mode === 'payment' ? { metadata } : undefined,
    subscription_data: mode === 'subscription' ? { metadata } : undefined,
  });
  return { sessionId: session.id, checkoutUrl: session.url, metadata };
}

/**
 * Create a shareable Stripe Payment Link.
 */
async function createPaymentLink({ amountCents, currency = 'usd', productName, botId, offerId, workflowId }) {
  const metadata = buildMetadata({ botId, offerId, workflowId, source: 'payment_link' });
  const price = await stripe.prices.create({
    unit_amount: amountCents,
    currency: currency.toLowerCase(),
    product_data: { name: productName, metadata },
    metadata,
  });
  const link = await stripe.paymentLinks.create({
    line_items: [{ price: price.id, quantity: 1 }],
    metadata,
  });
  return { id: link.id, url: link.url, metadata };
}

/**
 * Create a Stripe Subscription for a customer.
 */
async function createSubscription({ customerId, priceId, botId, offerId, workflowId }) {
  const metadata = buildMetadata({ botId, offerId, workflowId, source: 'subscription' });
  const subscription = await stripe.subscriptions.create({
    customer: customerId,
    items: [{ price: priceId }],
    metadata,
  });
  return { id: subscription.id, status: subscription.status, metadata };
}

/**
 * Issue a refund for a PaymentIntent.
 */
async function createRefund({ paymentIntentId, amountCents, botId, offerId, workflowId }) {
  const params = {
    payment_intent: paymentIntentId,
    metadata: buildMetadata({ botId, offerId, workflowId, source: 'refund' }),
  };
  if (amountCents) {
    params.amount = amountCents;
  }
  const refund = await stripe.refunds.create(params);
  return { id: refund.id, status: refund.status };
}

module.exports = {
  createCheckoutSession,
  createPaymentLink,
  createSubscription,
  createRefund,
  buildMetadata,
};

if (require.main === module) {
  const mode = process.env.STRIPE_SECRET_KEY ? 'configured' : 'simulation';
  console.log(`Dreamcobots Stripe Node.js client initialised in ${mode} mode.`);
}
