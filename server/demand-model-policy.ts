import { z } from "zod";

import {
  DEMAND_CATALOG_IDS,
  DEMAND_REASONS,
  DEMAND_RESEARCH_SOURCES,
} from "@shared/ai-demand-ontology";

import { selectBuddyModelsForTask } from "./buddy-model-policy";

export const demandModelMatchRequestSchema = z.object({
  reasonId: z.string().regex(/^(ai_usage|downloaded_apps|online_purchases)-\d{3}$/),
  preferredTier: z.enum(["free", "premium", "any"]).default("any"),
  approvePaidModelForThisRequest: z.boolean().default(false),
}).strict();

export type DemandModelMatchRequest = z.infer<typeof demandModelMatchRequestSchema>;

export function getDemandOntology() {
  return {
    schema: "dreamco.buddy_demand_ontology.v1",
    summary: {
      catalogs: DEMAND_CATALOG_IDS.length,
      reasons: DEMAND_REASONS.length,
      modelOptionsPerReason: 20,
      researchSources: DEMAND_RESEARCH_SOURCES.length,
    },
    researchSources: DEMAND_RESEARCH_SOURCES,
    reasons: DEMAND_REASONS,
  } as const;
}

export function matchDemandReasonToModels(
  input: z.input<typeof demandModelMatchRequestSchema>,
  environment: NodeJS.ProcessEnv = process.env,
) {
  const request = demandModelMatchRequestSchema.parse(input);
  const reason = DEMAND_REASONS.find((candidate) => candidate.id === request.reasonId);
  if (!reason) throw new Error(`Unknown demand reason: ${request.reasonId}`);
  const selection = selectBuddyModelsForTask({
    objective: `${reason.reason}. Task category: ${reason.taskCategory}.`,
    requiredCapabilities: reason.capabilities,
    preferredTier: request.preferredTier,
    priorities: { quality: 0.8, cost: 0.7, latency: 0.5, privacy: 0.7 },
    maxCandidates: 20,
    allowDiscovery: true,
    approvePaidModelForThisRequest: request.approvePaidModelForThisRequest,
  }, environment);
  return {
    schema: "dreamco.buddy_demand_model_choices.v1",
    reason,
    optionCount: selection.candidates.length,
    requestedOptionCount: 20,
    modelOptions: selection.candidates,
    selectedModelTargetId: null,
    userChoiceRequired: true,
    providerCallExecuted: false,
    paymentAuthorized: false,
    selectionTruth: selection.truthContract,
  } as const;
}
