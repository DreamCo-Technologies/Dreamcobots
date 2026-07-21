import { Router, type IRouter } from "express";
import { db, aiSourcesTable } from "@workspace/db";
import { desc } from "drizzle-orm";
import { indexSources } from "../lib/sourceIndexer";
import { requireAuth } from "../middlewares/authMiddleware";

const router: IRouter = Router();

// GET the indexed global AI sources catalog (LIVE — from the DB).
router.get("/sources", async (_req, res): Promise<void> => {
  const rows = await db.select().from(aiSourcesTable).orderBy(desc(aiSourcesTable.sizeBytes));
  const byRole: Record<string, number> = {};
  let totalModels = 0;
  let totalUseCases = 0;
  for (const r of rows) {
    byRole[r.role] = (byRole[r.role] ?? 0) + 1;
    totalModels += Number((r.signals as Record<string, unknown>)?.models ?? 0);
    totalUseCases += Number((r.signals as Record<string, unknown>)?.useCases ?? 0);
  }
  res.json({ total: rows.length, byRole, totalModels, totalUseCases, sources: rows });
});

// POST re-index the global AI sources from the Dreamcobots repo.
router.post("/sources/index", requireAuth, async (req, res): Promise<void> => {
  try {
    const limit = Math.min(Number(req.body?.limit ?? 40) || 40, 120);
    const result = await indexSources(limit);
    res.json(result);
  } catch (err) {
    req.log.error({ err }, "source indexing failed");
    res.status(500).json({ error: "Failed to index sources" });
  }
});

export default router;
