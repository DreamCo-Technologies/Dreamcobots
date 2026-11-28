import { and, desc, eq, sql } from "drizzle-orm";
import { z } from "zod";
import { db } from "./db";
import { leadEngineActivities, leadEngineRecords } from "@shared/schema";
import {
  LEAD_ENGINE_STAGES,
  buildLeadStagePlan,
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
  details: z.record(z.union([z.string().max(500), z.number().finite(), z.boolean()])).default({}),
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

function stageIndex(stage: LeadEngineRecord["stage"]) {
  return LEAD_ENGINE_STAGES.indexOf(stage);
}

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
  const qualification = qualifyLead(record);
  const stagePlan = buildLeadStagePlan(record);

  return withOwner(safeOwnerId, async (tx) => {
    const [existing] = await tx.select()
      .from(leadEngineRecords)
      .where(and(
        eq(leadEngineRecords.ownerId, safeOwnerId),
        eq(leadEngineRecords.leadId, record.leadId),
      ))
      .limit(1);

    if (existing && stageIndex(record.stage) < stageIndex(existing.stage as LeadEngineRecord["stage"])) {
      throw new Error("lead_engine_stage_regression_forbidden");
    }

    const [saved] = await tx.insert(leadEngineRecords).values({
      ownerId: safeOwnerId,
      leadId: record.leadId,
      organizationName: record.organizationName,
      stage: record.stage,
      qualificationScore: qualification.score,
      qualificationTier: qualification.tier,
      suppressionStatus: record.suppressionStatus,
      payload: record,
    }).onConflictDoUpdate({
      target: [leadEngineRecords.ownerId, leadEngineRecords.leadId],
      set: {
        organizationName: record.organizationName,
        stage: record.stage,
        qualificationScore: qualification.score,
        qualificationTier: qualification.tier,
        suppressionStatus: record.suppressionStatus,
        payload: record,
        updatedAt: new Date(),
      },
    }).returning();

    return { record: saved, qualification, stagePlan };
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
