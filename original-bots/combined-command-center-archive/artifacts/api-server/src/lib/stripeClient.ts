import type Stripe from "stripe";

const STRIPE_KEY = process.env.STRIPE_SECRET_KEY;

export async function getStripeClient(): Promise<Stripe | null> {
  if (!STRIPE_KEY || STRIPE_KEY.includes("placeholder")) return null;
  const { default: StripeCtor } = await import("stripe");
  return new StripeCtor(STRIPE_KEY);
}
