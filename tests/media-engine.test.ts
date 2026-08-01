import assert from "node:assert/strict";
import test from "node:test";

import {
  buildMediaBenchmarkPlan,
  buildMediaRenderPlan,
  getLocalMediaCatalog,
  mediaBenchmarkPlanRequestSchema,
  mediaRenderPlanRequestSchema,
} from "../server/media-engine";

const hash = "a".repeat(64);

function ownerVoiceRequest(overrides: Record<string, unknown> = {}) {
  return mediaRenderPlanRequestSchema.parse({
    projectId: "voice-test-1",
    mediaType: "voice_replication",
    objective: "Create a consented local narration preview for the owner.",
    script: "This is a signed synthetic fixture.",
    characterRole: "Warm course narrator",
    personalityTraits: { warmth: 0.9, clarity: 1, energy: 0.5 },
    commercialUse: true,
    rights: {
      sourceType: "adult_owner",
      subjectReference: "owner-1",
      sourceReferenceSha256: hash,
      consentReceiptReference: "consent-owner-1",
      ownerIsSubject: true,
      adultConfirmed: true,
      voiceUseApproved: true,
      likenessUseApproved: false,
      commercialUseApproved: true,
      commercialScope: "Owner-approved course narration and advertising for this project.",
      syntheticMediaLabelApproved: true,
      revoked: false,
    },
    ...overrides,
  });
}

test("local media catalog has no paid provider requirement and honest readiness", () => {
  const catalog = getLocalMediaCatalog();
  assert.equal(catalog.policy.paid_provider_required, false);
  assert.ok(catalog.engines.some((engine) => engine.id === "openvoice-v2-local"));
  assert.ok(catalog.engines.some((engine) => engine.id === "chatterbox-local"));
  assert.ok(catalog.engines.every((engine) => !engine.readiness.includes("production_ready")));
});

test("commercial owner voice selects an eligible local adapter without rendering", () => {
  const plan = buildMediaRenderPlan(ownerVoiceRequest({ preferredEngineId: "openvoice-v2-local" }));
  assert.equal(plan.selectedEngine.id, "openvoice-v2-local");
  assert.equal(plan.execution.paidProviderRequired, false);
  assert.equal(plan.execution.renderExecuted, false);
  assert.equal(plan.rights.rawMediaAcceptedByThisRoute, false);
});

test("revoked, minor, and non-owner voice requests are blocked", () => {
  assert.throws(
    () => buildMediaRenderPlan(ownerVoiceRequest({ rights: { ...ownerVoiceRequest().rights, revoked: true } })),
    /revoked/,
  );
  assert.throws(
    () => buildMediaRenderPlan(ownerVoiceRequest({ rights: { ...ownerVoiceRequest().rights, adultConfirmed: false } })),
    /minors/,
  );
  assert.throws(
    () => buildMediaRenderPlan(ownerVoiceRequest({ rights: { ...ownerVoiceRequest().rights, ownerIsSubject: false } })),
    /signed-in owner/,
  );
});

test("licensed performer work requires a written rights receipt", () => {
  assert.throws(
    () => buildMediaRenderPlan(ownerVoiceRequest({
      rights: {
        ...ownerVoiceRequest().rights,
        sourceType: "licensed_adult_performer",
        ownerIsSubject: false,
      },
    })),
    /rights receipt/,
  );
});

test("research-only image engines cannot be selected for commercial output", () => {
  const request = mediaRenderPlanRequestSchema.parse({
    projectId: "image-test-1",
    mediaType: "identity_preserving_image",
    objective: "Create a consented owner character study for a commercial project.",
    preferredEngineId: "instantid-local",
    commercialUse: true,
    rights: {
      sourceType: "adult_owner",
      subjectReference: "owner-1",
      sourceReferenceSha256: hash,
      consentReceiptReference: "consent-owner-1",
      ownerIsSubject: true,
      adultConfirmed: true,
      voiceUseApproved: false,
      likenessUseApproved: true,
      commercialUseApproved: true,
      commercialScope: "Owner-approved commercial character study for this project.",
      syntheticMediaLabelApproved: true,
      revoked: false,
    },
  });
  assert.throws(() => buildMediaRenderPlan(request), /not cleared for commercial/);
});

test("benchmark plans use synthetic fixtures and cannot claim results before a run", () => {
  const request = mediaBenchmarkPlanRequestSchema.parse({
    engineIds: ["openvoice-v2-local", "chatterbox-local"],
    modalities: ["voice"],
    commercialUse: true,
    ownerApprovedSyntheticFixturesOnly: true,
    maxRuntimeMinutes: 20,
  });
  const plan = buildMediaBenchmarkPlan(request);
  assert.equal(plan.resultState, "not_run");
  assert.equal(plan.comparisonClaimAllowed, false);
  assert.equal(plan.limits.externalUploads, false);
  assert.ok(plan.suites.some((suite) => suite.id === "rights_and_safety"));
});

test("external paid references are optional and require comparison approvals", () => {
  const base = {
    engineIds: ["openvoice-v2-local", "chatterbox-local"],
    targetIds: ["buddy-media-core", "elevenlabs-reference"],
    modalities: ["voice"] as const,
    commercialUse: false,
    ownerApprovedSyntheticFixturesOnly: true as const,
    maxRuntimeMinutes: 20,
  };
  assert.throws(
    () => buildMediaBenchmarkPlan(mediaBenchmarkPlanRequestSchema.parse(base)),
    /exact approval/,
  );
  const request = mediaBenchmarkPlanRequestSchema.parse({
    ...base,
    externalComparisonApproved: true,
    paidComparisonApproved: true,
  });
  const plan = buildMediaBenchmarkPlan(request);
  assert.equal(plan.ownedStack.required_external_provider, null);
  assert.equal(plan.externalCallExecuted, false);
  assert.equal(plan.limits.paidCalls, "requires_fresh_execution_approval");
});

test("commercial cloning requires an explicit usage scope", () => {
  assert.throws(
    () => buildMediaRenderPlan(ownerVoiceRequest({
      rights: {
        ...ownerVoiceRequest().rights,
        commercialUseApproved: false,
        commercialScope: undefined,
      },
    })),
    /written usage scope/,
  );
});
