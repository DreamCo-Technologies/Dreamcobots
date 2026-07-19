import Seo from "@/components/Seo";
import AppShell from "@/components/AppShell";
import { useState, useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import { Link } from "wouter";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Skeleton } from "@/components/ui/skeleton";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { cn } from "@/lib/utils";
import type { BotProfile } from "@shared/schema";
import { DIVISION_API_REGISTRIES, getTotalApiCount, getApiCountForDivision, TIER_PRICING } from "@shared/api-registry";
import { useToast } from "@/hooks/use-toast";
import { queryClient } from "@/lib/queryClient";
import {
  Activity,
  ArrowRight,
  ArrowUpRight,
  BarChart3,
  Bot,
  Download,
  RefreshCw,
  Copy,
  Building2,
  CircleDollarSign,
  Clock,
  DollarSign,
  Globe,
  Layers,
  LineChart,
  Network,
  Plug,
  Server,
  Sparkles,
  Target,
  TrendingUp,
  Users,
  Zap,
} from "lucide-react";

function generateDivisionRevenue(division: string, botCount: number) {
  const seed = division.length * 137 + botCount * 31;
  return {
    monthlyRevenue: Math.round((5000 + (seed % 45000)) * botCount / 10),
    growth: +(8 + (seed % 32) + (seed % 10) / 10).toFixed(1),
    clients: 10 + (seed % 90),
    avgDealSize: 500 + (seed % 4500),
    conversionRate: +(2 + (seed % 15) + (seed % 10) / 10).toFixed(1),
    apiCallsToday: 1000 + (seed % 49000),
    tasksCompleted: 50 + (seed % 450),
    uptime: +(97 + (seed % 30) / 10).toFixed(1),
  };
}

function generateBotRevenue(botId: number, tier: string) {
  const seed = botId * 137;
  const tierMultiplier = tier === "elite" ? 10 : tier === "enterprise" ? 5 : tier === "pro" ? 2 : 0.5;
  return {
    revenue: Math.round((100 + (seed % 4900)) * tierMultiplier),
    clients: Math.round((5 + (seed % 45)) * tierMultiplier),
    tasks: 20 + (seed % 480),
    apiCalls: 500 + (seed % 9500),
  };
}

const DIVISION_ICONS: Record<string, string> = {
  DreamFinance: "from-emerald-500/15 to-emerald-500/5",
  DreamSalesPro: "from-orange-500/15 to-orange-500/5",
  DreamRealEstate: "from-blue-500/15 to-blue-500/5",
  DreamAIInfra: "from-violet-500/15 to-violet-500/5",
  DreamRetail: "from-pink-500/15 to-pink-500/5",
  DreamProServices: "from-cyan-500/15 to-cyan-500/5",
  DreamData: "from-indigo-500/15 to-indigo-500/5",
  DreamGlobal: "from-teal-500/15 to-teal-500/5",
  DreamAutomation: "from-yellow-500/15 to-yellow-500/5",
  DreamContent: "from-rose-500/15 to-rose-500/5",
  DreamTrade: "from-lime-500/15 to-lime-500/5",
  DreamFlow: "from-sky-500/15 to-sky-500/5",
  DreamMarket: "from-fuchsia-500/15 to-fuchsia-500/5",
  DreamEmpire: "from-amber-500/15 to-amber-500/5",
  CommandCore: "from-slate-500/15 to-slate-500/5",
  GameTitan: "from-red-500/15 to-red-500/5",
};

export default function RevenuePage() {
  const [botSlug, setBotSlug] = useState<string | undefined>(undefined);
  const [selectedDivision, setSelectedDivision] = useState<string>("all");

  const botsQuery = useQuery<BotProfile[]>({ queryKey: ["/api/bots"] });
  const bots = botsQuery.data ?? [];

  const divisionGroups = useMemo(() => {
    const groups = new Map<string, BotProfile[]>();
    bots.forEach(b => {
      const arr = groups.get(b.division) || [];
      arr.push(b);
      groups.set(b.division, arr);
    });
    return groups;
  }, [bots]);

  const divisionStats = useMemo(() => {
    return Array.from(divisionGroups.entries()).map(([div, divBots]) => {
      const rev = generateDivisionRevenue(div, divBots.length);
      const apiCount = getApiCountForDivision(div);
      return { division: div, bots: divBots, apiCount, ...rev };
    }).sort((a, b) => b.monthlyRevenue - a.monthlyRevenue);
  }, [divisionGroups]);

  const totals = useMemo(() => {
    return divisionStats.reduce(
      (acc, d) => ({
        revenue: acc.revenue + d.monthlyRevenue,
        clients: acc.clients + d.clients,
        apiCalls: acc.apiCalls + d.apiCallsToday,
        tasks: acc.tasks + d.tasksCompleted,
      }),
      { revenue: 0, clients: 0, apiCalls: 0, tasks: 0 }
    );
  }, [divisionStats]);

  const filteredBots = selectedDivision === "all"
    ? bots
    : bots.filter(b => b.division === selectedDivision);

  const topBots = useMemo(() => {
    return filteredBots
      .map(b => ({ ...b, ...generateBotRevenue(b.id, b.tier) }))
      .sort((a, b) => b.revenue - a.revenue)
      .slice(0, 20);
  }, [filteredBots]);

  const totalApiCount = getTotalApiCount();

  return (
    <AppShell selectedBotSlug={botSlug} onBotChange={setBotSlug}>
      <Seo title="Revenue Dashboard - DreamCo Empire OS" description="Track revenue across all divisions and bots." />

      <div className="buddy-card buddy-noise buddy-appear overflow-hidden">
        <div className="px-5 pt-6 pb-5 md:px-8 md:pt-8 md:pb-6 border-b border-border/60">
          <div className="flex flex-wrap items-center justify-between gap-4">
            <div>
              <h1 className="text-2xl md:text-3xl" data-testid="text-revenue-title">Revenue Dashboard</h1>
              <p className="text-sm text-muted-foreground mt-1">Empire-wide revenue tracking & API integration metrics</p>
            </div>
            <div className="flex flex-wrap items-center gap-2">
              <Badge variant="secondary" className="rounded-full">
                <Plug className="h-3 w-3 mr-1.5 text-primary" />
                {totalApiCount} APIs Connected
              </Badge>
              <Badge variant="secondary" className="rounded-full">
                <Activity className="h-3 w-3 mr-1.5 text-green-500" />
                Live
              </Badge>
              <Button
                variant="outline"
                size="sm"
                onClick={() => {
                  const { toast } = (window as any).__dreamToast ?? {};
                  const csv = ["Division,Revenue,Clients,API Count",
                    ...topBotRevenue.map(b => `${b.division ?? ""},${generateBotRevenue(b.id, b.tier).revenue},${generateBotRevenue(b.id, b.tier).clients},${getApiCountForDivision(b.division ?? "")}`)
                  ].join("\n");
                  const blob = new Blob([csv], { type: "text/csv" });
                  const url = URL.createObjectURL(blob);
                  const a = document.createElement("a");
                  a.href = url;
                  a.download = `empire-revenue-${new Date().toISOString().slice(0,10)}.csv`;
                  a.click();
                  URL.revokeObjectURL(url);
                }}
                data-testid="button-export-revenue"
              >
                <Download className="h-3.5 w-3.5 mr-1.5" />
                Export CSV
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={async () => {
                  await queryClient.invalidateQueries({ queryKey: ["/api/bots"] });
                }}
                data-testid="button-refresh-revenue"
              >
                <RefreshCw className="h-3.5 w-3.5 mr-1.5" />
                Refresh
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => {
                  const text = [
                    `Revenue Report — ${new Date().toLocaleDateString()}`,
                    `Monthly Revenue: $${totals.revenue.toLocaleString()}`,
                    `Active Clients: ${totals.clients}`,
                    `APIs Connected: ${totalApiCount}`,
                  ].join("\n");
                  navigator.clipboard.writeText(text);
                }}
                data-testid="button-copy-revenue-report"
              >
                <Copy className="h-3.5 w-3.5 mr-1.5" />
                Copy Report
              </Button>
            </div>
          </div>
        </div>

        {botsQuery.isLoading ? (
          <div className="p-5 md:p-8 space-y-6">
            <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
              {Array.from({ length: 4 }).map((_, i) => <Skeleton key={i} className="h-28 rounded-2xl" />)}
            </div>
          </div>
        ) : (
          <div className="p-5 md:p-8 space-y-8 buddy-stagger">
            <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
              <Card data-testid="stat-total-revenue">
                <CardHeader className="flex flex-row items-center justify-between gap-1 space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium text-muted-foreground">Monthly Revenue</CardTitle>
                  <CircleDollarSign className="h-4 w-4 text-green-500" />
                </CardHeader>
                <CardContent>
                  <p className="text-3xl font-bold tracking-tight">${totals.revenue.toLocaleString()}</p>
                  <p className="text-xs text-green-600 dark:text-green-400 mt-1 flex items-center gap-1">
                    <TrendingUp className="h-3 w-3" /> +18.4% vs last month
                  </p>
                </CardContent>
              </Card>

              <Card data-testid="stat-total-clients">
                <CardHeader className="flex flex-row items-center justify-between gap-1 space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium text-muted-foreground">Active Clients</CardTitle>
                  <Users className="h-4 w-4 text-primary" />
                </CardHeader>
                <CardContent>
                  <p className="text-3xl font-bold tracking-tight">{totals.clients.toLocaleString()}</p>
                  <p className="text-xs text-muted-foreground mt-1">Across {divisionStats.length} divisions</p>
                </CardContent>
              </Card>

              <Card data-testid="stat-api-calls">
                <CardHeader className="flex flex-row items-center justify-between gap-1 space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium text-muted-foreground">API Calls Today</CardTitle>
                  <Zap className="h-4 w-4 text-yellow-500" />
                </CardHeader>
                <CardContent>
                  <p className="text-3xl font-bold tracking-tight">{totals.apiCalls.toLocaleString()}</p>
                  <p className="text-xs text-muted-foreground mt-1">{totalApiCount} integrations active</p>
                </CardContent>
              </Card>

              <Card data-testid="stat-tasks-completed">
                <CardHeader className="flex flex-row items-center justify-between gap-1 space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium text-muted-foreground">Tasks Completed</CardTitle>
                  <Target className="h-4 w-4 text-primary" />
                </CardHeader>
                <CardContent>
                  <p className="text-3xl font-bold tracking-tight">{totals.tasks.toLocaleString()}</p>
                  <p className="text-xs text-green-600 dark:text-green-400 mt-1 flex items-center gap-1">
                    <TrendingUp className="h-3 w-3" /> 96.3% success rate
                  </p>
                </CardContent>
              </Card>
            </div>

            <div>
              <div className="flex items-center justify-between gap-3 mb-4">
                <h2 className="text-lg font-semibold" data-testid="text-division-revenue">Division Revenue</h2>
                <Link href="/divisions" className="text-xs text-primary hover:underline underline-offset-4" data-testid="link-view-divisions">
                  View all divisions
                </Link>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {divisionStats.map(div => {
                  const gradient = DIVISION_ICONS[div.division] ?? "from-muted/50 to-muted/20";
                  return (
                    <Card key={div.division} className="overflow-visible" data-testid={`revenue-div-${div.division}`}>
                      <div className={cn("absolute inset-0 rounded-xl bg-gradient-to-br pointer-events-none opacity-40", gradient)} />
                      <CardContent className="p-4 relative">
                        <div className="flex items-start justify-between gap-3">
                          <div className="min-w-0">
                            <div className="flex items-center gap-2 flex-wrap">
                              <p className="text-sm font-semibold truncate">{div.division}</p>
                              <Badge variant="outline" className="rounded-full text-[10px]">{div.bots.length} bots</Badge>
                              {div.apiCount > 0 && (
                                <Badge variant="secondary" className="rounded-full text-[10px]">
                                  <Plug className="h-2.5 w-2.5 mr-1" />{div.apiCount} APIs
                                </Badge>
                              )}
                            </div>
                            <p className="text-2xl font-bold mt-1">${div.monthlyRevenue.toLocaleString()}<span className="text-xs text-muted-foreground font-normal">/mo</span></p>
                          </div>
                          <div className="text-right flex-shrink-0">
                            <p className="text-xs text-green-600 dark:text-green-400 flex items-center gap-1">
                              <TrendingUp className="h-3 w-3" /> +{div.growth}%
                            </p>
                            <p className="text-xs text-muted-foreground mt-1">{div.clients} clients</p>
                          </div>
                        </div>
                        <div className="mt-3 grid grid-cols-3 gap-3">
                          <div>
                            <p className="text-[10px] text-muted-foreground">Avg Deal</p>
                            <p className="text-xs font-semibold">${div.avgDealSize.toLocaleString()}</p>
                          </div>
                          <div>
                            <p className="text-[10px] text-muted-foreground">Conv Rate</p>
                            <p className="text-xs font-semibold">{div.conversionRate}%</p>
                          </div>
                          <div>
                            <p className="text-[10px] text-muted-foreground">Uptime</p>
                            <p className="text-xs font-semibold">{div.uptime}%</p>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  );
                })}
              </div>
            </div>

            <div>
              <div className="flex flex-wrap items-center justify-between gap-3 mb-4">
                <h2 className="text-lg font-semibold" data-testid="text-top-bots">Top Revenue Bots</h2>
                <Select value={selectedDivision} onValueChange={setSelectedDivision}>
                  <SelectTrigger className="w-[200px] rounded-xl" data-testid="select-division-filter">
                    <SelectValue placeholder="All Divisions" />
                  </SelectTrigger>
                  <SelectContent className="rounded-xl">
                    <SelectItem value="all">All Divisions</SelectItem>
                    {Array.from(divisionGroups.keys()).sort().map(d => (
                      <SelectItem key={d} value={d}>{d}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                {topBots.map((bot, i) => (
                  <Link key={bot.id} href={`/bot/${bot.id}`}>
                    <Card className="hover-elevate overflow-visible cursor-pointer" data-testid={`revenue-bot-${bot.id}`}>
                      <CardContent className="p-3">
                        <div className="flex items-center gap-3">
                          <span className="text-sm font-mono text-muted-foreground w-6 text-right flex-shrink-0">#{i + 1}</span>
                          <div className="h-9 w-9 rounded-xl bg-primary/10 flex items-center justify-center flex-shrink-0">
                            <Bot className="h-4 w-4 text-primary" />
                          </div>
                          <div className="min-w-0 flex-1">
                            <div className="flex items-center gap-2 flex-wrap">
                              <p className="text-sm font-semibold truncate">{bot.displayName}</p>
                              <Badge variant="outline" className="rounded-full text-[10px] capitalize">{bot.tier}</Badge>
                            </div>
                            <p className="text-xs text-muted-foreground truncate">{bot.division} - {bot.category}</p>
                          </div>
                          <div className="flex items-center gap-4 flex-shrink-0">
                            <div className="text-right">
                              <p className="text-sm font-bold">${bot.revenue.toLocaleString()}</p>
                              <p className="text-[10px] text-muted-foreground">/month</p>
                            </div>
                            <div className="text-right hidden sm:block">
                              <p className="text-xs font-medium">{bot.clients} clients</p>
                              <p className="text-[10px] text-muted-foreground">{bot.tasks} tasks</p>
                            </div>
                            <ArrowRight className="h-4 w-4 text-muted-foreground" />
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  </Link>
                ))}
              </div>
            </div>

            <Card data-testid="api-integration-summary">
              <CardHeader className="flex flex-row items-center justify-between gap-2 space-y-0">
                <CardTitle className="text-lg flex items-center gap-2">
                  <Network className="h-5 w-5 text-primary" />
                  API Integration Summary
                </CardTitle>
                <Badge variant="secondary" className="rounded-full">{totalApiCount} total</Badge>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                  {Object.entries(DIVISION_API_REGISTRIES).map(([div, registry]) => {
                    const apiCount = registry.categories.reduce((s, c) => s + c.apis.length, 0);
                    return (
                      <div key={div} className="flex items-center justify-between p-3 rounded-xl border border-border/40" data-testid={`api-summary-${div}`}>
                        <div className="flex items-center gap-2 min-w-0">
                          <Plug className="h-4 w-4 text-primary flex-shrink-0" />
                          <span className="text-sm font-medium truncate">{div}</span>
                        </div>
                        <div className="flex items-center gap-2 flex-shrink-0">
                          <Badge variant="outline" className="rounded-full text-[10px]">{apiCount} APIs</Badge>
                          <Badge variant="outline" className="rounded-full text-[10px]">{registry.categories.length} categories</Badge>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </CardContent>
            </Card>
          </div>
        )}
      </div>
    </AppShell>
  );
}
