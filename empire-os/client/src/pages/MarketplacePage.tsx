import { useState } from "react";
import Seo from "@/components/Seo";
import AppShell from "@/components/AppShell";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Skeleton } from "@/components/ui/skeleton";
import { cn } from "@/lib/utils";
import { useQuery, useMutation } from "@tanstack/react-query";
import { queryClient, apiRequest } from "@/lib/queryClient";
import { useToast } from "@/hooks/use-toast";
import {
  SUBSCRIPTION_TIERS,
  SKILL_PACKS,
  INDUSTRY_VERTICALS,
} from "@shared/bundles";
import {
  Check,
  Cpu,
  Download,
  Layers,
  Package,
  Plus,
  Puzzle,
  Search,
  Star,
  Store,
  Trash2,
  Users,
  Zap,
  Building2,
  Globe,
  Bot,
} from "lucide-react";
import type { Plugin } from "@shared/schema";

const CTA_LABELS: Record<string, string> = {
  Free: "Get Started",
  Pro: "Subscribe",
  Elite: "Subscribe",
  Enterprise: "Contact Sales",
};

const PLUGIN_CATEGORIES = ["all", "alerts", "savings", "finance", "integration", "tools", "ai", "marketing"];

function PluginsSection() {
  const { toast } = useToast();
  const [search, setSearch] = useState("");
  const [category, setCategory] = useState("all");
  const [createOpen, setCreateOpen] = useState(false);
  const [newPlugin, setNewPlugin] = useState({ name: "", slug: "", description: "", category: "tools" });

  const pluginsQuery = useQuery<Plugin[]>({
    queryKey: ["/api/plugins", search, category],
    queryFn: async () => {
      const params = new URLSearchParams();
      if (search) params.set("search", search);
      if (category !== "all") params.set("category", category);
      const res = await fetch(`/api/plugins?${params}`);
      return res.json();
    },
  });

  const installPlugin = useMutation({
    mutationFn: async (id: number) => {
      const res = await apiRequest("POST", `/api/plugins/${id}/install`);
      return res.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["/api/plugins"] });
      toast({ title: "Plugin installed" });
    },
  });

  const uninstallPlugin = useMutation({
    mutationFn: async (id: number) => {
      const res = await apiRequest("POST", `/api/plugins/${id}/uninstall`);
      return res.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["/api/plugins"] });
      toast({ title: "Plugin uninstalled" });
    },
  });

  const downloadPlugin = useMutation({
    mutationFn: async (id: number) => {
      const res = await apiRequest("POST", `/api/plugins/${id}/download`);
      return res.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["/api/plugins"] });
      toast({ title: "Plugin downloaded" });
    },
  });

  const createPlugin = useMutation({
    mutationFn: async (data: any) => {
      const res = await apiRequest("POST", "/api/plugins", data);
      return res.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["/api/plugins"] });
      setCreateOpen(false);
      setNewPlugin({ name: "", slug: "", description: "", category: "tools" });
      toast({ title: "Plugin created" });
    },
  });

  const plugins = pluginsQuery.data ?? [];

  return (
    <div className="space-y-4">
      <div className="flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search plugins..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-9"
            data-testid="input-plugin-search"
          />
        </div>
        <Select value={category} onValueChange={setCategory}>
          <SelectTrigger className="w-[160px]" data-testid="select-plugin-category">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            {PLUGIN_CATEGORIES.map(c => (
              <SelectItem key={c} value={c}>{c === "all" ? "All Categories" : c.charAt(0).toUpperCase() + c.slice(1)}</SelectItem>
            ))}
          </SelectContent>
        </Select>
        <Button onClick={() => setCreateOpen(true)} data-testid="button-create-plugin">
          <Plus className="h-4 w-4 mr-1" /> Create Plugin
        </Button>
      </div>

      {pluginsQuery.isLoading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {[1, 2, 3].map(i => <Skeleton key={i} className="h-48" />)}
        </div>
      ) : plugins.length === 0 ? (
        <Card>
          <CardContent className="p-8 text-center">
            <Puzzle className="h-12 w-12 mx-auto text-muted-foreground mb-3" />
            <p className="text-muted-foreground">No plugins found. Create one or adjust your search.</p>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {plugins.map((plugin) => (
            <Card key={plugin.id} className="hover-elevate flex flex-col" data-testid={`card-plugin-${plugin.id}`}>
              <CardHeader className="pb-2">
                <div className="flex items-center justify-between gap-2">
                  <CardTitle className="text-base">{plugin.name}</CardTitle>
                  <Badge variant="secondary" className="text-xs">{plugin.category}</Badge>
                </div>
                <p className="text-xs text-muted-foreground">v{plugin.version} by {plugin.author}</p>
              </CardHeader>
              <CardContent className="flex-1 flex flex-col gap-3">
                <p className="text-sm text-muted-foreground flex-1">{plugin.description}</p>
                <div className="flex items-center gap-3 text-xs text-muted-foreground">
                  <span className="flex items-center gap-1"><Download className="h-3 w-3" /> {plugin.downloads}</span>
                  <span className="flex items-center gap-1"><Star className="h-3 w-3" /> {plugin.rating}/5</span>
                </div>
                <div className="flex flex-wrap gap-1">
                  {(plugin.capabilities as string[])?.slice(0, 3).map(c => (
                    <Badge key={c} variant="outline" className="text-xs">{c}</Badge>
                  ))}
                </div>
                <div className="flex gap-2">
                  {plugin.installed ? (
                    <Button
                      size="sm"
                      variant="outline"
                      className="flex-1"
                      onClick={() => uninstallPlugin.mutate(plugin.id)}
                      data-testid={`button-uninstall-plugin-${plugin.id}`}
                    >
                      Uninstall
                    </Button>
                  ) : (
                    <Button
                      size="sm"
                      className="flex-1"
                      onClick={() => installPlugin.mutate(plugin.id)}
                      data-testid={`button-install-plugin-${plugin.id}`}
                    >
                      Install
                    </Button>
                  )}
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={() => downloadPlugin.mutate(plugin.id)}
                    data-testid={`button-download-plugin-${plugin.id}`}
                  >
                    <Download className="h-4 w-4" />
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      <Dialog open={createOpen} onOpenChange={setCreateOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Create Plugin</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div className="space-y-2">
              <Label>Name</Label>
              <Input
                value={newPlugin.name}
                onChange={(e) => setNewPlugin({ ...newPlugin, name: e.target.value, slug: e.target.value.toLowerCase().replace(/\s+/g, "-") })}
                placeholder="My Plugin"
                data-testid="input-plugin-name"
              />
            </div>
            <div className="space-y-2">
              <Label>Description</Label>
              <Textarea
                value={newPlugin.description}
                onChange={(e) => setNewPlugin({ ...newPlugin, description: e.target.value })}
                placeholder="What does this plugin do?"
                data-testid="input-plugin-description"
              />
            </div>
            <div className="space-y-2">
              <Label>Category</Label>
              <Select value={newPlugin.category} onValueChange={(v) => setNewPlugin({ ...newPlugin, category: v })}>
                <SelectTrigger data-testid="select-new-plugin-category">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {PLUGIN_CATEGORIES.filter(c => c !== "all").map(c => (
                    <SelectItem key={c} value={c}>{c.charAt(0).toUpperCase() + c.slice(1)}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="flex gap-2 justify-end">
              <Button variant="outline" onClick={() => setCreateOpen(false)}>Cancel</Button>
              <Button
                onClick={() => createPlugin.mutate(newPlugin)}
                disabled={!newPlugin.name || !newPlugin.description || createPlugin.isPending}
                data-testid="button-confirm-create-plugin"
              >
                Create
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}

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

        <Tabs defaultValue="plugins" className="space-y-6">
          <TabsList data-testid="marketplace-tabs">
            <TabsTrigger value="plugins" data-testid="tab-plugins">
              Plugins
            </TabsTrigger>
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

          <TabsContent value="plugins" className="space-y-4">
            <PluginsSection />
          </TabsContent>

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
