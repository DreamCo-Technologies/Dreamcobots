import assert from "node:assert/strict";
import test from "node:test";

import {
  buildMediaCandidatePlan,
  evaluateMediaCandidates,
  getMediaQualityLabCatalog,
  mediaCandidatePlanRequestSchema,
  mediaQualityEvaluationRequestSchema,
} from "../server/media-quality-lab";

const hash = "b".repeat(64);
const voiceDimensions = {
  identity_similarity: 0.94,
  intelligibility: 0.96,
  naturalness: 0.93,
  pronunciation: 0.92,
  prosody_control: 0.91,
  expressiveness: 0.9,
  artifact_cleanliness: 0.95,
  stability: 0.94,
  latency_efficiency: 0.82,
};
const passingGates = Object.fromEntries(
  getMediaQualityLabCatalog().hard_release_gates.map((gate) => [gate, true]),
);

function candidate(id: string, dimensions = voiceDimensions) {
  return {
    id,
    engineId: id.includes("openvoice") ? "openvoice-v2-local" : "chatterbox-local",
    dimensions,
    hardGates: passingGates,
    medianLatencyMs: id.includes("fast") ? 120 : 250,
    evidence: {
      artifactSha256: hash,
      fixtureSetSha256: hash,
      fixtureCount: 8,
      repetitionsPerFixture: 3,
      evaluatorVersion: "buddy-media-evaluator-v1",
      evidenceReference: `evidence:${id}`,
      engineVersion: "test-model-1",
    },
  };
}

test("highest-quality plans generate multiple local candidates without executing models", () => {
  const plan = buildMediaCandidatePlan(mediaCandidatePlanRequestSchema.parse({
    projectId: "quality-plan-1",
    modality: "voice",
    fixtureSetId: "voice-core-v1",
    engineIds: ["openvoice-v2-local", "chatterbox-local"],
    qualityMode: "highest_quality",
    commercialUse: true,
  }));
  assert.equal(plan.candidates.length, 12);
  assert.equal(plan.execution.renderExecuted, false);
  assert.equal(plan.execution.externalCallExecuted, false);
  assert.equal(plan.execution.ownerMediaUploaded, false);
});

test("paid owner-media comparisons need separate comparison, budget, consent, and upload approvals", () => {
  const base = {
    projectId: "quality-plan-2",
    modality: "voice" as const,
    fixtureSetId: "voice-core-v1",
    engineIds: ["chatterbox-local"],
    fixtureClass: "owner_consented_media" as const,
    comparisonTargetIds: ["elevenlabs-reference"],
  };
  assert.throws(() => buildMediaCandidatePlan(mediaCandidatePlanRequestSchema.parse(base)), /exact approval/);
  assert.throws(() => buildMediaCandidatePlan(mediaCandidatePlanRequestSchema.parse({
    ...base,
    externalComparisonApproved: true,
  })), /budget approval/);
  assert.throws(() => buildMediaCandidatePlan(mediaCandidatePlanRequestSchema.parse({
    ...base,
    externalComparisonApproved: true,
    paidComparisonApproved: true,
  })), /consent receipt/);
  assert.throws(() => buildMediaCandidatePlan(mediaCandidatePlanRequestSchema.parse({
    ...base,
    externalComparisonApproved: true,
    paidComparisonApproved: true,
    ownerMediaConsentReceipt: "consent:owner-media-comparison",
  })), /separate upload approval/);
  const plan = buildMediaCandidatePlan(mediaCandidatePlanRequestSchema.parse({
    ...base,
    externalComparisonApproved: true,
    paidComparisonApproved: true,
    ownerMediaConsentReceipt: "consent:owner-media-comparison",
    ownerMediaExternalUploadApproved: true,
  }));
  assert.equal(plan.execution.ownerMediaUploaded, false);
  assert.equal(plan.execution.externalCallExecuted, false);
});

test("the quality lab selects the strongest evidence-backed candidate", () => {
  const weaker = Object.fromEntries(Object.keys(voiceDimensions).map((key) => [key, 0.84]));
  const request = mediaQualityEvaluationRequestSchema.parse({
    projectId: "quality-eval-1",
    modality: "voice",
    fixtureSetId: "voice-core-v1",
    candidates: [candidate("openvoice-weaker", weaker), candidate("chatterbox-strong")],
  });
  assert.equal(request.candidates[1].dimensions.identity_similarity, 0.94);
  assert.equal(request.candidates[1].hardGates.active_consent, true);
  const evaluation = evaluateMediaCandidates(request);
  assert.equal(evaluation.status, "release_candidate_selected");
  assert.equal(evaluation.winner?.id, "chatterbox-strong");
  assert.ok((evaluation.winner?.score ?? 0) > 0.9);
});

test("rights failures and incomplete fixture evidence block release", () => {
  const failedRights = candidate("chatterbox-rights-fail");
  failedRights.hardGates = { ...passingGates, active_consent: false };
  const tooLittleEvidence = candidate("openvoice-too-small");
  tooLittleEvidence.evidence.fixtureCount = 2;
  const evaluation = evaluateMediaCandidates(mediaQualityEvaluationRequestSchema.parse({
    projectId: "quality-eval-2",
    modality: "voice",
    fixtureSetId: "voice-core-v1",
    candidates: [failedRights, tooLittleEvidence],
  }));
  assert.equal(evaluation.status, "no_release_candidate");
  assert.equal(evaluation.winner, null);
});

test("a regression guard blocks a candidate below the accepted local baseline", () => {
  const dimensions = Object.fromEntries(Object.keys(voiceDimensions).map((key) => [key, 0.85]));
  const evaluation = evaluateMediaCandidates(mediaQualityEvaluationRequestSchema.parse({
    projectId: "quality-eval-3",
    modality: "voice",
    fixtureSetId: "voice-core-v1",
    stableBaselineScore: 0.94,
    candidates: [candidate("chatterbox-regression", dimensions)],
  }));
  assert.equal(evaluation.regressionPassed, false);
  assert.equal(evaluation.winner, null);
});

test("an unblinded or undersized comparison cannot support a superiority claim", () => {
  const evaluation = evaluateMediaCandidates(mediaQualityEvaluationRequestSchema.parse({
    projectId: "quality-eval-4",
    modality: "voice",
    fixtureSetId: "voice-core-v1",
    candidates: [candidate("chatterbox-strong")],
    baselineComparison: {
      targetId: "elevenlabs-reference",
      blinded: false,
      randomizedOrder: true,
      identicalFixtures: true,
      fixtureCount: 10,
      ratingsPerFixture: 3,
      buddyWins: 25,
      baselineWins: 5,
      ties: 0,
      baselineScore: 0.88,
      fixtureSetSha256: hash,
      evidenceSha256: hash,
      evaluatorVersion: "buddy-pairwise-evaluator-v1",
      evidenceReference: "blind-test:incomplete",
    },
  }));
  assert.equal(evaluation.comparisonClaimAllowed, false);
  assert.equal(evaluation.comparison?.claim, null);
  assert.ok(evaluation.comparison?.failures.includes("review_not_blinded"));
});

test("only a sufficiently large blinded comparison can prove an advantage", () => {
  const evaluation = evaluateMediaCandidates(mediaQualityEvaluationRequestSchema.parse({
    projectId: "quality-eval-5",
    modality: "voice",
    fixtureSetId: "voice-core-v1",
    candidates: [candidate("chatterbox-strong")],
    baselineComparison: {
      targetId: "elevenlabs-reference",
      blinded: true,
      randomizedOrder: true,
      identicalFixtures: true,
      fixtureCount: 40,
      ratingsPerFixture: 3,
      buddyWins: 84,
      baselineWins: 24,
      ties: 12,
      baselineScore: 0.88,
      fixtureSetSha256: hash,
      evidenceSha256: hash,
      evaluatorVersion: "buddy-pairwise-evaluator-v1",
      evidenceReference: "blind-test:quality-eval-5",
    },
  }));
  assert.equal(evaluation.comparisonClaimAllowed, true);
  assert.equal(evaluation.comparison?.claimStatus, "evidence_backed_advantage");
  assert.match(evaluation.comparison?.claim ?? "", /outperformed ElevenLabs/);
});

test("unknown score dimensions invalidate a candidate instead of being ignored", () => {
  const evaluation = evaluateMediaCandidates(mediaQualityEvaluationRequestSchema.parse({
    projectId: "quality-eval-6",
    modality: "voice",
    fixtureSetId: "voice-core-v1",
    candidates: [candidate("chatterbox-extra", { ...voiceDimensions, invented_metric: 1 })],
  }));
  assert.equal(evaluation.winner, null);
  assert.deepEqual(evaluation.candidates[0].unknownDimensions, ["invented_metric"]);
});
