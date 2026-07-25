import { z } from "zod";

import openModelCatalog from "../config/buddy-open-model-coding-lab.json";

type OpenModelCatalog = {
  schema: string;
  model_families: Array<{
    id: string;
    label: string;
    developer: string;
    developer_region: string;
    access: string;
    license: string;
    official_source: string;
  }>;
  coding_tasks: Array<{ id: string; label: string; grader: string }>;
  evidence_fields: string[];
  open_source_sandbox: {
    supported_hosts: string[];
  };
};

export const OPEN_MODEL_CATALOG = openModelCatalog as OpenModelCatalog;

const sourceKinds = ["repository", "model_weights", "package"] as const;
const weightFormats = ["safetensors", "gguf", "onnx", "tflite"] as const;
const floatingRevisions = new Set(["main", "master", "latest", "head", "stable", "dev", "develop"]);

export const openModelComparisonRequestSchema = z.object({
  modelFamilyIds: z.array(z.string().min(1).max(80)).min(2).max(12),
  taskIds: z.array(z.string().min(1).max(80)).min(1).max(10),
  repetitions: z.number().int().min(1).max(3).default(1),
  localRuntimeId: z.string().min(1).max(80).optional(),
  maxBudgetUsd: z.number().min(0).max(10_000).default(0),
  allowExternalNetwork: z.boolean().default(false),
  approvePaidAdaptersForThisRun: z.boolean().default(false),
}).strict();

export const openSourceSandboxPlanRequestSchema = z.object({
  sourceKind: z.enum(sourceKinds),
  sourceUrl: z.string().url().max(2_048),
  revision: z.string().min(4).max(160).regex(/^[A-Za-z0-9][A-Za-z0-9._/+:-]*$/),
  declaredLicense: z.string().min(2).max(120),
  objective: z.string().min(10).max(2_000),
  ownerConfirmsRights: z.boolean(),
  allowNetworkDuringBuild: z.boolean().default(false),
  trustRemoteCode: z.boolean().default(false),
  weightFormat: z.enum(weightFormats).optional(),
  limits: z.object({
    timeoutSeconds: z.number().int().min(30).max(7_200).default(900),
    cpuCores: z.number().int().min(1).max(32).default(2),
    memoryMb: z.number().int().min(512).max(131_072).default(4_096),
    diskMb: z.number().int().min(1_024).max(524_288).default(20_480),
    processCount: z.number().int().min(8).max(512).default(64),
  }).strict(),
}).strict();

export type OpenModelComparisonRequest = z.infer<typeof openModelComparisonRequestSchema>;
export type OpenSourceSandboxPlanRequest = z.infer<typeof openSourceSandboxPlanRequestSchema>;

function unique<T>(values: T[]) {
  return [...new Set(values)];
}

export function createOpenModelComparisonPlan(input: OpenModelComparisonRequest) {
  const request = openModelComparisonRequestSchema.parse(input);
  const modelIds = unique(request.modelFamilyIds);
  const taskIds = unique(request.taskIds);
  const modelMap = new Map(OPEN_MODEL_CATALOG.model_families.map((model) => [model.id, model]));
  const taskMap = new Map(OPEN_MODEL_CATALOG.coding_tasks.map((task) => [task.id, task]));
  const models = modelIds.map((id) => {
    const model = modelMap.get(id);
    if (!model) throw new Error(`Unknown open-model family: ${id}`);
    return model;
  });
  const tasks = taskIds.map((id) => {
    const task = taskMap.get(id);
    if (!task) throw new Error(`Unknown coding task: ${id}`);
    return task;
  });
  const status = !request.allowExternalNetwork
    ? "local_evaluation_plan_ready"
    : request.maxBudgetUsd > 0 && !request.approvePaidAdaptersForThisRun
      ? "paid_adapter_approval_required"
      : "live_sandbox_and_adapters_required";
  return {
    schema: "dreamco.buddy_open_model_comparison_plan.v1",
    status,
    modelCount: models.length,
    taskCount: tasks.length,
    totalCases: models.length * tasks.length * request.repetitions,
    repetitions: request.repetitions,
    models: models.map((model) => ({
      id: model.id,
      label: model.label,
      developer: model.developer,
      developerRegion: model.developer_region,
      access: model.access,
      license: model.license,
      officialSource: model.official_source,
    })),
    tasks,
    localRuntimeId: request.localRuntimeId ?? null,
    externalNetworkApprovedForThisRun: request.allowExternalNetwork,
    paidAdaptersApprovedForThisRun: request.approvePaidAdaptersForThisRun,
    maxBudgetUsd: request.maxBudgetUsd,
    liveExecutionPerformed: false,
    scoring: {
      developerRegionUsedForScoring: false,
      groupingUnit: "exact model checkpoint",
      rankingInputs: [
        "signed test results",
        "license fit",
        "hardware and energy use",
        "latency",
        "actual cost",
        "language coverage",
        "safety regressions",
      ],
    },
    evidenceRequired: OPEN_MODEL_CATALOG.evidence_fields,
  } as const;
}

export function createOpenSourceSandboxPlan(input: OpenSourceSandboxPlanRequest) {
  const request = openSourceSandboxPlanRequestSchema.parse(input);
  const source = new URL(request.sourceUrl);
  if (source.username || source.password || source.search || source.hash) {
    throw new Error("Source URLs must not contain credentials, query strings, or fragments.");
  }
  if (source.protocol !== "https:" || !OPEN_MODEL_CATALOG.open_source_sandbox.supported_hosts.includes(source.hostname)) {
    throw new Error("Source must use HTTPS on an approved open-source host.");
  }
  if (floatingRevisions.has(request.revision.toLowerCase())) {
    throw new Error("Pin an exact commit, immutable tag, or model revision instead of a floating branch.");
  }
  if (!request.ownerConfirmsRights) {
    throw new Error("The owner must confirm the source license and usage rights.");
  }
  if (request.trustRemoteCode) {
    throw new Error("Remote model code is disabled in Buddy sandboxes.");
  }
  if (request.sourceKind === "model_weights" && !request.weightFormat) {
    throw new Error("Model weights require an approved non-pickle weight format.");
  }
  if (request.sourceKind !== "model_weights" && request.weightFormat) {
    throw new Error("Weight format only applies to model-weight sources.");
  }
  return {
    schema: "dreamco.buddy_open_source_sandbox_plan.v1",
    status: request.allowNetworkDuringBuild ? "network_approval_and_sandbox_adapter_required" : "sandbox_adapter_required",
    source: {
      kind: request.sourceKind,
      url: source.toString(),
      revision: request.revision,
      declaredLicense: request.declaredLicense,
      weightFormat: request.weightFormat ?? null,
    },
    objective: request.objective,
    liveExecutionPerformed: false,
    sandboxAdapterRequired: true,
    controls: {
      sourceMount: "read_only",
      workingDirectory: "ephemeral",
      user: "non_root",
      hostSockets: "none",
      secrets: "none",
      network: request.allowNetworkDuringBuild ? "one_run_approval_required" : "off",
      trustRemoteCode: false,
      limits: request.limits,
      outputs: "quarantined_until_tests_and_owner_review",
    },
    stages: [
      "verify exact revision, publisher, license, and file hashes",
      "scan secrets, malware, unsafe serialization, dependencies, and source provenance",
      "generate SBOM and open-source security scorecard evidence",
      "build in a disposable sandbox with locked dependencies",
      "run upstream, compatibility, mutation, security, and adversarial tests",
      "record logs, resource use, failures, and reproducible artifact hashes",
      "show source, behavior, license, and dependency diffs",
      "request owner approval for a reversible integration checkpoint",
    ],
    automaticMerge: false,
    automaticPublish: false,
  } as const;
}
