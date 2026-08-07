import { z } from "zod";

export const SALES_TEAM_ROLES = [
  "market_researcher","icp_builder","lead_researcher","prospector","outreach_writer","appointment_setter","discovery_rep","solution_consultant","demo_specialist","proposal_builder","roi_analyst","objection_handler","negotiator","closer","follow_up_rep","customer_success","expansion_rep","sales_manager","revenue_analyst","compliance_reviewer"
] as const;

export const salesChannelSchema = z.object({
  channel: z.enum(["email","phone","sms","linkedin","website_chat","social_dm","marketplace","in_person","webinar","video","partner","referral","other"]),
  enabled: z.boolean().default(false),
  adapterId: z.string().trim().max(160).nullable().default(null),
  freshApprovalRequired: z.boolean().default(true),
  platformPolicyCheckRequired: z.boolean().default(true),
}).strict();

export const botOfferSchema = z.object({
  offerId: z.string().trim().min(2).max(160),
  name: z.string().trim().min(2).max(200),
  problemSolved: z.string().trim().min(10).max(1500),
  idealCustomer: z.string().trim().min(5).max(1500),
  measurableOutcomes: z.array(z.string().trim().min(3).max(500)).min(1).max(50),
  proofPoints: z.array(z.string().trim().min(3).max(500)).max(100).default([]),
  pricingModel: z.string().trim().min(2).max(500),
  disqualifiers: z.array(z.string().trim().min(3).max(500)).max(50).default([]),
}).strict();

export const botSalesBenchmarkSchema = z.object({
  metricId: z.string().trim().min(2).max(160),
  label: z.string().trim().min(2).max(200),
  category: z.enum(["research","lead_quality","outreach","qualification","discovery","demo","proposal","objection","close","retention","expansion","compliance","roi"]),
  targetDirection: z.enum(["higher","lower","range"]),
  targetValue: z.number().finite().nullable().default(null),
  minimumPassingScore: z.number().min(0).max(100),
  evidenceRequired: z.boolean().default(true),
}).strict();

export const botSalesTeamSchema = z.object({
  schema: z.literal("dreamco.bot_sales_team.v1"),
  botSlug: z.string().trim().min(2).max(160),
  division: z.string().trim().min(2).max(160),
  category: z.string().trim().min(2).max(160),
  roles: z.array(z.enum(SALES_TEAM_ROLES)).min(5).max(SALES_TEAM_ROLES.length),
  offers: z.array(botOfferSchema).min(1).max(100),
  channels: z.array(salesChannelSchema).min(1).max(20),
  benchmarkSuite: z.array(botSalesBenchmarkSchema).min(5).max(200),
  learningLoop: z.object({
    learnFromWins: z.boolean().default(true),
    learnFromLosses: z.boolean().default(true),
    captureObjections: z.boolean().default(true),
    updateIcpFromOutcomes: z.boolean().default(true),
    updateMessagingFromExperiments: z.boolean().default(true),
    requireHumanReviewBeforeNewAutonomousOutboundPattern: z.boolean().default(true),
  }).strict(),
  controls: z.object({
    noDeceptiveClaims: z.literal(true),
    noFakeUrgency: z.literal(true),
    noUnauthorizedContacting: z.literal(true),
    respectOptOuts: z.literal(true),
    respectPlatformPolicies: z.literal(true),
    logEveryExternalAction: z.literal(true),
  }).strict(),
}).strict();

export const DEFAULT_BOT_SALES_METRICS = [
  ["research_accuracy","Research accuracy","research","higher",90],
  ["icp_fit","Ideal-customer fit","lead_quality","higher",85],
  ["lead_quality","Qualified lead quality","lead_quality","higher",80],
  ["reply_rate","Positive response rate","outreach","higher",70],
  ["meeting_rate","Qualified meeting rate","qualification","higher",70],
  ["discovery_quality","Discovery completeness","discovery","higher",85],
  ["demo_relevance","Demo relevance","demo","higher",85],
  ["proposal_quality","Proposal quality","proposal","higher",90],
  ["objection_quality","Objection handling","objection","higher",85],
  ["close_quality","Close quality","close","higher",80],
  ["roi_evidence","ROI evidence quality","roi","higher",90],
  ["retention_support","Retention support","retention","higher",80],
  ["expansion_fit","Expansion opportunity fit","expansion","higher",80],
  ["compliance","Sales compliance","compliance","higher",100]
] as const;
