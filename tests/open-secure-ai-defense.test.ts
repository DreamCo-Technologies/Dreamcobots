import assert from "node:assert/strict";
import test from "node:test";

import {
  createDefenseAssessment,
  createDefensiveSecurityReviewPlan,
  createGitHubProfileConnectionPlan,
  createModelDiscoveryPlan,
  createOpenSourceUpgradePlan,
  OPEN_SECURE_AI_DEFENSE_CATALOG,
} from "../server/open-secure-ai-defense";

const completeAssessment = {
  userProfileId: "owner-123",
  sourceKind: "model_weights" as const,
  sourceUrl: "https://huggingface.co/example/defense-model",
  exactRevision: "a1b2c3d4e5f6",
  declaredLicense: "Apache-2.0",
  intendedUse: "owned_system_hardening" as const,
  ownerConfirmsRights: true,
  checksum: `sha256:${"a".repeat(64)}`,
  signatureEvidence: "sigstore-bundle:artifact-123",
  sbomReference: "sbom:spdx-artifact-123",
  provenanceReference: "slsa:provenance-artifact-123",
  modelCardReference: "https://huggingface.co/example/defense-model",
  artifactFormat: "safetensors",
  trustRemoteCode: false,
  networkDuringBuild: false,
  requestsProtectedBranchWrite: false,
  requestsAutomaticMerge: false,
  containsUnredactedSecrets: false,
};

test("defense catalog is broad, current, and truthful about connections", () => {
  assert.ok(OPEN_SECURE_AI_DEFENSE_CATALOG.alliance_reference_tools.length >= 6);
  assert.ok(OPEN_SECURE_AI_DEFENSE_CATALOG.openssf_projects.length >= 23);
  assert.ok(OPEN_SECURE_AI_DEFENSE_CATALOG.model_discovery_sources.length >= 8);
  assert.equal(OPEN_SECURE_AI_DEFENSE_CATALOG.truth_contract.catalog_entry_means_connected, false);
  assert.equal(OPEN_SECURE_AI_DEFENSE_CATALOG.truth_contract.alliance_membership_claimed, false);
  assert.equal(OPEN_SECURE_AI_DEFENSE_CATALOG.model_discovery_sources.some((source) => source.connection_status === "connected"), false);
});

test("complete signed model evidence becomes a sandbox candidate without execution", () => {
  const result = createDefenseAssessment(completeAssessment);
  assert.equal(result.status, "sandbox_candidate");
  assert.equal(result.riskScore, 0);
  assert.equal(result.executionPerformed, false);
  assert.equal(result.sourceDownloaded, false);
  assert.match(result.assessmentId, /^def-[a-f0-9]{16}$/);
});

test("floating revisions, remote code, unsafe formats, and branch writes are blocked", () => {
  const result = createDefenseAssessment({
    ...completeAssessment,
    exactRevision: "main",
    artifactFormat: "pickle",
    trustRemoteCode: true,
    requestsProtectedBranchWrite: true,
    requestsAutomaticMerge: true,
  });
  assert.equal(result.status, "blocked");
  const findingIds = new Set(result.findings.map((row) => row.id));
  for (const expected of ["floating-revision", "remote-code", "protected-branch", "automatic-merge", "unsafe-model-format"]) {
    assert.equal(findingIds.has(expected), true, expected);
  }
});

test("missing supply-chain evidence requires review", () => {
  const result = createDefenseAssessment({
    userProfileId: "owner-123",
    sourceKind: "repository",
    sourceUrl: "https://github.com/example/defense-tool",
    exactRevision: "4d5e6f7a8b9c",
    declaredLicense: "MIT",
    intendedUse: "defensive_evaluation",
    ownerConfirmsRights: true,
    trustRemoteCode: false,
    networkDuringBuild: false,
    requestsProtectedBranchWrite: false,
    requestsAutomaticMerge: false,
    containsUnredactedSecrets: false,
  });
  assert.equal(result.status, "review_required");
  assert.ok(result.findings.some((row) => row.id === "missing-sbom"));
  assert.ok(result.findings.some((row) => row.id === "missing-provenance"));
});

test("source URLs reject credentials and unreviewed hosts", () => {
  assert.throws(() => createDefenseAssessment({
    ...completeAssessment,
    sourceUrl: "https://token@huggingface.co/example/model",
  }), /without credentials/);
  assert.throws(() => createDefenseAssessment({
    ...completeAssessment,
    sourceUrl: "https://unreviewed.example/model",
  }), /manual trust review/);
});

test("GitHub profile plans use OAuth identity, app installations, and no raw tokens", () => {
  const plan = createGitHubProfileConnectionPlan({
    userProfileId: "owner-123",
    githubLogin: "dreamco-owner",
    callbackOrigin: "https://app.example.com/auth/github/callback",
    repositoryAllowlist: ["DreamCo-Technologies/Dreamcobots"],
    requestedPermissions: ["contents:read", "contents:write", "pull_requests:write", "checks:read"],
    userApprovedConnectionIntent: true,
  });
  assert.equal(plan.status, "deployment_configuration_required");
  assert.equal(plan.connected, false);
  assert.equal(plan.identity.protocol, "oauth_pkce");
  assert.equal(plan.repositoryAuthority.protocol, "github_app_installation");
  assert.equal(plan.credentialHandling.browserAcceptsRawToken, false);
  assert.equal(plan.credentialHandling.publicApiReturnsRawToken, false);
});

test("model discovery plans do not invent live models or quality results", () => {
  const plan = createModelDiscoveryPlan({
    sourceIds: ["openai", "gemini", "hugging-face", "ollama"],
    taskCategories: ["coding", "agents", "safety"],
    allowNetwork: false,
    approvePaidDiscovery: false,
    maxBudgetUsd: 0,
  });
  assert.equal(plan.status, "network_approval_required");
  assert.equal(plan.discoveryPerformed, false);
  assert.equal(plan.liveModelsCalled, 0);
  assert.equal(plan.qualityClaimsProduced, 0);
});

test("upgrade plans require allowlisted repositories, passed evidence, and exact approval", () => {
  const assessment = createDefenseAssessment(completeAssessment);
  const base = {
    userProfileId: "owner-123",
    githubLogin: "dreamco-owner",
    targetRepository: "DreamCo-Technologies/Dreamcobots",
    repositoryAllowlist: ["DreamCo-Technologies/Dreamcobots"],
    baseBranch: "main",
    objective: "Add the verified defensive model adapter behind an approval gate.",
    assessmentId: assessment.assessmentId,
    assessmentStatus: assessment.status,
    exactApproval: true,
  };
  const plan = createOpenSourceUpgradePlan(base);
  assert.equal(plan.draftPullRequestOnly, true);
  assert.equal(plan.automaticMerge, false);
  assert.equal(plan.executionPerformed, false);
  assert.match(plan.repository.reviewBranch, /^buddy\/secure-upgrade-/);
  assert.throws(() => createOpenSourceUpgradePlan({ ...base, exactApproval: false }), /Exact owner approval/);
  assert.throws(() => createOpenSourceUpgradePlan({ ...base, targetRepository: "other/project" }), /outside this user's/);
});

test("authorized security reviews are scoped, non-destructive, and never guarantee protection", () => {
  const plan = createDefensiveSecurityReviewPlan({
    ownerProfileId: "owner-123",
    organizationName: "Owner Test Company",
    targetKind: "owned_web_app",
    targetReference: "asset:owner-web-app",
    scope: ["https://owner.example", "/login", "/api/health"],
    mode: "passive_review",
    ownerConfirmsAuthority: true,
    authorizationReference: "authorization:security-review-2026-08",
    productionTarget: true,
    exactApprovalForSafeActiveChecks: false,
    rateLimitRequestsPerMinute: 30,
  });
  assert.equal(plan.status, "passive_review_ready");
  assert.equal(plan.controls.rawCredentialsAccepted, false);
  assert.equal(plan.controls.stopOnUnexpectedAccess, true);
  assert.equal(plan.zeroBreachGuaranteed, false);
  assert.equal(plan.executionPerformed, false);
  assert.ok(plan.prohibitedChecks.some((check) => check.includes("denial of service")));
});

test("safe active production reviews require authority, exact approval, and a maintenance window", () => {
  const base = {
    ownerProfileId: "owner-123",
    organizationName: "Owner Test Company",
    targetKind: "owned_api" as const,
    targetReference: "asset:owner-api",
    scope: ["https://api.owner.example"],
    mode: "safe_active_validation" as const,
    ownerConfirmsAuthority: true,
    authorizationReference: "authorization:security-review-2026-08",
    productionTarget: true,
    exactApprovalForSafeActiveChecks: true,
    rateLimitRequestsPerMinute: 15,
  };
  assert.throws(() => createDefensiveSecurityReviewPlan(base), /maintenance window/);
  assert.throws(() => createDefensiveSecurityReviewPlan({ ...base, ownerConfirmsAuthority: false }), /must confirm testing authority/);
  const plan = createDefensiveSecurityReviewPlan({ ...base, maintenanceWindowReference: "window:approved-2026-08-02" });
  assert.equal(plan.status, "isolated_runner_and_monitoring_required");
});
