import { randomUUID } from "node:crypto";
import { and, desc, eq, sql } from "drizzle-orm";
import { z } from "zod";
import { db } from "./db";
import { leadEngineActivities, leadEngineRecords } from "@shared/schema";
import {
  assertLeadStageTransition,
  buildLeadStagePlan,
  hasCurrentLeadConsent,
  leadEngineRecordSchema,
  qualifyLead,
  type LeadEngineRecord,
} from "./lead-engine";

const ownerIdSchema = z.string().trim().min(2).max(80).regex(/^[A-Za-z0-9_.:-]+$/);
const activitySchema = z.object({
  eventId: z.string().regex(/^lead-event-[A-Za-z0-9-]{6,80}$/),
  eventType: z.enum([
    "lead_created",
    "stage_changed",
    "qualification_updated",
    "consent_updated",
    "suppression_changed",
    "owner_note",
    "proposal_handoff",
    "conversion_recorded",
  ]),
  details: z.record(z.string(), z.union([
    z.string().max(500).refine(
      (value) => !/(?:[\\w.+-]+@[\\w.-]+\\.[A-Za-z]{2,}|\\+?\\d[\\d\\s().-]{7,}\\d|github_pat_|ghs_|sk_(?:live|test)_)/i.test(value),
      "Activity details must not contain contact details or credentials",
    ),
    z.number().finite(),
    z.boolean(),
  ])).default({}),
}).strict();

export type LeadEngineActivityInput = z.infer<typeof activitySchema>;

function assertOwnerRecord(ownerId: string, record: LeadEngineRecord) {
  const parsedOwner = ownerIdSchema.parse(ownerId);
  const parsedRecord = leadEngineRecordSchema.parse(record);
  if (parsedRecord.ownerUserId !== parsedOwner) {
    throw new Error("lead_engine_owner_mismatch");
  }
  return { ownerId: parsedOwner, record: parsedRecord };
}

type LeadEngineTx = Parameters<Parameters<typeof db.transaction>[0]>[0];

/**
 * Every database operation runs in a transaction that sets a transaction-local
 * owner context. PostgreSQL RLS is the final isolation boundary; caller code
 * must obtain ownerId from an authenticated identity, never request JSON.
 */
async function withOwner<T>(ownerId: string, operation: (tx: LeadEngineTx) => Promise<T>): Promise<T> {
  const safeOwnerId = ownerIdSchema.parse(ownerId);
  return db.transaction(async (tx) => {
    await tx.execute(
      // SET LOCAL equivalent: automatically cleared when this transaction ends.
      sql`select set_config('app.owner_id', ${safeOwnerId}, true)`,
    );
    return operation(tx);
  });
}

export async function saveLeadEngineRecord(ownerId: string, input: LeadEngineRecord) {
  const { ownerId: safeOwnerId, record } = assertOwnerRecord(ownerId, input);
  return withOwner(safeOwnerId, async (tx) => {
    const [existing] = await tx.select()
      .from(leadEngineRecords)
      .where(and(
        eq(leadEngineRecords.ownerId, safeOwnerId),
        eq(leadEngineRecords.leadId, record.leadId),
      ))
      .limit(1);

    const previous = existing ? leadEngineRecordSchema.parse(existing.payload) : undefined;
    const validatedRecord = assertLeadStageTransition(previous, record);
    const validatedQualification = qualifyLead(validatedRecord);
    const validatedStagePlan = buildLeadStagePlan(validatedRecord);

    if (validatedRecord.stage === "convert" && previous?.stage !== "convert") {
      const [approval] = await tx.select({ id: leadEngineActivities.id })
        .from(leadEngineActivities)
        .where(and(
          eq(leadEngineActivities.ownerId, safeOwnerId),
          eq(leadEngineActivities.leadId, validatedRecord.leadId),
          eq(leadEngineActivities.eventId, validatedRecord.humanReviewEvidenceRef!),
          eq(leadEngineActivities.eventType, "conversion_approved"),
        ))
        .limit(1);
      if (!approval) throw new Error("lead_engine_conversion_approval_evidence_missing");
    }

    const [saved] = await tx.insert(leadEngineRecords).values({
      ownerId: safeOwnerId,
      leadId: validatedRecord.leadId,
      organizationName: validatedRecord.organizationName,
      stage: validatedRecord.stage,
      qualificationScore: validatedQualification.score,
      qualificationTier: validatedQualification.tier,
      suppressionStatus: validatedRecord.suppressionStatus,
      payload: validatedRecord,
    }).onConflictDoUpdate({
      target: [leadEngineRecords.ownerId, leadEngineRecords.leadId],
      set: {
        organizationName: validatedRecord.organizationName,
        stage: validatedRecord.stage,
        qualificationScore: validatedQualification.score,
        qualificationTier: validatedQualification.tier,
        suppressionStatus: validatedRecord.suppressionStatus,
        payload: validatedRecord,
        updatedAt: new Date(),
      },
    }).returning();

    let auditEventType: "lead_created" | "stage_changed" | "qualification_updated" | "consent_updated" | "suppression_changed" | undefined;
    let auditDetails: Record<string, string | number | boolean> = {};
    if (!previous) {
      auditEventType = "lead_created";
      auditDetails = { stage: validatedRecord.stage, qualificationScore: validatedQualification.score };
    } else if (previous.suppressionStatus !== validatedRecord.suppressionStatus) {
      auditEventType = "suppression_changed";
      auditDetails = { from: previous.suppressionStatus, to: validatedRecord.suppressionStatus };
    } else if (
      previous.consentEvidenceRef !== validatedRecord.consentEvidenceRef ||
      previous.consentObtainedAt !== validatedRecord.consentObtainedAt ||
      previous.consentExpiresAt !== validatedRecord.consentExpiresAt
    ) {
      auditEventType = "consent_updated";
      auditDetails = { consentEvidenceUpdated: true };
    } else if (previous.stage !== validatedRecord.stage) {
      auditEventType = "stage_changed";
      auditDetails = { fromStage: previous.stage, toStage: validatedRecord.stage };
    } else {
      const previousScore = qualifyLead(previous).score;
      if (previousScore !== validatedQualification.score) {
        auditEventType = "qualification_updated";
        auditDetails = { previousScore, qualificationScore: validatedQualification.score };
      }
    }

    if (auditEventType) {
      await tx.insert(leadEngineActivities).values({
        ownerId: safeOwnerId,
        leadId: validatedRecord.leadId,
        eventId: `lead-event-${randomUUID()}`,
        eventType: auditEventType,
        details: auditDetails,
      });
    }

    return { record: saved, qualification: validatedQualification, stagePlan: validatedStagePlan };
  });
}

/**
 * Records an explicit authenticated-owner approval for a qualified conversion.
 * The returned evidence reference is verified again by saveLeadEngineRecord
 * before a record may enter the convert stage.
 */
export async function approveLeadConversion(ownerId: string, leadId: string) {
  const safeOwnerId = ownerIdSchema.parse(ownerId);
  const safeLeadId = z.string().regex(/^lead-[A-Za-z0-9-]{4,80}$/).parse(leadId);

  return withOwner(safeOwnerId, async (tx) => {
    const [row] = await tx.select().from(leadEngineRecords).where(and(
      eq(leadEngineRecords.ownerId, safeOwnerId),
      eq(leadEngineRecords.leadId, safeLeadId),
    )).limit(1);
    if (!row) throw new Error("lead_engine_record_not_found");

    const lead = leadEngineRecordSchema.parse(row.payload);
    const qualification = qualifyLead(lead);
    if (
      lead.stage !== "nurture" ||
      qualification.tier !== "hot" ||
      !lead.budgetConfirmed ||
      !lead.useCase ||
      !hasCurrentLeadConsent(lead) ||
      lead.suppressionStatus !== "active"
    ) {
      throw new Error("lead_engine_conversion_not_eligible_for_owner_approval");
    }

    const evidenceRef = `lead-event-${randomUUID()}`;
    await tx.insert(leadEngineActivities).values({
      ownerId: safeOwnerId,
      leadId: safeLeadId,
      eventId: evidenceRef,
      eventType: "conversion_approved",
      details: {
        approval: "explicit_owner_approval",
        ownerId: safeOwnerId,
        qualificationScore: qualification.score,
        policy: "lead_engine_conversion_gate_v1",
      },
    });
    return {
      approved: true as const,
      leadId: safeLeadId,
      evidenceRef,
      qualificationScore: qualification.score,
      approvalRequiredAgainForEachNewLead: true as const,
    };
  });
}

export async function getLeadEngineRecord(ownerId: string, leadId: string) {
  const safeOwnerId = ownerIdSchema.parse(ownerId);
  const safeLeadId = z.string().regex(/^lead-[A-Za-z0-9-]{4,80}$/).parse(leadId);
  return withOwner(safeOwnerId, async (tx) => {
    const [record] = await tx.select().from(leadEngineRecords).where(and(
      eq(leadEngineRecords.ownerId, safeOwnerId),
      eq(leadEngineRecords.leadId, safeLeadId),
    )).limit(1);
    return record;
  });
}

export async function listLeadEngineRecords(ownerId: string, limit = 100) {
  const safeOwnerId = ownerIdSchema.parse(ownerId);
  const safeLimit = z.number().int().min(1).max(250).parse(limit);
  return withOwner(safeOwnerId, async (tx) => tx.select().from(leadEngineRecords)
    .where(eq(leadEngineRecords.ownerId, safeOwnerId))
    .orderBy(desc(leadEngineRecords.updatedAt))
    .limit(safeLimit));
}

export async function appendLeadEngineActivity(
  ownerId: string,
  leadId: string,
  input: LeadEngineActivityInput,
) {
  const safeOwnerId = ownerIdSchema.parse(ownerId);
  const safeLeadId = z.string().regex(/^lead-[A-Za-z0-9-]{4,80}$/).parse(leadId);
  const activity = activitySchema.parse(input);

  return withOwner(safeOwnerId, async (tx) => {
    const [lead] = await tx.select({ id: leadEngineRecords.id })
      .from(leadEngineRecords)
      .where(and(
        eq(leadEngineRecords.ownerId, safeOwnerId),
        eq(leadEngineRecords.leadId, safeLeadId),
      ))
      .limit(1);
    if (!lead) throw new Error("lead_engine_record_not_found");

    const [created] = await tx.insert(leadEngineActivities).values({
      ownerId: safeOwnerId,
      leadId: safeLeadId,
      eventId: activity.eventId,
      eventType: activity.eventType,
      details: activity.details,
    }).onConflictDoNothing({
      target: [leadEngineActivities.ownerId, leadEngineActivities.eventId],
    }).returning();

    if (created) return created;
    const [duplicate] = await tx.select().from(leadEngineActivities).where(and(
      eq(leadEngineActivities.ownerId, safeOwnerId),
      eq(leadEngineActivities.eventId, activity.eventId),
    )).limit(1);
    return duplicate;
  });
}

export async function listLeadEngineActivities(ownerId: string, leadId: string, limit = 100) {
  const safeOwnerId = ownerIdSchema.parse(ownerId);
  const safeLeadId = z.string().regex(/^lead-[A-Za-z0-9-]{4,80}$/).parse(leadId);
  const safeLimit = z.number().int().min(1).max(250).parse(limit);
  return withOwner(safeOwnerId, async (tx) => tx.select().from(leadEngineActivities)
    .where(and(
      eq(leadEngineActivities.ownerId, safeOwnerId),
      eq(leadEngineActivities.leadId, safeLeadId),
    ))
    .orderBy(desc(leadEngineActivities.createdAt))
    .limit(safeLimit));
}
