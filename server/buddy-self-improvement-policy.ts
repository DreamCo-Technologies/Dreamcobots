import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";

import { z } from "zod";

type ImprovementCatalog = {
  schema: string;
  mode: string;
  truth_contract: Record<string, boolean>;
  improvement_loop: Array<{ id: string; gate: string }>;
  hallucination_controls: Array<{ id: string; rule: string }>;
  claim_policy: Record<string, { minimum_evidence: number; verification: string }>;
  threat_controls: string[];
  change_classes: Array<{ id: string; risk: string; required_evidence: string[] }>;
  evaluation_requirements: {
    minimum_holdout_fixtures: number;
    minimum_repetitions: number;
    required_metrics: string[];
    automatic_failures: string[];
  };
  standards_references: Array<{ name: string; url: string; use: string }>;
};

const catalog = JSON.parse(
  readFileSync(resolve(process.cwd(), "config", "buddy-self-improvement.json"), "utf8"),
) as ImprovementCatalog;

const changeClassIds = catalog.change_classes.map((item) => item.id) as [string, ...string[]];
const claimKinds = ["factual", "current_factual", "inference", "estimate", "recommendation", "creative"] as const;
const secretLike = /(?:github_pat_|gh[pousr]_|ghs_|(?:sk|rk)[-_](?:live|test)?|AIza[0-9A-Za-z_-]+|xox[baprs]-|Bearer\s+|BEGIN .*PRIVATE KEY)/i;

const evidenceReferenceSchema = z.object({
  id: z.string().trim().min(3).max(120),
  kind: z.enum(["repository_test", "benchmark", "user_correction", "incident", "official_source", "tool_result"]),
  reference: z.string().trim().min(3).max(500),
  contentHash: z.string().regex(/^[a-f0-9]{16,64}$/),
}).strict();

export const recursiveImprovementRequestSchema = z.object({
  botId: z.string().trim().regex(/^[a-z0-9][a-z0-9-]{1,79}$/),
  objective: z.string().trim().min(10).max(2_000),
  changeClass: z.enum(changeClassIds),
  observations: z.array(z.string().trim().min(5).max(500)).min(1).max(20),
  evidence: z.array(evidenceReferenceSchema).max(50).default([]),
  maximumBudgetUsd: z.number().finite().min(0).max(100_000).default(0),
  allowNetwork: z.boolean().default(false),
  approvePaidRun: z.boolean().default(false),
  approveRelease: z.boolean().default(false),
}).strict();

const claimEvidenceSchema = z.object({
  sourceId: z.string().trim().min(3).max(120),
  sourceType: z.enum(["official_primary", "repository_evidence", "validated_tool", "user_confirmed", "secondary"]),
  retrievedAt: z.string().datetime(),
  contentHash: z.string().regex(/^[a-f0-9]{16,64}$/),
  supportsClaim: z.literal(true),
}).strict();

export const groundingReviewRequestSchema = z.object({
  context: z.enum(["general", "current_events", "code", "financial", "legal", "medical", "government", "emergency"]),
  reviewedAt: z.string().datetime(),
  claims: z.array(z.object({
    id: z.string().trim().min(2).max(120),
    text: z.string().trim().min(1).max(2_000),
    kind: z.enum(claimKinds),
    highStakes: z.boolean().default(false),
    evidence: z.array(claimEvidenceSchema).max(20).default([]),
  }).strict()).min(1).max(100),
}).strict();

function stableId(prefix: string, value: string): string {
  return `${prefix}-${createHash("sha256").update(value).digest("hex").slice(0, 20)}`;
}

function rejectSecrets(values: string[]): void {
  if (values.some((value) => secretLike.test(value))) {
    throw new Error("Improvement evidence must use references and hashes, never raw credentials.");
  }
}

export function createRecursiveImprovementPlan(input: z.input<typeof recursiveImprovementRequestSchema>) {
  const request = recursiveImprovementRequestSchema.parse(input);
  rejectSecrets([
    request.objective,
    ...request.observations,
    ...request.evidence.map((item) => item.reference),
  ]);
  const changeClass = catalog.change_classes.find((item) => item.id === request.changeClass)!;
  const fingerprint = createHash("sha256")
    .update(`${request.botId}:${request.changeClass}:${request.objective}:${JSON.stringify(request.observations)}`)
    .digest("hex")
    .slice(0, 20);
  const externalHeld = request.allowNetwork || request.approvePaidRun || request.maximumBudgetUsd > 0;
  return {
    schema: "dreamco.buddy_recursive_improvement_plan.v1",
    planId: stableId("improvement", fingerprint),
    fingerprint,
    botId: request.botId,
    objective: request.objective,
    mode: catalog.mode,
    status: externalHeld ? "proposal_ready_external_steps_held" : "local_proposal_ready",
    change: {
      class: changeClass.id,
      risk: changeClass.risk,
      requiredEvidence: changeClass.required_evidence,
      reviewBranch: `buddy-improvement/${request.botId}/${fingerprint}`,
    },
    observations: request.observations,
    evidenceReferences: request.evidence,
    loop: catalog.improvement_loop.map((stage, index) => ({
      order: index + 1,
      id: stage.id,
      gate: stage.gate,
      status: index < 2 ? "ready_for_review" : "not_run",
    })),
    evaluation: {
      ...catalog.evaluation_requirements,
      baselineRequired: true,
      signedFixturesRequired: true,
      holdoutIsolationRequired: true,
      failedResultsRetained: true,
    },
    permissions: {
      networkExecuted: false,
      paidRunExecuted: false,
      repositoryWriteExecuted: false,
      productionWriteExecuted: false,
      modelWeightsChanged: false,
      guardrailsChanged: false,
      selfMergeAllowed: false,
      selfGrantedPermissionsAllowed: false,
      releaseApprovedByThisPlan: false,
      requestedMaximumBudgetUsd: request.maximumBudgetUsd,
      requestedNetwork: request.allowNetwork,
      requestedPaidRun: request.approvePaidRun,
      requestedRelease: request.approveRelease,
    },
    release: {
      ownerReviewRequired: true,
      canaryRequired: true,
      rollbackRequired: true,
      exactApprovalMustOccurAfterEvidence: true,
    },
  } as const;
}

function isFreshPrimaryEvidence(evidence: z.infer<typeof claimEvidenceSchema>[], reviewedAt: Date): boolean {
  return evidence.some((item) => {
    const age = reviewedAt.getTime() - new Date(item.retrievedAt).getTime();
    return item.sourceType === "official_primary" && age >= 0 && age <= 30 * 86_400_000;
  });
}

export function createGroundingReview(input: z.input<typeof groundingReviewRequestSchema>) {
  const request = groundingReviewRequestSchema.parse(input);
  rejectSecrets(request.claims.flatMap((claim) => [claim.text, ...claim.evidence.map((item) => item.sourceId)]));
  const reviewedAt = new Date(request.reviewedAt);
  const claims = request.claims.map((claim) => {
    const policy = catalog.claim_policy[claim.kind];
    const evidenceCount = claim.evidence.length;
    const currentEvidenceReady = claim.kind !== "current_factual" || isFreshPrimaryEvidence(claim.evidence, reviewedAt);
    const evidenceReady = evidenceCount >= policy.minimum_evidence && currentEvidenceReady;
    const nonFactual = ["estimate", "recommendation", "creative"].includes(claim.kind);
    const status = claim.highStakes
      ? "qualified_review_required"
      : nonFactual
        ? "label_and_assumptions_required"
        : evidenceReady
          ? "supported"
          : claim.kind === "current_factual"
            ? "fresh_primary_verification_required"
            : "unsupported";
    return {
      id: claim.id,
      kind: claim.kind,
      status,
      evidenceCount,
      evidenceHashes: claim.evidence.map((item) => item.contentHash),
      verificationRule: policy.verification,
      responseInstruction: status === "supported"
        ? "Answer with evidence provenance."
        : status === "label_and_assumptions_required"
          ? "Label the content and state assumptions or tradeoffs."
          : status === "qualified_review_required"
            ? "Provide preparation support only and require qualified human review."
            : "Do not present this claim as fact; state what is unknown and how to verify it.",
    };
  });
  return {
    schema: "dreamco.buddy_grounding_review.v1",
    reviewId: stableId("grounding", `${request.reviewedAt}:${JSON.stringify(claims)}`),
    context: request.context,
    claims,
    summary: {
      total: claims.length,
      supported: claims.filter((claim) => claim.status === "supported").length,
      held: claims.filter((claim) => !["supported", "label_and_assumptions_required"].includes(claim.status)).length,
      qualifiedReviewRequired: claims.filter((claim) => claim.status === "qualified_review_required").length,
    },
    releaseAllowed: claims.every((claim) => ["supported", "label_and_assumptions_required"].includes(claim.status)),
    externalActionTaken: false,
    hallucinationFreeClaimAllowed: false,
  } as const;
}

export function getSelfImprovementCatalog() {
  return catalog;
}
