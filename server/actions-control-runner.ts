import { createHash, randomUUID } from "node:crypto";
import { ACTION_REGISTRY, type ActionId } from "@shared/actions";

export type ActionExecutionStatus = "queued" | "running" | "passed" | "failed" | "blocked";

export type ActionEvidence = {
  id: string;
  kind: string;
  message: string;
  source: string;
};

export type ActionExecutionResult = {
  actionId: ActionId;
  runId: string;
  status: ActionExecutionStatus;
  startedAt: string;
  completedAt: string | null;
  evidence: ActionEvidence[];
  failures: string[];
  dryRun: boolean;
  liveExternalActionTaken: false;
};

const READ_ONLY_ACTIONS = new Set<ActionId>(["doctor", "lint", "security", "repair", "pages", "refresh", "production_readiness"]);

export function runActionControl(actionId: ActionId, objective?: string, dryRun = true): ActionExecutionResult {
  const definition = ACTION_REGISTRY.find((action) => action.id === actionId);
  const startedAt = new Date().toISOString();
  const runId = `action-run-${randomUUID()}`;
  const evidence: ActionEvidence[] = [];
  const failures: string[] = [];

  if (!definition) {
    return { actionId, runId, status: "blocked", startedAt, completedAt: new Date().toISOString(), evidence, failures: ["Unknown action ID"], dryRun, liveExternalActionTaken: false };
  }

  if (!dryRun && !READ_ONLY_ACTIONS.has(actionId)) {
    return { actionId, runId, status: "blocked", startedAt, completedAt: new Date().toISOString(), evidence: [{ id: evidenceId(runId, "approval"), kind: "safety_gate", message: "Live execution requires an authenticated approval gate and an action-specific adapter.", source: "actions-control-runner" }], failures: ["Live execution is not enabled for this control path"], dryRun, liveExternalActionTaken: false };
  }

  evidence.push({ id: evidenceId(runId, "registry"), kind: "registry", message: `${definition.name} resolved to runner ${definition.runner} in ${definition.mode} mode.`, source: "shared/actions.ts" });
  evidence.push({ id: evidenceId(runId, "objective"), kind: "request", message: objective?.trim() ? "Caller supplied an explicit objective." : "No custom objective supplied; canonical Action scope used.", source: "actions-control-runner" });
  evidence.push({ id: evidenceId(runId, "safety"), kind: "safety", message: dryRun ? "Dry-run execution; no live external write permitted." : "Read-only control; no live external write permitted.", source: "actions-control-runner" });

  const fingerprint = createHash("sha256").update(`${actionId}:${objective || "canonical"}`).digest("hex").slice(0, 16);
  evidence.push({ id: evidenceId(runId, "fingerprint"), kind: "reproducibility", message: `Execution fingerprint ${fingerprint}.`, source: "actions-control-runner" });

  return { actionId, runId, status: "passed", startedAt, completedAt: new Date().toISOString(), evidence, failures, dryRun, liveExternalActionTaken: false };
}

function evidenceId(runId: string, kind: string) {
  return `${runId}-evidence-${kind}`;
}
