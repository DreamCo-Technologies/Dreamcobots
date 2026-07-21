'use strict';

/**
 * DreamCo Payment Auto Collector Bot
 *
 * Subscription billing + invoice automation with in-memory store.
 * Manages subscription lifecycle, generates tax-inclusive invoices,
 * simulates payment collection, and reports MRR/ARR metrics.
 *
 * BOT → ACTION → RESULT → REVENUE → VALIDATION → SCALE
 */

/** Subscription plan definitions. */
const PLANS = {
  starter: { name: 'Starter', price_usd: 29, features: ['basic_access', 'email_support'] },
  professional: {
    name: 'Professional',
    price_usd: 99,
    features: ['full_access', 'priority_support', 'analytics'],
  },
  business: {
    name: 'Business',
    price_usd: 299,
    features: ['full_access', 'dedicated_support', 'analytics', 'api_access', 'white_label'],
  },
  enterprise: {
    name: 'Enterprise',
    price_usd: 999,
    features: ['everything', 'sla', 'custom_integrations', 'dedicated_csm'],
  },
};

const TAX_RATE = 0.085; // 8.5%

/** In-memory subscription store. */
const subscriptions = [];

/** In-memory invoice store. */
const invoices = [];

/**
 * Create a new subscription for a customer.
 * @param {string} customerId - Unique customer identifier
 * @param {string} plan - One of the PLANS keys
 * @returns {Object} Subscription object
 */
function createSubscription(customerId, plan = 'starter') {
  const planConfig = PLANS[plan] || PLANS.starter;
  const subscription = {
    subscription_id: `SUB-${Date.now()}-${Math.floor(Math.random() * 9999)}`,
    customer_id: customerId,
    plan,
    plan_name: planConfig.name,
    price_usd: planConfig.price_usd,
    features: planConfig.features,
    status: 'active',
    billing_cycle: 'monthly',
    next_billing_date: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString(),
    created_at: new Date().toISOString(),
  };
  subscriptions.push(subscription);
  return subscription;
}

/**
 * Generate an invoice for an active subscription.
 * @param {string} subscriptionId - Subscription ID to invoice
 * @returns {Object} Invoice object with tax applied
 */
function generateInvoice(subscriptionId) {
  const sub = subscriptions.find((s) => s.subscription_id === subscriptionId);
  if (!sub) {
    return { error: `Subscription ${subscriptionId} not found` };
  }
  const subtotal = sub.price_usd;
  const tax = parseFloat((subtotal * TAX_RATE).toFixed(2));
  const total = parseFloat((subtotal + tax).toFixed(2));
  const invoice = {
    invoice_id: `INV-${Date.now()}-${Math.floor(Math.random() * 9999)}`,
    subscription_id: subscriptionId,
    customer_id: sub.customer_id,
    plan: sub.plan,
    subtotal,
    tax_rate: TAX_RATE,
    tax_amount: tax,
    total,
    status: 'pending',
    due_date: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString(),
    created_at: new Date().toISOString(),
  };
  invoices.push(invoice);
  return invoice;
}

/**
 * Simulate collecting payment for an invoice.
 * @param {string} invoiceId - Invoice ID to collect
 * @returns {Object} Payment result
 */
function collectPayment(invoiceId) {
  const invoice = invoices.find((inv) => inv.invoice_id === invoiceId);
  if (!invoice) {
    return { success: false, error: `Invoice ${invoiceId} not found` };
  }
  const success = Math.random() > 0.08; // 92% success rate
  invoice.status = success ? 'paid' : 'failed';
  invoice.paid_at = success ? new Date().toISOString() : null;
  return {
    success,
    invoice_id: invoiceId,
    amount_collected: success ? invoice.total : 0,
    status: invoice.status,
    message: success
      ? `Payment of $${invoice.total} collected for invoice ${invoiceId}`
      : `Payment failed for invoice ${invoiceId} — retry scheduled`,
  };
}

/**
 * Compute revenue and subscriber metrics from the in-memory store.
 * @returns {{ mrr: number, arr: number, total_subscribers: number, total_invoices: number }}
 */
function getStats() {
  const activeSubscriptions = subscriptions.filter((s) => s.status === 'active');
  const mrr = activeSubscriptions.reduce((sum, s) => sum + s.price_usd, 0);
  const paidInvoices = invoices.filter((inv) => inv.status === 'paid');
  return {
    mrr,
    arr: mrr * 12,
    total_subscribers: activeSubscriptions.length,
    total_invoices: invoices.length,
    paid_invoices: paidInvoices.length,
    total_collected: paidInvoices.reduce((sum, inv) => sum + inv.total, 0),
  };
}

/**
 * Main bot entry point — runs a billing collection cycle.
 * @param {Object} [options]
 * @param {number} [options.new_subscribers] - New subscribers to onboard this cycle
 * @returns {Object} Standardised bot output
 */
function run(options = {}) {
  const newCount = options.new_subscribers || Math.floor(Math.random() * 8) + 3;
  const planKeys = Object.keys(PLANS);

  // Onboard new subscribers
  const newSubs = [];
  for (let i = 0; i < newCount; i++) {
    const plan = planKeys[Math.floor(Math.random() * planKeys.length)];
    const sub = createSubscription(`CUST-${Date.now()}-${i}`, plan);
    newSubs.push(sub);
  }

  // Generate and collect invoices for new subscribers
  let collected = 0;
  for (const sub of newSubs) {
    const inv = generateInvoice(sub.subscription_id);
    if (inv.invoice_id) {
      const result = collectPayment(inv.invoice_id);
      if (result.success) collected++;
    }
  }

  const stats = getStats();
  const revenue = Math.floor(Math.random() * (3000 - 1200 + 1)) + 1200;
  const leadsGenerated = Math.floor(Math.random() * (40 - 20 + 1)) + 20;
  const conversionRate = newCount > 0 ? parseFloat((collected / newCount).toFixed(2)) : 0;

  return {
    bot: 'paymentAutoCollector',
    revenue,
    leads_generated: leadsGenerated,
    conversion_rate: conversionRate,
    new_subscribers: newCount,
    payments_collected: collected,
    mrr: stats.mrr,
    arr: stats.arr,
    total_subscribers: stats.total_subscribers,
    action: `Onboarded ${newCount} subscribers — collected ${collected} payments — MRR $${stats.mrr}`,
    timestamp: new Date().toISOString(),
  };
}

module.exports = {
  run,
  createSubscription,
  generateInvoice,
  collectPayment,
  getStats,
  PLANS,
  subscriptions,
  invoices,
};
