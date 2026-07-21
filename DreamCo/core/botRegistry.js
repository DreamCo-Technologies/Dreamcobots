'use strict';

/**
 * DreamCo — Bot Registry
 *
 * Tracks every registered bot with its status, last-run timestamp, and
 * any earned revenue.  Powers the dashboard, revenue tracking, and scaling.
 */

/** @type {Map<string, Object>} */
const _registry = new Map();

/**
 * Register a bot so the system can track and manage it.
 *
 * @param {{ name: string, category?: string }} bot - Bot descriptor
 * @returns {Object} The registered bot record
 */
function registerBot(bot) {
  if (!bot || !bot.name) {
    throw new Error('Bot must have a "name" property');
  }

  const record = {
    name: bot.name,
    category: bot.category || 'general',
    status: 'idle',
    lastRun: null,
    totalRevenue: 0,
    runCount: 0,
  };

  _registry.set(bot.name, record);
  return record;
}

/**
 * Update a bot's status after a run.
 *
 * @param {string} name - Bot name
 * @param {'idle'|'running'|'error'|'scaling'} status
 * @param {number} [revenue=0] - Revenue earned in this run
 */
function updateStatus(name, status, revenue = 0) {
  const record = _registry.get(name);
  if (!record) {
    throw new Error(`Bot "${name}" is not registered`);
  }

  record.status = status;
  record.lastRun = new Date().toISOString();
  record.totalRevenue += revenue;
  record.runCount += 1;
}

/**
 * Retrieve all registered bots.
 * @returns {Object[]} Array of bot records
 */
function getBots() {
  return Array.from(_registry.values());
}

/**
 * Retrieve a single bot by name.
 * @param {string} name
 * @returns {Object|undefined}
 */
function getBot(name) {
  return _registry.get(name);
}

/**
 * Deregister a bot (e.g. during shutdown or hot-reload).
 * @param {string} name
 */
function deregisterBot(name) {
  _registry.delete(name);
}

/**
 * Clear all registrations (useful in tests).
 */
function reset() {
  _registry.clear();
}

module.exports = { registerBot, updateStatus, getBots, getBot, deregisterBot, reset };
