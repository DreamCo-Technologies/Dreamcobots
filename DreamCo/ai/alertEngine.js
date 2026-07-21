'use strict';

/**
 * AlertEngine — generates urgency-tiered alerts for high-value opportunities.
 */

const { score } = require('./rankingAI');

const THRESHOLDS = {
  HIGH: { minProfit: 50, minScore: 80 },
  MEDIUM: { minProfit: 20, minScore: 50 },
  LOW: { minProfit: 5, minScore: 20 },
};

function getUrgency(item) {
  const profit = parseFloat(item.profit || item.revenue || 0);
  const s = score(item);
  if (profit >= THRESHOLDS.HIGH.minProfit || s >= THRESHOLDS.HIGH.minScore) {
    return 'HIGH';
  }
  if (profit >= THRESHOLDS.MEDIUM.minProfit || s >= THRESHOLDS.MEDIUM.minScore) {
    return 'MEDIUM';
  }
  if (profit >= THRESHOLDS.LOW.minProfit || s >= THRESHOLDS.LOW.minScore) {
    return 'LOW';
  }
  return null;
}

function generateAlert(item) {
  const urgency = getUrgency(item);
  if (!urgency) {
    return null;
  }
  return {
    urgency,
    item: item.name || item.id || 'Unknown',
    profit: parseFloat(item.profit || item.revenue || 0),
    score: score(item),
    message: `[${urgency}] ${item.name || item.id}: $${item.profit || item.revenue} profit opportunity`,
    timestamp: new Date().toISOString(),
  };
}

function filterAlerts(items, minUrgency = 'LOW') {
  const levels = ['LOW', 'MEDIUM', 'HIGH'];
  const minIdx = levels.indexOf(minUrgency);
  return items
    .map((item) => generateAlert(item))
    .filter((a) => a !== null && levels.indexOf(a.urgency) >= minIdx);
}

module.exports = { getUrgency, generateAlert, filterAlerts, THRESHOLDS };
