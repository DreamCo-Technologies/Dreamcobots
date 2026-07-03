import Stripe from "stripe";
import { StripeSync } from "stripe-replit-sync";
// ---------------------------------------------------------------------------
// Stripe client helpers
// ---------------------------------------------------------------------------
/** Returns a Stripe instance (not cached so keys are always fresh). */
export async function getUncachableStripeClient() {
    const secretKey = process.env.STRIPE_SECRET_KEY;
    if (!secretKey) {
        throw new Error("STRIPE_SECRET_KEY environment variable is not set");
    }
    return new Stripe(secretKey, { apiVersion: "2026-02-25.clover" });
}
/** Returns the Stripe publishable key from the environment. */
export async function getStripePublishableKey() {
    const key = process.env.STRIPE_PUBLISHABLE_KEY ?? process.env.VITE_STRIPE_PUBLISHABLE_KEY;
    if (!key) {
        throw new Error("STRIPE_PUBLISHABLE_KEY environment variable is not set");
    }
    return key;
}
/** Returns a StripeSync instance for schema migration and syncing. */
export async function getStripeSync() {
    const secretKey = process.env.STRIPE_SECRET_KEY;
    const databaseUrl = process.env.DATABASE_URL;
    if (!secretKey || !databaseUrl) {
        throw new Error("STRIPE_SECRET_KEY and DATABASE_URL must be set for Stripe sync");
    }
    return new StripeSync({ stripeSecretKey: secretKey, poolConfig: { connectionString: databaseUrl } });
}
