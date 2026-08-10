import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { z } from "zod";

type TraitDefinition = { id: string; label: string; default: number };
type ContextDefinition = { slang_allowed: boolean; trait_floors?: Record<string, number> };
type ConversationModel = { response_sequence: string[]; competencies: string[]; anti_patterns: string[] };
type PsychologyKnowledgeBoundary = { education_domains: string[]; allowed_uses: string[]; forbidden_uses: string[] };
type CommunicationCatalog = {
  schema: string;
  reviewed_on: string;
  policy: Record<string, boolean>;
  trait_groups: Array<{ id: string; label: string; traits: TraitDefinition[] }>;
  self_report_dimensions: Array<{ id: string; label: string; default: null }>;
  contexts: Record<string, ContextDefinition>;
  conversation_model: ConversationModel;
  explicit_cue_guidance: Record<string, string[]>;
  psychology_knowledge_boundary: PsychologyKnowledgeBoundary;
  relationship_integrity: Record<string, boolean>;
  grounding_behavior: Record<string, boolean | string[]>;
  benchmark_suites: Array<{ id: string; metrics: string[] }>;
  fixture_policy: Record<string, boolean | number>;
};

const catalog = JSON.parse(
  readFileSync(resolve(process.cwd(), "config", "buddy-communication-behavior.json"), "utf8"),
) as CommunicationCatalog;

const traitDefinitions = catalog.trait_groups.flatMap((group) => group.traits);
const traitIds = new Set(traitDefinitions.map((trait) => trait.id));
const selfReportIds = new Set(catalog.self_report_dimensions.map((trait) => trait.id));
const contextIds = Object.keys(catalog.contexts) as [string, ...string[]];
const cueIds = Object.keys(catalog.explicit_cue_guidance) as [string, ...string[]];

const unitRecordSchema = z.record(z.string(), z.number().min(0).max(1));
const defaultCommunicationProfile = {
  traits: {},
  selfReportDimensions: {},
  adaptSlang: true,
  voiceCueAdaptation: false,
  voiceCueConsent: false,
  retainBehaviorHistory: false,
};

export const communicationProfileSchema = z.object({
  traits: unitRecordSchema.default({}),
  selfReportDimensions: unitRecordSchema.default({}),
  adaptSlang: z.boolean().default(true),
  voiceCueAdaptation: z.boolean().default(false),
  voiceCueConsent: z.boolean().default(false),
  retainBehaviorHistory: z.boolean().default(false),
}).strict().superRefine((profile, context) => {
  for (const id of Object.keys(profile.traits)) {
    if (!traitIds.has(id)) context.addIssue({ code: z.ZodIssueCode.custom, message: `Unsupported communication trait: ${id}`, path: ["traits", id] });
  }
  for (const id of Object.keys(profile.selfReportDimensions)) {
    if (!selfReportIds.has(id)) context.addIssue({ code: z.ZodIssueCode.custom, message: `Unsupported self-report dimension: ${id}`, path: ["selfReportDimensions", id] });
  }
  if (profile.voiceCueAdaptation && !profile.voiceCueConsent) {
    context.addIssue({ code: z.ZodIssueCode.custom, message: "Voice-cue adaptation requires explicit opt-in.", path: ["voiceCueConsent"] });
  }
});

export const communicationPlanRequestSchema = z.object({
  objective: z.string().trim().min(3).max(4000),
  context: z.enum(contextIds).default("casual"),
  profile: communicationProfileSchema.default(defaultCommunicationProfile),
  ownerConfirmedCue: z.enum(cueIds).optional(),
}).strict();

export const communicationBenchmarkRequestSchema = z.object({
  suiteIds: z.array(z.string().trim().max(80)).min(1).max(catalog.benchmark_suites.length),
  targetProfileIds: z.array(z.string().trim().max(80)).min(1).max(12),
  syntheticFixturesOnly: z.literal(true),
  repetitionsPerFixture: z.number().int().min(3).max(20).default(3),
  retainRawConversations: z.literal(false),
}).strict();

function defaultTraits(): Record<string, number> {
  return Object.fromEntries(traitDefinitions.map((trait) => [trait.id, trait.default]));
}

function validateNoClinicalObjective(objective: string): void {
  if (/\b(diagnose|diagnosis|psychological profile for hiring|mental health score|personality disorder)\b/i.test(objective)) {
    throw new Error("Buddy communication profiles cannot diagnose, score mental health, or decide eligibility.");
  }
}

export function buildCommunicationPlan(request: z.infer<typeof communicationPlanRequestSchema>) {
  validateNoClinicalObjective(request.objective);
  const context = catalog.contexts[request.context];
  const traits: Record<string, number> = { ...defaultTraits(), ...request.profile.traits };
  for (const [id, floor] of Object.entries(context.trait_floors ?? {})) {
    traits[id] = Math.max(traits[id] ?? 0, floor);
  }
  const professional = !["casual", "creative"].includes(request.context);
  return {
    schema: "dreamco.buddy_communication_plan.v1",
    status: "communication_profile_ready",
    context: request.context,
    profile: {
      traits,
      selfReportDimensions: request.profile.selfReportDimensions,
      selfReportOnly: true,
      slangAllowed: context.slang_allowed && request.profile.adaptSlang && !professional,
      professionalOverride: professional,
    },
    cueAdaptation: {
      enabled: request.profile.voiceCueAdaptation && request.profile.voiceCueConsent,
      ownerConfirmedCue: request.ownerConfirmedCue ?? null,
      guidance: request.profile.voiceCueAdaptation && request.profile.voiceCueConsent && request.ownerConfirmedCue
        ? catalog.explicit_cue_guidance[request.ownerConfirmedCue]
        : [],
      inferredMentalState: false,
      diagnosisPerformed: false,
      rawVoiceStored: false,
    },
    memory: {
      behaviorHistoryRetained: request.profile.retainBehaviorHistory,
      rawConversationRetained: false,
      usefulPreferenceSummaryOnly: request.profile.retainBehaviorHistory,
    },
    boundaries: {
      hiddenPsychologicalInference: false,
      sensitiveTraitInference: false,
      clinicalUse: false,
      highImpactDecisionUse: false,
      userCanEditOrResetProfile: true,
    },
    conversationModel: catalog.conversation_model,
    psychologyKnowledgeBoundary: catalog.psychology_knowledge_boundary,
    relationshipIntegrity: catalog.relationship_integrity,
    groundingBehavior: catalog.grounding_behavior,
  };
}

export function buildCommunicationBenchmarkPlan(request: z.infer<typeof communicationBenchmarkRequestSchema>) {
  const suites = request.suiteIds.map((id) => catalog.benchmark_suites.find((suite) => suite.id === id));
  if (suites.some((suite) => !suite)) throw new Error("Every communication benchmark suite must exist in the catalog.");
  return {
    schema: "dreamco.buddy_communication_benchmark_plan.v1",
    status: "sandbox_plan_ready",
    targets: request.targetProfileIds,
    suites,
    fixtures: {
      syntheticOnly: true,
      repetitionsPerFixture: request.repetitionsPerFixture,
      protectedClassScoring: false,
      clinicalScoring: false,
      highImpactEligibilityScoring: false,
    },
    storage: {
      rawConversationsRetained: false,
      aggregateMetricsOnly: true,
      ownerDeletionSupported: true,
    },
    resultState: "not_run",
    superiorityClaimAllowed: false,
  };
}

export function getCommunicationBehaviorCatalog() {
  return catalog;
}
