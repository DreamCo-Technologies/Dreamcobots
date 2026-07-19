import Seo from "@/components/Seo";
import AppShell from "@/components/AppShell";
import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { Progress } from "@/components/ui/progress";
import { useQuery } from "@tanstack/react-query";
import { queryClient } from "@/lib/queryClient";
import { useToast } from "@/hooks/use-toast";
import {
  AlertTriangle,
  DollarSign,
  BarChart3,
  TrendingDown,
  Zap,
  RefreshCw,
  Download,
  Trash2,
  Target,
} from "lucide-react";
import type { CostEvent } from "@shared/schema";

interface CostSummary {
  totalTokens: number;
  totalCost: number;
  eventCount: number;
}

const COST_BUDGET = 50;

function exportCsv(costs: CostEvent[]) {
  const header = "ID,Service,Endpoint,Tokens,Cost ($),Date";
  const rows = costs.map(e =>
    [e.id, e.service, e.endpoint, e.tokens, (e.cost / 10000).toFixed(4),
    e.createdAt ? new Date(e.createdAt).toLocaleDateString() : ""].join(",")
  );
  const csv = [header, ...rows].join("\n");
  const blob = new Blob([csv], { type: "text/csv" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `empire-costs-${new Date().toISOString().slice(0, 10)}.csv`;
  a.click();
  URL.revokeObjectURL(url);
}

export default function CostTrackingPage() {
  const { toast } = useToast();
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [budgetTarget, setBudgetTarget] = useState(COST_BUDGET);

  const costsQuery = useQuery<CostEvent[]>({ queryKey: ["/api/costs"] });
  const summaryQuery = useQuery<CostSummary>({ queryKey: ["/api/costs/summary"] });

  const costs = costsQuery.data ?? [];
  const summary = summaryQuery.data;
  const totalCostRaw = summary?.totalCost ?? 0;
  const totalCost = totalCostRaw / 10000;
  const budgetPercent = Math.min((totalCost / budgetTarget) * 100, 100);
  const isOverBudget = totalCost > budgetTarget;
  const avgCost = summary?.eventCount ? totalCost / summary.eventCount : 0;

  async function handleRefresh() {
    setIsRefreshing(true);
    await queryClient.invalidateQueries({ queryKey: ["/api/costs"] });
    await queryClient.invalidateQueries({ queryKey: ["/api/costs/summary"] });
    setIsRefreshing(false);
    toast({ title: "Refreshed", description: "Cost data is up to date." });
  }

  function handleExport() {
    if (costs.length === 0) {
      toast({ title: "Nothing to export", description: "No cost events recorded yet.", variant: "destructive" });
      return;
    }
    exportCsv(costs);
    toast({ title: "Exported!", description: `${costs.length} events saved as CSV.` });
  }

  function handleCopyReport() {
    const report = [
      `DreamCo Empire OS — Cost Report (${new Date().toLocaleDateString()})`,
      `Total Cost: $${totalCost.toFixed(4)}`,
      `Total Events: ${summary?.eventCount ?? 0}`,
      `Total Tokens: ${(summary?.totalTokens ?? 0).toLocaleString()}`,
      `Avg Cost / Event: $${avgCost.toFixed(6)}`,
      `Budget Used: ${budgetPercent.toFixed(1)}% of $${budgetTarget}`,
    ].join("\n");
    navigator.clipboard.writeText(report);
    toast({ title: "Report copied!", description: "Cost summary copied to clipboard." });
  }

  return (
    <AppShell>
      <Seo title="Cost Tracking | DreamCo Empire OS" description="Monitor API costs and usage" />
      <div className="space-y-6">

        {/* ── Header ── */}
        <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold tracking-tight" data-testid="text-cost-tracking-title">Cost Tracking</h1>
            <p className="text-muted-foreground text-sm mt-1">Monitor API usage and keep costs near zero</p>
          </div>
          <div className="flex flex-wrap gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={handleRefresh}
              disabled={isRefreshing}
              data-testid="button-refresh-costs"
            >
              <RefreshCw className={`h-4 w-4 mr-2 ${isRefreshing ? "animate-spin" : ""}`} />
              Refresh
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={handleExport}
              data-testid="button-export-csv"
            >
              <Download className="h-4 w-4 mr-2" />
              Export CSV
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={handleCopyReport}
              data-testid="button-copy-report"
            >
              <BarChart3 className="h-4 w-4 mr-2" />
              Copy Report
            </Button>
          </div>
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
                  <p className="text-2xl font-bold">${Math.max(budgetTarget - totalCost, 0).toFixed(2)}</p>
                  <p className="text-[10px] text-muted-foreground">of ${budgetTarget} monthly</p>
                </CardContent>
              </Card>
            </div>

            <Card>
              <CardContent className="p-4">
                <div className="flex items-center justify-between mb-2">
                  <p className="text-sm font-medium">Budget Usage</p>
                  <div className="flex items-center gap-3">
                    <p className="text-sm font-medium">{budgetPercent.toFixed(1)}%</p>
                    <div className="flex gap-1">
                      {[25, 50, 100, 200].map(v => (
                        <Button
                          key={v}
                          variant={budgetTarget === v ? "default" : "outline"}
                          size="sm"
                          className="h-6 text-[10px] px-2 rounded-md"
                          onClick={() => setBudgetTarget(v)}
                          data-testid={`button-budget-${v}`}
                        >
                          ${v}
                        </Button>
                      ))}
                    </div>
                  </div>
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
                  <div className="flex items-center gap-2">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => {
                        const toks = summary?.totalTokens ?? 0;
                        navigator.clipboard.writeText(toks.toLocaleString());
                        toast({ title: "Copied!", description: `${toks.toLocaleString()} tokens copied.` });
                      }}
                      data-testid="button-copy-tokens"
                    >
                      Copy
                    </Button>
                    <Zap className="h-8 w-8 text-primary/20" />
                  </div>
                </div>
              </CardContent>
            </Card>
          </>
        )}

        <Card data-testid="card-recent-costs">
          <CardHeader className="pb-4">
            <div className="flex items-center justify-between">
              <CardTitle className="text-lg">Recent Cost Events</CardTitle>
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleExport}
                  data-testid="button-export-events"
                >
                  <Download className="h-3.5 w-3.5 mr-1.5" />
                  Export
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => {
                    const top = costs.slice(0, 5).map(e =>
                      `${e.service} — ${e.endpoint} — $${(e.cost / 10000).toFixed(4)}`
                    ).join("\n");
                    navigator.clipboard.writeText(top);
                    toast({ title: "Copied top 5 events" });
                  }}
                  data-testid="button-copy-top5"
                >
                  Copy Top 5
                </Button>
              </div>
            </div>
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
                {costs.slice(0, 100).map((event) => (
                  <div key={event.id} className="flex items-center justify-between p-3 rounded-xl border border-border/40 hover:bg-muted/30 transition-colors" data-testid={`cost-event-${event.id}`}>
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
                      <Button
                        variant="ghost"
                        size="sm"
                        className="h-6 w-6 p-0 rounded-md"
                        onClick={() => {
                          navigator.clipboard.writeText(`${event.service} | ${event.endpoint} | ${event.tokens} tokens | $${(event.cost / 10000).toFixed(4)}`);
                          toast({ title: "Copied event details" });
                        }}
                        data-testid={`button-copy-event-${event.id}`}
                      >
                        <BarChart3 className="h-3 w-3" />
                      </Button>
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
