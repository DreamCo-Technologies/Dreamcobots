import assert from "node:assert/strict";
import test from "node:test";

import { SUCCESS_QUESTIONNAIRE } from "../shared/buddy-success-contract";
import {
  createGrowthExperimentPlan,
  createIntentResult,
  createOntologyPlan,
  createSuccessProfilePlan,
} from "../server/buddy-success-policy";
import { buildBuddySuccessProgram } from "../tools/generate_buddy_success_program";

test("success questionnaire is useful, bounded, and avoids secret collection", () => {
  assert.equal(SUCCESS_QUESTIONNAIRE.length, 30);
  assert.ok(SUCCESS_QUESTIONNAIRE.every((question) => question.type !== ("password" as never)));
  assert.ok(SUCCESS_QUESTIONNAIRE.every((question) => !/ssn|account_number|secret|token|api_key/i.test(question.id)));
  const plan = createSuccessProfilePlan({
    profileId: "owner-local",
    answers: { primary_outcome: "Launch a tested service prototype", success_measure: "Three owner-reviewed customer interviews" },
    shareWithBots: true,
    ownerConfirmsNoSecrets: true,
  });
  assert.equal(plan.status, "profile_ready");
  assert.match(plan.botContext, /Launch a tested service prototype/);
  assert.equal(plan.storedByThisRoute, false);
  assert.equal(plan.boundaries.guaranteedIncomeClaims, false);
});

test("success profiles reject credentials and identifiers", () => {
  assert.throws(() => createSuccessProfilePlan({
    profileId: "owner-local",
    answers: { primary_outcome: "Grow a service", success_measure: "One sale", available_tools: "api key: do-not-store-this" },
    shareWithBots: true,
    ownerConfirmsNoSecrets: true,
  }), /must not contain credentials/);
});

test("Buddy infers build, fix, create, plan, and discover without a mode button", () => {
  assert.equal(createIntentResult({ objective: "Build a working invoicing prototype" }).intent, "Build");
  assert.equal(createIntentResult({ objective: "Debug the failed checkout test" }).intent, "Fix");
  assert.equal(createIntentResult({ objective: "Create a music video storyboard" }).intent, "Create");
  assert.equal(createIntentResult({ objective: "Plan the product launch roadmap" }).intent, "Plan");
  assert.equal(createIntentResult({ objective: "Research and compare current options" }).intent, "Discover");
});

test("weighted ontology is user-switchable with evidence and safety floors", () => {
  const balanced = createOntologyPlan({ profileId: "owner-local", mode: "balanced", weights: {} });
  assert.equal(balanced.total, 100);
  assert.equal(balanced.developerRegionUsedAsQualitySignal, false);
  assert.throws(() => createOntologyPlan({
    profileId: "owner-local",
    mode: "custom",
    weights: { evidence: 5, safety: 5, user_value: 30, revenue_potential: 30, time_saved: 20, cost_control: 10 },
  }), /hard minimum/);
});

test("growth plans measure experiments without guaranteeing or moving money", () => {
  const plan = createGrowthExperimentPlan({
    profileId: "owner-local",
    title: "Local website audit",
    problem: "Small businesses cannot quickly identify broken website conversion paths.",
    customer: "Owner-operated local businesses",
    offer: "A bounded conversion and accessibility audit",
    validationMethod: "Review five owner-approved public sites and ask for feedback on a sample report.",
    estimatedEffortHours: 4,
    maximumBudgetUsd: 0,
    allowExternalResearch: false,
    approveOutreach: false,
    approveSpend: false,
  });
  assert.equal(plan.status, "local_validation_plan_ready");
  assert.equal(plan.incomeGuaranteed, false);
  assert.equal(plan.moneyMoved, false);
  assert.equal(plan.outreachSent, false);
});

test("all 45 divisions receive charters, 100 capabilities, production gates, and benchmark systems", () => {
  const program = buildBuddySuccessProgram();
  assert.equal(program.divisions.length, 45);
  assert.equal(program.summary.division_must_have_updates, 4500);
  assert.equal(program.summary.division_upgrades, 4500);
  assert.equal(program.summary.division_capabilities, 4500);
  assert.equal(program.summary.daily_logical_benchmark_slots, 360);
  assert.equal(program.summary.production_ready_divisions, 0);
  assert.equal(program.summary.model_benchmark_targets, 200);
  assert.equal(program.summary.robot_division_archetypes, 45);
  assert.equal(program.improvement_templates.must_have_updates.length, 100);
  assert.equal(program.improvement_templates.upgrades.length, 100);
  assert.equal(program.improvement_templates.division_capabilities.length, 100);
  assert.ok(program.divisions.every((division) => division.must_have_updates.count === 100));
  assert.ok(program.divisions.every((division) => division.upgrades.count === 100));
  assert.ok(program.divisions.every((division) => division.capabilities.count === 100));
  assert.ok(program.divisions.every((division) => division.capabilities.focuses.length === 10));
  assert.ok(program.divisions.every((division) => division.charter.purpose.length >= 60));
  assert.ok(program.divisions.every((division) => division.production_readiness.gates.length === 12));
  assert.ok(program.divisions.every((division) => division.production_readiness.production_ready === false));
  assert.ok(program.divisions.every((division) => division.benchmark_system.dimensions.length >= 10));
  assert.ok(program.divisions.every((division) => division.benchmark_system.daily_operations.logical_parallel_worker_slots === 8));
  assert.ok(program.divisions.every((division) => division.benchmark_system.live_competitors_tested === 0));
  assert.equal(program.open_ai_alliance_watch.memberDirectory.membershipClaimedByDreamCo, false);
  assert.equal(program.open_ai_alliance_watch.activeProjectWatch.length, 13);
  assert.equal(program.safe_ai_training.productionSelfModificationAllowed, false);
  assert.equal(program.trust_and_access.raw_credentials_accepted, false);
});
