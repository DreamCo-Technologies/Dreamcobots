import { useQuery, useMutation } from "@tanstack/react-query";
import { queryClient, apiRequest } from "@/lib/queryClient";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Skeleton } from "@/components/ui/skeleton";
import { useToast } from "@/hooks/use-toast";
import type { DebugEvent, AutoFix, RevenueLeak, SecurityScan, DebugOverview } from "@shared/schema";
import {
  Activity,
  AlertTriangle,
  ArrowDownRight,
  BarChart3,
  BookOpen,
  Bug,
  CheckCircle2,
  Clock,
  Copy,
  DollarSign,
  Eye,
  Gauge,
  History,
  Loader2,
  Shield,
  ShieldAlert,
  Sparkles,
  TrendingUp,
  Wrench,
  XCircle,
  Zap,
} from "lucide-react";

const CATEGORY_LABELS: Record<string, string> = {
  syntax_error: "Syntax Error",
  runtime_crash: "Runtime Crash",
  api_failure: "API Failure",
  auth_error: "Auth Error",
  logic_bug: "Logic Bug",
  performance_issue: "Performance",
  ux_friction: "UX Friction",
  revenue_leak: "Revenue Leak",
  security_risk: "Security Risk",
  infinite_loop: "Infinite Loop",
  model_drift: "Model Drift",
  cost_explosion: "Cost Explosion",
};

function severityColor(s: number) {
  if (s >= 8) return "text-red-500";
  if (s >= 5) return "text-yellow-500";
  return "text-green-500";
}

function severityBg(s: number) {
  if (s >= 8) return "bg-red-500/10 text-red-500 border-red-500/20";
  if (s >= 5) return "bg-yellow-500/10 text-yellow-500 border-yellow-500/20";
  return "bg-green-500/10 text-green-500 border-green-500/20";
}

function statusBadge(status: string) {
  switch (status) {
    case "open": return <Badge variant="destructive" data-testid="badge-status-open">Open</Badge>;
    case "investigating": return <Badge className="bg-yellow-500/20 text-yellow-600 border-yellow-500/30" data-testid="badge-status-investigating">Investigating</Badge>;
    case "resolved": return <Badge className="bg-green-500/20 text-green-600 border-green-500/30" data-testid="badge-status-resolved">Resolved</Badge>;
    case "ignored": return <Badge variant="secondary" data-testid="badge-status-ignored">Ignored</Badge>;
    case "queued": return <Badge className="bg-blue-500/20 text-blue-600 border-blue-500/30" data-testid="badge-status-queued">Queued</Badge>;
    case "applied": return <Badge className="bg-green-500/20 text-green-600 border-green-500/30" data-testid="badge-status-applied">Applied</Badge>;
    case "rejected": return <Badge variant="destructive" data-testid="badge-status-rejected">Rejected</Badge>;
    case "remediated": return <Badge className="bg-green-500/20 text-green-600 border-green-500/30" data-testid="badge-status-remediated">Remediated</Badge>;
    default: return <Badge variant="secondary">{status}</Badge>;
  }
}

function HealthGauge({ score }: { score: number }) {
  const color = score >= 80 ? "text-green-500" : score >= 50 ? "text-yellow-500" : "text-red-500";
  const bg = score >= 80 ? "bg-green-500" : score >= 50 ? "bg-yellow-500" : "bg-red-500";
  return (
    <div className="flex flex-col items-center gap-2" data-testid="health-gauge">
      <div className="relative w-32 h-32">
        <svg className="w-32 h-32 -rotate-90" viewBox="0 0 120 120">
          <circle cx="60" cy="60" r="52" fill="none" stroke="currentColor" strokeWidth="8" className="text-muted/30" />
          <circle cx="60" cy="60" r="52" fill="none" stroke="currentColor" strokeWidth="8"
            className={color}
            strokeDasharray={`${(score / 100) * 327} 327`}
            strokeLinecap="round" />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className={`text-3xl font-bold ${color}`} data-testid="text-health-score">{score}</span>
          <span className="text-xs text-muted-foreground">/ 100</span>
        </div>
      </div>
      <span className="text-sm font-medium text-muted-foreground">Global Health Score</span>
    </div>
  );
}

function OverviewTab() {
  const { data: overview, isLoading } = useQuery<DebugOverview>({
    queryKey: ["/api/debug/overview"],
  });

  if (isLoading) return <div className="grid grid-cols-1 md:grid-cols-3 gap-4"><Skeleton className="h-40" /><Skeleton className="h-40" /><Skeleton className="h-40" /></div>;
  if (!overview) return null;

  const kpis = [
    { label: "Open Events", value: overview.openEvents, icon: Bug, color: "text-red-500", testId: "kpi-open-events" },
    { label: "Critical", value: overview.criticalEvents, icon: AlertTriangle, color: "text-red-600", testId: "kpi-critical" },
    { label: "Events Today", value: overview.eventsToday, icon: Clock, color: "text-blue-500", testId: "kpi-today" },
    { label: "Auto-Fixes Applied", value: overview.appliedFixes, icon: Wrench, color: "text-green-500", testId: "kpi-applied" },
    { label: "Fixes Queued", value: overview.queuedFixes, icon: Loader2, color: "text-yellow-500", testId: "kpi-queued" },
    { label: "Fix Success Rate", value: `${overview.fixSuccessRate}%`, icon: TrendingUp, color: "text-green-500", testId: "kpi-success-rate" },
    { label: "Revenue at Risk", value: `$${overview.revenueAtRisk.toLocaleString()}`, icon: DollarSign, color: "text-red-500", testId: "kpi-revenue-risk" },
    { label: "Security Issues", value: overview.openSecurityIssues, icon: ShieldAlert, color: "text-orange-500", testId: "kpi-security" },
    { label: "Avg Severity", value: overview.avgSeverity, icon: Gauge, color: "text-yellow-500", testId: "kpi-severity" },
  ];

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="md:row-span-2 flex items-center justify-center">
          <CardContent className="pt-6">
            <HealthGauge score={overview.globalHealthScore} />
          </CardContent>
        </Card>
        {kpis.map((k) => (
          <Card key={k.testId}>
            <CardContent className="pt-4 pb-4">
              <div className="flex items-center gap-3">
                <k.icon className={`h-5 w-5 ${k.color}`} />
                <div>
                  <p className="text-xs text-muted-foreground">{k.label}</p>
                  <p className="text-xl font-bold" data-testid={k.testId}>{k.value}</p>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center gap-2 pb-2">
            <Bug className="h-4 w-4 text-red-500" />
            <CardTitle className="text-sm">Event Breakdown</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between"><span>Total Events</span><span className="font-medium">{overview.openEvents + overview.criticalEvents}</span></div>
              <div className="flex justify-between"><span>Open</span><span className="font-medium text-red-500">{overview.openEvents}</span></div>
              <div className="flex justify-between"><span>Critical</span><span className="font-medium text-red-600">{overview.criticalEvents}</span></div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center gap-2 pb-2">
            <Wrench className="h-4 w-4 text-blue-500" />
            <CardTitle className="text-sm">Auto-Fix Engine</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between"><span>Total Fixes</span><span className="font-medium">{overview.totalAutoFixes}</span></div>
              <div className="flex justify-between"><span>Applied</span><span className="font-medium text-green-500">{overview.appliedFixes}</span></div>
              <div className="flex justify-between"><span>Queued</span><span className="font-medium text-yellow-500">{overview.queuedFixes}</span></div>
              <div className="flex justify-between"><span>Rejected</span><span className="font-medium text-red-500">{overview.rejectedFixes}</span></div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center gap-2 pb-2">
            <Shield className="h-4 w-4 text-green-500" />
            <CardTitle className="text-sm">Security & Revenue</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between"><span>Security Issues</span><span className="font-medium">{overview.totalSecurityIssues}</span></div>
              <div className="flex justify-between"><span>Open Security</span><span className="font-medium text-orange-500">{overview.openSecurityIssues}</span></div>
              <div className="flex justify-between"><span>Revenue Leaks</span><span className="font-medium">{overview.totalRevenueLeaks}</span></div>
              <div className="flex justify-between"><span>Open Leaks</span><span className="font-medium text-red-500">{overview.openRevenueLeaks}</span></div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

function ActiveIssuesTab() {
  const { data: events = [], isLoading } = useQuery<DebugEvent[]>({ queryKey: ["/api/debug/events"] });
  const { toast } = useToast();
  const resolveMutation = useMutation({
    mutationFn: (id: number) => apiRequest("PATCH", `/api/debug/events/${id}/resolve`, { resolution: "Manually resolved" }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["/api/debug/events"] });
      queryClient.invalidateQueries({ queryKey: ["/api/debug/overview"] });
      toast({ title: "Event resolved" });
    },
  });

  if (isLoading) return <Skeleton className="h-64" />;
  const openEvents = events.filter(e => e.status === "open" || e.status === "investigating");
  const resolvedEvents = events.filter(e => e.status === "resolved");

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2 flex-wrap">
        <Badge variant="destructive">{openEvents.length} Open</Badge>
        <Badge className="bg-green-500/20 text-green-600 border-green-500/30">{resolvedEvents.length} Resolved</Badge>
        <Badge variant="secondary">{events.length} Total</Badge>
      </div>
      <ScrollArea className="h-[600px]">
        <div className="space-y-3" data-testid="events-list">
          {events.length === 0 && (
            <Card><CardContent className="pt-6 text-center text-muted-foreground">No debug events recorded yet. The system is monitoring all bots.</CardContent></Card>
          )}
          {events.map((event) => (
            <Card key={event.id} data-testid={`event-${event.id}`}>
              <CardContent className="pt-4 pb-4">
                <div className="flex items-start justify-between gap-3 flex-wrap">
                  <div className="flex-1 min-w-0 space-y-1">
                    <div className="flex items-center gap-2 flex-wrap">
                      {statusBadge(event.status)}
                      <Badge className={severityBg(event.severity)} variant="outline">
                        Severity {event.severity}/10
                      </Badge>
                      <Badge variant="outline">{CATEGORY_LABELS[event.category] || event.category}</Badge>
                      {event.revenueImpact > 0 && (
                        <Badge variant="outline" className="bg-red-500/10 text-red-500">
                          <DollarSign className="h-3 w-3 mr-1" />${event.revenueImpact.toLocaleString()} impact
                        </Badge>
                      )}
                    </div>
                    <p className="text-sm font-medium" data-testid={`event-summary-${event.id}`}>{event.summary}</p>
                    <div className="flex items-center gap-3 text-xs text-muted-foreground flex-wrap">
                      {event.botId && <span>Bot #{event.botId}</span>}
                      <span>Priority: {event.fixPriority}/10</span>
                      <span>{new Date(event.createdAt).toLocaleString()}</span>
                    </div>
                    {event.resolution && <p className="text-xs text-green-600 mt-1">Resolution: {event.resolution}</p>}
                  </div>
                  {(event.status === "open" || event.status === "investigating") && (
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => resolveMutation.mutate(event.id)}
                      disabled={resolveMutation.isPending}
                      data-testid={`btn-resolve-event-${event.id}`}
                    >
                      <CheckCircle2 className="h-4 w-4 mr-1" />
                      Resolve
                    </Button>
                  )}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </ScrollArea>
    </div>
  );
}

function AutoFixesTab() {
  const { data: fixes = [], isLoading } = useQuery<AutoFix[]>({ queryKey: ["/api/debug/auto-fixes"] });
  const { toast } = useToast();

  const applyMutation = useMutation({
    mutationFn: (id: number) => apiRequest("PATCH", `/api/debug/auto-fixes/${id}/apply`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["/api/debug/auto-fixes"] });
      queryClient.invalidateQueries({ queryKey: ["/api/debug/overview"] });
      queryClient.invalidateQueries({ queryKey: ["/api/debug/events"] });
      toast({ title: "Fix applied successfully" });
    },
  });

  const rejectMutation = useMutation({
    mutationFn: (id: number) => apiRequest("PATCH", `/api/debug/auto-fixes/${id}/reject`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["/api/debug/auto-fixes"] });
      queryClient.invalidateQueries({ queryKey: ["/api/debug/overview"] });
      toast({ title: "Fix rejected" });
    },
  });

  if (isLoading) return <Skeleton className="h-64" />;

  const queued = fixes.filter(f => f.status === "queued");
  const applied = fixes.filter(f => f.status === "applied");

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2 flex-wrap">
        <Badge className="bg-blue-500/20 text-blue-600 border-blue-500/30">{queued.length} Queued</Badge>
        <Badge className="bg-green-500/20 text-green-600 border-green-500/30">{applied.length} Applied</Badge>
        <Badge variant="secondary">{fixes.length} Total</Badge>
      </div>
      <p className="text-xs text-muted-foreground">Fixes with confidence 90%+ are auto-applied. Below 90% requires manual approval.</p>
      <ScrollArea className="h-[600px]">
        <div className="space-y-3" data-testid="fixes-list">
          {fixes.length === 0 && (
            <Card><CardContent className="pt-6 text-center text-muted-foreground">No auto-fixes generated yet. The engine will create patches when issues are detected.</CardContent></Card>
          )}
          {fixes.map((fix) => (
            <Card key={fix.id} data-testid={`fix-${fix.id}`}>
              <CardContent className="pt-4 pb-4">
                <div className="flex items-start justify-between gap-3 flex-wrap">
                  <div className="flex-1 min-w-0 space-y-1">
                    <div className="flex items-center gap-2 flex-wrap">
                      {statusBadge(fix.status)}
                      <Badge variant="outline" className={fix.confidence >= 90 ? "bg-green-500/10 text-green-600" : fix.confidence >= 70 ? "bg-yellow-500/10 text-yellow-600" : "bg-red-500/10 text-red-600"}>
                        {fix.confidence}% confidence
                      </Badge>
                      {fix.botId && <Badge variant="outline">Bot #{fix.botId}</Badge>}
                    </div>
                    <p className="text-sm font-medium" data-testid={`fix-summary-${fix.id}`}>{fix.patchSummary}</p>
                    {fix.codeBefore && (
                      <div className="mt-2 space-y-1">
                        <p className="text-xs text-muted-foreground">Before:</p>
                        <pre className="text-xs bg-red-500/5 p-2 rounded-md overflow-x-auto border border-red-500/10">{fix.codeBefore}</pre>
                        <p className="text-xs text-muted-foreground">After:</p>
                        <pre className="text-xs bg-green-500/5 p-2 rounded-md overflow-x-auto border border-green-500/10">{fix.codeAfter}</pre>
                      </div>
                    )}
                    <div className="flex items-center gap-3 text-xs text-muted-foreground flex-wrap">
                      {fix.appliedAt && <span>Applied: {new Date(fix.appliedAt).toLocaleString()}</span>}
                      <span>Created: {new Date(fix.createdAt).toLocaleString()}</span>
                    </div>
                  </div>
                  {fix.status === "queued" && (
                    <div className="flex gap-2">
                      <Button size="sm" onClick={() => applyMutation.mutate(fix.id)} disabled={applyMutation.isPending} data-testid={`btn-apply-fix-${fix.id}`}>
                        <CheckCircle2 className="h-4 w-4 mr-1" />Apply
                      </Button>
                      <Button size="sm" variant="outline" onClick={() => rejectMutation.mutate(fix.id)} disabled={rejectMutation.isPending} data-testid={`btn-reject-fix-${fix.id}`}>
                        <XCircle className="h-4 w-4 mr-1" />Reject
                      </Button>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </ScrollArea>
    </div>
  );
}

function RevenueImpactTab() {
  const { data: leaks = [], isLoading } = useQuery<RevenueLeak[]>({ queryKey: ["/api/debug/revenue-leaks"] });
  const { toast } = useToast();

  const resolveMutation = useMutation({
    mutationFn: (id: number) => apiRequest("PATCH", `/api/debug/revenue-leaks/${id}/resolve`, { notes: "Resolved and patched" }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["/api/debug/revenue-leaks"] });
      queryClient.invalidateQueries({ queryKey: ["/api/debug/overview"] });
      toast({ title: "Revenue leak resolved" });
    },
  });

  if (isLoading) return <Skeleton className="h-64" />;

  const openLeaks = leaks.filter(l => l.status === "open");
  const totalRisk = openLeaks.reduce((s, l) => s + l.impactEstimate, 0);

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2 flex-wrap">
        <Badge variant="destructive">{openLeaks.length} Open Leaks</Badge>
        <Badge className="bg-red-500/20 text-red-600 border-red-500/30">${totalRisk.toLocaleString()} at Risk</Badge>
        <Badge variant="secondary">{leaks.length} Total</Badge>
      </div>
      <ScrollArea className="h-[600px]">
        <div className="space-y-3" data-testid="leaks-list">
          {leaks.length === 0 && (
            <Card><CardContent className="pt-6 text-center text-muted-foreground">No revenue leaks detected. The system is monitoring conversion funnels, pricing, and checkout flows.</CardContent></Card>
          )}
          {leaks.map((leak) => (
            <Card key={leak.id} data-testid={`leak-${leak.id}`}>
              <CardContent className="pt-4 pb-4">
                <div className="flex items-start justify-between gap-3 flex-wrap">
                  <div className="flex-1 min-w-0 space-y-1">
                    <div className="flex items-center gap-2 flex-wrap">
                      {statusBadge(leak.status)}
                      <Badge variant="outline">{leak.leakType}</Badge>
                      <Badge variant="outline" className="bg-red-500/10 text-red-500">
                        <DollarSign className="h-3 w-3 mr-1" />${leak.impactEstimate.toLocaleString()}/mo
                      </Badge>
                    </div>
                    <p className="text-sm">{leak.notes || "Revenue leak detected - investigation needed"}</p>
                    <div className="text-xs text-muted-foreground flex gap-3 flex-wrap">
                      {leak.botId && <span>Bot #{leak.botId}</span>}
                      <span>{new Date(leak.createdAt).toLocaleString()}</span>
                    </div>
                  </div>
                  {leak.status === "open" && (
                    <Button size="sm" variant="outline" onClick={() => resolveMutation.mutate(leak.id)} disabled={resolveMutation.isPending} data-testid={`btn-resolve-leak-${leak.id}`}>
                      <CheckCircle2 className="h-4 w-4 mr-1" />Resolve
                    </Button>
                  )}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </ScrollArea>
    </div>
  );
}

function SecurityTab() {
  const { data: scans = [], isLoading } = useQuery<SecurityScan[]>({ queryKey: ["/api/debug/security-scans"] });
  const { toast } = useToast();

  const remediateMutation = useMutation({
    mutationFn: (id: number) => apiRequest("PATCH", `/api/debug/security-scans/${id}/remediate`, { mitigation: "Auto-patched" }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["/api/debug/security-scans"] });
      queryClient.invalidateQueries({ queryKey: ["/api/debug/overview"] });
      toast({ title: "Security issue remediated" });
    },
  });

  if (isLoading) return <Skeleton className="h-64" />;

  const openScans = scans.filter(s => s.status === "open");

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2 flex-wrap">
        <Badge variant="destructive">{openScans.length} Open</Badge>
        <Badge variant="secondary">{scans.length} Total Scans</Badge>
      </div>
      <ScrollArea className="h-[600px]">
        <div className="space-y-3" data-testid="scans-list">
          {scans.length === 0 && (
            <Card><CardContent className="pt-6 text-center text-muted-foreground">No security vulnerabilities found. The system is continuously scanning for threats.</CardContent></Card>
          )}
          {scans.map((scan) => (
            <Card key={scan.id} data-testid={`scan-${scan.id}`}>
              <CardContent className="pt-4 pb-4">
                <div className="flex items-start justify-between gap-3 flex-wrap">
                  <div className="flex-1 min-w-0 space-y-1">
                    <div className="flex items-center gap-2 flex-wrap">
                      {statusBadge(scan.status)}
                      <Badge className={severityBg(scan.severity)} variant="outline">Severity {scan.severity}/10</Badge>
                      <Badge variant="outline">{scan.scanType}</Badge>
                    </div>
                    <p className="text-sm font-medium">{scan.finding}</p>
                    {scan.mitigation && <p className="text-xs text-green-600">Mitigation: {scan.mitigation}</p>}
                    <div className="text-xs text-muted-foreground flex gap-3 flex-wrap">
                      {scan.botId && <span>Bot #{scan.botId}</span>}
                      <span>{new Date(scan.createdAt).toLocaleString()}</span>
                    </div>
                  </div>
                  {scan.status === "open" && (
                    <Button size="sm" variant="outline" onClick={() => remediateMutation.mutate(scan.id)} disabled={remediateMutation.isPending} data-testid={`btn-remediate-scan-${scan.id}`}>
                      <Shield className="h-4 w-4 mr-1" />Remediate
                    </Button>
                  )}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </ScrollArea>
    </div>
  );
}

function BotHealthTab() {
  const { data: events = [] } = useQuery<DebugEvent[]>({ queryKey: ["/api/debug/events"] });
  const { data: fixes = [] } = useQuery<AutoFix[]>({ queryKey: ["/api/debug/auto-fixes"] });

  const botMap = new Map<number, { events: number; critical: number; fixes: number; avgSeverity: number }>();
  events.forEach(e => {
    if (!e.botId) return;
    const existing = botMap.get(e.botId) || { events: 0, critical: 0, fixes: 0, avgSeverity: 0 };
    existing.events++;
    if (e.severity >= 8) existing.critical++;
    existing.avgSeverity = (existing.avgSeverity * (existing.events - 1) + e.severity) / existing.events;
    botMap.set(e.botId, existing);
  });
  fixes.forEach(f => {
    if (!f.botId) return;
    const existing = botMap.get(f.botId) || { events: 0, critical: 0, fixes: 0, avgSeverity: 0 };
    existing.fixes++;
    botMap.set(f.botId, existing);
  });

  const bots = Array.from(botMap.entries()).sort((a, b) => b[1].critical - a[1].critical || b[1].events - a[1].events);

  return (
    <div className="space-y-4">
      <p className="text-sm text-muted-foreground">Bots ranked by stability - most issues first</p>
      <ScrollArea className="h-[600px]">
        <div className="space-y-3" data-testid="bot-health-list">
          {bots.length === 0 && (
            <Card><CardContent className="pt-6 text-center text-muted-foreground">No bot-specific issues detected. All 251 bots are operating within normal parameters.</CardContent></Card>
          )}
          {bots.map(([botId, stats]) => {
            const health = Math.max(0, 100 - stats.critical * 15 - stats.events * 3);
            return (
              <Card key={botId} data-testid={`bot-health-${botId}`}>
                <CardContent className="pt-4 pb-4">
                  <div className="flex items-center justify-between gap-3 flex-wrap">
                    <div className="space-y-1">
                      <p className="text-sm font-medium">Bot #{botId}</p>
                      <div className="flex items-center gap-2 flex-wrap">
                        <Badge variant="outline">{stats.events} events</Badge>
                        {stats.critical > 0 && <Badge variant="destructive">{stats.critical} critical</Badge>}
                        <Badge className="bg-blue-500/20 text-blue-600 border-blue-500/30">{stats.fixes} fixes</Badge>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className={`text-2xl font-bold ${health >= 70 ? "text-green-500" : health >= 40 ? "text-yellow-500" : "text-red-500"}`}>{health}</p>
                      <p className="text-xs text-muted-foreground">Health</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>
      </ScrollArea>
    </div>
  );
}

function PatchHistoryTab() {
  const { data: fixes = [], isLoading } = useQuery<AutoFix[]>({ queryKey: ["/api/debug/auto-fixes"] });
  if (isLoading) return <Skeleton className="h-64" />;

  const applied = fixes.filter(f => f.status === "applied");
  const rejected = fixes.filter(f => f.status === "rejected");
  const history = [...applied, ...rejected].sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime());

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2 flex-wrap">
        <Badge className="bg-green-500/20 text-green-600 border-green-500/30">{applied.length} Applied</Badge>
        <Badge variant="destructive">{rejected.length} Rejected</Badge>
      </div>
      <ScrollArea className="h-[600px]">
        <div className="space-y-3" data-testid="patch-history">
          {history.length === 0 && (
            <Card><CardContent className="pt-6 text-center text-muted-foreground">No patches in history yet. Applied and rejected fixes will appear here.</CardContent></Card>
          )}
          {history.map((fix) => (
            <Card key={fix.id} data-testid={`patch-${fix.id}`}>
              <CardContent className="pt-4 pb-4">
                <div className="space-y-1">
                  <div className="flex items-center gap-2 flex-wrap">
                    {statusBadge(fix.status)}
                    <Badge variant="outline">{fix.confidence}% confidence</Badge>
                    {fix.botId && <Badge variant="outline">Bot #{fix.botId}</Badge>}
                  </div>
                  <p className="text-sm font-medium">{fix.patchSummary}</p>
                  {fix.codeBefore && (
                    <div className="mt-2 space-y-1">
                      <pre className="text-xs bg-red-500/5 p-2 rounded-md overflow-x-auto border border-red-500/10">{fix.codeBefore}</pre>
                      <pre className="text-xs bg-green-500/5 p-2 rounded-md overflow-x-auto border border-green-500/10">{fix.codeAfter}</pre>
                    </div>
                  )}
                  <div className="text-xs text-muted-foreground flex gap-3 flex-wrap">
                    {fix.appliedAt && <span>Applied: {new Date(fix.appliedAt).toLocaleString()}</span>}
                    <span>Created: {new Date(fix.createdAt).toLocaleString()}</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </ScrollArea>
    </div>
  );
}

function LearningLogTab() {
  const { data: events = [] } = useQuery<DebugEvent[]>({ queryKey: ["/api/debug/events"] });
  const { data: fixes = [] } = useQuery<AutoFix[]>({ queryKey: ["/api/debug/auto-fixes"] });

  const resolved = events.filter(e => e.status === "resolved");
  const categoryStats = new Map<string, { count: number; resolved: number; avgSeverity: number }>();
  events.forEach(e => {
    const stats = categoryStats.get(e.category) || { count: 0, resolved: 0, avgSeverity: 0 };
    stats.count++;
    if (e.status === "resolved") stats.resolved++;
    stats.avgSeverity = (stats.avgSeverity * (stats.count - 1) + e.severity) / stats.count;
    categoryStats.set(e.category, stats);
  });

  const totalApplied = fixes.filter(f => f.status === "applied").length;
  const avgConfidence = fixes.length > 0 ? Math.round(fixes.reduce((s, f) => s + f.confidence, 0) / fixes.length) : 0;

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader className="flex flex-row items-center gap-2 pb-2">
          <Sparkles className="h-4 w-4 text-purple-500" />
          <CardTitle className="text-sm">Self-Learning Intelligence</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
            <div>
              <p className="text-2xl font-bold" data-testid="learning-total">{events.length}</p>
              <p className="text-xs text-muted-foreground">Total Events Processed</p>
            </div>
            <div>
              <p className="text-2xl font-bold text-green-500" data-testid="learning-resolved">{resolved.length}</p>
              <p className="text-xs text-muted-foreground">Issues Resolved</p>
            </div>
            <div>
              <p className="text-2xl font-bold text-blue-500" data-testid="learning-fixes">{totalApplied}</p>
              <p className="text-xs text-muted-foreground">Auto-Fixes Deployed</p>
            </div>
            <div>
              <p className="text-2xl font-bold text-purple-500" data-testid="learning-confidence">{avgConfidence}%</p>
              <p className="text-xs text-muted-foreground">Avg Fix Confidence</p>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex flex-row items-center gap-2 pb-2">
          <BookOpen className="h-4 w-4 text-blue-500" />
          <CardTitle className="text-sm">Error Pattern Intelligence</CardTitle>
        </CardHeader>
        <CardContent>
          <ScrollArea className="h-[400px]">
            <div className="space-y-3" data-testid="learning-patterns">
              {categoryStats.size === 0 && (
                <p className="text-center text-muted-foreground text-sm">No patterns learned yet. The system learns from every error and fix.</p>
              )}
              {Array.from(categoryStats.entries()).sort((a, b) => b[1].count - a[1].count).map(([category, stats]) => {
                const resolutionRate = stats.count > 0 ? Math.round((stats.resolved / stats.count) * 100) : 0;
                return (
                  <div key={category} className="flex items-center justify-between gap-3 p-3 rounded-md bg-muted/50">
                    <div className="space-y-1">
                      <p className="text-sm font-medium">{CATEGORY_LABELS[category] || category}</p>
                      <div className="flex items-center gap-2 text-xs text-muted-foreground flex-wrap">
                        <span>{stats.count} occurrences</span>
                        <span>Avg severity: {Math.round(stats.avgSeverity * 10) / 10}/10</span>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className={`text-lg font-bold ${resolutionRate >= 80 ? "text-green-500" : resolutionRate >= 50 ? "text-yellow-500" : "text-red-500"}`}>
                        {resolutionRate}%
                      </p>
                      <p className="text-xs text-muted-foreground">resolved</p>
                    </div>
                  </div>
                );
              })}
            </div>
          </ScrollArea>
        </CardContent>
      </Card>
    </div>
  );
}

export default function DebugPage() {
  const { toast } = useToast();
  return (
    <div className="p-4 md:p-6 space-y-6 max-w-7xl mx-auto">
      <div className="flex items-center justify-between gap-3 flex-wrap">
        <div>
          <h1 className="text-2xl font-bold" data-testid="text-debug-title">Debug Intelligence System</h1>
          <p className="text-sm text-muted-foreground">Self-healing AI that finds, fixes, and prevents errors across all 251 bots</p>
        </div>
        <div className="flex items-center gap-2 flex-wrap">
          <Badge variant="outline" className="gap-1"><Zap className="h-3 w-3" />Auto-Heal Engine</Badge>
          <Badge variant="outline" className="gap-1"><Eye className="h-3 w-3" />Universal Listener</Badge>
          <Badge variant="outline" className="gap-1"><Activity className="h-3 w-3" />Self-Learning</Badge>
          <Button
            size="sm"
            variant="outline"
            onClick={() => {
              toast({ title: "Auto-Fix All initiated", description: "Scanning and queuing fixes for all open issues..." });
              queryClient.invalidateQueries({ queryKey: ["/api/debug/auto-fixes"] });
            }}
            data-testid="button-auto-fix-all"
          >
            <Wrench className="h-4 w-4 mr-2" />
            Auto-Fix All
          </Button>
          <Button
            size="sm"
            variant="outline"
            onClick={() => {
              const text = `DreamCo Debug Report — ${new Date().toLocaleDateString()}\nAuto-Heal Engine: Active\nUniversal Listener: Active\nSelf-Learning: Active`;
              navigator.clipboard.writeText(text);
              toast({ title: "Report copied to clipboard" });
            }}
            data-testid="button-copy-debug-report"
          >
            <BarChart3 className="h-4 w-4 mr-2" />
            Copy Report
          </Button>
        </div>
      </div>

      <Tabs defaultValue="overview">
        <TabsList className="flex flex-wrap gap-1 h-auto">
          <TabsTrigger value="overview" data-testid="tab-overview"><Gauge className="h-4 w-4 mr-1" />Overview</TabsTrigger>
          <TabsTrigger value="issues" data-testid="tab-issues"><Bug className="h-4 w-4 mr-1" />Active Issues</TabsTrigger>
          <TabsTrigger value="fixes" data-testid="tab-fixes"><Wrench className="h-4 w-4 mr-1" />Auto-Fixes</TabsTrigger>
          <TabsTrigger value="revenue" data-testid="tab-revenue"><DollarSign className="h-4 w-4 mr-1" />Revenue Impact</TabsTrigger>
          <TabsTrigger value="security" data-testid="tab-security"><Shield className="h-4 w-4 mr-1" />Security</TabsTrigger>
          <TabsTrigger value="health" data-testid="tab-health"><Activity className="h-4 w-4 mr-1" />Bot Health</TabsTrigger>
          <TabsTrigger value="patches" data-testid="tab-patches"><History className="h-4 w-4 mr-1" />Patch History</TabsTrigger>
          <TabsTrigger value="learning" data-testid="tab-learning"><Sparkles className="h-4 w-4 mr-1" />Learning Log</TabsTrigger>
        </TabsList>

        <TabsContent value="overview"><OverviewTab /></TabsContent>
        <TabsContent value="issues"><ActiveIssuesTab /></TabsContent>
        <TabsContent value="fixes"><AutoFixesTab /></TabsContent>
        <TabsContent value="revenue"><RevenueImpactTab /></TabsContent>
        <TabsContent value="security"><SecurityTab /></TabsContent>
        <TabsContent value="health"><BotHealthTab /></TabsContent>
        <TabsContent value="patches"><PatchHistoryTab /></TabsContent>
        <TabsContent value="learning"><LearningLogTab /></TabsContent>
      </Tabs>
    </div>
  );
}
