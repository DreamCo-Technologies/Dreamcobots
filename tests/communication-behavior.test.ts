import assert from "node:assert/strict";
import test from "node:test";

import {
  buildCommunicationBenchmarkPlan,
  buildCommunicationPlan,
  communicationBenchmarkRequestSchema,
  communicationPlanRequestSchema,
  getCommunicationBehaviorCatalog,
} from "../server/communication-behavior";

test("professional communication applies evidence and formality floors", () => {
  const request = communicationPlanRequestSchema.parse({
    objective: "Prepare a professional contract review checklist for the owner.",
    context: "legal",
    profile: {
      traits: { formality: 0.2, evidence_focus: 0.3 },
      adaptSlang: true,
    },
  });
  const plan = buildCommunicationPlan(request);
  assert.equal(plan.profile.professionalOverride, true);
  assert.equal(plan.profile.slangAllowed, false);
  assert.ok(plan.profile.traits.formality >= 0.9);
  assert.ok(plan.profile.traits.evidence_focus >= 0.95);
});

test("Zod 4 record schemas preserve string-keyed communication traits", () => {
  const request = communicationPlanRequestSchema.parse({
    objective: "Prepare an evidence-focused explanation for a technical review.",
    context: "business",
    profile: {
      traits: { evidence_focus: 0.88, clarity: 0.91 },
      selfReportDimensions: {},
    },
  });
  assert.equal(request.profile.traits.evidence_focus, 0.88);
  assert.equal(request.profile.traits.clarity, 0.91);
});

test("voice-cue adaptation requires explicit opt-in and never diagnoses", () => {
  assert.throws(() => communicationPlanRequestSchema.parse({
    objective: "Adapt the pace of this teaching conversation.",
    context: "education",
    profile: { voiceCueAdaptation: true, voiceCueConsent: false },
  }), /requires explicit opt-in/);
  const request = communicationPlanRequestSchema.parse({
    objective: "Adapt the pace of this teaching conversation.",
    context: "education",
    profile: { voiceCueAdaptation: true, voiceCueConsent: true },
    ownerConfirmedCue: "confused",
  });
  const plan = buildCommunicationPlan(request);
  assert.equal(plan.cueAdaptation.enabled, true);
  assert.ok(plan.cueAdaptation.guidance.includes("use plain language"));
  assert.equal(plan.cueAdaptation.inferredMentalState, false);
  assert.equal(plan.cueAdaptation.diagnosisPerformed, false);
});

test("clinical and high-impact psychological scoring is blocked", () => {
  const request = communicationPlanRequestSchema.parse({
    objective: "Create a mental health score and psychological profile for hiring.",
    context: "business",
  });
  assert.throws(() => buildCommunicationPlan(request), /cannot diagnose, score mental health, or decide eligibility/);
});

test("communication benchmark uses synthetic fixtures and aggregate metrics", () => {
  const catalog = getCommunicationBehaviorCatalog();
  const request = communicationBenchmarkRequestSchema.parse({
    suiteIds: catalog.benchmark_suites.map((suite) => suite.id),
    targetProfileIds: ["buddy-default", "buddy-professional"],
    syntheticFixturesOnly: true,
    repetitionsPerFixture: 3,
    retainRawConversations: false,
  });
  const plan = buildCommunicationBenchmarkPlan(request);
  assert.equal(plan.suites.length, 24);
  assert.equal(plan.storage.rawConversationsRetained, false);
  assert.equal(plan.resultState, "not_run");
  assert.equal(plan.superiorityClaimAllowed, false);
});

test("catalog covers broad interaction traits without hidden inference", () => {
  const catalog = getCommunicationBehaviorCatalog();
  const traits = catalog.trait_groups.flatMap((group) => group.traits);
  assert.equal(traits.length, 32);
  assert.equal(catalog.self_report_dimensions.length, 5);
  assert.equal(catalog.policy.hidden_psychological_inference, false);
  assert.equal(catalog.policy.self_report_only_for_psychology_dimensions, true);
});

test("conversation model is natural, grounded, and relationship-safe", () => {
  const catalog = getCommunicationBehaviorCatalog();
  assert.equal(catalog.conversation_model.competencies.length, 30);
  assert.ok(catalog.conversation_model.response_sequence.includes("answer or act on the request before adding optional ideas"));
  assert.equal(catalog.relationship_integrity.buddy_identifies_as_ai, true);
  assert.equal(catalog.relationship_integrity.claims_human_feelings_or_consciousness, false);
  assert.equal(catalog.relationship_integrity.encourages_exclusive_dependency, false);
  assert.equal(catalog.grounding_behavior.zero_hallucination_claim_allowed, false);
});

test("explicit emotion guidance supports users without hidden inference", () => {
  const request = communicationPlanRequestSchema.parse({
    objective: "Help me break down a difficult project without adding pressure.",
    context: "casual",
    profile: { voiceCueAdaptation: true, voiceCueConsent: true },
    ownerConfirmedCue: "overwhelmed",
  });
  const plan = buildCommunicationPlan(request);
  assert.deepEqual(plan.cueAdaptation.guidance, [
    "reduce the task to one next step",
    "limit choices",
    "preserve pause and resume",
  ]);
  assert.equal(plan.cueAdaptation.inferredMentalState, false);
  assert.ok(plan.psychologyKnowledgeBoundary.forbidden_uses.includes("clinical diagnosis or treatment"));
});
