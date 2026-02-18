import Seo from "@/components/Seo";
import AppShell from "@/components/AppShell";
import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { TIER_PRICING, TIER_AUTONOMY_LIMITS, DIVISION_API_REGISTRIES, getTotalApiCount } from "@shared/api-registry";
import {
  Check,
  Crown,
  Layers,
  Lock,
  Network,
  Rocket,
  Shield,
  Sparkles,
  Star,
  Users,
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

export default function PricingPage() {
  const [botSlug, setBotSlug] = useState<string | undefined>(undefined);
  const [annual, setAnnual] = useState(false);

  const totalApis = getTotalApiCount();

  return (
    <AppShell selectedBotSlug={botSlug} onBotChange={setBotSlug}>
      <Seo title="Pricing - DreamCo Empire OS" description="Choose the right plan for your autonomous empire." />

      <div className="buddy-card buddy-noise buddy-appear overflow-hidden">
        <div className="px-5 pt-6 pb-5 md:px-8 md:pt-8 md:pb-6 border-b border-border/60">
          <div className="text-center max-w-2xl mx-auto">
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
              const price = annual ? Math.round(info.price * 0.8) : info.price;
              const autonomyLevels = TIER_AUTONOMY_LIMITS[tier];
              const isPopular = tier === "enterprise";

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
                      {price === 0 ? (
                        <p className="text-3xl font-bold">Free</p>
                      ) : (
                        <div className="flex items-baseline gap-1">
                          <p className="text-3xl font-bold">${price.toLocaleString()}</p>
                          <span className="text-sm text-muted-foreground">/mo</span>
                        </div>
                      )}
                      {annual && price > 0 && (
                        <p className="text-xs text-green-600 dark:text-green-400 mt-1">
                          ${(price * 12).toLocaleString()}/year (save ${(info.price * 12 * 0.2).toLocaleString()})
                        </p>
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

                    <Button
                      className={cn(
                        "w-full rounded-xl",
                        tier === "free" && "variant-outline",
                        tier === "enterprise" && "bg-[rgb(168_85_247)] text-white border-[rgb(168_85_247)]",
                        tier === "elite" && "bg-[rgb(245_158_11)] text-white border-[rgb(245_158_11)]",
                      )}
                      variant={tier === "free" ? "outline" : "default"}
                      data-testid={`btn-select-${tier}`}
                    >
                      {tier === "free" ? "Get Started" : tier === "elite" ? "Contact Sales" : "Upgrade Now"}
                    </Button>
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
