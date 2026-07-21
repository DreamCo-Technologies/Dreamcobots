/**
 * DreamCo LeadGenBot — Bots Route
 *
 * Handles bot-management API endpoints:
 *   POST /api/bots          — create (generate) a new bot
 *   GET  /api/bots          — list all registered bots
 *   GET  /api/bots/:id      — get details of a specific bot
 *   POST /api/bots/:id/run  — execute a bot by ID
 */

const express = require('express');
const router = express.Router();

const { generateBot, listBots, getBot, runBot } = require('../services/botGenerator');

// ---------------------------------------------------------------------------
// POST /api/bots  — generate a new bot from a template + command
// ---------------------------------------------------------------------------
router.post('/', (req, res) => {
  const { name, industry, command, tier = 'free' } = req.body;
  if (!name) {
    return res.status(400).json({ success: false, error: 'name is required' });
  }

  try {
    const bot = generateBot({ name, industry: industry || 'General', command, tier });
    res.status(201).json({ success: true, bot });
  } catch (err) {
    res.status(500).json({ success: false, error: err.message });
  }
});

// ---------------------------------------------------------------------------
// GET /api/bots  — list all bots
// ---------------------------------------------------------------------------
router.get('/', (_req, res) => {
  const bots = listBots();
  res.json({ success: true, total: bots.length, bots });
});

// ---------------------------------------------------------------------------
// GET /api/bots/:id  — get a single bot
// ---------------------------------------------------------------------------
router.get('/:id', (req, res) => {
  const bot = getBot(req.params.id);
  if (!bot) {
    return res.status(404).json({ success: false, error: 'Bot not found' });
  }
  res.json({ success: true, bot });
});

// ---------------------------------------------------------------------------
// POST /api/bots/:id/run  — execute a bot
// ---------------------------------------------------------------------------
router.post('/:id/run', (req, res) => {
  const bot = getBot(req.params.id);
  if (!bot) {
    return res.status(404).json({ success: false, error: 'Bot not found' });
  }

  try {
    const result = runBot(bot, req.body);
    res.json({ success: true, result });
  } catch (err) {
    res.status(500).json({ success: false, error: err.message });
  }
});

module.exports = router;
