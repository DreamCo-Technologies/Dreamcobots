import Stripe from 'stripe';

export async function getUncachableStripeClient() {
  const secretKey = await getStripeSecretKey();
  return new Stripe(secretKey);
}

export async function getStripePublishableKey() {
  const publishableKey = process.env.STRIPE_PUBLISHABLE_KEY || process.env.STRIPE_LIVE_PK;
  if (!publishableKey) throw new Error('Stripe publishable key is not configured.');
  return publishableKey;
}

export async function getStripeSecretKey() {
  const secretKey = process.env.STRIPE_SECRET_KEY || process.env.STRIPE_LIVE_SECRET_KEY;
  if (!secretKey) throw new Error('Stripe secret key is not configured.');
  return secretKey;
}
