function buildId(prefix) {
    return `${prefix}_${Math.random().toString(36).slice(2, 10)}`;
}
function nowIso() {
    return new Date().toISOString();
}
export function createDelegation(input) {
    const createdAt = nowIso();
    const needsApproval = input.riskLevel === "high";
    const dependencies = input.targetDivisions.map((division) => ({
        id: buildId("dep"),
        division,
        title: `${input.sourceWorkflow} support from ${division}`,
        status: "pending",
    }));
    const approvalGates = needsApproval
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
export function deriveDelegationStatus(delegation) {
    if (delegation.approvalGates.some((g) => g.required && g.status === "rejected"))
        return "rejected";
    if (delegation.approvalGates.some((g) => g.required && g.status !== "approved"))
        return "awaiting_approval";
    if (delegation.dependencies.every((d) => d.status === "complete"))
        return "complete";
    if (delegation.dependencies.some((d) => d.status === "blocked"))
        return "in_progress";
    if (delegation.dependencies.some((d) => d.status === "in_progress"))
        return "in_progress";
    return "pending";
}
export function updateDependencyStatus(delegation, dependencyId, status) {
    const dependencies = delegation.dependencies.map((dep) => dep.id === dependencyId ? { ...dep, status } : dep);
    const updated = { ...delegation, dependencies, updatedAt: nowIso() };
    return { ...updated, status: deriveDelegationStatus(updated) };
}
export function decideApprovalGate(delegation, gateId, decision, approverDivision) {
    const approvalGates = delegation.approvalGates.map((gate) => gate.id === gateId
        ? {
            ...gate,
            approverDivision,
            status: decision,
            approvedAt: nowIso(),
        }
        : gate);
    const updated = { ...delegation, approvalGates, updatedAt: nowIso() };
    return { ...updated, status: deriveDelegationStatus(updated) };
}
