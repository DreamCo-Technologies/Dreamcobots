import { readFileSync } from "node:fs";
import { resolve } from "node:path";

const root = process.cwd();
const dreamCodeLab = JSON.parse(readFileSync(resolve(root, "App_bots", "DreamCodeLab.json"), "utf8"));
const quality = JSON.parse(readFileSync(resolve(root, "config", "buddy-fleet-quality-program.json"), "utf8"));

const requiredBuilderRoles = [
  "code-reader",
  "ai-pair-prog",
  "deployment-mgr",
  "api-designer",
  "test-generator",
  "code-review-ai",
  "debug-detective",
  "monorepo-mgr",
  "perf-profiler",
  "docs-generator",
];

const requiredQualityWorkers = [
  "test-generator",
  "code-review-ai",
  "debug-detective",
  "perf-profiler",
  "security-scanner",
  "task-dependency-mgr",
  "improvement-engine",
  "ai-self-learner",
];

const botMap = new Map((dreamCodeLab.bots ?? []).map((bot: any) => [bot.slug, bot]));
const workerMap = new Map((quality.quality_workers ?? []).map((worker: any) => [worker.slug, worker]));
const missingBuilderRoles = requiredBuilderRoles.filter((slug) => !botMap.has(slug));
const missingQualityWorkers = requiredQualityWorkers.filter((slug) => !workerMap.has(slug));

const weakBuilderRoles = requiredBuilderRoles.flatMap((slug) => {
  const bot: any = botMap.get(slug);
  if (!bot) return [];
  const problems: string[] = [];
  if (!Array.isArray(bot.capabilities) || bot.capabilities.length < 6) problems.push("insufficient_capability_depth");
  if (!bot.description || String(bot.description).length < 25) problems.push("weak_description");
  if (!bot.targetUsers) problems.push("missing_target_users");
  return problems.length ? [{ slug, problems }] : [];
});

const releasePipeline = quality.release_pipeline ?? [];
const requiredReleaseGates = [
  "repository_contract",
  "dependency_closure",
  "adapter_contract",
  "live_end_to_end",
  "release_candidate",
  "owner_review",
  "production_observation",
];
const releaseIds = new Set(releasePipeline.map((phase: any) => phase.id));
const missingReleaseGates = requiredReleaseGates.filter((id) => !releaseIds.has(id));

const ready = missingBuilderRoles.length === 0 && missingQualityWorkers.length === 0 && weakBuilderRoles.length === 0 && missingReleaseGates.length === 0;
const report = {
  schema: "dreamco.builder_team_readiness.v1",
  checkedAt: new Date().toISOString(),
  dreamCodeLabProfiles: Array.isArray(dreamCodeLab.bots) ? dreamCodeLab.bots.length : 0,
  requiredBuilderRoles,
  requiredQualityWorkers,
  missingBuilderRoles,
  missingQualityWorkers,
  weakBuilderRoles,
  missingReleaseGates,
  readyForDailyBuildWork: ready,
};

console.log(JSON.stringify(report, null, 2));
process.exit(ready ? 0 : 1);
