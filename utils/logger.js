'use strict';

/**
 * DreamCo — Enhanced Structured Logger
 *
 * Wraps the base monitoring/logger.js with namespacing, log levels,
 * colour-coded console output, file rotation, and log retrieval.
 */

const fs = require('fs');
const path = require('path');

/** Log levels in ascending severity order. */
const LEVELS = { DEBUG: 0, INFO: 1, WARN: 2, ERROR: 3, CRITICAL: 4 };

/** ANSI colour codes for console output. */
const COLOURS = {
  DEBUG: '\x1b[36m', // Cyan
  INFO: '\x1b[32m', // Green
  WARN: '\x1b[33m', // Yellow
  ERROR: '\x1b[31m', // Red
  CRITICAL: '\x1b[35m', // Magenta
  RESET: '\x1b[0m',
};

const LOG_DIR = path.resolve('logs');
const LOG_FILE = path.join(LOG_DIR, 'app.log');
const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10 MB

/** In-memory ring buffer of recent log entries (max 1000). */
const recentLogs = [];
const MAX_RECENT = 1000;

/** Minimum level from environment (default INFO). */
const MIN_LEVEL =
  LEVELS[process.env.LOG_LEVEL] !== undefined ? LEVELS[process.env.LOG_LEVEL] : LEVELS.INFO;

/**
 * Ensure the log directory exists.
 */
function _ensureLogDir() {
  if (!fs.existsSync(LOG_DIR)) {
    fs.mkdirSync(LOG_DIR, { recursive: true });
  }
}

/**
 * Rotate the log file if it exceeds MAX_FILE_SIZE.
 */
function _rotateIfNeeded() {
  try {
    if (fs.existsSync(LOG_FILE)) {
      const stats = fs.statSync(LOG_FILE);
      if (stats.size >= MAX_FILE_SIZE) {
        const rotated = `${LOG_FILE}.${Date.now()}.bak`;
        fs.renameSync(LOG_FILE, rotated);
      }
    }
  } catch (_err) {
    // Non-fatal — continue even if rotation fails
  }
}

/**
 * Write a log entry to file and console.
 * @param {string} level - Log level string.
 * @param {string} namespace - Logger namespace.
 * @param {string} message - Log message.
 * @param {Object} [meta] - Additional metadata.
 */
function log(level, message, meta) {
  const normalizedLevel = (level || 'INFO').toUpperCase();
  const levelNum = LEVELS[normalizedLevel];
  if (levelNum === undefined || levelNum < MIN_LEVEL) {
    return;
  }

  const entry = {
    timestamp: new Date().toISOString(),
    level: normalizedLevel,
    namespace: 'dreamco',
    message,
    meta: meta || {},
  };

  const line = JSON.stringify(entry);

  // In-memory buffer
  recentLogs.push(entry);
  if (recentLogs.length > MAX_RECENT) {
    recentLogs.shift();
  }

  // Console output with colours
  const colour = COLOURS[normalizedLevel] || COLOURS.RESET;
  const reset = COLOURS.RESET;
  const prefix = `${colour}[${normalizedLevel}]${reset} ${entry.timestamp} [${entry.namespace}]`;
  const metaStr = Object.keys(entry.meta).length > 0 ? ` ${JSON.stringify(entry.meta)}` : '';
  console.log(`${prefix} ${message}${metaStr}`);

  // File output
  try {
    _ensureLogDir();
    _rotateIfNeeded();
    fs.appendFileSync(LOG_FILE, line + '\n');
  } catch (_err) {
    process.stderr.write(`[logger] Failed to write to ${LOG_FILE}: ${_err.message}\n`);
  }
}

/**
 * Create a namespaced logger instance.
 * @param {string} namespace - Module or component name.
 * @returns {{ debug, info, warn, error, critical }} Namespaced log functions.
 */
function createLogger(namespace) {
  const ns = namespace || 'default';
  return {
    debug: (msg, meta) => _logNs('DEBUG', ns, msg, meta),
    info: (msg, meta) => _logNs('INFO', ns, msg, meta),
    warn: (msg, meta) => _logNs('WARN', ns, msg, meta),
    error: (msg, meta) => _logNs('ERROR', ns, msg, meta),
    critical: (msg, meta) => _logNs('CRITICAL', ns, msg, meta),
  };
}

/**
 * Internal namespaced logger writer.
 * @param {string} level
 * @param {string} namespace
 * @param {string} message
 * @param {Object} [meta]
 */
function _logNs(level, namespace, message, meta) {
  const normalizedLevel = (level || 'INFO').toUpperCase();
  const levelNum = LEVELS[normalizedLevel];
  if (levelNum === undefined || levelNum < MIN_LEVEL) {
    return;
  }
  const entry = {
    timestamp: new Date().toISOString(),
    level: normalizedLevel,
    namespace,
    message,
    meta: meta || {},
  };
  const line = JSON.stringify(entry);
  recentLogs.push(entry);
  if (recentLogs.length > MAX_RECENT) {
    recentLogs.shift();
  }
  const colour = COLOURS[normalizedLevel] || COLOURS.RESET;
  const reset = COLOURS.RESET;
  const prefix = `${colour}[${normalizedLevel}]${reset} ${entry.timestamp} [${namespace}]`;
  const metaStr = Object.keys(entry.meta).length > 0 ? ` ${JSON.stringify(entry.meta)}` : '';
  console.log(`${prefix} ${message}${metaStr}`);
  try {
    _ensureLogDir();
    _rotateIfNeeded();
    fs.appendFileSync(LOG_FILE, line + '\n');
  } catch (_err) {
    process.stderr.write(`[logger] Failed to write to ${LOG_FILE}: ${_err.message}\n`);
  }
}

/**
 * Get the N most recent log entries, optionally filtered by level.
 * @param {number} n - Number of entries to return.
 * @param {string} [level] - Filter by exact level string.
 * @returns {Object[]} Array of log entry objects.
 */
function getRecentLogs(n, level) {
  let entries = recentLogs.slice();
  if (level) {
    const lvl = level.toUpperCase();
    entries = entries.filter((e) => e.level === lvl);
  }
  return entries.slice(-n);
}

// Convenience top-level log functions
const debug = (msg, meta) => log('DEBUG', msg, meta);
const info = (msg, meta) => log('INFO', msg, meta);
const warn = (msg, meta) => log('WARN', msg, meta);
const error = (msg, meta) => log('ERROR', msg, meta);
const critical = (msg, meta) => log('CRITICAL', msg, meta);

module.exports = {
  createLogger,
  log,
  info,
  warn,
  error,
  debug,
  critical,
  getRecentLogs,
  LEVELS,
};
