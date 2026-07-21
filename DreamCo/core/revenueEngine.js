'use strict';

/**
 * DreamCo — Revenue Engine
 *
 * Central monetization layer.  Tracks revenue from every source
 * (bots, affiliate links, subscriptions, etc.) and exposes aggregated
 * reporting so the system knows where money is actually flowing.
 */

const db = require('./database');

const COLLECTION = 'revenue';

/**
 * Record a revenue event.
 *
 * @param {string} source - Identifier for the revenue source (e.g. 'realEstateBot')
 * @param {number} amount  - USD amount earned
 * @param {Object} [meta]  - Optional extra metadata (e.g. { deal_id, lead_id })
 * @returns {Object} The persisted revenue record
 */
function trackRevenue(source, amount, meta = {}) {
  if (!source) {
    throw new Error('"source" is required');
  }
  if (typeof amount !== 'number' || amount < 0) {
    throw new Error('"amount" must be a non-negative number');
  }

  const record = db.save(COLLECTION, { source, amount, ...meta });
  console.log(`💰 [RevenueEngine] ${source} → $${amount.toFixed(2)}`);
  return record;
}

/**
 * Compute total revenue across all sources (or filtered by source).
 *
 * @param {string} [source] - Optional filter
 * @returns {number} Total USD
 */
function totalRevenue(source) {
  const docs = source ? db.find(COLLECTION, (d) => d.source === source) : db.load(COLLECTION);

  return docs.reduce((sum, d) => sum + (d.amount || 0), 0);
}

/**
 * Return a breakdown of revenue by source.
 * @returns {Object} { [source]: totalAmount }
 */
function revenueBySource() {
  const docs = db.load(COLLECTION);
  return docs.reduce((acc, d) => {
    acc[d.source] = (acc[d.source] || 0) + (d.amount || 0);
    return acc;
  }, {});
}

module.exports = { trackRevenue, totalRevenue, revenueBySource };
