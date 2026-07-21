import { useState } from "react";
import {
  useGetDashboardSummary, getGetDashboardSummaryQueryKey,
  useListBots, getListBotsQueryKey,
  useListCommits, getListCommitsQueryKey,
  useGetBuildProgress, getGetBuildProgressQueryKey
} from "@workspace/api-client-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Skeleton } from "@/components/ui/skeleton";
import { Bot, GitCommit, DollarSign, Activity, Zap, Server, Gauge } from "lucide-react";
import { Link } from "wouter";

export default function Dashboard() {
  const { data: summary, isLoading: isLoadingSummary } = useGetDashboardSummary({
    query: { queryKey: getGetDashboardSummaryQueryKey() }
  });

  const { data: bots, isLoading: isLoadingBots } = useListBots({
    query: { queryKey: getListBotsQueryKey() }
  });

  const { data: commits, isLoading: isLoadingCommits } = useListCommits({
    query: { queryKey: getListCommitsQueryKey() }
  });

  const { data: build, isLoading: isLoadingBuild } = useGetBuildProgress({
    query: { queryKey: getGetBuildProgressQueryKey() }
  });

  const getProgressColor = (percent: number) => {
    if (percent >= 80) return "bg-primary";
    if (percent >= 50) return "bg-amber-500";
    return "bg-destructive";
  };

  const dailyPercent = summary ? Math.min(100, (summary.dailyRevenue / (summary.dailyTarget || 500)) * 100) : 0;
  const monthlyPercent = summary ? Math.min(100, (summary.monthlyRevenue / (summary.monthlyTarget || 15000)) * 100) : 0;

  return (
    <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="flex flex-col gap-2">
        <h1 className="text-3xl font-mono font-bold tracking-tight text-foreground uppercase flex items-center gap-3">
          <Activity className="h-8 w-8 text-primary" />
          Executive_Dashboard
        </h1>
        <p className="text-muted-foreground font-mono text-sm uppercase tracking-wider">System Status: Online // Telemetry Active</p>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          title="Total Bots"
          value={summary?.totalBots}
          icon={<Bot className="h-5 w-5 text-primary" />}
          loading={isLoadingSummary}
        />
        <MetricCard
          title="Active Bots"
          value={summary?.activeBots}
          icon={<Zap className="h-5 w-5 text-primary" />}
          loading={isLoadingSummary}
          subtitle={`${summary?.idleBots || 0} Idle`}
        />
        <MetricCard
          title="Total Repos"
          value={summary?.totalRepos}
          icon={<Server className="h-5 w-5 text-primary" />}
          loading={isLoadingSummary}
        />
        <MetricCard
          title="Recent Commits"
          value={summary?.recentCommits}
          icon={<GitCommit className="h-5 w-5 text-primary" />}
          loading={isLoadingSummary}
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Revenue Tracking */}
        <Card className="lg:col-span-2 border-border/40 bg-card/50 backdrop-blur">
          <CardHeader>
            <CardTitle className="font-mono text-lg uppercase flex items-center gap-2">
              <DollarSign className="h-5 w-5 text-primary" />
              Revenue_Tracking
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-8">
            {isLoadingSummary ? (
              <div className="space-y-4">
                <Skeleton className="h-12 w-full" />
                <Skeleton className="h-12 w-full" />
              </div>
            ) : (
              <>
                <div className="space-y-2">
                  <div className="flex justify-between font-mono text-sm">
                    <span className="text-muted-foreground uppercase">Daily Revenue</span>
                    <span className="text-foreground">${summary?.dailyRevenue.toLocaleString()} / ${summary?.dailyTarget?.toLocaleString() || '500'}</span>
                  </div>
                  <Progress value={dailyPercent} className="h-2 bg-muted/50" indicatorClassName={getProgressColor(dailyPercent)} />
                </div>
                <div className="space-y-2">
                  <div className="flex justify-between font-mono text-sm">
                    <span className="text-muted-foreground uppercase">Monthly Revenue</span>
                    <span className="text-foreground">${summary?.monthlyRevenue.toLocaleString()} / ${summary?.monthlyTarget?.toLocaleString() || '15,000'}</span>
                  </div>
                  <Progress value={monthlyPercent} className="h-2 bg-muted/50" indicatorClassName={getProgressColor(monthlyPercent)} />
                </div>
              </>
            )}
          </CardContent>
        </Card>

        {/* Quick Actions / Status */}
        <Card className="border-border/40 bg-card/50 backdrop-blur">
          <CardHeader>
            <CardTitle className="font-mono text-lg uppercase">System_Status</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <Link href="/buddy">
              <div className="w-full group cursor-pointer border border-primary/20 bg-primary/5 hover:bg-primary/10 transition-colors rounded-md p-4 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="h-2 w-2 rounded-full bg-primary animate-pulse" />
                  <span className="font-mono text-sm text-primary uppercase">BuddyBot Active</span>
                </div>
                <Zap className="h-4 w-4 text-primary group-hover:scale-110 transition-transform" />
              </div>
            </Link>

            <div className="space-y-3 mt-6">
              <h4 className="font-mono text-xs text-muted-foreground uppercase mb-2">Bot Distribution</h4>
              {isLoadingBots ? (
                <Skeleton className="h-24 w-full" />
              ) : (
                <div className="space-y-2">
                  {Object.entries(
                    (bots || []).reduce((acc, bot) => {
                      acc[bot.category] = (acc[bot.category] || 0) + 1;
                      return acc;
                    }, {} as Record<string, number>)
                  ).slice(0, 4).map(([category, count]) => (
                    <div key={category} className="flex justify-between items-center text-sm font-mono">
                      <span className="text-muted-foreground">{category}</span>
                      <span className="text-foreground">{count}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Build Progress */}
      <Card className="border-border/40 bg-card/50 backdrop-blur">
        <CardHeader>
          <CardTitle className="font-mono text-lg uppercase flex items-center gap-2">
            <Gauge className="h-5 w-5 text-primary" />
            System_Build_Progress
            {!isLoadingBuild && build && (
              <span className="ml-auto text-3xl font-bold text-primary tabular-nums">
                {build.overallPercent}%
              </span>
            )}
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {isLoadingBuild ? (
            <div className="space-y-3">
              {[1, 2, 3, 4, 5, 6].map(i => <Skeleton key={i} className="h-10 w-full" />)}
            </div>
          ) : (
            <>
              <Progress
                value={build?.overallPercent ?? 0}
                className="h-2 bg-muted/50"
                indicatorClassName={getProgressColor(build?.overallPercent ?? 0)}
              />
              <div className="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-3 pt-2">
                {build?.sections?.map((s) => {
                  const pct = s.total > 0 ? Math.round((s.done / s.total) * 100) : 0;
                  return (
                    <div key={s.name} className="space-y-1">
                      <div className="flex justify-between font-mono text-xs">
                        <span className="text-muted-foreground uppercase tracking-wider">{s.name}</span>
                        <span className="text-foreground tabular-nums">{s.done} / {s.total}</span>
                      </div>
                      <Progress
                        value={pct}
                        className="h-1.5 bg-muted/40"
                        indicatorClassName={getProgressColor(pct)}
                      />
                    </div>
                  );
                })}
              </div>
            </>
          )}
        </CardContent>
      </Card>

      {/* GitHub Activity */}
      <Card className="border-border/40 bg-card/50 backdrop-blur">
        <CardHeader>
          <CardTitle className="font-mono text-lg uppercase flex items-center gap-2">
            <GitCommit className="h-5 w-5 text-primary" />
            Recent_Activity
          </CardTitle>
        </CardHeader>
        <CardContent>
          {isLoadingCommits ? (
            <div className="space-y-4">
              {[1, 2, 3].map(i => <Skeleton key={i} className="h-16 w-full" />)}
            </div>
          ) : (
            <div className="space-y-4">
              {commits?.slice(0, 5).map((commit) => (
                <div key={commit.sha} className="flex items-start gap-4 p-3 rounded-lg border border-border/40 bg-background/50">
                  <div className="h-8 w-8 rounded-full bg-primary/10 flex items-center justify-center shrink-0">
                    <GitCommit className="h-4 w-4 text-primary" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-foreground truncate">{commit.message}</p>
                    <div className="flex items-center gap-2 mt-1 text-xs text-muted-foreground font-mono">
                      <span className="text-primary/80">{commit.repoName}</span>
                      <span>•</span>
                      <span>{commit.author}</span>
                      <span>•</span>
                      <span>{new Date(commit.date).toLocaleDateString()}</span>
                    </div>
                  </div>
                  <div className="text-xs font-mono text-muted-foreground shrink-0">
                    {commit.sha.substring(0, 7)}
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

function MetricCard({ title, value, icon, loading, subtitle }: { title: string, value?: number, icon: React.ReactNode, loading: boolean, subtitle?: string }) {
  return (
    <Card className="border-border/40 bg-card/50 backdrop-blur">
      <CardContent className="p-6">
        <div className="flex items-center justify-between">
          <div className="space-y-2">
            <p className="text-xs font-mono text-muted-foreground uppercase tracking-wider">{title}</p>
            {loading ? (
              <Skeleton className="h-8 w-20" />
            ) : (
              <div className="flex items-baseline gap-2">
                <h3 className="text-3xl font-mono font-bold text-foreground">{value?.toLocaleString() || 0}</h3>
                {subtitle && <span className="text-xs font-mono text-muted-foreground">{subtitle}</span>}
              </div>
            )}
          </div>
          <div className="h-10 w-10 rounded-full bg-primary/10 flex items-center justify-center">
            {icon}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
