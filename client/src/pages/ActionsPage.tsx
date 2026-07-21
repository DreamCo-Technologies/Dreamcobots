import { useState } from "react";
import { Link, useLocation } from "wouter";
import AppShell from "@/components/AppShell";
import Seo from "@/components/Seo";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Skeleton } from "@/components/ui/skeleton";
import { useToast } from "@/hooks/use-toast";
import { useQuery, useMutation } from "@tanstack/react-query";
import { apiRequest, queryClient } from "@/lib/queryClient";
import { cn } from "@/lib/utils";
import {
  Bot, BrainCircuit, Activity, RefreshCw, Play, RotateCcw, Github,
  GitPullRequest, FolderOpen, FileCode, ExternalLink, CheckCircle2,
  AlertCircle, Clock, Zap, DollarSign, ShoppingBag, Building2, Landmark,
  Search, Filter, ChevronRight, Loader2, XCircle, Globe, Package,
  Truck, TrendingUp, Shield, Code, Store, CreditCard, ListTodo,
  BarChart2, CheckCheck, Trash2, Plus, ArrowRight, Sparkles,
  Cpu, Network, Wallet, Bug, Users, GitBranch, Star, Eye, ImageIcon,
} from "lucide-react";
import ImageGeneratorPanel from "@/components/ImageGeneratorPanel";

// ── Money-making API categories ──────────────────────────────────────────────
const MONEY_APIS = [
  // Freelance / Gig Economy
  { id: "fiverr",     cat: "Freelance",   name: "Fiverr",          icon: DollarSign,  color: "green",   url: "https://api.fiverr.com",         desc: "Sell gigs: coding, design, writing, AI services. $5–$10k per order.", revenue: "$5–$10,000/gig",   botHint: "DreamSalesPro",  docs: "https://developers.fiverr.com", free: false },
  { id: "upwork",     cat: "Freelance",   name: "Upwork",          icon: DollarSign,  color: "green",   url: "https://www.upwork.com/api",     desc: "Win freelance contracts. AI can bid, pitch, and deliver work.",       revenue: "$50–$500/hr",     botHint: "DreamSalesPro",  docs: "https://developers.upwork.com", free: false },
  { id: "freelancer", cat: "Freelance",   name: "Freelancer.com",  icon: DollarSign,  color: "blue",    url: "https://api.freelancer.com",     desc: "Auto-bid on projects. Use coding bots to deliver instantly.",         revenue: "$100–$5,000",     botHint: "DreamCodeLab",   docs: "https://developers.freelancer.com", free: false },
  { id: "toptal",     cat: "Freelance",   name: "Toptal",          icon: DollarSign,  color: "blue",    url: "https://www.toptal.com/api",     desc: "Top 3% talent network. Premium rates for elite bots.",               revenue: "$150–$300/hr",    botHint: "CommandCore",    docs: "https://www.toptal.com", free: false },

  // E-commerce
  { id: "amazon",     cat: "E-Commerce",  name: "Amazon SP-API",   icon: Package,     color: "orange",  url: "https://sellingpartnerapi-na.amazon.com", desc: "FBA product listing, pricing, orders, inventory management.",    revenue: "$1k–$100k/mo",   botHint: "DreamRetail",    docs: "https://developer-docs.amazon.com/sp-api/", free: false },
  { id: "ebay",       cat: "E-Commerce",  name: "eBay API",        icon: ShoppingBag, color: "red",     url: "https://api.ebay.com",           desc: "List & sell products. Auto-reprice. Arbitrage opportunities.",       revenue: "$500–$50k/mo",    botHint: "DreamRetail",    docs: "https://developer.ebay.com", free: true },
  { id: "etsy",       cat: "E-Commerce",  name: "Etsy API",        icon: Store,       color: "orange",  url: "https://openapi.etsy.com",       desc: "Sell digital products, print-on-demand, handmade at scale.",         revenue: "$500–$20k/mo",    botHint: "DreamContent",   docs: "https://developers.etsy.com", free: true },
  { id: "alibaba",    cat: "E-Commerce",  name: "Alibaba Open API",icon: Globe,       color: "orange",  url: "https://openapi.alibaba.com",    desc: "Source products wholesale. Sync to Amazon/eBay for profit.",         revenue: "30–70% margins", botHint: "DreamGlobal",    docs: "https://openapi.alibaba.com/api", free: false },
  { id: "aliexpress", cat: "E-Commerce",  name: "AliExpress API",  icon: Truck,       color: "red",     url: "https://api.aliexpress.com",     desc: "Drop-shipping automation. Zero inventory, direct ship.",             revenue: "$1k–$30k/mo",    botHint: "DreamRetail",    docs: "https://developers.aliexpress.com", free: false },
  { id: "temu",       cat: "E-Commerce",  name: "Temu / PDD API",  icon: ShoppingBag, color: "orange",  url: "https://open.pddapis.com",       desc: "PDD/Temu wholesale sourcing API. Ultra-low cost product source.",     revenue: "50–80% margins", botHint: "DreamGlobal",    docs: "https://open.pddapis.com/", free: false },
  { id: "shopify",    cat: "E-Commerce",  name: "Shopify Admin",   icon: Store,       color: "green",   url: "https://shopify.dev/api",        desc: "Build & manage stores. Auto-fulfillment. Multi-channel sync.",       revenue: "$5k–$500k/mo",   botHint: "DreamBizLaunch", docs: "https://shopify.dev/docs/api", free: true },
  { id: "walmart",    cat: "E-Commerce",  name: "Walmart MP API",  icon: ShoppingBag, color: "blue",    url: "https://developer.walmart.com",  desc: "List on Walmart Marketplace. 120M+ monthly shoppers.",               revenue: "$2k–$100k/mo",   botHint: "DreamRetail",    docs: "https://developer.walmart.com", free: true },

  // Government / Grants
  { id: "sam",        cat: "Government",  name: "SAM.gov API",     icon: Landmark,    color: "blue",    url: "https://api.sam.gov",            desc: "Federal contracts & solicitations. Billions in opportunities daily.", revenue: "$10k–$10M",       botHint: "DreamAdmin",     docs: "https://open.gsa.gov/api/sam/", free: true },
  { id: "grants",     cat: "Government",  name: "Grants.gov API",  icon: Landmark,    color: "blue",    url: "https://www.grants.gov/web/grants/s2s/grantor/schemas.html", desc: "Federal grant opportunities. Science, tech, business, community.", revenue: "$25k–$5M",       botHint: "DreamAdmin",     docs: "https://www.grants.gov/web/grants/applicants/api.html", free: true },
  { id: "usaspend",   cat: "Government",  name: "USASpending.gov", icon: TrendingUp,  color: "green",   url: "https://api.usaspending.gov",    desc: "Analyze federal spending. Find agencies that are buying your services.", revenue: "Data intel",    botHint: "DreamData",      docs: "https://api.usaspending.gov/docs/", free: true },
  { id: "sbir",       cat: "Government",  name: "SBIR API",        icon: Building2,   color: "indigo",  url: "https://www.sbir.gov/api",       desc: "Small business innovation grants up to $1.5M. Perfect for AI cos.", revenue: "$150k–$1.5M",    botHint: "DreamBizLaunch", docs: "https://www.sbir.gov/about/about-sbir", free: true },
  { id: "census",     cat: "Government",  name: "Census API",      icon: BarChart2,   color: "blue",    url: "https://api.census.gov",         desc: "Market research data. Target demographics for sales.",               revenue: "Market intel",   botHint: "DreamData",      docs: "https://www.census.gov/data/developers.html", free: true },
  { id: "bls",        cat: "Government",  name: "BLS Data API",    icon: BarChart2,   color: "slate",   url: "https://api.bls.gov",            desc: "Labor statistics. Industry trends & job market intelligence.",       revenue: "Market intel",   botHint: "DreamData",      docs: "https://www.bls.gov/developers/", free: true },

  // Crypto / Finance
  { id: "coingecko",  cat: "Crypto",      name: "CoinGecko API",   icon: Wallet,      color: "green",   url: "https://api.coingecko.com/api/v3", desc: "10,000+ coin prices, 30 calls/min FREE. Auto-trade signals.",     revenue: "$1k–$100k/mo",   botHint: "DreamCrypto",    docs: "https://docs.coingecko.com", free: true },
  { id: "binance",    cat: "Crypto",      name: "Binance API",     icon: TrendingUp,  color: "yellow",  url: "https://api.binance.com",        desc: "Spot & futures trading. Auto-bot trading at scale.",               revenue: "$500–$50k/mo",   botHint: "DreamCrypto",    docs: "https://binance-docs.github.io", free: true },
  { id: "coinbase",   cat: "Crypto",      name: "Coinbase Adv",    icon: CreditCard,  color: "blue",    url: "https://api.coinbase.com",       desc: "Buy/sell/transfer crypto. Institutional-grade trading API.",        revenue: "$1k–$1M/mo",     botHint: "DreamCrypto",    docs: "https://docs.cdp.coinbase.com", free: true },
  { id: "alpaca",     cat: "Crypto",      name: "Alpaca Markets",  icon: BarChart2,   color: "yellow",  url: "https://api.alpaca.markets",     desc: "Commission-free stocks & crypto. Paper & live trading.",            revenue: "$500–$50k/mo",   botHint: "DreamFinance",   docs: "https://alpaca.markets/docs/api-documentation/", free: true },

  // Real Estate
  { id: "zillow",     cat: "Real Estate", name: "Zillow API",      icon: Building2,   color: "blue",    url: "https://www.zillow.com/howto/api/", desc: "Property valuations. Find flip/rental deals.",                   revenue: "$10k–$500k",     botHint: "DreamRealEstate",docs: "https://www.zillow.com/howto/api/", free: false },
  { id: "attom",      cat: "Real Estate", name: "ATTOM Data API",  icon: Building2,   color: "green",   url: "https://api.gateway.attomdata.com", desc: "Property data, foreclosures, tax assessments nationwide.",        revenue: "$50k–$5M",       botHint: "DreamRealEstate",docs: "https://api.attomdata.com/documentation", free: false },
  { id: "hud",        cat: "Real Estate", name: "HUD Data API",    icon: Landmark,    color: "blue",    url: "https://www.hud.gov/developer",  desc: "HUD housing data. Section 8 opportunities, affordable housing.",    revenue: "Deal intel",     botHint: "DreamRealEstate",docs: "https://www.hud.gov/program_offices/cio/developer-resources", free: true },

  // AI / SaaS
  { id: "openai",     cat: "AI / SaaS",   name: "OpenAI API",      icon: BrainCircuit,color: "violet",  url: "https://api.openai.com",         desc: "Build AI products. Re-sell AI services at 10–100x markup.",        revenue: "$1k–$100k/mo",   botHint: "CommandCore",    docs: "https://platform.openai.com/docs", free: false },
  { id: "rapidapi",   cat: "AI / SaaS",   name: "RapidAPI Hub",    icon: Zap,         color: "blue",    url: "https://rapidapi.com",           desc: "10,000+ APIs. Resell API access. SaaS product pipeline.",           revenue: "$500–$50k/mo",   botHint: "DreamAIInfra",   docs: "https://docs.rapidapi.com", free: true },
  { id: "stripe",     cat: "AI / SaaS",   name: "Stripe API",      icon: CreditCard,  color: "violet",  url: "https://api.stripe.com",         desc: "Accept payments. Subscriptions, invoices, payouts worldwide.",      revenue: "All revenue",    botHint: "DreamPayments",  docs: "https://stripe.com/docs/api", free: true },
];

const CATS = ["All", ...Array.from(new Set(MONEY_APIS.map(a => a.cat)))];
const COLOR_MAP: Record<string, string> = {
  green: "border-green-500/30 bg-green-500/8 text-green-400",
  blue: "border-blue-500/30 bg-blue-500/8 text-blue-400",
  orange: "border-orange-500/30 bg-orange-500/8 text-orange-400",
  red: "border-red-500/30 bg-red-500/8 text-red-400",
  yellow: "border-yellow-500/30 bg-yellow-500/8 text-yellow-400",
  violet: "border-violet-500/30 bg-violet-500/8 text-violet-400",
  indigo: "border-indigo-500/30 bg-indigo-500/8 text-indigo-400",
  slate: "border-slate-500/30 bg-slate-500/8 text-slate-400",
};
const CAT_ICON: Record<string, any> = {
  Freelance: DollarSign, "E-Commerce": ShoppingBag, Government: Landmark,
  Crypto: Wallet, "Real Estate": Building2, "AI / SaaS": BrainCircuit,
};

function statusBadge(status: string) {
  if (status === "complete") return <Badge className="bg-green-500/15 text-green-400 border-green-500/30 text-[10px]"><CheckCircle2 className="h-3 w-3 mr-1" />Complete</Badge>;
  if (status === "running") return <Badge className="bg-blue-500/15 text-blue-400 border-blue-500/30 text-[10px]"><Loader2 className="h-3 w-3 mr-1 animate-spin" />Running</Badge>;
  if (status === "pending") return <Badge className="bg-amber-500/15 text-amber-400 border-amber-500/30 text-[10px]"><Clock className="h-3 w-3 mr-1" />Pending</Badge>;
  if (status === "failed") return <Badge className="bg-red-500/15 text-red-400 border-red-500/30 text-[10px]"><XCircle className="h-3 w-3 mr-1" />Failed</Badge>;
  if (status === "paused") return <Badge className="bg-slate-500/15 text-slate-400 border-slate-500/30 text-[10px]"><Shield className="h-3 w-3 mr-1" />Paused</Badge>;
  return <Badge className="text-[10px]">{status}</Badge>;
}

export default function ActionsPage() {
  const [, setLocation] = useLocation();
  const { toast } = useToast();
  const [activeTab, setActiveTab] = useState<"agents" | "tasks" | "repository" | "money-apis" | "debug" | "ai-tools">("agents");
  const [botSearch, setBotSearch] = useState("");
  const [botDivision, setBotDivision] = useState("All");
  const [apiCat, setApiCat] = useState("All");
  const [apiSearch, setApiSearch] = useState("");
  const [selectedBotSlug, setSelectedBotSlug] = useState<string | undefined>();
  const [taskSearch, setTaskSearch] = useState("");

  const botsQ = useQuery<any[]>({ queryKey: ["/api/bots"], select: (d: any) => d });
  const tasksQ = useQuery<any[]>({ queryKey: ["/api/tasks"], refetchInterval: 10000 });
  const githubQ = useQuery<any>({ queryKey: ["/api/github/status"], retry: 1 });
  const pullsQ = useQuery<any>({ queryKey: ["/api/github/pulls"], retry: 1 });
  const repoTreeQ = useQuery<any>({ queryKey: ["/api/github/repo-tree"], retry: 1, enabled: activeTab === "repository" });
  const wfQ = useQuery<any>({ queryKey: ["/api/github/workflows"], retry: 1, enabled: activeTab === "repository" });
  const creatorStudioQ = useQuery<any>({ queryKey: ["/api/buddy/creator-studio"], retry: 1 });
  const modelChoicesQ = useQuery<any>({ queryKey: ["/api/buddy/model-choices"], retry: 1 });
  const restoredFamiliesQ = useQuery<any>({ queryKey: ["/api/buddy/restored-bot-families"], retry: 1 });

  const restartAll = useMutation({
    mutationFn: () => apiRequest("POST", "/api/tasks/restart-all", {}),
    onSuccess: (d: any) => {
      queryClient.invalidateQueries({ queryKey: ["/api/tasks"] });
      toast({ title: `✅ Restarted ${d.restarted} tasks`, description: "All tasks set back to pending" });
    },
    onError: (e: any) => toast({ title: "Restart failed", description: e.message, variant: "destructive" }),
  });

  const restartTask = useMutation({
    mutationFn: (id: number) => apiRequest("POST", `/api/tasks/${id}/restart`, {}),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["/api/tasks"] });
      toast({ title: "Task restarted" });
    },
    onError: (e: any) => toast({ title: "Restart failed", description: e.message, variant: "destructive" }),
  });

  const runTask = useMutation({
    mutationFn: (id: number) => apiRequest("POST", `/api/tasks/${id}/run`, {}),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["/api/tasks"] });
      toast({ title: "Task started!" });
    },
    onError: (e: any) => toast({ title: "Run failed", description: e.message, variant: "destructive" }),
  });

  // Buddy bot
  const bots: any[] = botsQ.data ?? [];
  const buddy = bots.find((b: any) => b.slug === "buddy-bot");
  const divisions = ["All", ...Array.from(new Set(bots.map((b: any) => b.division).filter(Boolean))).sort()];

  const filteredBots = bots.filter((b: any) => {
    const matchDiv = botDivision === "All" || b.division === botDivision;
    const matchSearch = !botSearch || b.displayName?.toLowerCase().includes(botSearch.toLowerCase()) || b.division?.toLowerCase().includes(botSearch.toLowerCase());
    return matchDiv && matchSearch;
  });

  const tasks: any[] = tasksQ.data ?? [];
  const filteredTasks = tasks.filter((t: any) => !taskSearch || t.objective?.toLowerCase().includes(taskSearch.toLowerCase()) || t.division?.toLowerCase().includes(taskSearch.toLowerCase()));

  const filteredApis = MONEY_APIS.filter(a => {
    const matchCat = apiCat === "All" || a.cat === apiCat;
    const matchSearch = !apiSearch || a.name.toLowerCase().includes(apiSearch.toLowerCase()) || a.desc.toLowerCase().includes(apiSearch.toLowerCase());
    return matchCat && matchSearch;
  });

  const pulls: any[] = (pullsQ.data as any)?.pullRequests ?? [];
  const repoInfo = (githubQ.data as any)?.repo;
  const repoFiles: any[] = (repoTreeQ.data as any)?.tree ?? [];
  const runs: any[] = (wfQ.data as any)?.runs ?? [];

  const tabs = [
    { id: "agents", label: "Agents", icon: Bot, count: bots.length },
    { id: "tasks", label: "Tasks", icon: ListTodo, count: tasks.length },
    { id: "repository", label: "Repository", icon: Github, count: null },
    { id: "money-apis", label: "Money APIs", icon: DollarSign, count: MONEY_APIS.length },
    { id: "ai-tools", label: "AI Tools", icon: ImageIcon, count: null },
    { id: "debug", label: "Debug & Fix", icon: Bug, count: tasks.filter(t => t.status === "failed").length || null },
  ] as const;

  return (
    <AppShell selectedBotSlug={selectedBotSlug} onBotChange={setSelectedBotSlug}>
      <Seo title="Actions & Agents — DreamCo Empire OS" description="Manage all bots, tasks, GitHub repository, pull requests, and money-making APIs." />

      <div className="buddy-appear space-y-6">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-end md:justify-between gap-4">
          <div>
            <h2 className="text-3xl md:text-4xl" data-testid="actions-title">Actions & Agents</h2>
            <p className="mt-1 text-muted-foreground">
              {bots.length} bots · {tasks.length} tasks · {MONEY_APIS.length} revenue APIs · Full repository control
            </p>
          </div>
          <div className="flex gap-2 flex-wrap">
            {activeTab === "tasks" && (
              <Button
                onClick={() => restartAll.mutate()}
                disabled={restartAll.isPending}
                className="rounded-xl bg-gradient-to-r from-amber-600 to-orange-600 text-white shadow-md"
                data-testid="restart-all-btn"
              >
                {restartAll.isPending ? <><Loader2 className="h-4 w-4 mr-2 animate-spin" />Restarting...</> : <><RotateCcw className="h-4 w-4 mr-2" />Restart All Tasks</>}
              </Button>
            )}
            {activeTab === "agents" && (
              <Button
                onClick={() => setSelectedBotSlug("buddy-bot")}
                className="rounded-xl bg-gradient-to-r from-primary to-accent text-primary-foreground shadow-md"
                data-testid="connect-buddy-btn"
              >
                <BrainCircuit className="h-4 w-4 mr-2" />Connect to Buddy
              </Button>
            )}
          </div>
        </div>

        {/* Buddy Status Banner */}
        <Card className={cn("buddy-card rounded-2xl border p-4 flex flex-col sm:flex-row sm:items-center gap-4",
          buddy ? "border-primary/30 bg-primary/5" : "border-border/60")}>
          <div className="flex items-center gap-3 flex-1">
            <span className="inline-flex h-10 w-10 items-center justify-center rounded-xl bg-primary/15 border border-primary/30">
              <BrainCircuit className="h-5 w-5 text-primary" />
            </span>
            <div>
              <div className="flex items-center gap-2">
                <p className="font-bold text-sm">Buddy Bot</p>
                <Badge className={cn("text-[10px]", buddy ? "bg-green-500/15 text-green-400 border-green-500/30" : "bg-amber-500/15 text-amber-400")}>
                  {buddy ? "● Connected" : "Loading..."}
                </Badge>
                <Badge className="bg-primary/15 text-primary border-primary/30 text-[10px]">ELITE</Badge>
              </div>
              <p className="text-xs text-muted-foreground mt-0.5">
                Master coder · 500+ libraries · Routes all coding tasks from 1,051 bots · {buddy?.division ?? "CommandCore"}
              </p>
            </div>
          </div>
          <div className="flex gap-2">
            <Link href={buddy ? `/bot/${buddy.id}` : "/bots"}>
              <Button size="sm" variant="outline" className="rounded-xl" data-testid="buddy-detail-btn">
                <Eye className="h-3.5 w-3.5 mr-1.5" />Profile
              </Button>
            </Link>
            <Button
              size="sm"
              className="rounded-xl bg-primary text-primary-foreground"
              onClick={() => setSelectedBotSlug("buddy-bot")}
              data-testid="buddy-chat-btn"
            >
              <BrainCircuit className="h-3.5 w-3.5 mr-1.5" />Chat with Buddy
            </Button>
          </div>
        </Card>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4" data-testid="buddy-creator-model-bridge">
          <Card className="buddy-card rounded-2xl border border-border/60 p-4">
            <div className="flex items-center gap-3 mb-3">
              <span className="inline-flex h-9 w-9 items-center justify-center rounded-xl bg-violet-500/15 border border-violet-500/30">
                <Sparkles className="h-4 w-4 text-violet-400" />
              </span>
              <div>
                <p className="text-sm font-bold">Creator Studio</p>
                <p className="text-xs text-muted-foreground">{creatorStudioQ.data?.workflows?.length ?? 0} workflows</p>
              </div>
            </div>
            <div className="space-y-2">
              {(creatorStudioQ.data?.workflows ?? []).slice(0, 3).map((workflow: any) => (
                <div key={workflow.id} className="rounded-xl border border-border/40 p-3">
                  <p className="text-xs font-semibold">{workflow.label}</p>
                  <p className="text-[11px] text-muted-foreground mt-1">{(workflow.outputs ?? []).slice(0, 3).join(" · ")}</p>
                </div>
              ))}
            </div>
          </Card>

          <Card className="buddy-card rounded-2xl border border-border/60 p-4">
            <div className="flex items-center gap-3 mb-3">
              <span className="inline-flex h-9 w-9 items-center justify-center rounded-xl bg-blue-500/15 border border-blue-500/30">
                <BrainCircuit className="h-4 w-4 text-blue-400" />
              </span>
              <div>
                <p className="text-sm font-bold">Model Choice</p>
                <p className="text-xs text-muted-foreground">{modelChoicesQ.data?.choices?.length ?? 0} provider routes</p>
              </div>
            </div>
            <div className="flex flex-wrap gap-2">
              {(modelChoicesQ.data?.choices ?? []).slice(0, 8).map((choice: any) => (
                <Badge key={choice.id} variant="secondary" className="rounded-full text-[10px]">
                  {choice.provider}
                </Badge>
              ))}
            </div>
            <p className="text-xs text-muted-foreground mt-3">Users can choose a provider; Buddy still keeps paid/live actions behind approval.</p>
          </Card>

          <Card className="buddy-card rounded-2xl border border-border/60 p-4">
            <div className="flex items-center gap-3 mb-3">
              <span className="inline-flex h-9 w-9 items-center justify-center rounded-xl bg-green-500/15 border border-green-500/30">
                <Bot className="h-4 w-4 text-green-400" />
              </span>
              <div>
                <p className="text-sm font-bold">Restored Bot Families</p>
                <p className="text-xs text-muted-foreground">{restoredFamiliesQ.data?.totals?.files ?? 0} mapped files</p>
              </div>
            </div>
            <div className="space-y-2">
              {(restoredFamiliesQ.data?.families ?? []).slice(0, 4).map((family: any) => (
                <div key={family.id} className="flex items-center justify-between gap-3 text-xs">
                  <span className="truncate">{family.label}</span>
                  <Badge variant="secondary" className="text-[10px]">{family.python_count} py</Badge>
                </div>
              ))}
            </div>
          </Card>
        </div>

        {/* Tabs */}
        <div className="flex flex-wrap gap-2" data-testid="actions-tabs">
          {tabs.map(tab => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={cn(
                  "flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium border transition-all",
                  activeTab === tab.id
                    ? "bg-primary text-primary-foreground border-primary shadow-sm"
                    : "bg-card/60 border-border/60 text-muted-foreground hover:text-foreground hover:bg-card"
                )}
                data-testid={`tab-${tab.id}`}
              >
                <Icon className="h-4 w-4" />
                {tab.label}
                {tab.count !== null && tab.count > 0 && (
                  <span className={cn("text-[10px] px-1.5 py-0.5 rounded-full font-mono",
                    activeTab === tab.id ? "bg-white/20" : "bg-muted text-muted-foreground"
                  )}>{tab.count}</span>
                )}
              </button>
            );
          })}
        </div>

        {/* ═══════════════ AGENTS TAB ═══════════════ */}
        {activeTab === "agents" && (
          <div className="space-y-4">
            {/* Filters */}
            <div className="flex flex-col sm:flex-row gap-3">
              <div className="relative flex-1">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Search bots..."
                  value={botSearch}
                  onChange={e => setBotSearch(e.target.value)}
                  className="pl-9 rounded-xl border-border/60"
                  data-testid="bot-search"
                />
              </div>
              <div className="flex gap-2 flex-wrap">
                {divisions.slice(0, 8).map(div => (
                  <button
                    key={div}
                    onClick={() => setBotDivision(div)}
                    className={cn("px-3 py-1.5 rounded-lg text-xs font-medium border transition-all",
                      botDivision === div ? "bg-primary text-primary-foreground border-primary" : "bg-card/60 border-border/60 text-muted-foreground hover:text-foreground"
                    )}
                    data-testid={`division-filter-${div}`}
                  >
                    {div}
                  </button>
                ))}
                {divisions.length > 8 && (
                  <button
                    onClick={() => setBotDivision("All")}
                    className="px-3 py-1.5 rounded-lg text-xs font-medium border bg-card/60 border-border/60 text-muted-foreground"
                  >
                    +{divisions.length - 8} more
                  </button>
                )}
              </div>
            </div>

            {botsQ.isLoading ? (
              <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-3">
                {Array.from({ length: 9 }).map((_, i) => <Skeleton key={i} className="h-24 rounded-2xl" />)}
              </div>
            ) : (
              <>
                <p className="text-xs text-muted-foreground">{filteredBots.length} bots shown</p>
                <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-3" data-testid="bots-grid">
                  {filteredBots.slice(0, 60).map((bot: any) => {
                    const isBuddy = bot.slug === "buddy-bot";
                    return (
                      <Card
                        key={bot.id}
                        className={cn("buddy-card rounded-2xl border p-4 flex flex-col gap-2 group hover:shadow-md transition-all cursor-pointer",
                          isBuddy ? "border-primary/40 bg-primary/8" : "border-border/60"
                        )}
                        data-testid={`bot-card-${bot.slug}`}
                      >
                        <div className="flex items-start justify-between gap-2">
                          <div className="flex items-center gap-2 min-w-0">
                            <span className={cn("inline-flex h-7 w-7 items-center justify-center rounded-lg flex-shrink-0",
                              isBuddy ? "bg-primary/20 border border-primary/30" : "bg-muted/40 border border-border/50"
                            )}>
                              {isBuddy ? <BrainCircuit className="h-3.5 w-3.5 text-primary" /> : <Bot className="h-3.5 w-3.5 text-muted-foreground" />}
                            </span>
                            <div className="min-w-0">
                              <p className="font-semibold text-sm truncate">{bot.displayName}</p>
                              <p className="text-[10px] text-muted-foreground">{bot.division}</p>
                            </div>
                          </div>
                          <div className="flex gap-1 flex-shrink-0">
                            <Badge className={cn("text-[10px]",
                              bot.tier === "elite" ? "bg-primary/15 text-primary border-primary/30" :
                              bot.tier === "enterprise" ? "bg-violet-500/15 text-violet-400 border-violet-500/30" :
                              bot.tier === "pro" ? "bg-blue-500/15 text-blue-400 border-blue-500/30" :
                              "bg-muted text-muted-foreground border-border/50"
                            )}>{bot.tier ?? "free"}</Badge>
                          </div>
                        </div>
                        <p className="text-[11px] text-muted-foreground line-clamp-2 flex-1">{bot.description}</p>
                        <div className="flex gap-1.5 mt-1">
                          <Button
                            size="sm"
                            variant="outline"
                            className="rounded-lg h-7 text-[11px] flex-1"
                            onClick={() => setSelectedBotSlug(bot.slug)}
                            data-testid={`chat-bot-${bot.slug}`}
                          >
                            Chat
                          </Button>
                          <Link href={`/bot/${bot.id}`}>
                            <Button size="sm" variant="ghost" className="rounded-lg h-7 w-7 p-0" data-testid={`open-bot-${bot.slug}`}>
                              <ChevronRight className="h-3.5 w-3.5" />
                            </Button>
                          </Link>
                        </div>
                      </Card>
                    );
                  })}
                </div>
                {filteredBots.length > 60 && (
                  <div className="text-center pt-2">
                    <Link href="/bots">
                      <Button variant="outline" className="rounded-xl" data-testid="view-all-bots-btn">
                        View all {filteredBots.length} bots <ArrowRight className="h-4 w-4 ml-2" />
                      </Button>
                    </Link>
                  </div>
                )}
              </>
            )}
          </div>
        )}

        {/* ═══════════════ TASKS TAB ═══════════════ */}
        {activeTab === "tasks" && (
          <div className="space-y-4">
            {/* Stats */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              {[
                { label: "Total Tasks", val: tasks.length, color: "blue" },
                { label: "Running", val: tasks.filter(t => t.status === "running").length, color: "green" },
                { label: "Pending", val: tasks.filter(t => t.status === "pending").length, color: "amber" },
                { label: "Failed", val: tasks.filter(t => t.status === "failed").length, color: "red" },
              ].map(s => (
                <Card key={s.label} className={cn("buddy-card rounded-2xl border p-4 text-center", `border-${s.color}-500/20 bg-${s.color}-500/5`)}>
                  <p className={cn("text-2xl font-black", `text-${s.color}-400`)}>{s.val}</p>
                  <p className="text-xs text-muted-foreground mt-1">{s.label}</p>
                </Card>
              ))}
            </div>

            <div className="flex gap-3 items-center">
              <div className="relative flex-1">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input placeholder="Search tasks..." value={taskSearch} onChange={e => setTaskSearch(e.target.value)} className="pl-9 rounded-xl border-border/60" data-testid="task-search" />
              </div>
              <Button onClick={() => restartAll.mutate()} disabled={restartAll.isPending} variant="outline" className="rounded-xl" data-testid="restart-all-btn-2">
                {restartAll.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : <RotateCcw className="h-4 w-4 mr-2" />}
                Restart All
              </Button>
            </div>

            {tasksQ.isLoading ? (
              <div className="space-y-3">{Array.from({ length: 5 }).map((_, i) => <Skeleton key={i} className="h-20 rounded-2xl" />)}</div>
            ) : filteredTasks.length === 0 ? (
              <Card className="buddy-card rounded-2xl border border-border/60 p-12 text-center">
                <ListTodo className="h-8 w-8 text-muted-foreground/40 mx-auto mb-3" />
                <p className="text-sm text-muted-foreground">No tasks found</p>
                <Link href="/orchestration">
                  <Button className="mt-4 rounded-xl" data-testid="create-task-btn"><Plus className="h-4 w-4 mr-2" />Create Task</Button>
                </Link>
              </Card>
            ) : (
              <div className="space-y-2" data-testid="tasks-list">
                {filteredTasks.map((task: any) => (
                  <Card key={task.id} className="buddy-card rounded-2xl border border-border/60 p-4" data-testid={`task-card-${task.id}`}>
                    <div className="flex flex-col sm:flex-row sm:items-center gap-3">
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 flex-wrap">
                          {statusBadge(task.status)}
                          {task.division && <Badge variant="outline" className="text-[10px]">{task.division}</Badge>}
                          {task.autonomyMode && <Badge variant="outline" className="text-[10px]">{task.autonomyMode}</Badge>}
                        </div>
                        <p className="font-medium text-sm mt-1 line-clamp-2">{task.objective}</p>
                        <p className="text-[10px] text-muted-foreground mt-0.5">
                          ID #{task.id} · Priority {task.priority ?? 0} · Created {task.createdAt ? new Date(task.createdAt).toLocaleDateString() : "—"}
                        </p>
                      </div>
                      <div className="flex gap-2 flex-shrink-0">
                        <Button
                          size="sm"
                          variant="outline"
                          className="rounded-lg h-8"
                          onClick={() => restartTask.mutate(task.id)}
                          disabled={restartTask.isPending}
                          data-testid={`restart-task-${task.id}`}
                        >
                          <RotateCcw className="h-3.5 w-3.5 mr-1" />Restart
                        </Button>
                        {task.status !== "running" && (
                          <Button
                            size="sm"
                            className="rounded-lg h-8 bg-primary text-primary-foreground"
                            onClick={() => runTask.mutate(task.id)}
                            disabled={runTask.isPending}
                            data-testid={`run-task-${task.id}`}
                          >
                            <Play className="h-3.5 w-3.5 mr-1" />Run
                          </Button>
                        )}
                      </div>
                    </div>
                  </Card>
                ))}
              </div>
            )}

            <div className="flex justify-center pt-2">
              <Link href="/orchestration">
                <Button variant="outline" className="rounded-xl" data-testid="orchestration-link">
                  Full Task Manager <ArrowRight className="h-4 w-4 ml-2" />
                </Button>
              </Link>
            </div>
          </div>
        )}

        {/* ═══════════════ REPOSITORY TAB ═══════════════ */}
        {activeTab === "repository" && (
          <div className="space-y-4">
            {/* Repo header */}
            <Card className="buddy-card rounded-2xl border border-border/60 p-5">
              <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                <div className="flex items-center gap-3">
                  <span className="inline-flex h-10 w-10 items-center justify-center rounded-xl bg-muted/40 border border-border/50">
                    <Github className="h-5 w-5" />
                  </span>
                  <div>
                    <p className="font-bold">{repoInfo?.name ?? "DreamCo-Technologies/Dreamcobots"}</p>
                    <p className="text-xs text-muted-foreground">{repoInfo?.description ?? "Loading..."}</p>
                    {repoInfo && (
                      <div className="flex items-center gap-3 mt-1">
                        <span className="flex items-center gap-1 text-xs text-muted-foreground"><Star className="h-3 w-3" />{repoInfo.stars}</span>
                        <span className="flex items-center gap-1 text-xs text-muted-foreground"><GitBranch className="h-3 w-3" />{repoInfo.defaultBranch}</span>
                      </div>
                    )}
                  </div>
                </div>
                <div className="flex gap-2">
                  <a href="https://github.com/DreamCo-Technologies/Dreamcobots" target="_blank" rel="noreferrer">
                    <Button variant="outline" size="sm" className="rounded-xl" data-testid="open-github-btn"><ExternalLink className="h-3.5 w-3.5 mr-1.5" />Open on GitHub</Button>
                  </a>
                  <a href="https://github.com/DreamCo-Technologies/Dreamcobots/actions" target="_blank" rel="noreferrer">
                    <Button variant="outline" size="sm" className="rounded-xl" data-testid="open-actions-btn"><Activity className="h-3.5 w-3.5 mr-1.5" />Actions</Button>
                  </a>
                </div>
              </div>
            </Card>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
              {/* Pull Requests */}
              <Card className="buddy-card rounded-2xl border border-border/60 p-5">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-2">
                    <GitPullRequest className="h-4 w-4 text-primary" />
                    <span className="font-semibold text-sm">Pull Requests</span>
                    {pulls.length > 0 && <Badge className="text-[10px] bg-primary/15 text-primary border-primary/30">{pulls.length}</Badge>}
                  </div>
                  <Button variant="ghost" size="icon" className="h-7 w-7 rounded-lg" onClick={() => queryClient.invalidateQueries({ queryKey: ["/api/github/pulls"] })} data-testid="refresh-pulls-btn">
                    <RefreshCw className="h-3.5 w-3.5" />
                  </Button>
                </div>
                {pullsQ.isLoading ? (
                  <div className="space-y-2">{Array.from({ length: 3 }).map((_, i) => <Skeleton key={i} className="h-14 rounded-xl" />)}</div>
                ) : pullsQ.isError || (githubQ.data as any)?.connected === false ? (
                  <div className="text-center py-6 space-y-2">
                    <Github className="h-7 w-7 text-muted-foreground/40 mx-auto" />
                    <p className="text-sm text-muted-foreground">GitHub token required</p>
                    <p className="text-xs text-muted-foreground">Add GITHUB_TOKEN to environment secrets</p>
                  </div>
                ) : pulls.length === 0 ? (
                  <div className="text-center py-6">
                    <CheckCheck className="h-7 w-7 text-green-400 mx-auto mb-2" />
                    <p className="text-sm text-muted-foreground">No open pull requests</p>
                  </div>
                ) : (
                  <div className="space-y-2">
                    {pulls.map((pr: any) => (
                      <a key={pr.id} href={pr.url} target="_blank" rel="noreferrer" className="block" data-testid={`pr-${pr.id}`}>
                        <div className="flex items-start gap-3 p-3 rounded-xl border border-border/50 bg-muted/20 hover:bg-muted/40 transition-colors">
                          <GitPullRequest className={cn("h-4 w-4 mt-0.5 flex-shrink-0", pr.state === "open" ? "text-green-400" : "text-red-400")} />
                          <div className="min-w-0 flex-1">
                            <p className="text-sm font-medium truncate">{pr.title}</p>
                            <p className="text-[10px] text-muted-foreground">#{pr.id} by {pr.author} · {pr.state}</p>
                          </div>
                          <ExternalLink className="h-3 w-3 text-muted-foreground/50 flex-shrink-0 mt-1" />
                        </div>
                      </a>
                    ))}
                  </div>
                )}
              </Card>

              {/* Recent Workflow Runs */}
              <Card className="buddy-card rounded-2xl border border-border/60 p-5">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-2">
                    <Activity className="h-4 w-4 text-violet-400" />
                    <span className="font-semibold text-sm">Recent Workflow Runs</span>
                  </div>
                  <a href="https://github.com/DreamCo-Technologies/Dreamcobots/actions" target="_blank" rel="noreferrer">
                    <Button variant="ghost" size="sm" className="h-7 rounded-lg text-xs" data-testid="view-all-runs-btn"><ExternalLink className="h-3 w-3 mr-1" />View All</Button>
                  </a>
                </div>
                {wfQ.isLoading ? (
                  <div className="space-y-2">{Array.from({ length: 4 }).map((_, i) => <Skeleton key={i} className="h-14 rounded-xl" />)}</div>
                ) : runs.length === 0 ? (
                  <p className="text-sm text-muted-foreground text-center py-6">No workflow runs yet — connect GitHub token</p>
                ) : (
                  <div className="space-y-2">
                    {runs.slice(0, 8).map((run: any) => (
                      <a key={run.id} href={run.html_url} target="_blank" rel="noreferrer" data-testid={`run-${run.id}`}>
                        <div className="flex items-center gap-3 p-3 rounded-xl border border-border/50 bg-muted/20 hover:bg-muted/40 transition-colors">
                          <span className={cn("h-2.5 w-2.5 rounded-full flex-shrink-0",
                            run.conclusion === "success" ? "bg-green-400" :
                            run.conclusion === "failure" ? "bg-red-400" :
                            run.status === "in_progress" ? "bg-amber-400 animate-pulse" : "bg-muted-foreground/40"
                          )} />
                          <div className="min-w-0 flex-1">
                            <p className="text-sm font-medium truncate">{run.name}</p>
                            <p className="text-[10px] text-muted-foreground">{run.conclusion ?? run.status} · {run.created_at ? new Date(run.created_at).toLocaleDateString() : ""}</p>
                          </div>
                          <ExternalLink className="h-3 w-3 text-muted-foreground/50 flex-shrink-0" />
                        </div>
                      </a>
                    ))}
                  </div>
                )}
              </Card>
            </div>

            {/* Repo File Tree */}
            <Card className="buddy-card rounded-2xl border border-border/60 p-5">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2">
                  <FolderOpen className="h-4 w-4 text-amber-400" />
                  <span className="font-semibold text-sm">Repository Files Tracked</span>
                  {repoFiles.length > 0 && <Badge className="text-[10px] bg-amber-500/15 text-amber-400 border-amber-500/30">{repoFiles.length} files</Badge>}
                </div>
                <a href="https://github.com/DreamCo-Technologies/Dreamcobots/tree/main" target="_blank" rel="noreferrer">
                  <Button variant="ghost" size="sm" className="h-7 rounded-lg text-xs" data-testid="browse-repo-btn"><ExternalLink className="h-3 w-3 mr-1" />Browse</Button>
                </a>
              </div>
              {repoTreeQ.isLoading ? (
                <div className="space-y-1">{Array.from({ length: 8 }).map((_, i) => <Skeleton key={i} className="h-8 rounded-lg" />)}</div>
              ) : repoFiles.length === 0 ? (
                <div className="text-center py-6 space-y-2">
                  <FileCode className="h-7 w-7 text-muted-foreground/40 mx-auto" />
                  <p className="text-sm text-muted-foreground">
                    {(githubQ.data as any)?.connected === false ? "GitHub token required to browse files" : "Repository file tree unavailable"}
                  </p>
                  <div className="flex flex-wrap gap-2 justify-center">
                    {["bots/", "python_bots/", "java_bots/", "empire-os/", "workflows/"].map(f => (
                      <a key={f} href={`https://github.com/DreamCo-Technologies/Dreamcobots/tree/main/${f}`} target="_blank" rel="noreferrer">
                        <Badge variant="outline" className="cursor-pointer hover:bg-muted/50 transition-colors text-xs">{f}</Badge>
                      </a>
                    ))}
                  </div>
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-1 max-h-80 overflow-y-auto">
                  {repoFiles.slice(0, 120).map((f: any) => (
                    <a key={f.path} href={f.html_url ?? `https://github.com/DreamCo-Technologies/Dreamcobots/blob/main/${f.path}`} target="_blank" rel="noreferrer" className="flex items-center gap-1.5 px-2 py-1.5 rounded-lg hover:bg-muted/40 transition-colors group" data-testid={`file-${f.path?.replace(/\//g, "-")}`}>
                      {f.type === "tree" ? <FolderOpen className="h-3.5 w-3.5 text-amber-400 flex-shrink-0" /> : <FileCode className="h-3.5 w-3.5 text-muted-foreground flex-shrink-0" />}
                      <span className="text-xs truncate group-hover:text-primary transition-colors">{f.path}</span>
                    </a>
                  ))}
                </div>
              )}
            </Card>
          </div>
        )}

        {/* ═══════════════ MONEY APIs TAB ═══════════════ */}
        {activeTab === "money-apis" && (
          <div className="space-y-4">
            <Card className="buddy-card rounded-2xl border border-green-500/20 bg-green-500/5 p-4">
              <div className="flex items-center gap-3">
                <DollarSign className="h-5 w-5 text-green-400" />
                <div>
                  <p className="font-bold text-sm text-green-400">Autonomous Revenue APIs</p>
                  <p className="text-xs text-muted-foreground">
                    {MONEY_APIS.length} money-making APIs organized by category. Each is pre-assigned to the best bot. Bots use these to generate revenue autonomously.
                  </p>
                </div>
              </div>
            </Card>

            {/* Filters */}
            <div className="flex flex-col sm:flex-row gap-3">
              <div className="relative flex-1">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input placeholder="Search APIs..." value={apiSearch} onChange={e => setApiSearch(e.target.value)} className="pl-9 rounded-xl border-border/60" data-testid="api-search" />
              </div>
              <div className="flex gap-2 flex-wrap">
                {CATS.map(cat => {
                  const Icon = cat === "All" ? Zap : (CAT_ICON[cat] ?? DollarSign);
                  return (
                    <button
                      key={cat}
                      onClick={() => setApiCat(cat)}
                      className={cn("flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium border transition-all",
                        apiCat === cat ? "bg-primary text-primary-foreground border-primary" : "bg-card/60 border-border/60 text-muted-foreground hover:text-foreground"
                      )}
                      data-testid={`cat-${cat}`}
                    >
                      <Icon className="h-3 w-3" />{cat}
                    </button>
                  );
                })}
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-3" data-testid="money-apis-grid">
              {filteredApis.map(api => {
                const Icon = api.icon;
                const palette = COLOR_MAP[api.color] ?? COLOR_MAP.blue;
                return (
                  <Card key={api.id} className={cn("buddy-card rounded-2xl border p-4 flex flex-col gap-3 hover:shadow-md transition-all", palette)} data-testid={`api-card-${api.id}`}>
                    <div className="flex items-start justify-between gap-2">
                      <div className="flex items-center gap-2">
                        <span className={cn("inline-flex h-8 w-8 items-center justify-center rounded-lg border", palette)}>
                          <Icon className="h-4 w-4" />
                        </span>
                        <div>
                          <p className="font-bold text-sm">{api.name}</p>
                          <div className="flex items-center gap-1 mt-0.5">
                            <Badge className="text-[9px] bg-muted/60 text-muted-foreground border-border/50">{api.cat}</Badge>
                            {api.free && <Badge className="text-[9px] bg-green-500/15 text-green-400 border-green-500/30">FREE</Badge>}
                          </div>
                        </div>
                      </div>
                      <a href={api.docs} target="_blank" rel="noreferrer">
                        <Button variant="ghost" size="icon" className="h-7 w-7 rounded-lg" data-testid={`api-docs-${api.id}`}>
                          <ExternalLink className="h-3 w-3" />
                        </Button>
                      </a>
                    </div>

                    <p className="text-[11px] text-muted-foreground leading-relaxed flex-1">{api.desc}</p>

                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-1 text-xs">
                        <TrendingUp className="h-3 w-3 text-green-400" />
                        <span className="text-green-400 font-medium">{api.revenue}</span>
                      </div>
                      <div className="flex items-center gap-1 text-[10px] text-muted-foreground">
                        <Bot className="h-3 w-3" />
                        {api.botHint}
                      </div>
                    </div>

                    <div className="flex gap-2">
                      <Button
                        size="sm"
                        className="flex-1 rounded-lg h-8 text-[11px] bg-primary text-primary-foreground"
                        onClick={() => {
                          const botForApi = bots.find(b => b.division === api.botHint || b.displayName?.toLowerCase().includes(api.name.toLowerCase())) || buddy;
                          if (botForApi) setSelectedBotSlug(botForApi.slug);
                          toast({ title: `🤖 Bot assigned!`, description: `${api.botHint} bot ready to work with ${api.name}` });
                        }}
                        data-testid={`use-api-${api.id}`}
                      >
                        <Bot className="h-3 w-3 mr-1" />Use with Bot
                      </Button>
                      <a href={api.docs} target="_blank" rel="noreferrer" className="flex-shrink-0">
                        <Button size="sm" variant="outline" className="rounded-lg h-8 text-[11px]" data-testid={`test-api-${api.id}`}>
                          Test
                        </Button>
                      </a>
                    </div>
                  </Card>
                );
              })}
            </div>

            {/* Category Summary */}
            <Card className="buddy-card rounded-2xl border border-border/60 p-5">
              <p className="font-semibold text-sm mb-3 flex items-center gap-2"><BarChart2 className="h-4 w-4 text-primary" />Revenue API Categories</p>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                {CATS.filter(c => c !== "All").map(cat => {
                  const Icon = CAT_ICON[cat] ?? DollarSign;
                  const count = MONEY_APIS.filter(a => a.cat === cat).length;
                  const freeCount = MONEY_APIS.filter(a => a.cat === cat && a.free).length;
                  return (
                    <div
                      key={cat}
                      className="flex items-center gap-3 p-3 rounded-xl border border-border/50 bg-muted/20 cursor-pointer hover:bg-muted/40 transition-colors"
                      onClick={() => setApiCat(cat)}
                      data-testid={`cat-summary-${cat}`}
                    >
                      <Icon className="h-4 w-4 text-muted-foreground flex-shrink-0" />
                      <div>
                        <p className="text-sm font-medium">{cat}</p>
                        <p className="text-[10px] text-muted-foreground">{count} APIs · {freeCount} free</p>
                      </div>
                    </div>
                  );
                })}
              </div>
            </Card>
          </div>
        )}

        {/* ═══════════════ AI TOOLS TAB ═══════════════ */}
        {activeTab === "ai-tools" && (
          <div className="space-y-4">
            <div>
              <h3 className="text-lg font-semibold">AI Tools</h3>
              <p className="text-sm text-muted-foreground mt-0.5">Generate images and media using the Empire OS AI stack.</p>
            </div>
            <div className="max-w-xl">
              <ImageGeneratorPanel />
            </div>
          </div>
        )}

        {/* ═══════════════ DEBUG TAB ═══════════════ */}
        {activeTab === "debug" && (
          <div className="space-y-4">
            {/* Failed tasks */}
            <Card className="buddy-card rounded-2xl border border-red-500/20 bg-red-500/5 p-5">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2">
                  <XCircle className="h-4 w-4 text-red-400" />
                  <span className="font-semibold text-sm text-red-400">Failed / Blocked Tasks</span>
                  <Badge className="bg-red-500/15 text-red-400 border-red-500/30 text-[10px]">{tasks.filter(t => t.status === "failed").length}</Badge>
                </div>
                <Button
                  size="sm"
                  onClick={() => restartAll.mutate()}
                  disabled={restartAll.isPending}
                  className="rounded-xl bg-red-600 text-white hover:bg-red-700"
                  data-testid="restart-failed-btn"
                >
                  {restartAll.isPending ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <RotateCcw className="h-3.5 w-3.5 mr-1" />}
                  Restart All Failed
                </Button>
              </div>
              {tasks.filter(t => t.status === "failed").length === 0 ? (
                <div className="text-center py-6">
                  <CheckCircle2 className="h-8 w-8 text-green-400 mx-auto mb-2" />
                  <p className="text-sm text-green-400 font-medium">All tasks healthy — no failures</p>
                </div>
              ) : (
                <div className="space-y-2">
                  {tasks.filter(t => t.status === "failed").map((task: any) => (
                    <div key={task.id} className="flex items-center gap-3 p-3 rounded-xl border border-red-500/20 bg-red-500/5">
                      <XCircle className="h-4 w-4 text-red-400 flex-shrink-0" />
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium truncate">{task.objective}</p>
                        <p className="text-[10px] text-muted-foreground">{task.division} · #{task.id}</p>
                      </div>
                      <Button size="sm" variant="outline" className="rounded-lg h-7 border-red-500/30 text-red-400 hover:bg-red-500/10" onClick={() => restartTask.mutate(task.id)} disabled={restartTask.isPending} data-testid={`restart-failed-${task.id}`}>
                        <RotateCcw className="h-3 w-3 mr-1" />Fix
                      </Button>
                    </div>
                  ))}
                </div>
              )}
            </Card>

            {/* GitHub connection status */}
            <Card className="buddy-card rounded-2xl border border-border/60 p-5">
              <p className="font-semibold text-sm mb-3 flex items-center gap-2"><Github className="h-4 w-4" />GitHub Connection Status</p>
              <div className="space-y-2">
                {[
                  { label: "Repo Access", ok: (githubQ.data as any)?.connected, detail: (githubQ.data as any)?.repo?.name ?? "DreamCo-Technologies/Dreamcobots" },
                  { label: "GitHub Token", ok: (githubQ.data as any)?.tokenValid !== false && (githubQ.data as any)?.connected, detail: (githubQ.data as any)?.connected ? "Valid" : "Add GITHUB_TOKEN to environment secrets" },
                  { label: "Buddy Bot", ok: !!buddy, detail: buddy ? "Connected — Elite tier" : "Loading..." },
                  { label: "Tasks API", ok: !tasksQ.isError, detail: `${tasks.length} tasks loaded` },
                ].map(item => (
                  <div key={item.label} className="flex items-center gap-3 p-3 rounded-xl border border-border/50 bg-muted/20">
                    {item.ok ? <CheckCircle2 className="h-4 w-4 text-green-400 flex-shrink-0" /> : <AlertCircle className="h-4 w-4 text-amber-400 flex-shrink-0" />}
                    <div className="flex-1">
                      <p className="text-sm font-medium">{item.label}</p>
                      <p className="text-[10px] text-muted-foreground">{item.detail}</p>
                    </div>
                    <Badge className={cn("text-[10px]", item.ok ? "bg-green-500/15 text-green-400 border-green-500/30" : "bg-amber-500/15 text-amber-400 border-amber-500/30")}>
                      {item.ok ? "OK" : "Fix needed"}
                    </Badge>
                  </div>
                ))}
              </div>
            </Card>

            <div className="flex gap-3 flex-wrap">
              <Link href="/debug">
                <Button className="rounded-xl" data-testid="open-debug-btn"><Bug className="h-4 w-4 mr-2" />Full Debug Intelligence</Button>
              </Link>
              <Link href="/bot-activity">
                <Button variant="outline" className="rounded-xl" data-testid="open-command-center-btn"><Activity className="h-4 w-4 mr-2" />Command Center</Button>
              </Link>
              <Link href="/sandbox">
                <Button variant="outline" className="rounded-xl" data-testid="open-sandbox-btn"><Code className="h-4 w-4 mr-2" />Sandbox Factory</Button>
              </Link>
            </div>
          </div>
        )}
      </div>
    </AppShell>
  );
}
