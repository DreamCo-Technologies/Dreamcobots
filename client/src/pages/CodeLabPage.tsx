import { useState } from "react";
import Seo from "@/components/Seo";
import AppShell from "@/components/AppShell";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Progress } from "@/components/ui/progress";
import {
  Activity,
  AlertTriangle,
  ArrowUpRight,
  BookOpen,
  Braces,
  CheckCircle2,
  Clock,
  Code2,
  FileCode2,
  FileSearch,
  GitBranch,
  Key,
  Lock,
  Package,
  RefreshCw,
  Rocket,
  RotateCcw,
  Server,
  Shield,
  ShieldCheck,
  Sparkles,
  Terminal,
  TrendingUp,
  XCircle,
  Zap,
  Database,
  KeyRound,
  Eye,
  CalendarClock,
} from "lucide-react";

const HEADER_STATS = [
  { label: "Projects Active", value: "47", icon: Code2, color: "text-primary" },
  { label: "Lines Analyzed", value: "2.4M", icon: FileSearch, color: "text-violet-500" },
  { label: "Deployments Today", value: "18", icon: Rocket, color: "text-green-500" },
  { label: "AI Assists", value: "1,293", icon: Sparkles, color: "text-yellow-500" },
];

const ACTIVE_SESSIONS = [
  { id: 1, name: "dreamco-dashboard", language: "TypeScript", status: "active", lastEdit: "2 min ago", lines: 1240 },
  { id: 2, name: "api-gateway-v3", language: "Go", status: "active", lastEdit: "5 min ago", lines: 890 },
  { id: 3, name: "ml-pipeline", language: "Python", status: "paused", lastEdit: "18 min ago", lines: 3200 },
  { id: 4, name: "mobile-auth-sdk", language: "Kotlin", status: "active", lastEdit: "1 min ago", lines: 560 },
  { id: 5, name: "data-viz-lib", language: "Rust", status: "idle", lastEdit: "45 min ago", lines: 2100 },
];

const SUPPORTED_LANGUAGES = [
  "TypeScript", "JavaScript", "Python", "Go", "Rust", "Java", "Kotlin", "Swift",
  "C++", "C#", "Ruby", "PHP", "Dart", "Scala", "Elixir", "Haskell",
  "Lua", "R", "Julia", "Zig", "SQL", "GraphQL", "Solidity", "YAML",
];

const CODE_QUALITY_METRICS = [
  { label: "Syntax Accuracy", value: 98.2 },
  { label: "Logic Correctness", value: 94.7 },
  { label: "Style Compliance", value: 97.1 },
  { label: "Test Coverage", value: 89.3 },
];

const SCAN_ISSUES = [
  { severity: "critical", count: 3, color: "text-red-500" },
  { severity: "warning", count: 12, color: "text-yellow-500" },
  { severity: "info", count: 27, color: "text-blue-500" },
];

const SUPPORTED_FILE_TYPES = [
  ".ts", ".tsx", ".js", ".jsx", ".py", ".go", ".rs", ".java",
  ".kt", ".swift", ".cpp", ".cs", ".rb", ".php", ".dart", ".json",
  ".yaml", ".toml", ".sql", ".graphql", ".sol", ".md", ".html", ".css",
];

const DEPLOYMENTS = [
  { id: 1, name: "dreamco-web", env: "production", status: "deployed", time: "12 min ago", version: "v3.4.1" },
  { id: 2, name: "api-service", env: "staging", status: "building", time: "2 min ago", version: "v2.9.0-rc1" },
  { id: 3, name: "worker-queue", env: "production", status: "deployed", time: "1 hr ago", version: "v1.8.3" },
  { id: 4, name: "auth-gateway", env: "production", status: "failed", time: "35 min ago", version: "v4.0.0-beta" },
  { id: 5, name: "analytics-svc", env: "staging", status: "deployed", time: "4 hr ago", version: "v2.1.0" },
  { id: 6, name: "ml-inference", env: "development", status: "building", time: "8 min ago", version: "v0.5.2" },
];

const SECRET_TYPES = [
  { title: "API Keys", count: 24, icon: Key, rotationDays: 30, lastAccess: "2 min ago" },
  { title: "Database Credentials", count: 8, icon: Database, rotationDays: 90, lastAccess: "15 min ago" },
  { title: "OAuth Tokens", count: 12, icon: ShieldCheck, rotationDays: 14, lastAccess: "1 hr ago" },
  { title: "Encryption Keys", count: 6, icon: Lock, rotationDays: 180, lastAccess: "3 hr ago" },
];

const ACCESS_LOGS = [
  { user: "deploy-bot", secret: "STRIPE_SECRET_KEY", action: "read", time: "2 min ago" },
  { user: "ci-pipeline", secret: "DATABASE_URL", action: "read", time: "5 min ago" },
  { user: "admin", secret: "OPENAI_API_KEY", action: "rotate", time: "1 hr ago" },
  { user: "deploy-bot", secret: "AWS_ACCESS_KEY", action: "read", time: "2 hr ago" },
  { user: "ci-pipeline", secret: "GITHUB_TOKEN", action: "read", time: "3 hr ago" },
];

function getStatusBadge(status: string) {
  switch (status) {
    case "active":
      return <Badge variant="default" className="rounded-full"><Activity className="h-3 w-3 mr-1" />Active</Badge>;
    case "paused":
      return <Badge variant="secondary" className="rounded-full"><Clock className="h-3 w-3 mr-1" />Paused</Badge>;
    case "idle":
      return <Badge variant="outline" className="rounded-full"><Clock className="h-3 w-3 mr-1" />Idle</Badge>;
    case "deployed":
      return <Badge variant="default" className="rounded-full"><CheckCircle2 className="h-3 w-3 mr-1" />Deployed</Badge>;
    case "building":
      return <Badge variant="secondary" className="rounded-full"><RefreshCw className="h-3 w-3 mr-1 animate-spin" />Building</Badge>;
    case "failed":
      return <Badge variant="destructive" className="rounded-full"><XCircle className="h-3 w-3 mr-1" />Failed</Badge>;
    default:
      return <Badge variant="outline" className="rounded-full">{status}</Badge>;
  }
}

export default function CodeLabPage() {
  const [botSlug, setBotSlug] = useState<string | undefined>(undefined);

  const totalSecrets = SECRET_TYPES.reduce((s, t) => s + t.count, 0);

  return (
    <AppShell selectedBotSlug={botSlug} onBotChange={setBotSlug}>
      <Seo title="Code Lab - DreamCodeLab" description="Vibe coding, code reading, and AI development tools for DreamCo." />

      <div className="buddy-card buddy-noise buddy-appear overflow-hidden">
        <div className="px-5 pt-6 pb-5 md:px-8 md:pt-8 md:pb-6 border-b border-border/60">
          <div className="flex flex-wrap items-center justify-between gap-4">
            <div>
              <h1 className="text-2xl md:text-3xl" data-testid="text-codelab-title">Code Lab</h1>
              <p className="text-sm text-muted-foreground mt-1">Vibe coding, code reading & AI development tools</p>
            </div>
            <div className="flex items-center gap-3 flex-wrap">
              <Badge variant="secondary" className="rounded-full">
                <Terminal className="h-3 w-3 mr-1.5 text-primary" />
                DreamCodeLab
              </Badge>
              <Badge variant="secondary" className="rounded-full">
                <Activity className="h-3 w-3 mr-1.5 text-green-500" />
                Online
              </Badge>
            </div>
          </div>
        </div>

        <div className="p-5 md:p-8 space-y-8 buddy-stagger">
          <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
            {HEADER_STATS.map((stat) => (
              <Card key={stat.label} data-testid={`stat-${stat.label.toLowerCase().replace(/\s+/g, "-")}`}>
                <CardHeader className="flex flex-row items-center justify-between gap-1 space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium text-muted-foreground">{stat.label}</CardTitle>
                  <stat.icon className={`h-4 w-4 ${stat.color}`} />
                </CardHeader>
                <CardContent>
                  <p className="text-3xl font-bold tracking-tight">{stat.value}</p>
                </CardContent>
              </Card>
            ))}
          </div>

          <Tabs defaultValue="vibe-code" data-testid="tabs-codelab">
            <TabsList className="flex flex-wrap gap-1" data-testid="tabslist-codelab">
              <TabsTrigger value="vibe-code" data-testid="tab-vibe-code">
                <Sparkles className="h-4 w-4 mr-1.5" />Vibe Code
              </TabsTrigger>
              <TabsTrigger value="code-reader" data-testid="tab-code-reader">
                <BookOpen className="h-4 w-4 mr-1.5" />Code Reader
              </TabsTrigger>
              <TabsTrigger value="deploy" data-testid="tab-deploy">
                <Rocket className="h-4 w-4 mr-1.5" />Deploy
              </TabsTrigger>
              <TabsTrigger value="secrets" data-testid="tab-secrets">
                <Shield className="h-4 w-4 mr-1.5" />Secrets
              </TabsTrigger>
            </TabsList>

            <TabsContent value="vibe-code" className="space-y-6 mt-6">
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <Card data-testid="stat-code-generated">
                  <CardHeader className="flex flex-row items-center justify-between gap-1 space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium text-muted-foreground">Code Generated Today</CardTitle>
                    <Braces className="h-4 w-4 text-primary" />
                  </CardHeader>
                  <CardContent>
                    <p className="text-2xl font-bold">12,847</p>
                    <p className="text-xs text-muted-foreground mt-1">lines across 47 projects</p>
                  </CardContent>
                </Card>
                <Card data-testid="stat-ai-completions">
                  <CardHeader className="flex flex-row items-center justify-between gap-1 space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium text-muted-foreground">AI Completions</CardTitle>
                    <Zap className="h-4 w-4 text-yellow-500" />
                  </CardHeader>
                  <CardContent>
                    <p className="text-2xl font-bold">3,412</p>
                    <p className="text-xs text-green-600 dark:text-green-400 mt-1 flex items-center gap-1">
                      <TrendingUp className="h-3 w-3" /> 94.2% acceptance rate
                    </p>
                  </CardContent>
                </Card>
                <Card data-testid="stat-pair-sessions">
                  <CardHeader className="flex flex-row items-center justify-between gap-1 space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium text-muted-foreground">Pair Sessions</CardTitle>
                    <Terminal className="h-4 w-4 text-violet-500" />
                  </CardHeader>
                  <CardContent>
                    <p className="text-2xl font-bold">23</p>
                    <p className="text-xs text-muted-foreground mt-1">5 currently active</p>
                  </CardContent>
                </Card>
              </div>

              <div>
                <h3 className="text-base font-semibold mb-3" data-testid="text-active-sessions">Active Sessions</h3>
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                  {ACTIVE_SESSIONS.map((session) => (
                    <Card key={session.id} data-testid={`session-card-${session.id}`}>
                      <CardContent className="p-4">
                        <div className="flex items-start justify-between gap-3">
                          <div className="min-w-0">
                            <p className="text-sm font-semibold truncate">{session.name}</p>
                            <div className="flex items-center gap-2 mt-1 flex-wrap">
                              <Badge variant="outline" className="rounded-full text-[10px]">{session.language}</Badge>
                              {getStatusBadge(session.status)}
                            </div>
                          </div>
                          <FileCode2 className="h-4 w-4 text-muted-foreground flex-shrink-0 mt-0.5" />
                        </div>
                        <div className="mt-3 flex items-center justify-between gap-2 text-xs text-muted-foreground">
                          <span>{session.lines.toLocaleString()} lines</span>
                          <span>{session.lastEdit}</span>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </div>

              <div>
                <h3 className="text-base font-semibold mb-3" data-testid="text-supported-languages">Supported Languages</h3>
                <div className="flex flex-wrap gap-2">
                  {SUPPORTED_LANGUAGES.map((lang) => (
                    <Badge key={lang} variant="outline" className="rounded-full" data-testid={`lang-badge-${lang.toLowerCase()}`}>
                      {lang}
                    </Badge>
                  ))}
                </div>
              </div>

              <div>
                <h3 className="text-base font-semibold mb-3" data-testid="text-quality-metrics">Code Generation Quality</h3>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  {CODE_QUALITY_METRICS.map((metric) => (
                    <Card key={metric.label} data-testid={`metric-${metric.label.toLowerCase().replace(/\s+/g, "-")}`}>
                      <CardContent className="p-4">
                        <div className="flex items-center justify-between gap-2 mb-2">
                          <p className="text-sm font-medium">{metric.label}</p>
                          <p className="text-sm font-bold">{metric.value}%</p>
                        </div>
                        <Progress value={metric.value} className="h-2" />
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </div>
            </TabsContent>

            <TabsContent value="code-reader" className="space-y-6 mt-6">
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                <Card data-testid="stat-files-analyzed">
                  <CardHeader className="flex flex-row items-center justify-between gap-1 space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium text-muted-foreground">Files Analyzed</CardTitle>
                    <FileSearch className="h-4 w-4 text-primary" />
                  </CardHeader>
                  <CardContent>
                    <p className="text-2xl font-bold">8,492</p>
                  </CardContent>
                </Card>
                <Card data-testid="stat-code-quality">
                  <CardHeader className="flex flex-row items-center justify-between gap-1 space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium text-muted-foreground">Code Quality Score</CardTitle>
                    <CheckCircle2 className="h-4 w-4 text-green-500" />
                  </CardHeader>
                  <CardContent>
                    <p className="text-2xl font-bold">A-</p>
                    <p className="text-xs text-green-600 dark:text-green-400 mt-1">Top 15% of scanned repos</p>
                  </CardContent>
                </Card>
                <Card data-testid="stat-security-vulns">
                  <CardHeader className="flex flex-row items-center justify-between gap-1 space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium text-muted-foreground">Security Vulnerabilities</CardTitle>
                    <AlertTriangle className="h-4 w-4 text-yellow-500" />
                  </CardHeader>
                  <CardContent>
                    <p className="text-2xl font-bold">7</p>
                    <p className="text-xs text-muted-foreground mt-1">3 critical, 4 moderate</p>
                  </CardContent>
                </Card>
                <Card data-testid="stat-tech-debt">
                  <CardHeader className="flex flex-row items-center justify-between gap-1 space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium text-muted-foreground">Tech Debt</CardTitle>
                    <Clock className="h-4 w-4 text-orange-500" />
                  </CardHeader>
                  <CardContent>
                    <p className="text-2xl font-bold">42h</p>
                    <p className="text-xs text-muted-foreground mt-1">Estimated remediation</p>
                  </CardContent>
                </Card>
              </div>

              <Card data-testid="card-scan-results">
                <CardHeader className="flex flex-row items-center justify-between gap-2 space-y-0">
                  <CardTitle className="text-base flex items-center gap-2">
                    <FileSearch className="h-5 w-5 text-primary" />
                    Scan Results
                  </CardTitle>
                  <Button size="sm" data-testid="button-rescan">
                    <RefreshCw className="h-4 w-4 mr-1.5" />Re-scan
                  </Button>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {SCAN_ISSUES.map((issue) => (
                      <div key={issue.severity} className="flex items-center justify-between gap-3 p-3 rounded-lg border border-border/40">
                        <div className="flex items-center gap-3">
                          <AlertTriangle className={`h-4 w-4 ${issue.color}`} />
                          <span className="text-sm font-medium capitalize">{issue.severity}</span>
                        </div>
                        <Badge variant="outline" className="rounded-full">{issue.count} issues</Badge>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              <div>
                <h3 className="text-base font-semibold mb-3" data-testid="text-supported-filetypes">Supported File Types</h3>
                <div className="flex flex-wrap gap-2">
                  {SUPPORTED_FILE_TYPES.map((ft) => (
                    <Badge key={ft} variant="outline" className="rounded-full font-mono text-xs" data-testid={`filetype-badge-${ft.replace(".", "")}`}>
                      {ft}
                    </Badge>
                  ))}
                </div>
              </div>
            </TabsContent>

            <TabsContent value="deploy" className="space-y-6 mt-6">
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <Card data-testid="stat-total-deployments">
                  <CardHeader className="flex flex-row items-center justify-between gap-1 space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium text-muted-foreground">Total Deployments</CardTitle>
                    <Package className="h-4 w-4 text-primary" />
                  </CardHeader>
                  <CardContent>
                    <p className="text-2xl font-bold">1,847</p>
                    <p className="text-xs text-muted-foreground mt-1">All time</p>
                  </CardContent>
                </Card>
                <Card data-testid="stat-success-rate">
                  <CardHeader className="flex flex-row items-center justify-between gap-1 space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium text-muted-foreground">Success Rate</CardTitle>
                    <CheckCircle2 className="h-4 w-4 text-green-500" />
                  </CardHeader>
                  <CardContent>
                    <p className="text-2xl font-bold">97.8%</p>
                    <p className="text-xs text-green-600 dark:text-green-400 mt-1 flex items-center gap-1">
                      <TrendingUp className="h-3 w-3" /> +1.2% this week
                    </p>
                  </CardContent>
                </Card>
                <Card data-testid="stat-avg-build-time">
                  <CardHeader className="flex flex-row items-center justify-between gap-1 space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium text-muted-foreground">Avg Build Time</CardTitle>
                    <Clock className="h-4 w-4 text-violet-500" />
                  </CardHeader>
                  <CardContent>
                    <p className="text-2xl font-bold">2m 14s</p>
                    <p className="text-xs text-muted-foreground mt-1">Across all environments</p>
                  </CardContent>
                </Card>
              </div>

              <div>
                <h3 className="text-base font-semibold mb-3" data-testid="text-active-deployments">Active Deployments</h3>
                <div className="space-y-2">
                  {DEPLOYMENTS.map((dep) => (
                    <Card key={dep.id} data-testid={`deploy-card-${dep.id}`}>
                      <CardContent className="p-4">
                        <div className="flex items-center justify-between gap-3">
                          <div className="flex items-center gap-3 min-w-0">
                            <Server className="h-4 w-4 text-muted-foreground flex-shrink-0" />
                            <div className="min-w-0">
                              <p className="text-sm font-semibold truncate">{dep.name}</p>
                              <div className="flex items-center gap-2 mt-0.5 flex-wrap">
                                <span className="text-xs text-muted-foreground">{dep.version}</span>
                                <Badge variant="outline" className="rounded-full text-[10px]">{dep.env}</Badge>
                              </div>
                            </div>
                          </div>
                          <div className="flex items-center gap-3 flex-shrink-0">
                            <span className="text-xs text-muted-foreground hidden sm:inline">{dep.time}</span>
                            {getStatusBadge(dep.status)}
                            {dep.status === "deployed" && (
                              <Button size="sm" variant="outline" data-testid={`button-rollback-${dep.id}`}>
                                <RotateCcw className="h-3 w-3 mr-1" />Rollback
                              </Button>
                            )}
                            {dep.status === "failed" && (
                              <Button size="sm" data-testid={`button-retry-${dep.id}`}>
                                <RefreshCw className="h-3 w-3 mr-1" />Retry
                              </Button>
                            )}
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </div>

              <Card data-testid="card-deploy-frequency">
                <CardHeader>
                  <CardTitle className="text-base flex items-center gap-2">
                    <GitBranch className="h-5 w-5 text-primary" />
                    Deployment Frequency (Last 7 Days)
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex items-end gap-2 h-32">
                    {[12, 8, 15, 22, 18, 9, 14].map((val, i) => {
                      const days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];
                      return (
                        <div key={i} className="flex-1 flex flex-col items-center gap-1">
                          <div
                            className="w-full bg-primary/20 dark:bg-primary/30 rounded-md"
                            style={{ height: `${(val / 22) * 100}%` }}
                          />
                          <span className="text-[10px] text-muted-foreground">{days[i]}</span>
                        </div>
                      );
                    })}
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="secrets" className="space-y-6 mt-6">
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <Card data-testid="stat-total-secrets">
                  <CardHeader className="flex flex-row items-center justify-between gap-1 space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium text-muted-foreground">Total Secrets</CardTitle>
                    <KeyRound className="h-4 w-4 text-primary" />
                  </CardHeader>
                  <CardContent>
                    <p className="text-2xl font-bold">{totalSecrets}</p>
                    <p className="text-xs text-muted-foreground mt-1">Across 4 categories</p>
                  </CardContent>
                </Card>
                <Card data-testid="stat-next-rotation">
                  <CardHeader className="flex flex-row items-center justify-between gap-1 space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium text-muted-foreground">Next Rotation</CardTitle>
                    <CalendarClock className="h-4 w-4 text-orange-500" />
                  </CardHeader>
                  <CardContent>
                    <p className="text-2xl font-bold">3 days</p>
                    <p className="text-xs text-muted-foreground mt-1">OAuth tokens (12 keys)</p>
                  </CardContent>
                </Card>
                <Card data-testid="stat-access-events">
                  <CardHeader className="flex flex-row items-center justify-between gap-1 space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium text-muted-foreground">Access Events (24h)</CardTitle>
                    <Eye className="h-4 w-4 text-violet-500" />
                  </CardHeader>
                  <CardContent>
                    <p className="text-2xl font-bold">284</p>
                    <p className="text-xs text-green-600 dark:text-green-400 mt-1">All authorized</p>
                  </CardContent>
                </Card>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {SECRET_TYPES.map((st) => (
                  <Card key={st.title} data-testid={`secret-type-${st.title.toLowerCase().replace(/\s+/g, "-")}`}>
                    <CardContent className="p-4">
                      <div className="flex items-start justify-between gap-3">
                        <div className="flex items-center gap-3">
                          <div className="h-9 w-9 rounded-lg bg-primary/10 flex items-center justify-center flex-shrink-0">
                            <st.icon className="h-4 w-4 text-primary" />
                          </div>
                          <div>
                            <p className="text-sm font-semibold">{st.title}</p>
                            <p className="text-xs text-muted-foreground mt-0.5">{st.count} secrets stored</p>
                          </div>
                        </div>
                        <div className="text-right flex-shrink-0">
                          <Badge variant="outline" className="rounded-full text-[10px]">
                            <RefreshCw className="h-2.5 w-2.5 mr-1" />{st.rotationDays}d cycle
                          </Badge>
                        </div>
                      </div>
                      <div className="mt-3 text-xs text-muted-foreground flex items-center gap-1">
                        <Clock className="h-3 w-3" /> Last accessed {st.lastAccess}
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>

              <Card data-testid="card-access-logs">
                <CardHeader className="flex flex-row items-center justify-between gap-2 space-y-0">
                  <CardTitle className="text-base flex items-center gap-2">
                    <Eye className="h-5 w-5 text-primary" />
                    Recent Access Logs
                  </CardTitle>
                  <Button size="sm" variant="outline" data-testid="button-view-all-logs">
                    View All
                  </Button>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    {ACCESS_LOGS.map((log, i) => (
                      <div key={i} className="flex items-center justify-between gap-3 p-3 rounded-lg border border-border/40" data-testid={`access-log-${i}`}>
                        <div className="flex items-center gap-3 min-w-0">
                          <Shield className="h-4 w-4 text-muted-foreground flex-shrink-0" />
                          <div className="min-w-0">
                            <p className="text-sm font-medium truncate">{log.secret}</p>
                            <p className="text-xs text-muted-foreground">{log.user} - {log.action}</p>
                          </div>
                        </div>
                        <span className="text-xs text-muted-foreground flex-shrink-0">{log.time}</span>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>

          <Card data-testid="card-pricing-note">
            <CardContent className="p-4 flex items-center gap-3">
              <ArrowUpRight className="h-4 w-4 text-primary flex-shrink-0" />
              <p className="text-sm text-muted-foreground">
                Same fees as Replit - transparent and fair. No hidden costs for code generation, analysis, deployments, or secret management.
              </p>
            </CardContent>
          </Card>
        </div>
      </div>
    </AppShell>
  );
}
