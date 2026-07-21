import { useQuery } from "@tanstack/react-query";
import { Card } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Wallet, TrendingUp, TrendingDown, Target } from "lucide-react";

interface Summary { dailyRevenue: number; monthlyRevenue: number; dailyTarget: number; monthlyTarget: number; totalSubscriptions: number }

async function api<T = unknown>(path: string): Promise<T> {
  const r = await fetch(`/api${path}`, { headers: { "Content-Type": "application/json" } });
  if (!r.ok) throw new Error(`${r.status}: ${await r.text()}`);
  return r.json();
}

const money = (n: number) => `$${(n || 0).toLocaleString(undefined, { maximumFractionDigits: 0 })}`;

export default function CostsPage() {
  const summary = useQuery<Summary>({ queryKey: ["sum"], queryFn: () => api("/dashboard/summary"), refetchInterval: 15000 });
  const s = summary.data;

  const dailyPct = s && s.dailyTarget > 0 ? Math.min(100, (s.dailyRevenue / s.dailyTarget) * 100) : 0;
  const monthlyPct = s && s.monthlyTarget > 0 ? Math.min(100, (s.monthlyRevenue / s.monthlyTarget) * 100) : 0;

  return (
    <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="flex flex-col gap-2">
        <h1 className="text-3xl font-mono font-bold tracking-tight text-foreground uppercase flex items-center gap-3">
          <Wallet className="h-8 w-8 text-primary" />Cost_Tracking
        </h1>
        <p className="text-muted-foreground font-mono text-sm uppercase tracking-wider">Revenue vs target · live from Stripe-backed API</p>
      </div>

      {summary.isLoading ? (
        <div className="grid gap-4 md:grid-cols-2">{[0, 1].map((i) => <Skeleton key={i} className="h-40" />)}</div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2">
          <Card className="p-6 border-border/40 bg-card/50 backdrop-blur">
            <div className="flex items-center gap-2 font-mono text-xs text-muted-foreground uppercase"><TrendingUp className="h-4 w-4 text-emerald-400/70" />Daily Revenue</div>
            <div className="mt-2 flex items-baseline gap-2"><span className="text-4xl font-mono font-bold text-foreground">{money(s?.dailyRevenue ?? 0)}</span><span className="font-mono text-xs text-muted-foreground">/ {money(s?.dailyTarget ?? 0)} target</span></div>
            <div className="mt-3 h-2 rounded-full bg-muted overflow-hidden"><div className="h-full bg-emerald-400/70" style={{ width: `${dailyPct}%` }} /></div>
            <div className="mt-1 font-mono text-[10px] text-muted-foreground">{dailyPct.toFixed(1)}% of daily target</div>
          </Card>
          <Card className="p-6 border-border/40 bg-card/50 backdrop-blur">
            <div className="flex items-center gap-2 font-mono text-xs text-muted-foreground uppercase"><Target className="h-4 w-4 text-primary/70" />Monthly Revenue</div>
            <div className="mt-2 flex items-baseline gap-2"><span className="text-4xl font-mono font-bold text-foreground">{money(s?.monthlyRevenue ?? 0)}</span><span className="font-mono text-xs text-muted-foreground">/ {money(s?.monthlyTarget ?? 0)} target</span></div>
            <div className="mt-3 h-2 rounded-full bg-muted overflow-hidden"><div className="h-full bg-primary/70" style={{ width: `${monthlyPct}%` }} /></div>
            <div className="mt-1 font-mono text-[10px] text-muted-foreground">{monthlyPct.toFixed(1)}% of monthly target</div>
          </Card>
        </div>
      )}

      <Card className="p-4 border-border/40 bg-card/50 backdrop-blur flex items-center gap-3">
        <TrendingDown className="h-5 w-5 text-amber-400/70" />
        <p className="font-mono text-xs text-muted-foreground">
          Per-bot spend/cost breakdown lands once bots report token usage. Right now this view tracks the income side honestly — revenue and progress toward the {money(s?.dailyTarget ?? 500)}/day goal.
        </p>
      </Card>
    </div>
  );
}
