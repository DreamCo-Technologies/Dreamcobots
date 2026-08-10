import { useMemo, useState } from "react";
import { Link } from "wouter";
import AppShell from "@/components/AppShell";
import Seo from "@/components/Seo";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Skeleton } from "@/components/ui/skeleton";
import { useToast } from "@/hooks/use-toast";
import { useMutation, useQuery } from "@tanstack/react-query";
import { apiRequest, queryClient } from "@/lib/queryClient";
import { cn } from "@/lib/utils";
import {
  Activity,
  AlertCircle,
  ArrowRight,
  Bot,
  BrainCircuit,
  Bug,
  CheckCircle2,
  Clock,
  Code,
  CreditCard,
  DollarSign,
  ExternalLink,
  FileCode,
  FolderOpen,
  Github,
  GitPullRequest,
  ImageIcon,
  ListTodo,
  Loader2,
  Play,
  RefreshCw,
  RotateCcw,
  Search,
  Shield,
  XCircle,
} from "lucide-react";
import ImageGeneratorPanel from "@/components/ImageGeneratorPanel";

type ActionTab = "agents" | "tasks" | "repository" | "integrations" | "ai-tools" | "debug";

type RevenueIntegration = {
  id: string;
  category: string;
  name: string;
  docs: string;
  botHint: string;
  purpose: string;
};

const REVENUE_INTEGRATIONS: RevenueIntegration[] = [
  { id: "fiverr", category: "Freelance", name: "Fiverr", docs: "https://developers.fiverr.com", botHint: "DreamSalesPro", purpose: "Research marketplace opportunities and prepare service listings where platform rules permit." },
  { id: "upwork", category: "Freelance", name: "Upwork", docs: "https://developers.upwork.com", botHint: "DreamSalesPro", purpose: "Research contracts and prepare proposals for user review; account access and platform permissions are required." },
  { id: "freelancer", category: "Freelance", name: "Freelancer.com", docs: "https://developers.freelancer.com", botHint: "DreamSalesPro", purpose: "Research freelance projects and prepare response workflows." },
  { id: "amazon", category: "Commerce", name: "Amazon Selling Partner", docs: "https://developer-docs.amazon.com/sp-api/", botHint: "DreamRetail", purpose: "Merchant-authorized catalog, order, inventory, and fulfillment integration planning." },
  { id: "ebay", category: "Commerce", name: "eBay", docs: "https://developer.ebay.com", botHint: "DreamRetail", purpose: "Merchant-authorized listing, order, inventory, and pricing workflows." },
  { id: "etsy", category: "Commerce", name: "Etsy", docs: "https://developers.etsy.com", botHint: "DreamContent", purpose: "Seller-authorized shop, listing, and order workflows." },
  { id: "shopify", category: "Commerce", name: "Shopify", docs: "https://shopify.dev/docs/api", botHint: "DreamBizLaunch", purpose: "Store administration, catalog, order, and customer workflows with merchant authorization." },
  { id: "walmart", category: "Commerce", name: "Walmart Marketplace", docs: "https://developer.walmart.com", botHint: "DreamRetail", purpose: "Marketplace catalog and order integration planning for approved sellers." },
  { id: "sam", category: "Government", name: "SAM.gov", docs: "https://open.gsa.gov/api/sam/", botHint: "DreamAdmin", purpose: "Research public contracting opportunities; no bid or certification claims are submitted automatically." },
  { id: "grants", category: "Government", name: "Grants.gov", docs: "https://www.grants.gov/applicants/applicant-system-to-system", botHint: "DreamAdmin", purpose: "Research grant opportunities and prepare application materials for review." },
  { id: "usaspending", category: "Government", name: "USAspending.gov", docs: "https://api.usaspending.gov/docs/", botHint: "DreamData", purpose: "Analyze public spending data for market intelligence." },
  { id: "census", category: "Government", name: "U.S. Census API", docs: "https://www.census.gov/data/developers.html", botHint: "DreamData", purpose: "Use public demographic and economic data for market research." },
  { id: "bls", category: "Government", name: "BLS Public Data API", docs: "https://www.bls.gov/developers/", botHint: "DreamData", purpose: "Use public labor data for workforce and market research." },
  { id: "coingecko", category: "Market Data", name: "CoinGecko", docs: "https://docs.coingecko.com", botHint: "DreamCrypto", purpose: "Market-data research and analytics. No trading is implied by selecting this integration." },
  { id: "coinbase", category: "Market Data", name: "Coinbase Developer Platform", docs: "https://docs.cdp.coinbase.com", botHint: "DreamCrypto", purpose: "Plan authenticated digital-asset workflows subject to account permissions and risk controls." },
  { id: "alpaca", category: "Market Data", name: "Alpaca", docs: "https://docs.alpaca.markets", botHint: "DreamFinance", purpose: "Market-data and broker integration planning; live trading requires explicit authorization and controls." },
  { id: "hud", category: "Real Estate", name: "HUD Developer Resources", docs: "https://www.hud.gov/program_offices/cio/developer-resources", botHint: "DreamRealEstate", purpose: "Public housing and market-data research." },
  { id: "attom", category: "Real Estate", name: "ATTOM", docs: "https://api.developer.attomdata.com", botHint: "DreamRealEstate", purpose: "Property-data integration planning; subscription or credentials may be required." },
  { id: "openai", category: "AI / SaaS", name: "OpenAI API", docs: "https://platform.openai.com/docs", botHint: "CommandCore", purpose: "Model integration planning and authenticated AI workflows." },
  { id: "rapidapi", category: "AI / SaaS", name: "RapidAPI", docs: "https://docs.rapidapi.com", botHint: "DreamAIInfra", purpose: "Discover third-party APIs and evaluate them before connection." },
  { id: "stripe", category: "Payments", name: "Stripe", docs: "https://docs.stripe.com/api", botHint: "DreamPayments", purpose: "Payment-provider adapter candidate. Processing fees and provider requirements remain separate from Buddy software." },
  { id: "square", category: "Payments", name: "Square", docs: "https://developer.squareup.com/docs", botHint: "DreamPayments", purpose: "POS and payment-provider adapter candidate subject to merchant onboarding and provider requirements." },
];

const INTEGRATION_CATEGORIES = ["All", ...Array.from(new Set(REVENUE_INTEGRATIONS.map((item) => item.category)))];

const TASK_STAT_STYLES = {
  total: "border-blue-500/20 bg-blue-500/5 text-blue-400",
  running: "border-green-500/20 bg-green-500/5 text-green-400",
  pending: "border-amber-500/20 bg-amber-500/5 text-amber-400",
  failed: "border-red-500/20 bg-red-500/5 text-red-400",
} as const;

function statusBadge(status: string) {
  if (status === "complete") return <Badge className="bg-green-500/15 text-green-400 border-green-500/30 text-[10px]"><CheckCircle2 className="h-3 w-3 mr-1" />Complete</Badge>;
  if (status === "running") return <Badge className="bg-blue-500/15 text-blue-400 border-blue-500/30 text-[10px]"><Loader2 className="h-3 w-3 mr-1 animate-spin" />Running</Badge>;
  if (status === "pending") return <Badge className="bg-amber-500/15 text-amber-400 border-amber-500/30 text-[10px]"><Clock className="h-3 w-3 mr-1" />Pending</Badge>;
  if (status === "failed") return <Badge className="bg-red-500/15 text-red-400 border-red-500/30 text-[10px]"><XCircle className="h-3 w-3 mr-1" />Failed</Badge>;
  if (status === "paused") return <Badge className="bg-slate-500/15 text-slate-400 border-slate-500/30 text-[10px]"><Shield className="h-3 w-3 mr-1" />Paused</Badge>;
  return <Badge variant="outline" className="text-[10px]">{status || "unknown"}</Badge>;
}

function QueryError({ title, onRetry }: { title: string; onRetry: () => void }) {
  return (
    <Card className="buddy-card rounded-2xl border border-amber-500/30 bg-amber-500/5 p-6 text-center">
      <AlertCircle className="h-7 w-7 text-amber-400 mx-auto mb-2" />
      <p className="font-medium text-sm">{title}</p>
      <p className="text-xs text-muted-foreground mt-1">This is an API or connection error, not an empty result.</p>
      <Button variant="outline" size="sm" className="mt-3 rounded-xl" onClick={onRetry}><RefreshCw className="h-3.5 w-3.5 mr-1.5" />Retry</Button>
    </Card>
  );
}

export default function ActionsPage() {
  const { toast } = useToast();
  const [activeTab, setActiveTab] = useState<ActionTab>("agents");
  const [botSearch, setBotSearch] = useState("");
  const [botDivision, setBotDivision] = useState("All");
  const [integrationCategory, setIntegrationCategory] = useState("All");
  const [integrationSearch, setIntegrationSearch] = useState("");
  const [selectedBotSlug, setSelectedBotSlug] = useState<string | undefined>();
  const [taskSearch, setTaskSearch] = useState("");
  const [activeTaskId, setActiveTaskId] = useState<number | null>(null);

  const botsQ = useQuery<any[]>({ queryKey: ["/api/bots"] });
  const tasksQ = useQuery<any[]>({ queryKey: ["/api/tasks"], refetchInterval: 10000 });
  const githubQ = useQuery<any>({ queryKey: ["/api/github/status"], retry: 1 });
  const pullsQ = useQuery<any>({ queryKey: ["/api/github/pulls"], retry: 1, enabled: activeTab === "repository" || activeTab === "debug" });
  const repoTreeQ = useQuery<any>({ queryKey: ["/api/github/repo-tree"], retry: 1, enabled: activeTab === "repository" });
  const workflowsQ = useQuery<any>({ queryKey: ["/api/github/workflows"], retry: 1, enabled: activeTab === "repository" || activeTab === "debug" });

  const bots: any[] = Array.isArray(botsQ.data) ? botsQ.data : [];
  const tasks: any[] = Array.isArray(tasksQ.data) ? tasksQ.data : [];
  const buddy = bots.find((bot: any) => bot.slug === "buddy-bot");
  const failedTasks = tasks.filter((task: any) => task.status === "failed");

  const divisions = useMemo(
    () => ["All", ...Array.from(new Set(bots.map((bot: any) => bot.division).filter(Boolean))).sort()],
    [bots],
  );

  const filteredBots = bots.filter((bot: any) => {
    const search = botSearch.trim().toLowerCase();
    return (botDivision === "All" || bot.division === botDivision)
      && (!search || bot.displayName?.toLowerCase().includes(search) || bot.division?.toLowerCase().includes(search));
  });

  const filteredTasks = tasks.filter((task: any) => {
    const search = taskSearch.trim().toLowerCase();
    return !search || task.objective?.toLowerCase().includes(search) || task.title?.toLowerCase().includes(search) || task.division?.toLowerCase().includes(search);
  });

  const filteredIntegrations = REVENUE_INTEGRATIONS.filter((item) => {
    const search = integrationSearch.trim().toLowerCase();
    return (integrationCategory === "All" || item.category === integrationCategory)
      && (!search || item.name.toLowerCase().includes(search) || item.purpose.toLowerCase().includes(search) || item.botHint.toLowerCase().includes(search));
  });

  const restartAll = useMutation({
    mutationFn: () => apiRequest("POST", "/api/tasks/restart-all", {}),
    onSuccess: (data: any) => {
      queryClient.invalidateQueries({ queryKey: ["/api/tasks"] });
      toast({ title: `Restarted ${data?.restarted ?? "all"} tasks`, description: "Task state has been reset by the server." });
    },
    onError: (error: any) => toast({ title: "Restart failed", description: error.message, variant: "destructive" }),
  });

  const restartTask = useMutation({
    mutationFn: async (id: number) => {
      setActiveTaskId(id);
      return apiRequest("POST", `/api/tasks/${id}/restart`, {});
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["/api/tasks"] });
      toast({ title: "Task restarted" });
    },
    onError: (error: any) => toast({ title: "Restart failed", description: error.message, variant: "destructive" }),
    onSettled: () => setActiveTaskId(null),
  });

  const runTask = useMutation({
    mutationFn: async (id: number) => {
      setActiveTaskId(id);
      return apiRequest("POST", `/api/tasks/${id}/run`, {});
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["/api/tasks"] });
      toast({ title: "Task run completed", description: "The task run endpoint returned successfully." });
    },
    onError: (error: any) => toast({ title: "Run failed", description: error.message, variant: "destructive" }),
    onSettled: () => setActiveTaskId(null),
  });

  const restartFailed = useMutation({
    mutationFn: async () => Promise.all(failedTasks.map((task: any) => apiRequest("POST", `/api/tasks/${task.id}/restart`, {}))),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["/api/tasks"] });
      toast({ title: `Restarted ${failedTasks.length} failed task${failedTasks.length === 1 ? "" : "s"}` });
    },
    onError: (error: any) => toast({ title: "Failed-task restart did not finish", description: error.message, variant: "destructive" }),
  });

  const pulls: any[] = (pullsQ.data as any)?.pullRequests ?? [];
  const repoInfo = (githubQ.data as any)?.repo;
  const repoFiles: any[] = (repoTreeQ.data as any)?.tree ?? [];
  const runs: any[] = (workflowsQ.data as any)?.runs ?? [];
  const githubConnected = (githubQ.data as any)?.connected === true;

  const tabs: { id: ActionTab; label: string; icon: any; count?: number }[] = [
    { id: "agents", label: "Agents", icon: Bot, count: bots.length },
    { id: "tasks", label: "Tasks", icon: ListTodo, count: tasks.length },
    { id: "repository", label: "Repository", icon: Github },
    { id: "integrations", label: "Revenue Integrations", icon: DollarSign, count: REVENUE_INTEGRATIONS.length },
    { id: "ai-tools", label: "AI Tools", icon: ImageIcon },
    { id: "debug", label: "Health & Fix", icon: Bug, count: failedTasks.length || undefined },
  ];

  const healthItems = [
    { label: "Bots API", ok: !botsQ.isError, detail: botsQ.isError ? "Request failed" : `${bots.length} profiles loaded` },
    { label: "Tasks API", ok: !tasksQ.isError, detail: tasksQ.isError ? "Request failed" : `${tasks.length} tasks loaded` },
    { label: "GitHub backend", ok: githubConnected, detail: githubConnected ? "Connected" : "Disconnected or token unavailable" },
    { label: "Buddy profile", ok: !!buddy, detail: buddy ? `${buddy.division ?? "CommandCore"}` : botsQ.isError ? "Bots API unavailable" : "Profile not returned" },
  ];

  return (
    <AppShell selectedBotSlug={selectedBotSlug} onBotChange={setSelectedBotSlug}>
      <Seo title="Actions Control Center — DreamCo Empire OS" description="Operate Buddy bots and tasks, inspect repository health, plan integrations, and diagnose failures." />
      <div className="buddy-appear space-y-6">
        <div className="flex flex-col md:flex-row md:items-end md:justify-between gap-4">
          <div>
            <h2 className="text-3xl md:text-4xl" data-testid="actions-title">Actions Control Center</h2>
            <p className="mt-1 text-muted-foreground">Operate bots and tasks, inspect repository health, plan integrations, and see what is actually connected.</p>
          </div>
          <div className="flex gap-2 flex-wrap">
            <Button variant="outline" className="rounded-xl" onClick={() => {
              queryClient.invalidateQueries({ queryKey: ["/api/bots"] });
              queryClient.invalidateQueries({ queryKey: ["/api/tasks"] });
              queryClient.invalidateQueries({ queryKey: ["/api/github/status"] });
              queryClient.invalidateQueries({ queryKey: ["/api/github/pulls"] });
              queryClient.invalidateQueries({ queryKey: ["/api/github/workflows"] });
            }}><RefreshCw className="h-4 w-4 mr-2" />Refresh status</Button>
            <Button className="rounded-xl" onClick={() => setSelectedBotSlug("buddy-bot")} disabled={!buddy}><BrainCircuit className="h-4 w-4 mr-2" />Open Buddy</Button>
          </div>
        </div>

        <Card className="buddy-card rounded-2xl border border-border/60 p-4">
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
            {healthItems.map((item) => (
              <div key={item.label} className="rounded-xl border border-border/50 bg-muted/20 p-3">
                <div className="flex items-center gap-2">
                  {item.ok ? <CheckCircle2 className="h-4 w-4 text-green-400" /> : <AlertCircle className="h-4 w-4 text-amber-400" />}
                  <span className="font-medium text-sm">{item.label}</span>
                </div>
                <p className="text-[11px] text-muted-foreground mt-1">{item.detail}</p>
              </div>
            ))}
          </div>
        </Card>

        <div className="flex gap-2 overflow-x-auto pb-1" data-testid="actions-tabs">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            return (
              <button key={tab.id} onClick={() => setActiveTab(tab.id)} className={cn("flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium border transition-all whitespace-nowrap", activeTab === tab.id ? "bg-primary text-primary-foreground border-primary" : "bg-card/60 border-border/60 text-muted-foreground hover:text-foreground")} data-testid={`tab-${tab.id}`}>
                <Icon className="h-4 w-4" />{tab.label}
                {tab.count !== undefined && <span className={cn("text-[10px] px-1.5 py-0.5 rounded-full font-mono", activeTab === tab.id ? "bg-white/20" : "bg-muted")}>{tab.count}</span>}
              </button>
            );
          })}
        </div>

        {activeTab === "agents" && (
          <div className="space-y-4">
            <div className="flex flex-col gap-3">
              <div className="relative"><Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" /><Input className="pl-9 rounded-xl" value={botSearch} onChange={(event) => setBotSearch(event.target.value)} placeholder="Search bots or divisions..." /></div>
              <div className="flex gap-2 flex-wrap max-h-32 overflow-y-auto">
                {divisions.map((division) => <button key={division} onClick={() => setBotDivision(division)} className={cn("px-3 py-1.5 rounded-lg text-xs border", botDivision === division ? "bg-primary text-primary-foreground border-primary" : "bg-card border-border/60 text-muted-foreground")}>{division}</button>)}
              </div>
            </div>
            {botsQ.isLoading ? <div className="grid md:grid-cols-2 xl:grid-cols-3 gap-3">{Array.from({ length: 9 }).map((_, index) => <Skeleton key={index} className="h-28 rounded-2xl" />)}</div>
              : botsQ.isError ? <QueryError title="Bots could not be loaded" onRetry={() => botsQ.refetch()} />
              : filteredBots.length === 0 ? <Card className="p-8 text-center rounded-2xl"><p className="text-sm text-muted-foreground">No bots match these filters.</p></Card>
              : <div className="grid md:grid-cols-2 xl:grid-cols-3 gap-3">{filteredBots.slice(0, 100).map((bot: any) => <Card key={bot.id} className={cn("buddy-card rounded-2xl border p-4", bot.slug === "buddy-bot" ? "border-primary/40 bg-primary/5" : "border-border/60")}>
                  <div className="flex items-start justify-between gap-2"><div className="min-w-0"><p className="font-semibold text-sm truncate">{bot.displayName}</p><p className="text-[10px] text-muted-foreground">{bot.division ?? "Unassigned"}</p></div><Badge variant="outline" className="text-[10px]">{bot.tier ?? "free"}</Badge></div>
                  <p className="text-[11px] text-muted-foreground line-clamp-2 mt-2 min-h-8">{bot.description || "No description supplied."}</p>
                  <div className="flex gap-2 mt-3"><Button size="sm" variant="outline" className="flex-1 rounded-lg" onClick={() => setSelectedBotSlug(bot.slug)}>Chat</Button><Link href={`/bot/${bot.id}`}><Button size="sm" className="rounded-lg">Profile</Button></Link></div>
                </Card>)}</div>}
            {filteredBots.length > 100 && <p className="text-xs text-muted-foreground text-center">Showing the first 100 matching bots. Use search or division filters to narrow the list.</p>}
          </div>
        )}

        {activeTab === "tasks" && (
          <div className="space-y-4">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              {[
                { label: "Total", value: tasks.length, style: TASK_STAT_STYLES.total },
                { label: "Running", value: tasks.filter((task) => task.status === "running").length, style: TASK_STAT_STYLES.running },
                { label: "Pending", value: tasks.filter((task) => task.status === "pending").length, style: TASK_STAT_STYLES.pending },
                { label: "Failed", value: failedTasks.length, style: TASK_STAT_STYLES.failed },
              ].map((stat) => <Card key={stat.label} className={cn("rounded-2xl border p-4 text-center", stat.style)}><p className="text-2xl font-black">{stat.value}</p><p className="text-xs mt-1 opacity-80">{stat.label}</p></Card>)}
            </div>
            <div className="flex flex-col sm:flex-row gap-3"><div className="relative flex-1"><Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" /><Input className="pl-9 rounded-xl" value={taskSearch} onChange={(event) => setTaskSearch(event.target.value)} placeholder="Search tasks..." /></div><Button variant="outline" className="rounded-xl" onClick={() => restartAll.mutate()} disabled={restartAll.isPending || tasks.length === 0}><RotateCcw className="h-4 w-4 mr-2" />Restart all</Button></div>
            {tasksQ.isLoading ? <div className="space-y-2">{Array.from({ length: 5 }).map((_, index) => <Skeleton key={index} className="h-20 rounded-2xl" />)}</div>
              : tasksQ.isError ? <QueryError title="Tasks could not be loaded" onRetry={() => tasksQ.refetch()} />
              : filteredTasks.length === 0 ? <Card className="p-8 text-center rounded-2xl"><p className="text-sm text-muted-foreground">No tasks found.</p><Link href="/orchestration"><Button className="mt-3 rounded-xl">Create task</Button></Link></Card>
              : <div className="space-y-2">{filteredTasks.map((task: any) => <Card key={task.id} className="buddy-card rounded-2xl border border-border/60 p-4"><div className="flex flex-col sm:flex-row sm:items-center gap-3"><div className="flex-1 min-w-0"><div className="flex gap-2 flex-wrap">{statusBadge(task.status)}{task.division && <Badge variant="outline" className="text-[10px]">{task.division}</Badge>}</div><p className="font-medium text-sm mt-1">{task.objective || task.title}</p><p className="text-[10px] text-muted-foreground mt-1">Task #{task.id} · priority {task.priority ?? "—"}</p></div><div className="flex gap-2"><Button size="sm" variant="outline" className="rounded-lg" onClick={() => restartTask.mutate(task.id)} disabled={activeTaskId === task.id}><RotateCcw className="h-3.5 w-3.5 mr-1" />Restart</Button>{task.status !== "running" && <Button size="sm" className="rounded-lg" onClick={() => runTask.mutate(task.id)} disabled={activeTaskId === task.id}><Play className="h-3.5 w-3.5 mr-1" />Run</Button>}</div></div></Card>)}</div>}
            <div className="text-center"><Link href="/orchestration"><Button variant="outline" className="rounded-xl">Full Task Manager <ArrowRight className="h-4 w-4 ml-2" /></Button></Link></div>
          </div>
        )}

        {activeTab === "repository" && (
          <div className="space-y-4">
            <Card className="buddy-card rounded-2xl border border-border/60 p-5"><div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4"><div><p className="font-bold">{repoInfo?.name ?? "DreamCo-Technologies/Dreamcobots"}</p><p className="text-xs text-muted-foreground mt-1">Repository visibility and CI status. Write operations remain separately permission-gated.</p></div><div className="flex gap-2"><a href="https://github.com/DreamCo-Technologies/Dreamcobots" target="_blank" rel="noreferrer"><Button variant="outline" size="sm" className="rounded-xl"><Github className="h-3.5 w-3.5 mr-1.5" />Repository</Button></a><a href="https://github.com/DreamCo-Technologies/Dreamcobots/actions" target="_blank" rel="noreferrer"><Button variant="outline" size="sm" className="rounded-xl"><Activity className="h-3.5 w-3.5 mr-1.5" />GitHub Actions</Button></a></div></div></Card>
            {!githubConnected && !githubQ.isLoading && <QueryError title="GitHub backend is not connected" onRetry={() => githubQ.refetch()} />}
            <div className="grid lg:grid-cols-2 gap-4">
              <Card className="buddy-card rounded-2xl border border-border/60 p-5"><div className="flex items-center justify-between mb-3"><p className="font-semibold text-sm flex items-center gap-2"><GitPullRequest className="h-4 w-4" />Open pull requests</p><Button variant="ghost" size="sm" onClick={() => pullsQ.refetch()}><RefreshCw className="h-3.5 w-3.5" /></Button></div>{pullsQ.isLoading ? <Skeleton className="h-28 rounded-xl" /> : pullsQ.isError ? <p className="text-xs text-amber-400">Pull request status could not be loaded.</p> : pulls.length === 0 ? <p className="text-xs text-muted-foreground py-4 text-center">No open pull requests returned.</p> : <div className="space-y-2 max-h-80 overflow-y-auto">{pulls.map((pr: any) => <a key={pr.number ?? pr.id} href={pr.url ?? pr.html_url} target="_blank" rel="noreferrer" className="block rounded-xl border border-border/50 p-3 hover:bg-muted/30"><p className="text-sm font-medium truncate">{pr.title}</p><p className="text-[10px] text-muted-foreground">#{pr.number ?? pr.id} · {pr.state ?? "open"}</p></a>)}</div>}</Card>
              <Card className="buddy-card rounded-2xl border border-border/60 p-5"><div className="flex items-center justify-between mb-3"><p className="font-semibold text-sm flex items-center gap-2"><Activity className="h-4 w-4" />Recent workflow runs</p><Button variant="ghost" size="sm" onClick={() => workflowsQ.refetch()}><RefreshCw className="h-3.5 w-3.5" /></Button></div>{workflowsQ.isLoading ? <Skeleton className="h-28 rounded-xl" /> : workflowsQ.isError ? <p className="text-xs text-amber-400">Workflow status could not be loaded.</p> : runs.length === 0 ? <p className="text-xs text-muted-foreground py-4 text-center">No workflow runs returned.</p> : <div className="space-y-2 max-h-80 overflow-y-auto">{runs.slice(0, 12).map((run: any) => <a key={run.id} href={run.html_url} target="_blank" rel="noreferrer" className="flex items-center gap-2 rounded-xl border border-border/50 p-3 hover:bg-muted/30"><span className={cn("h-2.5 w-2.5 rounded-full", run.conclusion === "success" ? "bg-green-400" : run.conclusion === "failure" ? "bg-red-400" : run.status === "in_progress" ? "bg-amber-400 animate-pulse" : "bg-muted-foreground/50")} /><div className="min-w-0"><p className="text-sm font-medium truncate">{run.name}</p><p className="text-[10px] text-muted-foreground">{run.conclusion ?? run.status}</p></div></a>)}</div>}</Card>
            </div>
            <Card className="buddy-card rounded-2xl border border-border/60 p-5"><div className="flex items-center justify-between mb-3"><p className="font-semibold text-sm flex items-center gap-2"><FolderOpen className="h-4 w-4" />Repository files</p><Button variant="ghost" size="sm" onClick={() => repoTreeQ.refetch()}><RefreshCw className="h-3.5 w-3.5" /></Button></div>{repoTreeQ.isLoading ? <Skeleton className="h-36 rounded-xl" /> : repoTreeQ.isError ? <p className="text-xs text-amber-400">Repository tree could not be loaded.</p> : repoFiles.length === 0 ? <p className="text-xs text-muted-foreground text-center py-4">No repository tree returned.</p> : <div className="grid md:grid-cols-2 xl:grid-cols-3 gap-1 max-h-80 overflow-y-auto">{repoFiles.slice(0, 150).map((file: any) => <a key={file.path} href={file.html_url ?? `https://github.com/DreamCo-Technologies/Dreamcobots/blob/main/${file.path}`} target="_blank" rel="noreferrer" className="flex items-center gap-2 p-2 rounded-lg hover:bg-muted/30">{file.type === "tree" ? <FolderOpen className="h-3.5 w-3.5 text-amber-400" /> : <FileCode className="h-3.5 w-3.5 text-muted-foreground" />}<span className="text-xs truncate">{file.path}</span></a>)}</div>}</Card>
          </div>
        )}

        {activeTab === "integrations" && (
          <div className="space-y-4">
            <Card className="buddy-card rounded-2xl border border-primary/20 bg-primary/5 p-4"><p className="font-bold text-sm">Revenue integrations are references, not automatic connections</p><p className="text-xs text-muted-foreground mt-1">Selecting an integration opens Buddy for planning. External accounts, credentials, approvals, costs, legal requirements, and platform rules still apply. No revenue amount is guaranteed.</p></Card>
            <div className="flex flex-col gap-3"><div className="relative"><Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" /><Input className="pl-9 rounded-xl" placeholder="Search integrations..." value={integrationSearch} onChange={(event) => setIntegrationSearch(event.target.value)} /></div><div className="flex gap-2 flex-wrap">{INTEGRATION_CATEGORIES.map((category) => <button key={category} onClick={() => setIntegrationCategory(category)} className={cn("px-3 py-1.5 rounded-lg text-xs border", integrationCategory === category ? "bg-primary text-primary-foreground border-primary" : "bg-card border-border/60 text-muted-foreground")}>{category}</button>)}</div></div>
            <div className="grid md:grid-cols-2 xl:grid-cols-3 gap-3">{filteredIntegrations.map((item) => <Card key={item.id} className="buddy-card rounded-2xl border border-border/60 p-4"><div className="flex items-start justify-between gap-2"><div><p className="font-bold text-sm">{item.name}</p><Badge variant="outline" className="text-[9px] mt-1">{item.category}</Badge></div><a href={item.docs} target="_blank" rel="noreferrer"><Button variant="ghost" size="icon" className="h-7 w-7"><ExternalLink className="h-3.5 w-3.5" /></Button></a></div><p className="text-[11px] text-muted-foreground mt-3 min-h-12">{item.purpose}</p><div className="flex items-center justify-between gap-2 mt-3"><span className="text-[10px] text-muted-foreground flex items-center gap-1"><Bot className="h-3 w-3" />Suggested: {item.botHint}</span><Button size="sm" className="rounded-lg h-8 text-[11px]" onClick={() => { const suggested = bots.find((bot: any) => bot.division === item.botHint || bot.displayName?.includes(item.botHint)) || buddy; if (suggested) setSelectedBotSlug(suggested.slug); toast({ title: `Planning ${item.name}`, description: "Buddy opened for setup planning. This does not connect or authorize the external service." }); }} disabled={!buddy && bots.length === 0}>Plan with Buddy</Button></div></Card>)}</div>
          </div>
        )}

        {activeTab === "ai-tools" && <div className="space-y-4"><div><h3 className="text-lg font-semibold">AI Tools</h3><p className="text-sm text-muted-foreground">Media tools that are actually wired into this client.</p></div><div className="max-w-xl"><ImageGeneratorPanel /></div></div>}

        {activeTab === "debug" && (
          <div className="space-y-4">
            <Card className="buddy-card rounded-2xl border border-red-500/20 bg-red-500/5 p-5"><div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 mb-4"><div><p className="font-semibold text-sm text-red-400 flex items-center gap-2"><XCircle className="h-4 w-4" />Failed tasks <Badge className="bg-red-500/15 text-red-400 border-red-500/30 text-[10px]">{failedTasks.length}</Badge></p><p className="text-[11px] text-muted-foreground mt-1">This action restarts only failed tasks. It no longer resets healthy tasks.</p></div><Button size="sm" className="rounded-xl bg-red-600 text-white" onClick={() => restartFailed.mutate()} disabled={restartFailed.isPending || failedTasks.length === 0}>{restartFailed.isPending ? <Loader2 className="h-3.5 w-3.5 mr-1 animate-spin" /> : <RotateCcw className="h-3.5 w-3.5 mr-1" />}Restart failed only</Button></div>{tasksQ.isError ? <p className="text-xs text-amber-400">Tasks API unavailable; failure count is unknown.</p> : failedTasks.length === 0 ? <div className="text-center py-5"><CheckCircle2 className="h-7 w-7 text-green-400 mx-auto mb-2" /><p className="text-sm text-green-400">No failed tasks returned.</p></div> : <div className="space-y-2">{failedTasks.map((task: any) => <div key={task.id} className="flex items-center gap-3 rounded-xl border border-red-500/20 p-3"><div className="flex-1 min-w-0"><p className="text-sm font-medium truncate">{task.objective || task.title}</p><p className="text-[10px] text-muted-foreground">#{task.id} · {task.division ?? "Unassigned"}</p></div><Button size="sm" variant="outline" className="rounded-lg" onClick={() => restartTask.mutate(task.id)} disabled={activeTaskId === task.id}><RotateCcw className="h-3 w-3 mr-1" />Restart</Button></div>)}</div>}</Card>
            <Card className="buddy-card rounded-2xl border border-border/60 p-5"><p className="font-semibold text-sm mb-3">Connection truth</p><div className="space-y-2">{healthItems.map((item) => <div key={item.label} className="flex items-center gap-3 rounded-xl border border-border/50 bg-muted/20 p-3">{item.ok ? <CheckCircle2 className="h-4 w-4 text-green-400" /> : <AlertCircle className="h-4 w-4 text-amber-400" />}<div className="flex-1"><p className="text-sm font-medium">{item.label}</p><p className="text-[10px] text-muted-foreground">{item.detail}</p></div><Badge variant="outline" className="text-[10px]">{item.ok ? "OK" : "Needs attention"}</Badge></div>)}</div></Card>
            <div className="flex gap-3 flex-wrap"><Link href="/debug"><Button className="rounded-xl"><Bug className="h-4 w-4 mr-2" />Debug Intelligence</Button></Link><Link href="/bot-activity"><Button variant="outline" className="rounded-xl"><Activity className="h-4 w-4 mr-2" />Command Center</Button></Link><Link href="/sandbox"><Button variant="outline" className="rounded-xl"><Code className="h-4 w-4 mr-2" />Sandbox Factory</Button></Link></div>
          </div>
        )}
      </div>
    </AppShell>
  );
}
