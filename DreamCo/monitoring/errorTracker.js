'use strict';

/**
 * DreamCo — Error Tracker
 *
 * Captures and stores runtime errors so the system can detect patterns,
 * alert on spikes, and eventually auto-heal recurring failures.
 */

/** @type {Array<{message: string, stack?: string, time: string, context?: string}>} */
const _errors = [];

const MAX_ERRORS = 1000; // cap in-memory store to prevent unbounded growth

/**
 * Record an error for later analysis.
 *
 * @param {Error|string} err   - Error object or message string
 * @param {string} [context]  - Optional label (e.g. bot name, endpoint)
 */
function trackError(err, context) {
  const entry = {
    message: err instanceof Error ? err.message : String(err),
    stack: err instanceof Error ? err.stack : undefined,
    context: context || 'unknown',
    time: new Date().toISOString(),
  };

  _errors.push(entry);

  if (_errors.length >= MAX_ERRORS) {
    _errors.shift(); // drop the oldest entry (O(1) amortised)
  }

  return entry;
}

/**
 * Retrieve all tracked errors (newest first).
 * @returns {Object[]}
 */
function getErrors() {
  return [..._errors].reverse();
}

/**
 * Count of tracked errors (optionally filtered by context).
 * @param {string} [context]
 * @returns {number}
 */
function errorCount(context) {
  if (!context) {
    return _errors.length;
  }
  return _errors.filter((e) => e.context === context).length;
}

/**
 * Clear error history (useful in tests or after system recovery).
 */
function clearErrors() {
  _errors.length = 0;
}

module.exports = { trackError, getErrors, errorCount, clearErrors };
