'use strict';

/**
 * DreamCo — Lead Management & Selling System
 *
 * Captures leads from multiple sources, scores them with an AI-like
 * heuristic, and tracks their sale to buyers.
 */

const crypto = require('crypto');

/** In-memory lead store: leadId → lead. */
const leads = new Map();

/** Revenue ledger entries. */
const transactions = [];

/** Category value weights for scoring. */
const CATEGORY_WEIGHTS = {
  real_estate: 30,
  crypto: 25,
  business: 20,
  insurance: 18,
  legal: 15,
  marketing: 12,
  general: 8,
};

/**
 * Capture a new lead.
 * @param {Object} data - Lead data.
 * @param {string} data.name - Lead full name.
 * @param {string} data.email - Lead email address.
 * @param {string} [data.phone] - Lead phone number.
 * @param {string} [data.source] - Traffic source (e.g. 'linkedin').
 * @param {string} [data.category] - Lead category (e.g. 'real_estate').
 * @param {number} [data.score] - Override score (0–100).
 * @returns {Object} The captured lead.
 */
function captureLead(data) {
  if (!data || !data.email) {
    throw new Error('Lead must have an email address.');
  }
  const leadId = crypto.randomBytes(8).toString('hex');
  const lead = {
    leadId,
    name: data.name || 'Unknown',
    email: data.email,
    phone: data.phone || null,
    source: data.source || 'organic',
    category: data.category || 'general',
    score: typeof data.score === 'number' ? data.score : 0,
    status: 'new',
    soldAt: null,
    soldPrice: null,
    buyerName: null,
    createdAt: new Date().toISOString(),
  };
  leads.set(leadId, lead);
  return lead;
}

/**
 * Score a lead based on data completeness and category value.
 * @param {string} leadId - The lead identifier.
 * @returns {{ leadId: string, score: number }}
 */
function scoreLead(leadId) {
  const lead = leads.get(leadId);
  if (!lead) {
    throw new Error(`Lead '${leadId}' not found.`);
  }

  let score = 0;

  // Data completeness (up to 50 points)
  if (lead.name && lead.name !== 'Unknown') {
    score += 10;
  }
  if (lead.email) {
    score += 15;
  }
  if (lead.phone) {
    score += 15;
  }
  if (lead.source && lead.source !== 'organic') {
    score += 10;
  }

  // Category value (up to 30 points)
  const categoryBonus = CATEGORY_WEIGHTS[lead.category] || CATEGORY_WEIGHTS.general;
  score += categoryBonus;

  // Recency bonus (up to 20 points)
  const ageMs = Date.now() - new Date(lead.createdAt).getTime();
  const ageHours = ageMs / (1000 * 60 * 60);
  if (ageHours < 1) {
    score += 20;
  } else if (ageHours < 24) {
    score += 10;
  } else if (ageHours < 72) {
    score += 5;
  }

  score = Math.min(100, score);
  lead.score = score;
  return { leadId, score };
}

/**
 * Mark a lead as sold and record the transaction.
 * @param {string} leadId - The lead identifier.
 * @param {string} buyerName - Name of the buyer.
 * @param {number} price - Sale price in USD.
 * @returns {Object} Updated lead.
 */
function sellLead(leadId, buyerName, price) {
  const lead = leads.get(leadId);
  if (!lead) {
    throw new Error(`Lead '${leadId}' not found.`);
  }
  if (lead.status === 'sold') {
    throw new Error(`Lead '${leadId}' has already been sold.`);
  }
  lead.status = 'sold';
  lead.soldAt = new Date().toISOString();
  lead.soldPrice = Number(price);
  lead.buyerName = buyerName;
  transactions.push({ leadId, buyerName, price: Number(price), at: lead.soldAt });
  return lead;
}

/**
 * Get leads with optional filtering.
 * @param {{ status?: string, category?: string, minScore?: number }} [filter] - Filter criteria.
 * @returns {Object[]} Array of matching leads.
 */
function getLeads(filter) {
  const all = Array.from(leads.values());
  if (!filter) {
    return all;
  }
  return all.filter((lead) => {
    if (filter.status && lead.status !== filter.status) {
      return false;
    }
    if (filter.category && lead.category !== filter.category) {
      return false;
    }
    if (typeof filter.minScore === 'number' && lead.score < filter.minScore) {
      return false;
    }
    return true;
  });
}

/**
 * Get total lead revenue.
 * @returns {{ total: number, transactionCount: number }}
 */
function getRevenue() {
  const total = transactions.reduce((sum, t) => sum + t.price, 0);
  return { total: Number(total.toFixed(2)), transactionCount: transactions.length };
}

/**
 * Export leads in JSON or CSV format.
 * @param {'json'|'csv'} format - Export format.
 * @returns {string} Serialized lead data.
 */
function exportLeads(format) {
  const all = Array.from(leads.values());
  if (format === 'csv') {
    const headers = 'leadId,name,email,phone,source,category,score,status,soldPrice,createdAt';
    const rows = all.map((l) =>
      [
        l.leadId,
        l.name,
        l.email,
        l.phone || '',
        l.source,
        l.category,
        l.score,
        l.status,
        l.soldPrice || '',
        l.createdAt,
      ].join(',')
    );
    return [headers, ...rows].join('\n');
  }
  return JSON.stringify(all, null, 2);
}

module.exports = {
  captureLead,
  scoreLead,
  sellLead,
  getLeads,
  getRevenue,
  exportLeads,
};
