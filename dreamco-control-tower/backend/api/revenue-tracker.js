/**
 * DreamCo Control Tower — Revenue Tracker
 *
 * Tracks payment events sourced from Stripe and PayPal (or any provider)
 * and provides aggregation methods for the analytics dashboard.
 *
 * In production, wire up the Stripe SDK or PayPal SDK with real API keys
 * from config/payments.json (keys are populated at deploy time via env vars).
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const PAYMENTS_CONFIG = path.join(__dirname, '../../config/payments.json');

// In-memory ledger (replace with a persistent DB for production)
const ledger = [];

// ---------------------------------------------------------------------------
// Config helpers
// ---------------------------------------------------------------------------

export function getPaymentsConfig() {
  return JSON.parse(fs.readFileSync(PAYMENTS_CONFIG, 'utf8'));
}

// ---------------------------------------------------------------------------
// Record a payment event
// ---------------------------------------------------------------------------

/**
 * Record a payment against a bot or service.
 * @param {string} source - e.g. "stripe", "paypal"
 * @param {string} botName - bot or service the payment is attributed to
 * @param {number} amountUsd - amount in USD (decimal)
 * @param {object} [meta] - optional extra metadata
 */
export function recordPayment(source, botName, amountUsd, meta = {}) {
  const entry = {
    id: `pay_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`,
    source,
    bot: botName,
    amountUsd: Math.round(amountUsd * 100) / 100,
    recordedAt: new Date().toISOString(),
    meta,
  };
  ledger.push(entry);
  return entry;
}

// ---------------------------------------------------------------------------
// Aggregation
// ---------------------------------------------------------------------------

/**
 * Return a full revenue summary grouped by bot and source.
 */
export function getRevenueSummary() {
  const total = ledger.reduce((sum, e) => sum + e.amountUsd, 0);
  const byBot = {};
  const bySource = {};

  for (const entry of ledger) {
    byBot[entry.bot] = Math.round(((byBot[entry.bot] ?? 0) + entry.amountUsd) * 100) / 100;
    bySource[entry.source] =
      Math.round(((bySource[entry.source] ?? 0) + entry.amountUsd) * 100) / 100;
  }

  return {
    totalUsd: Math.round(total * 100) / 100,
    entryCount: ledger.length,
    byBot,
    bySource,
    recentEntries: ledger.slice(-20),
  };
}

/**
 * Return monthly revenue breakdown.
 */
export function getMonthlyRevenue() {
  const monthly = {};
  for (const entry of ledger) {
    const month = entry.recordedAt.slice(0, 7); // "YYYY-MM"
    monthly[month] = Math.round(((monthly[month] ?? 0) + entry.amountUsd) * 100) / 100;
  }
  return monthly;
}
