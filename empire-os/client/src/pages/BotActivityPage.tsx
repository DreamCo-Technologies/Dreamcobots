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
import { Github, RefreshCw, UploadCloud, Bot, BrainCircuit, Activity, CheckCircle2, AlertCircle, Loader2, FolderOpen, GitPullRequest, ExternalLink, FileCode, Coffee } from "lucide-react";

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
  const [activeTab, setActiveTab] = useState<"activity" | "github" | "classify">("activity");

  const activity = useQuery({ queryKey: ["/api/bot-activity"], refetchInterval: 15000 });
  const github = useQuery({ queryKey: ["/api/github/status"], retry: 1 });
  const classify = useQuery({ queryKey: ["/api/github/classify"] });

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

  const tabs = [
    { id: "activity", label: "Bot Activity", icon: Activity },
    { id: "github", label: "GitHub Sync", icon: Github },
    { id: "classify", label: "Bot Languages", icon: FolderOpen },
  ] as const;

  return (
    <AppShell selectedBotSlug={selectedBotSlug} onBotChange={setSelectedBotSlug}>
      <Seo title="Bot Activity & GitHub — DreamCo Empire OS" description="Monitor all bots and sync to GitHub" />

      <div className="buddy-appear space-y-6">
        <div className="flex flex-col md:flex-row md:items-end md:justify-between gap-4">
          <div>
            <h2 className="text-3xl md:text-4xl" data-testid="activity-title">Bot Activity & GitHub</h2>
            <p className="mt-1 text-muted-foreground">Real-time bot monitoring · DreamCo-Technologies/Dreamcobots</p>
          </div>
          {activeTab === "github" && (
            <Button onClick={() => pushAll.mutate()} disabled={pushAll.isPending} className="rounded-xl bg-gradient-to-r from-primary to-accent text-primary-foreground shadow-md" data-testid="push-all-btn">
              {pushAll.isPending ? <><Loader2 className="h-4 w-4 mr-2 animate-spin" />Pushing...</> : <><UploadCloud className="h-4 w-4 mr-2" />Push All Bots to GitHub</>}
            </Button>
          )}
        </div>

        {/* Tabs */}
        <div className="flex gap-2" data-testid="activity-tabs">
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

        {/* ── GITHUB TAB ── */}
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

                {/* Merge summary */}
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

                  {/* Push all bots */}
                  <div className="p-4 rounded-xl bg-muted/30 border border-border/50 space-y-2">
                    <p className="text-sm font-medium">Step 1 — Push All {activity.data?.totalBots ?? 1051} Bot Profiles</p>
                    <p className="text-xs text-muted-foreground">Pushes every bot as <code className="bg-muted px-1 rounded">bots/slug/bot_profile.json</code> + Python bots to <code className="bg-muted px-1 rounded">python_bots/</code> + Java bots to <code className="bg-muted px-1 rounded">java_bots/</code> + updates README</p>
                    <Button onClick={() => pushAll.mutate()} disabled={pushAll.isPending || pushSource.isPending} className="rounded-xl w-full" data-testid="push-all-btn-2">
                      {pushAll.isPending ? <><Loader2 className="h-4 w-4 mr-2 animate-spin" />Pushing bots... (this takes a few minutes)</> : <><UploadCloud className="h-4 w-4 mr-2" />Push All {activity.data?.totalBots ?? 1051} Bots</>}
                    </Button>
                    {pushAll.isSuccess && (
                      <div className="p-3 rounded-xl bg-green-500/10 border border-green-500/20 text-sm text-green-400">
                        ✅ {(pushAll.data as any)?.pushed} bots pushed · Python: {(pushAll.data as any)?.byLang?.python} · Java: {(pushAll.data as any)?.byLang?.java} · {(pushAll.data as any)?.errors?.length ?? 0} errors
                      </div>
                    )}
                  </div>

                  {/* Push source code */}
                  <div className="p-4 rounded-xl bg-muted/30 border border-border/50 space-y-2">
                    <p className="text-sm font-medium">Step 2 — Push Full Source Code</p>
                    <p className="text-xs text-muted-foreground">Pushes all 29 pages, server files, shared schema, and config to <code className="bg-muted px-1 rounded">empire-os/</code> folder on GitHub</p>
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

                {/* Pull Requests */}
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
                            <a href={pr.url} target="_blank" rel="noreferrer" className="text-primary hover:text-primary/80">
                              <ExternalLink className="h-3.5 w-3.5" />
                            </a>
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
