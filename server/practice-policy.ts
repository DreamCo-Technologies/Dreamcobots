import { randomUUID } from "node:crypto";

import { z } from "zod";

export const PRACTICE_MODES = [
  "job_interview",
  "career_plan",
  "sales_call",
  "customer_support",
  "manager_conversation",
  "negotiation",
  "presentation",
  "audition",
  "language_practice",
] as const;

const SPECIALISTS: Record<(typeof PRACTICE_MODES)[number], string[]> = {
  job_interview: ["resume-builder-bot", "job-application-bot", "buddy-bot"],
  career_plan: ["resume-builder-bot", "job-application-bot", "mos-career-planner"],
  sales_call: ["objection-handler-ai", "pitch-craft-ai", "buddy-bot"],
  customer_support: ["review-manager", "case-manager", "buddy-bot"],
  manager_conversation: ["project-management", "change-manager", "buddy-bot"],
  negotiation: ["cultural-intel", "contractual-risk-sim", "partnership-leverage"],
  presentation: ["pitch-deck", "pitch-craft-ai", "buddy-bot"],
  audition: ["animation-pipeline", "music-production", "buddy-bot"],
  language_practice: ["localization", "cultural-intel", "buddy-bot"],
};

export const practiceSessionRequestSchema = z.object({
  mode: z.enum(PRACTICE_MODES),
  targetRole: z.string().trim().min(2).max(160),
  context: z.string().trim().min(10).max(1_500),
  goals: z.array(z.string().trim().min(2).max(240)).min(1).max(8),
  difficulty: z.enum(["supportive", "realistic", "challenging"]),
  rounds: z.number().int().min(1).max(12),
  answerMode: z.enum(["text", "voice", "text_and_voice"]),
  useOwnerVoice: z.boolean().default(false),
  adultVoiceRightsConfirmed: z.boolean().default(false),
  candidatePracticeOnly: z.boolean().default(true),
}).strict();

export function createPracticeSessionPlan(input: z.infer<typeof practiceSessionRequestSchema>) {
  const request = practiceSessionRequestSchema.parse(input);
  if (request.useOwnerVoice && !request.adultVoiceRightsConfirmed) {
    throw new Error("Owner voice practice requires adult subject rights confirmation.");
  }
  if (["job_interview", "career_plan"].includes(request.mode) && !request.candidatePracticeOnly) {
    throw new Error("Job preparation cannot impersonate a candidate in a real interview or assessment.");
  }
  return {
    schema: "dreamco.buddy_practice_session_plan.v1",
    sessionId: `practice-${randomUUID()}`,
    status: "private_sandbox_ready",
    mode: request.mode,
    targetRole: request.targetRole,
    context: request.context,
    goals: [...new Set(request.goals)],
    difficulty: request.difficulty,
    rounds: request.rounds,
    answerMode: request.answerMode,
    specialistSlugs: SPECIALISTS[request.mode],
    reviewDimensions: [
      "clear objective",
      "specific evidence",
      "structured answer",
      "active listening",
      "honest uncertainty",
      "professional boundaries",
      "concise delivery",
      "useful next step",
    ],
    controls: {
      privatePracticeOnly: true,
      candidateImpersonationAllowed: false,
      automatedEmploymentDecisionAllowed: false,
      protectedTraitInferenceAllowed: false,
      fabricatedCredentialAllowed: false,
      rawVoiceStoredInPlan: false,
      exactApprovalBeforeExternalAction: true,
      liveExternalActionTaken: false,
    },
  } as const;
}
