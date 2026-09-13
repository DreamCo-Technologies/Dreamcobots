import assert from "node:assert/strict";
import test from "node:test";

import {
  BUDDY_EXPERT_MODE,
  createBuddyExpertSprint,
  createBuddyInventionProject,
  evaluateBuddyExpertSprint,
} from "../server/expert-mode-policy";

const sprintRequest = {
  sprintId: "expert-week-001",
  goal: "Learn to route every registered DreamCo resource to the right verified task.",
  hoursPerDay: 4,
  learningStyle: "balanced" as const,
  includedDays: [1, 2, 3, 4, 5, 6, 7],
  resourceIds: [],
  focusKeywords: [],
  connectionMethods: ["custom_rest", "mcp_transport"],
  externalRetrievalAuthorized: false,
  privateWorkspaceConfirmed: false,
};

test("Expert Mode builds a seven-day schedule covering every repository resource exactly once", () => {
  const sprint = createBuddyExpertSprint(sprintRequest);
  const scheduled = sprint.days.flatMap((day) => day.resourceIds);

  assert.equal(sprint.days.length, 7);
  assert.equal(sprint.resourceCount, BUDDY_EXPERT_MODE.resource_index.length);
  assert.equal(new Set(scheduled).size, BUDDY_EXPERT_MODE.resource_index.length);
  assert.equal(sprint.includesEveryRepositoryResource, true);
  assert.equal(sprint.status, "private_workspace_confirmation_required");
  assert.equal(sprint.learningStarted, false);
  assert.equal(sprint.externalRequestsStarted, false);
  assert.equal(sprint.masteryClaimed, false);
  assert.match(sprint.feasibility, /routing_and_indexing/);
});

test("Expert Mode rejects unknown resources and connection methods", () => {
  assert.throws(
    () => createBuddyExpertSprint({ ...sprintRequest, resourceIds: ["not-a-registered-resource"] }),
    /Unknown Expert Mode resources/,
  );
  assert.throws(
    () => createBuddyExpertSprint({ ...sprintRequest, connectionMethods: ["magic-direct-connection"] }),
    /Unsupported connection methods/,
  );
});

const passingEvidence = {
  sprintId: "expert-week-001",
  sprintManifestSha256: "a".repeat(64),
  hiddenHoldoutManifestSha256: "b".repeat(64),
  dayEvidence: BUDDY_EXPERT_MODE.days.map((day) => ({
    day: day.day,
    completedResourceIds: day.resource_ids,
    routingScores: [0.88, 0.90, 0.91],
    sourceVerificationScores: [0.94, 0.95, 0.96],
    applicationScores: [0.85, 0.86, 0.87],
    teachBackScores: [0.84, 0.85, 0.86],
    hiddenHoldoutScores: [0.82, 0.83, 0.84],
    evidenceArtifactSha256: String(day.day).repeat(64),
  })),
  ownerReviewed: false,
};

test("Expert Mode proves only bounded routing competency with repeat and holdout evidence", () => {
  const result = evaluateBuddyExpertSprint(passingEvidence);

  assert.equal(result.resourceCoverage.ratio, 1);
  assert.equal(result.gates.every_repository_resource_covered, true);
  assert.equal(result.gates.resources_assigned_to_correct_days, true);
  assert.equal(result.gates.every_day_passed, true);
  assert.equal(result.boundedResourceRoutingProven, true);
  assert.equal(result.status, "bounded_routing_competency_owner_review_required");
  assert.equal(result.universalMasteryClaimed, false);
  assert.equal(result.liveConnectionsClaimed, false);
  assert.equal(result.modelWeightsModified, false);
});

test("Expert Mode rejects evidence assigned to the wrong study day", () => {
  const dayOne = passingEvidence.dayEvidence[0];
  const dayTwo = passingEvidence.dayEvidence[1];
  const result = evaluateBuddyExpertSprint({
    ...passingEvidence,
    dayEvidence: passingEvidence.dayEvidence.map((day) => day.day === 1
      ? { ...dayOne, completedResourceIds: [...dayOne.completedResourceIds, dayTwo.completedResourceIds[0]] }
      : day),
  });

  assert.equal(result.gates.every_repository_resource_covered, true);
  assert.equal(result.gates.resources_assigned_to_correct_days, false);
  assert.equal(result.boundedResourceRoutingProven, false);
});

test("Expert Mode fails the sprint when a hidden holdout score misses the gate", () => {
  const result = evaluateBuddyExpertSprint({
    ...passingEvidence,
    dayEvidence: passingEvidence.dayEvidence.map((day) => day.day === 7
      ? { ...day, hiddenHoldoutScores: [0.40, 0.42, 0.41] }
      : day),
  });

  assert.equal(result.gates.every_day_passed, false);
  assert.equal(result.boundedResourceRoutingProven, false);
  assert.equal(result.status, "expert_sprint_evidence_failed");
});

test("Idea-to-Store builds all stages and product-specific compliance routing without taking external action", () => {
  const project = createBuddyInventionProject({
    projectId: "solar-sensor-001",
    title: "Solar garden safety sensor",
    ideaSummary: "A low-power connected sensor that alerts a homeowner when a garden gate is left open.",
    targetUser: "Homeowners and community gardens",
    country: "United States",
    prototypeType: "electronics",
    budgetUsd: 2_500,
    confidentiality: "private",
    ownerApprovesPublicResearch: false,
  });

  assert.equal(project.stages.length, BUDDY_EXPERT_MODE.invention_navigator.stages.length);
  assert.deepEqual(
    project.productSpecificRegulatorResources.map((item) => item?.id).sort(),
    ["cpsc-business-guidance", "fcc-equipment-authorization"],
  );
  assert.equal(project.status, "private_project_plan_ready");
  assert.equal(project.externalResearchStarted, false);
  assert.equal(project.filingsSubmitted, false);
  assert.equal(project.peopleContacted, false);
  assert.equal(project.purchasesMade, false);
  assert.equal(project.legalAdviceProvided, false);
  assert.equal(project.storeLaunchPerformed, false);
});

test("Idea-to-Store catches a private-project public-research conflict", () => {
  const project = createBuddyInventionProject({
    projectId: "private-invention-001",
    title: "Private invention",
    ideaSummary: "A confidential product concept that requires an owner disclosure decision before public research.",
    targetUser: "A defined customer segment",
    country: "United States",
    prototypeType: "mixed",
    budgetUsd: 0,
    confidentiality: "private",
    ownerApprovesPublicResearch: true,
  });

  assert.equal(project.status, "confidentiality_conflict_owner_review_required");
  assert.equal(project.externalResearchStarted, false);
});
