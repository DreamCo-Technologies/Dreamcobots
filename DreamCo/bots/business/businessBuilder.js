'use strict';

/**
 * DreamCo Business Builder Bot
 *
 * Generates business blueprints with revenue projections and step-by-step
 * launch plans for five core business models.
 *
 * BOT → ACTION → RESULT → REVENUE → VALIDATION → SCALE
 */

/** Supported business model identifiers. */
const BUSINESS_MODELS = ['saas', 'ecommerce', 'agency', 'consulting', 'marketplace'];

const MODEL_CONFIGS = {
  saas: {
    initial_investment: 5000,
    avg_monthly_revenue: 8000,
    growth_rate: 0.15,
    timeline_weeks: 12,
    steps: [
      'Define target market and ICP',
      'Validate idea with 10 customer interviews',
      'Build MVP (4–6 weeks)',
      'Launch beta with 10–20 free users',
      'Iterate based on feedback',
      'Launch paid tiers and begin marketing',
      'Automate onboarding and scale',
    ],
  },
  ecommerce: {
    initial_investment: 2000,
    avg_monthly_revenue: 5000,
    growth_rate: 0.12,
    timeline_weeks: 4,
    steps: [
      'Research winning products',
      'Set up Shopify/WooCommerce store',
      'Source products or set up print-on-demand',
      'Create product listings with SEO copy',
      'Launch Facebook/Instagram ads',
      'Optimise conversion rate',
      'Scale winning ads and add upsells',
    ],
  },
  agency: {
    initial_investment: 500,
    avg_monthly_revenue: 12000,
    growth_rate: 0.2,
    timeline_weeks: 3,
    steps: [
      'Pick a high-value niche service',
      'Create case studies or portfolio projects',
      'Build outreach system (cold email / LinkedIn)',
      'Onboard first 3 clients at reduced rate',
      'Deliver results and collect testimonials',
      'Raise rates and productise service',
      'Hire contractors and scale delivery',
    ],
  },
  consulting: {
    initial_investment: 200,
    avg_monthly_revenue: 10000,
    growth_rate: 0.18,
    timeline_weeks: 2,
    steps: [
      'Identify expertise and outcome you deliver',
      'Create a one-page offer',
      'Reach out to 50 potential clients per week',
      'Host discovery calls and close at premium rate',
      'Deliver 90-day engagement',
      'Package insights into frameworks / courses',
      'Build advisory retainer model',
    ],
  },
  marketplace: {
    initial_investment: 8000,
    avg_monthly_revenue: 15000,
    growth_rate: 0.25,
    timeline_weeks: 16,
    steps: [
      'Define supply and demand sides of marketplace',
      'Build MVP platform',
      'Seed supply side first (list 50+ providers)',
      'Attract demand side with content marketing',
      'Facilitate first 10 transactions manually',
      'Automate matching and payments',
      'Launch referral and affiliate program',
    ],
  },
};

/**
 * Build a full business blueprint for the given model.
 * @param {string} model - One of BUSINESS_MODELS
 * @returns {{ model: string, steps: string[], timeline: string, initial_investment: number, projected_revenue: number }}
 */
function buildBlueprint(model = 'saas') {
  const config = MODEL_CONFIGS[model] || MODEL_CONFIGS.saas;
  return {
    model,
    steps: config.steps,
    timeline: `${config.timeline_weeks} weeks to first revenue`,
    initial_investment: config.initial_investment,
    projected_revenue: Math.floor(config.avg_monthly_revenue * (1 + Math.random() * 0.4 - 0.2)),
  };
}

/**
 * Project cumulative revenue for a business model over N months.
 * @param {string} model - One of BUSINESS_MODELS
 * @param {number} months - Number of months to project
 * @returns {number} Projected total revenue in USD
 */
function projectRevenue(model = 'saas', months = 12) {
  const config = MODEL_CONFIGS[model] || MODEL_CONFIGS.saas;
  let total = 0;
  let monthly = config.avg_monthly_revenue;
  for (let i = 0; i < months; i++) {
    total += Math.floor(monthly);
    monthly *= 1 + config.growth_rate;
  }
  return total;
}

/**
 * Main bot entry point — generates a blueprint and revenue projection.
 * @param {Object} [options]
 * @param {string} [options.model] - Business model to build (default: random)
 * @param {number} [options.months] - Projection horizon in months (default: 12)
 * @returns {Object} Standardised bot output
 */
function run(options = {}) {
  const model =
    options.model || BUSINESS_MODELS[Math.floor(Math.random() * BUSINESS_MODELS.length)];
  const months = options.months || 12;

  const blueprint = buildBlueprint(model);
  const projectedAnnual = projectRevenue(model, months);
  const revenue = Math.floor(Math.random() * (5000 - 2000 + 1)) + 2000;
  const leadsGenerated = Math.floor(Math.random() * (50 - 20 + 1)) + 20;
  const conversionRate = parseFloat((Math.random() * 0.3 + 0.1).toFixed(2));

  return {
    bot: 'businessBuilder',
    model,
    revenue,
    leads_generated: leadsGenerated,
    conversion_rate: conversionRate,
    blueprint,
    projected_annual_revenue: projectedAnnual,
    action: `Built ${model} blueprint — ${blueprint.steps.length} launch steps, ${blueprint.timeline}`,
    timestamp: new Date().toISOString(),
  };
}

module.exports = { run, buildBlueprint, projectRevenue, BUSINESS_MODELS };
