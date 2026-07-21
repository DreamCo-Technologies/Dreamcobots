'use strict';

/**
 * DreamCo — Authentication Middleware
 *
 * Validates the x-api-key header against configured keys.
 * Used by all protected API endpoints.
 */

const config = require('../core/config');

const VALID_KEYS = new Set(config.api.keys);

/**
 * Authenticate request using x-api-key header.
 * Only the x-api-key header is accepted; the authorization header is
 * intentionally not supported to avoid authentication confusion.
 *
 * @param {import('http').IncomingMessage} req
 * @param {import('http').ServerResponse} res
 * @param {Function} next
 */
function authenticate(req, res, next) {
  const token = req.headers['x-api-key'];

  if (!token || !VALID_KEYS.has(token)) {
    res.writeHead(401, { 'Content-Type': 'application/json' });
    return res.end(JSON.stringify({ error: 'Unauthorized' }));
  }

  next();
}

module.exports = { authenticate, VALID_KEYS };
