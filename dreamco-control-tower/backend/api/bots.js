/**
 * DreamCo Control Tower — API Routes: Bots
 */

import { Router } from 'express';
import botManager from '../bot-manager.js';

const router = Router();

// GET /api/bots — list all bots with heartbeat status
router.get('/', async (req, res) => {
  try {
    const bots = await botManager.getBotStatuses();
    res.json({ bots, total: bots.length });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// GET /api/bots/:name — status for a single bot
router.get('/:name', async (req, res) => {
  const bots = await botManager.getBotStatuses();
  const bot = bots.find((b) => b.name === req.params.name);
  if (!bot) {
    return res.status(404).json({ error: 'Bot not found.' });
  }
  res.json(bot);
});

// POST /api/bots/:name/ping — record heartbeat
router.post('/:name/ping', (req, res) => {
  botManager.ping(req.params.name);
  res.json({ bot_name: req.params.name, status: 'live', pinged_at: new Date().toISOString() });
});

// POST /api/bots/:name/pull — pull latest code
router.post('/:name/pull', async (req, res) => {
  const bots = botManager.loadBots();
  const bot = bots.find((b) => b.name === req.params.name);
  if (!bot) {
    return res.status(404).json({ error: 'Bot not found.' });
  }

  const result = botManager.pullLatest(bot.repoPath);
  res.json(result);
});

// POST /api/bots/:name/pr — create auto-upgrade PR
router.post('/:name/pr', async (req, res) => {
  const bots = botManager.loadBots();
  const bot = bots.find((b) => b.name === req.params.name);
  if (!bot) {
    return res.status(404).json({ error: 'Bot not found.' });
  }

  const result = await botManager.createPullRequest({
    repo: bot.repo,
    head: req.body.branch || 'auto-upgrade',
    title: req.body.title || `🤖 Auto-upgrade: ${bot.name}`,
    body: req.body.body,
  });
  res.json(result);
});

export default router;
