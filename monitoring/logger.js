'use strict';

/**
 * DreamCo — System Logger
 *
 * Appends timestamped log lines to logs.txt so every bot run, error,
 * and revenue event is permanently recorded for auditing and debugging.
 */

const fs = require('fs');
const path = require('path');

const LOG_FILE = path.resolve('logs.txt');

/**
 * Append a message to the system log file.
 *
 * @param {string} message - Text to log
 * @param {'INFO'|'WARN'|'ERROR'} [level='INFO'] - Severity level
 */
function log(message, level = 'INFO') {
  const line = `${new Date().toISOString()} [${level}] ${message}\n`;

  try {
    fs.appendFileSync(LOG_FILE, line);
  } catch (err) {
    // Degrade gracefully — write to stderr so operators know logs are being lost
    process.stderr.write(`[logger] Failed to write to ${LOG_FILE}: ${err.message}\n`);
  }
}

/**
 * Shorthand helpers.
 */
const info = (msg) => log(msg, 'INFO');
const warn = (msg) => log(msg, 'WARN');
const error = (msg) => log(msg, 'ERROR');

module.exports = { log, info, warn, error };
