import { z } from "zod";

export const WORKSHOP_KINDS = [
  "movie",
  "series",
  "business",
  "app",
  "website",
  "sales",
  "marketing",
  "research",
  "data",
  "automation",
  "company_buddy",
  "personal_productivity",
] as const;

export const workshopButtonSchema = z.object({
  id: z.string().trim().regex(/^[a-z][a-z0-9_-]{1,80}$/),
  label: z.string().trim().min(2).max(80),
  userJob: z.string().trim().min(3).max(240),
  actionType: z.enum(["plan", "generate", "analyze", "simulate", "test", "connect", "publish", "deploy", "execute", "review"]),
  highImpact: z.boolean().default(false),
  requiresApproval: z.boolean().default(false),
  benchmarkSuiteIds: z.array(z.string().trim().min(2).max(120)).default([]),
}).strict();

export const workshopStageSchema = z.object({
  id: z.string().trim().regex(/^[a-z][a-z0-9_-]{1,80}$/),
  label: z.string().trim().min(2).max(80),
  objective: z.string().trim().min(5).max(500),
  buttons: z.array(workshopButtonSchema).min(1).max(40),
}).strict();

export const workshopDefinitionSchema = z.object({
  schema: z.literal("dreamco.workshop.v1"),
  id: z.string().trim().regex(/^[a-z][a-z0-9_-]{1,80}$/),
  kind: z.enum(WORKSHOP_KINDS),
  title: z.string().trim().min(2).max(120),
  description: z.string().trim().min(10).max(800),
  defaultDivision: z.string().trim().min(2).max(120),
  stages: z.array(workshopStageSchema).min(1).max(30),
  publishTargets: z.array(z.string().trim().min(2).max(120)).max(50).default([]),
  connectorRequirements: z.array(z.string().trim().min(2).max(120)).max(50).default([]),
  evidenceRequiredForCompletion: z.boolean().default(true),
}).strict();

export type WorkshopDefinition = z.infer<typeof workshopDefinitionSchema>;
