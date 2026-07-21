import { Router, type IRouter } from "express";
import { db, buddyNotesTable, insertBuddyNoteSchema } from "@workspace/db";
import { desc, eq, and } from "drizzle-orm";
import { requireAuth } from "../middlewares/authMiddleware";

const router: IRouter = Router();

// GET the authenticated user's Buddy memory (LIVE — from the DB). Notes are
// private per user. Optional ?category filter.
router.get("/buddy/notes", requireAuth, async (req, res): Promise<void> => {
  const userId = req.user!.id;
  const category = typeof req.query.category === "string" ? req.query.category : undefined;
  const where = category
    ? and(eq(buddyNotesTable.userId, userId), eq(buddyNotesTable.category, category))
    : eq(buddyNotesTable.userId, userId);
  const rows = await db.select().from(buddyNotesTable).where(where).orderBy(desc(buddyNotesTable.createdAt)).limit(300);
  const byCategory: Record<string, number> = {};
  for (const r of rows) byCategory[r.category] = (byCategory[r.category] ?? 0) + 1;
  res.json({ total: rows.length, byCategory, notes: rows });
});

// POST a note into the authenticated user's Buddy memory.
router.post("/buddy/notes", requireAuth, async (req, res): Promise<void> => {
  const parsed = insertBuddyNoteSchema.safeParse(req.body);
  if (!parsed.success) {
    res.status(400).json({ error: "invalid note", issues: parsed.error.issues });
    return;
  }
  const [row] = await db
    .insert(buddyNotesTable)
    .values({ ...parsed.data, userId: req.user!.id })
    .returning();
  res.status(201).json(row);
});

// DELETE one of the authenticated user's notes (scoped — can't touch others').
router.delete("/buddy/notes/:id", requireAuth, async (req, res): Promise<void> => {
  const id = String(req.params.id);
  await db.delete(buddyNotesTable).where(and(eq(buddyNotesTable.id, id), eq(buddyNotesTable.userId, req.user!.id)));
  res.status(204).end();
});

export default router;
