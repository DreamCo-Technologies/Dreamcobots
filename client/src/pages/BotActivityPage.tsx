import { useState } from "react";
import AppShell from "@/components/AppShell";
import Seo from "@/components/Seo";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { useToast } from "@/hooks/use-toast";
import { useQuery, useMutation } from "@tanstack/react-query";
import { apiRequest } from "@/lib/queryClient";
import { cn } from "@/lib/utils";
import { Github, RefreshCw, UploadCloud, Bot, Activity, CheckCircle2, AlertCircle, Loader2, FolderOpen, GitPullRequest, ExternalLink, FileCode, Coffee, BarChart2, Play, Zap, BrainCircuit, Globe, Download, Clock, TrendingUp } from "lucide-react";

const REPO = "DreamCo-Technologies/Dreamcobots";
const ACTIONS_URL = `https://github.com/${REPO}/actions`;
const DASHBOARD_WF_URL = `https://github.com/${REPO}/actions/workflows/dreamco-live-dashboard.yml`;

const LANG_COLORS: Record<string, string> = {
  python: "bg-blue-500/15 text-blue-400 border-blue-500/30",
  java: "bg-amber-500/15 text-amber-400 border-amber-500/30",
  typescript: "bg-cyan-500/15 text-cyan-400 border-cyan-500/30",
  general: "bg-muted text-muted-foreground border-border/50",
};

const LANG_ICONS: Record<string, any> = {
  python: FileCode,
  java: Coffee,
  typescript: FileCode,
  general: Bot,
};

export default function BotActivityPage() {
  const { toast } = useToast();
  const [selectedBotSlug, setSelectedBotSlug] = useState<string | undefined>();
  const [activeTab, setActiveTab] = useState<"activity" | "github" | "dashboard" | "classify">("activity");

  const activity = useQuery({ queryKey: ["/api/bot-activity"], refetchInterval: 15000 });
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

  const pushAll = useMutation({
    mutationFn: () => apiRequest("POST", "/api/github/push-all", {}),
    onSuccess: (data: any) => {
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
      toast({ title: "🚀 Live Dashboard triggered!", description: "Check GitHub Actions in ~2 minutes for results" });
    },
    onError: (e: any) => toast({ title: "Trigger failed", description: e.message, variant: "destructive" }),
  });

  const tabs = [
    { id: "activity", label: "Bot Activity", icon: Activity },
    { id: "github", label: "GitHub Sync", icon: Github },
    { id: "dashboard", label: "Live Dashboard", icon: BarChart2 },
    { id: "classify", label: "Bot Languages", icon: FolderOpen },
  ] as const;

  const wfData = (workflows.data as any) ?? {};
  const runs = wfData.runs ?? [];
  const wfList = wfData.workflows ?? [];

  return (
    <AppShell selectedBotSlug={selectedBotSlug} onBotChange={setSelectedBotSlug}>
      <Seo title="Bot Activity & GitHub — DreamCo Empire OS" description="Monitor all bots and sync to GitHub" />

      <div className="buddy-appear space-y-6">
        <div className="flex flex-col md:flex-row md:items-end md:justify-between gap-4">
          <div>
            <h2 className="text-3xl md:text-4xl" data-testid="activity-title">Bot Activity & GitHub</h2>
            <p className="mt-1 text-muted-foreground">Real-time bot monitoring · {REPO}</p>
          </div>
          <div className="flex gap-2">
            {activeTab === "github" && (
              <Button onClick={() => pushAll.mutate()} disabled={pushAll.isPending} className="rounded-xl bg-gradient-to-r from-primary to-accent text-primary-foreground shadow-md" data-testid="push-all-btn">
                {pushAll.isPending ? <><Loader2 className="h-4 w-4 mr-2 animate-spin" />Pushing...</> : <><UploadCloud className="h-4 w-4 mr-2" />Push All Bots</>}
              </Button>
            )}
            {activeTab === "dashboard" && (
              <Button onClick={() => triggerDashboard.mutate()} disabled={triggerDashboard.isPending} className="rounded-xl bg-gradient-to-r from-violet-600 to-blue-600 text-white shadow-md" data-testid="trigger-dashboard-btn">
                {triggerDashboard.isPending ? <><Loader2 className="h-4 w-4 mr-2 animate-spin" />Triggering...</> : <><Play className="h-4 w-4 mr-2" />Run Live Dashboard</>}
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
                    { label: "Bots with Memory", value: (activity.data?.bots ?? []).filter((b: any) => b.memoryCount > 0).length, color: "text-amber-400" },
                    { label: "Active Learning", value: (activity.data?.bots ?? []).reduce((a: number, b: any) => a + b.memoryCount, 0), color: "text-cyan-400" },
                  ].map(stat => (
                    <Card key={stat.label} className="buddy-card rounded-2xl border-border/60 p-4" data-testid={`stat-${stat.label}`}>
                      <p className="text-xs text-muted-foreground">{stat.label}</p>
                      <p className={cn("text-2xl font-bold mt-1", stat.color)}>{stat.value.toLocaleString()}</p>
                    </Card>
                  ))}
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-3">
                  {(activity.data?.bots ?? []).map((bot: any) => (
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
                <p className="text-sm text-muted-foreground mt-1">{(github.error as any)?.message ?? "Check your GITHUB_TOKEN secret"}</p>
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

                <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                  {[
                    { label: "Python Bots", value: (classify.data as any)?.summary?.python ?? 0, sub: "→ python_bots/", color: "text-blue-400" },
                    { label: "Java Bots", value: (classify.data as any)?.summary?.java ?? 0, sub: "→ java_bots/", color: "text-amber-400" },
                    { label: "TS Bots", value: (classify.data as any)?.summary?.typescript ?? 0, sub: "→ empire-os/", color: "text-cyan-400" },
                    { label: "General Bots", value: (classify.data as any)?.summary?.general ?? 0, sub: "→ bots/{slug}/", color: "text-purple-400" },
                  ].map(s => (
                    <Card key={s.label} className="buddy-card rounded-2xl border-border/60 p-4">
                      <p className={cn("text-2xl font-bold", s.color)}>{s.value}</p>
                      <p className="text-xs font-medium mt-0.5">{s.label}</p>
                      <p className="text-[10px] text-muted-foreground font-mono mt-1">{s.sub}</p>
                    </Card>
                  ))}
                </div>

                <Card className="buddy-card rounded-2xl border-border/60 p-5 space-y-4">
                  <div className="flex items-center gap-2">
                    <UploadCloud className="h-4 w-4 text-primary" />
                    <span className="font-semibold text-sm">Full Merge — Best of Both Worlds</span>
                  </div>
                  <div className="p-4 rounded-xl bg-muted/30 border border-border/50 space-y-2">
                    <p className="text-sm font-medium">Step 1 — Push All {activity.data?.totalBots ?? 1051} Bot Profiles</p>
                    <p className="text-xs text-muted-foreground">Pushes every bot as <code className="bg-muted px-1 rounded">bots/slug/replit_profile.json</code> + Python bots to <code className="bg-muted px-1 rounded">python_bots/</code> + Java bots to <code className="bg-muted px-1 rounded">java_bots/</code></p>
                    <Button onClick={() => pushAll.mutate()} disabled={pushAll.isPending || pushSource.isPending} className="rounded-xl w-full" data-testid="push-all-btn-2">
                      {pushAll.isPending ? <><Loader2 className="h-4 w-4 mr-2 animate-spin" />Pushing bots...</> : <><UploadCloud className="h-4 w-4 mr-2" />Push All {activity.data?.totalBots ?? 1051} Bots</>}
                    </Button>
                    {pushAll.isSuccess && (
                      <div className="p-3 rounded-xl bg-green-500/10 border border-green-500/20 text-sm text-green-400">
                        ✅ {(pushAll.data as any)?.pushed} bots pushed · Python: {(pushAll.data as any)?.byLang?.python} · Java: {(pushAll.data as any)?.byLang?.java} · {(pushAll.data as any)?.errors?.length ?? 0} errors
                      </div>
                    )}
                  </div>
                  <div className="p-4 rounded-xl bg-muted/30 border border-border/50 space-y-2">
                    <p className="text-sm font-medium">Step 2 — Push Full Source Code</p>
                    <p className="text-xs text-muted-foreground">Pushes all pages, server files, shared schema to <code className="bg-muted px-1 rounded">empire-os/</code> on GitHub</p>
                    <Button onClick={() => pushSource.mutate()} disabled={pushSource.isPending || pushAll.isPending} variant="outline" className="rounded-xl w-full" data-testid="push-source-btn">
                      {pushSource.isPending ? <><Loader2 className="h-4 w-4 mr-2 animate-spin" />Pushing source files...</> : <><Github className="h-4 w-4 mr-2" />Push Full Source Code (empire-os/)</>}
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

        {/* ── LIVE DASHBOARD TAB ── */}
        {activeTab === "dashboard" && (
          <div className="space-y-4">
            {/* Hero card */}
            <Card className="buddy-card rounded-2xl border-violet-500/30 bg-gradient-to-br from-violet-500/10 to-blue-500/5 p-6">
              <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <BarChart2 className="h-5 w-5 text-violet-400" />
                    <span className="font-bold text-lg">DreamCo Live Dashboard</span>
                    <Badge className="bg-violet-500/20 text-violet-300 border-violet-500/30 text-[10px]">GitHub Actions</Badge>
                  </div>
                  <p className="text-sm text-muted-foreground">6-job parallel workflow testing: Fleet Scan · Buddy Bot Protocol · Global AI Sources · Era Testing (2024→2026) · Core Tests · HTML Report</p>
                </div>
                <div className="flex gap-2 flex-shrink-0">
                  <Button onClick={() => triggerDashboard.mutate()} disabled={triggerDashboard.isPending} className="rounded-xl bg-gradient-to-r from-violet-600 to-blue-600 text-white" data-testid="run-dashboard-btn">
                    {triggerDashboard.isPending ? <><Loader2 className="h-4 w-4 mr-2 animate-spin" />Triggering...</> : <><Play className="h-4 w-4 mr-2" />Run Now</>}
                  </Button>
                  <a href={DASHBOARD_WF_URL} target="_blank" rel="noreferrer">
                    <Button variant="outline" className="rounded-xl" data-testid="view-actions-btn"><ExternalLink className="h-4 w-4 mr-2" />View in GitHub</Button>
                  </a>
                </div>
              </div>
            </Card>

            {/* 6 test modules */}
            <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
              {[
                { icon: Bot, color: "text-blue-400", bg: "bg-blue-500/10 border-blue-500/20", label: "Fleet Scan", desc: "1,051+ bots across 45 divisions. Counts profiles, detects Buddy, maps all divisions." },
                { icon: BrainCircuit, color: "text-violet-400", bg: "bg-violet-500/10 border-violet-500/20", label: "Buddy Deep Test", desc: "8-point protocol check: slug, CommandCore division, 500+ libraries, routing keywords, fleet refs." },
                { icon: Globe, color: "text-cyan-400", bg: "bg-cyan-500/10 border-cyan-500/20", label: "Global AI Sources", desc: "Scans 200+ providers: OpenAI, Claude, Gemini, Llama, Mistral, Groq + tool belt verification." },
                { icon: Zap, color: "text-amber-400", bg: "bg-amber-500/10 border-amber-500/20", label: "Era Testing", desc: "15 checks across 3 eras: Foundation (2024) → Intelligence (2025) → Full Autonomy (2026)." },
                { icon: CheckCircle2, color: "text-green-400", bg: "bg-green-500/10 border-green-500/20", label: "Core Test Suite", desc: "Full pytest run: 200+ test files, all divisions. Buddy, Crypto, Sales, Finance, Legal + more." },
                { icon: BarChart2, color: "text-rose-400", bg: "bg-rose-500/10 border-rose-500/20", label: "HTML Report", desc: "Downloadable live dashboard: division bar charts, era scores, AI provider tags, health badge." },
              ].map(m => {
                const Icon = m.icon;
                return (
                  <Card key={m.label} className={cn("buddy-card rounded-2xl border p-4", m.bg)} data-testid={`module-${m.label}`}>
                    <Icon className={cn("h-5 w-5 mb-2", m.color)} />
                    <p className="font-semibold text-sm">{m.label}</p>
                    <p className="text-xs text-muted-foreground mt-1 leading-relaxed">{m.desc}</p>
                  </Card>
                );
              })}
            </div>

            {/* ── LAST RUN RESULTS ── */}
            {lastRun.isLoading ? (
              <Skeleton className="h-48 rounded-2xl" />
            ) : (lastRun.data as any)?.run ? (() => {
              const lr = lastRun.data as any;
              const run = lr.run;
              const jobs: any[] = lr.jobs ?? [];
              const artifacts: any[] = lr.artifacts ?? [];
              const allSuccess = jobs.length > 0 && jobs.every((j: any) => j.conclusion === "success");
              const failCount = jobs.filter((j: any) => j.conclusion === "failure").length;
              const healthPct = allSuccess ? 100 : Math.round(((jobs.length - failCount) / Math.max(jobs.length, 1)) * 100);
              const healthColor = healthPct >= 80 ? "text-green-400" : healthPct >= 50 ? "text-amber-400" : "text-red-400";
              const healthBg = healthPct >= 80 ? "border-green-500/30 bg-green-500/5" : healthPct >= 50 ? "border-amber-500/30 bg-amber-500/5" : "border-red-500/30 bg-red-500/5";
              const JOB_META: Record<string, { color: string; icon: any }> = {
                "Fleet Scan": { color: "text-blue-400", icon: Bot },
                "Buddy Bot": { color: "text-violet-400", icon: BrainCircuit },
                "Global AI": { color: "text-cyan-400", icon: Globe },
                "Era Testing": { color: "text-amber-400", icon: Zap },
                "Core Test": { color: "text-green-400", icon: CheckCircle2 },
                "Live Dashboard": { color: "text-rose-400", icon: BarChart2 },
              };
              const getJobMeta = (name: string) => {
                const key = Object.keys(JOB_META).find(k => name.includes(k));
                return key ? JOB_META[key] : { color: "text-muted-foreground", icon: Activity };
              };
              return (
                <Card className={cn("buddy-card rounded-2xl border p-5 space-y-4", healthBg)} data-testid="last-run-results">
                  <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-3">
                    <div>
                      <div className="flex items-center gap-2 mb-1">
                        <TrendingUp className="h-4 w-4 text-primary" />
                        <span className="font-bold text-sm">Last Dashboard Run Results</span>
                        <Badge className={cn("text-[10px] rounded-md capitalize", run.conclusion === "success" ? "bg-green-500/20 text-green-300 border-green-500/30" : "bg-red-500/20 text-red-300 border-red-500/30")}>
                          {run.conclusion ?? "unknown"}
                        </Badge>
                      </div>
                      <div className="flex items-center gap-2 text-xs text-muted-foreground">
                        <Clock className="h-3 w-3" />
                        {run.created_at ? new Date(run.created_at).toLocaleString() : ""}
                        <span className="text-border">·</span>
                        <span>Run #{String(run.id).slice(-6)}</span>
                        <span className="text-border">·</span>
                        <span>{jobs.length}/6 jobs</span>
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      <div className="text-center">
                        <p className={cn("text-3xl font-bold", healthColor)}>{healthPct}%</p>
                        <p className="text-[10px] text-muted-foreground">Pipeline Health</p>
                      </div>
                      <a href={run.html_url} target="_blank" rel="noreferrer">
                        <Button variant="outline" size="sm" className="rounded-xl text-xs" data-testid="view-run-btn">
                          <ExternalLink className="h-3.5 w-3.5 mr-1.5" />View Run
                        </Button>
                      </a>
                    </div>
                  </div>

                  {/* Job status grid */}
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                    {jobs.map((job: any) => {
                      const meta = getJobMeta(job.name);
                      const Icon = meta.icon;
                      const ok = job.conclusion === "success";
                      const dur = (job.started_at && job.completed_at)
                        ? Math.round((new Date(job.completed_at).getTime() - new Date(job.started_at).getTime()) / 1000)
                        : null;
                      return (
                        <div key={job.id} className={cn("flex items-center gap-2 p-3 rounded-xl border text-sm", ok ? "bg-muted/20 border-border/40" : "bg-red-500/5 border-red-500/20")} data-testid={`job-result-${job.id}`}>
                          <Icon className={cn("h-4 w-4 flex-shrink-0", meta.color)} />
                          <div className="min-w-0 flex-1">
                            <p className="font-medium text-xs truncate">{job.name.replace(/ - .+$/, "")}</p>
                            <p className="text-[10px] text-muted-foreground">{ok ? `✓ ${dur ? dur + "s" : "passed"}` : "✗ failed"}</p>
                          </div>
                          <span className={cn("h-2 w-2 rounded-full flex-shrink-0", ok ? "bg-green-400" : "bg-red-400")} />
                        </div>
                      );
                    })}
                  </div>

                  {/* Artifacts */}
                  {artifacts.length > 0 && (
                    <div>
                      <p className="text-xs text-muted-foreground mb-2 font-medium">📦 {artifacts.length} Artifacts Produced</p>
                      <div className="flex flex-wrap gap-2">
                        {artifacts.map((a: any) => (
                          <a key={a.id} href={run.html_url} target="_blank" rel="noreferrer" className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg border border-border/50 bg-muted/30 text-xs hover:bg-muted/50 transition-colors" data-testid={`artifact-${a.id}`}>
                            <Download className="h-3 w-3 text-muted-foreground" />
                            {a.name}
                            <span className="text-muted-foreground/60">({Math.round(a.size_in_bytes / 1024)}KB)</span>
                          </a>
                        ))}
                      </div>
                    </div>
                  )}
                </Card>
              );
            })() : null}

            {/* Workflow run history */}
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
                <div className="space-y-2">{Array.from({length:4}).map((_,i)=><Skeleton key={i} className="h-10 rounded-xl"/>)}</div>
              ) : workflows.isError || runs.length === 0 ? (
                <div className="p-6 text-center space-y-3">
                  <p className="text-sm text-muted-foreground">No workflow run data available yet</p>
                  <p className="text-xs text-muted-foreground">Click "Run Now" to trigger the live dashboard, then refresh after ~2 minutes</p>
                  <a href={ACTIONS_URL} target="_blank" rel="noreferrer">
                    <Button variant="outline" size="sm" className="rounded-xl" data-testid="open-actions-btn"><ExternalLink className="h-3.5 w-3.5 mr-1.5" />Open GitHub Actions</Button>
                  </a>
                </div>
              ) : (
                <div className="space-y-2">
                  {runs.slice(0,12).map((run: any) => {
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
                          {run.html_url && (
                            <a href={run.html_url} target="_blank" rel="noreferrer" className="text-muted-foreground hover:text-primary"><ExternalLink className="h-3.5 w-3.5" /></a>
                          )}
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </Card>

            {/* All workflows */}
            {wfList.length > 0 && (
              <Card className="buddy-card rounded-2xl border-border/60 p-5">
                <div className="flex items-center gap-2 mb-4">
                  <Zap className="h-4 w-4 text-amber-400" />
                  <span className="font-semibold text-sm">All Workflows ({wfList.length})</span>
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
                        {wf.html_url && (
                          <a href={wf.html_url} target="_blank" rel="noreferrer" className="text-muted-foreground hover:text-primary"><ExternalLink className="h-3 w-3" /></a>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </Card>
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
                        {((classify.data as any)?.bots ?? []).slice(0, 200).map((bot: any) => (
                          <tr key={bot.id} className="border-b border-border/30 hover:bg-muted/20 transition-colors" data-testid={`classify-row-${bot.id}`}>
                            <td className="px-4 py-2 font-medium truncate max-w-[200px]">{bot.displayName}</td>
                            <td className="px-4 py-2 text-muted-foreground text-xs">{bot.division}</td>
                            <td className="px-4 py-2">
                              <Badge variant="outline" className={cn("text-xs rounded-md", LANG_COLORS[bot.language])}>bots/{bot.language}/</Badge>
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
