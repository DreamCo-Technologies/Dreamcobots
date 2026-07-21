import { useState } from "react";
import { useQuery, useMutation } from "@tanstack/react-query";
import { Link } from "wouter";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  GitMerge, CheckCircle2, XCircle, Loader2, PlayCircle, ExternalLink, Terminal, Bot,
  Send, Zap, Building2, Network, Bot as BotIcon, BarChart3, BookOpen, Brain, GraduationCap,
  Cpu, Globe, Workflow, ShoppingBag, Bitcoin, CreditCard, Rocket, Code2, Banknote,
  Bug, DollarSign, Tag, Plug, Clock, Wallet, Shield, MessageCircle, ArrowRight, Key, Wrench
} from "lucide-react";

interface Run { id: number; repo: string; name: string; branch: string | null; status: string; conclusion: string | null; event: string; runNumber: number; actor: string | null; url: string; createdAt: string; updatedAt: string }
interface ActionsResp { totals: { totalRuns: number; success: number; failure: number; inProgress: number }; runs: Run[] }
interface BotItem { name: string; displayName?: string; status?: string; invocations?: number; tier?: string }
interface Summary { totalBots: number; activeBots: number; idleBots: number; totalRepos: number; dailyRevenue: number; monthlyRevenue: number; dailyTarget: number; monthlyTarget: number; totalSubscriptions: number; recentCommits: number }
interface Tier { name: string; priceMonthly: number; requestsPerMonth: number; concurrentBots: number; models: string[] }
interface VibeStats { librariesLearned: number; ideasGenerated: number; buildsCompleted: number; avgImpactScore: number; ecosystems: { ecosystem: string; n: number }[] }
interface CapsResp { totals: { total: number; live: number; needsKey: number; planned: number } }

async function api<T = unknown>(path: string, init?: RequestInit): Promise<T> {
  const r = await fetch(`/api${path}`, { headers: { "Content-Type": "application/json", ...(init?.headers || {}) }, ...init });
  if (!r.ok) throw new Error(`${r.status}: ${await r.text()}`);
  return r.json();
}

function statusBadge(r: Run) {
  if (r.status === "in_progress" || r.status === "queued")
    return <Badge variant="outline" className="font-mono text-[10px] gap-1"><Loader2 className="h-3 w-3 animate-spin" />{r.status}</Badge>;
  if (r.conclusion === "success") return <Badge className="font-mono text-[10px] gap-1 bg-emerald-500/15 text-emerald-400 border-emerald-500/30"><CheckCircle2 className="h-3 w-3" />success</Badge>;
  if (r.conclusion === "failure") return <Badge variant="destructive" className="font-mono text-[10px] gap-1"><XCircle className="h-3 w-3" />failure</Badge>;
  return <Badge variant="secondary" className="font-mono text-[10px]">{r.conclusion ?? r.status}</Badge>;
}

type TileStatus = "live" | "needs_key" | "planned";
function statusChip(s: TileStatus) {
  if (s === "live") return <Badge className="font-mono text-[9px] gap-1 bg-emerald-500/15 text-emerald-400 border-emerald-500/30"><CheckCircle2 className="h-2.5 w-2.5" />LIVE</Badge>;
  if (s === "needs_key") return <Badge variant="outline" className="font-mono text-[9px] gap-1 text-amber-400 border-amber-500/30"><Key className="h-2.5 w-2.5" />KEY</Badge>;
  return <Badge variant="outline" className="font-mono text-[9px] gap-1 text-muted-foreground"><Wrench className="h-2.5 w-2.5" />WIP</Badge>;
}

interface Tile {
  id: string; title: string; icon: React.ReactNode; status: TileStatus;
  blurb: string; metric?: string; href?: string; note?: string;
}

export default function ActionsPage() {
  // Live data
  const summary = useQuery<Summary>({ queryKey: ["sum"], queryFn: () => api("/dashboard/summary"), refetchInterval: 15000 });
  const tiers = useQuery<Tier[]>({ queryKey: ["tiers"], queryFn: () => api("/dashboard/tiers") });
  const vibeStats = useQuery<VibeStats>({ queryKey: ["vstats"], queryFn: () => api("/vibe/stats"), refetchInterval: 10000 });
  const caps = useQuery<CapsResp>({ queryKey: ["caps"], queryFn: () => api("/buddy/capabilities") });
  const actions = useQuery<ActionsResp>({ queryKey: ["gha"], queryFn: () => api("/github/actions"), refetchInterval: 15000 });
  const bots = useQuery<BotItem[]>({ queryKey: ["bots"], queryFn: () => api("/bots"), staleTime: 60000 });

  // Buddy quick chat
  const [buddyMsg, setBuddyMsg] = useState("");
  const [buddyReply, setBuddyReply] = useState<string | null>(null);
  const buddyChat = useMutation({
    mutationFn: (m: string) => api<{ message: string }>("/buddy/chat", { method: "POST", body: JSON.stringify({ message: m, sessionId: "actions-hub" }) }),
    onSuccess: (d) => setBuddyReply(d.message),
  });

  // Bot trigger
  const [botName, setBotName] = useState("");
  const [botResult, setBotResult] = useState<string | null>(null);
  const botRun = useMutation({
    mutationFn: (n: string) => api<{ name: string; status: string; invocations: number }>(`/bots/${encodeURIComponent(n)}/run`, { method: "POST", body: JSON.stringify({ trigger: "actions-hub" }) }),
    onSuccess: (d) => setBotResult(`✓ ${d.name} → ${d.status} (invocations: ${d.invocations})`),
    onError: (e) => setBotResult(`✗ ${String(e)}`),
  });

  // Quick-test shortcuts derived from the real indexed fleet (no hardcoded names).
  const fav = (bots.data ?? []).slice(0, 6).map(b => b.name);

  const TILES: Tile[] = [
    { id: "chat", title: "Chat", icon: <MessageCircle className="h-5 w-5" />, status: "live", blurb: "Buddy multi-turn chat (gpt-5-mini).", href: "/buddy", metric: "active" },
    { id: "empire", title: "Empire HQ", icon: <Building2 className="h-5 w-5" />, status: "live", blurb: "Executive dashboard — KPIs & targets.", href: "/dashboard", metric: summary.data ? `$${summary.data.dailyRevenue.toFixed(0)} today / $${summary.data.dailyTarget} tgt` : "—" },
    { id: "divisions", title: "Divisions", icon: <Network className="h-5 w-5" />, status: "live", blurb: "Bot groupings by business division.", href: "/divisions", metric: summary.data ? `${summary.data.totalBots} bots` : "—" },
    { id: "fleet", title: "Bot Fleet", icon: <BotIcon className="h-5 w-5" />, status: "live", blurb: "Full indexed fleet, Run buttons live.", href: "/bots", metric: summary.data ? `${summary.data.activeBots} active / ${summary.data.totalBots}` : "—" },
    { id: "deals", title: "Deal Analyzer", icon: <BarChart3 className="h-5 w-5" />, status: "planned", blurb: "Real estate + business deal scoring.", href: "/deals", note: "Wire to real_estate_bot — ~4hr" },
    { id: "formulas", title: "Formula Vault", icon: <BookOpen className="h-5 w-5" />, status: "live", blurb: "Library mastery + revolutionary uses + math basis.", href: "/formulas", metric: vibeStats.data ? `${vibeStats.data.librariesLearned} libs / ${vibeStats.data.ideasGenerated} ideas` : "—" },
    { id: "learning", title: "Learning Matrix", icon: <GraduationCap className="h-5 w-5" />, status: "live", blurb: "Lesson-mode kid games (parent input).", href: "/learning-matrix", metric: "mode=lesson on Vibe Engine" },
    { id: "ai-leaders", title: "AI Leaders", icon: <Brain className="h-5 w-5" />, status: "planned", blurb: "Top AI models by benchmark.", href: "/ai-leaders", note: "Live LMArena scrape — ~3hr" },
    { id: "models-hub", title: "AI Models Hub", icon: <Cpu className="h-5 w-5" />, status: "live", blurb: "Buddy capability matrix + Image Studio.", href: "/capabilities", metric: caps.data ? `${caps.data.totals.live}/${caps.data.totals.total} live` : "—" },
    { id: "ecosystem", title: "AI Ecosystem", icon: <Globe className="h-5 w-5" />, status: "live", blurb: "Global library reach (40+ langs, CN/JP/RU/KR/IN).", href: "/ecosystem", metric: vibeStats.data ? `${vibeStats.data.ecosystems.length} ecosystems` : "—" },
    { id: "orchestration", title: "Orchestration", icon: <Workflow className="h-5 w-5" />, status: "live", blurb: "GitHub Actions workflow runs across all repos.", href: "/orchestration", metric: actions.data ? `${actions.data.totals.totalRuns} runs · ${actions.data.totals.success} ok` : "—" },
    { id: "marketplace", title: "Marketplace", icon: <ShoppingBag className="h-5 w-5" />, status: "planned", blurb: "Paid bot listings + buyer flow.", href: "/marketplace", note: "Stripe Connect + listing schema — ~8hr" },
    { id: "crypto", title: "Crypto", icon: <Bitcoin className="h-5 w-5" />, status: "needs_key", blurb: "Wallet balances + price feeds.", href: "/crypto", note: "Needs COINBASE_API_KEY or ALCHEMY_API_KEY" },
    { id: "payments", title: "Payments", icon: <CreditCard className="h-5 w-5" />, status: "live", blurb: "Stripe revenue + webhook handler.", href: "/revenue", metric: summary.data ? `$${summary.data.monthlyRevenue.toFixed(0)} MTD` : "—" },
    { id: "biz", title: "Biz Launch", icon: <Rocket className="h-5 w-5" />, status: "planned", blurb: "Spin up a new bot-driven business in N steps.", href: "/business", note: "Wizard + bot bundling — ~6hr" },
    { id: "code-lab", title: "Code Lab", icon: <Code2 className="h-5 w-5" />, status: "live", blurb: "Vibe Engine: code/game/sim/lesson/library.", href: "/vibe", metric: vibeStats.data ? `${vibeStats.data.buildsCompleted} builds` : "—" },
    { id: "loans", title: "Loans & Deals", icon: <Banknote className="h-5 w-5" />, status: "planned", blurb: "Aggregate SBA / business loan feed.", href: "/loans", note: "External API + scraper — ~6hr" },
    { id: "debug", title: "Debug Intel", icon: <Bug className="h-5 w-5" />, status: "live", blurb: "System health, build progress, env diagnostics.", href: "/system", metric: actions.data ? `${actions.data.totals.failure} failed runs` : "—" },
    { id: "revenue", title: "Revenue", icon: <DollarSign className="h-5 w-5" />, status: "live", blurb: "Real Stripe revenue, attribution by bot.", href: "/revenue", metric: summary.data ? `$${summary.data.dailyRevenue.toFixed(0)} / day` : "—" },
    { id: "pricing", title: "Pricing", icon: <Tag className="h-5 w-5" />, status: "live", blurb: "Tier matrix.", metric: tiers.data ? `${tiers.data.length} tiers · $${tiers.data[1]?.priceMonthly ?? 49}/mo PRO` : "—" },
    { id: "connections", title: "Connections", icon: <Plug className="h-5 w-5" />, status: "live", blurb: "All integrations / capabilities matrix.", href: "/capabilities", metric: caps.data ? `${caps.data.totals.needsKey} pending keys` : "—" },
    { id: "time", title: "Time Capsule", icon: <Clock className="h-5 w-5" />, status: "planned", blurb: "Daily snapshots of metrics for investor decks.", href: "/time-capsule", note: "Cron + JSON snapshot table — ~3hr" },
    { id: "costs", title: "Cost Tracking", icon: <Wallet className="h-5 w-5" />, status: "live", blurb: "Revenue vs target, daily & monthly progress.", href: "/costs", metric: vibeStats.data ? `${vibeStats.data.buildsCompleted} builds tracked` : "—" },
    { id: "autonomy", title: "Autonomy", icon: <Shield className="h-5 w-5" />, status: "planned", blurb: "Toggle Buddy autonomous action level (read / suggest / act).", href: "/autonomy", note: "Settings row + middleware gate — ~2hr" },
  ];

  return (
    <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
      {/* Header */}
      <div className="flex flex-col gap-2">
        <h1 className="text-3xl font-mono font-bold tracking-tight text-foreground uppercase flex items-center gap-3">
          <PlayCircle className="h-8 w-8 text-primary" />
          Command_Hub
        </h1>
        <p className="text-muted-foreground font-mono text-sm uppercase tracking-wider">
          Full replica · {TILES.filter(t => t.status === "live").length} LIVE · {TILES.filter(t => t.status === "needs_key").length} NEEDS_KEY · {TILES.filter(t => t.status === "planned").length} PLANNED · auto-refresh 15s
        </p>
      </div>

      {/* 23-tile command grid */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-6 gap-3">
        {TILES.map(t => {
          const inner = (
            <Card className="p-3 border-border/40 bg-card/50 backdrop-blur hover:border-primary/40 hover:bg-card/70 transition cursor-pointer h-full flex flex-col">
              <div className="flex items-start justify-between mb-2">
                <div className="text-primary">{t.icon}</div>
                {statusChip(t.status)}
              </div>
              <div className="font-mono text-sm text-foreground uppercase tracking-wide">{t.title}</div>
              <div className="font-mono text-[10px] text-muted-foreground mt-1 flex-1">{t.blurb}</div>
              {t.metric ? <div className="font-mono text-[10px] text-primary mt-2 truncate">{t.metric}</div> : null}
              {t.note ? <div className="font-mono text-[9px] text-amber-400/70 mt-1 italic">{t.note}</div> : null}
              {t.href ? <div className="font-mono text-[9px] text-primary/70 mt-1 flex items-center gap-1">OPEN <ArrowRight className="h-2.5 w-2.5" /></div> : null}
            </Card>
          );
          return t.href ? (
            <Link key={t.id} href={t.href} data-testid={`tile-${t.id}`}>{inner}</Link>
          ) : (
            <div key={t.id} data-testid={`tile-${t.id}`}>{inner}</div>
          );
        })}
      </div>

      {/* KPIs */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Stat label="GH_RUNS" value={actions.data?.totals.totalRuns ?? 0} loading={actions.isLoading} icon={<PlayCircle className="h-5 w-5 text-primary" />} />
        <Stat label="SUCCEEDED" value={actions.data?.totals.success ?? 0} loading={actions.isLoading} tone="emerald" icon={<CheckCircle2 className="h-5 w-5 text-emerald-400" />} />
        <Stat label="FAILED" value={actions.data?.totals.failure ?? 0} loading={actions.isLoading} tone="destructive" icon={<XCircle className="h-5 w-5 text-destructive" />} />
        <Stat label="ACTIVE_BOTS" value={summary.data?.activeBots ?? 0} loading={summary.isLoading} tone="primary" icon={<BotIcon className="h-5 w-5 text-primary" />} />
      </div>

      {/* Buddy + Bot live console */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <Card className="p-4 space-y-3 border-border/40 bg-card/50 backdrop-blur">
          <h2 className="font-mono text-sm text-primary uppercase tracking-wider flex items-center gap-2"><Terminal className="h-4 w-4" /> // buddy quick-test</h2>
          <form onSubmit={(e) => { e.preventDefault(); if (buddyMsg.trim()) buddyChat.mutate(buddyMsg.trim()); }} className="flex gap-2">
            <Input value={buddyMsg} onChange={(e) => setBuddyMsg(e.target.value)} placeholder="e.g. status of revenue today" className="font-mono text-sm" data-testid="input-buddy-quick" />
            <Button type="submit" disabled={!buddyMsg.trim() || buddyChat.isPending} className="font-mono text-xs">
              {buddyChat.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
            </Button>
          </form>
          {buddyChat.error ? <div className="font-mono text-xs text-destructive">{String(buddyChat.error as Error)}</div> : null}
          {buddyReply ? <div className="font-mono text-xs bg-background/80 border border-border/40 rounded p-3 whitespace-pre-wrap max-h-64 overflow-y-auto">{buddyReply}</div> : null}
        </Card>

        <Card className="p-4 space-y-3 border-border/40 bg-card/50 backdrop-blur">
          <h2 className="font-mono text-sm text-primary uppercase tracking-wider flex items-center gap-2"><Bot className="h-4 w-4" /> // bot quick-test ({bots.data?.length ?? 0})</h2>
          <div className="flex flex-wrap gap-1.5">
            {fav.map(b => (
              <Button key={b} size="sm" variant="outline" onClick={() => { setBotName(b); botRun.mutate(b); }} disabled={botRun.isPending} className="font-mono text-[10px] h-7" data-testid={`bot-quick-${b}`}>
                <Zap className="h-3 w-3 mr-1" />{b}
              </Button>
            ))}
          </div>
          <form onSubmit={(e) => { e.preventDefault(); if (botName.trim()) botRun.mutate(botName.trim()); }} className="flex gap-2">
            <Input value={botName} onChange={(e) => setBotName(e.target.value)} placeholder="bot_name (e.g. god_bot)" className="font-mono text-sm" list="bot-suggestions" data-testid="input-bot-name" />
            <datalist id="bot-suggestions">{(bots.data ?? []).slice(0, 50).map(b => <option key={b.name} value={b.name} />)}</datalist>
            <Button type="submit" disabled={!botName.trim() || botRun.isPending} className="font-mono text-xs">
              {botRun.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : "RUN"}
            </Button>
          </form>
          {botResult ? <div className={`font-mono text-xs rounded p-2 border ${botResult.startsWith("✓") ? "bg-emerald-500/10 border-emerald-500/30 text-emerald-400" : "bg-destructive/10 border-destructive/30 text-destructive"}`}>{botResult}</div> : null}
        </Card>
      </div>

      {/* Workflow runs */}
      <Card className="border-border/40 bg-card/50 backdrop-blur">
        <div className="p-4 border-b border-border/40">
          <h2 className="font-mono text-sm text-primary uppercase tracking-wider flex items-center gap-2"><GitMerge className="h-4 w-4" /> // workflow runs · 15s refresh</h2>
        </div>
        <div className="p-4">
          {actions.isLoading ? <div className="space-y-2">{[1,2,3,4,5].map(i => <Skeleton key={i} className="h-12 w-full" />)}</div>
          : (actions.data?.runs ?? []).length === 0 ? <div className="font-mono text-xs text-muted-foreground py-6 text-center">No workflow runs yet.</div>
          : <div className="divide-y divide-border/40">
              {actions.data!.runs.map(r => (
                <a key={r.id} href={r.url} target="_blank" rel="noreferrer" className="flex items-center gap-3 py-2.5 hover:bg-muted/30 px-2 -mx-2 rounded">
                  <GitMerge className="h-4 w-4 text-muted-foreground flex-shrink-0" />
                  <div className="min-w-0 flex-1">
                    <div className="font-mono text-sm text-foreground truncate">{r.name} <span className="text-muted-foreground">#{r.runNumber}</span></div>
                    <div className="font-mono text-[10px] text-muted-foreground truncate">{r.repo} · {r.branch ?? "—"} · {r.event} · {r.actor ?? "system"} · {new Date(r.updatedAt).toLocaleString()}</div>
                  </div>
                  {statusBadge(r)}
                  <ExternalLink className="h-3 w-3 text-muted-foreground" />
                </a>
              ))}
            </div>}
        </div>
      </Card>
    </div>
  );
}

function Stat({ label, value, loading, tone, icon }: { label: string; value: number; loading: boolean; tone?: "emerald" | "destructive" | "primary"; icon?: React.ReactNode }) {
  const color = tone === "emerald" ? "text-emerald-400" : tone === "destructive" ? "text-destructive" : "text-primary";
  return (
    <Card className="p-4 border-border/40 bg-card/50 backdrop-blur">
      <div className="flex items-center justify-between mb-2">
        <div className="font-mono text-[10px] uppercase text-muted-foreground tracking-wider">{label}</div>
        {icon}
      </div>
      {loading ? <Skeleton className="h-8 w-16" /> : <div className={`font-mono text-3xl ${color}`}>{value}</div>}
    </Card>
  );
}
