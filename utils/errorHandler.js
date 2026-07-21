'use strict';

/**
 * DreamCo — Unified Error Handler
 *
 * Provides a standard error class, categorization, formatting,
 * and wrapping utilities for all DreamCo modules.
 */

/** Standard error codes used across DreamCo. */
const ERROR_CODES = {
  BOT_FAILURE: 'BOT_FAILURE',
  PAYMENT_FAILURE: 'PAYMENT_FAILURE',
  API_ERROR: 'API_ERROR',
  DB_ERROR: 'DB_ERROR',
  AUTH_ERROR: 'AUTH_ERROR',
  VALIDATION_ERROR: 'VALIDATION_ERROR',
};

/**
 * DreamCoError — enriched Error class with code, context, and timestamp.
 */
class DreamCoError extends Error {
  /**
   * @param {string} message - Human-readable error message.
   * @param {string} code - One of ERROR_CODES.
   * @param {Object} [context] - Additional context (module, action, etc.).
   */
  constructor(message, code, context) {
    super(message);
    this.name = 'DreamCoError';
    this.code = code || ERROR_CODES.API_ERROR;
    this.context = context || {};
    this.timestamp = new Date().toISOString();
    this.isOperational = true;
    if (Error.captureStackTrace) {
      Error.captureStackTrace(this, DreamCoError);
    }
  }
}

/**
 * Handle an error: log it, categorize it, and return a standardized object.
 * @param {Error|DreamCoError} err - The error to handle.
 * @param {Object} [context] - Additional context to attach.
 * @returns {{ code: string, message: string, context: Object, timestamp: string, operational: boolean }}
 */
function handleError(err, context) {
  const code = err.code || _categorize(err);
  const ctx = { ...(err.context || {}), ...(context || {}) };
  const standardized = {
    code,
    message: err.message,
    context: ctx,
    timestamp: err.timestamp || new Date().toISOString(),
    operational: isOperational(err),
    stack: process.env.NODE_ENV !== 'production' ? err.stack : undefined,
  };
  // Log to stderr so the error is always visible
  process.stderr.write(`[DreamCo ERROR] [${code}] ${err.message} | ${JSON.stringify(ctx)}\n`);
  return standardized;
}

/**
 * Wrap a function (sync or async) with automatic error handling.
 * @param {Function} fn - The function to wrap.
 * @param {Object} [context] - Context to attach on failure.
 * @returns {Function} Wrapped function.
 */
function withErrorHandling(fn, context) {
  return async function (...args) {
    try {
      return await fn(...args);
    } catch (err) {
      return { error: handleError(err, context) };
    }
  };
}

/**
 * Format an error for an API response body.
 * @param {Error|DreamCoError} err - The error.
 * @returns {{ success: false, error: { code: string, message: string, timestamp: string } }}
 */
function formatError(err) {
  return {
    success: false,
    error: {
      code: err.code || _categorize(err),
      message: err.message || 'An unexpected error occurred.',
      timestamp: err.timestamp || new Date().toISOString(),
    },
  };
}

/**
 * Determine whether an error is operational (expected, recoverable) or a
 * programming error (unexpected bug).
 * @param {Error} err - The error.
 * @returns {boolean}
 */
function isOperational(err) {
  if (err instanceof DreamCoError) {
    return err.isOperational === true;
  }
  // Known operational error patterns
  const operationalMessages = ['not found', 'invalid', 'unauthorized', 'forbidden', 'timeout'];
  const msg = (err.message || '').toLowerCase();
  return operationalMessages.some((p) => msg.includes(p));
}

/**
 * Categorize a generic Error into a DreamCo error code.
 * @param {Error} err - The error.
 * @returns {string} Error code.
 */
function _categorize(err) {
  const msg = (err.message || '').toLowerCase();
  if (msg.includes('payment') || msg.includes('stripe') || msg.includes('paypal')) {
    return ERROR_CODES.PAYMENT_FAILURE;
  }
  if (msg.includes('auth') || msg.includes('token') || msg.includes('unauthorized')) {
    return ERROR_CODES.AUTH_ERROR;
  }
  if (msg.includes('database') || msg.includes('db') || msg.includes('query')) {
    return ERROR_CODES.DB_ERROR;
  }
  if (msg.includes('bot') || msg.includes('scraper') || msg.includes('automation')) {
    return ERROR_CODES.BOT_FAILURE;
  }
  if (msg.includes('invalid') || msg.includes('required') || msg.includes('must be')) {
    return ERROR_CODES.VALIDATION_ERROR;
  }
  return ERROR_CODES.API_ERROR;
}

module.exports = {
  ERROR_CODES,
  DreamCoError,
  handleError,
  withErrorHandling,
  formatError,
  isOperational,
};
