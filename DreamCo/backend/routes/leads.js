/**
 * DreamCo LeadGenBot — Leads Route
 *
 * Handles all lead-related API endpoints:
 *   GET  /api/leads           — fetch all stored leads (with optional filters)
 *   POST /api/leads           — add a new lead manually
 *   GET  /api/leads/export    — export leads as CSV
 *   POST /api/leads/scrape    — trigger a new scrape from the backend
 *   POST /api/subscribe       — create a Stripe subscription
 *   POST /api/buy-leads       — purchase leads via Stripe (pay-per-lead)
 */

const express = require('express');
const router = express.Router();
const path = require('path');
const fs = require('fs');

const { scrapeLeads } = require('../services/scraper');
const { leadsToCSV, generateId, formatTimestamp } = require('../utils/helpers');

const LEADS_FILE = path.join(__dirname, '..', 'data', 'leads.json');

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/** Load leads from the JSON data store. */
function loadLeads() {
  try {
    if (!fs.existsSync(LEADS_FILE)) {
      return [];
    }
    const raw = fs.readFileSync(LEADS_FILE, 'utf8');
    return JSON.parse(raw);
  } catch {
    return [];
  }
}

/** Persist leads to the JSON data store. */
function saveLeads(leads) {
  fs.writeFileSync(LEADS_FILE, JSON.stringify(leads, null, 2), 'utf8');
}

// ---------------------------------------------------------------------------
// GET /api/leads
// ---------------------------------------------------------------------------
router.get('/', (req, res) => {
  const leads = loadLeads();
  const { industry, limit } = req.query;

  let filtered = leads;
  if (industry) {
    filtered = leads.filter(
      (l) => l.industry && l.industry.toLowerCase() === industry.toLowerCase()
    );
  }
  if (limit) {
    filtered = filtered.slice(0, parseInt(limit, 10));
  }

  res.json({
    success: true,
    total: filtered.length,
    leads: filtered,
  });
});

// ---------------------------------------------------------------------------
// POST /api/leads  — add a lead manually
// ---------------------------------------------------------------------------
router.post('/', (req, res) => {
  const { name, email, phone, company, industry, location } = req.body;
  if (!name || !email) {
    return res.status(400).json({ success: false, error: 'name and email are required' });
  }

  const leads = loadLeads();
  const newLead = {
    id: generateId(),
    name,
    email,
    phone: phone || null,
    company: company || null,
    industry: industry || 'General',
    location: location || null,
    score: Math.floor(Math.random() * 40) + 60, // default quality score 60-100
    source: 'manual',
    created_at: formatTimestamp(),
    dreamco_powered: true,
  };

  leads.push(newLead);
  saveLeads(leads);

  res.status(201).json({ success: true, lead: newLead });
});

// ---------------------------------------------------------------------------
// GET /api/leads/export  — export as CSV
// ---------------------------------------------------------------------------
router.get('/export', (req, res) => {
  const leads = loadLeads();
  if (leads.length === 0) {
    return res.status(404).json({ success: false, error: 'No leads to export' });
  }

  const csv = leadsToCSV(leads);
  res.setHeader('Content-Type', 'text/csv');
  res.setHeader('Content-Disposition', `attachment; filename="dreamco_leads_${Date.now()}.csv"`);
  res.send(csv);
});

// ---------------------------------------------------------------------------
// POST /api/leads/scrape  — trigger a fresh scrape
// ---------------------------------------------------------------------------
router.post('/scrape', async (req, res) => {
  const { industry = 'Real Estate', count = 50 } = req.body;
  try {
    const scraped = await scrapeLeads({ industry, count: parseInt(count, 10) });
    const leads = loadLeads();

    // Deduplicate by email
    const existing = new Set(leads.map((l) => l.email));
    const newLeads = scraped.filter((l) => !existing.has(l.email));
    const all = [...leads, ...newLeads];
    saveLeads(all);

    res.json({
      success: true,
      scraped: scraped.length,
      new_leads: newLeads.length,
      total: all.length,
    });
  } catch (err) {
    res.status(500).json({ success: false, error: err.message });
  }
});

// ---------------------------------------------------------------------------
// POST /api/subscribe  — Stripe subscription (Starter $29 / Pro $99 / Agency $299)
// ---------------------------------------------------------------------------
router.post('/subscribe', async (req, res) => {
  const { plan, payment_method_id, email } = req.body;
  if (!plan || !payment_method_id || !email) {
    return res
      .status(400)
      .json({ success: false, error: 'plan, payment_method_id, and email are required' });
  }

  const plans = {
    starter: { price: 2900, name: 'Starter Plan — $29/month' },
    pro: { price: 9900, name: 'Pro Plan — $99/month' },
    agency: { price: 29900, name: 'Agency Plan — $299/month' },
  };

  const selected = plans[plan.toLowerCase()];
  if (!selected) {
    return res.status(400).json({ success: false, error: `Unknown plan: ${plan}` });
  }

  // When Stripe keys are configured, use the real Stripe SDK.
  // In sandbox/dev mode, return a simulated response.
  if (!process.env.STRIPE_SECRET_KEY || process.env.STRIPE_SECRET_KEY.startsWith('sk_test_YOUR')) {
    return res.json({
      success: true,
      simulated: true,
      subscription: {
        id: `sub_${generateId()}`,
        plan: plan.toLowerCase(),
        amount_cents: selected.price,
        description: selected.name,
        customer_email: email,
        status: 'active',
        created_at: formatTimestamp(),
        dreamco_powered: true,
      },
    });
  }

  try {
    const stripe = require('stripe')(process.env.STRIPE_SECRET_KEY);
    const customer = await stripe.customers.create({ email, payment_method: payment_method_id });
    await stripe.paymentMethods.attach(payment_method_id, { customer: customer.id });
    await stripe.customers.update(customer.id, {
      invoice_settings: { default_payment_method: payment_method_id },
    });

    const priceId = {
      starter: process.env.STRIPE_PRICE_STARTER,
      pro: process.env.STRIPE_PRICE_PRO,
      agency: process.env.STRIPE_PRICE_AGENCY,
    }[plan.toLowerCase()];

    const subscription = await stripe.subscriptions.create({
      customer: customer.id,
      items: [{ price: priceId }],
      expand: ['latest_invoice.payment_intent'],
    });

    res.json({ success: true, subscription: { id: subscription.id, status: subscription.status } });
  } catch (err) {
    res.status(500).json({ success: false, error: err.message });
  }
});

// ---------------------------------------------------------------------------
// POST /api/buy-leads  — pay-per-lead ($2–$10 per lead)
// ---------------------------------------------------------------------------
router.post('/buy-leads', async (req, res) => {
  const { quantity = 10, payment_method_id, email } = req.body;
  if (!payment_method_id || !email) {
    return res
      .status(400)
      .json({ success: false, error: 'payment_method_id and email are required' });
  }

  const qty = Math.max(1, parseInt(quantity, 10));
  const price_per_lead = qty >= 100 ? 2 : qty >= 50 ? 5 : 10; // volume discount
  const total_cents = qty * price_per_lead * 100;

  if (!process.env.STRIPE_SECRET_KEY || process.env.STRIPE_SECRET_KEY.startsWith('sk_test_YOUR')) {
    return res.json({
      success: true,
      simulated: true,
      order: {
        id: `ord_${generateId()}`,
        quantity: qty,
        price_per_lead_usd: price_per_lead,
        total_usd: (total_cents / 100).toFixed(2),
        customer_email: email,
        status: 'paid',
        created_at: formatTimestamp(),
        dreamco_powered: true,
      },
    });
  }

  try {
    const stripe = require('stripe')(process.env.STRIPE_SECRET_KEY);
    const intent = await stripe.paymentIntents.create({
      amount: total_cents,
      currency: 'usd',
      payment_method: payment_method_id,
      confirm: true,
      description: `DreamCo LeadGenBot — ${qty} leads @ $${price_per_lead}/lead`,
      receipt_email: email,
    });

    res.json({
      success: true,
      order: {
        payment_intent_id: intent.id,
        quantity: qty,
        price_per_lead_usd: price_per_lead,
        total_usd: (total_cents / 100).toFixed(2),
        status: intent.status,
      },
    });
  } catch (err) {
    res.status(500).json({ success: false, error: err.message });
  }
});

module.exports = router;
