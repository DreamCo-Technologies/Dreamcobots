import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";

import { z } from "zod";

type OrganizationRecord = {
  id: string;
  name: string;
  capabilityEvidenceStatus?: string;
  evidenceStatus?: string;
  tools: string[];
  commonUserJobs: string[];
  liveBenchmarksCompleted?: number;
};

type OrganizationRegistry = {
  schema: string;
  summary: Record<string, number>;
  userNeedTaxonomy: Array<{ id: string; description: string }>;
  benchmarkDimensions: string[];
  benchmarkWorkflow: string[];
  existingProviders: OrganizationRecord[];
  allianceMembers: OrganizationRecord[];
};

const registryPath = resolve(process.cwd(), "config/generated/ai_organization_intelligence.json");

export function loadOrganizationIntelligenceRegistry(): OrganizationRegistry {
  return JSON.parse(readFileSync(registryPath, "utf8")) as OrganizationRegistry;
}

export const organizationBenchmarkPlanRequestSchema = z.object({
  ownerProfileId: z.string().trim().min(3).max(96).regex(/^[A-Za-z0-9_.:-]+$/),
  organizationIds: z.array(z.string().trim().min(3).max(160).regex(/^[a-z0-9-]+$/)).min(1).max(300),
  userNeedIds: z.array(z.string().trim().min(3).max(80).regex(/^[a-z0-9_]+$/)).min(1).max(20),
  signedFixturesPerNeed: z.number().int().min(1).max(20).default(3),
  maxConcurrency: z.number().int().min(1).max(32).default(8),
  allowNetwork: z.boolean().default(false),
  approveNetworkForThisRun: z.boolean().default(false),
  maximumPaidBudgetUsd: z.number().finite().min(0).max(10_000).default(0),
  approvePaidBudgetForThisRun: z.boolean().default(false),
}).strict();

export type OrganizationBenchmarkPlanRequest = z.infer<typeof organizationBenchmarkPlanRequestSchema>;

export function createOrganizationBenchmarkPlan(input: OrganizationBenchmarkPlanRequest) {
  const request = organizationBenchmarkPlanRequestSchema.parse(input);
  const registry = loadOrganizationIntelligenceRegistry();
  const organizations = [...registry.existingProviders, ...registry.allianceMembers];
  const organizationMap = new Map(organizations.map((item) => [item.id, item]));
  const needMap = new Map(registry.userNeedTaxonomy.map((item) => [item.id, item]));
  const selectedOrganizations = [...new Set(request.organizationIds)].map((id) => {
    const organization = organizationMap.get(id);
    if (!organization) throw new Error(`Unknown organization intelligence id: ${id}`);
    return organization;
  });
  const selectedNeeds = [...new Set(request.userNeedIds)].map((id) => {
    const need = needMap.get(id);
    if (!need) throw new Error(`Unknown organization benchmark user need: ${id}`);
    return need;
  });
  const requiresResearch = selectedOrganizations.some((item) =>
    (item.capabilityEvidenceStatus || item.evidenceStatus || "").includes("research_required"),
  );
  let status = "local_catalog_plan_ready";
  if (request.allowNetwork && !request.approveNetworkForThisRun) status = "network_approval_required";
  else if (request.maximumPaidBudgetUsd > 0 && !request.approvePaidBudgetForThisRun) status = "paid_budget_approval_required";
  else if (request.allowNetwork && requiresResearch) status = "official_source_research_required";
  else if (request.allowNetwork) status = "configured_adapters_and_exact_versions_required";

  const totalCases = selectedOrganizations.length * selectedNeeds.length * request.signedFixturesPerNeed;
  return {
    schema: "dreamco.organization_benchmark_plan.v1",
    planId: `organization-benchmark-${createHash("sha256")
      .update([request.ownerProfileId, ...selectedOrganizations.map((item) => item.id), ...selectedNeeds.map((item) => item.id)].join("|"))
      .digest("hex")
      .slice(0, 16)}`,
    status,
    organizations: selectedOrganizations.map((item) => ({
      id: item.id,
      name: item.name,
      declaredTools: item.tools.length,
      declaredUserJobs: item.commonUserJobs.length,
      evidenceStatus: item.capabilityEvidenceStatus || item.evidenceStatus || "research_required",
      liveBenchmarksCompleted: 0,
    })),
    userNeeds: selectedNeeds,
    benchmarkDimensions: registry.benchmarkDimensions,
    workflow: registry.benchmarkWorkflow,
    capacity: {
      organizationCount: selectedOrganizations.length,
      userNeedCount: selectedNeeds.length,
      signedFixturesPerNeed: request.signedFixturesPerNeed,
      totalCases,
      maxConcurrency: request.maxConcurrency,
      plannedWaves: Math.ceil(totalCases / request.maxConcurrency),
    },
    permissions: {
      network: request.allowNetwork && request.approveNetworkForThisRun,
      maximumPaidBudgetUsd: request.approvePaidBudgetForThisRun ? request.maximumPaidBudgetUsd : 0,
      credentialValuesAccepted: false,
      productionRoutingChanges: false,
    },
    executionPerformed: false,
    permanentBestClaimed: false,
    liveEvidenceRecorded: 0,
  } as const;
}
