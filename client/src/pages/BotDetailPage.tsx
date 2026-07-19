import { useParams } from "wouter";
import { useQuery, useMutation } from "@tanstack/react-query";
import { Link } from "wouter";
import Seo from "@/components/Seo";
import AppShell from "@/components/AppShell";
import { useState, useMemo } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { Progress } from "@/components/ui/progress";
import { cn } from "@/lib/utils";
import { useToast } from "@/hooks/use-toast";
import { useSubscriptionTier, isBotUnlocked } from "@/hooks/use-subscription";
import { apiRequest, queryClient } from "@/lib/queryClient";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import type { BotProfile, BotMetric, BotError, BotFinancial, BotMemory } from "@shared/schema";
import { TIER_AUTONOMY_LIMITS, DIVISION_API_REGISTRIES } from "@shared/api-registry";
import { DIVISION_FORMULAS, type DivisionFormula } from "@shared/division-formulas";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  ArrowLeft,
  Activity,
  BarChart3,
  Bot,
  Brain,
  CheckCircle2,
  ChevronRight,
  CircleDollarSign,
  Clock,
  Cpu,
  Database,
  FlaskConical,
  Globe,
  HardDrive,
  Layers,
  LineChart,
  Lock,
  MessageSquare,
  Monitor,
  Network,
  Play,
  Plug,
  Power,
  Rocket,
  Server,
  Shield,
  Sparkles,
  Star,
  Target,
  TrendingUp,
  Unlock,
  Users,
  Zap,
  Calculator,
  BookOpen,
  Plus,
  Send,
  Trash2,
} from "lucide-react";

const TIER_COLORS: Record<string, string> = {
  free: "bg-muted text-muted-foreground",
  pro: "bg-[rgb(59_130_246)]/15 text-[rgb(59_130_246)] border border-[rgb(59_130_246)]/20",
  enterprise: "bg-[rgb(168_85_247)]/15 text-[rgb(168_85_247)] border border-[rgb(168_85_247)]/20",
  elite: "bg-[rgb(245_158_11)]/15 text-[rgb(245_158_11)] border border-[rgb(245_158_11)]/20",
};

const STATUS_COLORS: Record<string, { bg: string; text: string; dot: string }> = {
  active: { bg: "bg-[rgb(34_197_94)]/10", text: "text-[rgb(34_197_94)]", dot: "bg-[rgb(34_197_94)]" },
  paused: { bg: "bg-[rgb(245_158_11)]/10", text: "text-[rgb(245_158_11)]", dot: "bg-[rgb(245_158_11)]" },
  inactive: { bg: "bg-[rgb(239_68_68)]/10", text: "text-[rgb(239_68_68)]", dot: "bg-[rgb(239_68_68)]" },
};

const DIVISION_FEATURES: Record<string, string[]> = {
  DreamFinance: [
    "Real-time market data ingestion", "Multi-exchange order routing", "Portfolio risk analytics",
    "Tax-loss harvesting engine", "Regulatory compliance checks", "Custom strategy backtesting",
    "Automated position sizing", "Drawdown protection system", "Cross-asset correlation matrix",
    "Sentiment-driven signal generation", "Institutional-grade execution", "Smart order splitting",
    "Liquidity aggregation", "Fee optimization routing", "Performance attribution analysis",
    "Benchmark comparison tools", "Monte Carlo risk simulation", "Alpha factor discovery",
    "Custom indicator builder", "Multi-timeframe analysis",
  ],
  DreamRealEstate: [
    "Property valuation AI models", "Cap rate & NOI analysis", "Market comparable engine",
    "Zoning & permit database", "Construction cost estimation", "Tenant screening automation",
    "Lease management suite", "Property condition scoring", "Energy efficiency analysis",
    "Tax incentive discovery", "1031 exchange planning", "Investment cash flow projections",
    "Rent growth forecasting", "Vacancy risk prediction", "Neighborhood growth scoring",
    "Maintenance schedule optimizer", "Investor reporting automation", "Syndication management",
    "Drone survey integration", "Smart building IoT analytics",
  ],
  DreamSalesPro: [
    "AI lead scoring engine", "Multi-channel outreach sequencing", "CRM auto-enrichment",
    "Predictive pipeline analytics", "Smart meeting scheduler", "Objection response library",
    "Proposal auto-generation", "Contract lifecycle tracking", "Deal room management",
    "Revenue forecasting models", "Territory optimization", "Competitive battle cards",
    "Buyer intent signals", "Sales playbook generator", "Win/loss analysis engine",
    "Account health monitoring", "Churn prediction models", "Expansion revenue tracking",
    "Sales coaching AI", "Quota attainment analytics",
  ],
  DreamAIInfra: [
    "Multi-model routing engine", "Token usage metering", "Auto model fine-tuning pipeline",
    "Latency optimization system", "Cost-per-query analytics", "Model versioning & registry",
    "A/B model testing framework", "Prompt injection defense", "Data poisoning detection",
    "Bias & fairness auditing", "SLA monitoring dashboard", "Auto-scaling infrastructure",
    "Multi-tenant isolation", "Compliance audit trails", "API monetization platform",
    "White-label packaging", "Feature flag management", "Canary deployment system",
    "GPU resource scheduler", "Training data pipeline manager",
  ],
  DreamRetail: [
    "AI demand forecasting", "Dynamic pricing engine", "Conversion rate optimizer",
    "Cart abandonment recovery", "Visual product search", "Customer segmentation AI",
    "Loyalty program manager", "Multi-marketplace listing sync", "Inventory optimization",
    "Returns analysis engine", "Supplier management portal", "Product recommendation AI",
    "Fulfillment routing optimizer", "Social commerce integration", "Subscription box curator",
    "Print-on-demand automation", "Dropshipping supplier matcher", "SEO product listing optimizer",
    "Review management system", "Price war navigation engine",
  ],
  DreamProServices: [
    "Client proposal generator", "Automated coaching sessions", "Course creation platform",
    "Certification management", "Webinar hosting automation", "Group coaching facilitation",
    "Membership tier management", "Digital product builder", "Contract drafting engine",
    "Brand identity generator", "Ad campaign manager", "Newsletter automation",
    "Sponsorship matching engine", "Community management AI", "eBook publishing pipeline",
    "Speaking engagement booker", "Mentorship matching system", "Tax filing automation",
    "Payroll processing engine", "Event planning assistant",
  ],
  DreamData: [
    "Advanced data mining", "Predictive analytics engine", "Market sentiment analyzer",
    "Viral trend predictor", "KPI dashboard builder", "Ad targeting optimizer",
    "SEO performance tracker", "Competitor intelligence feed", "Web scraping automation",
    "Business intelligence suite", "Attribution modeling engine", "Price war navigation",
    "Demand pattern predictor", "Revenue attribution model", "Cross-region analytics",
    "Data quality scoring", "Anomaly detection system", "Natural language querying",
    "Automated report generation", "Data pipeline orchestrator",
  ],
  DreamGlobal: [
    "Cross-border tax optimizer", "International market entry AI", "Global compliance monitor",
    "Trade finance automation", "Currency hedging engine", "Tariff classification optimizer",
    "Export opportunity scanner", "Global logistics optimizer", "Country risk scorer",
    "International partner matcher", "Import/export documentation", "Supply chain diversifier",
    "Multi-region growth planner", "Global M&A target finder", "AI translation engine",
    "Cultural adaptation advisor", "Regulatory change tracker", "Transfer pricing optimizer",
    "International payroll manager", "Global talent acquisition",
  ],
  DreamAutomation: [
    "Robotic process automation", "Chatbot builder platform", "Virtual receptionist system",
    "Email management AI", "Task scheduling automation", "CRM workflow automator",
    "Invoice generation engine", "Smart calendar optimizer", "Social media auto-poster",
    "Funnel builder platform", "API integration manager", "Workflow visual builder",
    "OCR data entry automation", "Customer service bot", "Personal assistant AI",
    "SaaS platform builder", "Mobile app generator", "No-code app creator",
    "Domain valuation engine", "Website flipping analyzer",
  ],
  DreamContent: [
    "YouTube channel automation", "Podcast production suite", "TikTok content generator",
    "SEO blog writer", "AI voiceover engine", "Content syndication network",
    "Influencer growth engine", "Ad revenue optimizer", "Video editing automation",
    "Audiobook production pipeline", "Script writing AI", "Press release generator",
    "News aggregation platform", "Infographic designer", "Learning platform builder",
    "Thumbnail generation AI", "Hashtag optimization", "Engagement analytics",
    "Content calendar planner", "A/B headline testing",
  ],
  DreamTrade: [
    "Visual strategy builder", "Advanced backtesting engine", "Paper trading simulator",
    "Risk governance system", "Multi-exchange API router", "Performance analytics dashboard",
    "Copy trading platform", "Signal execution engine", "Multi-wallet crypto manager",
    "Mining rig optimizer", "Order flow analysis", "Slippage minimization",
    "Smart routing engine", "Market microstructure analysis", "Custom indicator library",
    "Strategy marketplace", "Social trading feed", "P&L attribution system",
    "Risk-adjusted return metrics", "Automated journaling",
  ],
  DreamFlow: [
    "Web automation engine", "Smart CAPTCHA handling", "Proxy rotation manager",
    "Data cleaning AI", "CRM export connector", "Browser fingerprint management",
    "Rate limiting intelligence", "Error self-healing", "Scheduled workflow runs",
    "Visual flow builder", "Data deduplication", "Format standardization",
    "Quality scoring system", "Multi-source aggregation", "API endpoint generator",
    "Webhook management", "Data transformation pipeline", "Export format converter",
    "Compliance logging", "Performance monitoring",
  ],
  DreamMarket: [
    "Multi-marketplace manager", "Product arbitrage finder", "Dropshipping automation",
    "Affiliate marketing engine", "Digital franchise platform", "Listing optimization AI",
    "Inventory sync engine", "Price optimization system", "Order routing intelligence",
    "Customer communication AI", "Review management system", "Marketplace analytics",
    "Supplier management", "Commission tracking", "Brand enforcement system",
    "Royalty collection automation", "Marketplace SEO optimizer", "Cross-platform analytics",
    "Competitive monitoring", "Revenue attribution",
  ],
  DreamEmpire: [
    "Cross-division monitoring", "Revenue optimization engine", "Auto-scaling infrastructure",
    "White-label publishing", "Investor report generator", "Empire health dashboard",
    "Resource allocation AI", "Performance benchmarking", "SLA enforcement system",
    "Strategic planning assistant", "Board reporting automation", "Growth metrics tracker",
    "Cost center analysis", "Profitability modeling", "Division performance ranking",
    "Talent allocation optimizer", "Budget forecasting engine", "Risk aggregation system",
    "Regulatory compliance hub", "Executive briefing generator",
  ],
  CommandCore: [
    "Multi-bot coordination hub", "Performance monitoring", "Resource allocation engine",
    "Task scheduling optimizer", "System analytics dashboard", "Cross-bot data sharing",
    "Self-debugging engine", "Cloud auto-scaling", "AI self-learning module",
    "Security compliance engine", "Audit trail management", "Alert rule processor",
    "Health check automation", "Dependency graph manager", "Load balancing intelligence",
    "Error cascade prevention", "Capacity planning AI", "Cost optimization system",
    "Uptime guarantee engine", "Emergency failover management",
  ],
  GameTitan: [
    "Reinforcement learning engine", "Real-time game prediction", "Co-op strategy advisor",
    "Auto-grind task automation", "Performance analytics tracker", "Skill assessment system",
    "Meta analysis engine", "Build optimization advisor", "Team composition analyzer",
    "Win condition predictor", "Replay analysis AI", "Training regimen builder",
    "Reaction time optimizer", "Map awareness coach", "Economy management advisor",
    "Tournament bracket predictor", "Streaming integration", "Community ranking system",
    "Achievement tracker", "Progression optimizer",
  ],
};

const COMPETITIVE_ADVANTAGES = [
  "24/7 autonomous operation with zero downtime",
  "Self-learning AI that improves with every interaction",
  "Enterprise-grade security with SOC 2 compliance",
  "Real-time data processing at scale",
  "Multi-region deployment for global coverage",
  "Automatic failover and disaster recovery",
  "API-first architecture for seamless integrations",
  "White-label ready for enterprise clients",
  "Custom model fine-tuning per client",
  "Comprehensive audit trail and compliance logging",
];

function generateMetrics(botId: number) {
  const seed = botId * 137;
  return {
    cpuUsage: 15 + (seed % 35),
    memoryUsage: 25 + (seed % 40),
    apiCalls: 5000 + (seed % 45000),
    uptime: 97 + ((seed % 30) / 10),
    tasksCompleted: 100 + (seed % 900),
    tasksFailed: seed % 15,
    revenue: 1000 + (seed % 49000),
    responseTime: 50 + (seed % 200),
    activeUsers: 50 + (seed % 450),
    satisfaction: 92 + ((seed % 80) / 10),
  };
}

function BotMemorySection({ botId }: { botId: number }) {
  const { toast } = useToast();
  const [newKey, setNewKey] = useState("");
  const [newValue, setNewValue] = useState("");

  const memoryQuery = useQuery<BotMemory[]>({
    queryKey: ["/api/bots", botId, "memory"],
    queryFn: async () => {
      const res = await fetch(`/api/bots/${botId}/memory`);
      return res.json();
    },
    enabled: !isNaN(botId),
  });

  const saveMutation = useMutation({
    mutationFn: async (data: { key: string; value: string }) => {
      const res = await apiRequest("POST", `/api/bots/${botId}/memory`, data);
      return res.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["/api/bots", botId, "memory"] });
      setNewKey("");
      setNewValue("");
      toast({ title: "Memory saved" });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: async (id: number) => {
      await apiRequest("DELETE", `/api/bots/${botId}/memory/${id}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["/api/bots", botId, "memory"] });
      toast({ title: "Memory deleted" });
    },
  });

  const memories = memoryQuery.data ?? [];

  return (
    <Card data-testid="bot-memory-section">
      <CardHeader className="flex flex-row items-center justify-between gap-2 space-y-0 pb-4">
        <CardTitle className="text-lg flex items-center gap-2">
          <BookOpen className="h-5 w-5 text-primary" />
          Bot Memory
        </CardTitle>
        <Badge variant="secondary" className="rounded-full">{memories.length} entries</Badge>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex flex-col sm:flex-row gap-2">
          <Input
            placeholder="Key (e.g. preference)"
            value={newKey}
            onChange={(e) => setNewKey(e.target.value)}
            className="sm:w-40"
            data-testid="input-memory-key"
          />
          <Input
            placeholder="Value"
            value={newValue}
            onChange={(e) => setNewValue(e.target.value)}
            className="flex-1"
            data-testid="input-memory-value"
          />
          <Button
            size="sm"
            onClick={() => saveMutation.mutate({ key: newKey, value: newValue })}
            disabled={!newKey || !newValue || saveMutation.isPending}
            data-testid="button-save-memory"
          >
            <Plus className="h-4 w-4 mr-1" /> Save
          </Button>
        </div>
        {memories.length === 0 ? (
          <p className="text-sm text-muted-foreground text-center py-4">No memories stored yet. Add a key-value pair above.</p>
        ) : (
          <div className="space-y-2">
            {memories.map((mem) => (
              <div key={mem.id} className="flex items-center gap-3 p-3 rounded-xl border border-border/40 hover-elevate" data-testid={`memory-entry-${mem.id}`}>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <Badge variant="outline" className="text-xs">{mem.key}</Badge>
                    {mem.category && <Badge variant="secondary" className="text-xs">{mem.category}</Badge>}
                  </div>
                  <p className="text-sm mt-1 truncate">{typeof mem.value === 'string' ? mem.value : JSON.stringify(mem.value)}</p>
                </div>
                <Button
                  size="icon"
                  variant="ghost"
                  className="h-7 w-7 flex-shrink-0"
                  onClick={() => deleteMutation.mutate(mem.id)}
                  data-testid={`button-delete-memory-${mem.id}`}
                >
                  <Trash2 className="h-3.5 w-3.5" />
                </Button>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}

export default function BotDetailPage() {
  const params = useParams<{ id: string }>();
  const botId = Number(params.id);
  const [botSlug, setBotSlug] = useState<string | undefined>(undefined);
  const [selectedFormula, setSelectedFormula] = useState<DivisionFormula | null>(null);

  const botQuery = useQuery<BotProfile>({
    queryKey: ["/api/bots", botId],
    enabled: !isNaN(botId),
  });

  const metricsQuery = useQuery<BotMetric[]>({
    queryKey: ["/api/metrics/bot", botId],
    enabled: !isNaN(botId),
  });

  const errorsQuery = useQuery<BotError[]>({
    queryKey: ["/api/errors"],
  });

  const financialsQuery = useQuery<BotFinancial[]>({
    queryKey: ["/api/financials"],
  });

  const { toast } = useToast();
  const subscriptionQuery = useSubscriptionTier();

  const controlsMutation = useMutation({
    mutationFn: async (body: { autonomyLevel?: string; operationalMode?: string }) => {
      const res = await apiRequest("PATCH", `/api/bots/${botId}/controls`, body);
      return res.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["/api/bots", botId] });
      queryClient.invalidateQueries({ queryKey: ["/api/bots"] });
      toast({ title: "Bot updated", description: "Control settings saved successfully." });
    },
    onError: (err: any) => {
      toast({ title: "Update failed", description: err?.message ?? "Unknown error", variant: "destructive" });
    },
  });

  const bot = botQuery.data;
  const metrics = useMemo(() => generateMetrics(botId), [botId]);
  const divisionFeatures = bot ? (DIVISION_FEATURES[bot.division] ?? DIVISION_FEATURES.CommandCore) : [];
  const capabilities = bot ? (Array.isArray(bot.capabilities) ? bot.capabilities as string[] : []) : [];

  const nicheCount = Math.min(Math.ceil(capabilities.length * 0.4), capabilities.length);
  const nicheCapabilities = capabilities.slice(0, nicheCount);
  const platformCapabilities = capabilities.slice(nicheCount);

  if (botQuery.isLoading) {
    return (
      <AppShell selectedBotSlug={botSlug} onBotChange={setBotSlug}>
        <div className="space-y-4">
          <Skeleton className="h-10 w-48" />
          <Skeleton className="h-64 w-full rounded-2xl" />
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {Array.from({ length: 6 }).map((_, i) => <Skeleton key={i} className="h-32 rounded-2xl" />)}
          </div>
        </div>
      </AppShell>
    );
  }

  if (!bot) {
    return (
      <AppShell selectedBotSlug={botSlug} onBotChange={setBotSlug}>
        <div className="text-center py-20">
          <Bot className="h-16 w-16 mx-auto text-muted-foreground/40" />
          <h2 className="mt-4 text-xl font-semibold">Bot not found</h2>
          <Link href="/divisions" className="inline-block mt-4">
            <Button variant="outline" className="rounded-xl" data-testid="back-to-divisions" asChild>
              <span>
                <ArrowLeft className="h-4 w-4 mr-2" /> Back to Divisions
              </span>
            </Button>
          </Link>
        </div>
      </AppShell>
    );
  }

  const statusStyle = STATUS_COLORS[bot.status] ?? STATUS_COLORS.active;
  const activeTier = subscriptionQuery.data?.tier ?? null;
  const unlocked = isBotUnlocked(bot.tier, activeTier);
  const isPaidTier = bot.tier && bot.tier !== "free";

  return (
    <AppShell selectedBotSlug={botSlug} onBotChange={setBotSlug}>
      <Seo title={`${bot.displayName} - DreamCo Empire OS`} description={bot.description} />

      <div className="space-y-6">
        <div className="flex items-center gap-2">
          <Link href="/divisions" data-testid="back-to-divisions">
            <Button variant="ghost" size="icon" asChild>
              <span><ArrowLeft className="h-4 w-4" /></span>
            </Button>
          </Link>
          <span className="text-sm text-muted-foreground">Divisions</span>
          <ChevronRight className="h-3 w-3 text-muted-foreground" />
          <Link href={`/divisions?d=${bot.division}`}>
            <span className="text-sm text-muted-foreground hover:text-foreground cursor-pointer">{bot.division}</span>
          </Link>
          <ChevronRight className="h-3 w-3 text-muted-foreground" />
          <span className="text-sm font-medium">{bot.displayName}</span>
        </div>

        <Card data-testid="bot-detail-header">
          <CardContent className="p-6 md:p-8">
            <div className="flex flex-col md:flex-row md:items-start justify-between gap-6">
              <div className="flex items-start gap-4">
                <div className="h-16 w-16 rounded-2xl bg-gradient-to-br from-primary/20 to-primary/5 border border-primary/20 flex items-center justify-center flex-shrink-0">
                  <Brain className="h-8 w-8 text-primary" />
                </div>
                <div>
                  <div className="flex items-center gap-3 flex-wrap">
                    <h1 className="text-2xl md:text-3xl font-bold" data-testid="bot-detail-name">{bot.displayName}</h1>
                    <div className={cn("flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium", statusStyle.bg, statusStyle.text)}>
                      <span className={cn("h-2 w-2 rounded-full", statusStyle.dot)} />
                      {bot.status}
                    </div>
                  </div>
                  <p className="text-sm font-mono text-muted-foreground mt-1" data-testid="bot-detail-slug">{bot.slug}</p>
                  <p className="text-sm text-muted-foreground mt-2 max-w-2xl">{bot.description}</p>
                  <div className="mt-3 flex flex-wrap items-center gap-2">
                    <Badge variant="secondary" className="rounded-full">{bot.division}</Badge>
                    <Badge variant="outline" className={cn("rounded-full capitalize", TIER_COLORS[bot.tier])}>{bot.tier}</Badge>
                    {isPaidTier && !subscriptionQuery.isLoading && unlocked && (
                      <Badge className="rounded-full bg-emerald-500/15 text-emerald-500 border border-emerald-500/30" data-testid="badge-unlocked-bot">
                        <Unlock className="h-3 w-3 mr-1" />
                        Unlocked
                      </Badge>
                    )}
                    {isPaidTier && !subscriptionQuery.isLoading && !unlocked && (
                      <Badge className="rounded-full bg-muted text-muted-foreground border border-border/40" data-testid="badge-locked-bot">
                        <Lock className="h-3 w-3 mr-1" />
                        Locked
                      </Badge>
                    )}
                    <Badge variant="outline" className="rounded-full capitalize">{bot.category}</Badge>
                    {bot.priceRange && (
                      <Badge variant="outline" className="rounded-full text-green-600 dark:text-green-400 border-green-500/20">
                        {bot.priceRange}
                      </Badge>
                    )}
                  </div>
                </div>
              </div>
              <div className="flex flex-col gap-2 md:items-end flex-shrink-0">
                <div className="text-right">
                  <p className="text-xs text-muted-foreground">Revenue Model</p>
                  <p className="text-sm font-medium" data-testid="bot-detail-revenue-model">{bot.revenueModel || "N/A"}</p>
                </div>
                <div className="text-right">
                  <p className="text-xs text-muted-foreground">Target Users</p>
                  <p className="text-sm font-medium" data-testid="bot-detail-target-users">{bot.targetUsers || "N/A"}</p>
                </div>
                {isPaidTier && !subscriptionQuery.isLoading && !unlocked && (
                  <Link href="/pricing">
                    <Button size="sm" className="rounded-xl mt-1" data-testid="btn-activate-bot">
                      <Zap className="h-4 w-4 mr-2" />
                      Activate
                    </Button>
                  </Link>
                )}
                {isPaidTier && !subscriptionQuery.isLoading && unlocked && (
                  <Link href={`/chat/${bot.slug}`}>
                    <Button size="sm" variant="outline" className="rounded-xl mt-1 border-emerald-500/30 text-emerald-600 dark:text-emerald-400 hover:bg-emerald-500/10" data-testid="btn-launch-bot">
                      <Unlock className="h-4 w-4 mr-2" />
                      Launch Bot
                    </Button>
                  </Link>
                )}
              </div>
            </div>
          </CardContent>
        </Card>

        <Card data-testid="bot-control-panel">
          <CardHeader className="flex flex-row items-center justify-between gap-2 space-y-0 pb-4">
            <CardTitle className="text-lg flex items-center gap-2">
              <Monitor className="h-5 w-5 text-primary" />
              Bot Control Panel
            </CardTitle>
            <Badge
              variant="outline"
              className={cn(
                "rounded-full capitalize",
                bot.operationalMode === "live" && "bg-[rgb(34_197_94)]/10 text-[rgb(34_197_94)] border-[rgb(34_197_94)]/20",
                bot.operationalMode === "sandbox" && "bg-[rgb(245_158_11)]/10 text-[rgb(245_158_11)] border-[rgb(245_158_11)]/20",
                bot.operationalMode === "offline" && "bg-[rgb(239_68_68)]/10 text-[rgb(239_68_68)] border-[rgb(239_68_68)]/20",
              )}
              data-testid="bot-mode-badge"
            >
              {bot.operationalMode === "live" ? "LIVE" : bot.operationalMode === "sandbox" ? "SANDBOX" : "OFFLINE"}
            </Badge>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div>
                <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-3">Autonomy Level</p>
                {(() => {
                  const allowed = TIER_AUTONOMY_LIMITS[bot.tier] ?? ["guided"];
                  const canSemi = allowed.includes("semi-autonomous");
                  const canFull = allowed.includes("full-autonomy");
                  return (
                    <div className="flex flex-col gap-2">
                      <Button
                        variant={bot.autonomyLevel === "guided" ? "default" : "outline"}
                        className={cn("justify-start rounded-xl", bot.autonomyLevel === "guided" && "bg-primary text-primary-foreground")}
                        disabled={controlsMutation.isPending}
                        onClick={() => controlsMutation.mutate({ autonomyLevel: "guided" })}
                        data-testid="btn-autonomy-guided"
                      >
                        <Shield className="h-4 w-4 mr-2" />
                        Guided
                      </Button>
                      <Button
                        variant={bot.autonomyLevel === "semi-autonomous" ? "default" : "outline"}
                        className={cn("justify-start rounded-xl", bot.autonomyLevel === "semi-autonomous" && "bg-[rgb(245_158_11)] text-white border-[rgb(245_158_11)]", !canSemi && "opacity-50")}
                        disabled={controlsMutation.isPending || !canSemi}
                        onClick={() => canSemi && controlsMutation.mutate({ autonomyLevel: "semi-autonomous" })}
                        data-testid="btn-autonomy-semi"
                      >
                        {canSemi ? <Activity className="h-4 w-4 mr-2" /> : <Lock className="h-4 w-4 mr-2" />}
                        Semi-Autonomous
                        {!canSemi && <Badge variant="outline" className="ml-auto rounded-full text-[9px]">Pro+</Badge>}
                      </Button>
                      <Button
                        variant={bot.autonomyLevel === "full-autonomy" ? "default" : "outline"}
                        className={cn("justify-start rounded-xl", bot.autonomyLevel === "full-autonomy" && "bg-[rgb(34_197_94)] text-white border-[rgb(34_197_94)]", !canFull && "opacity-50")}
                        disabled={controlsMutation.isPending || !canFull}
                        onClick={() => canFull && controlsMutation.mutate({ autonomyLevel: "full-autonomy" })}
                        data-testid="btn-autonomy-full"
                      >
                        {canFull ? <Rocket className="h-4 w-4 mr-2" /> : <Lock className="h-4 w-4 mr-2" />}
                        Full Autonomy
                        {!canFull && <Badge variant="outline" className="ml-auto rounded-full text-[9px]">Enterprise+</Badge>}
                      </Button>
                    </div>
                  );
                })()}
                <p className="text-[10px] text-muted-foreground mt-2">
                  {bot.autonomyLevel === "guided" && "You approve all actions before execution."}
                  {bot.autonomyLevel === "semi-autonomous" && "Low-risk actions auto-execute. High-risk flagged for approval."}
                  {bot.autonomyLevel === "full-autonomy" && "All actions auto-execute. Reporting only."}
                </p>
              </div>

              <div>
                <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-3">Operational Mode</p>
                <div className="flex flex-col gap-2">
                  <Button
                    variant={bot.operationalMode === "sandbox" ? "default" : "outline"}
                    className={cn("justify-start rounded-xl", bot.operationalMode === "sandbox" && "bg-[rgb(245_158_11)] text-white border-[rgb(245_158_11)]")}
                    disabled={controlsMutation.isPending}
                    onClick={() => controlsMutation.mutate({ operationalMode: "sandbox" })}
                    data-testid="btn-mode-sandbox"
                  >
                    <FlaskConical className="h-4 w-4 mr-2" />
                    Sandbox Testing
                  </Button>
                  <Button
                    variant={bot.operationalMode === "live" ? "default" : "outline"}
                    className={cn("justify-start rounded-xl", bot.operationalMode === "live" && "bg-[rgb(34_197_94)] text-white border-[rgb(34_197_94)]")}
                    disabled={controlsMutation.isPending}
                    onClick={() => controlsMutation.mutate({ operationalMode: "live" })}
                    data-testid="btn-mode-live"
                  >
                    <Play className="h-4 w-4 mr-2" />
                    Live Mode
                  </Button>
                  <Button
                    variant={bot.operationalMode === "offline" ? "default" : "outline"}
                    className={cn("justify-start rounded-xl", bot.operationalMode === "offline" && "bg-[rgb(239_68_68)] text-white border-[rgb(239_68_68)]")}
                    disabled={controlsMutation.isPending}
                    onClick={() => controlsMutation.mutate({ operationalMode: "offline" })}
                    data-testid="btn-mode-offline"
                  >
                    <Power className="h-4 w-4 mr-2" />
                    Offline
                  </Button>
                </div>
                <p className="text-[10px] text-muted-foreground mt-2">
                  {bot.operationalMode === "sandbox" && "Testing mode: no real transactions. Safe to experiment."}
                  {bot.operationalMode === "live" && "Live mode: real transactions and revenue generation active."}
                  {bot.operationalMode === "offline" && "Bot is powered down. No activity."}
                </p>
              </div>

              <div>
                <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-3">Quick Status</p>
                <div className="space-y-3">
                  <div className="flex items-center justify-between p-3 rounded-xl border border-border/40">
                    <span className="text-sm text-muted-foreground">Autonomy</span>
                    <Badge variant="secondary" className="rounded-full capitalize" data-testid="status-autonomy">{bot.autonomyLevel}</Badge>
                  </div>
                  <div className="flex items-center justify-between p-3 rounded-xl border border-border/40">
                    <span className="text-sm text-muted-foreground">Mode</span>
                    <Badge
                      variant="secondary"
                      className={cn(
                        "rounded-full capitalize",
                        bot.operationalMode === "live" && "bg-[rgb(34_197_94)]/15 text-[rgb(34_197_94)]",
                        bot.operationalMode === "sandbox" && "bg-[rgb(245_158_11)]/15 text-[rgb(245_158_11)]",
                        bot.operationalMode === "offline" && "bg-[rgb(239_68_68)]/15 text-[rgb(239_68_68)]",
                      )}
                      data-testid="status-mode"
                    >
                      {bot.operationalMode}
                    </Badge>
                  </div>
                  <div className="flex items-center justify-between p-3 rounded-xl border border-border/40">
                    <span className="text-sm text-muted-foreground">Status</span>
                    <Badge
                      variant="secondary"
                      className={cn(
                        "rounded-full capitalize",
                        bot.status === "active" && "bg-[rgb(34_197_94)]/15 text-[rgb(34_197_94)]",
                      )}
                      data-testid="status-bot"
                    >
                      {bot.status}
                    </Badge>
                  </div>
                  <div className="flex items-center justify-between p-3 rounded-xl border border-border/40">
                    <span className="text-sm text-muted-foreground">Tier</span>
                    <Badge variant="outline" className={cn("rounded-full capitalize", TIER_COLORS[bot.tier])} data-testid="status-tier">{bot.tier}</Badge>
                  </div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-3" data-testid="bot-metrics-grid">
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center gap-2 mb-2">
                <Cpu className="h-4 w-4 text-primary" />
                <p className="text-xs text-muted-foreground">CPU Usage</p>
              </div>
              <p className="text-2xl font-bold">{metrics.cpuUsage}%</p>
              <Progress value={metrics.cpuUsage} className="mt-2 h-1.5" />
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center gap-2 mb-2">
                <HardDrive className="h-4 w-4 text-primary" />
                <p className="text-xs text-muted-foreground">Memory</p>
              </div>
              <p className="text-2xl font-bold">{metrics.memoryUsage}%</p>
              <Progress value={metrics.memoryUsage} className="mt-2 h-1.5" />
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center gap-2 mb-2">
                <Activity className="h-4 w-4 text-[rgb(34_197_94)]" />
                <p className="text-xs text-muted-foreground">Uptime</p>
              </div>
              <p className="text-2xl font-bold">{metrics.uptime.toFixed(1)}%</p>
              <Progress value={metrics.uptime} className="mt-2 h-1.5" />
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center gap-2 mb-2">
                <Zap className="h-4 w-4 text-[rgb(245_158_11)]" />
                <p className="text-xs text-muted-foreground">API Calls</p>
              </div>
              <p className="text-2xl font-bold">{metrics.apiCalls.toLocaleString()}</p>
              <p className="text-[10px] text-muted-foreground mt-1">Last 30 days</p>
            </CardContent>
          </Card>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center gap-2 mb-2">
                <CheckCircle2 className="h-4 w-4 text-[rgb(34_197_94)]" />
                <p className="text-xs text-muted-foreground">Tasks Done</p>
              </div>
              <p className="text-2xl font-bold">{metrics.tasksCompleted}</p>
              <p className="text-[10px] text-[rgb(34_197_94)]">
                {Math.round(metrics.tasksCompleted / (metrics.tasksCompleted + metrics.tasksFailed) * 100)}% success
              </p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center gap-2 mb-2">
                <CircleDollarSign className="h-4 w-4 text-[rgb(34_197_94)]" />
                <p className="text-xs text-muted-foreground">Revenue</p>
              </div>
              <p className="text-2xl font-bold">${metrics.revenue.toLocaleString()}</p>
              <p className="text-[10px] text-[rgb(34_197_94)]">This month</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center gap-2 mb-2">
                <Users className="h-4 w-4 text-primary" />
                <p className="text-xs text-muted-foreground">Active Users</p>
              </div>
              <p className="text-2xl font-bold">{metrics.activeUsers}</p>
              <p className="text-[10px] text-muted-foreground">Current session</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center gap-2 mb-2">
                <Star className="h-4 w-4 text-[rgb(245_158_11)]" />
                <p className="text-xs text-muted-foreground">Satisfaction</p>
              </div>
              <p className="text-2xl font-bold">{metrics.satisfaction.toFixed(1)}%</p>
              <Progress value={metrics.satisfaction} className="mt-2 h-1.5" />
            </CardContent>
          </Card>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card data-testid="bot-capabilities-section">
            <CardHeader className="flex flex-row items-center justify-between gap-2 space-y-0 pb-4">
              <CardTitle className="text-lg flex items-center gap-2">
                <Sparkles className="h-5 w-5 text-primary" />
                Niche Specialization
              </CardTitle>
              <Badge variant="secondary" className="rounded-full">{nicheCapabilities.length} niche features</Badge>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 gap-2">
                {nicheCapabilities.map((cap, i) => (
                  <div key={i} className="flex items-center gap-3 p-3 rounded-xl border border-border/40 hover-elevate" data-testid={`capability-${i}`}>
                    <div className="h-8 w-8 rounded-lg bg-primary/10 flex items-center justify-center flex-shrink-0">
                      <Target className="h-4 w-4 text-primary" />
                    </div>
                    <div>
                      <p className="text-sm font-medium">{cap}</p>
                      <p className="text-[10px] text-muted-foreground">Niche-specific</p>
                    </div>
                  </div>
                ))}
              </div>
              {platformCapabilities.length > 0 && (
                <div>
                  <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2">Platform Features ({platformCapabilities.length})</p>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-1.5">
                    {platformCapabilities.map((cap, i) => (
                      <div key={i} className="flex items-center gap-2 p-2 rounded-lg text-sm" data-testid={`platform-cap-${i}`}>
                        <CheckCircle2 className="h-3 w-3 text-muted-foreground flex-shrink-0" />
                        <span className="text-muted-foreground text-xs">{cap}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

          <Card data-testid="bot-extended-features">
            <CardHeader className="flex flex-row items-center justify-between gap-2 space-y-0 pb-4">
              <CardTitle className="text-lg flex items-center gap-2">
                <Layers className="h-5 w-5 text-primary" />
                {bot.division} Platform Features
              </CardTitle>
              <Badge variant="secondary" className="rounded-full">{divisionFeatures.length} features</Badge>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                {divisionFeatures.map((feat, i) => (
                  <div key={i} className="flex items-center gap-2 p-2 rounded-lg text-sm" data-testid={`division-feature-${i}`}>
                    <Zap className="h-3 w-3 text-primary flex-shrink-0" />
                    <span className="text-muted-foreground">{feat}</span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        {(() => {
          const formulas = DIVISION_FORMULAS[bot.division];
          if (!formulas || formulas.length === 0) return null;
          return (
            <Card data-testid="bot-formula-toolkit">
              <CardHeader className="flex flex-row items-center justify-between gap-2 space-y-0 pb-4">
                <CardTitle className="text-lg flex items-center gap-2">
                  <Calculator className="h-5 w-5 text-primary" />
                  High-Profit Formula Toolkit
                </CardTitle>
                <Badge variant="secondary" className="rounded-full">{formulas.length} formulas</Badge>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-2">
                  {formulas.map((f) => (
                    <Button
                      key={f.id}
                      variant="outline"
                      size="sm"
                      className="justify-start text-left"
                      onClick={() => setSelectedFormula(f)}
                      data-testid={`formula-btn-${f.id}`}
                    >
                      <FlaskConical className="h-3.5 w-3.5 flex-shrink-0 text-primary" />
                      <span className="text-xs truncate">{f.name}</span>
                    </Button>
                  ))}
                </div>
              </CardContent>
            </Card>
          );
        })()}

        <Dialog open={!!selectedFormula} onOpenChange={(open) => !open && setSelectedFormula(null)}>
          <DialogContent className="max-w-lg">
            <DialogHeader>
              <DialogTitle className="flex items-center gap-2">
                <Calculator className="h-5 w-5 text-primary" />
                {selectedFormula?.name}
              </DialogTitle>
            </DialogHeader>
            {selectedFormula && (
              <div className="space-y-4">
                <div>
                  <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-1">Description</p>
                  <p className="text-sm">{selectedFormula.description}</p>
                </div>
                <div>
                  <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-1">Formula</p>
                  <div className="p-3 rounded-lg bg-muted/50 border border-border/40 font-mono text-sm break-all">
                    {selectedFormula.formula}
                  </div>
                </div>
                <div className="flex items-center justify-between text-xs text-muted-foreground">
                  <span>Formula #{selectedFormula.id}</span>
                  <Badge variant="outline" className="rounded-full text-[10px]">{bot.division}</Badge>
                </div>
              </div>
            )}
          </DialogContent>
        </Dialog>

        {(() => {
          const registry = DIVISION_API_REGISTRIES[bot.division];
          if (!registry) return null;
          const totalApis = registry.categories.reduce((s, c) => s + c.apis.length, 0);
          return (
            <Card data-testid="bot-api-integrations">
              <CardHeader className="flex flex-row items-center justify-between gap-2 space-y-0 pb-4">
                <CardTitle className="text-lg flex items-center gap-2">
                  <Plug className="h-5 w-5 text-primary" />
                  API Integrations
                </CardTitle>
                <Badge variant="secondary" className="rounded-full">{totalApis} connected</Badge>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {registry.categories.map(cat => (
                    <div key={cat.name}>
                      <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2">{cat.name}</p>
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                        {cat.apis.map(api => {
                          const TIER_ORDER: Record<string, number> = { free: 0, pro: 1, enterprise: 2, elite: 3 };
                          const botTierLevel = TIER_ORDER[bot.tier] ?? 0;
                          const apiTierLevel = TIER_ORDER[api.tier] ?? 0;
                          const tierAllowed = botTierLevel >= apiTierLevel;
                          return (
                            <div
                              key={api.name}
                              className={cn("flex items-center gap-3 p-2.5 rounded-xl border border-border/40", !tierAllowed && "opacity-40")}
                              data-testid={`api-${api.name.toLowerCase().replace(/\s/g, "-")}`}
                            >
                              <div className={cn(
                                "h-8 w-8 rounded-lg flex items-center justify-center flex-shrink-0",
                                tierAllowed ? "bg-green-500/10" : "bg-muted/50"
                              )}>
                                {tierAllowed ? (
                                  <Zap className="h-3.5 w-3.5 text-green-500" />
                                ) : (
                                  <Lock className="h-3.5 w-3.5 text-muted-foreground" />
                                )}
                              </div>
                              <div className="min-w-0 flex-1">
                                <div className="flex items-center gap-2 flex-wrap">
                                  <p className="text-sm font-medium">{api.name}</p>
                                  {!tierAllowed && (
                                    <Badge variant="outline" className="rounded-full text-[9px] capitalize">{api.tier}+</Badge>
                                  )}
                                </div>
                                <p className="text-[10px] text-muted-foreground truncate">{api.description}</p>
                              </div>
                            </div>
                          );
                        })}
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          );
        })()}

        <BotMemorySection botId={botId} />

        <Card data-testid="bot-prospectus">
          <CardHeader className="pb-4">
            <CardTitle className="text-lg flex items-center gap-2">
              <Target className="h-5 w-5 text-primary" />
              Investment Prospectus
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="space-y-4">
                <div>
                  <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2">Business Model</p>
                  <div className="space-y-2">
                    <div className="flex items-center gap-2">
                      <CircleDollarSign className="h-4 w-4 text-[rgb(34_197_94)]" />
                      <span className="text-sm">{bot.revenueModel || "SaaS Subscription"}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <TrendingUp className="h-4 w-4 text-primary" />
                      <span className="text-sm">{bot.priceRange || "Contact for pricing"}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <Users className="h-4 w-4 text-muted-foreground" />
                      <span className="text-sm">{bot.targetUsers || "Enterprise & SMB"}</span>
                    </div>
                  </div>
                </div>
                <div>
                  <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2">Performance</p>
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">Monthly Revenue</span>
                      <span className="font-medium">${metrics.revenue.toLocaleString()}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">Active Users</span>
                      <span className="font-medium">{metrics.activeUsers}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">Tasks Completed</span>
                      <span className="font-medium">{metrics.tasksCompleted}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">Uptime SLA</span>
                      <span className="font-medium">{metrics.uptime.toFixed(1)}%</span>
                    </div>
                  </div>
                </div>
              </div>

              <div className="space-y-4">
                <div>
                  <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2">Technical Specs</p>
                  <div className="space-y-2">
                    <div className="flex items-center gap-2">
                      <Server className="h-4 w-4 text-muted-foreground" />
                      <span className="text-sm">Multi-region cloud deployment</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <Database className="h-4 w-4 text-muted-foreground" />
                      <span className="text-sm">Real-time data processing</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <Shield className="h-4 w-4 text-muted-foreground" />
                      <span className="text-sm">SOC 2 Type II compliant</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <Lock className="h-4 w-4 text-muted-foreground" />
                      <span className="text-sm">End-to-end encryption</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <Network className="h-4 w-4 text-muted-foreground" />
                      <span className="text-sm">RESTful & WebSocket APIs</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <Globe className="h-4 w-4 text-muted-foreground" />
                      <span className="text-sm">Global CDN with edge caching</span>
                    </div>
                  </div>
                </div>
                <div>
                  <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2">Avg Response Time</p>
                  <p className="text-2xl font-bold">{metrics.responseTime}ms</p>
                  <p className="text-[10px] text-muted-foreground">P95 latency</p>
                </div>
              </div>

              <div>
                <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2">Competitive Advantages</p>
                <div className="space-y-2">
                  {COMPETITIVE_ADVANTAGES.map((adv, i) => (
                    <div key={i} className="flex items-start gap-2">
                      <Rocket className="h-3.5 w-3.5 text-primary mt-0.5 flex-shrink-0" />
                      <span className="text-sm text-muted-foreground">{adv}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card data-testid="bot-system-prompt">
          <CardHeader className="pb-4">
            <CardTitle className="text-lg flex items-center gap-2">
              <MessageSquare className="h-5 w-5 text-primary" />
              System Prompt
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="p-4 rounded-xl bg-muted/30 border border-border/40">
              <p className="text-sm leading-relaxed whitespace-pre-wrap" data-testid="bot-system-prompt-text">{bot.systemPrompt}</p>
            </div>
          </CardContent>
        </Card>

        <Card data-testid="bot-traits-section">
          <CardHeader className="pb-4">
            <CardTitle className="text-lg flex items-center gap-2">
              <BarChart3 className="h-5 w-5 text-primary" />
              Configuration & Traits
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              {Object.entries(bot.traits as Record<string, string>).map(([key, value]) => (
                <div key={key} className="p-3 rounded-xl border border-border/40">
                  <p className="text-[10px] text-muted-foreground uppercase tracking-wider">{key}</p>
                  <p className="text-sm font-medium mt-1 capitalize">{String(value)}</p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </AppShell>
  );
}
