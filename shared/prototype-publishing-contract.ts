import { z } from "zod";

export const PROTOTYPE_KINDS = ["mobile_app","web_app","website","desktop_app","api","automation","ai_agent","hardware_invention","iot_device","robotics","consumer_product","industrial_product","media_project","game","other"] as const;
export const PROTOTYPE_STATES = ["idea","spec","mockup","prototype","validated","release_candidate","published","archived"] as const;

export const prototypeArtifactSchema = z.object({
  artifactId: z.string().trim().min(2).max(160),
  kind: z.enum(["code","design","cad","schematic","bom","test_result","video","image","document","binary","dataset","other"]),
  pathOrReference: z.string().trim().min(2).max(1024),
  generatedBy: z.string().trim().min(2).max(160),
  verified: z.boolean().default(false),
}).strict();

export const prototypeProjectSchema = z.object({
  schema: z.literal("dreamco.prototype_project.v1"),
  projectId: z.string().trim().min(2).max(160),
  ownerOrTenantId: z.string().trim().min(2).max(160),
  title: z.string().trim().min(2).max(240),
  kind: z.enum(PROTOTYPE_KINDS),
  state: z.enum(PROTOTYPE_STATES).default("idea"),
  goal: z.string().trim().min(5).max(4000),
  targetUsers: z.array(z.string().trim().min(2).max(240)).max(100).default([]),
  requirements: z.array(z.string().trim().min(2).max(1000)).max(500).default([]),
  artifacts: z.array(prototypeArtifactSchema).max(5000).default([]),
  deploymentRequired: z.boolean().default(false),
  publishTargets: z.array(z.enum(["apple_app_store","google_play","web","github_release","cloud","enterprise_catalog","amazon_appstore","microsoft_store","other"])).max(30).default([]),
  verificationProfileId: z.string().trim().min(2).max(160).nullable().default(null),
}).strict();

export const publishGateSchema = z.object({
  schema: z.literal("dreamco.publish_gate.v1"),
  projectId: z.string().trim().min(2).max(160),
  target: z.string().trim().min(2).max(160),
  requiredChecks: z.array(z.string().trim().min(2).max(160)).min(1).max(500),
  passedChecks: z.array(z.string().trim().min(2).max(160)).max(500).default([]),
  credentialsConfigured: z.boolean().default(false),
  userApprovalRequired: z.boolean().default(true),
  userApproved: z.boolean().default(false),
}).strict();

export function canPublish(input: z.infer<typeof publishGateSchema>) {
  const passed = new Set(input.passedChecks);
  const missingChecks = input.requiredChecks.filter(check => !passed.has(check));
  if (missingChecks.length) return { allowed: false, reason: "verification_incomplete", missingChecks } as const;
  if (!input.credentialsConfigured) return { allowed: false, reason: "credentials_not_configured", missingChecks: [] } as const;
  if (input.userApprovalRequired && !input.userApproved) return { allowed: false, reason: "user_approval_required", missingChecks: [] } as const;
  return { allowed: true, reason: "publish_ready", missingChecks: [] } as const;
}
