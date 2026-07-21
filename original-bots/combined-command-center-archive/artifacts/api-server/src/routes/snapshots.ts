import { Router, type IRouter } from "express";
import { db, snapshotsTable, agentsTable, aiSourcesTable } from "@workspace/db";
import { sql, desc } from "drizzle-orm";
import { requireAuth } from "../middlewares/authMiddleware";

const router: IRouter = Router();

/** Compute the current, honest, DB-derived empire metrics. */
async function captureMetrics(): Promise<Record<string, number>> {
  const [agents] = await db.select({ c: sql<number>`count(*)::int` }).from(agentsTable);
  const [active] = await db
    .select({ c: sql<number>`count(*)::int` })
    .from(agentsTable)
    .where(sql`${agentsTable.status} = 'active'`);
  const [sources] = await db.select({ c: sql<number>`count(*)::int` }).from(aiSourcesTable);
  const [invocations] = await db
    .select({ c: sql<number>`coalesce(sum(${agentsTable.invocations}),0)::int` })
    .from(agentsTable);
  const [revenue] = await db
    .select({ c: sql<number>`coalesce(sum(${agentsTable.revenueGenerated}),0)::float` })
    .from(agentsTable);

  return {
    agents: agents?.c ?? 0,
    activeAgents: active?.c ?? 0,
    aiSources: sources?.c ?? 0,
    totalInvocations: invocations?.c ?? 0,
    revenueGenerated: revenue?.c ?? 0,
  };
}

// GET current live metrics without persisting.
router.get("/snapshots/live", async (_req, res): Promise<void> => {
  res.json(await captureMetrics());
});

// GET snapshot history (most recent first).
router.get("/snapshots", async (req, res): Promise<void> => {
  const limit = Math.min(Number(req.query.limit ?? 90) || 90, 365);
  const rows = await db.select().from(snapshotsTable).orderBy(desc(snapshotsTable.capturedAt)).limit(limit);
  res.json(rows);
});

// POST capture a snapshot now. Each call appends a new point in time.
router.post("/snapshots", requireAuth, async (req, res): Promise<void> => {
  try {
    const metrics = await captureMetrics();
    const [row] = await db
      .insert(snapshotsTable)
      .values({ metrics, meta: { source: "manual", note: req.body?.note ?? null } })
      .returning();
    res.status(201).json(row);
  } catch (err) {
    req.log.error({ err }, "snapshot capture failed");
    res.status(500).json({ error: "Failed to capture snapshot" });
  }
});

export default router;
