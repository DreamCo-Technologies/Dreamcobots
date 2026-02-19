import Seo from "@/components/Seo";
import AppShell from "@/components/AppShell";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { cn } from "@/lib/utils";
import {
  SUBSCRIPTION_TIERS,
  SKILL_PACKS,
  INDUSTRY_VERTICALS,
} from "@shared/bundles";
import {
  Check,
  Cpu,
  Layers,
  Package,
  Store,
  Users,
  Zap,
  Building2,
  Globe,
  Bot,
} from "lucide-react";

const CTA_LABELS: Record<string, string> = {
  Free: "Get Started",
  Pro: "Subscribe",
  Elite: "Subscribe",
  Enterprise: "Contact Sales",
};

export default function MarketplacePage() {
  return (
    <AppShell>
      <Seo title="AI Marketplace | DreamCo Empire OS" description="Browse subscription tiers, skill packs, and industry verticals for the DreamCo AI ecosystem." />

      <div className="space-y-6">
        <div>
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-xl bg-primary/10 flex items-center justify-center">
              <Store className="h-5 w-5 text-primary" />
            </div>
            <div>
              <h2 className="text-2xl font-bold">AI Marketplace</h2>
              <p className="text-sm text-muted-foreground">
                Subscription plans, skill packs, and enterprise verticals for your AI fleet
              </p>
            </div>
          </div>
        </div>

        <Tabs defaultValue="tiers" className="space-y-6">
          <TabsList data-testid="marketplace-tabs">
            <TabsTrigger value="tiers" data-testid="tab-tiers">
              Subscription Tiers
            </TabsTrigger>
            <TabsTrigger value="packs" data-testid="tab-packs">
              Skill Packs
            </TabsTrigger>
            <TabsTrigger value="verticals" data-testid="tab-verticals">
              Industry Verticals
            </TabsTrigger>
          </TabsList>

          <TabsContent value="tiers" className="space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
              {SUBSCRIPTION_TIERS.map((tier) => (
                <Card
                  key={tier.name}
                  className={cn(
                    "hover-elevate flex flex-col",
                    tier.highlight && "border-primary border-2 relative"
                  )}
                  data-testid={`card-tier-${tier.name.toLowerCase()}`}
                >
                  {tier.highlight && (
                    <div className="absolute -top-3 left-1/2 -translate-x-1/2">
                      <Badge variant="default" className="rounded-full">
                        Most Popular
                      </Badge>
                    </div>
                  )}
                  <CardHeader className="pb-2">
                    <CardTitle className="text-lg">{tier.name}</CardTitle>
                    <div className="flex items-baseline gap-1 mt-1">
                      <span className="text-3xl font-bold">{tier.price}</span>
                      <span className="text-sm text-muted-foreground">
                        /{tier.period}
                      </span>
                    </div>
                  </CardHeader>
                  <CardContent className="flex-1 flex flex-col gap-4">
                    <div className="space-y-2 flex-1">
                      {tier.features.map((feature) => (
                        <div
                          key={feature}
                          className="flex items-start gap-2 text-sm"
                        >
                          <Check className="h-4 w-4 text-primary mt-0.5 shrink-0" />
                          <span>{feature}</span>
                        </div>
                      ))}
                    </div>

                    <div className="space-y-2 pt-2 border-t border-border/40">
                      <div className="flex items-center gap-2 text-xs text-muted-foreground">
                        <Cpu className="h-3.5 w-3.5 shrink-0" />
                        <span>{tier.modelAccess}</span>
                      </div>
                      <div className="flex items-center gap-2 text-xs text-muted-foreground">
                        <Bot className="h-3.5 w-3.5 shrink-0" />
                        <span>
                          {tier.agentLimit === -1
                            ? "Unlimited agents"
                            : `Up to ${tier.agentLimit} agent${tier.agentLimit !== 1 ? "s" : ""}`}
                        </span>
                      </div>
                    </div>

                    <Button
                      className="w-full"
                      variant={tier.highlight ? "default" : "outline"}
                      data-testid={`btn-tier-${tier.name.toLowerCase()}`}
                    >
                      {CTA_LABELS[tier.name] ?? "Subscribe"}
                    </Button>
                  </CardContent>
                </Card>
              ))}
            </div>
          </TabsContent>

          <TabsContent value="packs" className="space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {SKILL_PACKS.map((pack) => (
                <Card
                  key={pack.name}
                  className="hover-elevate flex flex-col"
                  data-testid={`card-pack-${pack.name.toLowerCase().replace(/\s+/g, "-")}`}
                >
                  <CardHeader className="pb-2">
                    <div className="flex items-center justify-between gap-2 flex-wrap">
                      <CardTitle className="text-base">{pack.name}</CardTitle>
                      <Badge variant="secondary">{pack.price}</Badge>
                    </div>
                  </CardHeader>
                  <CardContent className="flex-1 flex flex-col gap-4">
                    <p className="text-sm text-muted-foreground">
                      {pack.description}
                    </p>

                    <div className="flex items-center gap-2 text-xs text-muted-foreground">
                      <Users className="h-3.5 w-3.5 shrink-0" />
                      <span>{pack.agentCount} agents included</span>
                    </div>

                    <div className="flex flex-wrap gap-1.5">
                      {pack.providers.map((provider) => (
                        <Badge
                          key={provider}
                          variant="outline"
                          className="text-xs"
                        >
                          {provider}
                        </Badge>
                      ))}
                    </div>

                    <div className="space-y-1.5 flex-1">
                      {pack.features.map((feature) => (
                        <div
                          key={feature}
                          className="flex items-start gap-2 text-sm"
                        >
                          <Check className="h-3.5 w-3.5 text-primary mt-0.5 shrink-0" />
                          <span>{feature}</span>
                        </div>
                      ))}
                    </div>

                    <Button
                      variant="outline"
                      className="w-full"
                      data-testid={`btn-pack-${pack.name.toLowerCase().replace(/\s+/g, "-")}`}
                    >
                      Add Pack
                    </Button>
                  </CardContent>
                </Card>
              ))}
            </div>
          </TabsContent>

          <TabsContent value="verticals" className="space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {INDUSTRY_VERTICALS.map((vertical) => (
                <Card
                  key={vertical.name}
                  className="hover-elevate flex flex-col"
                  data-testid={`card-vertical-${vertical.name.toLowerCase().replace(/\s+/g, "-")}`}
                >
                  <CardHeader className="pb-2">
                    <div className="flex items-center justify-between gap-2 flex-wrap">
                      <CardTitle className="text-base">
                        {vertical.name}
                      </CardTitle>
                      <Badge variant="secondary">{vertical.price}</Badge>
                    </div>
                  </CardHeader>
                  <CardContent className="flex-1 flex flex-col gap-4">
                    <p className="text-sm text-muted-foreground">
                      {vertical.description}
                    </p>

                    <div className="flex items-center gap-2 text-xs text-muted-foreground">
                      <Building2 className="h-3.5 w-3.5 shrink-0" />
                      <span>{vertical.targetClients}</span>
                    </div>

                    <div className="flex flex-wrap gap-1.5">
                      {vertical.providers.map((provider) => (
                        <Badge
                          key={provider}
                          variant="outline"
                          className="text-xs"
                        >
                          {provider}
                        </Badge>
                      ))}
                    </div>

                    <div className="space-y-1.5 flex-1">
                      {vertical.features.map((feature) => (
                        <div
                          key={feature}
                          className="flex items-start gap-2 text-sm"
                        >
                          <Check className="h-3.5 w-3.5 text-primary mt-0.5 shrink-0" />
                          <span>{feature}</span>
                        </div>
                      ))}
                    </div>

                    <Button
                      variant="outline"
                      className="w-full"
                      data-testid={`btn-vertical-${vertical.name.toLowerCase().replace(/\s+/g, "-")}`}
                    >
                      Learn More
                    </Button>
                  </CardContent>
                </Card>
              ))}
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </AppShell>
  );
}
