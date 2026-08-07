import { z } from "zod";

export const VERIFICATION_LEVELS = ["contract","unit","integration","ui","build","security","performance","e2e","live"] as const;
export const VERIFICATION_STATES = ["passed","failed","skipped","blocked"] as const;

export const verificationExpectationSchema = z.object({
  id: z.string().trim().min(2).max(160),
  owner: z.string().trim().min(2).max(160),
  level: z.enum(VERIFICATION_LEVELS),
  description: z.string().trim().min(5).max(1000),
  command: z.string().trim().min(2).max(500),
  requiredForMerge: z.boolean().default(true),
  requiredForProduction: z.boolean().default(true),
  requiresCredentials: z.boolean().default(false),
  timeoutSeconds: z.number().int().min(1).max(7200).default(1200),
}).strict();

export const verificationResultSchema = z.object({
  expectationId: z.string().trim().min(2).max(160),
  state: z.enum(VERIFICATION_STATES),
  exitCode: z.number().int().nullable(),
  durationMs: z.number().int().min(0),
  summary: z.string().max(4000),
}).strict();

export const universalVerificationReportSchema = z.object({
  schema: z.literal("dreamco.universal_verification_report.v1"),
  startedAt: z.string().datetime(),
  completedAt: z.string().datetime(),
  mode: z.enum(["quick","ci","full","production"]),
  results: z.array(verificationResultSchema),
  totals: z.object({
    passed: z.number().int().min(0),
    failed: z.number().int().min(0),
    skipped: z.number().int().min(0),
    blocked: z.number().int().min(0),
  }).strict(),
  mergeReady: z.boolean(),
  productionReady: z.boolean(),
}).strict();

export type VerificationExpectation = z.infer<typeof verificationExpectationSchema>;
export type UniversalVerificationReport = z.infer<typeof universalVerificationReportSchema>;
