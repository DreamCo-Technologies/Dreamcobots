'use strict';

/**
 * DreamCo — Bots Controller
 *
 * Business logic for the /bots API endpoints.
 * Keeps route definitions thin and logic centralised.
 */

const registry = require('../../core/botRegistry');
const { runAllBots } = require('../../orchestrator/runAllBots');

/**
 * GET /bots — list all registered bots with their current status.
 *
 * @param {import('http').IncomingMessage} _req
 * @param {import('http').ServerResponse} res
 */
function listBots(_req, res) {
  const bots = registry.getBots();
  res.writeHead(200, { 'Content-Type': 'application/json' });
  res.end(JSON.stringify({ bots, total: bots.length }));
}

/**
 * POST /bots/run — trigger a full bot cycle and return results.
 *
 * @param {import('http').IncomingMessage} _req
 * @param {import('http').ServerResponse} res
 */
async function runBots(_req, res) {
  try {
    const data = await runAllBots();
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify(data));
  } catch (err) {
    res.writeHead(500, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ error: err.message }));
  }
}

module.exports = { listBots, runBots };
