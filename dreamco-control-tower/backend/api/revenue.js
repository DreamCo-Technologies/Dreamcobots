/**
 * DreamCo Control Tower — API Routes: Revenue
 */

import { Router } from 'express';
import { getRevenueSummary } from '../revenue-tracker.js';

const router = Router();

// GET /api/revenue — combined revenue from all payment providers
router.get('/', async (req, res) => {
  try {
    const summary = await getRevenueSummary();
    res.json(summary);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

export default router;
