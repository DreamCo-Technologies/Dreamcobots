import { Router, type IRouter } from "express";
import { db, mediaJobsTable } from "@workspace/db";
import { desc, eq } from "drizzle-orm";
import { z } from "zod/v4";
import { requireAuth } from "../middlewares/authMiddleware";
import { generate, getCapabilities, getCapability, NeedsKeyError, type MediaKind } from "../lib/mediaProviders";

const router: IRouter = Router();

// Public: which media capabilities are LIVE vs NEEDS_KEY. Honest status only.
router.get("/media/capabilities", (_req, res): void => {
  res.json({ capabilities: getCapabilities() });
});

// The authenticated user's own media-generation history (audit trail).
router.get("/media/jobs", requireAuth, async (req, res): Promise<void> => {
  const rows = await db
    .select()
    .from(mediaJobsTable)
    .where(eq(mediaJobsTable.userId, req.user!.id))
    .orderBy(desc(mediaJobsTable.createdAt))
    .limit(100);
  res.json({ total: rows.length, jobs: rows });
});

const generateSchema = z.object({
  kind: z.enum(["image", "voice", "music", "video", "commercial"]),
  prompt: z.string().min(1).max(4000),
  // Consent gate: the caller MUST affirm they are authorized to generate /
  // clone this content. No job runs without it.
  consent: z.literal(true, { message: "explicit consent is required to generate media" }),
  params: z.record(z.string(), z.unknown()).optional(),
});

// Generate media. Requires auth AND an explicit consent acknowledgement.
// Every attempt is recorded in media_jobs as an audit-trail row.
router.post("/media/generate", requireAuth, async (req, res): Promise<void> => {
  const parsed = generateSchema.safeParse(req.body);
  if (!parsed.success) {
    res.status(400).json({ error: "invalid request", issues: parsed.error.issues });
    return;
  }
  const { kind, prompt, params } = parsed.data;
  const userId = req.user!.id;
  const cap = getCapability(kind as MediaKind);

  // Capability not connected: record the attempt and return an honest 503.
  if (cap.status !== "live") {
    const [job] = await db
      .insert(mediaJobsTable)
      .values({ userId, kind, provider: cap.provider, status: cap.status, prompt, params: params ?? {}, consent: true, error: cap.note })
      .returning();
    res.status(503).json({ status: cap.status, capability: cap, job });
    return;
  }

  // Record the running job (consent affirmed, user authenticated).
  const [job] = await db
    .insert(mediaJobsTable)
    .values({ userId, kind, provider: cap.provider, status: "running", prompt, params: params ?? {}, consent: true })
    .returning();

  try {
    const result = await generate(kind as MediaKind, prompt, params ?? {});
    const [updated] = await db
      .update(mediaJobsTable)
      .set({ status: "succeeded", provider: result.provider, resultUrl: result.resultUrl, params: { ...(params ?? {}), ...(result.meta ?? {}) } })
      .where(eq(mediaJobsTable.id, job!.id))
      .returning();
    res.json({ status: "succeeded", job: updated });
  } catch (err) {
    const isNeedsKey = err instanceof NeedsKeyError;
    const message = err instanceof Error ? err.message : "generation failed";
    const [updated] = await db
      .update(mediaJobsTable)
      .set({ status: isNeedsKey ? "needs_key" : "failed", error: message })
      .where(eq(mediaJobsTable.id, job!.id))
      .returning();
    req.log.error({ err, kind }, "media generation failed");
    res.status(isNeedsKey ? 503 : 502).json({ status: isNeedsKey ? "needs_key" : "failed", error: message, job: updated });
  }
});

export default router;
