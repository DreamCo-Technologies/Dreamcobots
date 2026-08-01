import assert from "node:assert/strict";
import test from "node:test";

import {
  createModelBenchmarkPlan,
  gradeDeterministicBenchmarkOutput,
  MODEL_BENCHMARK_SUITE_IDS,
  runModelCatalogAudit,
} from "../server/model-benchmark-policy";

test("the benchmark catalog audits exactly 100 targets without pretending to call them", () => {
  const audit = runModelCatalogAudit();
  assert.equal(audit.targets, 100);
  assert.equal(audit.failed, 0);
  assert.equal(audit.liveModelsCalled, 0);
});

test("paid live benchmark plans stop at budget and approval gates", () => {
  const plan = createModelBenchmarkPlan({
    targetIds: [1, 3, 7],
    suiteIds: [...MODEL_BENCHMARK_SUITE_IDS],
    repetitions: 1,
    maxBudgetUsd: 0,
    allowExternalNetwork: true,
    approvePaidModelsForThisRun: false,
  });
  assert.equal(plan.status, "paid_budget_approval_required");
  assert.equal(plan.liveBenchmarkExecuted, false);
  assert.equal(plan.totalCases, 36);
});

test("an approved benchmark remains blocked until live adapters execute it", () => {
  const plan = createModelBenchmarkPlan({
    targetIds: [1, 7],
    suiteIds: ["instruction_following", "structured_output"],
    repetitions: 2,
    maxBudgetUsd: 5,
    allowExternalNetwork: true,
    approvePaidModelsForThisRun: true,
  });
  assert.equal(plan.status, "live_adapters_required");
  assert.equal(plan.liveBenchmarkExecuted, false);
  assert.equal(plan.totalCases, 8);
});

test("deterministic graders reject extra text and malformed output", () => {
  assert.deepEqual(gradeDeterministicBenchmarkOutput("instruction_following", "READY"), { passed: true, score: 1 });
  assert.deepEqual(gradeDeterministicBenchmarkOutput("instruction_following", "READY!"), { passed: false, score: 0 });
  assert.deepEqual(gradeDeterministicBenchmarkOutput("arithmetic_reasoning", "42"), { passed: true, score: 1 });
  assert.deepEqual(
    gradeDeterministicBenchmarkOutput("structured_output", '{"result":42,"confidence":0.9}'),
    { passed: true, score: 1 },
  );
  assert.deepEqual(gradeDeterministicBenchmarkOutput("structured_output", "not-json"), { passed: false, score: 0 });
});
