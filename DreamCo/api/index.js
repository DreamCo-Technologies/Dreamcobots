'use strict';

/**
 * DreamCo API
 *
 * Lightweight HTTP API server exposing the DreamCo Money Operating System
 * to external consumers.  Supports API-key authentication and per-bot or
 * full-run endpoints.
 */

const http = require('http');
const { runAllBots, processBot, BOTS } = require('../orchestrator/index');

const PORT = process.env.API_PORT || 3001;

// Simple in-memory API key store (replace with database in production)
const VALID_API_KEYS = new Set(
  (process.env.DREAMCO_API_KEYS || 'dreamco_pro_123').split(',').map((k) => k.trim())
);

/**
 * Parse JSON body from an incoming request.
 * @param {http.IncomingMessage} req
 * @returns {Promise<Object>}
 */
function parseBody(req) {
  return new Promise((resolve, reject) => {
    let raw = '';
    req.on('data', (chunk) => {
      raw += chunk;
    });
    req.on('end', () => {
      try {
        resolve(raw ? JSON.parse(raw) : {});
      } catch (e) {
        reject(e);
      }
    });
    req.on('error', reject);
  });
}

/**
 * Authenticate request using x-api-key header.
 * @param {http.IncomingMessage} req
 * @returns {boolean}
 */
function authenticate(req) {
  const key = req.headers['x-api-key'];
  return key && VALID_API_KEYS.has(key);
}

/**
 * Send a JSON response.
 */
function json(res, statusCode, data) {
  res.writeHead(statusCode, { 'Content-Type': 'application/json' });
  res.end(JSON.stringify(data));
}

/**
 * Route handler — POST /run-bots
 * Runs all registered bots and returns aggregated results.
 */
async function handleRunBots(req, res) {
  if (!authenticate(req)) {
    return json(res, 401, { error: 'Unauthorized' });
  }
  const data = runAllBots();
  json(res, 200, data);
}

/**
 * Route handler — POST /run-single
 * Runs a single bot by name.
 */
async function handleRunSingle(req, res) {
  if (!authenticate(req)) {
    return json(res, 401, { error: 'Unauthorized' });
  }

  let body;
  try {
    body = await parseBody(req);
  } catch {
    return json(res, 400, { error: 'Invalid JSON body' });
  }

  const { name } = body;
  if (!name) {
    return json(res, 400, { error: 'Missing "name" field in request body' });
  }

  const botEntry = BOTS.find((b) => b.name === name);
  if (!botEntry) {
    return json(res, 404, { error: `Bot "${name}" not found` });
  }

  const result = processBot(botEntry.name, botEntry.module, body.options || {});
  json(res, 200, result);
}

/**
 * Start the API HTTP server.
 * @param {number} [port]
 * @returns {http.Server}
 */
function startServer(port = PORT) {
  const server = http.createServer(async (req, res) => {
    if (req.url === '/health' && req.method === 'GET') {
      return json(res, 200, {
        status: 'ok',
        service: 'dreamco-api',
        bots: BOTS.map((b) => b.name),
      });
    }
    if (req.url === '/run-bots' && req.method === 'POST') {
      return handleRunBots(req, res);
    }
    if (req.url === '/run-single' && req.method === 'POST') {
      return handleRunSingle(req, res);
    }
    json(res, 404, { error: 'Not found' });
  });

  server.listen(port, () => {
    console.log(`🔌 DreamCo API running at http://localhost:${port}`);
  });

  return server;
}

module.exports = { startServer, authenticate, VALID_API_KEYS };

if (require.main === module) {
  startServer();
}
