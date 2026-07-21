import { Router, type IRouter } from "express";
import { db, botRunsTable, botEarningsTable, botLearningsTable } from "@workspace/db";
import { desc, sql, gte } from "drizzle-orm";

const router: IRouter = Router();

router.get("/bots/runs", async (_req, res): Promise<void> => {
  const limit = 50;
  try {
    const rows = await db
      .select()
      .from(botRunsTable)
      .orderBy(desc(botRunsTable.startedAt))
      .limit(limit);
    res.json(rows);
  } catch {
    res.json([]);
  }
});

router.get("/bots/runs/stats", async (_req, res): Promise<void> => {
  try {
    const dayAgo = new Date(Date.now() - 86_400_000);
    const total = await db.select({ c: sql<number>`count(*)::int` }).from(botRunsTable);
    const last24h = await db
      .select({ c: sql<number>`count(*)::int` })
      .from(botRunsTable)
      .where(gte(botRunsTable.startedAt, dayAgo));
    const byBot = await db
      .select({
        botSlug: botRunsTable.botSlug,
        runs: sql<number>`count(*)::int`,
        revenue: sql<number>`coalesce(sum(${botRunsTable.revenueUsd}), 0)::float`,
      })
      .from(botRunsTable)
      .groupBy(botRunsTable.botSlug)
      .orderBy(sql`count(*) desc`)
      .limit(10);
    res.json({
      total: total[0]?.c ?? 0,
      last24h: last24h[0]?.c ?? 0,
      topBots: byBot,
    });
  } catch {
    res.json({ total: 0, last24h: 0, topBots: [] });
  }
});

router.get("/bots/earnings", async (_req, res): Promise<void> => {
  try {
    const rows = await db
      .select()
      .from(botEarningsTable)
      .orderBy(desc(botEarningsTable.occurredAt))
      .limit(50);
    const totals = await db
      .select({
        botSlug: botEarningsTable.botSlug,
        total: sql<number>`coalesce(sum(${botEarningsTable.amountUsd}), 0)::float`,
      })
      .from(botEarningsTable)
      .groupBy(botEarningsTable.botSlug)
      .orderBy(sql`coalesce(sum(amount_usd), 0) desc`)
      .limit(10);
    const grand = await db
      .select({ total: sql<number>`coalesce(sum(${botEarningsTable.amountUsd}), 0)::float` })
      .from(botEarningsTable);
    res.json({
      grandTotal: grand[0]?.total ?? 0,
      topEarners: totals,
      recent: rows,
    });
  } catch {
    res.json({ grandTotal: 0, topEarners: [], recent: [] });
  }
});

router.get("/bots/learnings", async (_req, res): Promise<void> => {
  try {
    const rows = await db
      .select()
      .from(botLearningsTable)
      .orderBy(desc(botLearningsTable.createdAt))
      .limit(50);
    const totals = await db
      .select({
        botSlug: botLearningsTable.botSlug,
        count: sql<number>`count(*)::int`,
        avgReward: sql<number>`coalesce(avg(${botLearningsTable.reward}), 0)::float`,
      })
      .from(botLearningsTable)
      .groupBy(botLearningsTable.botSlug)
      .orderBy(sql`count(*) desc`)
      .limit(10);
    const grand = await db
      .select({ c: sql<number>`count(*)::int` })
      .from(botLearningsTable);
    res.json({
      total: grand[0]?.c ?? 0,
      topLearners: totals,
      recent: rows,
    });
  } catch {
    res.json({ total: 0, topLearners: [], recent: [] });
  }
});

export default router;
