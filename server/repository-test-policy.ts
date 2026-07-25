import { randomUUID } from "node:crypto";

import { z } from "zod";

const suiteIdSchema = z.string().regex(/^[a-z][a-z0-9-]{2,63}$/);

export const repositoryTestPlanRequestSchema = z.object({
  suiteIds: z.array(suiteIdSchema).min(1).max(50),
  mode: z.enum(["contract", "sandbox", "adapter"]).default("contract"),
  allowNetwork: z.boolean().default(false),
  exactApprovalForExternalTests: z.boolean().default(false),
  maxBudgetUsd: z.number().min(0).max(10_000).default(0),
}).strict();

export type RepositoryTestRegistry = {
  schema: string;
  scan_id: string;
  safety_contract: Record<string, unknown>;
  summary: Record<string, number>;
  suites: Array<{
    id: string;
    name: string;
    area: string;
    level: "local_contract" | "repository_sandbox" | "adapter_optional" | "credentials_required";
    status: string;
    scripts: string[];
    sources: string[];
    tests: string[];
    boundary: string;
    missing_scripts: string[];
    missing_evidence: string[];
  }>;
};

export function createRepositoryTestPlan(
  input: z.infer<typeof repositoryTestPlanRequestSchema>,
  registry: RepositoryTestRegistry,
) {
  const request = repositoryTestPlanRequestSchema.parse(input);
  const suiteMap = new Map(registry.suites.map((suite) => [suite.id, suite]));
  const suiteIds = [...new Set(request.suiteIds)];
  const suites = suiteIds.map((suiteId) => {
    const suite = suiteMap.get(suiteId);
    if (!suite) throw new Error(`Unknown repository test suite: ${suiteId}`);

    let readiness = "local_contract_ready";
    if (suite.status === "blocked_missing_evidence") {
      readiness = "blocked_missing_evidence";
    } else if (suite.level === "repository_sandbox" && request.mode === "contract") {
      readiness = "contract_checks_ready_sandbox_not_requested";
    } else if (suite.level === "repository_sandbox") {
      readiness = "isolated_sandbox_runner_required";
    } else if (suite.level === "adapter_optional" || suite.level === "credentials_required") {
      readiness = request.mode !== "adapter"
        ? "held_adapter_mode_not_requested"
        : !request.allowNetwork || !request.exactApprovalForExternalTests
          ? "held_network_and_exact_approval_required"
          : "adapter_credentials_and_runner_verification_required";
    }

    return {
      id: suite.id,
      name: suite.name,
      area: suite.area,
      level: suite.level,
      readiness,
      scriptIds: suite.scripts,
      commands: suite.scripts.map((scriptId) => `npm run ${scriptId}`),
      evidence: [...suite.sources, ...suite.tests],
      boundary: suite.boundary,
      browserExecutionAllowed: false,
    };
  });

  return {
    schema: "dreamco.repository_test_plan.v1",
    planId: `repository-test-${randomUUID()}`,
    scanId: registry.scan_id,
    status: suites.some((suite) => suite.readiness.startsWith("blocked"))
      ? "blocked_suites_present"
      : suites.some((suite) => suite.readiness.startsWith("held"))
        ? "approval_or_adapter_required"
        : "owner_runner_handoff_ready",
    mode: request.mode,
    allowNetwork: request.allowNetwork,
    exactApprovalForExternalTests: request.exactApprovalForExternalTests,
    maxBudgetUsd: request.maxBudgetUsd,
    suites,
    testsExecutedByPlanner: false,
    externalActionTaken: false,
    arbitraryCommandsAccepted: false,
    runnerHandoff: "Run npm run test:repository from the reviewed repository checkout for the full local test path.",
  } as const;
}
