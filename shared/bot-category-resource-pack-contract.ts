import { z } from "zod";

export const RESOURCE_TYPES = [
  "official_agency","association","directory","vendor","supplier","marketplace","funding","grant","loan","investor","accelerator","incubator","standards_body","education","research","licensing","insurance","legal_support","accounting","banking","logistics","import_export","government_contracting","community","professional_network","software","api","data_source","other"
] as const;

export const contactChannelSchema = z.object({
  type: z.enum(["website","phone","email","form","address","api","social","directory_profile","other"]),
  value: z.string().trim().min(2).max(1024),
  verifiedAt: z.string().datetime().nullable().default(null),
  officialSource: z.boolean().default(false),
}).strict();

export const categoryResourceSchema = z.object({
  resourceId: z.string().trim().min(2).max(160),
  name: z.string().trim().min(2).max(240),
  type: z.enum(RESOURCE_TYPES),
  categories: z.array(z.string().trim().min(2).max(160)).min(1).max(100),
  jurisdictions: z.array(z.string().trim().min(2).max(160)).max(100).default([]),
  purpose: z.string().trim().min(5).max(1500),
  contactChannels: z.array(contactChannelSchema).max(25).default([]),
  eligibilityOrRequirements: z.array(z.string().trim().min(2).max(500)).max(100).default([]),
  sourceReferences: z.array(z.string().trim().min(2).max(1024)).max(100).default([]),
  evidenceState: z.enum(["declared","official_verified","contact_verified","adapter_verified","deprecated"]).default("declared"),
  lastCheckedAt: z.string().datetime().nullable().default(null),
}).strict();

export const botCategoryResourcePackSchema = z.object({
  schema: z.literal("dreamco.bot_category_resource_pack.v1"),
  botSlug: z.string().trim().min(2).max(160),
  category: z.string().trim().min(2).max(160),
  professionOrIndustry: z.array(z.string().trim().min(2).max(160)).min(1).max(50),
  resources: z.array(categoryResourceSchema).max(5000).default([]),
  requiredResourceTypes: z.array(z.enum(RESOURCE_TYPES)).max(RESOURCE_TYPES.length).default([]),
  refreshPolicy: z.object({
    officialSourcesDays: z.number().int().min(1).max(365).default(30),
    businessContactsDays: z.number().int().min(1).max(365).default(90),
    fundingSourcesDays: z.number().int().min(1).max(365).default(14),
    marketplaceSourcesDays: z.number().int().min(1).max(365).default(30),
  }).strict(),
  controls: z.object({
    doNotInventContacts: z.literal(true),
    labelUnverifiedContacts: z.literal(true),
    respectContactPreferencesAndOptOuts: z.literal(true),
    requireApprovalBeforeOutboundContact: z.literal(true),
    useOfficialSourcesForRegulatoryClaims: z.literal(true),
  }).strict(),
}).strict();

export function resourceCoverage(pack: z.infer<typeof botCategoryResourcePackSchema>) {
  const present = new Set(pack.resources.map((resource) => resource.type));
  const missing = pack.requiredResourceTypes.filter((type) => !present.has(type));
  return {
    required: pack.requiredResourceTypes.length,
    covered: pack.requiredResourceTypes.length - missing.length,
    missing,
    complete: missing.length === 0,
  } as const;
}
