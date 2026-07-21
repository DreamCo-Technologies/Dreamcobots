/**
 * DreamCo LeadGenBot — Utility Helpers
 *
 * Shared utility functions for formatting, ID generation, and CSV export.
 */

const { randomUUID } = require('crypto');

/**
 * Generate a unique ID string.
 * @returns {string}
 */
function generateId() {
  if (typeof randomUUID === 'function') {
    return randomUUID().replace(/-/g, '').slice(0, 16);
  }
  // Fallback for older Node versions
  return Math.random().toString(36).slice(2, 18) + Date.now().toString(36);
}

/**
 * Return the current UTC timestamp as an ISO 8601 string.
 * @returns {string}
 */
function formatTimestamp() {
  return new Date().toISOString();
}

/**
 * Convert an array of lead objects to a CSV string.
 *
 * @param {Array<object>} leads
 * @returns {string} CSV-formatted string with header row.
 */
function leadsToCSV(leads) {
  if (!leads || leads.length === 0) {
    return '';
  }

  const COLUMNS = [
    'id',
    'name',
    'email',
    'phone',
    'company',
    'industry',
    'location',
    'score',
    'source',
    'created_at',
  ];

  const header = COLUMNS.join(',');
  const rows = leads.map((lead) =>
    COLUMNS.map((col) => {
      const val = lead[col] == null ? '' : String(lead[col]);
      // Escape quotes and wrap fields containing commas or quotes
      if (val.includes(',') || val.includes('"') || val.includes('\n')) {
        return `"${val.replace(/"/g, '""')}"`;
      }
      return val;
    }).join(',')
  );

  return [header, ...rows].join('\n');
}

/**
 * Validate that an email address has a basic valid format.
 * @param {string} email
 * @returns {boolean}
 */
function isValidEmail(email) {
  if (!email || typeof email !== 'string') {
    return false;
  }
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

/**
 * Clamp a number between min and max.
 * @param {number} value
 * @param {number} min
 * @param {number} max
 * @returns {number}
 */
function clamp(value, min, max) {
  return Math.min(Math.max(value, min), max);
}

module.exports = { generateId, formatTimestamp, leadsToCSV, isValidEmail, clamp };
