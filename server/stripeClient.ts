import Stripe from 'stripe';

async function getCredentials() {
  const secretKey = process.env.STRIPE_SECRET_KEY || process.env.STRIPE_LIVE_SECRET_KEY;
  const publishableKey = process.env.STRIPE_PUBLISHABLE_KEY || process.env.STRIPE_LIVE_PK;

  if (!secretKey || !publishableKey) {
    throw new Error('Stripe not configured. Set STRIPE_SECRET_KEY and STRIPE_PUBLISHABLE_KEY environment secrets.');
  }

  return { secretKey, publishableKey };
}

export async function getUncachableStripeClient() {
  const { secretKey } = await getCredentials();
  return new Stripe(secretKey);
}

export async function getStripePublishableKey() {
  const { publishableKey } = await getCredentials();
  return publishableKey;
}

export async function getStripeSecretKey() {
  const { secretKey } = await getCredentials();
  return secretKey;
}
