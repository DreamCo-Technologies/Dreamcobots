import { z } from "zod";

export const SALES_TRAINING_SKILLS = [
  "product_knowledge","industry_knowledge","prospecting","research","cold_calling","cold_email","social_selling","discovery","qualification","active_listening","rapport","presentation","demo","storytelling","value_selling","roi_selling","objection_handling","negotiation","closing","follow_up","crm_hygiene","pipeline_management","forecasting","account_management","upsell","cross_sell","customer_success","compliance","time_management","call_control","question_quality","confidence","clarity","empathy","adaptability"
] as const;

export const salesRepScoreSchema = z.object({
  skill: z.enum(SALES_TRAINING_SKILLS),
  score: z.number().min(0).max(100),
  evidenceCount: z.number().int().min(0),
  trend: z.enum(["improving","flat","declining","unknown"]),
  lastEvaluatedAt: z.string().datetime().nullable().default(null),
}).strict();

export const salesPracticeSessionSchema = z.object({
  sessionId: z.string().trim().min(3).max(160),
  scenario: z.string().trim().min(10).max(2000),
  difficulty: z.number().int().min(1).max(10),
  buyerPersona: z.string().trim().min(3).max(500),
  objections: z.array(z.string().trim().min(3).max(500)).max(50).default([]),
  targetSkills: z.array(z.enum(SALES_TRAINING_SKILLS)).min(1),
  transcriptReference: z.string().trim().max(1024).nullable().default(null),
  scores: z.array(salesRepScoreSchema).default([]),
  coachFeedback: z.array(z.string().trim().min(3).max(1000)).default([]),
  nextDrills: z.array(z.string().trim().min(3).max(500)).default([]),
}).strict();

export const humanSalesRepProfileSchema = z.object({
  schema: z.literal("dreamco.human_sales_rep.v1"),
  repId: z.string().trim().min(3).max(160),
  displayName: z.string().trim().min(2).max(160),
  teamId: z.string().trim().min(2).max(160),
  role: z.enum(["sdr","bdr","account_executive","account_manager","customer_success","sales_manager","sales_engineer","founder_seller","other"]),
  productsOrBotsSold: z.array(z.string().trim().min(2).max(160)).max(500).default([]),
  scores: z.array(salesRepScoreSchema).default([]),
  trainingPlan: z.array(z.object({
    skill: z.enum(SALES_TRAINING_SKILLS),
    targetScore: z.number().min(0).max(100),
    drills: z.array(z.string().trim().min(3).max(500)).min(1).max(50),
    benchmarkSuiteIds: z.array(z.string().trim().min(2).max(160)).default([]),
  }).strict()).default([]),
  performance: z.object({
    activities: z.number().int().min(0).default(0),
    conversations: z.number().int().min(0).default(0),
    qualifiedMeetings: z.number().int().min(0).default(0),
    proposals: z.number().int().min(0).default(0),
    closedWon: z.number().int().min(0).default(0),
    closedLost: z.number().int().min(0).default(0),
    revenueInfluencedUsd: z.number().min(0).default(0),
    averageSalesCycleDays: z.number().min(0).nullable().default(null),
    retentionRate: z.number().min(0).max(1).nullable().default(null),
  }).strict(),
  coaching: z.object({
    rolePlayEnabled: z.boolean().default(true),
    callReviewEnabled: z.boolean().default(true),
    objectionDrillsEnabled: z.boolean().default(true),
    personalizedDailyPractice: z.boolean().default(true),
    managerVisibility: z.boolean().default(true),
    repCanViewAllScores: z.boolean().default(true),
  }).strict(),
}).strict();

export function prioritizeSalesTraining(rep: z.infer<typeof humanSalesRepProfileSchema>) {
  return [...rep.scores]
    .sort((a, b) => a.score - b.score)
    .map((item) => ({ skill: item.skill, score: item.score, trend: item.trend }))
    .slice(0, 10);
}
