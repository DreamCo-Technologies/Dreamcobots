import { useState, useMemo } from "react";
import Seo from "@/components/Seo";
import AppShell from "@/components/AppShell";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { cn } from "@/lib/utils";
import { useToast } from "@/hooks/use-toast";
import { AI_CATEGORIES, AI_PROVIDERS } from "@shared/ai-ecosystem";
import {
  Globe,
  Search,
  Layers,
  Cpu,
  Building2,
  Sparkles,
  ExternalLink,
  BookOpen,
  Download,
  Copy,
  Link2,
} from "lucide-react";

const PRICING_OPTIONS = ["All", "free", "freemium", "paid", "enterprise", "open-source"] as const;

const PRICING_LABELS: Record<string, string> = {
  All: "All",
  free: "Free",
  freemium: "Freemium",
  paid: "Paid",
  enterprise: "Enterprise",
  "open-source": "Open-Source",
};

const PRICING_BADGE_CLASS: Record<string, string> = {
  free: "border-green-500/40 bg-green-500/10 text-green-600 dark:text-green-400",
  freemium: "border-blue-500/40 bg-blue-500/10 text-blue-600 dark:text-blue-400",
  paid: "border-amber-500/40 bg-amber-500/10 text-amber-600 dark:text-amber-400",
  enterprise: "border-purple-500/40 bg-purple-500/10 text-purple-600 dark:text-purple-400",
  "open-source": "border-emerald-500/40 bg-emerald-500/10 text-emerald-600 dark:text-emerald-400",
};

export default function EcosystemPage() {
  const { toast } = useToast();
  const [search, setSearch] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("All");
  const [selectedPricing, setSelectedPricing] = useState("All");
  const [watchlist, setWatchlist] = useState<Set<number>>(new Set());

  function toggleWatch(id: number, name: string) {
    setWatchlist(prev => {
      const next = new Set(prev);
      if (next.has(id)) { next.delete(id); toast({ title: `Removed ${name} from watchlist` }); }
      else { next.add(id); toast({ title: `Added ${name} to watchlist` }); }
      return next;
    });
  }

  function exportWatchlist() {
    const items = AI_PROVIDERS.filter(p => watchlist.has(p.id));
    if (!items.length) { toast({ title: "Watchlist is empty", variant: "destructive" }); return; }
    const text = items.map(p => `${p.name} (${p.category}) — ${p.bestAt}`).join("\n");
    navigator.clipboard.writeText(text);
    toast({ title: `Copied ${items.length} providers to clipboard` });
  }

  const filtered = useMemo(() => {
    const q = search.toLowerCase().trim();
    return AI_PROVIDERS.filter((p) => {
      if (selectedCategory !== "All" && p.category !== selectedCategory) return false;
      if (selectedPricing !== "All" && p.freeVsPaid !== selectedPricing) return false;
      if (q) {
        return (
          p.name.toLowerCase().includes(q) ||
          p.category.toLowerCase().includes(q) ||
          p.coreSkill.toLowerCase().includes(q) ||
          p.bestAt.toLowerCase().includes(q) ||
          p.agentSpecialization.toLowerCase().includes(q)
        );
      }
      return true;
    });
  }, [search, selectedCategory, selectedPricing]);

  const freeFreemiumCount = AI_PROVIDERS.filter(
    (p) => p.freeVsPaid === "free" || p.freeVsPaid === "freemium"
  ).length;
  const enterpriseCount = AI_PROVIDERS.filter(
    (p) => p.freeVsPaid === "enterprise"
  ).length;

  return (
    <AppShell>
      <Seo title="AI Ecosystem - DreamCo Empire OS" description="Browse 200+ AI providers across 20 categories" />

      <div className="space-y-6">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-xl bg-primary/10 flex items-center justify-center">
              <Globe className="h-5 w-5 text-primary" />
            </div>
            <div>
              <h2 className="text-xl font-bold" data-testid="text-ecosystem-title">AI Ecosystem</h2>
              <p className="text-sm text-muted-foreground" data-testid="text-provider-count">
                {AI_PROVIDERS.length} providers across {AI_CATEGORIES.length} categories
              </p>
            </div>
          </div>
          <div className="flex gap-2">
            <Button variant="outline" size="sm" onClick={exportWatchlist} data-testid="button-export-watchlist">
              <Copy className="h-4 w-4 mr-2" />
              Copy Watchlist ({watchlist.size})
            </Button>
            <Button variant="outline" size="sm" onClick={() => { setSearch(""); setSelectedCategory("All"); setSelectedPricing("All"); toast({ title: "Filters cleared" }); }} data-testid="button-clear-filters">
              Clear Filters
            </Button>
          </div>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          <Card data-testid="stat-total-providers">
            <CardContent className="p-4">
              <div className="flex items-center gap-2">
                <div className="h-8 w-8 rounded-lg bg-primary/10 flex items-center justify-center">
                  <Layers className="h-4 w-4 text-primary" />
                </div>
                <div>
                  <p className="text-xs text-muted-foreground">Total Providers</p>
                  <p className="text-lg font-bold">{AI_PROVIDERS.length}</p>
                </div>
              </div>
            </CardContent>
          </Card>
          <Card data-testid="stat-categories">
            <CardContent className="p-4">
              <div className="flex items-center gap-2">
                <div className="h-8 w-8 rounded-lg bg-primary/10 flex items-center justify-center">
                  <Cpu className="h-4 w-4 text-primary" />
                </div>
                <div>
                  <p className="text-xs text-muted-foreground">Categories</p>
                  <p className="text-lg font-bold">{AI_CATEGORIES.length}</p>
                </div>
              </div>
            </CardContent>
          </Card>
          <Card data-testid="stat-free-freemium">
            <CardContent className="p-4">
              <div className="flex items-center gap-2">
                <div className="h-8 w-8 rounded-lg bg-green-500/10 flex items-center justify-center">
                  <Sparkles className="h-4 w-4 text-green-500" />
                </div>
                <div>
                  <p className="text-xs text-muted-foreground">Free / Freemium</p>
                  <p className="text-lg font-bold">{freeFreemiumCount}</p>
                </div>
              </div>
            </CardContent>
          </Card>
          <Card data-testid="stat-enterprise">
            <CardContent className="p-4">
              <div className="flex items-center gap-2">
                <div className="h-8 w-8 rounded-lg bg-purple-500/10 flex items-center justify-center">
                  <Building2 className="h-4 w-4 text-purple-500" />
                </div>
                <div>
                  <p className="text-xs text-muted-foreground">Enterprise</p>
                  <p className="text-lg font-bold">{enterpriseCount}</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search providers by name, category, skill..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-9"
            data-testid="input-search-providers"
          />
        </div>

        <div>
          <p className="text-xs font-medium text-muted-foreground mb-2">Pricing</p>
          <div className="flex flex-wrap gap-2">
            {PRICING_OPTIONS.map((opt) => (
              <Button
                key={opt}
                variant={selectedPricing === opt ? "default" : "outline"}
                size="sm"
                onClick={() => setSelectedPricing(opt)}
                className="rounded-md toggle-elevate"
                data-testid={`filter-pricing-${opt.toLowerCase()}`}
              >
                {PRICING_LABELS[opt]}
              </Button>
            ))}
          </div>
        </div>

        <div>
          <p className="text-xs font-medium text-muted-foreground mb-2">Category</p>
          <div className="flex flex-wrap gap-2">
            <Button
              variant={selectedCategory === "All" ? "default" : "outline"}
              size="sm"
              onClick={() => setSelectedCategory("All")}
              className="rounded-md toggle-elevate"
              data-testid="filter-category-all"
            >
              All
            </Button>
            {AI_CATEGORIES.map((cat) => (
              <Button
                key={cat}
                variant={selectedCategory === cat ? "default" : "outline"}
                size="sm"
                onClick={() => setSelectedCategory(cat)}
                className="rounded-md toggle-elevate"
                data-testid={`filter-category-${cat.toLowerCase().replace(/[^a-z0-9]/g, "-")}`}
              >
                {cat}
              </Button>
            ))}
          </div>
        </div>

        <p className="text-sm text-muted-foreground" data-testid="text-filtered-count">
          Showing {filtered.length} of {AI_PROVIDERS.length} providers
        </p>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filtered.map((provider) => (
            <Card
              key={provider.id}
              className="hover-elevate rounded-md"
              data-testid={`card-provider-${provider.id}`}
            >
              <CardHeader className="pb-2">
                <div className="flex items-start justify-between gap-2">
                  <CardTitle className="text-base">{provider.name}</CardTitle>
                  <Badge
                    variant="outline"
                    className={cn(
                      "rounded-md text-xs shrink-0 no-default-hover-elevate no-default-active-elevate",
                      PRICING_BADGE_CLASS[provider.freeVsPaid]
                    )}
                    data-testid={`badge-pricing-${provider.id}`}
                  >
                    {PRICING_LABELS[provider.freeVsPaid]}
                  </Badge>
                </div>
                <Badge variant="secondary" className="w-fit rounded-md text-xs no-default-hover-elevate no-default-active-elevate">
                  {provider.category}
                </Badge>
              </CardHeader>
              <CardContent className="space-y-3 pt-0">
                <div>
                  <p className="text-xs font-medium text-muted-foreground">Core Skill</p>
                  <p className="text-sm">{provider.coreSkill}</p>
                </div>
                <div>
                  <p className="text-xs font-medium text-muted-foreground">Best At</p>
                  <p className="text-sm">{provider.bestAt}</p>
                </div>
                <div>
                  <p className="text-xs font-medium text-muted-foreground">Agent Specialization</p>
                  <p className="text-sm">{provider.agentSpecialization}</p>
                </div>
                <div>
                  <p className="text-xs font-medium text-muted-foreground mb-1">Bundle Fit</p>
                  <div className="flex flex-wrap gap-1">
                    {provider.bundleFit.map((tag) => (
                      <Badge
                        key={tag}
                        variant="outline"
                        className="rounded-md text-xs no-default-hover-elevate no-default-active-elevate"
                      >
                        {tag}
                      </Badge>
                    ))}
                  </div>
                </div>
                <div className="flex gap-2 pt-1">
                  <Button
                    size="sm"
                    variant="outline"
                    className="flex-1 h-8 text-xs rounded-lg"
                    onClick={() => window.open(`https://www.google.com/search?q=${encodeURIComponent(provider.name + " API documentation")}`, "_blank")}
                    data-testid={`button-docs-${provider.id}`}
                  >
                    <BookOpen className="h-3 w-3 mr-1.5" />
                    Docs
                  </Button>
                  <Button
                    size="sm"
                    variant={watchlist.has(provider.id) ? "default" : "outline"}
                    className="flex-1 h-8 text-xs rounded-lg"
                    onClick={() => toggleWatch(provider.id, provider.name)}
                    data-testid={`button-watch-${provider.id}`}
                  >
                    <Link2 className="h-3 w-3 mr-1.5" />
                    {watchlist.has(provider.id) ? "Watching" : "Watch"}
                  </Button>
                  <Button
                    size="sm"
                    variant="ghost"
                    className="h-8 w-8 p-0 rounded-lg"
                    onClick={() => {
                      navigator.clipboard.writeText(`${provider.name}: ${provider.bestAt} — ${provider.agentSpecialization}`);
                      toast({ title: `Copied ${provider.name} info` });
                    }}
                    data-testid={`button-copy-${provider.id}`}
                  >
                    <Copy className="h-3 w-3" />
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {filtered.length === 0 && (
          <div className="py-12 text-center text-muted-foreground" data-testid="text-no-results">
            <p className="text-sm">No providers match your filters.</p>
          </div>
        )}
      </div>
    </AppShell>
  );
}
