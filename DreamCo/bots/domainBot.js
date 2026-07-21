'use strict';

/**
 * DreamCo domainBot — manage, sell, and flip domains for DreamCo apps and websites.
 *
 * Functions
 * ---------
 * search(query, options)        Search domains for a keyword and return availability.
 * valuate(domainName)           Estimate the market value of a domain.
 * addToPortfolio(entry)         Record a newly registered domain in the in-memory portfolio.
 * listPortfolio(userId, opts)   List domains owned by a user (with optional status filter).
 * markForSale(domainId, ask)    Set a domain's asking price and mark it as LISTED.
 * closeSale(domainId, sold)     Record the sale price and mark the domain as SOLD.
 * flip(options)                 Record a complete buy→sell flip in one step.
 * summary(userId)               Return aggregate portfolio statistics for a user.
 * run(options)                  Main entry point (returns top flip opportunities).
 */

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const TLD_MULTIPLIERS = {
  '.com': 1.8,
  '.io': 1.4,
  '.ai': 2.0,
  '.co': 1.2,
  '.app': 1.1,
  '.net': 0.9,
  '.org': 0.8,
};

const STATUS = {
  OWNED: 'owned',
  LISTED: 'listed',
  SOLD: 'sold',
  FLIPPED: 'flipped',
};

// ---------------------------------------------------------------------------
// In-memory portfolio store  (replace with Firestore/DB in production)
// ---------------------------------------------------------------------------

const _portfolio = {}; // domainId → entry
let _nextId = 1;

function _newId() {
  return `dom-${String(_nextId++).padStart(4, '0')}`;
}

// ---------------------------------------------------------------------------
// Valuation heuristic
// ---------------------------------------------------------------------------

function _tldMultiplier(name) {
  const ext = name.includes('.') ? '.' + name.split('.').slice(1).join('.') : '.com';
  return TLD_MULTIPLIERS[ext] ?? 0.75;
}

function _lengthFactor(name) {
  const label = name.split('.')[0].length;
  if (label <= 3) return 4.0;
  if (label <= 5) return 2.5;
  if (label <= 8) return 1.5;
  if (label <= 12) return 1.0;
  return 0.7;
}

/**
 * Estimate the market value of *domainName*.
 * @param {string} domainName
 * @param {number} [registrationCost=12.99]
 * @returns {number} estimated value in USD
 */
function valuate(domainName, registrationCost = 12.99) {
  const base = Math.max(registrationCost * 3, 15);
  const value = base * _tldMultiplier(domainName) * _lengthFactor(domainName);
  return Math.round(value * 100) / 100;
}

// ---------------------------------------------------------------------------
// Search
// ---------------------------------------------------------------------------

const _TLD_LIST = ['.com', '.io', '.ai', '.co', '.app', '.net', '.org'];

/**
 * Search for domains matching *query* and return availability info.
 * Simulates registrar API results deterministically.
 *
 * @param {string} query    Keyword to search (e.g. "dreamco")
 * @param {{ tlds?: string[], limit?: number }} [options]
 * @returns {{ bot: string, query: string, results: object[], timestamp: string }}
 */
function search(query, options = {}) {
  const { tlds = _TLD_LIST.slice(0, 5), limit = 5 } = options;
  const base = query.toLowerCase().replace(/[^a-z0-9-]/g, '');
  const results = tlds.slice(0, limit).map((tld) => {
    const name = `${base}${tld}`;
    // Deterministic availability: hash-based
    const hash = name.split('').reduce((acc, c) => acc + c.charCodeAt(0), 0);
    const available = hash % 3 !== 0;
    const price = available ? (tld === '.com' ? 12.99 : tld === '.io' ? 39.99 : 14.99) : 0;
    return {
      name,
      available,
      price_usd: price,
      estimated_value_usd: valuate(name, price),
      premium: !available && hash % 7 === 0,
    };
  });

  return {
    bot: 'domainBot',
    query,
    results,
    timestamp: new Date().toISOString(),
  };
}

// ---------------------------------------------------------------------------
// Portfolio CRUD
// ---------------------------------------------------------------------------

/**
 * Record a newly registered domain in the portfolio.
 *
 * @param {{ name: string, userId: string, registrar?: string, registrationCost?: number, expiryDate?: string, notes?: string }} entry
 * @returns {object} domain record
 */
function addToPortfolio(entry) {
  if (!entry || !entry.name || !entry.userId) {
    throw new Error("'name' and 'userId' are required");
  }
  const domainId = _newId();
  const cost = typeof entry.registrationCost === 'number' ? entry.registrationCost : 12.99;
  const record = {
    domainId,
    name: entry.name.trim().toLowerCase(),
    userId: entry.userId,
    registrar: entry.registrar || 'Namecheap',
    registrationCost: cost,
    askPrice: null,
    status: STATUS.OWNED,
    registeredAt: new Date().toISOString(),
    expiryDate: entry.expiryDate || null,
    estimatedValue: valuate(entry.name, cost),
    soldPrice: null,
    profit: null,
    notes: entry.notes || '',
  };
  _portfolio[domainId] = record;
  return record;
}

/**
 * List domains in the portfolio for *userId*.
 *
 * @param {string} userId
 * @param {{ status?: string }} [opts]
 * @returns {object[]}
 */
function listPortfolio(userId, opts = {}) {
  const { status } = opts;
  return Object.values(_portfolio)
    .filter((d) => d.userId === userId && (!status || d.status === status))
    .sort((a, b) => new Date(b.registeredAt) - new Date(a.registeredAt));
}

// ---------------------------------------------------------------------------
// Sell workflow
// ---------------------------------------------------------------------------

/**
 * Mark a domain as listed for sale with an asking price.
 *
 * @param {string} domainId
 * @param {number} askPrice  Asking price in USD (must be > 0)
 * @returns {object} updated domain record
 */
function markForSale(domainId, askPrice) {
  const dom = _portfolio[domainId];
  if (!dom) throw new Error(`Domain '${domainId}' not found`);
  if (dom.status !== STATUS.OWNED) {
    throw new Error(`Domain must be OWNED to list for sale (current: ${dom.status})`);
  }
  if (!askPrice || askPrice <= 0) throw new Error('Ask price must be greater than zero');
  dom.status = STATUS.LISTED;
  dom.askPrice = askPrice;
  return dom;
}

/**
 * Close a domain sale — record the sold price and mark as SOLD.
 *
 * @param {string} domainId
 * @param {number} soldPrice  Actual sale amount in USD (must be > 0)
 * @returns {object} updated domain record
 */
function closeSale(domainId, soldPrice) {
  const dom = _portfolio[domainId];
  if (!dom) throw new Error(`Domain '${domainId}' not found`);
  if (dom.status !== STATUS.LISTED) {
    throw new Error(`Domain must be LISTED to close a sale (current: ${dom.status})`);
  }
  if (!soldPrice || soldPrice <= 0) throw new Error('Sold price must be greater than zero');
  dom.status = STATUS.SOLD;
  dom.soldPrice = soldPrice;
  dom.profit = Math.round((soldPrice - dom.registrationCost) * 100) / 100;
  return dom;
}

// ---------------------------------------------------------------------------
// Flip (buy + sell in one step)
// ---------------------------------------------------------------------------

/**
 * Record a complete domain flip (acquire and sell in one transaction).
 *
 * @param {{ name: string, userId: string, buyPrice: number, sellPrice: number, registrar?: string, notes?: string }} options
 * @returns {object} domain record with status FLIPPED and profit set
 */
function flip(options = {}) {
  const { name, userId, buyPrice = 0, sellPrice, registrar = 'Namecheap', notes = '' } = options;
  if (!name || !userId) throw new Error("'name' and 'userId' are required");
  if (!sellPrice || sellPrice <= 0) throw new Error('sellPrice must be greater than zero');

  const record = addToPortfolio({ name, userId, registrar, registrationCost: buyPrice, notes });
  record.status = STATUS.FLIPPED;
  record.soldPrice = sellPrice;
  record.profit = Math.round((sellPrice - buyPrice) * 100) / 100;
  return record;
}

// ---------------------------------------------------------------------------
// Portfolio summary
// ---------------------------------------------------------------------------

/**
 * Return aggregate statistics for a user's domain portfolio.
 *
 * @param {string} userId
 * @returns {object}
 */
function summary(userId) {
  const domains = Object.values(_portfolio).filter((d) => d.userId === userId);
  const counts = { owned: 0, listed: 0, sold: 0, flipped: 0 };
  let totalInvested = 0;
  let totalRevenue = 0;
  let portfolioValue = 0;

  for (const d of domains) {
    counts[d.status] = (counts[d.status] || 0) + 1;
    totalInvested += d.registrationCost;
    if (d.soldPrice !== null) totalRevenue += d.soldPrice;
    if (d.status === STATUS.OWNED || d.status === STATUS.LISTED) {
      portfolioValue += d.estimatedValue;
    }
  }

  return {
    userId,
    totalDomains: domains.length,
    ...counts,
    totalInvestedUsd: Math.round(totalInvested * 100) / 100,
    totalRevenueUsd: Math.round(totalRevenue * 100) / 100,
    totalProfitUsd: Math.round((totalRevenue - totalInvested) * 100) / 100,
    portfolioEstimatedValueUsd: Math.round(portfolioValue * 100) / 100,
  };
}

// ---------------------------------------------------------------------------
// Main run function — surfaces top domain flip opportunities
// ---------------------------------------------------------------------------

/**
 * Main entry point for domainBot.
 * Returns a list of suggested domain flipping opportunities.
 *
 * @param {{ keywords?: string[], minProfit?: number, userId?: string }} [options]
 * @returns {{ bot: string, opportunities: object[], timestamp: string }}
 */
function run(options = {}) {
  const { keywords = ['dreamco', 'aibot', 'flipit', 'earnmore', 'protools'], minProfit = 500 } = options;

  const opportunities = keywords.flatMap((kw) => {
    const res = search(kw, { tlds: ['.com', '.io', '.ai'], limit: 3 });
    return res.results
      .filter((r) => r.available && r.price_usd > 0)
      .map((r) => ({
        name: r.name,
        buyPrice: r.price_usd,
        estimatedSellPrice: r.estimated_value_usd,
        estimatedProfit: Math.round((r.estimated_value_usd - r.price_usd) * 100) / 100,
        roi_pct: Math.round(((r.estimated_value_usd - r.price_usd) / r.price_usd) * 100),
      }))
      .filter((o) => o.estimatedProfit >= minProfit);
  });

  opportunities.sort((a, b) => b.estimatedProfit - a.estimatedProfit);

  return {
    bot: 'domainBot',
    action: `Found ${opportunities.length} domain flip opportunities`,
    opportunities,
    timestamp: new Date().toISOString(),
  };
}

module.exports = { search, valuate, addToPortfolio, listPortfolio, markForSale, closeSale, flip, summary, run };
