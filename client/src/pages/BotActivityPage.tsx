import { useState } from "react";
import { Link } from "wouter";
import AppShell from "@/components/AppShell";
import Seo from "@/components/Seo";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { useToast } from "@/hooks/use-toast";
import { useQuery, useMutation } from "@tanstack/react-query";
import { apiRequest, queryClient } from "@/lib/queryClient";
import type { BotActivityResponse, BotActivityItem } from "@shared/schema";
import { cn } from "@/lib/utils";
import {
  Github, RefreshCw, UploadCloud, Bot, Activity, CheckCircle2, AlertCircle,
  Loader2, FolderOpen, GitPullRequest, ExternalLink, FileCode, Coffee,
  BarChart2, Play, Zap, BrainCircuit, Globe, Download, Clock, TrendingUp,
  Building2, Calculator, FlaskConical, Brain, Trophy, Cpu, Network, Store,
  Wallet, CreditCard, Rocket, Code, Landmark, Bug, Tag, Plug, DollarSign,
  Sparkles, Shield, LayoutDashboard, ArrowRight, CheckCheck, XCircle,
} from "lucide-react";

const REPO = "DreamCo-Technologies/Dreamcobots";
const ACTIONS_URL = `https://github.com/${REPO}/actions`;
const DASHBOARD_WF_URL = `https://github.com/${REPO}/actions/workflows/dreamco-live-dashboard.yml`;

const ICON_MAP: Record<string, any> = {
  Bot, BrainCircuit, Building2, Calculator, FlaskConical, Brain, Trophy, Cpu,
  Globe, Network, Store, Wallet, CreditCard, Rocket, Code, Landmark, Bug,
  TrendingUp, Tag, Plug, Clock, DollarSign, Zap, Activity, LayoutDashboard,
};

const BASE_MODULES = [
  { id: "fleet",        name: "Bot Fleet",       path: "/bots",           icon: "Bot",          color: "blue" },
  { id: "buddy",        name: "Buddy Bot",        path: "/bots/buddy-bot", icon: "BrainCircuit", color: "violet" },
  { id: "divisions",    name: "Divisions",        path: "/divisions",      icon: "Building2",    color: "indigo" },
  { id: "deals",        name: "Deal Analyzer",    path: "/deals",          icon: "Calculator",   color: "emerald" },
  { id: "formulas",     name: "Formula Vault",    path: "/formulas",       icon: "FlaskConical", color: "amber" },
  { id: "learning",     name: "Learning Matrix",  path: "/learning-matrix",icon: "Brain",        color: "cyan" },
  { id: "ai-leaders",   name: "AI Leaders",       path: "/ai-leaders",     icon: "Trophy",       color: "yellow" },
  { id: "ai-models",    name: "AI Models Hub",    path: "/ai-models",      icon: "Cpu",          color: "pink" },
  { id: "ecosystem",    name: "AI Ecosystem",     path: "/ecosystem",      icon: "Globe",        color: "teal" },
  { id: "orchestration",name: "Orchestration",    path: "/orchestration",  icon: "Network",      color: "purple" },
  { id: "marketplace",  name: "Marketplace",      path: "/marketplace",    icon: "Store",        color: "orange" },
  { id: "crypto",       name: "Crypto",           path: "/crypto",         icon: "Wallet",       color: "green" },
  { id: "payments",     name: "Payments",         path: "/payments",       icon: "CreditCard",   color: "blue" },
  { id: "business",     name: "Biz Launch",       path: "/business",       icon: "Rocket",       color: "rose" },
  { id: "code-lab",     name: "Code Lab",         path: "/code-lab",       icon: "Code",         color: "cyan" },
  { id: "loans",        name: "Loans & Deals",    path: "/loans",          icon: "Landmark",     color: "lime" },
  { id: "debug",        name: "Debug Intel",      path: "/debug",          icon: "Bug",          color: "red" },
  { id: "revenue",      name: "Revenue",          path: "/revenue",        icon: "TrendingUp",   color: "green" },
  { id: "pricing",      name: "Pricing",          path: "/pricing",        icon: "Tag",          color: "violet" },
  { id: "connections",  name: "Connections",      path: "/connections",    icon: "Plug",         color: "sky" },
  { id: "time-capsule", name: "Time Capsule",     path: "/time-capsule",   icon: "Clock",        color: "slate" },
  { id: "costs",        name: "Cost Tracking",    path: "/costs",          icon: "DollarSign",   color: "amber" },
  { id: "autonomy",     name: "Autonomy",         path: "/autonomy",       icon: "Zap",          color: "yellow" },
  { id: "era-testing",  name: "Era Testing",      path: "/bot-activity",   icon: "Activity",     color: "indigo" },
];

const COLOR_MAP: Record<string, { bg: string; border: string; text: string; dot: string }> = {
  blue:    { bg: "bg-blue-500/10",    border: "border-blue-500/20",    text: "text-blue-400",    dot: "bg-blue-400" },
  violet:  { bg: "bg-violet-500/10",  border: "border-violet-500/20",  text: "text-violet-400",  dot: "bg-violet-400" },
  indigo:  { bg: "bg-indigo-500/10",  border: "border-indigo-500/20",  text: "text-indigo-400",  dot: "bg-indigo-400" },
  emerald: { bg: "bg-emerald-500/10", border: "border-emerald-500/20", text: "text-emerald-400", dot: "bg-emerald-400" },
  amber:   { bg: "bg-amber-500/10",   border: "border-amber-500/20",   text: "text-amber-400",   dot: "bg-amber-400" },
  cyan:    { bg: "bg-cyan-500/10",    border: "border-cyan-500/20",    text: "text-cyan-400",    dot: "bg-cyan-400" },
  yellow:  { bg: "bg-yellow-500/10",  border: "border-yellow-500/20",  text: "text-yellow-400",  dot: "bg-yellow-400" },
  pink:    { bg: "bg-pink-500/10",    border: "border-pink-500/20",    text: "text-pink-400",    dot: "bg-pink-400" },
  teal:    { bg: "bg-teal-500/10",    border: "border-teal-500/20",    text: "text-teal-400",    dot: "bg-teal-400" },
  purple:  { bg: "bg-purple-500/10",  border: "border-purple-500/20",  text: "text-purple-400",  dot: "bg-purple-400" },
  orange:  { bg: "bg-orange-500/10",  border: "border-orange-500/20",  text: "text-orange-400",  dot: "bg-orange-400" },
  green:   { bg: "bg-green-500/10",   border: "border-green-500/20",   text: "text-green-400",   dot: "bg-green-400" },
  rose:    { bg: "bg-rose-500/10",    border: "border-rose-500/20",    text: "text-rose-400",    dot: "bg-rose-400" },
  red:     { bg: "bg-red-500/10",     border: "border-red-500/20",     text: "text-red-400",     dot: "bg-red-400" },
  sky:     { bg: "bg-sky-500/10",     border: "border-sky-500/20",     text: "text-sky-400",     dot: "bg-sky-400" },
  slate:   { bg: "bg-slate-500/10",   border: "border-slate-500/20",   text: "text-slate-400",   dot: "bg-slate-400" },
  lime:    { bg: "bg-lime-500/10",    border: "border-lime-500/20",    text: "text-lime-400",    dot: "bg-lime-400" },
};

const LANG_COLORS: Record<string, string> = {
  python: "bg-blue-500/15 text-blue-400 border-blue-500/30",
  java: "bg-amber-500/15 text-amber-400 border-amber-500/30",
  typescript: "bg-cyan-500/15 text-cyan-400 border-cyan-500/30",
  general: "bg-muted text-muted-foreground border-border/50",
};

const LANG_ICONS: Record<string, any> = {
  python: FileCode, java: Coffee, typescript: FileCode, general: Bot,
};

export default function BotActivityPage() {
  const { toast } = useToast();
  const [selectedBotSlug, setSelectedBotSlug] = useState<string | undefined>();
  const [activeTab, setActiveTab] = useState<"activity" | "github" | "dashboard" | "classify">("dashboard");

  const activity = useQuery<BotActivityResponse>({ queryKey: ["/api/bot-activity"], refetchInterval: 15000 });
  const github = useQuery({ queryKey: ["/api/github/status"], retry: 1 });
  const classify = useQuery({ queryKey: ["/api/github/classify"] });
  const workflows = useQuery({
    queryKey: ["/api/github/workflows"],
    retry: 1,
    refetchInterval: activeTab === "dashboard" ? 30000 : false,
  });
  const lastRun = useQuery({
    queryKey: ["/api/github/last-dashboard-run"],
    retry: 1,
    refetchInterval: activeTab === "dashboard" ? 60000 : false,
    enabled: activeTab === "dashboard",
  });
  const modulesStatus = useQuery({
    queryKey: ["/api/modules/status"],
    retry: 1,
    refetchInterval: activeTab === "dashboard" ? 60000 : false,
    enabled: activeTab === "dashboard",
  });

  const pushAll = useMutation({
    mutationFn: () => apiRequest("POST", "/api/github/push-all", {}),
    onSuccess: (data: any) => {
      queryClient.invalidateQueries({ queryKey: ["/api/github/status"] });
      toast({ title: `✅ Pushed ${data.pushed} bots to GitHub!`, description: `Python: ${data.byLang?.python ?? 0} | Java: ${data.byLang?.java ?? 0} | TS: ${data.byLang?.typescript ?? 0} | ${data.errors?.length ?? 0} errors` });
    },
    onError: (e: any) => toast({ title: "Push failed", description: e.message, variant: "destructive" }),
  });

  const pushSource = useMutation({
    mutationFn: () => apiRequest("POST", "/api/github/push-source", {}),
    onSuccess: (data: any) => {
      toast({ title: `✅ Source code pushed!`, description: `${data.pushed} files synced to empire-os/ on GitHub` });
    },
    onError: (e: any) => toast({ title: "Source push failed", description: e.message, variant: "destructive" }),
  });

  const triggerDashboard = useMutation({
    mutationFn: () => apiRequest("POST", "/api/github/trigger-workflow", { workflow: "dreamco-live-dashboard.yml" }),
    onSuccess: () => {
      toast({ title: "🚀 Master Dashboard triggered!", description: "All 24 modules testing in GitHub Actions — refresh in ~3 minutes" });
      setTimeout(() => {
        queryClient.invalidateQueries({ queryKey: ["/api/github/last-dashboard-run"] });
        queryClient.invalidateQueries({ queryKey: ["/api/modules/status"] });
      }, 5000);
    },
    onError: (e: any) => toast({ title: "Trigger failed", description: e.message, variant: "destructive" }),
  });

  const tabs = [
    { id: "dashboard", label: "Command Center", icon: LayoutDashboard },
    { id: "activity", label: "Bot Activity", icon: Activity },
    { id: "github", label: "GitHub Sync", icon: Github },
    { id: "classify", label: "Bot Languages", icon: FolderOpen },
  ] as const;

  const wfData = (workflows.data as any) ?? {};
  const runs = wfData.runs ?? [];
  const wfList = wfData.workflows ?? [];
  // Merge API status data onto BASE_MODULES — grid always shows all 24 even when GitHub is offline
  const apiModules: any[] = (modulesStatus.data as any)?.modules ?? [];
  const statusMap = Object.fromEntries(apiModules.map((m: any) => [m.id, m]));
  const modules = BASE_MODULES.map(m => ({ ...m, status: "unknown", jobName: null, lastRunAt: null, runUrl: null, ...statusMap[m.id] }));
  const overallHealth = (modulesStatus.data as any)?.overallHealth ?? 0;
  const lastModuleRunAt = (modulesStatus.data as any)?.lastRunAt;
  const lastModuleRunUrl = (modulesStatus.data as any)?.lastRunUrl;
  const isOffline = (modulesStatus.data as any)?.offline ?? !modulesStatus.data;

  const passCount = modules.filter((m: any) => m.status === "success").length;
  const failCount = modules.filter((m: any) => m.status === "failure").length;
  const unknownCount = modules.length - passCount - failCount;

  return (
    <AppShell selectedBotSlug={selectedBotSlug} onBotChange={setSelectedBotSlug}>
      <Seo title="Command Center — DreamCo Empire OS" description="24-module command center with GitHub Actions integration" />

      <div className="buddy-appear space-y-6">
        <div className="flex flex-col md:flex-row md:items-end md:justify-between gap-4">
          <div>
            <h2 className="text-3xl md:text-4xl" data-testid="activity-title">Empire Command Center</h2>
            <p className="mt-1 text-muted-foreground">24-module live testing · {REPO}</p>
          </div>
          <div className="flex gap-2">
            {activeTab === "github" && (
              <Button onClick={() => pushAll.mutate()} disabled={pushAll.isPending} className="rounded-xl bg-gradient-to-r from-primary to-accent text-primary-foreground shadow-md" data-testid="push-all-btn">
                {pushAll.isPending ? <><Loader2 className="h-4 w-4 mr-2 animate-spin" />Pushing...</> : <><UploadCloud className="h-4 w-4 mr-2" />Push All Bots</>}
              </Button>
            )}
            {activeTab === "dashboard" && (
              <Button onClick={() => triggerDashboard.mutate()} disabled={triggerDashboard.isPending} className="rounded-xl bg-gradient-to-r from-violet-600 to-blue-600 text-white shadow-md" data-testid="trigger-dashboard-btn">
                {triggerDashboard.isPending ? <><Loader2 className="h-4 w-4 mr-2 animate-spin" />Triggering...</> : <><Play className="h-4 w-4 mr-2" />Run All 24 Tests</>}
              </Button>
            )}
          </div>
        </div>

        {/* Tabs */}
        <div className="flex flex-wrap gap-2" data-testid="activity-tabs">
          {tabs.map(tab => {
            const Icon = tab.icon;
            return (
              <button key={tab.id} onClick={() => setActiveTab(tab.id)} className={cn("flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium border transition-all", activeTab === tab.id ? "bg-primary text-primary-foreground border-primary shadow-sm" : "bg-card/60 border-border/60 text-muted-foreground hover:text-foreground hover:bg-card")} data-testid={`tab-${tab.id}`}>
                <Icon className="h-4 w-4" /> {tab.label}
              </button>
            );
          })}
        </div>

        {/* ── COMMAND CENTER TAB ── */}
        {activeTab === "dashboard" && (
          <div className="space-y-5">
            {/* Hero — overall health */}
            <Card className="buddy-card rounded-2xl border-violet-500/30 bg-gradient-to-br from-violet-500/10 via-blue-500/5 to-transparent p-6">
              <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-5">
                <div className="flex items-center gap-6">
                  <div className="text-center">
                    <p className={cn("text-5xl font-black tabular-nums", overallHealth >= 80 ? "text-green-400" : overallHealth >= 50 ? "text-amber-400" : "text-red-400")} data-testid="health-score">{overallHealth}%</p>
                    <p className="text-xs text-muted-foreground mt-1">System Health</p>
                  </div>
                  <div className="grid grid-cols-3 gap-3">
                    <div className="text-center p-3 rounded-xl bg-green-500/10 border border-green-500/20">
                      <p className="text-xl font-bold text-green-400">{passCount}</p>
                      <p className="text-[10px] text-muted-foreground">Passing</p>
                    </div>
                    <div className="text-center p-3 rounded-xl bg-red-500/10 border border-red-500/20">
                      <p className="text-xl font-bold text-red-400">{failCount}</p>
                      <p className="text-[10px] text-muted-foreground">Failing</p>
                    </div>
                    <div className="text-center p-3 rounded-xl bg-muted/30 border border-border/40">
                      <p className="text-xl font-bold text-muted-foreground">{unknownCount}</p>
                      <p className="text-[10px] text-muted-foreground">Pending</p>
                    </div>
                  </div>
                </div>
                <div className="space-y-2">
                  <div className="flex items-center gap-2 text-xs text-muted-foreground">
                    <Clock className="h-3.5 w-3.5" />
                    {lastModuleRunAt ? <>Last run: {new Date(lastModuleRunAt).toLocaleString()}</> : "No run data — click Run All Tests"}
                  </div>
                  {isOffline && (
                    <div className="flex items-center gap-1.5 text-xs text-amber-400">
                      <AlertCircle className="h-3.5 w-3.5" />GitHub token expired — refresh at github.com/settings/tokens
                    </div>
                  )}
                  <div className="flex gap-2">
                    <Button onClick={() => triggerDashboard.mutate()} disabled={triggerDashboard.isPending} className="rounded-xl bg-gradient-to-r from-violet-600 to-blue-600 text-white" data-testid="run-all-btn">
                      {triggerDashboard.isPending ? <><Loader2 className="h-4 w-4 mr-2 animate-spin" />Triggering...</> : <><Play className="h-4 w-4 mr-2" />Run All Tests</>}
                    </Button>
                    {lastModuleRunUrl && (
                      <a href={lastModuleRunUrl} target="_blank" rel="noreferrer">
                        <Button variant="outline" className="rounded-xl" data-testid="view-last-run-btn"><ExternalLink className="h-4 w-4 mr-2" />View Run</Button>
                      </a>
                    )}
                    <Button variant="ghost" size="icon" className="rounded-xl" onClick={() => { queryClient.invalidateQueries({ queryKey: ["/api/modules/status"] }); queryClient.invalidateQueries({ queryKey: ["/api/github/last-dashboard-run"] }); }} data-testid="refresh-modules-btn">
                      <RefreshCw className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </div>
            </Card>

            {/* 24 Module Grid — always rendered; status overlaid from API */}
            <div className="grid grid-cols-2 md:grid-cols-3 xl:grid-cols-4 gap-3" data-testid="modules-grid">
                {modules.map((mod: any) => {
                  const Icon = ICON_MAP[mod.icon] ?? Bot;
                  const palette = COLOR_MAP[mod.color] ?? COLOR_MAP.blue;
                  const isPass = mod.status === "success";
                  const isFail = mod.status === "failure";
                  const isRunning = mod.status === "in_progress";
                  return (
                    <Card key={mod.id} className={cn("buddy-card rounded-2xl border p-4 flex flex-col justify-between group hover:shadow-md transition-all", palette.bg, palette.border)} data-testid={`module-card-${mod.id}`}>
                      <div className="flex items-start justify-between mb-3">
                        <div className="flex items-center gap-2">
                          <Icon className={cn("h-5 w-5", palette.text)} />
                          <span className={cn("h-2 w-2 rounded-full", isPass ? "bg-green-400" : isFail ? "bg-red-400" : isRunning ? "bg-amber-400 animate-pulse" : "bg-muted-foreground/40")} />
                        </div>
                        {isPass && <CheckCircle2 className="h-3.5 w-3.5 text-green-400 opacity-80" />}
                        {isFail && <XCircle className="h-3.5 w-3.5 text-red-400 opacity-80" />}
                      </div>
                      <div className="flex-1">
                        <p className="font-semibold text-sm leading-tight">{mod.name}</p>
                        <p className={cn("text-[10px] mt-0.5 font-medium capitalize", isPass ? "text-green-400" : isFail ? "text-red-400" : isRunning ? "text-amber-400" : "text-muted-foreground")}>
                          {mod.status === "unknown" ? "not yet tested" : mod.status}
                        </p>
                      </div>
                      <div className="flex items-center gap-1.5 mt-3">
                        <Link href={mod.path}>
                          <Button size="sm" variant="secondary" className="rounded-lg h-7 text-[11px] flex-1" data-testid={`open-module-${mod.id}`}>
                            Open <ArrowRight className="h-3 w-3 ml-1" />
                          </Button>
                        </Link>
                        {mod.runUrl && (
                          <a href={mod.runUrl} target="_blank" rel="noreferrer">
                            <Button size="sm" variant="ghost" className="rounded-lg h-7 w-7 p-0" data-testid={`run-link-${mod.id}`}>
                              <ExternalLink className="h-3 w-3" />
                            </Button>
                          </a>
                        )}
                      </div>
                    </Card>
                  );
                })}
                {modules.length === 0 && (
                  <div className="col-span-4 py-12 text-center space-y-3">
                    <Github className="h-10 w-10 text-muted-foreground/40 mx-auto" />
                    <p className="text-sm text-muted-foreground">No module data yet</p>
                    <p className="text-xs text-muted-foreground">Click "Run All Tests" to kick off the 24-module GitHub Actions pipeline</p>
                    <Button onClick={() => triggerDashboard.mutate()} disabled={triggerDashboard.isPending} className="rounded-xl" data-testid="empty-run-btn">
                      <Play className="h-4 w-4 mr-2" />Run All Tests
                    </Button>
                  </div>
                )}
            </div>

            {/* Last run job-level results */}
            {(lastRun.data as any)?.run && (() => {
              const lr = lastRun.data as any;
              const run = lr.run;
              const jobs: any[] = lr.jobs ?? [];
              const arts: any[] = lr.artifacts ?? [];
              const allPass = jobs.every((j: any) => j.conclusion === "success");
              const failJ = jobs.filter((j: any) => j.conclusion === "failure").length;
              return (
                <Card className={cn("buddy-card rounded-2xl border p-5 space-y-4", allPass ? "border-green-500/30 bg-green-500/5" : failJ > 0 ? "border-amber-500/30 bg-amber-500/5" : "border-border/60")} data-testid="last-run-detail">
                  <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-3">
                    <div>
                      <div className="flex items-center gap-2 mb-1">
                        <TrendingUp className="h-4 w-4 text-primary" />
                        <span className="font-bold text-sm">Last Workflow Run</span>
                        <Badge className={cn("text-[10px]", run.conclusion === "success" ? "bg-green-500/20 text-green-300 border-green-500/30" : "bg-amber-500/20 text-amber-300 border-amber-500/30")}>
                          {run.conclusion ?? "in progress"}
                        </Badge>
                      </div>
                      <p className="text-xs text-muted-foreground flex items-center gap-2">
                        <Clock className="h-3 w-3" />
                        {run.created_at ? new Date(run.created_at).toLocaleString() : ""} · {jobs.length}/6 jobs · {arts.length} artifacts
                      </p>
                    </div>
                    <a href={run.html_url} target="_blank" rel="noreferrer">
                      <Button variant="outline" size="sm" className="rounded-xl" data-testid="view-run-detail-btn"><ExternalLink className="h-3.5 w-3.5 mr-1.5" />View Full Run</Button>
                    </a>
                  </div>
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                    {jobs.map((job: any) => {
                      const ok = job.conclusion === "success";
                      const dur = job.started_at && job.completed_at ? Math.round((new Date(job.completed_at).getTime() - new Date(job.started_at).getTime()) / 1000) : null;
                      return (
                        <div key={job.id} className={cn("flex items-center gap-2 p-3 rounded-xl border text-sm", ok ? "bg-muted/20 border-border/40" : "bg-red-500/5 border-red-500/20")} data-testid={`job-${job.id}`}>
                          <span className={cn("h-2 w-2 rounded-full flex-shrink-0", ok ? "bg-green-400" : "bg-red-400")} />
                          <div className="min-w-0">
                            <p className="font-medium text-xs truncate">{job.name.replace(/ - .+$/, "")}</p>
                            <p className="text-[10px] text-muted-foreground">{ok ? `✓ ${dur ? dur + "s" : "passed"}` : "✗ failed"}</p>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                  {arts.length > 0 && (
                    <div>
                      <p className="text-xs text-muted-foreground font-medium mb-2">📦 Artifacts ({arts.length})</p>
                      <div className="flex flex-wrap gap-2">
                        {arts.map((a: any) => (
                          <a key={a.id} href={run.html_url} target="_blank" rel="noreferrer" className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg border border-border/50 bg-muted/30 text-xs hover:bg-muted/50 transition-colors" data-testid={`artifact-${a.id}`}>
                            <Download className="h-3 w-3 text-muted-foreground" />
                            {a.name}
                          </a>
                        ))}
                      </div>
                    </div>
                  )}
                </Card>
              );
            })()}

            {/* GitHub workflow list */}
            <Card className="buddy-card rounded-2xl border-border/60 p-5">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2">
                  <Github className="h-4 w-4 text-muted-foreground" />
                  <span className="font-semibold text-sm">Recent Workflow Runs</span>
                </div>
                <div className="flex items-center gap-2">
                  <Button variant="ghost" size="sm" className="rounded-lg text-xs h-7" onClick={() => (workflows as any).refetch()} data-testid="refresh-runs-btn">
                    <RefreshCw className="h-3 w-3 mr-1" />Refresh
                  </Button>
                  <a href={ACTIONS_URL} target="_blank" rel="noreferrer" className="text-xs text-primary hover:underline flex items-center gap-1" data-testid="all-actions-link">
                    All Actions <ExternalLink className="h-3 w-3" />
                  </a>
                </div>
              </div>
              {workflows.isLoading ? (
                <div className="space-y-2">{Array.from({ length: 4 }).map((_, i) => <Skeleton key={i} className="h-10 rounded-xl" />)}</div>
              ) : runs.length === 0 ? (
                <div className="p-6 text-center space-y-2">
                  <p className="text-sm text-muted-foreground">No workflow data — token may be expired</p>
                  <a href={ACTIONS_URL} target="_blank" rel="noreferrer">
                    <Button variant="outline" size="sm" className="rounded-xl" data-testid="open-actions-btn"><ExternalLink className="h-3.5 w-3.5 mr-1.5" />Open GitHub Actions</Button>
                  </a>
                </div>
              ) : (
                <div className="space-y-2">
                  {runs.slice(0, 12).map((run: any) => {
                    const statusColor = run.conclusion === "success" ? "text-green-400" : run.conclusion === "failure" ? "text-red-400" : run.status === "in_progress" ? "text-amber-400 animate-pulse" : "text-muted-foreground";
                    const statusDot = run.conclusion === "success" ? "bg-green-400" : run.conclusion === "failure" ? "bg-red-400" : run.status === "in_progress" ? "bg-amber-400" : "bg-muted-foreground/40";
                    return (
                      <div key={run.id} className="flex items-center gap-3 p-3 rounded-xl bg-muted/20 hover:bg-muted/30 transition-colors border border-border/30" data-testid={`run-${run.id}`}>
                        <span className={cn("h-2 w-2 rounded-full flex-shrink-0", statusDot)} />
                        <div className="min-w-0 flex-1">
                          <p className="text-sm font-medium truncate">{run.name}</p>
                          <p className="text-[11px] text-muted-foreground">{run.created_at ? new Date(run.created_at).toLocaleString() : ""}</p>
                        </div>
                        <div className="flex items-center gap-2 flex-shrink-0">
                          <span className={cn("text-xs font-medium capitalize", statusColor)}>{run.conclusion || run.status}</span>
                          {run.html_url && <a href={run.html_url} target="_blank" rel="noreferrer" className="text-muted-foreground hover:text-primary"><ExternalLink className="h-3.5 w-3.5" /></a>}
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </Card>

            {/* All active workflows */}
            {wfList.length > 0 && (
              <Card className="buddy-card rounded-2xl border-border/60 p-5">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-2">
                    <Zap className="h-4 w-4 text-amber-400" />
                    <span className="font-semibold text-sm">All Workflows ({wfList.length})</span>
                  </div>
                  <a href={DASHBOARD_WF_URL} target="_blank" rel="noreferrer" className="text-xs text-primary hover:underline flex items-center gap-1" data-testid="dashboard-wf-link">
                    Master Dashboard <ExternalLink className="h-3 w-3" />
                  </a>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                  {wfList.map((wf: any) => (
                    <div key={wf.id} className="flex items-center justify-between p-3 rounded-xl border border-border/40 bg-card/40 hover:bg-card/60 transition-colors" data-testid={`wf-${wf.id}`}>
                      <div className="min-w-0 flex-1">
                        <p className="text-sm font-medium truncate">{wf.name}</p>
                        <p className="text-[10px] text-muted-foreground font-mono truncate">{wf.path}</p>
                      </div>
                      <div className="flex items-center gap-2 flex-shrink-0 ml-2">
                        <Badge variant="outline" className={cn("text-[10px] rounded-md capitalize", wf.state === "active" ? "border-green-500/30 text-green-400" : "border-muted text-muted-foreground")}>{wf.state}</Badge>
                        {wf.html_url && <a href={wf.html_url} target="_blank" rel="noreferrer" className="text-muted-foreground hover:text-primary"><ExternalLink className="h-3 w-3" /></a>}
                      </div>
                    </div>
                  ))}
                </div>
              </Card>
            )}
          </div>
        )}

        {/* ── ACTIVITY TAB ── */}
        {activeTab === "activity" && (
          <div className="space-y-4">
            {activity.isLoading ? (
              <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-3">
                {Array.from({ length: 12 }).map((_, i) => <Skeleton key={i} className="h-28 rounded-2xl" />)}
              </div>
            ) : activity.isError ? (
              <Card className="buddy-card rounded-2xl p-6 text-center border-destructive/30">
                <AlertCircle className="h-8 w-8 text-destructive mx-auto mb-2" />
                <p className="text-sm text-muted-foreground">Could not load bot activity</p>
              </Card>
            ) : (
              <>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                  {[
                    { label: "Total Bots", value: activity.data?.totalBots ?? 0, color: "text-primary" },
                    { label: "Conversations", value: activity.data?.totalConversations ?? 0, color: "text-green-400" },
                    { label: "Bots with Memory", value: (activity.data?.bots ?? []).filter((b: BotActivityItem) => b.memoryCount > 0).length, color: "text-amber-400" },
                    { label: "Active Learning", value: (activity.data?.bots ?? []).reduce((a: number, b: BotActivityItem) => a + b.memoryCount, 0), color: "text-cyan-400" },
                  ].map(stat => (
                    <Card key={stat.label} className="buddy-card rounded-2xl border-border/60 p-4" data-testid={`stat-${stat.label}`}>
                      <p className="text-xs text-muted-foreground">{stat.label}</p>
                      <p className={cn("text-2xl font-bold mt-1", stat.color)}>{stat.value.toLocaleString()}</p>
                    </Card>
                  ))}
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-3">
                  {(activity.data?.bots ?? []).map((bot: BotActivityItem) => (
                    <Card key={bot.id} className="buddy-card rounded-2xl border-border/60 p-4 hover:border-border transition-all" data-testid={`bot-activity-${bot.id}`}>
                      <div className="flex items-start justify-between gap-2">
                        <div className="min-w-0 flex-1">
                          <p className="font-semibold text-sm truncate">{bot.displayName}</p>
                          <p className="text-xs text-muted-foreground truncate">{bot.division}</p>
                        </div>
                        <div className="flex items-center gap-1.5 flex-shrink-0">
                          <span className={cn("h-2 w-2 rounded-full", bot.memoryCount > 0 ? "bg-green-400" : "bg-muted-foreground/40")} />
                          <Badge variant="outline" className="text-[10px] rounded-md capitalize">{bot.tier}</Badge>
                        </div>
                      </div>
                      {bot.lastLearning && (
                        <div className="mt-2 p-2 rounded-lg bg-primary/5 border border-primary/15">
                          <p className="text-[10px] text-primary/70 font-medium">🧠 Last Learning</p>
                          <p className="text-xs text-muted-foreground mt-0.5 line-clamp-2">{bot.lastLearning}</p>
                        </div>
                      )}
                      <div className="mt-2 flex items-center justify-between text-[11px] text-muted-foreground">
                        <span>{bot.memoryCount} memories</span>
                        <span className={cn("flex items-center gap-1", bot.status === "active" ? "text-green-400" : "text-muted-foreground")}>
                          {bot.status === "active" ? <><CheckCircle2 className="h-3 w-3" />Active</> : <><RefreshCw className="h-3 w-3" />Idle</>}
                        </span>
                      </div>
                    </Card>
                  ))}
                </div>
              </>
            )}
          </div>
        )}

        {/* ── GITHUB SYNC TAB ── */}
        {activeTab === "github" && (
          <div className="space-y-4">
            {github.isLoading ? <Skeleton className="h-40 rounded-2xl" /> : github.isError ? (
              <Card className="buddy-card rounded-2xl border-destructive/30 bg-destructive/5 p-6">
                <AlertCircle className="h-6 w-6 text-destructive mb-2" />
                <p className="font-semibold">GitHub connection failed</p>
                <p className="text-sm text-muted-foreground mt-1">Token may be expired — regenerate at github.com/settings/tokens and update GITHUB_TOKEN secret</p>
              </Card>
            ) : (
              <>
                <Card className="buddy-card rounded-2xl border-green-500/30 bg-green-500/5 p-5">
                  <div className="flex items-center gap-3 mb-3">
                    <CheckCircle2 className="h-5 w-5 text-green-400" />
                    <span className="font-semibold text-green-400">Connected to GitHub</span>
                  </div>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div><p className="text-xs text-muted-foreground">Repository</p><p className="font-semibold text-sm mt-0.5">{(github.data as any)?.repo?.name}</p></div>
                    <div><p className="text-xs text-muted-foreground">Stars</p><p className="font-semibold text-sm mt-0.5">{(github.data as any)?.repo?.stars ?? 0}</p></div>
                    <div><p className="text-xs text-muted-foreground">Forks</p><p className="font-semibold text-sm mt-0.5">{(github.data as any)?.repo?.forks ?? 0}</p></div>
                    <div><p className="text-xs text-muted-foreground">Branch</p><p className="font-semibold text-sm mt-0.5">{(github.data as any)?.repo?.defaultBranch}</p></div>
                  </div>
                  <a href={(github.data as any)?.repo?.url} target="_blank" rel="noreferrer" className="mt-3 inline-flex items-center gap-1.5 text-sm text-primary hover:underline" data-testid="repo-link">
                    <ExternalLink className="h-3.5 w-3.5" />View on GitHub
                  </a>
                </Card>

                <Card className="buddy-card rounded-2xl border-border/60 p-5 space-y-4">
                  <div className="flex items-center gap-2">
                    <UploadCloud className="h-4 w-4 text-primary" />
                    <span className="font-semibold text-sm">Push All Bots + Source Code to GitHub</span>
                  </div>
                  <div className="p-4 rounded-xl bg-muted/30 border border-border/50 space-y-2">
                    <p className="text-sm font-medium">Step 1 — Push {(activity.data as any)?.totalBots ?? 1051} Bot Profiles</p>
                    <p className="text-xs text-muted-foreground">Every bot → <code className="bg-muted px-1 rounded">bots/slug/replit_profile.json</code> + Python bots → <code className="bg-muted px-1 rounded">python_bots/</code> + Java → <code className="bg-muted px-1 rounded">java_bots/</code></p>
                    <Button onClick={() => pushAll.mutate()} disabled={pushAll.isPending || pushSource.isPending} className="rounded-xl w-full" data-testid="push-all-btn-2">
                      {pushAll.isPending ? <><Loader2 className="h-4 w-4 mr-2 animate-spin" />Pushing bots...</> : <><UploadCloud className="h-4 w-4 mr-2" />Push All {(activity.data as any)?.totalBots ?? 1051} Bots</>}
                    </Button>
                    {pushAll.isSuccess && (
                      <div className="p-3 rounded-xl bg-green-500/10 border border-green-500/20 text-sm text-green-400">
                        ✅ {(pushAll.data as any)?.pushed} bots pushed · Python: {(pushAll.data as any)?.byLang?.python} · Java: {(pushAll.data as any)?.byLang?.java} · {(pushAll.data as any)?.errors?.length ?? 0} errors
                      </div>
                    )}
                  </div>
                  <div className="p-4 rounded-xl bg-muted/30 border border-border/50 space-y-2">
                    <p className="text-sm font-medium">Step 2 — Push Full Source Code (empire-os/)</p>
                    <p className="text-xs text-muted-foreground">All 24 pages, server routes, shared schema → <code className="bg-muted px-1 rounded">empire-os/</code></p>
                    <Button onClick={() => pushSource.mutate()} disabled={pushSource.isPending || pushAll.isPending} variant="outline" className="rounded-xl w-full" data-testid="push-source-btn">
                      {pushSource.isPending ? <><Loader2 className="h-4 w-4 mr-2 animate-spin" />Pushing source...</> : <><Github className="h-4 w-4 mr-2" />Push Full Source Code</>}
                    </Button>
                    {pushSource.isSuccess && (
                      <div className="p-3 rounded-xl bg-green-500/10 border border-green-500/20 text-sm text-green-400">
                        ✅ {(pushSource.data as any)?.pushed} source files pushed to empire-os/
                      </div>
                    )}
                  </div>
                </Card>

                {((github.data as any)?.pullRequests ?? []).length > 0 && (
                  <Card className="buddy-card rounded-2xl border-border/60 p-5">
                    <div className="flex items-center gap-2 mb-4">
                      <GitPullRequest className="h-4 w-4 text-primary" />
                      <span className="font-semibold text-sm">Pull Requests ({(github.data as any)?.pullRequests?.length})</span>
                    </div>
                    <div className="space-y-2">
                      {((github.data as any)?.pullRequests ?? []).map((pr: any) => (
                        <div key={pr.id} className="flex items-center justify-between gap-3 p-3 rounded-xl border border-border/50 bg-card/40" data-testid={`pr-${pr.id}`}>
                          <div className="min-w-0">
                            <p className="text-sm font-medium truncate">#{pr.id} {pr.title}</p>
                            <p className="text-xs text-muted-foreground">by {pr.author}</p>
                          </div>
                          <div className="flex items-center gap-2 flex-shrink-0">
                            <Badge variant={pr.state === "open" ? "default" : "secondary"} className="text-xs capitalize">{pr.state}</Badge>
                            <a href={pr.url} target="_blank" rel="noreferrer" className="text-primary hover:text-primary/80"><ExternalLink className="h-3.5 w-3.5" /></a>
                          </div>
                        </div>
                      ))}
                    </div>
                  </Card>
                )}
              </>
            )}
          </div>
        )}

        {/* ── CLASSIFY TAB ── */}
        {activeTab === "classify" && (
          <div className="space-y-4">
            {classify.isLoading ? <Skeleton className="h-40 rounded-2xl" /> : (
              <>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                  {Object.entries((classify.data as any)?.summary ?? {}).filter(([k]) => k !== "total").map(([lang, count]) => {
                    const Icon = LANG_ICONS[lang] ?? Bot;
                    return (
                      <Card key={lang} className={cn("buddy-card rounded-2xl border p-4", LANG_COLORS[lang])} data-testid={`lang-${lang}`}>
                        <Icon className="h-5 w-5 mb-2" />
                        <p className="text-xs font-medium capitalize">bots/{lang}/</p>
                        <p className="text-2xl font-bold mt-1">{count as number}</p>
                        <p className="text-xs opacity-70 mt-0.5">{lang} bots</p>
                      </Card>
                    );
                  })}
                </div>
                <Card className="buddy-card rounded-2xl border-border/60 overflow-hidden">
                  <div className="p-4 border-b border-border/60">
                    <p className="text-sm font-medium">All {(classify.data as any)?.summary?.total} bots classified</p>
                  </div>
                  <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                      <thead>
                        <tr className="border-b border-border/60 bg-muted/30">
                          <th className="text-left px-4 py-2.5 text-xs font-medium text-muted-foreground">Bot Name</th>
                          <th className="text-left px-4 py-2.5 text-xs font-medium text-muted-foreground">Division</th>
                          <th className="text-left px-4 py-2.5 text-xs font-medium text-muted-foreground">GitHub Folder</th>
                        </tr>
                      </thead>
                      <tbody>
                        {((classify.data as any)?.bots ?? []).map((bot: any) => (
                          <tr key={bot.id} className="border-b border-border/30 hover:bg-muted/20 transition-colors" data-testid={`classify-row-${bot.id}`}>
                            <td className="px-4 py-2.5">
                              <Link href={`/bot/${bot.slug}`} className="font-medium hover:text-primary transition-colors">{bot.displayName}</Link>
                            </td>
                            <td className="px-4 py-2.5 text-muted-foreground">{bot.division}</td>
                            <td className="px-4 py-2.5">
                              <Badge variant="outline" className={cn("text-[10px] rounded-md", LANG_COLORS[bot.language])}>{bot.language === "general" ? "bots/" : `${bot.language}_bots/`}</Badge>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </Card>
              </>
            )}
          </div>
        )}
      </div>
    </AppShell>
  );
}
