'use strict';

/**
 * DreamCo — Money Module Tests
 *
 * Comprehensive test suite for:
 *   - affiliate_engine.js
 *   - lead_seller.js
 *   - auto_checkout.js
 *   - pricing_engine.js
 */

// ---------------------------------------------------------------------------
// affiliate_engine
// ---------------------------------------------------------------------------
describe('affiliateEngine', () => {
  let engine;

  beforeEach(() => {
    // Re-require to get a fresh module instance with reset state
    jest.resetModules();
    engine = require('../money/affiliate_engine');
  });

  test('DEFAULT_PROGRAMS contains 5 pre-loaded programs', () => {
    expect(Array.isArray(engine.DEFAULT_PROGRAMS)).toBe(true);
    expect(engine.DEFAULT_PROGRAMS.length).toBe(5);
  });

  test('DEFAULT_PROGRAMS contains amazon, clickbank, shareasale, impact, cj', () => {
    const names = engine.DEFAULT_PROGRAMS.map((p) => p.name);
    expect(names).toContain('amazon');
    expect(names).toContain('clickbank');
    expect(names).toContain('shareasale');
    expect(names).toContain('impact');
    expect(names).toContain('cj');
  });

  test('registerProgram registers a new program and returns it', () => {
    const prog = engine.registerProgram('testprog', {
      displayName: 'Test Program',
      baseUrl: 'https://test.com/',
      commissionRate: 0.1,
      cookieDays: 30,
    });
    expect(prog.name).toBe('testprog');
    expect(prog.commissionRate).toBe(0.1);
    expect(prog.earnings).toBe(0);
  });

  test('registerProgram throws on missing name', () => {
    expect(() => engine.registerProgram('', {})).toThrow();
  });

  test('registerProgram overwrites existing program', () => {
    engine.registerProgram('amazon', {
      displayName: 'Updated',
      baseUrl: 'https://x.com/',
      commissionRate: 0.05,
    });
    const earnings = engine.getEarnings('amazon');
    expect(earnings.program).toBe('amazon');
  });

  test('generateLink returns linkId, url, and program', () => {
    const result = engine.generateLink('amazon', 'B123', 'user1');
    expect(result).toHaveProperty('linkId');
    expect(result).toHaveProperty('url');
    expect(result.program).toBe('amazon');
    expect(result.url).toContain('B123');
  });

  test('generateLink throws for unknown program', () => {
    expect(() => engine.generateLink('nonexistent', 'B123', 'u1')).toThrow();
  });

  test('trackClick increments click count', () => {
    const link = engine.generateLink('amazon', 'B456', 'u2');
    const result = engine.trackClick(link.linkId);
    expect(result.totalClicks).toBe(1);
    const result2 = engine.trackClick(link.linkId);
    expect(result2.totalClicks).toBe(2);
  });

  test('trackClick throws for unknown linkId', () => {
    expect(() => engine.trackClick('nonexistent')).toThrow();
  });

  test('trackConversion computes commission correctly', () => {
    const link = engine.generateLink('amazon', 'B789', 'u3');
    const result = engine.trackConversion(link.linkId, 100);
    // Amazon is 4% commission
    expect(result.commission).toBeCloseTo(4.0, 2);
  });

  test('trackConversion accumulates earnings on program', () => {
    const link = engine.generateLink('clickbank', 'CB001', 'u4');
    engine.trackConversion(link.linkId, 200);
    const earnings = engine.getEarnings('clickbank');
    // ClickBank 50% = $100
    expect(earnings.earnings).toBeCloseTo(100, 2);
  });

  test('getEarnings returns correct structure', () => {
    const e = engine.getEarnings('amazon');
    expect(e).toHaveProperty('program');
    expect(e).toHaveProperty('earnings');
    expect(e).toHaveProperty('clicks');
    expect(e).toHaveProperty('conversions');
  });

  test('getEarnings throws for unregistered program', () => {
    expect(() => engine.getEarnings('notexist')).toThrow();
  });

  test('getAllEarnings returns total and byProgram array', () => {
    const result = engine.getAllEarnings();
    expect(result).toHaveProperty('total');
    expect(Array.isArray(result.byProgram)).toBe(true);
    expect(result.byProgram.length).toBeGreaterThanOrEqual(5);
  });

  test('getAllEarnings total is sum of byProgram earnings', () => {
    const link = engine.generateLink('amazon', 'TEST', 'u99');
    engine.trackConversion(link.linkId, 50);
    const result = engine.getAllEarnings();
    const sum = result.byProgram.reduce((s, p) => s + p.earnings, 0);
    expect(result.total).toBeCloseTo(sum, 2);
  });

  test('getTopPrograms returns N programs sorted by earnings', () => {
    const link = engine.generateLink('clickbank', 'TOP', 'u5');
    engine.trackConversion(link.linkId, 1000);
    const top = engine.getTopPrograms(3);
    expect(top.length).toBeLessThanOrEqual(3);
    // Should be sorted descending
    for (let i = 1; i < top.length; i++) {
      expect(top[i - 1].earnings).toBeGreaterThanOrEqual(top[i].earnings);
    }
  });

  test('getTopPrograms(1) returns exactly one program', () => {
    const top = engine.getTopPrograms(1);
    expect(top.length).toBe(1);
  });
});

// ---------------------------------------------------------------------------
// lead_seller
// ---------------------------------------------------------------------------
describe('leadSeller', () => {
  let seller;

  beforeEach(() => {
    jest.resetModules();
    seller = require('../money/lead_seller');
  });

  test('captureLead creates a lead with correct fields', () => {
    const lead = seller.captureLead({
      name: 'Alice',
      email: 'alice@test.com',
      category: 'real_estate',
    });
    expect(lead).toHaveProperty('leadId');
    expect(lead.name).toBe('Alice');
    expect(lead.email).toBe('alice@test.com');
    expect(lead.status).toBe('new');
  });

  test('captureLead throws without email', () => {
    expect(() => seller.captureLead({ name: 'No Email' })).toThrow();
  });

  test('captureLead defaults source to organic', () => {
    const lead = seller.captureLead({ email: 'test@x.com' });
    expect(lead.source).toBe('organic');
  });

  test('scoreLead returns score 0-100', () => {
    const lead = seller.captureLead({
      name: 'Bob',
      email: 'bob@test.com',
      phone: '555-0001',
      source: 'linkedin',
      category: 'crypto',
    });
    const { score } = seller.scoreLead(lead.leadId);
    expect(score).toBeGreaterThanOrEqual(0);
    expect(score).toBeLessThanOrEqual(100);
  });

  test('scoreLead high-value category scores higher', () => {
    const realEstate = seller.captureLead({
      email: 'a@a.com',
      category: 'real_estate',
      name: 'X',
      phone: '555-1',
    });
    const general = seller.captureLead({
      email: 'b@b.com',
      category: 'general',
      name: 'Y',
      phone: '555-2',
    });
    const { score: s1 } = seller.scoreLead(realEstate.leadId);
    const { score: s2 } = seller.scoreLead(general.leadId);
    expect(s1).toBeGreaterThan(s2);
  });

  test('scoreLead throws for unknown leadId', () => {
    expect(() => seller.scoreLead('nonexistent')).toThrow();
  });

  test('sellLead marks lead as sold', () => {
    const lead = seller.captureLead({ email: 'sell@test.com' });
    const sold = seller.sellLead(lead.leadId, 'BuyerCorp', 50);
    expect(sold.status).toBe('sold');
    expect(sold.soldPrice).toBe(50);
    expect(sold.buyerName).toBe('BuyerCorp');
  });

  test('sellLead throws if lead already sold', () => {
    const lead = seller.captureLead({ email: 'double@test.com' });
    seller.sellLead(lead.leadId, 'Buyer1', 25);
    expect(() => seller.sellLead(lead.leadId, 'Buyer2', 25)).toThrow();
  });

  test('sellLead throws for unknown leadId', () => {
    expect(() => seller.sellLead('bad_id', 'B', 10)).toThrow();
  });

  test('getLeads returns all leads without filter', () => {
    seller.captureLead({ email: 'l1@test.com' });
    seller.captureLead({ email: 'l2@test.com' });
    expect(seller.getLeads().length).toBeGreaterThanOrEqual(2);
  });

  test('getLeads filters by status', () => {
    const lead = seller.captureLead({ email: 'filter@test.com' });
    seller.sellLead(lead.leadId, 'Buyer', 40);
    const sold = seller.getLeads({ status: 'sold' });
    expect(sold.every((l) => l.status === 'sold')).toBe(true);
  });

  test('getLeads filters by minScore', () => {
    seller.captureLead({ email: 'low@test.com' });
    const all = seller.getLeads({ minScore: 0 });
    const high = seller.getLeads({ minScore: 99 });
    expect(high.length).toBeLessThanOrEqual(all.length);
  });

  test('getRevenue returns total and transactionCount', () => {
    const lead = seller.captureLead({ email: 'rev@test.com' });
    seller.sellLead(lead.leadId, 'RevBuyer', 100);
    const rev = seller.getRevenue();
    expect(rev.total).toBeGreaterThanOrEqual(100);
    expect(rev.transactionCount).toBeGreaterThanOrEqual(1);
  });

  test('exportLeads returns JSON string by default', () => {
    seller.captureLead({ email: 'exp@test.com' });
    const json = seller.exportLeads('json');
    expect(() => JSON.parse(json)).not.toThrow();
    expect(Array.isArray(JSON.parse(json))).toBe(true);
  });

  test('exportLeads returns CSV with headers', () => {
    seller.captureLead({ email: 'csv@test.com' });
    const csv = seller.exportLeads('csv');
    expect(typeof csv).toBe('string');
    expect(csv).toContain('leadId');
    expect(csv).toContain('email');
  });
});

// ---------------------------------------------------------------------------
// auto_checkout
// ---------------------------------------------------------------------------
describe('autoCheckout', () => {
  let checkout;

  beforeEach(() => {
    jest.resetModules();
    checkout = require('../money/auto_checkout');
  });

  test('DISCOUNT_CODES has 5 pre-loaded codes', () => {
    const keys = Object.keys(checkout.DISCOUNT_CODES);
    expect(keys.length).toBe(5);
  });

  test('createOrder creates a pending order', () => {
    const order = checkout.createOrder(
      [{ name: 'Bot License', price: 49, quantity: 1 }],
      'cust_1',
      'stripe'
    );
    expect(order).toHaveProperty('orderId');
    expect(order.status).toBe('pending');
    expect(order.total).toBe(49);
  });

  test('createOrder throws with empty items', () => {
    expect(() => checkout.createOrder([], 'c1', 'stripe')).toThrow();
  });

  test('createOrder throws with invalid payment method', () => {
    expect(() => checkout.createOrder([{ name: 'X', price: 10 }], 'c1', 'bitcoin')).toThrow();
  });

  test('processPayment marks order as paid (stripe)', () => {
    const order = checkout.createOrder([{ name: 'X', price: 99 }], 'c2', 'stripe');
    const result = checkout.processPayment(order.orderId, { token: 'tok_test' });
    expect(result).toHaveProperty('txnId');
    expect(result.processorResponse.processor).toBe('stripe');
    expect(checkout.getOrder(order.orderId).status).toBe('paid');
  });

  test('processPayment marks order as paid (paypal)', () => {
    const order = checkout.createOrder([{ name: 'Y', price: 150 }], 'c3', 'paypal');
    const result = checkout.processPayment(order.orderId, {});
    expect(result.processorResponse.processor).toBe('paypal');
  });

  test('processPayment marks order as paid (crypto)', () => {
    const order = checkout.createOrder([{ name: 'Z', price: 200 }], 'c4', 'crypto');
    const result = checkout.processPayment(order.orderId, {});
    expect(result.processorResponse.processor).toBe('crypto');
  });

  test('processPayment throws for already-paid order', () => {
    const order = checkout.createOrder([{ name: 'W', price: 50 }], 'c5', 'stripe');
    checkout.processPayment(order.orderId, {});
    expect(() => checkout.processPayment(order.orderId, {})).toThrow();
  });

  test('applyDiscount percent reduces total correctly', () => {
    const order = checkout.createOrder([{ name: 'A', price: 100 }], 'c6', 'stripe');
    const updated = checkout.applyDiscount(order.orderId, 'DREAMCO10');
    expect(updated.total).toBeCloseTo(90, 2);
    expect(updated.discountCode).toBe('DREAMCO10');
  });

  test('applyDiscount fixed reduces total correctly', () => {
    const order = checkout.createOrder([{ name: 'B', price: 200 }], 'c7', 'stripe');
    const updated = checkout.applyDiscount(order.orderId, 'FLAT50');
    expect(updated.total).toBeCloseTo(150, 2);
  });

  test('applyDiscount throws for invalid code', () => {
    const order = checkout.createOrder([{ name: 'C', price: 100 }], 'c8', 'stripe');
    expect(() => checkout.applyDiscount(order.orderId, 'FAKE_CODE')).toThrow();
  });

  test('generateInvoice returns correct invoice object', () => {
    const order = checkout.createOrder([{ name: 'D', price: 75 }], 'c9', 'stripe');
    const invoice = checkout.generateInvoice(order.orderId);
    expect(invoice).toHaveProperty('invoiceId');
    expect(invoice.orderId).toBe(order.orderId);
    expect(invoice.total).toBe(75);
  });

  test('getOrder returns order by ID', () => {
    const order = checkout.createOrder([{ name: 'E', price: 30 }], 'c10', 'stripe');
    expect(checkout.getOrder(order.orderId)).toBeDefined();
    expect(checkout.getOrder(order.orderId).orderId).toBe(order.orderId);
  });

  test('getOrder returns null for unknown ID', () => {
    expect(checkout.getOrder('bad_id')).toBeNull();
  });

  test('getRevenue accumulates across paid orders', () => {
    const o1 = checkout.createOrder([{ name: 'F', price: 100 }], 'c11', 'stripe');
    const o2 = checkout.createOrder([{ name: 'G', price: 200 }], 'c12', 'paypal');
    checkout.processPayment(o1.orderId, {});
    checkout.processPayment(o2.orderId, {});
    const rev = checkout.getRevenue();
    expect(rev.total).toBeGreaterThanOrEqual(300);
    expect(rev.orderCount).toBeGreaterThanOrEqual(2);
  });
});

// ---------------------------------------------------------------------------
// pricing_engine
// ---------------------------------------------------------------------------
describe('pricingEngine', () => {
  let engine;

  beforeEach(() => {
    jest.resetModules();
    engine = require('../money/pricing_engine');
  });

  test('TIER_MULTIPLIERS has FREE, PRO, ENTERPRISE', () => {
    expect(engine.TIER_MULTIPLIERS).toHaveProperty('FREE');
    expect(engine.TIER_MULTIPLIERS).toHaveProperty('PRO');
    expect(engine.TIER_MULTIPLIERS).toHaveProperty('ENTERPRISE');
  });

  test('setBasePrice stores and returns price record', () => {
    const record = engine.setBasePrice('prod_1', 99);
    expect(record.productId).toBe('prod_1');
    expect(record.basePrice).toBe(99);
  });

  test('setBasePrice throws for negative price', () => {
    expect(() => engine.setBasePrice('prod_neg', -5)).toThrow();
  });

  test('setBasePrice throws for missing productId', () => {
    expect(() => engine.setBasePrice('', 10)).toThrow();
  });

  test('setBasePrice records price history on update', () => {
    engine.setBasePrice('prod_hist', 50);
    engine.setBasePrice('prod_hist', 60);
    const history = engine.getPricingHistory('prod_hist');
    expect(history.history.length).toBeGreaterThanOrEqual(1);
  });

  test('getDynamicPrice returns higher price for high demand', () => {
    engine.setBasePrice('prod_demand', 100);
    const low = engine.getDynamicPrice('prod_demand', { demandScore: 10 });
    const high = engine.getDynamicPrice('prod_demand', { demandScore: 90 });
    expect(high.dynamicPrice).toBeGreaterThan(low.dynamicPrice);
  });

  test('getDynamicPrice applies peak hour surcharge', () => {
    engine.setBasePrice('prod_peak', 100);
    const normal = engine.getDynamicPrice('prod_peak', { demandScore: 50, isPeakHour: false });
    const peak = engine.getDynamicPrice('prod_peak', { demandScore: 50, isPeakHour: true });
    expect(peak.dynamicPrice).toBeGreaterThanOrEqual(normal.dynamicPrice);
  });

  test('getDynamicPrice returns base price with neutral context', () => {
    engine.setBasePrice('prod_neutral', 100);
    const result = engine.getDynamicPrice('prod_neutral', { demandScore: 50 });
    expect(result.dynamicPrice).toBeGreaterThan(0);
    expect(result).toHaveProperty('factors');
  });

  test('getDynamicPrice throws for unset product', () => {
    expect(() => engine.getDynamicPrice('prod_unknown', {})).toThrow();
  });

  test('applyTierPricing FREE returns $0', () => {
    const result = engine.applyTierPricing(100, 'FREE');
    expect(result.tieredPrice).toBe(0);
  });

  test('applyTierPricing PRO returns base price', () => {
    const result = engine.applyTierPricing(100, 'PRO');
    expect(result.tieredPrice).toBe(100);
  });

  test('applyTierPricing ENTERPRISE applies 2.5x multiplier', () => {
    const result = engine.applyTierPricing(100, 'ENTERPRISE');
    expect(result.tieredPrice).toBe(250);
  });

  test('applyTierPricing throws for unknown tier', () => {
    expect(() => engine.applyTierPricing(100, 'ULTRA')).toThrow();
  });

  test('runCompetitorAnalysis returns competitors and recommendation', () => {
    engine.setBasePrice('prod_comp', 100);
    const result = engine.runCompetitorAnalysis('prod_comp');
    expect(result).toHaveProperty('competitors');
    expect(Array.isArray(result.competitors)).toBe(true);
    expect(result.competitors.length).toBe(4);
    expect(result).toHaveProperty('recommendation');
    expect(result).toHaveProperty('avgCompetitorPrice');
  });

  test('runCompetitorAnalysis throws for unset product', () => {
    expect(() => engine.runCompetitorAnalysis('prod_missing')).toThrow();
  });

  test('optimizePrice returns suggested price', () => {
    engine.setBasePrice('prod_opt', 100);
    const result = engine.optimizePrice('prod_opt');
    expect(result).toHaveProperty('suggestedPrice');
    expect(result.suggestedPrice).toBeGreaterThan(0);
    expect(result).toHaveProperty('reason');
  });

  test('optimizePrice with history suggests different price', () => {
    engine.setBasePrice('prod_opth', 80);
    engine.setBasePrice('prod_opth', 120); // creates history entry for 80
    const result = engine.optimizePrice('prod_opth');
    expect(result.suggestedPrice).not.toEqual(result.currentPrice);
  });

  test('getPricingHistory returns history array', () => {
    engine.setBasePrice('prod_ph', 50);
    const result = engine.getPricingHistory('prod_ph');
    expect(result).toHaveProperty('currentPrice');
    expect(Array.isArray(result.history)).toBe(true);
  });

  test('getPricingHistory throws for unknown product', () => {
    expect(() => engine.getPricingHistory('unknown_prod')).toThrow();
  });
});
