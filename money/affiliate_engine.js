'use strict';

/**
 * DreamCo — Affiliate Marketing Engine
 *
 * Manages multiple affiliate programs, generates tracked links,
 * records click/conversion events, and computes earnings.
 */

const crypto = require('crypto');

/** Pre-loaded affiliate programs. */
const DEFAULT_PROGRAMS = [
  {
    name: 'amazon',
    displayName: 'Amazon Associates',
    baseUrl: 'https://www.amazon.com/dp/',
    commissionRate: 0.04,
    cookieDays: 24,
    category: 'general',
  },
  {
    name: 'clickbank',
    displayName: 'ClickBank',
    baseUrl: 'https://hop.clickbank.net/',
    commissionRate: 0.5,
    cookieDays: 60,
    category: 'digital_products',
  },
  {
    name: 'shareasale',
    displayName: 'ShareASale',
    baseUrl: 'https://www.shareasale.com/r.cfm',
    commissionRate: 0.15,
    cookieDays: 30,
    category: 'retail',
  },
  {
    name: 'impact',
    displayName: 'Impact',
    baseUrl: 'https://impact.com/track/',
    commissionRate: 0.2,
    cookieDays: 30,
    category: 'saas',
  },
  {
    name: 'cj',
    displayName: 'Commission Junction (CJ)',
    baseUrl: 'https://www.anrdoezrs.net/click-',
    commissionRate: 0.08,
    cookieDays: 45,
    category: 'retail',
  },
];

/** In-memory registry of registered programs. */
const programs = new Map();

/** In-memory link store: linkId → link metadata. */
const links = new Map();

/** In-memory event log. */
const events = [];

// Pre-load default programs
DEFAULT_PROGRAMS.forEach((p) =>
  programs.set(p.name, { ...p, earnings: 0, clicks: 0, conversions: 0 })
);

/**
 * Register a new affiliate program.
 * @param {string} name - Unique program identifier.
 * @param {Object} config - Program configuration.
 * @param {string} config.displayName - Human-readable name.
 * @param {string} config.baseUrl - Base URL for link generation.
 * @param {number} config.commissionRate - Commission rate (0–1).
 * @param {number} [config.cookieDays=30] - Cookie lifetime in days.
 * @param {string} [config.category='general'] - Program category.
 * @returns {Object} The registered program.
 */
function registerProgram(name, config) {
  if (!name || typeof name !== 'string') {
    throw new Error('Program name must be a non-empty string.');
  }
  const program = {
    name,
    displayName: config.displayName || name,
    baseUrl: config.baseUrl || '',
    commissionRate: Number(config.commissionRate) || 0,
    cookieDays: Number(config.cookieDays) || 30,
    category: config.category || 'general',
    earnings: 0,
    clicks: 0,
    conversions: 0,
  };
  programs.set(name, program);
  return program;
}

/**
 * Generate a tracked affiliate link.
 * @param {string} programName - Name of the registered program.
 * @param {string} productId - Product or offer identifier.
 * @param {string} userId - User or sub-ID for attribution.
 * @returns {{ linkId: string, url: string, program: string }}
 */
function generateLink(programName, productId, userId) {
  const program = programs.get(programName);
  if (!program) {
    throw new Error(`Program '${programName}' is not registered.`);
  }
  const linkId = crypto.randomBytes(8).toString('hex');
  const url = `${program.baseUrl}${productId}?tag=${userId}&ref=${linkId}`;
  const link = {
    linkId,
    url,
    program: programName,
    productId,
    userId,
    clicks: 0,
    conversions: 0,
    revenue: 0,
    createdAt: new Date().toISOString(),
  };
  links.set(linkId, link);
  return { linkId, url, program: programName };
}

/**
 * Track a click on an affiliate link.
 * @param {string} linkId - The link identifier.
 * @returns {{ linkId: string, totalClicks: number }}
 */
function trackClick(linkId) {
  const link = links.get(linkId);
  if (!link) {
    throw new Error(`Link '${linkId}' not found.`);
  }
  link.clicks += 1;
  const program = programs.get(link.program);
  if (program) {
    program.clicks += 1;
  }
  events.push({ type: 'click', linkId, program: link.program, at: new Date().toISOString() });
  return { linkId, totalClicks: link.clicks };
}

/**
 * Track a conversion and compute commission.
 * @param {string} linkId - The link identifier.
 * @param {number} amount - Sale amount in USD.
 * @returns {{ linkId: string, commission: number, totalRevenue: number }}
 */
function trackConversion(linkId, amount) {
  const link = links.get(linkId);
  if (!link) {
    throw new Error(`Link '${linkId}' not found.`);
  }
  const program = programs.get(link.program);
  if (!program) {
    throw new Error(`Program '${link.program}' not found.`);
  }
  const commission = Number((amount * program.commissionRate).toFixed(2));
  link.conversions += 1;
  link.revenue += commission;
  program.conversions += 1;
  program.earnings += commission;
  events.push({
    type: 'conversion',
    linkId,
    program: link.program,
    amount,
    commission,
    at: new Date().toISOString(),
  });
  return { linkId, commission, totalRevenue: link.revenue };
}

/**
 * Get total earnings for a specific program.
 * @param {string} programName - Name of the program.
 * @returns {{ program: string, earnings: number, clicks: number, conversions: number }}
 */
function getEarnings(programName) {
  const program = programs.get(programName);
  if (!program) {
    throw new Error(`Program '${programName}' is not registered.`);
  }
  return {
    program: programName,
    earnings: program.earnings,
    clicks: program.clicks,
    conversions: program.conversions,
  };
}

/**
 * Get earnings across all registered programs.
 * @returns {{ total: number, byProgram: Object[] }}
 */
function getAllEarnings() {
  let total = 0;
  const byProgram = [];
  programs.forEach((program, name) => {
    total += program.earnings;
    byProgram.push({
      program: name,
      earnings: program.earnings,
      clicks: program.clicks,
      conversions: program.conversions,
    });
  });
  return { total: Number(total.toFixed(2)), byProgram };
}

/**
 * Get the top N programs by earnings.
 * @param {number} n - Number of programs to return.
 * @returns {Object[]} Array of program stats, sorted by earnings descending.
 */
function getTopPrograms(n) {
  const all = [];
  programs.forEach((program, name) => {
    all.push({ program: name, earnings: program.earnings, clicks: program.clicks });
  });
  return all.sort((a, b) => b.earnings - a.earnings).slice(0, n);
}

module.exports = {
  DEFAULT_PROGRAMS,
  registerProgram,
  generateLink,
  trackClick,
  trackConversion,
  getEarnings,
  getAllEarnings,
  getTopPrograms,
};
