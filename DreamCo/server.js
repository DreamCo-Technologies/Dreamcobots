'use strict';

const express = require('express');
const dealBot = require('./bots/dealBot');
const pennyBot = require('./bots/pennyBot');
const receiptBot = require('./bots/receiptBot');
const flipBot = require('./bots/flipBot');
const couponBot = require('./bots/couponBot');
const domainBot = require('./bots/domainBot');
const profitEngine = require('./ai/profitEngine');
const rankingAI = require('./ai/rankingAI');
const alertEngine = require('./ai/alertEngine');
const SCHEMAS = require('./firebase/schemas');

const app = express();
app.use(express.json());

// 1. GET /deals
app.get('/deals', (req, res) => {
  const { minProfit = 10, limit = 10 } = req.query;
  res.json(dealBot.run({ minProfit: parseFloat(minProfit), limit: parseInt(limit, 10) }));
});

// 2. GET /flips
app.get('/flips', (req, res) => {
  const { minProfit = 20, city = 'Local' } = req.query;
  res.json(flipBot.run({ minProfit: parseFloat(minProfit), city }));
});

// 3. GET /penny-deals
app.get('/penny-deals', (req, res) => {
  const { threshold = 1.0 } = req.query;
  res.json(pennyBot.run({ threshold: parseFloat(threshold) }));
});

// 4. GET /cashback
app.get('/cashback', (req, res) => {
  const { items } = req.query;
  const itemList = items ? items.split(',') : [];
  res.json(receiptBot.run({ items: itemList }));
});

// 5. GET /coupons
app.get('/coupons', (req, res) => {
  const { sources } = req.query;
  const sourceList = sources ? sources.split(',') : ['Honey', 'Rakuten', 'Ibotta'];
  res.json(couponBot.run({ sources: sourceList }));
});

// 6. GET /alerts
app.get('/alerts', (req, res) => {
  const { minUrgency = 'LOW' } = req.query;
  const deals = dealBot.run({ minProfit: 5, limit: 20 }).deals;
  const alerts = alertEngine.filterAlerts(deals, minUrgency);
  res.json({ alerts, count: alerts.length, timestamp: new Date().toISOString() });
});

// 7. GET /rank
app.get('/rank', (req, res) => {
  const { n = 10 } = req.query;
  const deals = dealBot.run({ minProfit: 0, limit: 50 }).deals;
  res.json({ ranked: rankingAI.topN(deals, parseInt(n, 10)), timestamp: new Date().toISOString() });
});

// 8. GET /schemas
app.get('/schemas', (req, res) => {
  res.json(SCHEMAS);
});

// 9. POST /profit
app.post('/profit', (req, res) => {
  const deal = req.body;
  res.json(profitEngine.calculateDeal(deal));
});

// 10. POST /profit/flip
app.post('/profit/flip', (req, res) => {
  const { buyPrice, sellPrice, feesPct } = req.body;
  res.json(
    profitEngine.calculateFlip(
      parseFloat(buyPrice),
      parseFloat(sellPrice),
      feesPct ? parseFloat(feesPct) : undefined
    )
  );
});

// 11. GET /health
app.get('/health', (req, res) => {
  res.json({ status: 'ok', service: 'DreamCo Money OS', timestamp: new Date().toISOString() });
});

// 12. GET /stack
app.get('/stack', (req, res) => {
  const { minProfit = 10 } = req.query;
  const mp = parseFloat(minProfit);
  const deals = dealBot.run({ minProfit: mp, limit: 20 }).deals;
  const pennies = pennyBot.run({}).pennyDeals;
  const coupons = couponBot.run({}).coupons;
  const ranked = rankingAI.topN([...deals, ...pennies], 10);
  const alerts = alertEngine.filterAlerts(ranked);
  const totalRevenue = ranked.reduce((s, d) => s + parseFloat(d.profit || d.revenue || 0), 0);
  res.json({
    deals,
    penny_deals: pennies,
    coupons,
    ranked,
    alerts,
    estimated_daily_profit: Math.round(totalRevenue * 100) / 100,
    timestamp: new Date().toISOString(),
  });
});

// 13. GET /bots
app.get('/bots', (req, res) => {
  res.json({
    bots: ['dealBot', 'pennyBot', 'receiptBot', 'flipBot', 'couponBot', 'domainBot'],
    ai: ['profitEngine', 'rankingAI', 'alertEngine'],
    version: '1.0.0',
  });
});

// ---------------------------------------------------------------------------
// Domain management endpoints
// ---------------------------------------------------------------------------

// 14. GET /domains
// List or search domains.  Query params: keyword (search), userId (portfolio).
app.get('/domains', (req, res) => {
  const { keyword, userId, status } = req.query;
  if (keyword) {
    // Search mode: find available domains matching the keyword
    const result = domainBot.search(keyword);
    return res.json(result);
  }
  if (userId) {
    // Portfolio mode: list this user's domains
    const domains = domainBot.listPortfolio(userId, { status });
    return res.json({ userId, domains, count: domains.length, timestamp: new Date().toISOString() });
  }
  // Default: return top flip opportunities
  res.json(domainBot.run());
});

// 15. POST /domains
// Register a new domain into a user's portfolio.
app.post('/domains', (req, res) => {
  const { name, userId, registrar, registrationCost, expiryDate, notes } = req.body;
  if (!name || !userId) {
    return res.status(400).json({ error: "'name' and 'userId' are required" });
  }
  try {
    const domain = domainBot.addToPortfolio({ name, userId, registrar, registrationCost, expiryDate, notes });
    res.status(201).json(domain);
  } catch (err) {
    res.status(400).json({ error: err.message });
  }
});

// 16. POST /domains/flip
// Record a completed domain flip (buy + sell in one step).
app.post('/domains/flip', (req, res) => {
  const { name, userId, buyPrice, sellPrice, registrar, notes } = req.body;
  if (!name || !userId) {
    return res.status(400).json({ error: "'name' and 'userId' are required" });
  }
  try {
    const domain = domainBot.flip({ name, userId, buyPrice, sellPrice, registrar, notes });
    res.status(201).json(domain);
  } catch (err) {
    res.status(400).json({ error: err.message });
  }
});

// 17. PUT /domains/:domainId/sell
// Mark a domain for sale or close a sale.
// Body: { action: 'list'|'close', askPrice?: number, soldPrice?: number }
app.put('/domains/:domainId/sell', (req, res) => {
  const { domainId } = req.params;
  const { action, askPrice, soldPrice } = req.body;
  try {
    let domain;
    if (action === 'list') {
      domain = domainBot.markForSale(domainId, parseFloat(askPrice));
    } else if (action === 'close') {
      domain = domainBot.closeSale(domainId, parseFloat(soldPrice));
    } else {
      return res.status(400).json({ error: "'action' must be 'list' or 'close'" });
    }
    res.json(domain);
  } catch (err) {
    res.status(400).json({ error: err.message });
  }
});

// 18. GET /domains/:userId/summary
// Return aggregate portfolio statistics for a user.
app.get('/domains/:userId/summary', (req, res) => {
  const { userId } = req.params;
  res.json(domainBot.summary(userId));
});

// 19. GET /domains/valuate
// Estimate the market value of a domain name.  Query param: name.
app.get('/domains/valuate', (req, res) => {
  const { name, cost } = req.query;
  if (!name) {
    return res.status(400).json({ error: "'name' query parameter is required" });
  }
  const estimated = domainBot.valuate(name, cost ? parseFloat(cost) : undefined);
  res.json({ name, estimated_value_usd: estimated, timestamp: new Date().toISOString() });
});

const PORT = process.env.PORT || 3001;

if (require.main === module) {
  app.listen(PORT, () => console.log(`DreamCo Money OS API running on port ${PORT}`));
}

module.exports = app;
