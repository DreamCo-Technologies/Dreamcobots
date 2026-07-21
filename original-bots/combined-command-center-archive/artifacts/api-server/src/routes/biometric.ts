import { Router, type IRouter } from "express";
import { db, mediaJobsTable, legalAcknowledgmentsTable, biometricEnrollmentsTable } from "@workspace/db";
import { and, desc, eq } from "drizzle-orm";
import { randomUUID } from "node:crypto";
import { z } from "zod/v4";
import { requireAuth } from "../middlewares/authMiddleware";
import { BIOMETRIC_POLICY, POLICY_KEY, POLICY_VERSION } from "../lib/legalPolicy";
import {
  generateClone,
  getCloneCapabilities,
  getCloneCapability,
  NeedsKeyError,
  type CloneModality,
} from "../lib/mediaProviders";

const router: IRouter = Router();

// ── Legal policy ("read all the laws before signing up to use Buddy") ──────────

// Public: the versioned biometric/likeness policy the user must read & accept.
router.get("/legal/biometric-policy", (_req, res): void => {
  res.json({ policy: BIOMETRIC_POLICY });
});

// The authenticated user's acknowledgments, plus whether the CURRENT policy
// version has been accepted (the gate for enrollment / cloning).
router.get("/legal/acknowledgments", requireAuth, async (req, res): Promise<void> => {
  const rows = await db
    .select()
    .from(legalAcknowledgmentsTable)
    .where(eq(legalAcknowledgmentsTable.userId, req.user!.id))
    .orderBy(desc(legalAcknowledgmentsTable.acknowledgedAt));
  const currentAccepted = rows.some((r) => r.documentKey === POLICY_KEY && r.version === POLICY_VERSION);
  res.json({ currentVersion: POLICY_VERSION, currentAccepted, acknowledgments: rows });
});

const ackSchema = z.object({
  version: z.string().min(1),
  // The user must affirm each promise from the policy before we record acceptance.
  accept: z.literal(true, { message: "you must accept the policy to continue" }),
});

router.post("/legal/acknowledge", requireAuth, async (req, res): Promise<void> => {
  const parsed = ackSchema.safeParse(req.body);
  if (!parsed.success) {
    res.status(400).json({ error: "invalid request", issues: parsed.error.issues });
    return;
  }
  if (parsed.data.version !== POLICY_VERSION) {
    res.status(409).json({ error: "policy version out of date", currentVersion: POLICY_VERSION });
    return;
  }
  const [row] = await db
    .insert(legalAcknowledgmentsTable)
    .values({ userId: req.user!.id, documentKey: POLICY_KEY, version: POLICY_VERSION })
    .returning();
  res.json({ acknowledgment: row });
});

// ── Cloning capabilities (engine readiness; honest needs_config) ───────────────

router.get("/biometric/capabilities", (_req, res): void => {
  res.json({ capabilities: getCloneCapabilities() });
});

// ── Biometric enrollment ("sign in with your voice/image to use it") ───────────

async function hasCurrentLawsAck(userId: string): Promise<boolean> {
  const rows = await db
    .select()
    .from(legalAcknowledgmentsTable)
    .where(
      and(
        eq(legalAcknowledgmentsTable.userId, userId),
        eq(legalAcknowledgmentsTable.documentKey, POLICY_KEY),
        eq(legalAcknowledgmentsTable.version, POLICY_VERSION),
      ),
    )
    .limit(1);
  return rows.length > 0;
}

async function activeEnrollment(userId: string, modality: CloneModality) {
  const rows = await db
    .select()
    .from(biometricEnrollmentsTable)
    .where(
      and(
        eq(biometricEnrollmentsTable.userId, userId),
        eq(biometricEnrollmentsTable.modality, modality),
        eq(biometricEnrollmentsTable.status, "enrolled"),
      ),
    )
    .orderBy(desc(biometricEnrollmentsTable.createdAt))
    .limit(1);
  return rows[0] ?? null;
}

router.get("/biometric/enrollments", requireAuth, async (req, res): Promise<void> => {
  const rows = await db
    .select()
    .from(biometricEnrollmentsTable)
    .where(eq(biometricEnrollmentsTable.userId, req.user!.id))
    .orderBy(desc(biometricEnrollmentsTable.createdAt));
  res.json({ enrollments: rows });
});

const enrollSchema = z.object({
  modality: z.enum(["voice", "image"]),
  // Explicit, per-enrollment consent that the sample is the user's own or
  // authorized. No enrollment without it.
  consent: z.literal(true, { message: "explicit consent is required to enroll a biometric" }),
  enrollmentMethod: z.enum(["recorded", "uploaded"]),
});

router.post("/biometric/enroll", requireAuth, async (req, res): Promise<void> => {
  const parsed = enrollSchema.safeParse(req.body);
  if (!parsed.success) {
    res.status(400).json({ error: "invalid request", issues: parsed.error.issues });
    return;
  }
  const userId = req.user!.id;
  // Gate: the current laws must be acknowledged before any enrollment.
  if (!(await hasCurrentLawsAck(userId))) {
    res.status(412).json({ error: "legal acknowledgment required", currentVersion: POLICY_VERSION });
    return;
  }
  const { modality, enrollmentMethod } = parsed.data;
  // Supersede any prior active enrollment for this modality (single active per modality).
  await db
    .update(biometricEnrollmentsTable)
    .set({ status: "revoked", revokedAt: new Date() })
    .where(
      and(
        eq(biometricEnrollmentsTable.userId, userId),
        eq(biometricEnrollmentsTable.modality, modality),
        eq(biometricEnrollmentsTable.status, "enrolled"),
      ),
    );
  const [row] = await db
    .insert(biometricEnrollmentsTable)
    .values({
      userId,
      modality,
      status: "enrolled",
      enrollmentMethod,
      // The bindable reference is ALWAYS server-generated. Clients cannot supply
      // or influence it, so cloning can only ever bind to this enrollment record
      // — never to a client-controlled / arbitrary external sample id (IDOR).
      sampleRef: `enroll:${modality}:${randomUUID()}`,
      lawsVersion: POLICY_VERSION,
    })
    .returning();
  res.json({ enrollment: row });
});

const revokeSchema = z.object({ modality: z.enum(["voice", "image"]) });

router.post("/biometric/revoke", requireAuth, async (req, res): Promise<void> => {
  const parsed = revokeSchema.safeParse(req.body);
  if (!parsed.success) {
    res.status(400).json({ error: "invalid request", issues: parsed.error.issues });
    return;
  }
  await db
    .update(biometricEnrollmentsTable)
    .set({ status: "revoked", revokedAt: new Date() })
    .where(
      and(
        eq(biometricEnrollmentsTable.userId, req.user!.id),
        eq(biometricEnrollmentsTable.modality, parsed.data.modality),
        eq(biometricEnrollmentsTable.status, "enrolled"),
      ),
    );
  res.json({ revoked: true, modality: parsed.data.modality });
});

// ── Clone generation (fully gated) ─────────────────────────────────────────────

const cloneSchema = z.object({
  modality: z.enum(["voice", "image"]),
  prompt: z.string().min(1).max(4000),
  consent: z.literal(true, { message: "explicit consent is required to clone" }),
  params: z.record(z.string(), z.unknown()).optional(),
});

// Append a row to the consent audit ledger (media_jobs) for EVERY clone attempt,
// including ones rejected at a gate, so the ledger is a complete record.
async function logCloneAttempt(args: {
  userId: string;
  kind: string;
  provider: string;
  status: string;
  prompt: string;
  consent: boolean;
  error?: string | null;
  extra?: Record<string, unknown>;
}) {
  const [job] = await db
    .insert(mediaJobsTable)
    .values({
      userId: args.userId,
      kind: args.kind,
      provider: args.provider,
      status: args.status,
      prompt: args.prompt,
      params: { clone: true, ...(args.extra ?? {}) },
      consent: args.consent,
      error: args.error ?? null,
    })
    .returning();
  return job;
}

router.post("/biometric/clone", requireAuth, async (req, res): Promise<void> => {
  const userId = req.user!.id;
  const parsed = cloneSchema.safeParse(req.body);
  if (!parsed.success) {
    // Log the rejected attempt for a complete audit ledger.
    const rawModality = req.body?.modality === "image" ? "image" : "voice";
    const rawPrompt = typeof req.body?.prompt === "string" ? req.body.prompt.slice(0, 4000) : "";
    await logCloneAttempt({
      userId,
      kind: rawModality,
      provider: "DreamCo Clone (self-hosted)",
      status: "rejected_invalid_request",
      prompt: rawPrompt,
      consent: req.body?.consent === true,
      error: "invalid request",
    });
    res.status(400).json({ error: "invalid request", issues: parsed.error.issues });
    return;
  }
  const { modality, prompt, params } = parsed.data;

  // Gate 1: current laws acknowledged.
  if (!(await hasCurrentLawsAck(userId))) {
    await logCloneAttempt({
      userId,
      kind: modality,
      provider: "DreamCo Clone (self-hosted)",
      status: "rejected_no_legal_ack",
      prompt,
      consent: true,
      error: `legal acknowledgment required (policy ${POLICY_VERSION})`,
      extra: params ?? {},
    });
    res.status(412).json({ error: "legal acknowledgment required", currentVersion: POLICY_VERSION });
    return;
  }
  // Gate 2: an active enrollment exists for this modality (you can only clone
  // a voice/face you have personally enrolled and consented to).
  const enrollment = await activeEnrollment(userId, modality);
  if (!enrollment) {
    await logCloneAttempt({
      userId,
      kind: modality,
      provider: "DreamCo Clone (self-hosted)",
      status: "rejected_no_enrollment",
      prompt,
      consent: true,
      error: `no active ${modality} enrollment`,
      extra: params ?? {},
    });
    res.status(412).json({ error: `no active ${modality} enrollment — enroll your ${modality} first`, modality });
    return;
  }
  // Gate 3: the enrollment must carry a bindable sample reference. Cloning binds
  // strictly to this server-held reference — never to client-supplied input.
  if (!enrollment.sampleRef) {
    await logCloneAttempt({
      userId,
      kind: modality,
      provider: "DreamCo Clone (self-hosted)",
      status: "rejected_no_sample",
      prompt,
      consent: true,
      error: "enrollment has no bindable sample reference",
      extra: { ...(params ?? {}), enrollmentId: enrollment.id },
    });
    res.status(412).json({ error: `enrollment has no bindable sample — re-enroll your ${modality}`, modality });
    return;
  }

  const cap = getCloneCapability(modality as CloneModality);
  const mediaKind = modality === "voice" ? "voice" : "image";

  // Gate 3: engine connected. If not, record the honest attempt and 503.
  if (cap.status !== "live") {
    const [job] = await db
      .insert(mediaJobsTable)
      .values({ userId, kind: mediaKind, provider: cap.provider, status: "needs_config", prompt, params: { ...(params ?? {}), clone: true, enrollmentId: enrollment.id }, consent: true, error: cap.note })
      .returning();
    res.status(503).json({ status: "needs_config", capability: cap, job });
    return;
  }

  const [job] = await db
    .insert(mediaJobsTable)
    .values({ userId, kind: mediaKind, provider: cap.provider, status: "running", prompt, params: { ...(params ?? {}), clone: true, enrollmentId: enrollment.id }, consent: true })
    .returning();

  try {
    const result = await generateClone(modality as CloneModality, prompt, enrollment.sampleRef, params ?? {});
    const [updated] = await db
      .update(mediaJobsTable)
      .set({ status: "succeeded", provider: result.provider, resultUrl: result.resultUrl, params: { ...(params ?? {}), clone: true, enrollmentId: enrollment.id, ...(result.meta ?? {}) } })
      .where(eq(mediaJobsTable.id, job!.id))
      .returning();
    res.json({ status: "succeeded", job: updated });
  } catch (err) {
    const isNeedsKey = err instanceof NeedsKeyError;
    const message = err instanceof Error ? err.message : "clone failed";
    const [updated] = await db
      .update(mediaJobsTable)
      .set({ status: isNeedsKey ? "needs_config" : "failed", error: message })
      .where(eq(mediaJobsTable.id, job!.id))
      .returning();
    req.log.error({ err, modality }, "clone generation failed");
    res.status(isNeedsKey ? 503 : 502).json({ status: isNeedsKey ? "needs_config" : "failed", error: message, job: updated });
  }
});

export default router;
