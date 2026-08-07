import { z } from "zod";

export const TRAINING_SOURCE_TYPES = [
  "chat_export",
  "document",
  "book",
  "video",
  "audio",
  "web",
  "github_repository",
  "knowledge_base",
  "database",
  "api",
  "email_export",
  "calendar_export",
  "notes",
  "user_feedback",
] as const;

export const personalBuddyTrainingSourceSchema = z.object({
  id: z.string().trim().regex(/^[A-Za-z0-9_.:/-]{2,160}$/),
  name: z.string().trim().min(2).max(200),
  type: z.enum(TRAINING_SOURCE_TYPES),
  sourceReference: z.string().trim().min(2).max(1024),
  ownerAuthorized: z.literal(true),
  rightsConfirmed: z.boolean().default(false),
  ingestionMode: z.enum(["reference_only", "index", "summarize", "extract_structured", "fine_tune_candidate"]).default("index"),
  refreshMode: z.enum(["manual", "scheduled", "webhook", "none"]).default("manual"),
  allowedUses: z.array(z.enum(["answering", "retrieval", "planning", "workflow_context", "evaluation", "personalization", "private_training"])).min(1).max(7),
  dataClass: z.enum(["public", "personal", "confidential", "restricted"]).default("personal"),
  retentionDays: z.number().int().min(1).max(3650).default(365),
  citationRequired: z.boolean().default(true),
}).strict();

export const personalBuddyProfileSchema = z.object({
  schema: z.literal("dreamco.personal_buddy.v1"),
  buddyId: z.string().trim().regex(/^[A-Za-z0-9_.:-]{3,120}$/),
  displayName: z.string().trim().min(2).max(120).default("Buddy"),
  ownerProfileId: z.string().trim().min(3).max(120),
  purpose: z.string().trim().min(10).max(2000),
  preferredStyle: z.object({
    directness: z.number().min(0).max(1).default(0.7),
    warmth: z.number().min(0).max(1).default(0.7),
    detail: z.number().min(0).max(1).default(0.6),
  }).strict(),
  trainingSources: z.array(personalBuddyTrainingSourceSchema).max(5000).default([]),
  capabilities: z.array(z.string().trim().min(2).max(160)).max(500).default([]),
  connectedApps: z.array(z.string().trim().min(2).max(160)).max(500).default([]),
  enrolledDevices: z.array(z.string().trim().min(2).max(160)).max(500).default([]),
  policies: z.object({
    externalWritesDisabledByDefault: z.boolean().default(true),
    freshApprovalForHighImpactActions: z.boolean().default(true),
    secretsByReferenceOnly: z.boolean().default(true),
    privateTrainingRequiresOptIn: z.boolean().default(true),
    userCanExportAndDeleteMemory: z.boolean().default(true),
    sourceProvenanceRequired: z.boolean().default(true),
  }).strict(),
}).strict();

export type PersonalBuddyProfile = z.infer<typeof personalBuddyProfileSchema>;

export function summarizeTrainingCoverage(profile: PersonalBuddyProfile) {
  const byType = Object.fromEntries(TRAINING_SOURCE_TYPES.map((type) => [type, 0])) as Record<string, number>;
  for (const source of profile.trainingSources) byType[source.type] += 1;
  return {
    buddyId: profile.buddyId,
    sourceCount: profile.trainingSources.length,
    byType,
    privateTrainingCandidateCount: profile.trainingSources.filter((source) => source.allowedUses.includes("private_training")).length,
  } as const;
}
