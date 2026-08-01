import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";

import { buildFleetQualityProgram } from "../tools/generate_buddy_fleet_quality_program";

test("every fleet profile has a governed production build and learning plan", () => {
  const program = buildFleetQualityProgram();
  assert.equal(program.summary.profiles, 1051);
  assert.equal(program.summary.per_bot_build_plans, 1051);
  assert.equal(program.summary.per_bot_dependency_plans, 1051);
  assert.equal(program.summary.per_bot_release_plans, 1051);
  assert.equal(program.summary.per_bot_learning_plans, 1051);
  assert.equal(program.summary.unique_learning_paths, 1051);
  assert.equal(program.summary.unique_competitor_benchmark_suites, 1051);
  assert.equal(program.summary.production_ready_profiles, 0);
  assert.ok(program.bots.every((bot) => bot.build_plan.completed_phases.includes("repository_contract")));
  assert.ok(program.bots.every((bot) => bot.build_plan.remaining_phases.includes("dependency_closure")));
  assert.ok(program.bots.every((bot) => bot.build_plan.remaining_phases.includes("live_end_to_end")));
  assert.ok(program.bots.every((bot) => bot.production_status === "gates_remaining"));
});

test("every bot has a separate ordered learning path and competitor suite", () => {
  const program = buildFleetQualityProgram();
  const pathIds = program.bots.map((bot) => bot.learning_path.path_id);
  const suiteIds = program.bots.map((bot) => bot.competitor_benchmark.suite_id);
  const modules = program.bots.flatMap((bot) => bot.benchmark_plan.capabilities);
  assert.equal(new Set(pathIds).size, 1051);
  assert.equal(new Set(suiteIds).size, 1051);
  assert.equal(new Set(modules.map((module) => module.learning_module_id)).size, 8408);
  assert.equal(new Set(modules.map((module) => module.competitor_benchmark_id)).size, 8408);
  assert.ok(program.bots.every((bot) => bot.learning_path.module_count === bot.benchmark_plan.capabilities.length));
  assert.ok(program.bots.every((bot) => bot.learning_path.stages.length >= 8));
  assert.ok(program.bots.every((bot) => bot.learning_path.stages[0].status === "passed_repository_evidence"));
  assert.ok(program.bots.every((bot) => bot.competitor_benchmark.current_ranking_claimed === false));
  assert.ok(program.bots.every((bot) => bot.competitor_benchmark.status === "current_sources_and_live_runs_required"));
  assert.ok(program.bots.every((bot) => bot.benchmark_plan.capabilities.every((module, index) => module.learning_order === index + 1)));
});

test("every declared capability has repeatable evidence and an honest competitor benchmark state", () => {
  const program = buildFleetQualityProgram();
  assert.equal(program.summary.per_capability_benchmark_plans, 8408);
  assert.equal(program.summary.repository_capability_contracts_passed, 8408);
  assert.equal(program.summary.live_competitor_benchmarks_completed, 0);
  assert.equal(program.summary.live_end_to_end_profiles_passed, 0);
  const capabilities = program.bots.flatMap((bot) => bot.benchmark_plan.capabilities);
  assert.equal(new Set(capabilities.map((capability) => capability.fixture_id)).size, 8408);
  assert.ok(capabilities.every((capability) => capability.repository_contract_status === "passed"));
  assert.ok(capabilities.every((capability) => capability.live_competitor_benchmark_status === "not_run"));
  assert.ok(capabilities.every((capability) => capability.live_end_to_end_status === "not_run"));
  assert.ok(capabilities.every((capability) => capability.benchmark_dimensions.length >= 10));
});

test("quality workers resolve to real fleet profiles and cannot self-release", () => {
  const program = buildFleetQualityProgram();
  const fleetSlugs = new Set(program.bots.map((bot) => bot.bot_id));
  assert.ok(program.quality_workers.length >= 10);
  assert.ok(program.quality_workers.every((worker) => fleetSlugs.has(worker.slug)));
  assert.equal(program.truth_policy.no_self_merge_or_unreviewed_production_change, true);
  assert.equal(program.continuous_learning.mode, "owner_scheduled_evidence_proposals");
  assert.ok((program.continuous_learning.forbidden_outputs as string[]).includes("self merge"));
});

test("Test Center exposes and exports each bot learning path", () => {
  const html = readFileSync(new URL("../website/test-center.html", import.meta.url), "utf8");
  const script = readFileSync(new URL("../website/test-center.js", import.meta.url), "utf8");
  assert.match(html, /Every profile has its own ordered learning path/);
  assert.match(html, /<span>Learning paths<\/span>/);
  assert.match(html, /buddy-fleet-quality-program\.js\?v=2/);
  assert.match(script, /Separate learning path/);
  assert.match(script, /Competitor benchmark suite/);
  assert.match(script, /learningPathPolicy: quality\.learning_path_policy/);
  assert.match(script, /capability\.benchmark_id/);
});

test("Test Center exposes proposal-only recursive improvement evidence", () => {
  const html = readFileSync(new URL("../website/test-center.html", import.meta.url), "utf8");
  const script = readFileSync(new URL("../website/test-center.js", import.meta.url), "utf8");
  assert.match(html, /Recursive improvement guardrails/);
  assert.match(html, /cannot self-grant access, self-merge, silently train on conversations/);
  assert.match(html, /buddy-self-improvement\.js\?v=1/);
  assert.match(script, /window\.BUDDY_SELF_IMPROVEMENT/);
  assert.match(script, /improvement\.hallucination_controls/);
  assert.match(script, /improvement-live-changes'\)\.textContent = '0'/);
});
