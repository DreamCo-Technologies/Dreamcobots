import Seo from "@/components/Seo";
import AppShell from "@/components/AppShell";
import { useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useEmpireOverview, useAutonomyMode, useSetAutonomyMode } from "@/hooks/use-empire";
import { useBots } from "@/hooks/use-bots";
import { useTasks } from "@/hooks/use-tasks";
import { useQuery } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Skeleton } from "@/components/ui/skeleton";
import { Link } from "wouter";
import {
  Activity,
  AlertTriangle,
  ArrowRight,
  Bot,
  Building2,
  DollarSign,
  Globe,
  Shield,
  ShieldCheck,
  Sparkles,
  TrendingUp,
  Zap,
  Cpu,
  BarChart3,
  Bell,
  BookOpen,
  PlayCircle,
  Store,
  Workflow,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { apiRequest } from "@/lib/queryClient";
import type { AutonomyMode, BotHealthSummary, DivisionStats } from "@shared/schema";

const DIVISION_COLORS: Record<string, string> = {
  DreamFinance: "from-emerald-500/15 to-emerald-500/5",
  DreamRealEstate: "from-blue-500/15 to-blue-500/5",
  DreamSalesPro: "from-orange-500/15 to-orange-500/5",
  DreamAIInfra: "from-violet-500/15 to-violet-500/5",
  DreamRetail: "from-pink-500/15 to-pink-500/5",
  DreamProServices: "from-cyan-500/15 to-cyan-500/5",
  DreamData: "from-indigo-500/15 to-indigo-500/5",
  DreamGlobal: "from-teal-500/15 to-teal-500/5",
  DreamAutomation: "from-yellow-500/15 to-yellow-500/5",
  DreamContent: "from-rose-500/15 to-rose-500/5",
  DreamTrade: "from-lime-500/15 to-lime-500/5",
  DreamFlow: "from-sky-500/15 to-sky-500/5",
  DreamMarket: "from-fuchsia-500/15 to-fuchsia-500/5",
  DreamEmpire: "from-amber-500/15 to-amber-500/5",
  CommandCore: "from-slate-500/15 to-slate-500/5",
  GameTitan: "from-red-500/15 to-red-500/5",
};

const AUTONOMY_MODES: { value: AutonomyMode; label: string; desc: string; color: string }[] = [
  { value: "guided", label: "Guided", desc: "User approval on all actions", color: "bg-[rgb(59_130_246)]" },
  { value: "semi-autonomous", label: "Semi-Auto", desc: "Low-risk auto-execution", color: "bg-[rgb(245_158_11)]" },
  { value: "full-autonomy", label: "Full Auto", desc: "Reporting only", color: "bg-[rgb(34_197_94)]" },
];

export default function DashboardPage() {
  const [botSlug, setBotSlug] = useState<string | undefined>(undefined);
  const queryClient = useQueryClient();
  const empire = useEmpireOverview();
  const autonomyQuery = useAutonomyMode();
  const setMode = useSetAutonomyMode();
  const tasks = useTasks();
  const healthQuery = useQuery<BotHealthSummary>({ queryKey: ["/api/metrics/health"] });
  const alertsQuery = useQuery({ queryKey: ["/api/alerts"] });

  const currentMode = (autonomyQuery.data as any)?.mode ?? "guided";
  const data = empire.data;
  const health = healthQuery.data;
  const alerts = (alertsQuery.data ?? []) as any[];

  const taskCounts = new Map<string, number>();
  (tasks.data ?? []).forEach(t => taskCounts.set(t.status, (taskCounts.get(t.status) ?? 0) + 1));

  const runDivisionWorkflow = useMutation({
    mutationFn: async (division: string) => {
      const res = await apiRequest("POST", `/api/divisions/${encodeURIComponent(division)}/workflows/run`, {
        title: `${division} quick workflow`,
      });
      return res.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["/api/tasks"] });
      queryClient.invalidateQueries({ queryKey: ["/api/empire/overview"] });
    },
  });

  const requestCrossDivisionHelp = useMutation({
    mutationFn: async (division: string) => {
      const fallbackTargets: Record<string, string[]> = {
        DreamRealEstate: ["DreamFinance", "DreamLegal", "DreamMarket", "DreamConstruction", "DreamDecision", "CommandCore"],
      };
      const targets = fallbackTargets[division] ?? ["CommandCore", "DreamDecision", "DreamFinance"];
      const res = await apiRequest("POST", "/api/orchestration/delegations", {
        sourceDivision: division,
        sourceWorkflow: `${division} cross-division escalation`,
        objective: `Request support from ${targets.join(", ")} for critical ${division} workflow`,
        targetDivisions: targets,
        riskLevel: "high",
        requestedBy: "dashboard-quick-action",
      });
      return res.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["/api/empire/overview"] });
      queryClient.invalidateQueries({ queryKey: ["/api/orchestration/delegations"] });
    },
  });

  return (
    <AppShell selectedBotSlug={botSlug} onBotChange={setBotSlug}>
      <Seo title="DreamCo Empire OS - Command Center" description="Real-time overview of all DreamCo divisions, bots, and metrics." />

      <div className="buddy-card buddy-noise buddy-appear overflow-hidden">
        <div className="px-5 pt-6 pb-5 md:px-8 md:pt-8 md:pb-6 border-b border-border/60">
          <div className="flex flex-wrap items-center justify-between gap-4">
            <div>
              <h1 className="text-2xl md:text-3xl" data-testid="text-dashboard-title">Empire Command Center</h1>
              <p className="text-sm text-muted-foreground mt-1">Real-time overview of all DreamCo divisions</p>
            </div>
            <div className="flex items-center gap-3">
              <Badge variant="secondary" className="rounded-full">
                <Activity className="h-3 w-3 mr-1.5 text-green-500" />
                Systems Online
              </Badge>
            </div>
          </div>
        </div>

        {empire.isLoading ? (
          <div className="p-5 md:p-8 space-y-6">
            <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
              {Array.from({ length: 4 }).map((_, i) => <Skeleton key={i} className="h-28 rounded-2xl" />)}
            </div>
            <Skeleton className="h-48 rounded-2xl" />
          </div>
        ) : (
          <div className="p-5 md:p-8 space-y-8 buddy-stagger">
            {/* Key Stats */}
            <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
              <Card data-testid="stat-total-bots">
                <CardHeader className="flex flex-row items-center justify-between gap-1 space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium text-muted-foreground">Total Bots</CardTitle>
                  <Bot className="h-4 w-4 text-primary" />
                </CardHeader>
                <CardContent>
                  <p className="text-3xl font-bold tracking-tight">{data?.totalBots ?? 0}</p>
                  <p className="text-xs text-muted-foreground mt-1">Across {data?.totalDivisions ?? 0} divisions</p>
                </CardContent>
              </Card>

              <Card data-testid="stat-active-bots">
                <CardHeader className="flex flex-row items-center justify-between gap-1 space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium text-muted-foreground">Active Bots</CardTitle>
                  <Zap className="h-4 w-4 text-green-500" />
                </CardHeader>
                <CardContent>
                  <p className="text-3xl font-bold tracking-tight">{health?.activeBots ?? data?.totalBots ?? 0}</p>
                  <p className="text-xs text-muted-foreground mt-1">
                    {health?.avgUptime ?? 100}% avg uptime
                  </p>
                </CardContent>
              </Card>

              <Card data-testid="stat-autonomy">
                <CardHeader className="flex flex-row items-center justify-between gap-1 space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium text-muted-foreground">Autonomy Mode</CardTitle>
                  <ShieldCheck className="h-4 w-4 text-yellow-500" />
                </CardHeader>
                <CardContent>
                  <div className="flex items-center gap-2">
                    <span className={cn("h-2.5 w-2.5 rounded-full", AUTONOMY_MODES.find(m => m.value === currentMode)?.color)} />
                    <p className="text-xl font-bold tracking-tight">{AUTONOMY_MODES.find(m => m.value === currentMode)?.label}</p>
                  </div>
                  <p className="text-xs text-muted-foreground mt-1">
                    {AUTONOMY_MODES.find(m => m.value === currentMode)?.desc}
                  </p>
                </CardContent>
              </Card>

              <Card data-testid="stat-tasks">
                <CardHeader className="flex flex-row items-center justify-between gap-1 space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium text-muted-foreground">Tasks</CardTitle>
                  <BarChart3 className="h-4 w-4 text-accent" />
                </CardHeader>
                <CardContent>
                  <p className="text-3xl font-bold tracking-tight">{(tasks.data ?? []).length}</p>
                  <p className="text-xs text-muted-foreground mt-1">
                    {taskCounts.get("running") ?? 0} running, {taskCounts.get("pending") ?? 0} pending
                  </p>
                </CardContent>
              </Card>
            </div>

            {/* System Health + Autonomy Mode */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
              {/* System Health */}
              <Card>
                <CardHeader className="flex flex-row items-center justify-between gap-1 space-y-0">
                  <CardTitle className="text-lg">System Health</CardTitle>
                  <Cpu className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-muted-foreground">Fleet Uptime</span>
                    <div className="flex items-center gap-2">
                      <Progress value={health?.avgUptime ?? 100} className="w-20 h-2" />
                      <span className="text-sm font-mono">{health?.avgUptime ?? 100}%</span>
                    </div>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-muted-foreground">Open Errors</span>
                    <Badge variant={health?.totalErrors ? "destructive" : "secondary"} className="rounded-full">
                      {health?.totalErrors ?? 0}
                    </Badge>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-muted-foreground">API Calls (total)</span>
                    <span className="text-sm font-mono">{(health?.totalApiCalls ?? 0).toLocaleString()}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-muted-foreground">Tasks Completed</span>
                    <span className="text-sm font-mono">{health?.totalTasksCompleted ?? 0}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-muted-foreground">Revenue Tracked</span>
                    <span className="text-sm font-semibold text-green-600 dark:text-green-400">${((health?.totalRevenue ?? 0) / 100).toLocaleString()}</span>
                  </div>
                </CardContent>
              </Card>

              {/* Autonomy Mode Selector */}
              <Card>
                <CardHeader className="flex flex-row items-center justify-between gap-1 space-y-0">
                  <CardTitle className="text-lg">Autonomy Mode</CardTitle>
                  <Link href="/autonomy" className="text-xs text-primary hover:underline underline-offset-4" data-testid="link-autonomy-settings">
                    Settings
                  </Link>
                </CardHeader>
                <CardContent className="space-y-3">
                  {AUTONOMY_MODES.map(m => (
                    <button
                      key={m.value}
                      className={cn(
                        "w-full rounded-xl border p-3 text-left transition-all",
                        currentMode === m.value
                          ? "border-primary/40 bg-gradient-to-br from-primary/8 to-transparent shadow-sm"
                          : "border-border/60 bg-card/40 hover-elevate"
                      )}
                      onClick={() => setMode.mutate(m.value)}
                      disabled={setMode.isPending}
                      data-testid={`mode-${m.value}`}
                    >
                      <div className="flex items-center gap-2">
                        <span className={cn("h-2 w-2 rounded-full", m.color)} />
                        <span className="text-sm font-semibold">{m.label}</span>
                        {currentMode === m.value && <Badge variant="secondary" className="ml-auto rounded-full text-[10px]">Active</Badge>}
                      </div>
                      <p className="text-xs text-muted-foreground mt-1">{m.desc}</p>
                    </button>
                  ))}
                </CardContent>
              </Card>
            </div>

            {/* Alert Rules */}
            <Card>
              <CardHeader className="flex flex-row items-center justify-between gap-1 space-y-0">
                <CardTitle className="text-lg">Auto-Remediation Rules</CardTitle>
                <Bell className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  {alerts.map((rule: any) => (
                    <div key={rule.id} className="rounded-xl border border-border/60 p-3" data-testid={`alert-rule-${rule.id}`}>
                      <div className="flex items-center justify-between gap-2">
                        <div className="flex items-center gap-2 min-w-0">
                          <AlertTriangle className="h-3.5 w-3.5 text-yellow-500 flex-shrink-0" />
                          <span className="text-sm font-medium truncate">{rule.name}</span>
                        </div>
                        <Badge variant={rule.enabled ? "secondary" : "outline"} className="rounded-full text-[10px] flex-shrink-0">
                          {rule.enabled ? "ON" : "OFF"}
                        </Badge>
                      </div>
                      <p className="text-xs text-muted-foreground mt-1.5">{rule.action}</p>
                      <p className="text-[10px] text-muted-foreground/70 mt-1 font-mono">Threshold: {rule.threshold}</p>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Division Overview */}
            <div>
              <div className="flex items-center justify-between gap-3 mb-4">
                <h2 className="text-lg">Division Overview</h2>
                <Link href="/divisions" className="text-xs text-primary hover:underline underline-offset-4" data-testid="link-all-divisions">
                  View all
                </Link>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {(data?.divisions ?? [])
                  .filter(d => d.botCount > 0)
                  .sort((a, b) => b.botCount - a.botCount)
                  .map((div: DivisionStats) => {
                    const gradient = DIVISION_COLORS[div.division] ?? "from-muted/50 to-muted/20";
                    const pct = Math.round((div.botCount / (data?.totalBots || 1)) * 100);
                    const runtime = div.runtime;
                    return (
                      <div
                        key={div.division}
                        className="group relative rounded-xl border border-border/60 p-4 overflow-visible"
                        data-testid={`division-${div.division}`}
                      >
                        <div className={cn("absolute inset-0 rounded-xl bg-gradient-to-br pointer-events-none opacity-60", gradient)} />
                        <div className="relative space-y-3">
                          <div className="flex items-center justify-between gap-3">
                            <div className="flex items-center gap-3 min-w-0">
                              <span className="inline-flex h-8 w-8 items-center justify-center rounded-xl bg-card/80 border border-border/60 shadow-sm flex-shrink-0">
                                <Building2 className="h-4 w-4 text-foreground/70" />
                              </span>
                              <div className="min-w-0">
                                <p className="text-sm font-semibold truncate">{div.division}</p>
                                <p className="text-xs text-muted-foreground">{div.botCount} bots • CEO {runtime?.ceoAgent?.displayName ?? "Unassigned"}</p>
                              </div>
                            </div>
                            <Badge
                              variant="outline"
                              className={cn(
                                "rounded-full text-[10px]",
                                runtime?.health === "healthy" && "text-green-500 border-green-500/30",
                                runtime?.health === "warning" && "text-yellow-500 border-yellow-500/30",
                                runtime?.health === "critical" && "text-red-500 border-red-500/30",
                              )}
                            >
                              {runtime?.health ?? "unknown"}
                            </Badge>
                          </div>
                          <div className="grid grid-cols-3 gap-2 text-[10px] text-muted-foreground">
                            <div className="rounded-lg border border-border/40 px-2 py-1.5">
                              <p className="font-semibold text-foreground">{runtime?.kpis.activeWorkflows ?? 0}</p>
                              <p>workflows</p>
                            </div>
                            <div className="rounded-lg border border-border/40 px-2 py-1.5">
                              <p className="font-semibold text-foreground">${(((runtime?.kpis.revenueCents ?? 0) / 100) || 0).toLocaleString()}</p>
                              <p>revenue</p>
                            </div>
                            <div className="rounded-lg border border-border/40 px-2 py-1.5">
                              <p className="font-semibold text-foreground">{runtime?.kpis.openAlerts ?? 0}</p>
                              <p>alerts</p>
                            </div>
                          </div>
                          <div className="flex items-center gap-2">
                            <div className="w-24">
                              <Progress value={runtime?.kpis.uptimePct ?? pct} className="h-1.5 rounded-full" />
                            </div>
                            <span className="text-xs text-muted-foreground">{runtime?.kpis.uptimePct ?? pct}% uptime</span>
                            <span className="text-xs text-muted-foreground">{runtime?.workflowEngine.active ?? 0} active / {runtime?.workflowEngine.queued ?? 0} queued</span>
                          </div>
                          <div className="grid grid-cols-2 gap-2">
                            <Button
                              size="sm"
                              variant="secondary"
                              className="rounded-lg h-8 text-[11px]"
                              onClick={() => runDivisionWorkflow.mutate(div.division)}
                              disabled={runDivisionWorkflow.isPending}
                              data-testid={`quick-run-${div.division}`}
                            >
                              <PlayCircle className="h-3.5 w-3.5 mr-1" />
                              Run workflow
                            </Button>
                            <Link href="/marketplace">
                              <Button size="sm" variant="outline" className="w-full rounded-lg h-8 text-[11px]" data-testid={`quick-market-${div.division}`}>
                                <Store className="h-3.5 w-3.5 mr-1" />
                                Marketplace
                              </Button>
                            </Link>
                            <Link href="/learning-matrix">
                              <Button size="sm" variant="outline" className="w-full rounded-lg h-8 text-[11px]" data-testid={`quick-knowledge-${div.division}`}>
                                <BookOpen className="h-3.5 w-3.5 mr-1" />
                                Knowledge base
                              </Button>
                            </Link>
                            <Button
                              size="sm"
                              variant="outline"
                              className="rounded-lg h-8 text-[11px]"
                              onClick={() => requestCrossDivisionHelp.mutate(div.division)}
                              disabled={requestCrossDivisionHelp.isPending}
                              data-testid={`quick-help-${div.division}`}
                            >
                              <Workflow className="h-3.5 w-3.5 mr-1" />
                              Cross-division help
                            </Button>
                          </div>
                          <Link
                            href={`/divisions?d=${encodeURIComponent(div.division)}`}
                            className="inline-flex items-center text-xs text-primary hover:underline underline-offset-4"
                          >
                            Open division
                            <ArrowRight className="h-3.5 w-3.5 ml-1 text-muted-foreground" />
                          </Link>
                        </div>
                      </div>
                    );
                  })}
              </div>
            </div>

            {/* Task Status */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Task Status</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                {["pending", "running", "paused", "complete", "failed"].map(s => (
                  <div key={s} className="flex items-center justify-between rounded-xl border border-border/60 bg-card/60 px-4 py-2.5">
                    <div className="flex items-center gap-3">
                      <span className={cn("h-2.5 w-2.5 rounded-full",
                        s === "running" ? "bg-[rgb(34_197_94)]" :
                        s === "pending" ? "bg-[rgb(245_158_11)]" :
                        s === "paused" ? "bg-[rgb(59_130_246)]" :
                        s === "complete" ? "bg-[rgb(34_197_94)]" :
                        "bg-[rgb(239_68_68)]"
                      )} />
                      <p className="text-sm font-medium capitalize">{s}</p>
                    </div>
                    <p className="text-sm text-muted-foreground font-mono">{taskCounts.get(s) ?? 0}</p>
                  </div>
                ))}
              </CardContent>
            </Card>
          </div>
        )}
      </div>
    </AppShell>
  );
}
