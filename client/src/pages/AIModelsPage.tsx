import { useMemo, useState } from "react";
import Seo from "@/components/Seo";
import AppShell from "@/components/AppShell";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from "@/components/ui/dialog";
import { useToast } from "@/hooks/use-toast";
import { apiRequest } from "@/lib/queryClient";
import {
  AI_MODELS,
  AI_MODEL_CATEGORIES,
  PACKAGE_DEALS,
  type AIModel,
} from "@shared/ai-models";
import {
  Search,
  Check,
  Crown,
  Sparkles,
  Gift,
  Lock,
  ChevronRight,
  Globe,
  Zap,
  Star,
  BookOpen,
  ShoppingCart,
  Package,
} from "lucide-react";

function tierBadge(tier: string) {
  switch (tier) {
    case "free":
      return <Badge className="bg-green-500/10 text-green-600 dark:text-green-400 rounded-lg text-[10px]" data-testid={`badge-tier-${tier}`}>Free</Badge>;
    case "paid":
      return <Badge className="bg-amber-500/10 text-amber-600 dark:text-amber-400 rounded-lg text-[10px]" data-testid={`badge-tier-${tier}`}>Paid</Badge>;
    case "freemium":
      return <Badge className="bg-blue-500/10 text-blue-600 dark:text-blue-400 rounded-lg text-[10px]" data-testid={`badge-tier-${tier}`}>Freemium</Badge>;
    default:
      return null;
  }
}

export default function AIModelsPage() {
  const [search, setSearch] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("All");
  const [tierFilter, setTierFilter] = useState<"all" | "free" | "paid" | "freemium">("all");
  const [selectedModel, setSelectedModel] = useState<AIModel | null>(null);
  const [showPackages, setShowPackages] = useState(false);
  const { toast } = useToast();

  const filtered = useMemo(() => {
    return AI_MODELS.filter((m) => {
      const matchesSearch =
        !search ||
        m.name.toLowerCase().includes(search.toLowerCase()) ||
        m.provider.toLowerCase().includes(search.toLowerCase()) ||
        m.bestFor.toLowerCase().includes(search.toLowerCase());
      const matchesCategory = selectedCategory === "All" || m.category === selectedCategory;
      const matchesTier = tierFilter === "all" || m.tier === tierFilter;
      return matchesSearch && matchesCategory && matchesTier;
    });
  }, [search, selectedCategory, tierFilter]);

  const freeCount = AI_MODELS.filter((m) => m.tier === "free").length;
  const freemiumCount = AI_MODELS.filter((m) => m.tier === "freemium").length;
  const paidCount = AI_MODELS.filter((m) => m.tier === "paid").length;

  async function handleCheckout(packageId: string) {
    toast({ title: "Redirecting to checkout...", description: "Setting up your package deal." });
    try {
      const productsRes = await apiRequest("GET", "/api/stripe/products");
      const products = await productsRes.json();
      if (products.length === 0) {
        toast({ title: "No products available", description: "Please set up Stripe products first.", variant: "destructive" });
        return;
      }
      const matched = products.find((p: any) => p.name?.toLowerCase().includes(packageId));
      const priceId = matched?.priceId ?? products[0]?.priceId;
      if (!priceId) {
        toast({ title: "No price found", description: "Please configure pricing in Stripe.", variant: "destructive" });
        return;
      }
      const checkoutRes = await apiRequest("POST", "/api/stripe/checkout", { priceId });
      const { url } = await checkoutRes.json();
      if (url) window.location.href = url;
    } catch (e: any) {
      toast({ title: "Checkout failed", description: e?.message ?? "Unknown error", variant: "destructive" });
    }
  }

  return (
    <AppShell>
      <Seo
        title="DreamCo Empire OS — AI Models Hub"
        description="100 AI models — free and paid — with instructions, benefits, and package deals."
      />

      <Dialog open={!!selectedModel} onOpenChange={(open) => !open && setSelectedModel(null)}>
        {selectedModel && (
          <DialogContent className="max-w-lg max-h-[80vh] overflow-y-auto" data-testid="model-detail-dialog">
            <DialogHeader>
              <DialogTitle className="flex items-center gap-2" data-testid="model-dialog-title">
                {selectedModel.name}
                {tierBadge(selectedModel.tier)}
              </DialogTitle>
              <DialogDescription data-testid="model-dialog-description">{selectedModel.provider} — {selectedModel.country}</DialogDescription>
            </DialogHeader>

            <div className="space-y-4 mt-2">
              <div>
                <p className="text-sm font-medium mb-1">How This Benefits You</p>
                <p className="text-sm text-muted-foreground" data-testid="model-benefit">{selectedModel.benefit}</p>
              </div>

              <Separator />

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <p className="text-xs font-semibold text-green-600 dark:text-green-400 mb-2 flex items-center gap-1">
                    <Gift className="h-3 w-3" /> Free Features
                  </p>
                  <ul className="space-y-1" data-testid="free-features-list">
                    {selectedModel.freeFeatures.map((f, i) => (
                      <li key={i} className="text-xs text-muted-foreground flex items-start gap-1.5">
                        <Check className="h-3 w-3 text-green-500 mt-0.5 shrink-0" />
                        {f}
                      </li>
                    ))}
                  </ul>
                </div>

                <div>
                  <p className="text-xs font-semibold text-amber-600 dark:text-amber-400 mb-2 flex items-center gap-1">
                    <Crown className="h-3 w-3" /> Paid Features ({selectedModel.paidPrice})
                  </p>
                  <ul className="space-y-1" data-testid="paid-features-list">
                    {selectedModel.paidFeatures.map((f, i) => (
                      <li key={i} className="text-xs text-muted-foreground flex items-start gap-1.5">
                        <Star className="h-3 w-3 text-amber-500 mt-0.5 shrink-0" />
                        {f}
                      </li>
                    ))}
                  </ul>
                </div>
              </div>

              <Separator />

              <div>
                <p className="text-sm font-medium mb-1 flex items-center gap-1">
                  <BookOpen className="h-3.5 w-3.5" /> Instructions After Purchase
                </p>
                <div className="bg-muted/50 rounded-xl p-3" data-testid="model-instructions">
                  {selectedModel.instructions.split("\n").map((line, i) => (
                    <p key={i} className="text-xs text-muted-foreground">{line}</p>
                  ))}
                </div>
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs text-muted-foreground">Package deal</p>
                  <p className="text-sm font-medium" data-testid="model-package-price">{selectedModel.packagePrice}</p>
                </div>
                {selectedModel.tier === "free" ? (
                  <Button className="rounded-xl" data-testid="button-use-free-model">
                    <Zap className="h-4 w-4 mr-1" /> Use Free
                  </Button>
                ) : (
                  <Button className="rounded-xl" onClick={() => { setSelectedModel(null); setShowPackages(true); }} data-testid="button-view-packages">
                    <ShoppingCart className="h-4 w-4 mr-1" /> View Packages
                  </Button>
                )}
              </div>
            </div>
          </DialogContent>
        )}
      </Dialog>

      <Dialog open={showPackages} onOpenChange={setShowPackages}>
        <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto" data-testid="packages-dialog">
          <DialogHeader>
            <DialogTitle data-testid="packages-dialog-title">Package Deals</DialogTitle>
            <DialogDescription data-testid="packages-dialog-description">Get more AI models for less — bundle pricing saves you up to 80%.</DialogDescription>
          </DialogHeader>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">
            {PACKAGE_DEALS.map((pkg) => (
              <Card key={pkg.id} className={`p-4 rounded-2xl border-border/60 ${pkg.id === "empire" ? "ring-2 ring-primary" : ""}`} data-testid={`package-card-${pkg.id}`}>
                {pkg.id === "empire" && (
                  <Badge className="mb-2 bg-primary text-primary-foreground text-[10px]" data-testid="badge-most-popular">Most Popular</Badge>
                )}
                <p className="text-lg font-bold" data-testid={`text-package-name-${pkg.id}`}>{pkg.name}</p>
                <p className="text-2xl font-bold text-primary mt-1" data-testid={`text-package-price-${pkg.id}`}>{pkg.price}</p>
                <p className="text-xs text-muted-foreground mt-1" data-testid={`text-package-models-${pkg.id}`}>{pkg.models} AI models included</p>
                <p className="text-xs text-muted-foreground mt-2">{pkg.description}</p>

                <Separator className="my-3" />

                <ul className="space-y-1.5">
                  {pkg.includes.map((item, i) => (
                    <li key={i} className="text-xs flex items-start gap-1.5">
                      <Check className="h-3 w-3 text-green-500 mt-0.5 shrink-0" />
                      <span className="text-muted-foreground">{item}</span>
                    </li>
                  ))}
                </ul>

                <Button
                  className="w-full mt-4 rounded-xl"
                  variant={pkg.id === "empire" ? "default" : "outline"}
                  onClick={() => handleCheckout(pkg.id)}
                  data-testid={`button-checkout-${pkg.id}`}
                >
                  Get {pkg.name}
                </Button>
              </Card>
            ))}
          </div>
        </DialogContent>
      </Dialog>

      <div className="buddy-appear">
        <div className="flex flex-col md:flex-row md:items-end md:justify-between gap-4">
          <div className="min-w-0">
            <h2 className="text-3xl md:text-4xl" data-testid="page-title">AI Models Hub</h2>
            <p className="mt-2 text-sm text-muted-foreground max-w-2xl">
              100 AI models at your fingertips — free and paid. Every model comes with clear instructions, benefits, and package deals. You're the entrepreneur, AI works for you.
            </p>
          </div>
          <Button className="rounded-xl shrink-0" onClick={() => setShowPackages(true)} data-testid="button-open-packages">
            <Package className="h-4 w-4 mr-2" />
            Package Deals
          </Button>
        </div>

        <div className="mt-6 grid grid-cols-2 md:grid-cols-4 gap-4">
          <Card className="buddy-card rounded-2xl border-border/60 p-4 text-center" data-testid="stat-card-total">
            <div className="h-10 w-10 rounded-xl bg-blue-500/10 mx-auto flex items-center justify-center">
              <Sparkles className="h-5 w-5 text-blue-500" />
            </div>
            <p className="mt-2 text-2xl font-bold" data-testid="stat-total">100</p>
            <p className="text-xs text-muted-foreground">Total Models</p>
          </Card>
          <Card className="buddy-card rounded-2xl border-border/60 p-4 text-center" data-testid="stat-card-free">
            <div className="h-10 w-10 rounded-xl bg-green-500/10 mx-auto flex items-center justify-center">
              <Gift className="h-5 w-5 text-green-500" />
            </div>
            <p className="mt-2 text-2xl font-bold" data-testid="stat-free">{freeCount}</p>
            <p className="text-xs text-muted-foreground">Completely Free</p>
          </Card>
          <Card className="buddy-card rounded-2xl border-border/60 p-4 text-center" data-testid="stat-card-freemium">
            <div className="h-10 w-10 rounded-xl bg-blue-500/10 mx-auto flex items-center justify-center">
              <Zap className="h-5 w-5 text-blue-500" />
            </div>
            <p className="mt-2 text-2xl font-bold" data-testid="stat-freemium">{freemiumCount}</p>
            <p className="text-xs text-muted-foreground">Free + Paid Tiers</p>
          </Card>
          <Card className="buddy-card rounded-2xl border-border/60 p-4 text-center" data-testid="stat-card-paid">
            <div className="h-10 w-10 rounded-xl bg-amber-500/10 mx-auto flex items-center justify-center">
              <Crown className="h-5 w-5 text-amber-500" />
            </div>
            <p className="mt-2 text-2xl font-bold" data-testid="stat-paid">{paidCount}</p>
            <p className="text-xs text-muted-foreground">Premium Only</p>
          </Card>
        </div>

        <Card className="buddy-card rounded-3xl border-border/60 mt-6 p-5" data-testid="tier-comparison-card">
          <div className="flex items-center gap-3 mb-4">
            <div className="h-10 w-10 rounded-2xl bg-green-500/10 flex items-center justify-center shrink-0">
              <Gift className="h-5 w-5 text-green-500" />
            </div>
            <div>
              <h3 className="font-semibold">Free vs Paid — What You Get</h3>
              <p className="text-xs text-muted-foreground">Click any model below to see exactly what's included free and what's premium.</p>
            </div>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            <div className="rounded-xl border border-green-500/20 bg-green-500/5 p-3" data-testid="tier-info-free">
              <p className="text-sm font-medium text-green-600 dark:text-green-400">Free Tier</p>
              <p className="text-xs text-muted-foreground mt-1">Basic access to {freeCount} models. Limited features, great for getting started and learning.</p>
            </div>
            <div className="rounded-xl border border-blue-500/20 bg-blue-500/5 p-3" data-testid="tier-info-freemium">
              <p className="text-sm font-medium text-blue-600 dark:text-blue-400">Freemium Tier</p>
              <p className="text-xs text-muted-foreground mt-1">{freemiumCount} models with free basics + premium upgrades. Try before you buy.</p>
            </div>
            <div className="rounded-xl border border-amber-500/20 bg-amber-500/5 p-3" data-testid="tier-info-paid">
              <p className="text-sm font-medium text-amber-600 dark:text-amber-400">Premium Tier</p>
              <p className="text-xs text-muted-foreground mt-1">{paidCount} exclusive models. Full power, no limits, enterprise features.</p>
            </div>
          </div>
        </Card>

        <div className="mt-6 space-y-4">
          <div className="flex flex-col md:flex-row gap-3">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search models, providers, use cases..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="pl-9 rounded-xl"
                data-testid="input-search-models"
              />
            </div>
            <div className="flex gap-2" data-testid="tier-filters">
              {(["all", "free", "freemium", "paid"] as const).map((t) => (
                <Button
                  key={t}
                  size="sm"
                  variant={tierFilter === t ? "default" : "outline"}
                  className="text-xs rounded-lg"
                  onClick={() => setTierFilter(t)}
                  data-testid={`button-tier-filter-${t}`}
                >
                  {t === "all" ? "All" : t.charAt(0).toUpperCase() + t.slice(1)}
                </Button>
              ))}
            </div>
          </div>

          <div className="flex flex-wrap gap-2" data-testid="category-filters">
            <Button
              size="sm"
              variant={selectedCategory === "All" ? "default" : "outline"}
              className="text-xs rounded-lg"
              onClick={() => setSelectedCategory("All")}
              data-testid="button-filter-all"
            >
              All
            </Button>
            {AI_MODEL_CATEGORIES.map((cat) => (
              <Button
                key={cat}
                size="sm"
                variant={selectedCategory === cat ? "default" : "outline"}
                className="text-xs rounded-lg"
                onClick={() => setSelectedCategory(cat)}
                data-testid={`button-filter-${cat.toLowerCase().replace(/\s+/g, "-")}`}
              >
                {cat}
              </Button>
            ))}
          </div>

          <p className="text-xs text-muted-foreground" data-testid="text-results-count">
            Showing {filtered.length} of {AI_MODELS.length} models
          </p>

          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4" data-testid="models-grid">
            {filtered.map((model) => (
              <Card
                key={model.id}
                className="buddy-card rounded-2xl border-border/60 p-4 cursor-pointer group"
                onClick={() => setSelectedModel(model)}
                data-testid={`card-model-${model.id}`}
              >
                <div className="flex items-start justify-between gap-2">
                  <div className="min-w-0">
                    <div className="flex items-center gap-2">
                      <p className="font-semibold text-sm truncate" data-testid={`text-model-name-${model.id}`}>{model.name}</p>
                      {tierBadge(model.tier)}
                    </div>
                    <p className="text-xs text-muted-foreground mt-0.5" data-testid={`text-model-provider-${model.id}`}>{model.provider} — {model.country}</p>
                  </div>
                  <ChevronRight className="h-4 w-4 text-muted-foreground shrink-0 mt-1" />
                </div>

                <Badge variant="outline" className="text-[10px] rounded-lg mt-2" data-testid={`badge-category-${model.id}`}>{model.category}</Badge>

                <p className="mt-2 text-xs text-muted-foreground leading-relaxed line-clamp-2" data-testid={`text-best-for-${model.id}`}>{model.bestFor}</p>

                <Separator className="my-2" />

                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    {model.tier === "free" ? (
                      <span className="text-xs font-medium text-green-600 dark:text-green-400 flex items-center gap-1" data-testid={`text-price-${model.id}`}>
                        <Gift className="h-3 w-3" /> Free
                      </span>
                    ) : model.tier === "freemium" ? (
                      <span className="text-xs font-medium text-blue-600 dark:text-blue-400 flex items-center gap-1" data-testid={`text-price-${model.id}`}>
                        <Zap className="h-3 w-3" /> Free + {model.paidPrice}
                      </span>
                    ) : (
                      <span className="text-xs font-medium text-amber-600 dark:text-amber-400 flex items-center gap-1" data-testid={`text-price-${model.id}`}>
                        <Lock className="h-3 w-3" /> {model.paidPrice}
                      </span>
                    )}
                  </div>
                  <span className="text-[10px] text-muted-foreground" data-testid={`text-package-price-${model.id}`}>{model.packagePrice}</span>
                </div>
              </Card>
            ))}
          </div>

          {filtered.length === 0 && (
            <div className="text-center py-12" data-testid="empty-state">
              <Globe className="h-10 w-10 text-muted-foreground mx-auto" />
              <p className="mt-3 text-sm font-medium">No models found</p>
              <p className="text-xs text-muted-foreground mt-1">Try adjusting your search or filters.</p>
            </div>
          )}
        </div>
      </div>
    </AppShell>
  );
}
