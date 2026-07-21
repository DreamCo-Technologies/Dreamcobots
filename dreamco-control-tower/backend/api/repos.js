/**
 * DreamCo Control Tower — API Routes: Repos
 */

import { Router } from 'express';
import repoManager from '../repo-manager.js';

const router = Router();
const OWNER = process.env.GITHUB_OWNER || 'ireanjordan24';

// GET /api/repos/:name — single repo status
router.get('/:name', async (req, res) => {
  try {
    const status = await repoManager.getRepoStatus(OWNER, req.params.name);
    res.json(status);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// POST /api/repos/multi — multiple repos at once
router.post('/multi', async (req, res) => {
  const { repos } = req.body;
  if (!Array.isArray(repos) || !repos.length) {
    return res.status(400).json({ error: 'repos array is required.' });
  }
  try {
    const statuses = await repoManager.getMultiRepoStatus(OWNER, repos);
    const conflicts = repoManager.detectConflicts(statuses);
    res.json({ statuses, conflicts, total: statuses.length });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

export default router;
