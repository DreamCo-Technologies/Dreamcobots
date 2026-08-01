import { z } from "zod";

import { MODEL_BENCHMARK_TARGETS } from "@shared/model-benchmark-targets";

export const MODEL_BENCHMARK_SUITE_IDS = [
  "instruction_following",
  "structured_output",
  "arithmetic_reasoning",
  "code_generation",
  "code_repair",
  "long_context_retrieval",
  "grounded_research",
  "tool_selection",
  "safety_boundary",
  "multilingual",
  "vision_understanding",
  "audio_understanding",
] as const;

export const modelBenchmarkPlanRequestSchema = z.object({
  targetIds: z.array(z.number().int().min(1).max(10_000)).min(1).max(200),
  suiteIds: z.array(z.enum(MODEL_BENCHMARK_SUITE_IDS)).min(1).max(MODEL_BENCHMARK_SUITE_IDS.length),
  repetitions: z.number().int().min(1).max(3).default(1),
  maxBudgetUsd: z.number().min(0).max(10_000).default(0),
  allowExternalNetwork: z.boolean().default(false),
  approvePaidModelsForThisRun: z.boolean().default(false),
}).strict();

export type ModelBenchmarkPlanRequest = z.infer<typeof modelBenchmarkPlanRequestSchema>;

export function runModelCatalogAudit() {
  const targets = MODEL_BENCHMARK_TARGETS.map((model) => {
    const checks = {
      identity: Boolean(model.name.trim() && model.provider.trim()),
      taskFit: Boolean(model.bestFor.trim() && model.category.trim()),
      accessMetadata: Boolean(model.tier && model.accessNote.trim()),
      capabilities: model.declaredCapabilities.length > 0,
      discoveryTruth: !model.discoveryTarget || Boolean(model.officialCatalog),
    };
    return {
      id: model.id,
      name: model.name,
      provider: model.provider,
      passed: Object.values(checks).every(Boolean),
      checks,
      liveModelCalled: false,
    };
  });
  return {
    schema: "dreamco.buddy_model_catalog_audit.v1",
    targets: targets.length,
    passed: targets.filter((target) => target.passed).length,
    failed: targets.filter((target) => !target.passed).length,
    liveModelsCalled: 0,
    claim: "Catalog validation only. This is not a model quality score.",
    results: targets,
  } as const;
}

export function createModelBenchmarkPlan(input: ModelBenchmarkPlanRequest) {
  const request = modelBenchmarkPlanRequestSchema.parse(input);
  const uniqueTargetIds = [...new Set(request.targetIds)];
  const uniqueSuiteIds = [...new Set(request.suiteIds)];
  const targetMap = new Map(MODEL_BENCHMARK_TARGETS.map((model) => [model.id, model]));
  const targets = uniqueTargetIds.map((id) => {
    const model = targetMap.get(id);
    if (!model) throw new Error(`Unknown benchmark target: ${id}`);
    return model;
  });
  const paidTargets = targets.filter((target) => !["free", "discovery"].includes(target.tier));
  const discoveryTargets = targets.filter((target) => target.discoveryTarget);
  const totalCases = targets.length * uniqueSuiteIds.length * request.repetitions;
  const status = !request.allowExternalNetwork
    ? "local_catalog_plan_ready"
    : discoveryTargets.length
      ? "official_catalog_discovery_required"
      : paidTargets.length && (!request.approvePaidModelsForThisRun || request.maxBudgetUsd <= 0)
      ? "paid_budget_approval_required"
      : "live_adapters_required";

  return {
    schema: "dreamco.buddy_model_benchmark_plan.v1",
    status,
    targetCount: targets.length,
    paidTargetCount: paidTargets.length,
    discoveryTargetCount: discoveryTargets.length,
    suiteCount: uniqueSuiteIds.length,
    repetitions: request.repetitions,
    totalCases,
    maxBudgetUsd: request.maxBudgetUsd,
    paidApprovalRecordedForThisRun: request.approvePaidModelsForThisRun,
    externalNetworkApprovedForThisRun: request.allowExternalNetwork,
    liveBenchmarkExecuted: false,
    targets: targets.map((target) => ({
      id: target.id,
      name: target.name,
      provider: target.provider,
      tier: target.tier,
      discoveryTarget: target.discoveryTarget,
      exactModelId: target.exactModelId,
      officialCatalog: target.officialCatalog,
    })),
    suites: uniqueSuiteIds,
    evidenceRequiredPerCase: [
      "provider and exact model id",
      "model version or provider response metadata",
      "signed prompt fixture hash",
      "redacted response hash",
      "latency and retry count",
      "input and output token usage when available",
      "actual cost when available",
      "grader result and grader version",
      "UTC timestamp",
    ],
    controls: {
      shuffleTargetOrder: true,
      identicalFixturesPerComparableModel: true,
      providerWarmupExcluded: true,
      failuresRemainVisible: true,
      rawPrivateContentRetained: false,
      noAutomaticPaidReruns: true,
    },
  } as const;
}

export function gradeDeterministicBenchmarkOutput(
  suiteId: "instruction_following" | "structured_output" | "arithmetic_reasoning",
  output: string,
) {
  const trimmed = output.trim();
  if (suiteId === "instruction_following") return { passed: trimmed === "READY", score: trimmed === "READY" ? 1 : 0 };
  if (suiteId === "arithmetic_reasoning") return { passed: trimmed === "42", score: trimmed === "42" ? 1 : 0 };
  try {
    const parsed = JSON.parse(trimmed) as { result?: unknown; confidence?: unknown };
    const passed = parsed.result === 42
      && typeof parsed.confidence === "number"
      && parsed.confidence >= 0
      && parsed.confidence <= 1;
    return { passed, score: passed ? 1 : 0 };
  } catch {
    return { passed: false, score: 0 };
  }
}
