'use strict';

/**
 * DreamCo — Dynamic Pricing Intelligence Engine
 *
 * Sets base prices, computes demand-adjusted dynamic prices,
 * applies tier multipliers, runs competitor analysis, and
 * suggests optimal pricing based on historical data.
 */

/** In-memory price store: productId → price data. */
const priceStore = new Map();

/** Tier multipliers for FREE/PRO/ENTERPRISE. */
const TIER_MULTIPLIERS = {
  FREE: 0,
  PRO: 1.0,
  ENTERPRISE: 2.5,
};

/** Simulated competitor price offsets by product category. */
const COMPETITOR_OFFSETS = {
  saas: 0.95,
  bots: 0.9,
  leads: 1.1,
  consulting: 1.05,
  data: 0.85,
};

/**
 * Set or update the base price for a product.
 * @param {string} productId - Product identifier.
 * @param {number} price - Base price in USD.
 * @returns {Object} The stored price record.
 */
function setBasePrice(productId, price) {
  if (!productId) {
    throw new Error('productId is required.');
  }
  if (typeof price !== 'number' || price < 0) {
    throw new Error('price must be a non-negative number.');
  }
  const existing = priceStore.get(productId) || { history: [] };
  if (existing.basePrice !== undefined) {
    existing.history.push({ price: existing.basePrice, recordedAt: new Date().toISOString() });
  }
  existing.productId = productId;
  existing.basePrice = price;
  existing.updatedAt = new Date().toISOString();
  priceStore.set(productId, existing);
  return existing;
}

/**
 * Calculate a dynamic price based on demand, competition, and time-of-day.
 * @param {string} productId - Product identifier.
 * @param {Object} [context] - Pricing context.
 * @param {number} [context.demandScore] - Demand score 0–100 (default 50).
 * @param {number} [context.competitorPrice] - Known competitor price.
 * @param {boolean} [context.isPeakHour] - Whether it's peak demand hours.
 * @returns {{ productId: string, dynamicPrice: number, factors: Object }}
 */
function getDynamicPrice(productId, context) {
  const record = priceStore.get(productId);
  if (!record) {
    throw new Error(`No base price found for product '${productId}'.`);
  }
  const ctx = context || {};
  const demandScore = typeof ctx.demandScore === 'number' ? ctx.demandScore : 50;
  const isPeakHour = ctx.isPeakHour || false;

  let multiplier = 1.0;

  // Demand adjustment: high demand → premium price
  if (demandScore > 80) {
    multiplier += 0.2;
  } else if (demandScore > 60) {
    multiplier += 0.1;
  } else if (demandScore < 20) {
    multiplier -= 0.15;
  }

  // Peak hour surcharge
  if (isPeakHour) {
    multiplier += 0.05;
  }

  // Competitor alignment
  if (typeof ctx.competitorPrice === 'number' && ctx.competitorPrice > 0) {
    const competitorRatio = ctx.competitorPrice / record.basePrice;
    // Stay within 10% of competitor
    if (competitorRatio < 0.9) {
      multiplier = Math.min(multiplier, 0.95);
    } else if (competitorRatio > 1.1) {
      multiplier = Math.min(multiplier, competitorRatio * 0.98);
    }
  }

  const dynamicPrice = Number((record.basePrice * multiplier).toFixed(2));

  return {
    productId,
    basePrice: record.basePrice,
    dynamicPrice,
    factors: { demandScore, isPeakHour, multiplier: Number(multiplier.toFixed(4)) },
  };
}

/**
 * Apply tier-based pricing to a given price.
 * @param {number} price - Base price.
 * @param {'FREE'|'PRO'|'ENTERPRISE'} tier - Subscription tier.
 * @returns {{ tier: string, price: number, tieredPrice: number }}
 */
function applyTierPricing(price, tier) {
  const normalizedTier = (tier || 'FREE').toUpperCase();
  const multiplier = TIER_MULTIPLIERS[normalizedTier];
  if (multiplier === undefined) {
    throw new Error(`Unknown tier '${tier}'. Must be FREE, PRO, or ENTERPRISE.`);
  }
  const tieredPrice = Number((price * multiplier).toFixed(2));
  return { tier: normalizedTier, price, tieredPrice };
}

/**
 * Simulate a competitor price analysis for a product.
 * @param {string} productId - Product identifier.
 * @returns {{ productId: string, competitors: Object[], avgCompetitorPrice: number, recommendation: string }}
 */
function runCompetitorAnalysis(productId) {
  const record = priceStore.get(productId);
  if (!record) {
    throw new Error(`No base price found for product '${productId}'.`);
  }
  const base = record.basePrice;
  const competitors = [
    { name: 'CompetitorA', price: Number((base * 0.9).toFixed(2)) },
    { name: 'CompetitorB', price: Number((base * 1.05).toFixed(2)) },
    { name: 'CompetitorC', price: Number((base * 0.95).toFixed(2)) },
    { name: 'CompetitorD', price: Number((base * 1.15).toFixed(2)) },
  ];
  const avgCompetitorPrice = Number(
    (competitors.reduce((s, c) => s + c.price, 0) / competitors.length).toFixed(2)
  );
  const recommendation =
    base > avgCompetitorPrice * 1.1
      ? 'Consider lowering price to be more competitive.'
      : base < avgCompetitorPrice * 0.85
        ? 'You may be underpricing — consider increasing.'
        : 'Price is competitive.';

  return { productId, competitors, avgCompetitorPrice, recommendation };
}

/**
 * Suggest the optimal price for a product based on its history.
 * @param {string} productId - Product identifier.
 * @returns {{ productId: string, currentPrice: number, suggestedPrice: number, reason: string }}
 */
function optimizePrice(productId) {
  const record = priceStore.get(productId);
  if (!record) {
    throw new Error(`No base price found for product '${productId}'.`);
  }
  const history = record.history || [];
  let suggestedPrice = record.basePrice;
  let reason = 'No history available; keeping current price.';

  if (history.length > 0) {
    const avg = history.reduce((s, h) => s + h.price, 0) / history.length;
    // Nudge toward historical average with a slight premium
    suggestedPrice = Number((((record.basePrice + avg) / 2) * 1.05).toFixed(2));
    reason = `Optimized based on ${history.length} historical data point(s).`;
  }

  return { productId, currentPrice: record.basePrice, suggestedPrice, reason };
}

/**
 * Get pricing history for a product.
 * @param {string} productId - Product identifier.
 * @returns {{ productId: string, currentPrice: number, history: Object[] }}
 */
function getPricingHistory(productId) {
  const record = priceStore.get(productId);
  if (!record) {
    throw new Error(`No base price found for product '${productId}'.`);
  }
  return {
    productId,
    currentPrice: record.basePrice,
    history: record.history || [],
  };
}

module.exports = {
  TIER_MULTIPLIERS,
  COMPETITOR_OFFSETS,
  setBasePrice,
  getDynamicPrice,
  applyTierPricing,
  runCompetitorAnalysis,
  optimizePrice,
  getPricingHistory,
};
