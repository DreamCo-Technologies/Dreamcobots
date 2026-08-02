import { createHash } from "node:crypto";

import { z } from "zod";

import {
  DAILY_BENCHMARK_WORKER_ROLES,
  DIVISION_DOMAIN_PROFILES,
  OFFICIAL_AI_ALLIANCE_WATCH,
  PRODUCTION_READINESS_GATES,
  SAFE_AI_TRAINING_CONTRACT,
  UNIVERSAL_CONNECTOR_LIFECYCLE,
} from "../shared/division-production-contract";

const divisionNames = Object.keys(DIVISION_DOMAIN_PROFILES);
const divisionName = z.string().trim().refine((value) => divisionNames.includes(value), "Unknown DreamCo division");

export const dailyDivisionBenchmarkRequestSchema = z.object({
  ownerProfileId: z.string().trim().min(3).max(96).regex(/^[A-Za-z0-9_.:-]+$/),
  divisions: z.array(divisionName).min(1).max(45),
  signedFixturesPerDivision: z.number().int().min(1).max(100).default(10),
  maxConcurrency: z.number().int().min(1).max(32).default(8),
  schedule: z.enum(["once", "daily"]).default("once"),
  allowNetwork: z.boolean().default(false),
  maxPaidBudgetUsd: z.number().finite().min(0).max(10_000).default(0),
  approveNetworkForThisRun: z.boolean().default(false),
  approvePaidBudgetForThisRun: z.boolean().default(false),
}).strict();

export const capabilityGapRequestSchema = z.object({
  ownerProfileId: z.string().trim().min(3).max(96).regex(/^[A-Za-z0-9_.:-]+$/),
  goal: z.string().trim().min(10).max(2_000),
  division: divisionName,
  missingCapability: z.string().trim().min(3).max(240),
  availableEvidence: z.array(z.string().trim().min(3).max(500)).max(30).default([]),
  exactBuildApproval: z.boolean().default(false),
}).strict();

export type DailyDivisionBenchmarkRequest = z.infer<typeof dailyDivisionBenchmarkRequestSchema>;
export type CapabilityGapRequest = z.infer<typeof capabilityGapRequestSchema>;

function stableId(prefix: string, values: string[]) {
  return `${prefix}-${createHash("sha256").update(values.join("|")).digest("hex").slice(0, 16)}`;
}

function unique<T>(values: T[]) {
  return [...new Set(values)];
}

export function buildDivisionProductionRegistry() {
  return {
    schema: "dreamco.division_production_registry.v1",
    divisions: divisionNames.map((name) => ({
      name,
      charter: DIVISION_DOMAIN_PROFILES[name],
      profilePoolReference: "config/generated/bots.catalog.json",
      newCapabilityContracts: 100,
      dailyLogicalWorkerSlots: DAILY_BENCHMARK_WORKER_ROLES.length,
      productionReady: false,
      readinessGates: PRODUCTION_READINESS_GATES,
    })),
    summary: {
      divisions: divisionNames.length,
      capabilityContracts: divisionNames.length * 100,
      logicalDailyWorkerSlots: divisionNames.length * DAILY_BENCHMARK_WORKER_ROLES.length,
      productionReadyDivisions: 0,
    },
    allianceWatch: OFFICIAL_AI_ALLIANCE_WATCH,
    safeTraining: SAFE_AI_TRAINING_CONTRACT,
    connectorLifecycle: UNIVERSAL_CONNECTOR_LIFECYCLE,
  } as const;
}

export function createDailyDivisionBenchmarkPlan(input: DailyDivisionBenchmarkRequest) {
  const request = dailyDivisionBenchmarkRequestSchema.parse(input);
  const divisions = unique(request.divisions);
  const totalFixtures = divisions.length * request.signedFixturesPerDivision;
  let status = "local_fixture_plan_ready";
  if (request.allowNetwork && !request.approveNetworkForThisRun) status = "network_approval_required";
  else if (request.maxPaidBudgetUsd > 0 && !request.approvePaidBudgetForThisRun) status = "paid_budget_approval_required";
  else if (request.allowNetwork) status = "external_benchmark_adapters_required";

  return {
    schema: "dreamco.daily_division_benchmark_plan.v1",
    planId: stableId("division-benchmark", [request.ownerProfileId, ...divisions, String(request.signedFixturesPerDivision)]),
    status,
    schedule: request.schedule,
    schedulerRequired: request.schedule === "daily",
    divisions: divisions.map((name) => ({
      name,
      profilePoolReference: "config/generated/bots.catalog.json",
      signedFixtureTarget: request.signedFixturesPerDivision,
      workerRoles: DAILY_BENCHMARK_WORKER_ROLES,
      logicalWorkerSlots: DAILY_BENCHMARK_WORKER_ROLES.length,
      externalCompetitorRunsCompleted: 0,
    })),
    capacity: {
      totalSignedFixtures: totalFixtures,
      maxRuntimeConcurrency: request.maxConcurrency,
      plannedWaves: Math.ceil(totalFixtures / request.maxConcurrency),
      logicalWorkerSlots: divisions.length * DAILY_BENCHMARK_WORKER_ROLES.length,
    },
    permissions: {
      network: request.allowNetwork && request.approveNetworkForThisRun,
      maximumPaidBudgetUsd: request.approvePaidBudgetForThisRun ? request.maxPaidBudgetUsd : 0,
      externalWrites: false,
      productionRelease: false,
    },
    evidence: [
      "exact target and version",
      "signed input fixture and expected outcome",
      "quality, safety, latency, and cost results",
      "failure and recovery result",
      "difference from previous accepted baseline",
      "owner-visible daily report",
    ],
    executionPerformed: false,
    permanentBestClaimed: false,
  } as const;
}

export function createCapabilityGapPlan(input: CapabilityGapRequest) {
  const request = capabilityGapRequestSchema.parse(input);
  return {
    schema: "dreamco.capability_gap_plan.v1",
    planId: stableId("capability-gap", [request.ownerProfileId, request.division, request.goal, request.missingCapability]),
    status: request.exactBuildApproval ? "review_branch_and_sandbox_required" : "owner_build_approval_required",
    division: request.division,
    goal: request.goal,
    missingCapability: request.missingCapability,
    availableEvidence: unique(request.availableEvidence),
    lifecycle: [
      "define the user outcome and non-goals",
      "discover official documentation and compatible open-source candidates",
      "verify licenses, rights, provenance, dependencies, and security posture",
      "write the capability, tool, data, permission, and failure contracts",
      "build on a review branch with network off by default",
      "run synthetic and owner-authorized fixtures",
      "compare against the current baseline and relevant competitors",
      "complete all production readiness gates",
      "request owner review before deployment",
      "monitor measured outcomes and schedule the next gap review",
    ],
    productionReadyClaimed: false,
    selfGrantedPermissions: false,
    automaticMerge: false,
    automaticRelease: false,
  } as const;
}
