import { getUncachableStripeClient } from './stripeClient';

const EMPIRE_TIERS = [
  {
    name: "DreamCo Free",
    description: "Get started with guided AI bots across all 16 divisions. Perfect for exploring the Empire OS platform.",
    metadata: {
      tier: "free",
      botLimit: "5",
      autonomyLevel: "guided",
      divisions: "all",
    },
    prices: [
      { unit_amount: 0, interval: "month" as const },
    ],
  },
  {
    name: "DreamCo Pro",
    description: "Unlock semi-autonomous operations with 50 bots, advanced analytics, and priority API access across all divisions.",
    metadata: {
      tier: "pro",
      botLimit: "50",
      autonomyLevel: "semi-autonomous",
      divisions: "all",
      popular: "true",
    },
    prices: [
      { unit_amount: 29900, interval: "month" as const },
      { unit_amount: 287000, interval: "year" as const },
    ],
  },
  {
    name: "DreamCo Enterprise",
    description: "Full autonomy mode with 150 bots, all 269 API integrations, dedicated support, and custom bot training.",
    metadata: {
      tier: "enterprise",
      botLimit: "150",
      autonomyLevel: "full-autonomy",
      divisions: "all",
      apiAccess: "all",
    },
    prices: [
      { unit_amount: 99900, interval: "month" as const },
      { unit_amount: 959000, interval: "year" as const },
    ],
  },
  {
    name: "DreamCo Elite",
    description: "Unlimited bots, white-glove onboarding, custom division creation, dedicated infrastructure, and 24/7 priority support.",
    metadata: {
      tier: "elite",
      botLimit: "unlimited",
      autonomyLevel: "full-autonomy",
      divisions: "custom",
      dedicatedInfra: "true",
      whiteGlove: "true",
    },
    prices: [
      { unit_amount: 249900, interval: "month" as const },
      { unit_amount: 2399000, interval: "year" as const },
    ],
  },
];

export async function seedStripeProducts() {
  console.log("Seeding DreamCo Empire tier products in Stripe...\n");

  const stripe = await getUncachableStripeClient();

  for (const tier of EMPIRE_TIERS) {
    const existing = await stripe.products.search({ query: `name:'${tier.name}'` });
    if (existing.data.length > 0) {
      console.log(`  [skip] ${tier.name} already exists (${existing.data[0].id})`);
      continue;
    }

    const product = await stripe.products.create({
      name: tier.name,
      description: tier.description,
      metadata: tier.metadata as unknown as Record<string, string>,
    });
    console.log(`  [created] ${tier.name} -> ${product.id}`);

    for (const price of tier.prices) {
      if (price.unit_amount === 0) {
        const p = await stripe.prices.create({
          product: product.id,
          unit_amount: 0,
          currency: "usd",
          recurring: { interval: price.interval },
        });
        console.log(`    Price: FREE/${price.interval} -> ${p.id}`);
      } else {
        const p = await stripe.prices.create({
          product: product.id,
          unit_amount: price.unit_amount,
          currency: "usd",
          recurring: { interval: price.interval },
        });
        console.log(`    Price: $${(price.unit_amount / 100).toFixed(2)}/${price.interval} -> ${p.id}`);
      }
    }
  }

  console.log("\nDone! Products are available through the live billing API.");
}

if (process.argv[1]?.endsWith('seed-stripe-products.ts')) {
  seedStripeProducts().catch(console.error);
}
