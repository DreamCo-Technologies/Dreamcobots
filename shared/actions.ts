import { z } from "zod";

export const ACTION_IDS = [
  "doctor",
  "test",
  "lint",
  "security",
  "benchmark",
  "repair",
  "pages",
  "bundle",
  "refresh",
  "production_readiness",
] as const;

export type ActionId = (typeof ACTION_IDS)[number];

export const actionRunRequestSchema = z.object({
  actionId: z.enum(ACTION_IDS),
  objective: z.string().trim().min(3).max(4_000).optional(),
  dryRun: z.boolean().default(true),
}).strict();

export const actionRunResultSchema = z.object({
  actionId: z.enum(ACTION_IDS),
  runId: z.string().min(1),
  status: z.enum(["queued", "running", "passed", "failed", "blocked"]),
  startedAt: z.string().datetime(),
  completedAt: z.string().datetime().nullable(),
  evidence: z.array(z.object({
    id: z.string().min(1),
    kind: z.string().min(1),
    message: z.string(),
    source: z.string().min(1),
  })),
  failures: z.array(z.string()),
  dryRun: z.boolean(),
  liveExternalActionTaken: z.literal(false),
});

export const ACTION_REGISTRY = [
  { id: "doctor", name: "Run Doctor", runner: "repository_doctor", mode: "read_only" },
  { id: "test", name: "Run Tests", runner: "test_harness", mode: "sandbox" },
  { id: "lint", name: "Run Lint", runner: "static_quality", mode: "read_only" },
  { id: "security", name: "Security Check", runner: "security_audit", mode: "read_only" },
  { id: "benchmark", name: "Benchmark Locally", runner: "local_benchmark", mode: "sandbox" },
  { id: "repair", name: "Find Repair Plan", runner: "repair_planner", mode: "plan_only" },
  { id: "pages", name: "Verify Pages Data", runner: "pages_contract", mode: "read_only" },
  { id: "bundle", name: "Prepare Device Bundle", runner: "device_bundle_check", mode: "sandbox" },
  { id: "refresh", name: "Refresh GitHub Runs", runner: "github_run_refresh", mode: "read_only" },
  { id: "production_readiness", name: "Production Readiness", runner: "production_gate", mode: "read_only" },
] as const;

export function getActionDefinition(actionId: ActionId) {
  return ACTION_REGISTRY.find((action) => action.id === actionId);
}
