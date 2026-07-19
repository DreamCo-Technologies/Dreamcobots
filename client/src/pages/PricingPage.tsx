import Seo from "@/components/Seo";
import AppShell from "@/components/AppShell";
import { useState } from "react";
import { useQuery, useMutation } from "@tanstack/react-query";
import { apiRequest, queryClient } from "@/lib/queryClient";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { cn } from "@/lib/utils";
import { TIER_PRICING, TIER_AUTONOMY_LIMITS, DIVISION_API_REGISTRIES, getTotalApiCount } from "@shared/api-registry";
import { useToast } from "@/hooks/use-toast";
import {
  Check,
  ChevronDown,
  ChevronUp,
  Crown,
  ExternalLink,
  Layers,
  Loader2,
  Lock,
  Mail,
  Network,
  Rocket,
  Settings,
  Shield,
  Sparkles,
  Star,
  Zap,
} from "lucide-react";

const TIER_STYLES: Record<string, { gradient: string; border: string; badge: string; icon: typeof Shield }> = {
  free: { gradient: "from-muted/30 to-muted/10", border: "border-border/60", badge: "bg-muted text-muted-foreground", icon: Shield },
  pro: { gradient: "from-[rgb(59_130_246)]/10 to-[rgb(59_130_246)]/3", border: "border-[rgb(59_130_246)]/30", badge: "bg-[rgb(59_130_246)]/15 text-[rgb(59_130_246)]", icon: Zap },
  enterprise: { gradient: "from-[rgb(168_85_247)]/10 to-[rgb(168_85_247)]/3", border: "border-[rgb(168_85_247)]/30", badge: "bg-[rgb(168_85_247)]/15 text-[rgb(168_85_247)]", icon: Crown },
  elite: { gradient: "from-[rgb(245_158_11)]/10 to-[rgb(245_158_11)]/3", border: "border-[rgb(245_158_11)]/30", badge: "bg-[rgb(245_158_11)]/15 text-[rgb(245_158_11)]", icon: Star },
};

const AUTONOMY_DESCRIPTIONS: Record<string, string> = {
  guided: "You approve every action before execution",
  "semi-autonomous": "Low-risk auto-execution, high-risk flagged for approval",
  "full-autonomy": "Full auto-execution with reporting only",
};

interface StripeProduct {
  id: string;
  name: string;
  description: string;
  metadata: Record<string, string>;
  prices: Array<{
    id: string;
    unit_amount: number;
    currency: string;
    recurring: { interval: string } | null;
  }>;
}

function getTierFromProduct(product: StripeProduct): string {
  return product.metadata?.tier || "free";
}

function getMonthlyPrice(product: StripeProduct): { id: string; amount: number } | null {
  const monthly = product.prices.find(p => p.recurring?.interval === "month");
  return monthly ? { id: monthly.id, amount: monthly.unit_amount } : null;
}

function getYearlyPrice(product: StripeProduct): { id: string; amount: number } | null {
  const yearly = product.prices.find(p => p.recurring?.interval === "year");
  return yearly ? { id: yearly.id, amount: yearly.unit_amount } : null;
}

export default function PricingPage() {
  const [botSlug, setBotSlug] = useState<string | undefined>(undefined);
  const [annual, setAnnual] = useState(false);
  const [restoreOpen, setRestoreOpen] = useState(false);
  const [restoreEmail, setRestoreEmail] = useState("");
  const [portalError, setPortalError] = useState<{ title: string; detail: string; code?: string } | null>(null);
  const { toast } = useToast();

  const totalApis = getTotalApiCount();

  const urlParams = new URLSearchParams(window.location.search);
  const checkoutSuccess = urlParams.get("success") === "true";
  const checkoutCanceled = urlParams.get("canceled") === "true";

  const { data: subStatus, isLoading: subStatusLoading } = useQuery<{ hasActiveSubscription: boolean }>({
    queryKey: ["/api/stripe/subscription-status"],
    refetchOnWindowFocus: true,
    staleTime: 30_000,
  });

  const hasActiveSubscription = subStatus?.hasActiveSubscription ?? false;

  const { data: productsData } = useQuery<{ products: StripeProduct[] }>({
    queryKey: ["/api/stripe/products"],
  });

  const checkoutMutation = useMutation({
    mutationFn: async (priceId: string) => {
      const res = await apiRequest("POST", "/api/stripe/checkout", { priceId });
      return await res.json();
    },
    onSuccess: (data: { url: string }) => {
      if (data.url) {
        window.location.href = data.url;
      }
    },
    onError: (error: Error) => {
      toast({
        title: "Checkout Error",
        description: error.message,
        variant: "destructive",
      });
    },
  });

  const portalMutation = useMutation({
    mutationFn: async () => {
      setPortalError(null);
      let res: Response;
      try {
        res = await fetch("/api/stripe/portal", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          credentials: "include",
          body: JSON.stringify({}),
        });
      } catch {
        throw new Error("Network error — could not reach the server.");
      }
      const body = await res.json().catch(() => ({}));
      if (!res.ok) {
        const err = new Error(body.error || "Failed to open billing portal") as any;
        err.detail = body.detail ?? "";
        err.code = body.code ?? "";
        throw err;
      }
      return body as { url: string };
    },
    onSuccess: (data: { url: string }) => {
      if (data.url) {
        window.location.href = data.url;
      }
    },
    onError: (error: any) => {
      const code: string = error.code ?? "";
      const detail: string = error.detail ?? "";

      if (code === "portal_not_configured") {
        setPortalError({
          title: "Billing Portal not enabled",
          detail: detail || "Go to stripe.com/dashboard → Settings → Billing → Customer portal and activate it.",
          code,
        });
        return;
      }
      if (code === "stripe_not_configured" || code === "stripe_auth_error") {
        setPortalError({
          title: "Stripe is not configured",
          detail: detail || "Add STRIPE_SECRET_KEY and STRIPE_PUBLISHABLE_KEY as environment secrets.",
          code,
        });
        return;
      }

      toast({
        title: "Portal Error",
        description: detail || error.message || "An unexpected error occurred.",
        variant: "destructive",
      });
    },
  });

  const restoreMutation = useMutation({
    mutationFn: async (email: string) => {
      const res = await apiRequest("POST", "/api/stripe/restore-subscription", { email });
      if (!res.ok) {
        const body = await res.json();
        throw new Error(body.error || "Restore failed");
      }
      return await res.json();
    },
    onSuccess: () => {
      toast({
        title: "Subscription restored",
        description: "Your active subscription has been found and restored.",
      });
      setRestoreOpen(false);
      setRestoreEmail("");
      queryClient.invalidateQueries({ queryKey: ["/api/stripe/subscription-status"] });
    },
    onError: (error: Error) => {
      toast({
        title: "Subscription not found",
        description: error.message,
        variant: "destructive",
      });
    },
  });

  const stripeProducts = productsData?.products || [];

  const getProductForTier = (tier: string) => {
    return stripeProducts.find(p => getTierFromProduct(p) === tier);
  };

  const handleSubscribe = (tier: string) => {
    const product = getProductForTier(tier);
    if (!product) return;

    const price = annual ? getYearlyPrice(product) : getMonthlyPrice(product);
    if (!price || price.amount === 0) return;

    checkoutMutation.mutate(price.id);
  };

  return (
    <AppShell selectedBotSlug={botSlug} onBotChange={setBotSlug}>
      <Seo title="Pricing - DreamCo Empire OS" description="Choose the right plan for your autonomous empire." />

      <div className="buddy-card buddy-noise buddy-appear overflow-hidden">
        <div className="px-5 pt-6 pb-5 md:px-8 md:pt-8 md:pb-6 border-b border-border/60">
          <div className="text-center max-w-2xl mx-auto">
            {checkoutSuccess && (
              <div className="mb-4 p-3 rounded-xl bg-green-500/10 border border-green-500/30 text-green-600 dark:text-green-400 text-sm" data-testid="checkout-success">
                Payment successful! Your Empire tier has been upgraded.
              </div>
            )}
            {checkoutCanceled && (
              <div className="mb-4 p-3 rounded-xl bg-yellow-500/10 border border-yellow-500/30 text-yellow-600 dark:text-yellow-400 text-sm" data-testid="checkout-canceled">
                Checkout was canceled. You can try again anytime.
              </div>
            )}

            {!subStatusLoading && hasActiveSubscription && (
              <div className="mb-4" data-testid="manage-subscription-banner">
                <div className="p-3 rounded-xl bg-primary/5 border border-primary/20 flex items-center justify-between gap-3">
                  <div className="flex items-center gap-2 text-sm">
                    <Check className="h-4 w-4 text-green-500 flex-shrink-0" />
                    <span className="text-foreground font-medium">You have an active subscription</span>
                  </div>
                  <Button
                    size="sm"
                    variant="outline"
                    className="rounded-xl gap-1.5 flex-shrink-0"
                    onClick={() => portalMutation.mutate()}
                    disabled={portalMutation.isPending}
                    data-testid="btn-manage-subscription"
                  >
                    {portalMutation.isPending ? (
                      <Loader2 className="h-3.5 w-3.5 animate-spin" />
                    ) : (
                      <Settings className="h-3.5 w-3.5" />
                    )}
                    Manage Subscription
                    {!portalMutation.isPending && <ExternalLink className="h-3 w-3 opacity-50" />}
                  </Button>
                </div>
                {portalError && (
                  <div className="mt-2 p-3 rounded-xl bg-destructive/10 border border-destructive/30 text-left" data-testid="portal-error-inline">
                    <p className="text-sm font-medium text-destructive">{portalError.title}</p>
                    <p className="text-xs text-muted-foreground mt-0.5">{portalError.detail}</p>
                    {portalError.code === "portal_not_configured" && (
                      <a
                        href="https://dashboard.stripe.com/settings/billing/portal"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-xs text-primary underline mt-1 inline-flex items-center gap-1"
                        data-testid="link-stripe-portal-settings"
                      >
                        Open Stripe Portal Settings <ExternalLink className="h-3 w-3" />
                      </a>
                    )}
                  </div>
                )}
              </div>
            )}

            {!subStatusLoading && !hasActiveSubscription && (
              <div className="mb-4 rounded-xl border border-border/60 overflow-hidden" data-testid="restore-subscription-section">
                <button
                  className="w-full flex items-center justify-between gap-2 px-4 py-3 text-sm text-muted-foreground hover:text-foreground hover:bg-muted/30 transition-colors"
                  onClick={() => setRestoreOpen(v => !v)}
                  data-testid="btn-restore-toggle"
                >
                  <span className="flex items-center gap-2">
                    <Mail className="h-4 w-4 flex-shrink-0" />
                    Already subscribed? Restore your subscription
                  </span>
                  {restoreOpen ? (
                    <ChevronUp className="h-4 w-4 flex-shrink-0" />
                  ) : (
                    <ChevronDown className="h-4 w-4 flex-shrink-0" />
                  )}
                </button>
                {restoreOpen && (
                  <div className="px-4 pb-4 pt-1 bg-muted/20 border-t border-border/40">
                    <p className="text-xs text-muted-foreground mb-3">
                      If you cleared your browser data or switched browsers, enter the email address you used to subscribe and we'll reconnect your plan.
                    </p>
                    <form
                      className="flex gap-2"
                      onSubmit={e => {
                        e.preventDefault();
                        if (restoreEmail.trim()) restoreMutation.mutate(restoreEmail.trim());
                      }}
                    >
                      <Input
                        type="email"
                        placeholder="your@email.com"
                        value={restoreEmail}
                        onChange={e => setRestoreEmail(e.target.value)}
                        className="rounded-xl text-sm h-9"
                        disabled={restoreMutation.isPending}
                        data-testid="input-restore-email"
                      />
                      <Button
                        type="submit"
                        size="sm"
                        className="rounded-xl flex-shrink-0 h-9"
                        disabled={restoreMutation.isPending || !restoreEmail.trim()}
                        data-testid="btn-restore-submit"
                      >
                        {restoreMutation.isPending ? (
                          <Loader2 className="h-3.5 w-3.5 animate-spin" />
                        ) : (
                          "Restore"
                        )}
                      </Button>
                    </form>
                  </div>
                )}
              </div>
            )}

            <h1 className="text-2xl md:text-3xl" data-testid="text-pricing-title">Choose Your Empire Tier</h1>
            <p className="text-sm text-muted-foreground mt-2">
              Scale your autonomous AI workforce from a single bot to a full 251-bot empire
            </p>
            <div className="mt-4 inline-flex items-center gap-2 p-1 rounded-xl bg-muted/50 border border-border/60">
              <button
                className={cn(
                  "px-4 py-1.5 rounded-lg text-sm font-medium transition-all",
                  !annual ? "bg-background shadow-sm" : "text-muted-foreground"
                )}
                onClick={() => setAnnual(false)}
                data-testid="btn-monthly"
              >
                Monthly
              </button>
              <button
                className={cn(
                  "px-4 py-1.5 rounded-lg text-sm font-medium transition-all",
                  annual ? "bg-background shadow-sm" : "text-muted-foreground"
                )}
                onClick={() => setAnnual(true)}
                data-testid="btn-annual"
              >
                Annual
                <Badge variant="secondary" className="ml-1.5 rounded-full text-[10px]">Save 20%</Badge>
              </button>
            </div>
          </div>
        </div>

        <div className="p-5 md:p-8 space-y-8 buddy-stagger">
          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4">
            {(["free", "pro", "enterprise", "elite"] as const).map(tier => {
              const info = TIER_PRICING[tier];
              const style = TIER_STYLES[tier];
              const TierIcon = style.icon;
              const autonomyLevels = TIER_AUTONOMY_LIMITS[tier];
              const isPopular = tier === "enterprise";

              const stripeProduct = getProductForTier(tier);
              const monthlyPrice = stripeProduct ? getMonthlyPrice(stripeProduct) : null;
              const yearlyPrice = stripeProduct ? getYearlyPrice(stripeProduct) : null;

              const displayPrice = annual && yearlyPrice
                ? Math.round(yearlyPrice.amount / 12 / 100)
                : monthlyPrice
                  ? monthlyPrice.amount / 100
                  : info.price;

              const isFree = tier === "free";

              return (
                <Card
                  key={tier}
                  className={cn("relative overflow-visible", style.border, isPopular && "ring-2 ring-[rgb(168_85_247)]/30")}
                  data-testid={`pricing-tier-${tier}`}
                >
                  {isPopular && (
                    <div className="absolute -top-3 left-1/2 -translate-x-1/2">
                      <Badge className="bg-[rgb(168_85_247)] text-white rounded-full px-3">Most Popular</Badge>
                    </div>
                  )}
                  <div className={cn("absolute inset-0 rounded-xl bg-gradient-to-b pointer-events-none opacity-60", style.gradient)} />
                  <CardContent className="relative p-6">
                    <div className="flex items-center gap-2 mb-4">
                      <div className={cn("h-10 w-10 rounded-xl flex items-center justify-center", style.badge)}>
                        <TierIcon className="h-5 w-5" />
                      </div>
                      <div>
                        <p className="text-lg font-bold capitalize">{info.label}</p>
                        <Badge variant="outline" className="rounded-full text-[10px] capitalize">{tier} tier</Badge>
                      </div>
                    </div>

                    <div className="mb-6">
                      {displayPrice === 0 ? (
                        <p className="text-3xl font-bold">Free</p>
                      ) : (
                        <div className="flex items-baseline gap-1">
                          <p className="text-3xl font-bold">${displayPrice.toLocaleString()}</p>
                          <span className="text-sm text-muted-foreground">/mo</span>
                        </div>
                      )}
                      {annual && yearlyPrice && yearlyPrice.amount > 0 && (
                        <p className="text-xs text-green-600 dark:text-green-400 mt-1">
                          ${(yearlyPrice.amount / 100).toLocaleString()}/year
                        </p>
                      )}
                      {stripeProduct && (
                        <Badge variant="secondary" className="rounded-full text-[9px] mt-2">
                          <Sparkles className="h-2.5 w-2.5 mr-1" />
                          Live Stripe
                        </Badge>
                      )}
                    </div>

                    <div className="mb-6">
                      <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2">Autonomy Access</p>
                      <div className="space-y-1.5">
                        {(["guided", "semi-autonomous", "full-autonomy"] as const).map(mode => {
                          const allowed = autonomyLevels.includes(mode);
                          return (
                            <div key={mode} className={cn("flex items-center gap-2 text-sm", !allowed && "opacity-40")}>
                              {allowed ? (
                                <Check className="h-3.5 w-3.5 text-green-500 flex-shrink-0" />
                              ) : (
                                <Lock className="h-3.5 w-3.5 text-muted-foreground flex-shrink-0" />
                              )}
                              <span className="capitalize">{mode.replace("-", " ")}</span>
                            </div>
                          );
                        })}
                      </div>
                    </div>

                    <div className="space-y-2 mb-6">
                      {info.features.map((f, i) => (
                        <div key={i} className="flex items-start gap-2">
                          <Check className="h-3.5 w-3.5 text-green-500 mt-0.5 flex-shrink-0" />
                          <span className="text-sm text-muted-foreground">{f}</span>
                        </div>
                      ))}
                    </div>

                    {hasActiveSubscription && !isFree ? (
                      <Button
                        className="w-full rounded-xl"
                        variant="outline"
                        onClick={() => portalMutation.mutate()}
                        disabled={portalMutation.isPending}
                        data-testid={`btn-manage-${tier}`}
                      >
                        {portalMutation.isPending ? (
                          <Loader2 className="h-4 w-4 animate-spin mr-2" />
                        ) : (
                          <Settings className="h-4 w-4 mr-2" />
                        )}
                        Manage Plan
                      </Button>
                    ) : (
                      <Button
                        className={cn(
                          "w-full rounded-xl",
                          tier === "enterprise" && "bg-[rgb(168_85_247)] text-white border-[rgb(168_85_247)]",
                          tier === "elite" && "bg-[rgb(245_158_11)] text-white border-[rgb(245_158_11)]",
                        )}
                        variant={tier === "free" ? "outline" : "default"}
                        disabled={checkoutMutation.isPending || subStatusLoading}
                        onClick={() => !isFree && handleSubscribe(tier)}
                        data-testid={`btn-select-${tier}`}
                      >
                        {checkoutMutation.isPending ? (
                          <Loader2 className="h-4 w-4 animate-spin mr-2" />
                        ) : null}
                        {isFree ? "Get Started Free" : tier === "elite" ? "Subscribe Elite" : "Subscribe Now"}
                      </Button>
                    )}
                  </CardContent>
                </Card>
              );
            })}
          </div>

          <Card data-testid="autonomy-comparison">
            <CardHeader>
              <CardTitle className="text-lg flex items-center gap-2">
                <Layers className="h-5 w-5 text-primary" />
                Autonomy Tier Comparison
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground mb-4">
                Higher autonomy tiers unlock more automated revenue generation. Premium tiers include full autonomous operation where bots execute, optimize, and scale without manual intervention.
              </p>
              <div className="space-y-3">
                {(["guided", "semi-autonomous", "full-autonomy"] as const).map(mode => (
                  <div key={mode} className="p-4 rounded-xl border border-border/40">
                    <div className="flex flex-wrap items-center justify-between gap-3">
                      <div className="flex items-center gap-3">
                        <div className={cn(
                          "h-10 w-10 rounded-xl flex items-center justify-center",
                          mode === "guided" && "bg-[rgb(59_130_246)]/15 text-[rgb(59_130_246)]",
                          mode === "semi-autonomous" && "bg-[rgb(245_158_11)]/15 text-[rgb(245_158_11)]",
                          mode === "full-autonomy" && "bg-[rgb(34_197_94)]/15 text-[rgb(34_197_94)]",
                        )}>
                          {mode === "guided" && <Shield className="h-5 w-5" />}
                          {mode === "semi-autonomous" && <Zap className="h-5 w-5" />}
                          {mode === "full-autonomy" && <Rocket className="h-5 w-5" />}
                        </div>
                        <div>
                          <p className="text-sm font-semibold capitalize">{mode.replace(/-/g, " ")}</p>
                          <p className="text-xs text-muted-foreground">{AUTONOMY_DESCRIPTIONS[mode]}</p>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        {(["free", "pro", "enterprise", "elite"] as const).map(tier => {
                          const allowed = TIER_AUTONOMY_LIMITS[tier].includes(mode);
                          return (
                            <Badge
                              key={tier}
                              variant={allowed ? "secondary" : "outline"}
                              className={cn("rounded-full capitalize text-[10px]", !allowed && "opacity-40")}
                            >
                              {allowed ? <Check className="h-2.5 w-2.5 mr-1" /> : <Lock className="h-2.5 w-2.5 mr-1" />}
                              {tier}
                            </Badge>
                          );
                        })}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          <Card data-testid="api-coverage">
            <CardHeader className="flex flex-row items-center justify-between gap-2 space-y-0">
              <CardTitle className="text-lg flex items-center gap-2">
                <Network className="h-5 w-5 text-primary" />
                API Integration Coverage
              </CardTitle>
              <Badge variant="secondary" className="rounded-full">{totalApis} APIs</Badge>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground mb-4">
                DreamSalesPro alone connects to 100+ sales APIs. Enterprise and Elite tiers unlock the full integration stack across all divisions.
              </p>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                {Object.entries(DIVISION_API_REGISTRIES)
                  .sort(([,a], [,b]) => {
                    const ac = a.categories.reduce((s, c) => s + c.apis.length, 0);
                    const bc = b.categories.reduce((s, c) => s + c.apis.length, 0);
                    return bc - ac;
                  })
                  .map(([div, registry]) => {
                    const apiCount = registry.categories.reduce((s, c) => s + c.apis.length, 0);
                    return (
                      <div key={div} className="p-3 rounded-xl border border-border/40">
                        <div className="flex items-center justify-between gap-2">
                          <p className="text-sm font-medium truncate">{div}</p>
                          <Badge variant="outline" className="rounded-full text-[10px]">{apiCount} APIs</Badge>
                        </div>
                        <div className="mt-2 flex flex-wrap gap-1">
                          {registry.categories.slice(0, 3).map(c => (
                            <Badge key={c.name} variant="secondary" className="rounded-full text-[9px]">{c.name}</Badge>
                          ))}
                          {registry.categories.length > 3 && (
                            <Badge variant="secondary" className="rounded-full text-[9px]">+{registry.categories.length - 3} more</Badge>
                          )}
                        </div>
                      </div>
                    );
                  })}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </AppShell>
  );
}
