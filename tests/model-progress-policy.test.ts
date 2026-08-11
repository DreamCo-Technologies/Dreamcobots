import assert from "node:assert/strict";
import test from "node:test";

import {
  createModelImprovementPlan,
  getModelProgressCenter,
  selectModelCouncil,
} from "../server/model-progress-policy";

test("all 500 model targets have categorized source and setup records", () => {
  const catalog = getModelProgressCenter();
  assert.equal(catalog.summary.modelTargets, 500);
  assert.equal(catalog.summary.providerSources, 100);
  assert.equal(catalog.summary.catalogReady, 500);
  assert.equal(catalog.summary.categorized, 500);
  assert.equal(catalog.summary.sourceLinked, 500);
  assert.equal(catalog.summary.setupPathsReady, 500);
  assert.equal(catalog.summary.liveConnected, 0);
  assert.equal(catalog.summary.liveBenchmarked, 0);
  assert.equal(catalog.truthContract.target_is_company_connection, false);
});

test("every task has separate 20-seat free and premium councils", () => {
  const catalog = getModelProgressCenter();
  assert.equal(catalog.taskCategories.length, 20);
  assert.equal(catalog.councils.length, 40);
  for (const task of catalog.taskCategories) {
    const free = catalog.councils.find((item) => item.task === task && item.mode === "free");
    const premium = catalog.councils.find((item) => item.task === task && item.mode === "premium");
    assert.equal(free?.members.length, 20, `missing free council seats for ${task}`);
    assert.equal(premium?.members.length, 20, `missing premium council seats for ${task}`);
    assert.ok(free?.members.every((member) => ["free", "freemium"].includes(member.tier)));
    assert.ok(premium?.members.every((member) => ["paid", "freemium"].includes(member.tier)));
  }
});

test("premium council pauses before a paid provider call", () => {
  const selection = selectModelCouncil({
    taskCategory: "Coding",
    mode: "premium",
    approvePaidModelsForThisRequest: false,
  });
  assert.equal(selection.memberCount, 20);
  assert.equal(selection.status, "paid_approval_required");
  assert.equal(selection.providerCallsExecuted, 0);
  assert.equal(selection.liveQualityClaimed, false);
});

test("local improvement plan creates a reversible Bootcamp route without training", () => {
  const plan = createModelImprovementPlan({
    taskCategory: "Research",
    mode: "free",
    maxBudgetUsd: 0,
    approvePaidModelsForThisRun: false,
    allowExternalNetwork: false,
    allowWeightTraining: false,
  });
  assert.equal(plan.status, "local_bootcamp_plan_ready");
  assert.equal(plan.trainingExecuted, false);
  assert.equal(plan.modelReleased, false);
  assert.equal(plan.providerCallsExecuted, 0);
  assert.equal(plan.controls.checkpointAndRollback, true);
  assert.equal(plan.controls.productionSelfModification, false);
});

test("50 dataset packages are empty rights-gated templates", () => {
  const catalog = getModelProgressCenter();
  assert.equal(catalog.datasetPackages.length, 50);
  assert.ok(catalog.datasetPackages.every((item: any) => item.status === "template_only"));
  assert.ok(catalog.datasetPackages.every((item: any) => item.recordsIncluded === 0));
  assert.ok(catalog.datasetPackages.every((item: any) => item.sellableVerified === false));
  assert.ok(catalog.datasetPackages.every((item: any) => item.blockedInputs.includes("private conversations")));
});
