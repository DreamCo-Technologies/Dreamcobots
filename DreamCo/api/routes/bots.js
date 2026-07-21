'use strict';

/**
 * DreamCo — Bots Router
 *
 * Mounts all /bots routes onto the given HTTP handler router.
 * Keeps route registration separate from controller logic.
 */

const { authenticate } = require('../auth');
const { listBots, runBots } = require('../controllers/botsController');

/**
 * Register bot routes on a plain Node.js http.Server request handler.
 * Returns null if no route matched (so callers can chain other routers).
 *
 * @param {import('http').IncomingMessage} req
 * @param {import('http').ServerResponse} res
 * @returns {boolean} true if the route was handled
 */
function botsRouter(req, res) {
  // GET /bots — list bots (public)
  if (req.url === '/bots' && req.method === 'GET') {
    listBots(req, res);
    return true;
  }

  // POST /bots/run — trigger a full cycle (requires auth)
  if (req.url === '/bots/run' && req.method === 'POST') {
    authenticate(req, res, () => runBots(req, res));
    return true;
  }

  return false;
}

module.exports = { botsRouter };
