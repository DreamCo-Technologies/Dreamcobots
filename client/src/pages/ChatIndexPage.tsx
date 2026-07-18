import { useState, useEffect, useMemo } from "react";
import { useLocation } from "wouter";
import { useQuery, useMutation } from "@tanstack/react-query";
import Seo from "@/components/Seo";
import AppShell from "@/components/AppShell";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Skeleton } from "@/components/ui/skeleton";
import { cn } from "@/lib/utils";
import { apiRequest } from "@/lib/queryClient";
import { useCreateConversation } from "@/hooks/use-conversations";
import { useBots } from "@/hooks/use-bots";
import { useEmpireOverview } from "@/hooks/use-empire";
import { useToast } from "@/hooks/use-toast";
import {
  Send, Map, Hammer, Zap, GraduationCap, ShoppingCart, Search,
  Bot, Sparkles, Terminal, ChevronRight, Star, Building2,
  Code2, Cpu, DollarSign, Activity, Lock, CheckCircle2,
  CreditCard, Crown, Rocket, Loader2,
} from "lucide-react";

type ChatMode = "plan" | "build" | "execute" | "teach";

const MODES: { id: ChatMode; label: string; icon: typeof Map; color: string; bg: string; desc: string; prompts: string[] }[] = [
  {
    id: "plan", label: "Plan", icon: Map, color: "text-blue-400", bg: "bg-blue-500/10 border-blue-500/30 hover:border-blue-400/60",
    desc: "Strategy & roadmaps",
    prompts: [
      "Map out a 90-day revenue plan for my AI-powered SaaS.",
      "Design the architecture for an autonomous content empire.",
      "Break my business idea into phases with revenue milestones.",
      "Create a competitive analysis of the top 10 players in my niche.",
    ],
  },
  {
    id: "build", label: "Build", icon: Hammer, color: "text-amber-400", bg: "bg-amber-500/10 border-amber-500/30 hover:border-amber-400/60",
    desc: "Create & implement",
    prompts: [
      "Build an automation pipeline that generates passive income.",
      "Help me create a full landing page for my AI product launch.",
      "Set up an automated lead generation system for my business.",
      "Design a bot workflow that handles customer onboarding end-to-end.",
    ],
  },
  {
    id: "execute", label: "Execute", icon: Zap, color: "text-green-400", bg: "bg-green-500/10 border-green-500/30 hover:border-green-400/60",
    desc: "Take action & results",
    prompts: [
      "Write 5 high-converting email sequences for my product launch.",
      "Generate a week of social media content for my AI startup.",
      "Create a pitch deck outline that closes investors.",
      "Draft a partnership proposal for a strategic alliance.",
    ],
  },
  {
    id: "teach", label: "Teach", icon: GraduationCap, color: "text-purple-400", bg: "bg-purple-500/10 border-purple-500/30 hover:border-purple-400/60",
    desc: "Learn & master skills",
    prompts: [
      "Teach me how to use AI to automate my entire business workflow.",
      "Explain prompt engineering like I'm a beginner entrepreneur.",
      "Walk me through building my first revenue-generating bot.",
      "Show me the top money-making strategies using AI tools today.",
    ],
  },
];

const CODE_LINES = [
  { t: 0, text: "// DreamCo Empire OS — Live Bot Monitor", cls: "text-slate-500" },
  { t: 200, text: "import { EmpireOS } from '@dreamco/core';", cls: "text-blue-400" },
  { t: 400, text: "", cls: "" },
  { t: 600, text: "const empire = new EmpireOS({", cls: "text-slate-200" },
  { t: 700, text: "  bots: 1051,", cls: "text-emerald-400" },
  { t: 800, text: "  divisions: 45,", cls: "text-emerald-400" },
  { t: 900, text: "  autonomy: 'full-auto',", cls: "text-yellow-400" },
  { t: 1000, text: "  revenue: '$18.4M ARR',", cls: "text-emerald-400" },
  { t: 1100, text: "});", cls: "text-slate-200" },
  { t: 1300, text: "", cls: "" },
  { t: 1400, text: "// Active bot fleet status", cls: "text-slate-500" },
  { t: 1600, text: "await empire.deploy({", cls: "text-slate-200" },
  { t: 1700, text: "  mode: 'wealth-generation',", cls: "text-yellow-400" },
  { t: 1800, text: "  targets: ['leads', 'content', 'deals'],", cls: "text-blue-400" },
  { t: 1900, text: "  schedule: '24/7',", cls: "text-emerald-400" },
  { t: 2000, text: "});", cls: "text-slate-200" },
  { t: 2200, text: "", cls: "" },
  { t: 2300, text: "// ✅ Empire online — all systems go", cls: "text-emerald-500" },
];

function CodexPanel({ selectedBot }: { selectedBot: any }) {
  const [visibleLines, setVisibleLines] = useState(0);
  const [cursor, setCursor] = useState(true);

  useEffect(() => {
    setVisibleLines(0);
    let i = 0;
    const timers: ReturnType<typeof setTimeout>[] = [];
    CODE_LINES.forEach((line, idx) => {
      const t = setTimeout(() => { setVisibleLines(idx + 1); }, line.t);
      timers.push(t);
    });
    return () => timers.forEach(clearTimeout);
  }, []);

  useEffect(() => {
    const t = setInterval(() => setCursor(c => !c), 530);
    return () => clearInterval(t);
  }, []);

  return (
    <div className="h-full flex flex-col bg-[#0d1117] rounded-2xl border border-white/10 overflow-hidden shadow-2xl">
      <div className="flex items-center gap-2 px-4 py-3 border-b border-white/8 bg-[#161b22]">
        <div className="flex gap-1.5">
          <span className="h-3 w-3 rounded-full bg-red-500/80" />
          <span className="h-3 w-3 rounded-full bg-yellow-500/80" />
          <span className="h-3 w-3 rounded-full bg-green-500/80" />
        </div>
        <div className="flex items-center gap-2 ml-2">
          <Code2 className="h-3.5 w-3.5 text-slate-400" />
          <span className="text-xs text-slate-400 font-mono">empire-os.ts</span>
        </div>
        <div className="ml-auto flex items-center gap-1.5">
          <span className="h-1.5 w-1.5 rounded-full bg-green-400 animate-pulse" />
          <span className="text-[10px] text-green-400 font-mono">LIVE</span>
        </div>
      </div>

      <ScrollArea className="flex-1">
        <div className="p-4 font-mono text-[13px] leading-6">
          {CODE_LINES.slice(0, visibleLines).map((line, i) => (
            <div key={i} className={cn("whitespace-pre", line.cls || "text-slate-300")}>
              <span className="text-slate-600 select-none mr-4 text-[11px]">{String(i + 1).padStart(2, "0")}</span>
              {line.text}
              {i === visibleLines - 1 && visibleLines < CODE_LINES.length && (
                <span className={cn("inline-block w-2 h-4 bg-primary/80 ml-0.5 align-middle", cursor ? "opacity-100" : "opacity-0")} />
              )}
            </div>
          ))}
          {visibleLines >= CODE_LINES.length && (
            <div className="text-slate-300">
              <span className="text-slate-600 select-none mr-4 text-[11px]">{String(CODE_LINES.length + 1).padStart(2, "0")}</span>
              <span className={cn("inline-block w-2 h-4 bg-primary/80 ml-0.5 align-middle", cursor ? "opacity-100" : "opacity-0")} />
            </div>
          )}
        </div>
      </ScrollArea>

      {selectedBot && (
        <div className="border-t border-white/8 bg-[#161b22] p-3">
          <div className="flex items-center gap-2 mb-2">
            <Terminal className="h-3 w-3 text-green-400" />
            <span className="text-[10px] font-mono text-green-400">ACTIVE BOT</span>
          </div>
          <div className="font-mono text-[11px] space-y-1">
            <div className="flex justify-between">
              <span className="text-slate-400">name:</span>
              <span className="text-blue-300 truncate ml-2 max-w-[160px]">{selectedBot.displayName}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">division:</span>
              <span className="text-emerald-300">{selectedBot.division}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">tier:</span>
              <span className="text-yellow-300">{selectedBot.tier ?? "free"}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">status:</span>
              <span className="text-green-400">● online</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

const TIER_COLORS: Record<string, string> = {
  free: "bg-slate-500/20 text-slate-300 border-slate-500/30",
  pro: "bg-blue-500/20 text-blue-300 border-blue-500/30",
  elite: "bg-purple-500/20 text-purple-300 border-purple-500/30",
  enterprise: "bg-amber-500/20 text-amber-300 border-amber-500/30",
};

const PLAN_META: Record<string, { icon: typeof Bot; color: string; highlight: boolean; perks: string[] }> = {
  free:       { icon: Bot,     color: "text-slate-400",  highlight: false, perks: ["5 bots", "Guided mode", "All 45 divisions", "Community support"] },
  pro:        { icon: Rocket,  color: "text-blue-400",   highlight: true,  perks: ["50 bots", "Semi-auto mode", "Advanced analytics", "Priority API access"] },
  enterprise: { icon: Star,    color: "text-amber-400",  highlight: false, perks: ["150 bots", "Full autonomy", "All 269 APIs", "Dedicated support"] },
  elite:      { icon: Crown,   color: "text-purple-400", highlight: false, perks: ["Unlimited bots", "White-glove onboarding", "Custom divisions", "Dedicated infra"] },
};

function PricingPlansTab() {
  const { toast } = useToast();
  const [yearly, setYearly] = useState(false);

  const productsQuery = useQuery<{ products: any[] }>({
    queryKey: ["/api/stripe/products"],
  });

  const checkoutMutation = useMutation({
    mutationFn: async (priceId: string) => {
      const res = await apiRequest("POST", "/api/stripe/checkout", { priceId });
      return res.json();
    },
    onSuccess: (data) => {
      if (data?.url) {
        window.location.href = data.url;
      } else {
        toast({ title: "Checkout failed", description: "No checkout URL returned.", variant: "destructive" });
      }
    },
    onError: (err: any) => {
      toast({ title: "Checkout failed", description: err?.message ?? "Something went wrong.", variant: "destructive" });
    },
  });

  const products = productsQuery.data?.products ?? [];

  const tierOrder = ["free", "pro", "enterprise", "elite"];
  const sorted = [...products].sort((a, b) => {
    const ai = tierOrder.indexOf(a.metadata?.tier ?? "");
    const bi = tierOrder.indexOf(b.metadata?.tier ?? "");
    return ai - bi;
  });

  if (productsQuery.isLoading) {
    return (
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 p-6">
        {Array.from({ length: 4 }).map((_, i) => <Skeleton key={i} className="h-56 rounded-2xl" />)}
      </div>
    );
  }

  if (sorted.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-16 gap-3 text-center">
        <CreditCard className="h-10 w-10 text-muted-foreground/40" />
        <p className="font-semibold">Stripe not connected yet</p>
        <p className="text-sm text-muted-foreground max-w-xs">
          Add your <span className="font-mono text-xs bg-muted px-1 py-0.5 rounded">STRIPE_SECRET_KEY</span> and{" "}
          <span className="font-mono text-xs bg-muted px-1 py-0.5 rounded">STRIPE_PUBLISHABLE_KEY</span> environment secrets to enable live checkout.
        </p>
      </div>
    );
  }

  return (
    <div className="px-6 py-5">
      <div className="flex items-center justify-center gap-3 mb-6">
        <span className={cn("text-sm font-medium", !yearly ? "text-foreground" : "text-muted-foreground")}>Monthly</span>
        <button
          onClick={() => setYearly(v => !v)}
          className={cn("relative h-6 w-11 rounded-full border-2 transition-colors", yearly ? "bg-primary border-primary" : "bg-muted border-border")}
          data-testid="billing-toggle"
        >
          <span className={cn("absolute top-0.5 left-0.5 h-4 w-4 rounded-full bg-white shadow transition-transform", yearly && "translate-x-5")} />
        </button>
        <span className={cn("text-sm font-medium", yearly ? "text-foreground" : "text-muted-foreground")}>
          Yearly <Badge className="ml-1 text-[10px] h-4 bg-green-500/20 text-green-400 border-green-500/30">20% off</Badge>
        </span>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        {sorted.map((product) => {
          const tierKey = (product.metadata?.tier ?? "free").toLowerCase();
          const meta = PLAN_META[tierKey] ?? PLAN_META.free;
          const Icon = meta.icon;
          const prices = product.prices ?? [];
          const monthlyPrice = prices.find((p: any) => p.recurring?.interval === "month");
          const yearlyPrice = prices.find((p: any) => p.recurring?.interval === "year");
          const activePrice = yearly ? (yearlyPrice ?? monthlyPrice) : monthlyPrice;
          const amount = activePrice ? activePrice.unit_amount / 100 : 0;
          const isFree = amount === 0;
          const priceDisplay = isFree ? "Free" : `$${amount.toLocaleString()}/${yearly ? "yr" : "mo"}`;

          return (
            <div
              key={product.id}
              className={cn(
                "relative rounded-2xl border p-5 flex flex-col gap-4 transition-all",
                meta.highlight
                  ? "border-primary/60 bg-primary/5 shadow-lg shadow-primary/10"
                  : "border-border/60 bg-card/60"
              )}
              data-testid={`plan-card-${tierKey}`}
            >
              {meta.highlight && (
                <span className="absolute -top-3 left-1/2 -translate-x-1/2 text-[11px] font-bold px-3 py-1 rounded-full bg-primary text-primary-foreground">
                  MOST POPULAR
                </span>
              )}
              <div className="flex items-center gap-3">
                <span className={cn("inline-flex h-10 w-10 items-center justify-center rounded-xl bg-card border", meta.highlight ? "border-primary/40" : "border-border/50")}>
                  <Icon className={cn("h-5 w-5", meta.color)} />
                </span>
                <div>
                  <p className="font-bold text-base">{product.name}</p>
                  <Badge className={cn("text-[10px] border mt-0.5", TIER_COLORS[tierKey] ?? TIER_COLORS.free)}>{tierKey}</Badge>
                </div>
              </div>

              <div>
                <span className="text-3xl font-extrabold">{priceDisplay}</span>
                {!isFree && <span className="text-sm text-muted-foreground ml-1">/ {product.metadata?.botLimit ?? "?"} bots</span>}
              </div>

              <ul className="space-y-1.5 flex-1">
                {(meta.perks).map((perk) => (
                  <li key={perk} className="flex items-center gap-2 text-sm text-muted-foreground">
                    <CheckCircle2 className="h-3.5 w-3.5 text-green-400 flex-shrink-0" />
                    {perk}
                  </li>
                ))}
              </ul>

              <Button
                className={cn("w-full rounded-xl font-semibold", meta.highlight ? "bg-gradient-to-r from-primary to-accent text-primary-foreground" : "")}
                variant={meta.highlight ? "default" : "outline"}
                disabled={isFree || checkoutMutation.isPending}
                onClick={() => {
                  if (isFree) {
                    return;
                  }
                  if (!activePrice?.id) {
                    toast({ title: "Price not found", description: "Could not find a price for this plan.", variant: "destructive" });
                    return;
                  }
                  checkoutMutation.mutate(activePrice.id);
                }}
                data-testid={`subscribe-${tierKey}`}
              >
                {checkoutMutation.isPending ? (
                  <Loader2 className="h-4 w-4 animate-spin mr-2" />
                ) : isFree ? (
                  <><CheckCircle2 className="h-4 w-4 mr-2" />Current Plan</>
                ) : (
                  <><CreditCard className="h-4 w-4 mr-2" />Subscribe</>
                )}
              </Button>
            </div>
          );
        })}
      </div>
    </div>
  );
}

function BuyBotsModal({ open, onClose }: { open: boolean; onClose: () => void }) {
  const [tab, setTab] = useState<"bots" | "plans">("plans");
  const [search, setSearch] = useState("");
  const [division, setDivision] = useState("all");
  const [tierFilter, setTierFilter] = useState("all");
  const bots = useBots();
  const { toast } = useToast();

  const productsQuery = useQuery<{ products: any[] }>({
    queryKey: ["/api/stripe/products"],
    enabled: open,
  });

  const checkoutMutation = useMutation({
    mutationFn: async (priceId: string) => {
      const baseUrl = window.location.origin;
      const res = await apiRequest("POST", "/api/stripe/checkout", {
        priceId,
        successUrl: `${baseUrl}/?checkout=success`,
        cancelUrl: `${baseUrl}/?checkout=canceled`,
      });
      return res.json();
    },
    onSuccess: (data) => {
      if (data?.url) {
        window.location.href = data.url;
      } else {
        toast({ title: "Checkout failed", description: "No checkout URL returned.", variant: "destructive" });
      }
    },
    onError: (err: any) => {
      toast({ title: "Checkout failed", description: err?.message ?? "Something went wrong.", variant: "destructive" });
    },
  });

  const tierToPriceId = useMemo(() => {
    const products = productsQuery.data?.products ?? [];
    const map: Record<string, string> = {};
    for (const product of products) {
      const tierKey = product.metadata?.tier;
      if (!tierKey) continue;
      const monthly = product.prices?.find((p: any) => p.recurring?.interval === "month");
      if (monthly) map[tierKey] = monthly.id;
    }
    return map;
  }, [productsQuery.data]);

  const allBots = bots.data ?? [];
  const divisions = useMemo(() => {
    const divs = Array.from(new Set(allBots.map((b) => b.division).filter(Boolean)));
    return divs.sort();
  }, [allBots]);

  const filtered = useMemo(() => {
    return allBots.filter((b) => {
      const matchSearch = !search || b.displayName.toLowerCase().includes(search.toLowerCase()) || (b.description ?? "").toLowerCase().includes(search.toLowerCase());
      const matchDiv = division === "all" || b.division === division;
      const matchTier = tierFilter === "all" || (b.tier ?? "free") === tierFilter;
      return matchSearch && matchDiv && matchTier;
    });
  }, [allBots, search, division, tierFilter]);

  return (
    <Dialog open={open} onOpenChange={(v) => !v && onClose()}>
      <DialogContent className="max-w-4xl h-[85vh] flex flex-col p-0 gap-0 overflow-hidden">
        <DialogHeader className="px-6 py-4 border-b border-border/60 flex-shrink-0">
          <DialogTitle className="flex items-center gap-2 text-xl">
            <ShoppingCart className="h-5 w-5 text-primary" />
            Bot Marketplace
            <Badge variant="secondary" className="ml-2">{allBots.length} bots</Badge>
          </DialogTitle>
        </DialogHeader>

        {/* Tab switcher */}
        <div className="flex border-b border-border/40 flex-shrink-0">
          {(["plans", "bots"] as const).map((t) => (
            <button
              key={t}
              onClick={() => setTab(t)}
              className={cn(
                "flex-1 py-3 text-sm font-semibold transition-colors border-b-2 -mb-px",
                tab === t
                  ? "border-primary text-primary"
                  : "border-transparent text-muted-foreground hover:text-foreground"
              )}
              data-testid={`tab-${t}`}
            >
              {t === "plans" ? "💳 Subscription Plans" : "🤖 Browse Bots"}
            </button>
          ))}
        </div>

        {tab === "plans" ? (
          <ScrollArea className="flex-1">
            <PricingPlansTab />
          </ScrollArea>
        ) : (
          <>
            <div className="px-6 py-3 border-b border-border/40 flex flex-wrap gap-3 flex-shrink-0">
              <div className="relative flex-1 min-w-[200px]">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  placeholder="Search bots by name or capability..."
                  className="pl-9 rounded-xl"
                  data-testid="bot-search"
                />
              </div>
              <select
                value={division}
                onChange={(e) => setDivision(e.target.value)}
                className="rounded-xl border border-border/60 bg-card px-3 py-2 text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-ring/30"
                data-testid="filter-division"
              >
                <option value="all">All Divisions</option>
                {divisions.slice(0, 45).map((d) => (
                  <option key={d} value={d}>{d}</option>
                ))}
              </select>
              <select
                value={tierFilter}
                onChange={(e) => setTierFilter(e.target.value)}
                className="rounded-xl border border-border/60 bg-card px-3 py-2 text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-ring/30"
                data-testid="filter-tier"
              >
                <option value="all">All Tiers</option>
                <option value="free">Free</option>
                <option value="pro">Pro</option>
                <option value="elite">Elite</option>
                <option value="enterprise">Enterprise</option>
              </select>
            </div>

            <ScrollArea className="flex-1 px-6 py-4">
              {bots.isLoading ? (
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  {Array.from({ length: 8 }).map((_, i) => (
                    <Skeleton key={i} className="h-32 rounded-xl" />
                  ))}
                </div>
              ) : (
                <>
                  <p className="text-xs text-muted-foreground mb-3">Showing {filtered.length} of {allBots.length} bots</p>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    {filtered.slice(0, 100).map((bot) => {
                      const tierKey = (bot.tier ?? "free").toLowerCase();
                      const tierClass = TIER_COLORS[tierKey] ?? TIER_COLORS.free;
                      const isFree = tierKey === "free";
                      const priceId = tierToPriceId[tierKey];
                      return (
                        <div
                          key={bot.id}
                          className="rounded-xl border border-border/60 bg-card/60 p-4 hover:border-primary/40 hover:bg-card transition-all group"
                          data-testid={`bot-card-${bot.id}`}
                        >
                          <div className="flex items-start justify-between gap-2 mb-2">
                            <div className="flex items-center gap-2 min-w-0">
                              <span className="inline-flex h-8 w-8 items-center justify-center rounded-lg bg-primary/10 border border-primary/20 flex-shrink-0">
                                <Bot className="h-4 w-4 text-primary" />
                              </span>
                              <div className="min-w-0">
                                <p className="font-semibold text-sm truncate">{bot.displayName}</p>
                                <p className="text-[11px] text-muted-foreground truncate">{bot.division}</p>
                              </div>
                            </div>
                            <Badge className={cn("text-[10px] border flex-shrink-0", tierClass)}>
                              {bot.tier ?? "free"}
                            </Badge>
                          </div>
                          <p className="text-xs text-muted-foreground line-clamp-2 mb-3">
                            {bot.description ?? "Specialized AI bot for autonomous task execution."}
                          </p>
                          {bot.category && (
                            <div className="flex flex-wrap gap-1 mb-3">
                              <span className="text-[10px] px-1.5 py-0.5 rounded-md bg-muted text-muted-foreground">{bot.category}</span>
                            </div>
                          )}
                          <div className="flex items-center justify-between">
                            <span className="text-sm font-bold text-primary capitalize">{isFree ? "Free" : tierKey + " tier"}</span>
                            <Button
                              size="sm"
                              variant={isFree ? "outline" : "default"}
                              className="rounded-lg text-xs h-8"
                              disabled={!isFree && checkoutMutation.isPending}
                              onClick={() => {
                                if (isFree) {
                                  toast({ title: `${bot.displayName} activated!`, description: "Bot added to your fleet." });
                                } else if (priceId) {
                                  checkoutMutation.mutate(priceId);
                                } else {
                                  setTab("plans");
                                }
                              }}
                              data-testid={`buy-bot-${bot.id}`}
                            >
                              {isFree ? (
                                <><CheckCircle2 className="h-3 w-3 mr-1" />Activate</>
                              ) : checkoutMutation.isPending ? (
                                <Loader2 className="h-3 w-3 animate-spin mr-1" />
                              ) : (
                                <><CreditCard className="h-3 w-3 mr-1" />Subscribe</>
                              )}
                            </Button>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                  {filtered.length > 100 && (
                    <p className="text-center text-xs text-muted-foreground mt-4 py-2">
                      Showing first 100 results. Use search or filters to narrow down.
                    </p>
                  )}
                </>
              )}
            </ScrollArea>
          </>
        )}
      </DialogContent>
    </Dialog>
  );
}

export default function ChatIndexPage() {
  const [, navigate] = useLocation();
  const { toast } = useToast();
  const createConversation = useCreateConversation();
  const bots = useBots();
  const empire = useEmpireOverview();

  const [botSlug, setBotSlug] = useState<string | undefined>(undefined);
  const [mode, setMode] = useState<ChatMode>("build");

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const checkout = params.get("checkout");
    if (checkout === "success") {
      toast({ title: "Payment successful! 🎉", description: "Your Empire tier has been upgraded. Enjoy your new bots!" });
      window.history.replaceState({}, "", "/");
    } else if (checkout === "canceled") {
      toast({ title: "Checkout canceled", description: "No charge was made. You can subscribe anytime." });
      window.history.replaceState({}, "", "/");
    }
  }, []);

  const [input, setInput] = useState("");
  const [buyOpen, setBuyOpen] = useState(false);

  const selectedBot = useMemo(() => {
    const list = bots.data ?? [];
    const slug = botSlug ?? list.find((b) => b.isDefault)?.slug ?? list[0]?.slug;
    return list.find((b) => b.slug === slug);
  }, [botSlug, bots.data]);

  const modeConfig = MODES.find((m) => m.id === mode)!;

  async function handleSend(text?: string) {
    const content = (text ?? input).trim();
    if (!content) return;
    try {
      const created = await createConversation.mutateAsync({ title: content.slice(0, 60) } as any);
      navigate(`/c/${created.id}`);
    } catch (e: any) {
      toast({ title: "Couldn't start chat", description: e?.message, variant: "destructive" });
    }
  }

  const totalBots = empire.data?.totalBots ?? 1051;

  return (
    <AppShell selectedBotSlug={botSlug} onBotChange={setBotSlug}>
      <Seo
        title="DreamCo Empire OS — Home"
        description="1051 AI bots working for you. ChatGPT meets Codex — autonomous wealth generation."
      />

      <BuyBotsModal open={buyOpen} onClose={() => setBuyOpen(false)} />

      <div className="h-full grid grid-cols-1 xl:grid-cols-[1fr_420px] gap-5">
        {/* ─── LEFT: ChatGPT panel ─── */}
        <div className="flex flex-col gap-4">
          {/* Header */}
          <div className="flex items-center gap-3">
            <span className="inline-flex h-10 w-10 items-center justify-center rounded-2xl bg-gradient-to-br from-primary/25 to-accent/15 border border-primary/30 flex-shrink-0">
              <Sparkles className="h-5 w-5 text-primary" />
            </span>
            <div className="min-w-0 flex-1">
              <h1 className="text-2xl font-bold leading-tight">DreamCo Empire OS</h1>
              <p className="text-sm text-muted-foreground">{totalBots.toLocaleString()} bots ready · Full Autonomy</p>
            </div>
            <Button
              onClick={() => setBuyOpen(true)}
              className="flex-shrink-0 rounded-xl px-4 py-2 bg-gradient-to-r from-primary to-accent text-primary-foreground shadow-md hover:shadow-lg hover:shadow-primary/25 hover:-translate-y-0.5 transition-all gap-2 font-semibold"
              data-testid="buy-bots-btn"
            >
              <ShoppingCart className="h-4 w-4" />
              Buy Bots
              <Badge className="ml-0.5 text-[10px] h-4 px-1.5 bg-white/20 text-white border-0">
                {totalBots}
              </Badge>
            </Button>
          </div>

          {/* Mode tabs */}
          <div className="grid grid-cols-4 gap-2">
            {MODES.map((m) => {
              const Icon = m.icon;
              const active = mode === m.id;
              return (
                <button
                  key={m.id}
                  onClick={() => setMode(m.id)}
                  className={cn(
                    "flex flex-col items-center gap-1.5 rounded-xl border px-2 py-3 text-center transition-all",
                    active ? cn("border-primary/60 bg-primary/10 shadow-sm shadow-primary/20", m.color) : cn("border-border/50 bg-card/40 text-muted-foreground hover:text-foreground", m.bg)
                  )}
                  data-testid={`mode-${m.id}`}
                >
                  <Icon className={cn("h-4 w-4", active ? m.color : "")} />
                  <span className="text-xs font-semibold">{m.label}</span>
                  <span className="text-[10px] opacity-70 hidden sm:block">{m.desc}</span>
                </button>
              );
            })}
          </div>

          {/* Suggested prompts */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
            {modeConfig.prompts.map((prompt, i) => (
              <button
                key={i}
                onClick={() => handleSend(prompt)}
                className="text-left rounded-xl border border-border/50 bg-card/40 px-4 py-3 text-sm text-muted-foreground hover:text-foreground hover:border-primary/40 hover:bg-card/70 transition-all group"
                data-testid={`prompt-${i}`}
              >
                <span className="flex items-start gap-2">
                  <ChevronRight className="h-3.5 w-3.5 mt-0.5 text-primary/60 flex-shrink-0 group-hover:text-primary transition-colors" />
                  <span className="line-clamp-2">{prompt}</span>
                </span>
              </button>
            ))}
          </div>

          {/* Stats row */}
          <div className="grid grid-cols-3 gap-3">
            {[
              { icon: Cpu, label: "Active Bots", value: totalBots.toLocaleString() },
              { icon: Building2, label: "Divisions", value: "45" },
              { icon: Activity, label: "Autonomy", value: "Full Auto" },
            ].map(({ icon: Icon, label, value }) => (
              <div key={label} className="rounded-xl border border-border/40 bg-card/30 px-3 py-2.5 text-center">
                <Icon className="h-4 w-4 text-primary mx-auto mb-1" />
                <p className="text-base font-bold">{value}</p>
                <p className="text-[10px] text-muted-foreground">{label}</p>
              </div>
            ))}
          </div>

          {/* Input bar */}
          <div className="rounded-2xl border border-border/60 bg-card/60 backdrop-blur p-3 shadow-lg">
            <div className="flex gap-2 items-end">
              <div className="flex-1">
                <textarea
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  placeholder={`${modeConfig.desc} — describe your goal or pick a prompt above…`}
                  rows={2}
                  className="w-full resize-none rounded-xl border border-border/60 bg-background/50 px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-ring/30 focus:border-primary/60 transition-all placeholder:text-muted-foreground/60"
                  onKeyDown={(e) => {
                    if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); handleSend(); }
                  }}
                  data-testid="chat-input"
                />
              </div>
              <Button
                onClick={() => handleSend()}
                disabled={!input.trim() || createConversation.isPending}
                className="rounded-xl px-4 py-3 h-auto bg-gradient-to-r from-primary to-accent text-primary-foreground shadow-md hover:shadow-lg hover:shadow-primary/25 hover:-translate-y-0.5 active:translate-y-0 transition-all flex-shrink-0"
                data-testid="send-btn"
              >
                <Send className="h-4 w-4" />
              </Button>
            </div>
            <div className="flex items-center justify-between mt-2 px-1">
              <p className="text-[11px] text-muted-foreground">↵ Enter to send · Shift+Enter for newline</p>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setBuyOpen(true)}
                className="rounded-xl text-xs border-primary/40 text-primary hover:bg-primary/10 hover:border-primary/70 gap-1.5 h-8 font-semibold"
                data-testid="buy-bots-btn"
              >
                <ShoppingCart className="h-3.5 w-3.5" />
                Buy Bots
                <Badge className="ml-1 text-[9px] h-4 px-1 bg-primary/20 text-primary border-primary/30">
                  {totalBots}
                </Badge>
              </Button>
            </div>
          </div>
        </div>

        {/* ─── RIGHT: Codex panel ─── */}
        <div className="hidden xl:flex flex-col gap-4">
          <div className="flex-1 min-h-0">
            <CodexPanel selectedBot={selectedBot} />
          </div>

          {/* Quick actions under code panel */}
          <div className="grid grid-cols-2 gap-2">
            {[
              { icon: ShoppingCart, label: "Buy Bots", sub: `${totalBots} available`, action: () => setBuyOpen(true), primary: true },
              { icon: Star, label: "Bot Fleet", sub: "Manage all bots", action: () => navigate("/bots"), primary: false },
              { icon: DollarSign, label: "Revenue", sub: "$18.4M ARR", action: () => navigate("/revenue"), primary: false },
              { icon: Lock, label: "Full Auto", sub: "Autonomy on", action: () => navigate("/autonomy"), primary: false },
            ].map(({ icon: Icon, label, sub, action, primary }) => (
              <button
                key={label}
                onClick={action}
                className={cn(
                  "flex items-center gap-3 rounded-xl border px-3 py-3 text-left transition-all hover:-translate-y-0.5",
                  primary
                    ? "border-primary/40 bg-primary/8 hover:bg-primary/14 hover:border-primary/60"
                    : "border-border/50 bg-card/40 hover:bg-card/70 hover:border-border"
                )}
                data-testid={`quick-${label.toLowerCase().replace(/\s/g, "-")}`}
              >
                <span className={cn("inline-flex h-8 w-8 items-center justify-center rounded-lg flex-shrink-0",
                  primary ? "bg-primary/15" : "bg-muted/60"
                )}>
                  <Icon className={cn("h-4 w-4", primary ? "text-primary" : "text-muted-foreground")} />
                </span>
                <div className="min-w-0">
                  <p className={cn("text-sm font-semibold", primary ? "text-primary" : "")}>{label}</p>
                  <p className="text-[11px] text-muted-foreground">{sub}</p>
                </div>
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Mobile Buy Bots button (shown below on small screens) */}
      <div className="xl:hidden mt-4 flex justify-center">
        <Button
          onClick={() => setBuyOpen(true)}
          className="rounded-xl px-6 py-3 bg-gradient-to-r from-primary to-accent text-primary-foreground shadow-md gap-2"
          data-testid="buy-bots-mobile"
        >
          <ShoppingCart className="h-4 w-4" />
          Buy Bots ({totalBots})
        </Button>
      </div>
    </AppShell>
  );
}
