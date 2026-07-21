'use strict';

/**
 * DreamCo Ad Engine Bot
 *
 * Multi-platform ad campaign generation + ROI analysis bot.
 * Generates optimised ad campaigns across Google, Facebook, TikTok,
 * Instagram, and YouTube, then validates return on ad spend.
 *
 * BOT → ACTION → RESULT → REVENUE → VALIDATION → SCALE
 */

/** Supported advertising platforms. */
const AD_PLATFORMS = ['google_ads', 'facebook_ads', 'tiktok_ads', 'instagram_ads', 'youtube_ads'];

const CAMPAIGN_TYPES = ['brand_awareness', 'lead_generation', 'retargeting', 'conversion'];

const PLATFORM_MULTIPLIERS = {
  google_ads: 3.2,
  facebook_ads: 2.8,
  tiktok_ads: 2.1,
  instagram_ads: 2.5,
  youtube_ads: 2.9,
};

const REVENUE_MIN = 1500;
const REVENUE_MAX = 3500;
const LEADS_MIN = 40;
const LEADS_MAX = 80;

/**
 * Generate an ad campaign for a given platform and budget.
 * @param {string} platform - One of AD_PLATFORMS
 * @param {number} budget - Total ad spend in USD
 * @returns {Object} Campaign configuration object
 */
function generateCampaign(platform = 'google_ads', budget = 500) {
  const type = CAMPAIGN_TYPES[Math.floor(Math.random() * CAMPAIGN_TYPES.length)];
  const multiplier = PLATFORM_MULTIPLIERS[platform] || 2.0;
  const estimatedReach = Math.floor(budget * multiplier * (Math.random() * 0.5 + 0.75));
  const estimatedClicks = Math.floor(estimatedReach * (Math.random() * 0.04 + 0.01));
  const estimatedConversions = Math.floor(estimatedClicks * (Math.random() * 0.08 + 0.02));

  return {
    campaign_id: `CAM-${Date.now()}-${Math.floor(Math.random() * 1000)}`,
    platform,
    type,
    budget,
    estimated_reach: estimatedReach,
    estimated_clicks: estimatedClicks,
    estimated_conversions: estimatedConversions,
    cost_per_click: parseFloat((budget / Math.max(estimatedClicks, 1)).toFixed(2)),
    status: 'draft',
    created_at: new Date().toISOString(),
  };
}

/**
 * Calculate return on investment for an ad campaign.
 * @param {number} spend - Total amount spent on ads in USD
 * @param {number} revenue - Revenue generated from the campaign in USD
 * @returns {number} ROI as a percentage
 */
function calculateROI(spend, revenue) {
  if (spend <= 0) return 0;
  return parseFloat((((revenue - spend) / spend) * 100).toFixed(2));
}

/**
 * Main bot entry point — runs a single ad engine cycle.
 * @param {Object} [options]
 * @param {string} [options.platform] - Target platform (default: random)
 * @param {number} [options.budget] - Ad budget per campaign (default: 500)
 * @returns {Object} Standardised bot output
 */
function run(options = {}) {
  const platform =
    options.platform || AD_PLATFORMS[Math.floor(Math.random() * AD_PLATFORMS.length)];
  const budget = options.budget || Math.floor(Math.random() * 1000) + 200;

  const campaign = generateCampaign(platform, budget);
  const revenue = Math.floor(Math.random() * (REVENUE_MAX - REVENUE_MIN + 1)) + REVENUE_MIN;
  const roi = calculateROI(budget, revenue);
  const leadsGenerated = Math.floor(Math.random() * (LEADS_MAX - LEADS_MIN + 1)) + LEADS_MIN;
  const conversions = campaign.estimated_conversions;
  const conversionRate =
    leadsGenerated > 0 ? parseFloat((conversions / leadsGenerated).toFixed(2)) : 0;

  return {
    bot: 'adEngine',
    platform,
    revenue,
    leads_generated: leadsGenerated,
    conversion_rate: conversionRate,
    roi_percent: roi,
    campaign,
    action: `Launched ${campaign.type} campaign on ${platform} — budget $${budget}, est. reach ${campaign.estimated_reach}`,
    timestamp: new Date().toISOString(),
  };
}

module.exports = { run, generateCampaign, calculateROI, AD_PLATFORMS };
