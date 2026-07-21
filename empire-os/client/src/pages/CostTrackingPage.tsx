import Seo from "@/components/Seo";
import AppShell from "@/components/AppShell";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Progress } from "@/components/ui/progress";
import { useQuery } from "@tanstack/react-query";
import {
  AlertTriangle,
  DollarSign,
  BarChart3,
  TrendingDown,
  Zap,
} from "lucide-react";
import type { CostEvent } from "@shared/schema";

interface CostSummary {
  totalTokens: number;
  totalCost: number;
  eventCount: number;
}

const COST_BUDGET = 50;

export default function CostTrackingPage() {
  const costsQuery = useQuery<CostEvent[]>({
    queryKey: ["/api/costs"],
  });

  const summaryQuery = useQuery<CostSummary>({
    queryKey: ["/api/costs/summary"],
  });

  const costs = costsQuery.data ?? [];
  const summary = summaryQuery.data;
  const totalCostRaw = summary?.totalCost ?? 0;
  const totalCost = totalCostRaw / 10000;
  const budgetPercent = Math.min((totalCost / COST_BUDGET) * 100, 100);
  const isOverBudget = totalCost > COST_BUDGET;
  const avgCost = summary?.eventCount ? totalCost / summary.eventCount : 0;

  return (
    <AppShell>
      <Seo title="Cost Tracking | DreamCo Empire OS" description="Monitor API costs and usage" />
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold tracking-tight" data-testid="text-cost-tracking-title">Cost Tracking</h1>
          <p className="text-muted-foreground text-sm mt-1">Monitor API usage and keep costs near zero</p>
        </div>

        {summaryQuery.isLoading ? (
          <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
            {[1, 2, 3, 4].map(i => <Skeleton key={i} className="h-28" />)}
          </div>
        ) : (
          <>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              <Card data-testid="card-total-cost">
                <CardContent className="p-4">
                  <div className="flex items-center gap-2 mb-2">
                    <DollarSign className="h-4 w-4 text-primary" />
                    <p className="text-xs text-muted-foreground">Total Cost</p>
                  </div>
                  <p className="text-2xl font-bold">${totalCost.toFixed(2)}</p>
                  <p className="text-[10px] text-muted-foreground">Lifetime spend</p>
                </CardContent>
              </Card>
              <Card data-testid="card-event-count">
                <CardContent className="p-4">
                  <div className="flex items-center gap-2 mb-2">
                    <Zap className="h-4 w-4 text-primary" />
                    <p className="text-xs text-muted-foreground">API Calls</p>
                  </div>
                  <p className="text-2xl font-bold">{summary?.eventCount ?? 0}</p>
                  <p className="text-[10px] text-muted-foreground">Total events</p>
                </CardContent>
              </Card>
              <Card data-testid="card-avg-cost">
                <CardContent className="p-4">
                  <div className="flex items-center gap-2 mb-2">
                    <BarChart3 className="h-4 w-4 text-primary" />
                    <p className="text-xs text-muted-foreground">Avg Cost</p>
                  </div>
                  <p className="text-2xl font-bold">${avgCost.toFixed(4)}</p>
                  <p className="text-[10px] text-muted-foreground">Per event</p>
                </CardContent>
              </Card>
              <Card data-testid="card-savings">
                <CardContent className="p-4">
                  <div className="flex items-center gap-2 mb-2">
                    <TrendingDown className="h-4 w-4 text-[rgb(34_197_94)]" />
                    <p className="text-xs text-muted-foreground">Budget Remaining</p>
                  </div>
                  <p className="text-2xl font-bold">${Math.max(COST_BUDGET - totalCost, 0).toFixed(2)}</p>
                  <p className="text-[10px] text-muted-foreground">of ${COST_BUDGET} monthly</p>
                </CardContent>
              </Card>
            </div>

            <Card>
              <CardContent className="p-4">
                <div className="flex items-center justify-between mb-2">
                  <p className="text-sm font-medium">Budget Usage</p>
                  <p className="text-sm font-medium">{budgetPercent.toFixed(1)}%</p>
                </div>
                <Progress value={budgetPercent} className="h-3" />
                {isOverBudget && (
                  <div className="flex items-center gap-2 mt-2 text-[rgb(239_68_68)]">
                    <AlertTriangle className="h-4 w-4" />
                    <p className="text-sm font-medium">Budget exceeded! Review usage below.</p>
                  </div>
                )}
              </CardContent>
            </Card>

            <Card data-testid="card-total-tokens">
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-xs text-muted-foreground">Total Tokens Used</p>
                    <p className="text-2xl font-bold">{(summary?.totalTokens ?? 0).toLocaleString()}</p>
                  </div>
                  <Zap className="h-8 w-8 text-primary/20" />
                </div>
              </CardContent>
            </Card>
          </>
        )}

        <Card data-testid="card-recent-costs">
          <CardHeader className="pb-4">
            <CardTitle className="text-lg">Recent Cost Events</CardTitle>
          </CardHeader>
          <CardContent>
            {costsQuery.isLoading ? (
              <div className="space-y-2">
                {[1, 2, 3].map(i => <Skeleton key={i} className="h-12" />)}
              </div>
            ) : costs.length === 0 ? (
              <div className="text-center py-6">
                <DollarSign className="h-10 w-10 mx-auto text-muted-foreground mb-2" />
                <p className="text-muted-foreground text-sm">No cost events recorded. Your system is running cost-free!</p>
              </div>
            ) : (
              <div className="space-y-2">
                {costs.slice(0, 50).map((event) => (
                  <div key={event.id} className="flex items-center justify-between p-3 rounded-xl border border-border/40 hover-elevate" data-testid={`cost-event-${event.id}`}>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <span className="text-sm font-medium capitalize">{event.service}</span>
                        <Badge variant="outline" className="text-xs">{event.tokens} tokens</Badge>
                      </div>
                      <p className="text-xs text-muted-foreground mt-0.5">{event.endpoint}</p>
                    </div>
                    <div className="flex items-center gap-3 flex-shrink-0">
                      <span className="text-sm font-medium">${(event.cost / 10000).toFixed(4)}</span>
                      <span className="text-xs text-muted-foreground">
                        {event.createdAt ? new Date(event.createdAt).toLocaleDateString() : ""}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </AppShell>
  );
}
