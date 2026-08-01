import { createHash } from "node:crypto";
import { z } from "zod";

import defenseCatalog from "../config/buddy-open-secure-ai-defense.json";

type DefenseCatalog = typeof defenseCatalog;
type FindingSeverity = "info" | "review" | "blocked";

const FLOATING_REVISIONS = new Set(["main", "master", "latest", "head", "stable", "dev", "develop", "nightly"]);
const SAFE_MODEL_FORMATS = new Set(["safetensors", "gguf", "onnx", "tflite"]);
const TOKEN_LIKE = /(?:github_pat_|gh[opsu]_|ghs_|(?:sk|rk)_(?:live|test)_|BEGIN .*PRIVATE KEY)/i;
const SOURCE_HOSTS = new Set([
  "github.com",
  "gitlab.com",
  "codeberg.org",
  "huggingface.co",
  "pypi.org",
  "npmjs.com",
  "www.npmjs.com",
  "ghcr.io",
]);

export const OPEN_SECURE_AI_DEFENSE_CATALOG = defenseCatalog as DefenseCatalog;

const evidenceReference = z.string().trim().min(3).max(512).refine(
  (value) => !TOKEN_LIKE.test(value),
  "Evidence must be a reference or URL, never a credential value.",
);

export const defenseAssessmentRequestSchema = z.object({
  userProfileId: z.string().trim().min(3).max(96).regex(/^[A-Za-z0-9_.:-]+$/),
  sourceKind: z.enum(["repository", "package", "container", "model_weights", "agent_tool"]),
  sourceUrl: z.string().url().max(2_048),
  exactRevision: z.string().trim().min(4).max(200).regex(/^[A-Za-z0-9][A-Za-z0-9._/+:-]*$/),
  declaredLicense: z.string().trim().min(2).max(160),
  intendedUse: z.enum(["defensive_evaluation", "compatibility_testing", "owned_system_hardening", "security_education"]),
  ownerConfirmsRights: z.boolean(),
  checksum: z.string().trim().regex(/^sha256:[a-f0-9]{64}$/i).optional(),
  signatureEvidence: evidenceReference.optional(),
  sbomReference: evidenceReference.optional(),
  provenanceReference: evidenceReference.optional(),
  modelCardReference: evidenceReference.optional(),
  artifactFormat: z.string().trim().min(2).max(40).optional(),
  trustRemoteCode: z.boolean().default(false),
  networkDuringBuild: z.boolean().default(false),
  requestsProtectedBranchWrite: z.boolean().default(false),
  requestsAutomaticMerge: z.boolean().default(false),
  containsUnredactedSecrets: z.boolean().default(false),
}).strict();

export const githubProfileConnectionPlanRequestSchema = z.object({
  userProfileId: z.string().trim().min(3).max(96).regex(/^[A-Za-z0-9_.:-]+$/),
  githubLogin: z.string().trim().min(1).max(39).regex(/^[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?$/),
  callbackOrigin: z.string().url().max(512),
  repositoryAllowlist: z.array(z.string().regex(/^[A-Za-z0-9_.-]+\/[A-Za-z0-9_.-]+$/)).min(1).max(50),
  requestedPermissions: z.array(z.enum([
    "metadata:read",
    "contents:read",
    "contents:write",
    "pull_requests:write",
    "checks:read",
    "issues:write",
  ])).max(6).default(["metadata:read", "contents:read", "pull_requests:write"]),
  userApprovedConnectionIntent: z.boolean(),
}).strict();

export const modelDiscoveryPlanRequestSchema = z.object({
  sourceIds: z.array(z.string().trim().min(1).max(80)).min(1).max(8),
  taskCategories: z.array(z.enum([
    "reasoning",
    "coding",
    "agents",
    "vision",
    "audio",
    "video",
    "multilingual",
    "embeddings",
    "safety",
  ])).min(1).max(9),
  allowNetwork: z.boolean().default(false),
  approvePaidDiscovery: z.boolean().default(false),
  maxBudgetUsd: z.number().min(0).max(10_000).default(0),
}).strict();

export const openSourceUpgradePlanRequestSchema = z.object({
  userProfileId: z.string().trim().min(3).max(96).regex(/^[A-Za-z0-9_.:-]+$/),
  githubLogin: z.string().trim().min(1).max(39),
  targetRepository: z.string().regex(/^[A-Za-z0-9_.-]+\/[A-Za-z0-9_.-]+$/),
  repositoryAllowlist: z.array(z.string().regex(/^[A-Za-z0-9_.-]+\/[A-Za-z0-9_.-]+$/)).min(1).max(50),
  baseBranch: z.string().trim().min(1).max(120).regex(/^[A-Za-z0-9][A-Za-z0-9._/-]*$/),
  objective: z.string().trim().min(10).max(2_000),
  assessmentId: z.string().regex(/^def-[a-f0-9]{16}$/),
  assessmentStatus: z.enum(["blocked", "review_required", "sandbox_candidate"]),
  exactApproval: z.boolean(),
}).strict();

export const defensiveSecurityReviewRequestSchema = z.object({
  ownerProfileId: z.string().trim().min(3).max(96).regex(/^[A-Za-z0-9_.:-]+$/),
  organizationName: z.string().trim().min(2).max(160),
  targetKind: z.enum(["owned_web_app", "owned_api", "owned_repository", "owned_cloud_configuration", "owned_network"]),
  targetReference: evidenceReference,
  scope: z.array(z.string().trim().min(1).max(300)).min(1).max(100),
  mode: z.enum(["passive_review", "safe_active_validation"]).default("passive_review"),
  ownerConfirmsAuthority: z.boolean(),
  authorizationReference: evidenceReference,
  productionTarget: z.boolean().default(false),
  maintenanceWindowReference: evidenceReference.optional(),
  exactApprovalForSafeActiveChecks: z.boolean().default(false),
  rateLimitRequestsPerMinute: z.number().int().min(1).max(120).default(30),
}).strict();

export type DefenseAssessmentRequest = z.infer<typeof defenseAssessmentRequestSchema>;
export type GitHubProfileConnectionPlanRequest = z.infer<typeof githubProfileConnectionPlanRequestSchema>;
export type ModelDiscoveryPlanRequest = z.infer<typeof modelDiscoveryPlanRequestSchema>;
export type OpenSourceUpgradePlanRequest = z.infer<typeof openSourceUpgradePlanRequestSchema>;
export type DefensiveSecurityReviewRequest = z.infer<typeof defensiveSecurityReviewRequestSchema>;

function unique<T>(items: T[]) {
  return [...new Set(items)];
}

function validateSourceUrl(raw: string) {
  const source = new URL(raw);
  if (source.protocol !== "https:" || source.username || source.password || source.search || source.hash) {
    throw new Error("Use an official HTTPS source URL without credentials, query strings, or fragments.");
  }
  if (!SOURCE_HOSTS.has(source.hostname.toLowerCase())) {
    throw new Error("The source host needs a manual trust review before Buddy may inspect it.");
  }
  return source;
}

function finding(id: string, severity: FindingSeverity, title: string, action: string) {
  return { id, severity, title, action } as const;
}

function stableAssessmentId(request: DefenseAssessmentRequest) {
  const digest = createHash("sha256")
    .update([request.userProfileId, request.sourceUrl, request.exactRevision, request.intendedUse].join("|"))
    .digest("hex")
    .slice(0, 16);
  return `def-${digest}`;
}

export function createDefenseAssessment(input: DefenseAssessmentRequest) {
  const request = defenseAssessmentRequestSchema.parse(input);
  const source = validateSourceUrl(request.sourceUrl);
  const findings: ReturnType<typeof finding>[] = [];

  if (FLOATING_REVISIONS.has(request.exactRevision.toLowerCase())) {
    findings.push(finding("floating-revision", "blocked", "Revision is mutable", "Pin an exact commit, immutable release tag, package version, image digest, or model revision."));
  }
  if (!request.ownerConfirmsRights) {
    findings.push(finding("rights-unconfirmed", "blocked", "Usage rights are not confirmed", "Confirm the exact source, model, data, and dependency terms before evaluation."));
  }
  if (request.containsUnredactedSecrets) {
    findings.push(finding("secret-material", "blocked", "Unredacted secrets are present", "Remove credentials and use approved vault references."));
  }
  if (request.trustRemoteCode) {
    findings.push(finding("remote-code", "blocked", "Remote model code was requested", "Use a reviewed local adapter with remote code disabled."));
  }
  if (request.requestsProtectedBranchWrite) {
    findings.push(finding("protected-branch", "blocked", "Protected-branch write was requested", "Use a dedicated review branch and draft pull request."));
  }
  if (request.requestsAutomaticMerge) {
    findings.push(finding("automatic-merge", "blocked", "Automatic merge was requested", "Require tests and exact owner approval before merge."));
  }
  if (request.sourceKind === "model_weights") {
    const format = request.artifactFormat?.toLowerCase();
    if (!format || !SAFE_MODEL_FORMATS.has(format)) {
      findings.push(finding("unsafe-model-format", "blocked", "Model format is missing or unsafe", "Use safetensors, GGUF, ONNX, or TFLite and verify the exact artifact."));
    }
    if (!request.modelCardReference) {
      findings.push(finding("missing-model-card", "review", "Model card evidence is missing", "Record the exact model card, license, limitations, and intended use."));
    }
  }
  if (!request.checksum) {
    findings.push(finding("missing-checksum", "review", "SHA-256 evidence is missing", "Calculate and record the artifact checksum before loading it."));
  }
  if (!request.signatureEvidence) {
    findings.push(finding("missing-signature", "review", "Signature evidence is missing", "Verify a publisher signature or complete a documented manual provenance review."));
  }
  if (!request.sbomReference) {
    findings.push(finding("missing-sbom", "review", "SBOM evidence is missing", "Generate an SBOM and map vulnerabilities before integration."));
  }
  if (!request.provenanceReference) {
    findings.push(finding("missing-provenance", "review", "Build provenance is missing", "Record source, builder, dependency lock, and reproducible artifact evidence."));
  }
  if (request.networkDuringBuild) {
    findings.push(finding("network-request", "review", "Build network access was requested", "Approve a one-run destination allowlist and capture every request."));
  }

  const hasBlocked = findings.some((row) => row.severity === "blocked");
  const hasReview = findings.some((row) => row.severity === "review");
  const status = hasBlocked ? "blocked" : hasReview ? "review_required" : "sandbox_candidate";
  const riskScore = Math.min(100,
    findings.reduce((score, row) => score + (row.severity === "blocked" ? 24 : row.severity === "review" ? 8 : 1), 0),
  );

  return {
    schema: "dreamco.buddy_defense_assessment.v1",
    assessmentId: stableAssessmentId(request),
    status,
    riskScore,
    source: {
      kind: request.sourceKind,
      url: source.toString(),
      host: source.hostname,
      exactRevision: request.exactRevision,
      declaredLicense: request.declaredLicense,
      artifactFormat: request.artifactFormat ?? null,
    },
    intendedUse: request.intendedUse,
    findings,
    evidence: {
      checksum: request.checksum ?? null,
      signature: request.signatureEvidence ?? null,
      sbom: request.sbomReference ?? null,
      provenance: request.provenanceReference ?? null,
      modelCard: request.modelCardReference ?? null,
    },
    nextStage: status === "sandbox_candidate" ? "owner_approved_disposable_sandbox" : status === "review_required" ? "complete_missing_evidence" : "resolve_blocking_findings",
    executionPerformed: false,
    sourceDownloaded: false,
    connectionEstablished: false,
    controls: OPEN_SECURE_AI_DEFENSE_CATALOG.open_source_upgrade_contract,
  } as const;
}

function isAllowedCallbackOrigin(raw: string) {
  const url = new URL(raw);
  if (url.username || url.password || url.search || url.hash) return false;
  if (url.protocol === "https:") return true;
  return url.protocol === "http:" && ["127.0.0.1", "localhost", "::1"].includes(url.hostname);
}

export function createGitHubProfileConnectionPlan(
  input: GitHubProfileConnectionPlanRequest,
  readiness = { oauthClientIdConfigured: false, githubAppConfigured: false, encryptedVaultConfigured: false },
) {
  const request = githubProfileConnectionPlanRequestSchema.parse(input);
  if (!isAllowedCallbackOrigin(request.callbackOrigin)) {
    throw new Error("GitHub callbacks require HTTPS, except an owner-controlled loopback address for local development.");
  }
  const permissions = unique(["metadata:read", ...request.requestedPermissions]);
  const configured = readiness.oauthClientIdConfigured && readiness.githubAppConfigured && readiness.encryptedVaultConfigured;
  const status = !request.userApprovedConnectionIntent
    ? "owner_approval_required"
    : configured
      ? "user_authorization_required"
      : "deployment_configuration_required";
  return {
    schema: "dreamco.buddy_github_profile_connection_plan.v1",
    status,
    userProfileId: request.userProfileId,
    expectedGitHubLogin: request.githubLogin,
    callbackOrigin: new URL(request.callbackOrigin).origin,
    repositoryAllowlist: unique(request.repositoryAllowlist),
    identity: {
      protocol: "oauth_pkce",
      scopes: ["read:user"],
      authorizationPerformed: false,
    },
    repositoryAuthority: {
      protocol: "github_app_installation",
      permissions,
      installationPerformed: false,
      organizationWideAccess: false,
    },
    credentialHandling: {
      browserAcceptsRawToken: false,
      publicApiReturnsRawToken: false,
      storage: "encrypted_vault_reference_only",
      rotationAndRevocationRequired: true,
    },
    readiness,
    connected: false,
    connectionHealthVerified: false,
    requiredSteps: [
      "configure the OAuth client and exact callback URL",
      "install the repository app only on owner-selected repositories",
      "complete owner authorization and verify the returned GitHub identity",
      "store only encrypted credential references under the user profile",
      "run a read-only health check and record granted permissions",
    ],
  } as const;
}

export function createModelDiscoveryPlan(input: ModelDiscoveryPlanRequest) {
  const request = modelDiscoveryPlanRequestSchema.parse(input);
  const sourceMap = new Map(OPEN_SECURE_AI_DEFENSE_CATALOG.model_discovery_sources.map((source) => [source.id, source]));
  const sources = unique(request.sourceIds).map((id) => {
    const source = sourceMap.get(id);
    if (!source) throw new Error(`Unknown model discovery source: ${id}`);
    return source;
  });
  const hosted = sources.filter((source) => ["hosted_api", "hosted_and_open_weight"].includes(source.access));
  const status = !request.allowNetwork && hosted.length
    ? "network_approval_required"
    : request.allowNetwork && request.approvePaidDiscovery && request.maxBudgetUsd <= 0
      ? "positive_budget_required"
      : request.allowNetwork
        ? "configured_discovery_adapters_required"
        : "local_discovery_plan_ready";
  return {
    schema: "dreamco.buddy_model_discovery_plan.v1",
    status,
    sources,
    taskCategories: unique(request.taskCategories),
    currentOpenModelWatchlist: OPEN_SECURE_AI_DEFENSE_CATALOG.priority_open_model_watchlist_2026,
    maxBudgetUsd: request.maxBudgetUsd,
    networkApprovedForThisPlan: request.allowNetwork,
    paidDiscoveryApprovedForThisPlan: request.approvePaidDiscovery,
    discoveryPerformed: false,
    liveModelsCalled: 0,
    qualityClaimsProduced: 0,
    evidenceRequired: [
      "exact model id and revision",
      "official source and access terms",
      "task-matched signed fixtures",
      "latency, resource, cost, safety, and failure results",
      "UTC observation time and adapter version",
    ],
  } as const;
}

function objectiveSlug(objective: string) {
  return objective.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "").slice(0, 36) || "upgrade";
}

export function createOpenSourceUpgradePlan(input: OpenSourceUpgradePlanRequest) {
  const request = openSourceUpgradePlanRequestSchema.parse(input);
  if (!request.repositoryAllowlist.includes(request.targetRepository)) {
    throw new Error("The target repository is outside this user's approved repository allowlist.");
  }
  if (request.assessmentStatus !== "sandbox_candidate") {
    throw new Error("Complete the defense assessment before preparing an upgrade pull request.");
  }
  if (!request.exactApproval) {
    throw new Error("Exact owner approval is required to prepare a repository upgrade plan.");
  }
  const branchName = `buddy/secure-upgrade-${objectiveSlug(request.objective)}-${request.assessmentId.slice(-6)}`;
  return {
    schema: "dreamco.buddy_open_source_upgrade_plan.v1",
    status: "github_connection_and_sandbox_execution_required",
    owner: { userProfileId: request.userProfileId, githubLogin: request.githubLogin },
    repository: { name: request.targetRepository, baseBranch: request.baseBranch, reviewBranch: branchName },
    objective: request.objective,
    assessmentId: request.assessmentId,
    stages: [
      "verify the user GitHub identity and repository installation",
      "create a review branch from the selected base revision",
      "retrieve only the approved source revision into quarantine",
      "verify signature, checksum, license, SBOM, provenance, and vulnerability evidence",
      "build and test in a disposable non-root sandbox with network off by default",
      "compare behavior, security, cost, and dependency changes",
      "prepare a signed evidence packet and draft pull request",
      "wait for owner review before merge, deployment, or publishing",
    ],
    protectedBranchWrite: false,
    draftPullRequestOnly: true,
    automaticMerge: false,
    automaticPublish: false,
    executionPerformed: false,
  } as const;
}

export function createDefensiveSecurityReviewPlan(input: DefensiveSecurityReviewRequest) {
  const request = defensiveSecurityReviewRequestSchema.parse(input);
  if (!request.ownerConfirmsAuthority) {
    throw new Error("The asset owner or authorized administrator must confirm testing authority.");
  }
  if (request.mode === "safe_active_validation" && !request.exactApprovalForSafeActiveChecks) {
    throw new Error("Safe active checks require exact approval for this assessment.");
  }
  if (request.productionTarget && request.mode === "safe_active_validation" && !request.maintenanceWindowReference) {
    throw new Error("Production safe-active checks require a documented maintenance window.");
  }
  const reviewId = `security-review-${createHash("sha256")
    .update([request.ownerProfileId, request.organizationName, request.targetKind, request.targetReference, ...request.scope].join("|"))
    .digest("hex")
    .slice(0, 16)}`;
  return {
    schema: "dreamco.defensive_security_review_plan.v1",
    reviewId,
    status: request.mode === "passive_review" ? "passive_review_ready" : "isolated_runner_and_monitoring_required",
    organizationName: request.organizationName,
    target: {
      kind: request.targetKind,
      reference: request.targetReference,
      scope: unique(request.scope),
      production: request.productionTarget,
    },
    authorization: {
      authorityConfirmed: true,
      evidenceReference: request.authorizationReference,
      exactSafeActiveApproval: request.exactApprovalForSafeActiveChecks,
      maintenanceWindowReference: request.maintenanceWindowReference ?? null,
    },
    allowedChecks: [
      "security headers, TLS, and public configuration",
      "dependency, lockfile, SBOM, and known-vulnerability review",
      "secret scanning against redacted repository material",
      "authentication and authorization design review",
      "synthetic-account access-control fixtures",
      "rate-limit and abuse-control configuration review",
      "logging, backup, recovery, and incident-readiness review",
      "safe input-validation fixtures with no persistence",
    ],
    prohibitedChecks: [
      "credential guessing, password spraying, or phishing",
      "destructive payloads or data modification",
      "denial of service or resource exhaustion",
      "persistence, malware, evasion, or lateral movement",
      "testing third-party assets outside written scope",
      "accessing real customer data or private communications",
    ],
    controls: {
      maximumRequestsPerMinute: request.rateLimitRequestsPerMinute,
      rawCredentialsAccepted: false,
      syntheticAccountsOnly: true,
      stopOnUnexpectedAccess: true,
      evidenceRedactionRequired: true,
      ownerVisibleAuditLogRequired: true,
      emergencyStopRequired: true,
    },
    reportPurpose: "Show verified security gaps and practical remediation priorities without fear-based or guaranteed-security claims.",
    zeroBreachGuaranteed: false,
    executionPerformed: false,
  } as const;
}
