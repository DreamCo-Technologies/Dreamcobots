import assert from "node:assert/strict";
import test from "node:test";
import { createDelegation, decideApprovalGate, updateDependencyStatus } from "./division-orchestration";

test("high risk delegation requires CommandCore approval gate", () => {
  const delegation = createDelegation({
    sourceDivision: "DreamRealEstate",
    sourceWorkflow: "Distressed property acquisition",
    objective: "Need finance and legal support",
    targetDivisions: ["DreamFinance", "DreamLegal", "CommandCore"],
    riskLevel: "high",
    requestedBy: "integration-test",
  });

  assert.equal(delegation.status, "awaiting_approval");
  assert.equal(delegation.approvalGates.length, 1);
  assert.equal(delegation.approvalGates[0]?.approverDivision, "CommandCore");
});

test("delegation transitions to complete once approved and dependencies complete", () => {
  const delegation = createDelegation({
    sourceDivision: "DreamRealEstate",
    sourceWorkflow: "Portfolio buyout",
    objective: "Coordinate finance, legal, and market support",
    targetDivisions: ["DreamFinance", "DreamLegal"],
    riskLevel: "high",
    requestedBy: "integration-test",
  });
  const gateId = delegation.approvalGates[0]!.id;
  const approved = decideApprovalGate(delegation, gateId, "approved", "CommandCore");
  assert.equal(approved.status, "pending");

  const depA = approved.dependencies[0]!.id;
  const depB = approved.dependencies[1]!.id;
  const inProgress = updateDependencyStatus(approved, depA, "in_progress");
  assert.equal(inProgress.status, "in_progress");

  const finishedA = updateDependencyStatus(inProgress, depA, "complete");
  const finishedB = updateDependencyStatus(finishedA, depB, "complete");
  assert.equal(finishedB.status, "complete");
});
