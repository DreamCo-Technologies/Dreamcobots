import { useQuery } from "@tanstack/react-query";
import { CheckCircle2, Circle, Loader2, AlertCircle, Activity, Brain, Zap, Wrench } from "lucide-react";

type BuildProgress = {
  overallPercent: number;
  sections: { name: string; done: number; total: number }[];
  detail: {
    pagesBuilt: number;
    pagesPlanned: number;
    contractPushed: number;
    contractTotal: number;
    totalBots: number;
    botsWithManifest: number;
    openPRs: number;
    prsProcessed: number;
    prsMerged: number;
    prsArchived: number;
    integrations: { github: boolean; stripe: boolean; openai: boolean; database: boolean };
    probeStatus: string;
  };
};

type RunsStats = { total: number; last24h: number; topBots: { botSlug: string; runs: number; revenue: number }[] };
type EarningsResp = { grandTotal: number; topEarners: { botSlug: string; total: number }[]; recent: unknown[] };
type LearningsResp = { total: number; topLearners: { botSlug: string; count: number; avgReward: number }[]; recent: unknown[] };

type PhaseItem = { name: string; status: "built" | "partial" | "planned"; note?: string };
type Phase = { num: number; title: string; items: PhaseItem[] };

function buildPhases(d: BuildProgress["detail"]): Phase[] {
  const i = d.integrations;
  return [
    {
      num: 1,
      title: "Foundation Architecture",
      items: [
        { name: "pnpm monorepo workspace", status: "built" },
        { name: "API gateway (Express + OpenAPI codegen)", status: "built" },
        { name: "PostgreSQL + Drizzle ORM (10 ontology tables)", status: "built" },
        { name: "GitHub repo integration", status: i.github ? "built" : "planned" },
        { name: "Stripe billing integration", status: i.stripe ? "built" : "partial", note: i.stripe ? undefined : "STRIPE_SECRET_KEY missing — code is wired, just paste key" },
        { name: "OpenAI/Anthropic/Gemini routing", status: i.openai ? "partial" : "planned", note: "OpenAI proxy live; router TBD" },
      ],
    },
    {
      num: 2,
      title: "Command Center UI",
      items: [
        { name: "React + TypeScript + Tailwind + Vite", status: "built" },
        { name: "Dashboard summary widgets", status: "built" },
        { name: "Bot registry (171 bots, named capabilities)", status: "built" },
        { name: "Buddy AI chat console", status: "built" },
        { name: "Revenue panel", status: "built" },
        { name: "GitHub repos panel", status: "built" },
        { name: "Divisions panel (6 divisions)", status: "built" },
        { name: "Copilot PR review panel", status: "built" },
        { name: "System Status w/ Agent Runtime Matrix", status: "built" },
        { name: "Global command bar (Linear/Raycast)", status: "planned" },
        { name: "Live workflow graph (DAG visualization)", status: "planned" },
        { name: "Multi-agent network visualization", status: "planned" },
      ],
    },
    {
      num: 3,
      title: "Auth & Security",
      items: [
        { name: "DreamCo Auth (OIDC + PKCE)", status: "built" },
        { name: "Session storage in Postgres", status: "built" },
        { name: "Clerk (social login)", status: "planned" },
        { name: "GitHub OAuth (act-on-behalf)", status: "planned" },
        { name: "MCP server / bearer tokens", status: "planned" },
        { name: "RBAC + audit logs", status: "planned" },
      ],
    },
    {
      num: 4,
      title: "Bot Fleet & Contract",
      items: [
        { name: `${d.totalBots || 171} bots discovered`, status: "built" },
        { name: "Named capabilities per category (21 cats)", status: "built" },
        { name: `Bot contract pushed (${d.contractPushed}/${d.contractTotal} files)`, status: d.contractPushed === d.contractTotal ? "built" : "partial" },
        { name: `Bots with bot.manifest.json (${d.botsWithManifest}/${d.totalBots || 171})`, status: d.botsWithManifest > 0 ? "partial" : "planned" },
        { name: `Open PRs to review (${d.openPRs})`, status: d.openPRs === 0 ? "built" : "partial" },
        { name: "Bot Run buttons → records bot_runs in DB", status: "built" },
        { name: "Bot Learnings seeded on every run", status: "built" },
      ],
    },
    {
      num: 5,
      title: "AI Orchestration & Buddy Kernel",
      items: [
        { name: "Buddy: full fleet catalog in system prompt", status: "built" },
        { name: "Buddy: Planner (decomposes goals)", status: "partial", note: "via prompting" },
        { name: "Buddy: Memory (long-term recall)", status: "planned" },
        { name: "Buddy: Routing (multi-model)", status: "planned" },
        { name: "Buddy: Runtime (tool-calling bots)", status: "planned" },
        { name: "Buddy: Event Bus listener", status: "partial", note: "events table exists" },
        { name: "Buddy: Revenue Ops awareness", status: "planned" },
        { name: "Buddy: Autonomous workflow generation", status: "planned" },
      ],
    },
    {
      num: 6,
      title: "Monetization (bots making money)",
      items: [
        { name: "bot_earnings table", status: "built" },
        { name: "Stripe checkout (PRO $49, ENTERPRISE $299)", status: i.stripe ? "built" : "partial", note: i.stripe ? undefined : "code live, key needed" },
        { name: "Stripe webhook → bot_earnings auto-credit", status: i.stripe && d.integrations.stripe ? "built" : "partial" },
        { name: "Per-bot revenue attribution (metadata.bot_slug)", status: "built" },
        { name: "Revenue Operating System (leads → MRR)", status: "planned" },
        { name: "Outreach + conversion tracking", status: "planned" },
      ],
    },
    {
      num: 7,
      title: "Learning & Memory",
      items: [
        { name: "bot_learnings table (kind/prompt/outcome/reward)", status: "built" },
        { name: "Auto-seed learning row per run", status: "built" },
        { name: "Reward feedback loop", status: "planned" },
        { name: "Embedding column ready (pgvector)", status: "partial" },
        { name: "Vector retrieval API", status: "planned" },
      ],
    },
    {
      num: 8,
      title: "Repo Intelligence",
      items: [
        { name: "GitHub tree probe (bot detection)", status: "built" },
        { name: "PR sweep / contract enforcement (96 PRs reviewed)", status: "built" },
        { name: "Architecture drift detection", status: "planned" },
        { name: "Dead bot / duplicate detection", status: "planned" },
        { name: "Dependency graph", status: "planned" },
      ],
    },
    {
      num: 9,
      title: "Workflow Engine",
      items: [
        { name: "workflows + events tables", status: "built" },
        { name: "Visual DAG builder", status: "planned" },
        { name: "Event-driven triggers (NATS/Kafka)", status: "planned" },
        { name: "Auto repo auditor workflow", status: "planned" },
        { name: "AI market scanner workflow", status: "planned" },
      ],
    },
    {
      num: 10,
      title: "Observability",
      items: [
        { name: "Pino structured logging", status: "built" },
        { name: "Bot run telemetry (durations, tokens, cost)", status: "built" },
        { name: "OpenTelemetry / Prometheus / Grafana", status: "planned" },
        { name: "Per-agent health scores", status: "partial", note: "schema ready" },
      ],
    },
  ];
}

const STATUS_META = {
  built: { icon: CheckCircle2, color: "text-primary", bg: "bg-primary/10 border-primary/30", label: "BUILT" },
  partial: { icon: Loader2, color: "text-yellow-500", bg: "bg-yellow-500/10 border-yellow-500/30", label: "BUILDING" },
  planned: { icon: Circle, color: "text-muted-foreground", bg: "bg-muted/30 border-border/40", label: "PLANNED" },
} as const;

function computeRecommendations(
  detail: BuildProgress["detail"],
  runs: RunsStats | undefined,
  earnings: EarningsResp | undefined,
  learnings: LearningsResp | undefined,
): { action: string; why: string; priority: "high" | "med" | "low" }[] {
  const out: { action: string; why: string; priority: "high" | "med" | "low" }[] = [];
  if (!detail.integrations.stripe) {
    out.push({ action: "Add STRIPE_SECRET_KEY", why: "Unblocks live revenue, bot earnings auto-credit, MRR tracking", priority: "high" });
  }
  if (detail.openPRs > 0) {
    out.push({ action: `Sweep ${detail.openPRs} open PRs in Dreamcobots`, why: "Non-compliant PRs block bot fleet contract", priority: "high" });
  }
  if (detail.botsWithManifest < detail.totalBots) {
    out.push({
      action: `Generate bot.manifest.json for ${detail.totalBots - detail.botsWithManifest} bots`,
      why: "Manifest enables capability discovery + Buddy tool-calling",
      priority: "med",
    });
  }
  if ((runs?.total ?? 0) === 0) {
    out.push({ action: "Click Run on a bot to seed runtime telemetry", why: "Bot runs are recorded but DB is empty", priority: "low" });
  }
  if ((earnings?.grandTotal ?? 0) === 0 && detail.integrations.stripe) {
    out.push({ action: "Create first Stripe checkout to validate webhook → bot_earnings flow", why: "Earnings table ready but no revenue routed yet", priority: "med" });
  }
  if ((learnings?.total ?? 0) > 0 && (learnings?.topLearners?.[0]?.avgReward ?? 0) < 0.5) {
    out.push({ action: "Improve reward signal — current avg reward < 0.5", why: "Learning loop will plateau without stronger feedback", priority: "low" });
  }
  out.push({ action: "Build Live Workflow Graph (DAG visualizer)", why: "Required for enterprise-grade orchestration view", priority: "med" });
  out.push({ action: "Wire Buddy tool-calling → can run any bot from chat", why: "Unlocks autonomous operations queue", priority: "high" });
  return out;
}

export default function SystemPage() {
  const { data, isLoading, error } = useQuery<BuildProgress>({
    queryKey: ["build-progress"],
    queryFn: async () => (await fetch("/api/dashboard/build-progress")).json(),
    refetchInterval: 30_000,
  });
  const { data: runs } = useQuery<RunsStats>({
    queryKey: ["runs-stats"],
    queryFn: async () => (await fetch("/api/bots/runs/stats")).json(),
    refetchInterval: 15_000,
  });
  const { data: earnings } = useQuery<EarningsResp>({
    queryKey: ["earnings"],
    queryFn: async () => (await fetch("/api/bots/earnings")).json(),
    refetchInterval: 15_000,
  });
  const { data: learnings } = useQuery<LearningsResp>({
    queryKey: ["learnings"],
    queryFn: async () => (await fetch("/api/bots/learnings")).json(),
    refetchInterval: 15_000,
  });

  if (isLoading) return <div className="font-mono text-muted-foreground">Loading system status...</div>;
  if (error || !data)
    return (
      <div className="font-mono text-red-500 flex items-center gap-2">
        <AlertCircle className="h-4 w-4" /> Failed to load build progress
      </div>
    );

  const phases = buildPhases(data.detail);
  const all = phases.flatMap((p) => p.items);
  const builtCount = all.filter((i) => i.status === "built").length;
  const partialCount = all.filter((i) => i.status === "partial").length;
  const plannedCount = all.filter((i) => i.status === "planned").length;
  const totalItems = all.length;
  const realPercent = Math.round(((builtCount + partialCount * 0.5) / totalItems) * 100);
  const recs = computeRecommendations(data.detail, runs, earnings, learnings);

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-mono font-bold text-primary tracking-wider uppercase">SYSTEM_STATUS</h1>
        <p className="text-xs font-mono text-muted-foreground uppercase tracking-wider mt-1">
          Built vs Building // Live probe of GitHub + DB + Stripe + bot runtime
        </p>
      </div>

      {/* Top stat strip */}
      <div className="grid grid-cols-2 md:grid-cols-6 gap-3">
        <div className="p-3 border border-primary/30 bg-primary/5 rounded-sm">
          <div className="text-[10px] font-mono uppercase text-muted-foreground tracking-wider">Overall</div>
          <div className="font-mono text-2xl font-bold text-primary">{realPercent}%</div>
        </div>
        <div className="p-3 border border-primary/30 bg-primary/5 rounded-sm">
          <div className="text-[10px] font-mono uppercase text-muted-foreground tracking-wider">Built</div>
          <div className="font-mono text-2xl font-bold text-primary">{builtCount}</div>
        </div>
        <div className="p-3 border border-yellow-500/30 bg-yellow-500/5 rounded-sm">
          <div className="text-[10px] font-mono uppercase text-muted-foreground tracking-wider">Building</div>
          <div className="font-mono text-2xl font-bold text-yellow-500">{partialCount}</div>
        </div>
        <div className="p-3 border border-border/40 bg-muted/20 rounded-sm">
          <div className="text-[10px] font-mono uppercase text-muted-foreground tracking-wider">Planned</div>
          <div className="font-mono text-2xl font-bold text-muted-foreground">{plannedCount}</div>
        </div>
        <div className="p-3 border border-blue-500/30 bg-blue-500/5 rounded-sm">
          <div className="text-[10px] font-mono uppercase text-muted-foreground tracking-wider">Bot Runs 24h</div>
          <div className="font-mono text-2xl font-bold text-blue-400">{runs?.last24h ?? 0}</div>
        </div>
        <div className="p-3 border border-green-500/30 bg-green-500/5 rounded-sm">
          <div className="text-[10px] font-mono uppercase text-muted-foreground tracking-wider">Earnings</div>
          <div className="font-mono text-2xl font-bold text-green-400">${(earnings?.grandTotal ?? 0).toFixed(2)}</div>
        </div>
      </div>

      <div className="h-2 w-full bg-muted/30 rounded-sm overflow-hidden flex">
        <div className="bg-primary" style={{ width: `${(builtCount / totalItems) * 100}%` }} />
        <div className="bg-yellow-500" style={{ width: `${(partialCount / totalItems) * 100}%` }} />
      </div>

      {/* Recommended Actions */}
      <div className="border border-yellow-500/30 rounded-sm bg-yellow-500/5">
        <div className="px-4 py-3 border-b border-yellow-500/30 flex items-center gap-2">
          <Wrench className="h-4 w-4 text-yellow-500" />
          <div className="font-mono text-sm font-bold text-yellow-500 uppercase tracking-wider">Recommended Actions</div>
          <div className="ml-auto font-mono text-[10px] text-muted-foreground">{recs.length} suggestions</div>
        </div>
        <div className="divide-y divide-border/40">
          {recs.map((r, i) => (
            <div key={i} className="px-4 py-2.5 flex items-start gap-3">
              <div
                className={`font-mono text-[9px] uppercase tracking-wider px-1.5 py-0.5 rounded border mt-0.5 ${
                  r.priority === "high"
                    ? "bg-red-500/10 border-red-500/30 text-red-400"
                    : r.priority === "med"
                    ? "bg-yellow-500/10 border-yellow-500/30 text-yellow-400"
                    : "bg-muted/30 border-border/40 text-muted-foreground"
                }`}
              >
                {r.priority}
              </div>
              <div className="flex-1">
                <div className="font-mono text-sm text-foreground">{r.action}</div>
                <div className="font-mono text-[10px] text-muted-foreground mt-0.5">{r.why}</div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Agent Runtime Matrix */}
      <div className="border border-border/40 rounded-sm bg-card/50">
        <div className="px-4 py-3 border-b border-border/40 flex items-center gap-2">
          <Activity className="h-4 w-4 text-primary" />
          <div className="font-mono text-sm font-bold text-foreground uppercase tracking-wider">Agent Runtime Matrix</div>
          <div className="ml-auto font-mono text-[10px] text-muted-foreground">top 10 by run count</div>
        </div>
        {(runs?.topBots?.length ?? 0) === 0 ? (
          <div className="px-4 py-4 font-mono text-xs text-muted-foreground">
            No runs yet. Click <span className="text-primary">Run</span> on any bot in the Bot Registry to populate.
          </div>
        ) : (
          <table className="w-full font-mono text-xs">
            <thead className="text-[10px] uppercase text-muted-foreground border-b border-border/40">
              <tr>
                <th className="text-left px-4 py-2">Bot</th>
                <th className="text-right px-4 py-2">Runs</th>
                <th className="text-right px-4 py-2">Revenue</th>
                <th className="text-right px-4 py-2">Learnings</th>
                <th className="text-right px-4 py-2">Avg Reward</th>
              </tr>
            </thead>
            <tbody>
              {(runs?.topBots ?? []).map((b) => {
                const learner = learnings?.topLearners.find((l) => l.botSlug === b.botSlug);
                const earner = earnings?.topEarners.find((e) => e.botSlug === b.botSlug);
                return (
                  <tr key={b.botSlug} className="border-b border-border/20 last:border-0">
                    <td className="px-4 py-2 text-foreground">{b.botSlug}</td>
                    <td className="px-4 py-2 text-right text-blue-400">{b.runs}</td>
                    <td className="px-4 py-2 text-right text-green-400">${(earner?.total ?? 0).toFixed(2)}</td>
                    <td className="px-4 py-2 text-right text-purple-400">{learner?.count ?? 0}</td>
                    <td className="px-4 py-2 text-right text-muted-foreground">{(learner?.avgReward ?? 0).toFixed(2)}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        )}
      </div>

      {/* Buddy Kernel Subsystems */}
      <div className="border border-border/40 rounded-sm bg-card/50">
        <div className="px-4 py-3 border-b border-border/40 flex items-center gap-2">
          <Brain className="h-4 w-4 text-primary" />
          <div className="font-mono text-sm font-bold text-foreground uppercase tracking-wider">Buddy Kernel</div>
        </div>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-2 p-4">
          {[
            { name: "Planner", status: "partial" as const },
            { name: "Memory", status: "planned" as const },
            { name: "Routing", status: "planned" as const },
            { name: "Runtime", status: "planned" as const },
            { name: "Knowledge", status: "built" as const },
            { name: "Event Bus", status: "partial" as const },
            { name: "Revenue Ops", status: "planned" as const },
            { name: "Auto Workflows", status: "planned" as const },
          ].map((s) => {
            const meta = STATUS_META[s.status];
            const Icon = meta.icon;
            return (
              <div key={s.name} className={`flex items-center gap-2 px-3 py-2 rounded border ${meta.bg}`}>
                <Icon className={`h-3 w-3 ${meta.color} ${s.status === "partial" ? "animate-spin" : ""}`} />
                <span className="font-mono text-xs text-foreground">{s.name}</span>
              </div>
            );
          })}
        </div>
      </div>

      {/* Phase Breakdown */}
      <div className="space-y-4">
        <div className="flex items-center gap-2">
          <Zap className="h-4 w-4 text-primary" />
          <div className="font-mono text-sm font-bold text-foreground uppercase tracking-wider">Phase Breakdown</div>
        </div>
        {phases.map((phase) => (
          <div key={phase.num} className="border border-border/40 rounded-sm bg-card/50">
            <div className="px-4 py-3 border-b border-border/40 flex items-center gap-3">
              <div className="font-mono text-xs text-muted-foreground">PHASE {phase.num}</div>
              <div className="font-mono text-sm font-bold text-foreground uppercase tracking-wider">{phase.title}</div>
              <div className="ml-auto font-mono text-[10px] text-muted-foreground">
                {phase.items.filter((i) => i.status === "built").length} / {phase.items.length}
              </div>
            </div>
            <div className="divide-y divide-border/40">
              {phase.items.map((item, idx) => {
                const meta = STATUS_META[item.status];
                const Icon = meta.icon;
                return (
                  <div key={idx} className="px-4 py-2.5 flex items-center gap-3">
                    <Icon className={`h-4 w-4 ${meta.color} ${item.status === "partial" ? "animate-spin" : ""}`} />
                    <div className="flex-1 font-mono text-sm">{item.name}</div>
                    {item.note && <div className="font-mono text-[10px] text-muted-foreground italic">{item.note}</div>}
                    <div className={`font-mono text-[9px] uppercase tracking-wider px-1.5 py-0.5 rounded border ${meta.bg} ${meta.color}`}>{meta.label}</div>
                  </div>
                );
              })}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
