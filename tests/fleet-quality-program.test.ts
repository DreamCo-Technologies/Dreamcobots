import assert from "node:assert/strict";
import test from "node:test";

import { buildFleetQualityProgram } from "../tools/generate_buddy_fleet_quality_program";

test("every fleet profile has a governed production build and learning plan", () => {
  const program = buildFleetQualityProgram();
  assert.equal(program.summary.profiles, 1051);
  assert.equal(program.summary.per_bot_build_plans, 1051);
  assert.equal(program.summary.per_bot_dependency_plans, 1051);
  assert.equal(program.summary.per_bot_release_plans, 1051);
  assert.equal(program.summary.per_bot_learning_plans, 1051);
  assert.equal(program.summary.production_ready_profiles, 0);
  assert.ok(program.bots.every((bot) => bot.build_plan.completed_phases.includes("repository_contract")));
  assert.ok(program.bots.every((bot) => bot.build_plan.remaining_phases.includes("dependency_closure")));
  assert.ok(program.bots.every((bot) => bot.build_plan.remaining_phases.includes("live_end_to_end")));
  assert.ok(program.bots.every((bot) => bot.production_status === "gates_remaining"));
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
