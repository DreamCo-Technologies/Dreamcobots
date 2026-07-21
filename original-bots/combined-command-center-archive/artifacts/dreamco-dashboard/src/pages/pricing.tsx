import { useQuery } from "@tanstack/react-query";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Tag, CheckCircle2, Cpu, Zap } from "lucide-react";

interface Tier { name: string; priceMonthly: number; requestsPerMonth: number; concurrentBots: number; models: string[] }

async function api<T = unknown>(path: string): Promise<T> {
  const r = await fetch(`/api${path}`, { headers: { "Content-Type": "application/json" } });
  if (!r.ok) throw new Error(`${r.status}: ${await r.text()}`);
  return r.json();
}

export default function PricingPage() {
  const tiers = useQuery<Tier[]>({ queryKey: ["tiers"], queryFn: () => api("/dashboard/tiers") });

  return (
    <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="flex flex-col gap-2">
        <h1 className="text-3xl font-mono font-bold tracking-tight text-foreground uppercase flex items-center gap-3">
          <Tag className="h-8 w-8 text-primary" />Pricing
        </h1>
        <p className="text-muted-foreground font-mono text-sm uppercase tracking-wider">Subscription tiers · live from API</p>
      </div>

      {tiers.isLoading ? (
        <div className="grid gap-4 md:grid-cols-3">{[0, 1, 2].map((i) => <Skeleton key={i} className="h-72" />)}</div>
      ) : tiers.isError ? (
        <Card className="p-6 border-destructive/40 font-mono text-sm text-destructive">Failed to load tiers.</Card>
      ) : (
        <div className="grid gap-4 md:grid-cols-3">
          {tiers.data!.map((t) => {
            const featured = t.name === "PRO";
            return (
              <Card key={t.name} className={`p-6 border-border/40 bg-card/50 backdrop-blur flex flex-col ${featured ? "ring-1 ring-primary/40" : ""}`}>
                {featured ? <Badge className="self-start mb-3 font-mono text-[9px] bg-primary/15 text-primary border-primary/30">POPULAR</Badge> : null}
                <div className="font-mono text-sm uppercase tracking-wider text-muted-foreground">{t.name}</div>
                <div className="mt-2 mb-4 flex items-baseline gap-1">
                  <span className="text-4xl font-mono font-bold text-foreground">${t.priceMonthly}</span>
                  <span className="font-mono text-xs text-muted-foreground">/mo</span>
                </div>
                <ul className="space-y-2 font-mono text-sm text-foreground/80 flex-1">
                  <li className="flex items-center gap-2"><CheckCircle2 className="h-4 w-4 text-emerald-400/70" />{t.requestsPerMonth.toLocaleString()} requests / mo</li>
                  <li className="flex items-center gap-2"><Cpu className="h-4 w-4 text-primary/70" />{t.concurrentBots} concurrent bots</li>
                  <li className="flex items-start gap-2"><Zap className="h-4 w-4 text-amber-400/70 mt-0.5" /><span>{t.models.join(", ")}</span></li>
                </ul>
              </Card>
            );
          })}
        </div>
      )}
      <p className="font-mono text-xs text-muted-foreground">Checkout wiring runs through the Stripe integration once <code className="text-amber-300/90">STRIPE_SECRET_KEY</code> is set.</p>
    </div>
  );
}
