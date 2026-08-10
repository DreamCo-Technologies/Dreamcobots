import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";

import { z } from "zod";

import { selectBestModelForTask } from "./model-intelligence-router";

type FleetBot = {
  identity: {
    slug: string;
    display_name: string;
    division: string;
    category: string;
  };
  mission: string;
  capability_search: string;
  capability_count: number;
};

type FleetCatalog = {
  bots: FleetBot[];
};

type RouterPolicy = {
  activation_policy: {
    maximum_parallel_independent_lanes: number;
    maximum_parallel_writers_per_owner: number;
    lazy_activation: boolean;
    activate_only_needed_bots: boolean;
    activate_only_needed_models: boolean;
    activate_only_needed_tools: boolean;
    task_scoped_subbots_expire: boolean;
  };
};

const policy = JSON.parse(
  readFileSync(resolve(process.cwd(), "config", "buddy-intelligent-task-router.json"), "utf8"),
) as RouterPolicy;

const fleet = JSON.parse(
  readFileSync(resolve(process.cwd(), "config", "generated", "bots.catalog.json"), "utf8"),
) as FleetCatalog;

export const intelligentTaskRequestSchema = z.object({
  objective: z.string().trim().min(5).max(5000),
  requiredCapabilities: z.array(z.string().trim().min(2).max(160)).max(40).default([]),
  requiredTools: z.array(z.string().trim().min(2).max(120)).max(30).default([]),
  requiredModalities: z.array(z.string().trim().min(2).max(80)).max(12).default([]),
  minimumContextTokens: z.number().int().nonnegative().max(20_000_000).default(0),
  writeScopes: z.array(z.string().trim().min(1).max(300)).max(50).default([]),
  preferOpenWeight: z.boolean().default(false),
  requireOpenWeight: z.boolean().default(false),
  preferLocal: z.boolean().default(false),
  allowPaid: z.boolean().default(false),
  maximumParallelLanes: z.number().int().min(1).max(32).optional(),
}).strict();

export type IntelligentTaskRequest = z.infer<typeof intelligentTaskRequestSchema>;

const STOP = new Set([
  "about", "after", "again", "also", "because", "before", "buddy", "could", "from", "have", "into",
  "make", "need", "please", "should", "that", "their", "then", "this", "through", "using", "want", "with", "would", "your",
]);

function tokens(value: string) {
  return new Set(
    value
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, " ")
      .split(/\s+/)
      .filter((token) => token.length >= 3 && !STOP.has(token)),
  );
}

function overlap(left: Set<string>, right: Set<string>) {
  let count = 0;
  for (const token of left) if (right.has(token)) count += 1;
  return count;
}

function botScore(bot: FleetBot, objective: string, requested: string[]) {
  const objectiveTokens = tokens(`${objective} ${requested.join(" ")}`);
  const botText = `${bot.identity.slug} ${bot.identity.display_name} ${bot.identity.division} ${bot.identity.category} ${bot.mission} ${bot.capability_search}`;
  const botTokens = tokens(botText);
  let score = overlap(objectiveTokens, botTokens) * 12;
  const capabilities = bot.capability_search.toLowerCase();
  for (const requestedCapability of requested) {
    if (capabilities.includes(requestedCapability.toLowerCase())) score += 40;
  }
  if (/dreambot|master/i.test(bot.identity.slug)) score += 1;
  return score;
}

function inferTaskStages(objective: string, requiredCapabilities: string[]) {
  const text = `${objective} ${requiredCapabilities.join(" ")}`.toLowerCase();
  const stages: Array<{ id: string; purpose: string; dependencies: string[]; write: boolean }> = [];

  stages.push({ id: "understand", purpose: "Understand objective, constraints, evidence requirements, and success criteria.", dependencies: [], write: false });

  if (/research|search|current|latest|compare|market|source|evidence/.test(text)) {
    stages.push({ id: "research", purpose: "Gather and validate required evidence before implementation.", dependencies: ["understand"], write: false });
  }
  if (/build|code|implement|fix|debug|refactor|upgrade|create|deploy/.test(text)) {
    stages.push({ id: "implement", purpose: "Produce the smallest implementation that satisfies the objective.", dependencies: stages.some((stage) => stage.id === "research") ? ["research"] : ["understand"], write: true });
  }
  if (/test|debug|fix|build|code|implement|upgrade|deploy/.test(text)) {
    stages.push({ id: "verify", purpose: "Run targeted tests, regression checks, and acceptance criteria.", dependencies: stages.some((stage) => stage.id === "implement") ? ["implement"] : ["understand"], write: false });
  }
  if (/deploy|publish|send|purchase|payment|live|production/.test(text)) {
    stages.push({ id: "approval", purpose: "Stop at the required live-action approval boundary.", dependencies: stages.some((stage) => stage.id === "verify") ? ["verify"] : [stages.at(-1)!.id], write: false });
  }
  if (stages.length === 1) {
    stages.push({ id: "execute", purpose: "Complete the task using the selected specialist and model route.", dependencies: ["understand"], write: false });
  }
  return stages;
}

function chooseBots(objective: string, capabilities: string[], limit = 6) {
  return fleet.bots
    .map((bot) => ({ bot, score: botScore(bot, objective, capabilities) }))
    .filter((entry) => entry.score > 0)
    .sort((a, b) => b.score - a.score || a.bot.identity.slug.localeCompare(b.bot.identity.slug))
    .slice(0, limit);
}

export function compileIntelligentTask(input: z.input<typeof intelligentTaskRequestSchema>) {
  const request = intelligentTaskRequestSchema.parse(input);
  const taskId = `task-${createHash("sha256").update(JSON.stringify(request)).digest("hex").slice(0, 20)}`;
  const botCandidates = chooseBots(request.objective, request.requiredCapabilities);
  const canonicalMaster = botCandidates[0]?.bot ?? fleet.bots.find((bot) => bot.identity.slug === "dreambot") ?? fleet.bots[0];
  if (!canonicalMaster) throw new Error("No canonical Buddy fleet bot is available.");

  const requiredSpecialists = botCandidates
    .slice(1)
    .filter((entry) => entry.score >= Math.max(12, (botCandidates[0]?.score ?? 0) * 0.35))
    .slice(0, 4)
    .map((entry) => ({
      slug: entry.bot.identity.slug,
      displayName: entry.bot.identity.display_name,
      division: entry.bot.identity.division,
      role: "task_scoped_specialist",
      score: entry.score,
      expiresAfterTask: true,
    }));

  const modelRoute = selectBestModelForTask({
    objective: request.objective,
    requiredCapabilities: request.requiredCapabilities,
    requiredTools: request.requiredTools,
    requiredModalities: request.requiredModalities,
    minimumContextTokens: request.minimumContextTokens,
    preferOpenWeight: request.preferOpenWeight,
    requireOpenWeight: request.requireOpenWeight,
    preferLocal: request.preferLocal,
    allowPaid: request.allowPaid,
    qualityPriority: 1,
    costPriority: 0.25,
    latencyPriority: 0.25,
    privacyPriority: 0.35,
    maxCandidates: 8,
  });

  const rawStages = inferTaskStages(request.objective, request.requiredCapabilities);
  const laneLimit = Math.min(
    request.maximumParallelLanes ?? policy.activation_policy.maximum_parallel_independent_lanes,
    policy.activation_policy.maximum_parallel_independent_lanes,
  );

  const writeOwner = request.writeScopes.length ? request.writeScopes.join("|") : "task-readonly";
  const compiledStages = rawStages.map((stage, index) => ({
    ...stage,
    lane: Math.min(index + 1, laneLimit),
    writerOwner: stage.write ? writeOwner : null,
    assignedBotSlug: index === 0 || !requiredSpecialists.length
      ? canonicalMaster.identity.slug
      : requiredSpecialists[(index - 1) % requiredSpecialists.length].slug,
    selectedModelId: modelRoute.selected?.modelId ?? null,
    selectedExactModelId: modelRoute.selected?.exactModelId ?? null,
    activateAtStageStart: true,
    deactivateAtStageEnd: stage.id !== "approval",
  }));

  const uniqueActiveBots = new Set(compiledStages.map((stage) => stage.assignedBotSlug));
  const uniqueActiveModels = new Set(compiledStages.map((stage) => stage.selectedModelId).filter(Boolean));
  const independentStages = compiledStages.filter((stage) => stage.dependencies.length === 0).length;

  return {
    schema: "dreamco.intelligent_task_compilation.v1",
    taskId,
    objective: request.objective,
    status: "compiled_lazy_execution_graph",
    qualityPolicy: "best_verified_task_fit_first",
    master: {
      slug: canonicalMaster.identity.slug,
      displayName: canonicalMaster.identity.display_name,
      division: canonicalMaster.identity.division,
    },
    taskScopedSpecialists: requiredSpecialists,
    modelRoute,
    graph: {
      stages: compiledStages,
      maximumParallelLanes: laneLimit,
      maximumParallelWritersPerOwner: policy.activation_policy.maximum_parallel_writers_per_owner,
      independentRootStages: independentStages,
      conflictingWritesSerialized: true,
    },
    activation: {
      lazy: policy.activation_policy.lazy_activation,
      activeBotCount: uniqueActiveBots.size,
      activeModelCount: uniqueActiveModels.size,
      totalFleetBotCount: fleet.bots.length,
      fleetActivationRatio: Number((uniqueActiveBots.size / Math.max(1, fleet.bots.length)).toFixed(6)),
      taskScopedWorkersExpire: policy.activation_policy.task_scoped_subbots_expire,
      allUnusedBotsRemainInactive: true,
      allUnusedModelsRemainInactive: true,
    },
    costControls: {
      all500ModelsCalled: false,
      shortlistBeforeBenchmark: true,
      duplicateInferenceSuppressed: true,
      contextRightSizingRequired: true,
      qualityFloorPreservedBeforeCheaperFallback: true,
    },
  } as const;
}
