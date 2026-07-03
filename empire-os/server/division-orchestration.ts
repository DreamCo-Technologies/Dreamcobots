import type {
  CrossDivisionDelegation,
  DelegationApprovalGate,
  DelegationDependency,
  DelegationRiskLevel,
  DelegationStatus,
  Division,
} from "@shared/schema";

function buildId(prefix: string): string {
  return `${prefix}_${Math.random().toString(36).slice(2, 10)}`;
}

function nowIso(): string {
  return new Date().toISOString();
}

export interface CreateDelegationInput {
  sourceDivision: Division;
  sourceWorkflow: string;
  objective: string;
  targetDivisions: Division[];
  riskLevel: DelegationRiskLevel;
  requestedBy: string;
}

export function createDelegation(input: CreateDelegationInput): CrossDivisionDelegation {
  const createdAt = nowIso();
  const needsApproval = input.riskLevel === "high";
  const dependencies: DelegationDependency[] = input.targetDivisions.map((division) => ({
    id: buildId("dep"),
    division,
    title: `${input.sourceWorkflow} support from ${division}`,
    status: "pending",
  }));

  const approvalGates: DelegationApprovalGate[] = needsApproval
    ? [
        {
          id: buildId("gate"),
          gate: "command_core",
          required: true,
          status: "pending",
          approverDivision: "CommandCore",
          approvedAt: null,
        },
      ]
    : [];

  return {
    id: buildId("del"),
    sourceDivision: input.sourceDivision,
    sourceWorkflow: input.sourceWorkflow,
    targetDivisions: input.targetDivisions,
    objective: input.objective,
    riskLevel: input.riskLevel,
    status: needsApproval ? "awaiting_approval" : "pending",
    dependencies,
    approvalGates,
    requestedBy: input.requestedBy,
    createdAt,
    updatedAt: createdAt,
  };
}

export function deriveDelegationStatus(delegation: CrossDivisionDelegation): DelegationStatus {
  if (delegation.approvalGates.some((g) => g.required && g.status === "rejected")) return "rejected";
  if (delegation.approvalGates.some((g) => g.required && g.status !== "approved")) return "awaiting_approval";
  if (delegation.dependencies.every((d) => d.status === "complete")) return "complete";
  if (delegation.dependencies.some((d) => d.status === "blocked")) return "in_progress";
  if (delegation.dependencies.some((d) => d.status === "in_progress")) return "in_progress";
  return "pending";
}

export function updateDependencyStatus(
  delegation: CrossDivisionDelegation,
  dependencyId: string,
  status: DelegationDependency["status"],
): CrossDivisionDelegation {
  const dependencies = delegation.dependencies.map((dep) =>
    dep.id === dependencyId ? { ...dep, status } : dep,
  );
  const updated = { ...delegation, dependencies, updatedAt: nowIso() };
  return { ...updated, status: deriveDelegationStatus(updated) };
}

export function decideApprovalGate(
  delegation: CrossDivisionDelegation,
  gateId: string,
  decision: "approved" | "rejected",
  approverDivision: Division,
): CrossDivisionDelegation {
  const approvalGates = delegation.approvalGates.map((gate) =>
    gate.id === gateId
      ? {
          ...gate,
          approverDivision,
          status: decision,
          approvedAt: nowIso(),
        }
      : gate,
  );
  const updated = { ...delegation, approvalGates, updatedAt: nowIso() };
  return { ...updated, status: deriveDelegationStatus(updated) };
}
