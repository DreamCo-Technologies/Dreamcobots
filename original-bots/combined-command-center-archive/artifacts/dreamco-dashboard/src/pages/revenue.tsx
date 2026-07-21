import {
  useGetStripeRevenue, getGetStripeRevenueQueryKey,
  useListSubscriptions, getListSubscriptionsQueryKey,
  useListTransactions, getListTransactionsQueryKey,
  useListTiers, getListTiersQueryKey,
} from "@workspace/api-client-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Skeleton } from "@/components/ui/skeleton";
import { Badge } from "@/components/ui/badge";
import { DollarSign, TrendingUp, CreditCard, Calendar, Receipt, AlertCircle } from "lucide-react";

const tierColors: Record<string, string> = {
  FREE: "bg-muted text-muted-foreground border-border",
  PRO: "bg-blue-500/10 text-blue-400 border-blue-500/30",
  ENTERPRISE: "bg-amber-500/10 text-amber-400 border-amber-500/30",
};

function progressColor(pct: number) {
  if (pct >= 80) return "bg-primary";
  if (pct >= 50) return "bg-amber-500";
  return "bg-destructive";
}

export default function Revenue() {
  const { data: revenue, isLoading: loadingRev } = useGetStripeRevenue({
    query: { queryKey: getGetStripeRevenueQueryKey() },
  });
  const { data: subs, isLoading: loadingSubs } = useListSubscriptions({
    query: { queryKey: getListSubscriptionsQueryKey() },
  });
  const { data: txs, isLoading: loadingTxs } = useListTransactions({
    query: { queryKey: getListTransactionsQueryKey() },
  });
  const { data: tiers } = useListTiers({
    query: { queryKey: getListTiersQueryKey() },
  });

  const dailyPct = revenue ? Math.min(100, (revenue.dailyRevenue / (revenue.dailyTarget || 500)) * 100) : 0;
  const weeklyPct = revenue ? Math.min(100, (revenue.weeklyRevenue / (revenue.weeklyTarget || 3500)) * 100) : 0;
  const monthlyPct = revenue ? Math.min(100, (revenue.monthlyRevenue / (revenue.monthlyTarget || 15000)) * 100) : 0;

  const mrr = (subs || []).reduce((s, x) => s + (x.amount || 0), 0);

  return (
    <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="flex flex-col gap-2">
        <h1 className="text-3xl font-mono font-bold tracking-tight text-foreground uppercase flex items-center gap-3">
          <DollarSign className="h-8 w-8 text-primary" />
          Financial_Ops
        </h1>
        <p className="text-muted-foreground font-mono text-sm uppercase tracking-wider">
          Real-Time Revenue Telemetry // {revenue?.connected ? "Stripe Connected" : "Demo Mode"}
        </p>
      </div>

      {!revenue?.connected && !loadingRev && (
        <div className="border border-amber-500/30 bg-amber-500/5 rounded-md p-4 flex items-start gap-3">
          <AlertCircle className="h-5 w-5 text-amber-400 shrink-0 mt-0.5" />
          <div className="font-mono text-sm">
            <div className="text-amber-400 uppercase tracking-wider">Stripe Not Connected</div>
            <div className="text-muted-foreground mt-1">Displaying demo data. Add STRIPE_SECRET_KEY to environment to see live metrics.</div>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard title="Total Revenue" value={revenue?.totalRevenue} loading={loadingRev} icon={<TrendingUp className="h-5 w-5 text-primary" />} />
        <MetricCard title="MRR (Active Subs)" value={mrr} loading={loadingSubs} icon={<CreditCard className="h-5 w-5 text-primary" />} />
        <MetricCard title="Active Subs" value={subs?.length} loading={loadingSubs} icon={<Calendar className="h-5 w-5 text-primary" />} isCount />
        <MetricCard title="Recent Transactions" value={txs?.length} loading={loadingTxs} icon={<Receipt className="h-5 w-5 text-primary" />} isCount />
      </div>

      <Card className="border-border/40 bg-card/50 backdrop-blur">
        <CardHeader>
          <CardTitle className="font-mono text-lg uppercase flex items-center gap-2">
            <TrendingUp className="h-5 w-5 text-primary" />
            Target_Tracking
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          {loadingRev ? (
            <Skeleton className="h-32 w-full" />
          ) : (
            <>
              <TargetBar label="Daily" value={revenue?.dailyRevenue || 0} target={revenue?.dailyTarget || 500} pct={dailyPct} />
              <TargetBar label="Weekly" value={revenue?.weeklyRevenue || 0} target={revenue?.weeklyTarget || 3500} pct={weeklyPct} />
              <TargetBar label="Monthly" value={revenue?.monthlyRevenue || 0} target={revenue?.monthlyTarget || 15000} pct={monthlyPct} />
            </>
          )}
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card className="border-border/40 bg-card/50 backdrop-blur">
          <CardHeader>
            <CardTitle className="font-mono text-lg uppercase flex items-center gap-2">
              <CreditCard className="h-5 w-5 text-primary" />
              Active_Subscriptions
            </CardTitle>
          </CardHeader>
          <CardContent>
            {loadingSubs ? (
              <div className="space-y-3">
                {[1, 2, 3].map(i => <Skeleton key={i} className="h-16 w-full" />)}
              </div>
            ) : (subs || []).length === 0 ? (
              <p className="text-muted-foreground font-mono text-sm text-center py-8">No active subscriptions</p>
            ) : (
              <div className="space-y-2">
                {subs!.map((s) => (
                  <div key={s.id} className="flex items-center justify-between p-3 rounded-md border border-border/40 bg-background/50">
                    <div className="min-w-0 flex-1">
                      <div className="text-sm font-mono text-foreground truncate">{s.customer}</div>
                      <div className="text-xs font-mono text-muted-foreground mt-0.5">
                        Renews {new Date(s.currentPeriodEnd).toLocaleDateString()}
                      </div>
                    </div>
                    <div className="flex items-center gap-3 shrink-0">
                      <Badge variant="outline" className={`font-mono text-xs uppercase ${tierColors[s.plan] ?? tierColors.FREE}`}>{s.plan}</Badge>
                      <span className="font-mono text-sm text-primary">${s.amount}</span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        <Card className="border-border/40 bg-card/50 backdrop-blur">
          <CardHeader>
            <CardTitle className="font-mono text-lg uppercase flex items-center gap-2">
              <Receipt className="h-5 w-5 text-primary" />
              Recent_Transactions
            </CardTitle>
          </CardHeader>
          <CardContent>
            {loadingTxs ? (
              <div className="space-y-3">
                {[1, 2, 3].map(i => <Skeleton key={i} className="h-16 w-full" />)}
              </div>
            ) : (txs || []).length === 0 ? (
              <p className="text-muted-foreground font-mono text-sm text-center py-8">No transactions</p>
            ) : (
              <div className="space-y-2">
                {txs!.slice(0, 8).map((t) => (
                  <div key={t.id} className="flex items-center justify-between p-3 rounded-md border border-border/40 bg-background/50">
                    <div className="min-w-0 flex-1">
                      <div className="text-sm font-mono text-foreground truncate">{t.description}</div>
                      <div className="text-xs font-mono text-muted-foreground mt-0.5">
                        {new Date(t.date).toLocaleString()}
                      </div>
                    </div>
                    <div className="flex items-center gap-2 shrink-0">
                      <div className={`h-2 w-2 rounded-full ${t.status === 'succeeded' ? 'bg-primary' : 'bg-amber-500'}`} />
                      <span className="font-mono text-sm text-primary">${t.amount}</span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      <Card className="border-border/40 bg-card/50 backdrop-blur">
        <CardHeader>
          <CardTitle className="font-mono text-lg uppercase">Pricing_Tiers</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {(tiers || []).map((tier) => (
              <div key={tier.name} className="rounded-md border border-border/40 bg-background/50 p-5 hover:border-primary/40 transition-colors">
                <div className="flex items-baseline justify-between">
                  <Badge variant="outline" className={`font-mono text-xs uppercase ${tierColors[tier.name] ?? tierColors.FREE}`}>{tier.name}</Badge>
                  <div className="font-mono">
                    <span className="text-2xl font-bold text-foreground">${tier.priceMonthly}</span>
                    <span className="text-xs text-muted-foreground">/mo</span>
                  </div>
                </div>
                <ul className="mt-4 space-y-2 font-mono text-xs text-muted-foreground">
                  <li>{tier.requestsPerMonth.toLocaleString()} requests/mo</li>
                  <li>{tier.concurrentBots} concurrent bots</li>
                  <li>Models: {tier.models.join(", ")}</li>
                </ul>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

function MetricCard({ title, value, loading, icon, isCount }: { title: string; value?: number; loading: boolean; icon: React.ReactNode; isCount?: boolean }) {
  return (
    <Card className="border-border/40 bg-card/50 backdrop-blur">
      <CardContent className="p-6">
        <div className="flex items-center justify-between">
          <div className="space-y-2">
            <p className="text-xs font-mono text-muted-foreground uppercase tracking-wider">{title}</p>
            {loading ? (
              <Skeleton className="h-8 w-24" />
            ) : (
              <h3 className="text-3xl font-mono font-bold text-foreground">
                {isCount ? (value ?? 0).toLocaleString() : `$${(value ?? 0).toLocaleString(undefined, { minimumFractionDigits: 0, maximumFractionDigits: 2 })}`}
              </h3>
            )}
          </div>
          <div className="h-10 w-10 rounded-full bg-primary/10 flex items-center justify-center">{icon}</div>
        </div>
      </CardContent>
    </Card>
  );
}

function TargetBar({ label, value, target, pct }: { label: string; value: number; target: number; pct: number }) {
  return (
    <div className="space-y-2">
      <div className="flex justify-between font-mono text-sm">
        <span className="text-muted-foreground uppercase tracking-wider">{label}</span>
        <span className="text-foreground">
          ${value.toLocaleString(undefined, { maximumFractionDigits: 2 })}
          <span className="text-muted-foreground"> / ${target.toLocaleString()}</span>
          <span className="ml-2 text-primary">{pct.toFixed(0)}%</span>
        </span>
      </div>
      <Progress value={pct} className="h-2 bg-muted/50" indicatorClassName={progressColor(pct)} />
    </div>
  );
}
