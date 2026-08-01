import { createHash } from "node:crypto";
import { readFileSync, writeFileSync } from "node:fs";
import { dirname, relative, resolve } from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

import { buildFleetCatalog } from "./generate_bot_fleet_catalog";

type QualitySource = {
  schema: string;
  catalog_reviewed_on: string;
  stale_after_days: number;
  truth_policy: Record<string, boolean>;
  benchmark_dimensions: Array<{ id: string; label: string; target: string }>;
  competitor_discovery: Record<string, unknown>;
  quality_workers: Array<{ slug: string; role: string }>;
  release_pipeline: Array<{ id: string; gate: string }>;
  dependency_gates: string[];
  continuous_learning: Record<string, unknown>;
  efficiency_budgets: Record<string, unknown>;
};

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const SOURCE_PATH = resolve(ROOT, "config", "buddy-fleet-quality-program.json");
const GENERATED_PATH = resolve(ROOT, "config", "generated", "buddy_fleet_quality_program.json");
const PUBLIC_PATH = resolve(ROOT, "website", "data", "buddy-fleet-quality-program.js");
const REPORT_PATH = resolve(ROOT, "reports", "BUDDY_FLEET_QUALITY_PROGRAM.md");

function digest(value: string) {
  return createHash("sha256").update(value).digest("hex").slice(0, 20);
}

export function buildFleetQualityProgram() {
  const source = JSON.parse(readFileSync(SOURCE_PATH, "utf8")) as QualitySource;
  const fleet = buildFleetCatalog();
  const fleetSlugs = new Set(fleet.bots.map((bot) => bot.identity.slug));
  const dimensionIds = source.benchmark_dimensions.map((dimension) => dimension.id);
  const phaseIds = source.release_pipeline.map((phase) => phase.id);
  const workerSlugs = source.quality_workers.map((worker) => worker.slug);

  if (new Set(dimensionIds).size !== dimensionIds.length || dimensionIds.length < 10) {
    throw new Error("Fleet quality dimensions must be unique and comprehensive.");
  }
  if (new Set(phaseIds).size !== phaseIds.length || phaseIds.length < 8) {
    throw new Error("Fleet quality release phases must be unique and comprehensive.");
  }
  for (const slug of workerSlugs) {
    if (!fleetSlugs.has(slug)) throw new Error(`Fleet quality worker does not resolve: ${slug}`);
  }

  const bots = fleet.bots.map((bot) => {
    const apiNames = bot.api_candidates.map((api) => api.name);
    const capabilities = bot.capabilities.map((capability) => ({
      capability_test_id: capability.test_id,
      name: capability.name,
      fixture_id: `quality-fixture-${digest(`${bot.identity.slug}:${capability.name}:v1`)}`,
      repository_contract_status: capability.test_status === "reported_by_fleet_e2e" ? "passed" : "missing",
      repository_evidence: capability.test_evidence,
      benchmark_dimensions: dimensionIds,
      competitor_discovery_status: "current_sources_required",
      live_competitor_benchmark_status: "not_run",
      live_end_to_end_status: "not_run",
    }));
    const completedPhases = ["catalog_and_route", "repository_contract"];
    const nextActions = [
      "Run a clean dependency and import audit on the review branch.",
      apiNames.length
        ? `Implement mock and failure contracts for the selected adapter candidates: ${apiNames.slice(0, 3).join(", ")}.`
        : "Document whether this profile can remain local-only or needs a new owner-approved adapter.",
      "Discover current task-specific competitors from official sources and record versions, terms, and prices.",
      "Run identical signed fixtures in staging, record failures, and prioritize measured gaps.",
      "Verify authentication, authorization, telemetry, rollback, and owner approval before production release.",
    ];
    return {
      bot_id: bot.identity.slug,
      display_name: bot.identity.display_name,
      division: bot.identity.division,
      category: bot.identity.category,
      quality_plan_id: `quality-plan-${digest(bot.identity.slug)}`,
      evidence: {
        buddy_route: bot.readiness.buddy_chat_route,
        governed_runtime: bot.readiness.executable_runtime_instance,
        repository_capability_contracts_passed: capabilities.filter((item) => item.repository_contract_status === "passed").length,
        repository_capability_contracts_total: capabilities.length,
        configured_external_adapters: 0,
        live_end_to_end_flows_passed: 0,
        live_competitor_benchmarks_passed: 0,
      },
      production_status: "gates_remaining",
      build_plan: {
        completed_phases: completedPhases,
        remaining_phases: phaseIds.filter((phase) => !completedPhases.includes(phase)),
        next_actions: nextActions,
        assigned_quality_workers: workerSlugs,
        dependency_gate_reference: "config/buddy-fleet-quality-program.json#dependency_gates",
        release_pipeline_reference: "config/buddy-fleet-quality-program.json#release_pipeline",
        learning_policy_reference: "config/buddy-fleet-quality-program.json#continuous_learning",
      },
      benchmark_plan: {
        current_competitor_ranking_claimed: false,
        candidate_limit_per_capability: Number(source.competitor_discovery.maximum_candidates_per_capability || 5),
        live_network_default: "off",
        paid_runs_require_per_run_approval: true,
        capabilities,
      },
      buddy_prompts: {
        repository_test: bot.sample_test_prompt,
        improvement: `Review ${bot.identity.display_name} (${bot.identity.slug}). Run repository tests first, audit dependencies, discover current competitors from official sources, prepare identical benchmark fixtures for every declared capability, and propose a review branch that closes measured gaps. Do not spend, publish, contact providers, or merge without exact approval.`,
      },
    };
  });

  const capabilityPlans = bots.reduce((total, bot) => total + bot.benchmark_plan.capabilities.length, 0);
  const repositoryContractsPassed = bots.reduce(
    (total, bot) => total + bot.evidence.repository_capability_contracts_passed,
    0,
  );
  return {
    schema: "dreamco.buddy_fleet_quality_program.v1",
    catalog_reviewed_on: source.catalog_reviewed_on,
    stale_after_days: source.stale_after_days,
    truth_policy: source.truth_policy,
    summary: {
      profiles: bots.length,
      divisions: new Set(bots.map((bot) => bot.division)).size,
      per_bot_build_plans: bots.length,
      per_bot_dependency_plans: bots.length,
      per_bot_release_plans: bots.length,
      per_bot_learning_plans: bots.length,
      per_capability_benchmark_plans: capabilityPlans,
      repository_capability_contracts_passed: repositoryContractsPassed,
      live_competitor_benchmarks_completed: 0,
      live_end_to_end_profiles_passed: 0,
      production_ready_profiles: 0,
    },
    benchmark_dimensions: source.benchmark_dimensions,
    competitor_discovery: source.competitor_discovery,
    quality_workers: source.quality_workers,
    release_pipeline: source.release_pipeline,
    dependency_gates: source.dependency_gates,
    continuous_learning: source.continuous_learning,
    efficiency_budgets: source.efficiency_budgets,
    bots,
  };
}

function stableJson(value: unknown) {
  return `${JSON.stringify(value, null, 2)}\n`;
}

function publicProgram(program: ReturnType<typeof buildFleetQualityProgram>) {
  return {
    schema: program.schema,
    catalog_reviewed_on: program.catalog_reviewed_on,
    stale_after_days: program.stale_after_days,
    truth_policy: program.truth_policy,
    summary: program.summary,
    benchmark_dimensions: program.benchmark_dimensions,
    competitor_discovery: program.competitor_discovery,
    quality_workers: program.quality_workers,
    release_pipeline: program.release_pipeline,
    dependency_gates: program.dependency_gates,
    continuous_learning: program.continuous_learning,
    efficiency_budgets: program.efficiency_budgets,
    bots: program.bots.map((bot) => ({
      bot_id: bot.bot_id,
      display_name: bot.display_name,
      division: bot.division,
      category: bot.category,
      quality_plan_id: bot.quality_plan_id,
      evidence: bot.evidence,
      production_status: bot.production_status,
      build_plan: {
        completed_phases: bot.build_plan.completed_phases,
        remaining_phases: bot.build_plan.remaining_phases,
        next_actions: bot.build_plan.next_actions,
      },
      benchmark_plan: {
        current_competitor_ranking_claimed: bot.benchmark_plan.current_competitor_ranking_claimed,
        candidate_limit_per_capability: bot.benchmark_plan.candidate_limit_per_capability,
        live_network_default: bot.benchmark_plan.live_network_default,
        paid_runs_require_per_run_approval: bot.benchmark_plan.paid_runs_require_per_run_approval,
        capabilities: bot.benchmark_plan.capabilities.map((capability) => ({
          capability_test_id: capability.capability_test_id,
          name: capability.name,
          fixture_id: capability.fixture_id,
          repository_contract_status: capability.repository_contract_status,
          repository_evidence: capability.repository_evidence,
          competitor_discovery_status: capability.competitor_discovery_status,
          live_competitor_benchmark_status: capability.live_competitor_benchmark_status,
          live_end_to_end_status: capability.live_end_to_end_status,
        })),
      },
      buddy_prompts: bot.buddy_prompts,
    })),
  };
}

function report(program: ReturnType<typeof buildFleetQualityProgram>) {
  const lines = [
    "# Buddy Fleet Quality Program",
    "",
    "This report separates repository contract evidence from live end-to-end and competitor evidence. It does not claim permanent rankings, perfection, or production readiness without deployed proof.",
    "",
    "## Coverage",
    "",
    `- Bot build plans: ${program.summary.per_bot_build_plans}`,
    `- Capability benchmark plans: ${program.summary.per_capability_benchmark_plans}`,
    `- Repository capability contracts passed: ${program.summary.repository_capability_contracts_passed}`,
    `- Live competitor benchmarks completed: ${program.summary.live_competitor_benchmarks_completed}`,
    `- Live end-to-end profiles passed: ${program.summary.live_end_to_end_profiles_passed}`,
    `- Production-ready profiles evidenced: ${program.summary.production_ready_profiles}`,
    "",
    "## Release Pipeline",
    "",
    "| Phase | Evidence gate |",
    "| --- | --- |",
    ...program.release_pipeline.map((phase) => `| ${phase.id} | ${phase.gate} |`),
    "",
    "## Continuous Improvement Boundary",
    "",
    "Buddy may prepare evidence, issues, review branches, and draft pull requests. It may not self-merge, silently change models, spend money, or perform production actions without the configured approval gate.",
  ];
  return `${lines.join("\n")}\n`;
}

export function writeFleetQualityProgram({ check = false } = {}) {
  const program = buildFleetQualityProgram();
  const publicCatalog = publicProgram(program);
  const outputs = [
    [GENERATED_PATH, stableJson(program)],
    [PUBLIC_PATH, `window.BUDDY_FLEET_QUALITY_PROGRAM=${JSON.stringify(publicCatalog)};\n`],
    [REPORT_PATH, report(program)],
  ] as const;
  if (check) {
    for (const [path, expected] of outputs) {
      if (readFileSync(path, "utf8") !== expected) {
        throw new Error(`${relative(ROOT, path)} is stale; regenerate the fleet quality program`);
      }
    }
  } else {
    for (const [path, content] of outputs) writeFileSync(path, content, "utf8");
  }
  return program.summary;
}

if (process.argv[1] && pathToFileURL(resolve(process.argv[1])).href === import.meta.url) {
  console.log(JSON.stringify({ ok: true, ...writeFleetQualityProgram({ check: process.argv.includes("--check") }) }, null, 2));
}
