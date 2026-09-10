import { createHash, randomUUID } from "node:crypto";

export type ExperimentKind = "capability" | "dataset" | "model" | "agent" | "tool" | "benchmark";
export type SandboxNetwork = "none" | "allowlist";
export type SandboxState = "planned" | "running" | "passed" | "failed" | "quarantined" | "blocked" | "rolled_back";
export type PromotionState = "hold" | "candidate" | "promoted";

export interface ResourceLimits {
  timeoutMs: number;
  maxOutputBytes: number;
  maxMemoryMb: number;
  maxCpuMs: number;
  maxArtifacts: number;
}

export interface ToolBoundary {
  toolId: string;
  mode: "deny" | "read_only" | "fixture_only";
}

export interface ExperimentPermissions {
  filesystem: "fixture_read_only" | "workspace_ephemeral";
  network: SandboxNetwork;
  networkAllowlist?: string[];
  secrets: "none";
  production: "none";
  tools: ToolBoundary[];
}

export interface ProvenanceRecord {
  sourceReference: string;
  sourceVersion: string;
  licenseOrUsageBasis: string;
  transformation: string;
  integrityHash: string;
}

export interface ExperimentPlan {
  id: string;
  kind: ExperimentKind;
  title: string;
  stableVersion: string;
  command: string[];
  fixtureDigest: string;
  baselineDigest: string;
  seed?: string;
  permissions: ExperimentPermissions;
  limits: ResourceLimits;
  provenance: ProvenanceRecord[];
  benchmarkIds: string[];
  requiredPromotionGates: string[];
}

export interface Artifact {
  id: string;
  type: "input_manifest" | "stdout" | "stderr" | "result" | "failure" | "provenance" | "cleanup";
  content: string;
  sha256: string;
  redacted: boolean;
}

export interface HostResult {
  exitCode: number | null;
  stdout: string;
  stderr: string;
  durationMs: number;
  peakMemoryMb?: number;
  cpuMs?: number;
}

/** An isolation provider owns process execution. This contract never executes an experiment itself. */
export interface IsolatedExperimentHost {
  run(plan: Readonly<ExperimentPlan>): Promise<HostResult>;
  cleanup?(plan: Readonly<ExperimentPlan>): Promise<void>;
}

export interface ExperimentRun {
  runId: string;
  planId: string;
  state: SandboxState;
  startedAt: string;
  completedAt: string | null;
  artifacts: Artifact[];
  baselineDigest: string;
  resultDigest: string | null;
  failureReason: string | null;
  rollbackTarget: string;
}

export interface PromotionAssessment {
  state: PromotionState;
  missingGates: string[];
  reason: string;
}

const DEFAULT_LIMITS: ResourceLimits = {
  timeoutMs: 120_000,
  maxOutputBytes: 1_000_000,
  maxMemoryMb: 512,
  maxCpuMs: 60_000,
  maxArtifacts: 16,
};

const TOKEN_LIKE = /(?:gh[pousr]_[A-Za-z0-9_-]{8,}|sk-[A-Za-z0-9_-]{8,}|Bearer\s+[A-Za-z0-9._-]{8,}|-----BEGIN[\s\S]*?PRIVATE KEY-----)/gi;
const sha256 = (value: string) => createHash("sha256").update(value).digest("hex");
const redact = (value: string) => value.replace(TOKEN_LIKE, "[REDACTED]");

export function createExperimentPlan(input: Omit<ExperimentPlan, "limits"> & { limits?: Partial<ResourceLimits> }): ExperimentPlan {
  const plan: ExperimentPlan = { ...input, limits: { ...DEFAULT_LIMITS, ...input.limits } };
  assertExperimentPlan(plan);
  return Object.freeze({ ...plan, command: [...plan.command], benchmarkIds: [...plan.benchmarkIds], requiredPromotionGates: [...plan.requiredPromotionGates], provenance: plan.provenance.map((record) => ({ ...record })), permissions: { ...plan.permissions, tools: plan.permissions.tools.map((tool) => ({ ...tool })), networkAllowlist: plan.permissions.networkAllowlist ? [...plan.permissions.networkAllowlist] : undefined } });
}

export function assertExperimentPlan(plan: ExperimentPlan): void {
  if (!/^[a-z0-9][a-z0-9._-]{2,127}$/i.test(plan.id)) throw new Error("Experiment id is invalid");
  if (!plan.title.trim() || !plan.stableVersion.trim()) throw new Error("Experiment title and stable version are required");
  if (plan.command.length === 0 || plan.command.some((token) => !token || token.includes("..") || /[\r\n]/.test(token))) throw new Error("Experiment command is invalid");
  if (!/^[a-f0-9]{64}$/i.test(plan.fixtureDigest) || !/^[a-f0-9]{64}$/i.test(plan.baselineDigest)) throw new Error("Fixture and baseline digests must be SHA-256 values");
  if (["dataset", "model", "benchmark"].includes(plan.kind) && !plan.seed) throw new Error("Deterministic seed is required for dataset, model, and benchmark experiments");
  if (plan.permissions.secrets !== "none" || plan.permissions.production !== "none") throw new Error("Experiments may not access secrets or production");
  if (plan.permissions.network === "none" && (plan.permissions.networkAllowlist?.length ?? 0) > 0) throw new Error("Network allowlist requires allowlist mode");
  if (plan.permissions.network === "allowlist" && (plan.permissions.networkAllowlist?.length ?? 0) === 0) throw new Error("Allowlist network mode needs an explicit allowlist");
  if (plan.permissions.tools.some((tool) => tool.mode !== "deny" && tool.mode !== "read_only" && tool.mode !== "fixture_only")) throw new Error("Tool boundary is invalid");
  for (const [name, value] of Object.entries(plan.limits)) if (!Number.isFinite(value) || value <= 0) throw new Error(`Invalid resource limit: ${name}`);
  if (plan.limits.maxArtifacts > 64) throw new Error("Artifact count limit is too high");
  if (plan.provenance.length === 0 || plan.provenance.some((record) => !record.sourceReference || !record.sourceVersion || !record.licenseOrUsageBasis || !/^[a-f0-9]{64}$/i.test(record.integrityHash))) throw new Error("Complete provenance records are required");
}

function artifact(type: Artifact["type"], content: string): Artifact {
  const safeContent = redact(content);
  return { id: `${type}-${randomUUID()}`, type, content: safeContent, sha256: sha256(safeContent), redacted: safeContent !== content };
}

function bounded(value: string, maxBytes: number): string {
  const buffer = Buffer.from(value, "utf8");
  return buffer.length <= maxBytes ? value : `${buffer.subarray(0, maxBytes).toString("utf8")}\n[OUTPUT_TRUNCATED]`;
}

export class GovernedExperimentSandbox {
  async run(plan: ExperimentPlan, host?: IsolatedExperimentHost): Promise<ExperimentRun> {
    assertExperimentPlan(plan);
    const manifest = JSON.stringify({ id: plan.id, kind: plan.kind, stableVersion: plan.stableVersion, fixtureDigest: plan.fixtureDigest, baselineDigest: plan.baselineDigest, seed: plan.seed ?? null, permissions: plan.permissions, limits: plan.limits, provenance: plan.provenance, benchmarkIds: plan.benchmarkIds });
    const run: ExperimentRun = { runId: `sandbox-${randomUUID()}`, planId: plan.id, state: "planned", startedAt: new Date().toISOString(), completedAt: null, artifacts: [artifact("input_manifest", manifest), artifact("provenance", JSON.stringify(plan.provenance))], baselineDigest: plan.baselineDigest, resultDigest: null, failureReason: null, rollbackTarget: plan.stableVersion };
    if (!host) return { ...run, state: "blocked", completedAt: new Date().toISOString(), failureReason: "No isolation host configured", artifacts: [...run.artifacts, artifact("failure", "No isolation host configured; execution was not attempted.")] };
    run.state = "running";
    try {
      const result = await host.run(plan);
      const stdout = bounded(result.stdout, plan.limits.maxOutputBytes);
      const stderr = bounded(result.stderr, plan.limits.maxOutputBytes);
      run.artifacts.push(artifact("stdout", stdout), artifact("stderr", stderr));
      const exceeded = result.durationMs > plan.limits.timeoutMs || (result.peakMemoryMb ?? 0) > plan.limits.maxMemoryMb || (result.cpuMs ?? 0) > plan.limits.maxCpuMs;
      const passed = result.exitCode === 0 && !exceeded;
      const outcome = JSON.stringify({ exitCode: result.exitCode, durationMs: result.durationMs, peakMemoryMb: result.peakMemoryMb ?? null, cpuMs: result.cpuMs ?? null, exceeded });
      run.artifacts.push(artifact("result", outcome));
      run.resultDigest = sha256(outcome);
      run.state = passed ? "passed" : "quarantined";
      run.failureReason = passed ? null : exceeded ? "Resource limit exceeded" : `Host exit code: ${result.exitCode ?? "unknown"}`;
      if (!passed) run.artifacts.push(artifact("failure", run.failureReason));
    } catch (error) {
      run.state = "quarantined";
      run.failureReason = error instanceof Error ? error.message : "Isolation host failed";
      run.artifacts.push(artifact("failure", run.failureReason));
    }
    try {
      await host.cleanup?.(plan);
      run.artifacts.push(artifact("cleanup", "Host cleanup completed."));
    } catch (error) {
      run.state = "quarantined";
      run.failureReason = "Isolation host cleanup failed";
      run.artifacts.push(artifact("failure", error instanceof Error ? error.message : run.failureReason));
    }
    run.completedAt = new Date().toISOString();
    return run;
  }
}

export function assessPromotion(run: ExperimentRun, evidence: { baselineCompared: boolean; reproducible: boolean; benchmarkPassed: boolean; groundingPassed: boolean; datasetQualityPassed: boolean; regressionPassed: boolean; ownerApproved: boolean }): PromotionAssessment {
  if (run.state !== "passed") return { state: "hold", missingGates: ["sandbox_run_passed"], reason: "Only a passed sandbox run can be evaluated for promotion." };
  if (!run.resultDigest || run.artifacts.some((item) => !/^[a-f0-9]{64}$/i.test(item.sha256))) return { state: "hold", missingGates: ["artifact_integrity"], reason: "Artifact integrity evidence is incomplete." };
  const missingGates = Object.entries(evidence).filter(([, value]) => !value).map(([name]) => name);
  if (missingGates.length) return { state: "hold", missingGates, reason: "Promotion remains held until every required gate has evidence." };
  return { state: "candidate", missingGates: [], reason: "Candidate only: deployment still requires a separate controlled release decision." };
}
