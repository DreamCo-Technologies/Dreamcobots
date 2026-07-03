import type {
  AlertRule,
  AutonomyMode,
  AutonomousTask,
  BotError,
  BotFinancial,
  BotMetric,
  BotProfile,
  BotTier,
  Division,
  DivisionRuntime,
  DivisionRuntimeHealth,
  Formula,
  Plugin,
} from "@shared/schema";

const TIER_SCORE: Record<BotTier, number> = {
  free: 1,
  pro: 2,
  enterprise: 3,
  elite: 4,
};

function toIso(value: unknown): string | null {
  if (!value) return null;
  if (value instanceof Date) return value.toISOString();
  if (typeof value === "string") return value;
  return null;
}

function computeHealth(workflowBlocked: number, openAlerts: number, failedRuns: number): DivisionRuntimeHealth {
  if (workflowBlocked > 3 || openAlerts > 5 || failedRuns > 6) return "critical";
  if (workflowBlocked > 0 || openAlerts > 2 || failedRuns > 2) return "warning";
  return "healthy";
}

export interface BuildDivisionRuntimeInput {
  division: Division;
  autonomyMode: AutonomyMode;
  bots: BotProfile[];
  tasks: AutonomousTask[];
  latestMetrics: BotMetric[];
  errors: BotError[];
  financials: BotFinancial[];
  alertRules: AlertRule[];
  plugins: Plugin[];
  formulas: Formula[];
  activeDelegations: number;
}

export function buildDivisionRuntime(input: BuildDivisionRuntimeInput): DivisionRuntime {
  const { division, autonomyMode, bots, tasks, latestMetrics, errors, financials, alertRules, plugins, formulas, activeDelegations } = input;
  const botById = new Map<number, BotProfile>(bots.map((b) => [b.id, b]));
  const metricRows = latestMetrics.filter((m) => botById.has(m.botId));
  const financialRows = financials.filter((f) => botById.has(f.botId));
  const errorRows = errors.filter((e) => botById.has(e.botId) && !e.resolved);

  const leadershipCandidate =
    bots.find((b) => ["system", "leadership", "autonomy", "management"].includes(String(b.category).toLowerCase())) ??
    [...bots].sort((a, b) => (TIER_SCORE[b.tier as BotTier] ?? 0) - (TIER_SCORE[a.tier as BotTier] ?? 0))[0];

  const openDecisions = tasks.filter((t) => t.status === "pending").length;
  const workflowActive = tasks.filter((t) => t.status === "running").length + activeDelegations;
  const workflowQueued = tasks.filter((t) => t.status === "pending").length;
  const workflowBlocked = tasks.filter((t) => t.status === "paused").length + Math.min(errorRows.length, 4);
  const workflowCompleted = tasks.filter((t) => t.status === "complete").length;
  const failedRuns = tasks.filter((t) => t.status === "failed").length;
  const openAlerts = alertRules.filter((a) => a.enabled).length + Math.min(errorRows.length, 6);

  const revenueCents = financialRows
    .filter((f) => f.status === "completed")
    .reduce((sum, f) => sum + Number(f.amount || 0), 0);
  const revenueFromMetrics = metricRows.reduce((sum, m) => sum + Number(m.revenue || 0), 0);
  const normalizedRevenue = revenueCents > 0 ? revenueCents : revenueFromMetrics;

  const avgUptime = metricRows.length
    ? Math.round(metricRows.reduce((sum, m) => sum + Number(m.uptime || 0), 0) / metricRows.length)
    : 100;

  const health = computeHealth(workflowBlocked, openAlerts, failedRuns);
  const latestTask = [...tasks]
    .sort((a, b) => {
      const aTime = new Date(a.lastRunAt ?? a.createdAt).getTime();
      const bTime = new Date(b.lastRunAt ?? b.createdAt).getTime();
      return bTime - aTime;
    })[0];

  const specialists = bots
    .filter((b) => b.id !== leadershipCandidate?.id)
    .sort((a, b) => (TIER_SCORE[b.tier as BotTier] ?? 0) - (TIER_SCORE[a.tier as BotTier] ?? 0))
    .slice(0, 5)
    .map((b, idx) => ({
      slug: b.slug,
      displayName: b.displayName,
      status: (b.status as "active" | "paused" | "inactive") ?? "active",
      tier: b.tier as BotTier,
      workload: Math.min(100, Math.max(5, 15 + idx * 12 + workflowActive * 5)),
    }));

  const activeAlerts = [
    workflowBlocked > 0 ? `${workflowBlocked} blocked workflows` : null,
    errorRows.length > 0 ? `${errorRows.length} unresolved runtime errors` : null,
    avgUptime < 95 ? `uptime below target (${avgUptime}%)` : null,
  ].filter(Boolean) as string[];

  return {
    division,
    ceoAgent: leadershipCandidate
      ? {
          slug: leadershipCandidate.slug,
          displayName: leadershipCandidate.displayName,
          status: leadershipCandidate.status === "active" ? "active" : leadershipCandidate.status === "paused" ? "degraded" : "offline",
          autonomyMode,
          openDecisions,
          lastDecisionAt: toIso(latestTask?.lastRunAt ?? latestTask?.createdAt),
        }
      : null,
    specialists,
    workflowEngine: {
      active: workflowActive,
      queued: workflowQueued,
      blocked: workflowBlocked,
      completed: workflowCompleted,
      health,
    },
    learningEngine: {
      status: avgUptime >= 98 ? "optimized" : avgUptime >= 93 ? "learning" : "warming",
      signalsLearned: metricRows.reduce((sum, m) => sum + Number(m.tasksCompleted || 0), 0),
      knowledgeCoverage: Math.min(100, Math.max(10, bots.length * 2 + formulas.length)),
      lastSyncAt: toIso(latestTask?.lastRunAt ?? latestTask?.createdAt),
    },
    toolMarketplace: {
      availableTools: plugins.length,
      enabledTools: plugins.filter((p) => p.status === "published").length,
      topTools: plugins.slice(0, 3).map((p) => p.name),
    },
    knowledgeBase: {
      formulas: formulas.length,
      snippets: specialists.length * 8,
      docs: bots.filter((b) => Boolean(b.description)).length,
      lastUpdatedAt: toIso(latestTask?.createdAt ?? null),
    },
    kpis: {
      activeWorkflows: workflowActive,
      revenueCents: normalizedRevenue,
      uptimePct: avgUptime,
      openAlerts,
      failedRuns,
    },
    health,
    activeAlerts,
  };
}
