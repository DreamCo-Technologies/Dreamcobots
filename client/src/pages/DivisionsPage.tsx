import Seo from "@/components/Seo";
import AppShell from "@/components/AppShell";
import { useState, useMemo } from "react";
import { useEmpireOverview, useBotsByDivision } from "@/hooks/use-empire";
import { useBots } from "@/hooks/use-bots";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Skeleton } from "@/components/ui/skeleton";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Link, useSearch } from "wouter";
import { useToast } from "@/hooks/use-toast";
import {
  Bot,
  Building2,
  ChevronRight,
  CircleDollarSign,
  Filter,
  Search,
  MessageSquare,
  Copy,
  Sparkles,
  Users,
  Zap,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { DIVISIONS, BOT_TIERS } from "@shared/schema";

const TIER_COLORS: Record<string, string> = {
  free: "bg-muted text-muted-foreground",
  pro: "bg-[rgb(59_130_246)]/15 text-[rgb(59_130_246)] border border-[rgb(59_130_246)]/20",
  enterprise: "bg-[rgb(168_85_247)]/15 text-[rgb(168_85_247)] border border-[rgb(168_85_247)]/20",
  elite: "bg-[rgb(245_158_11)]/15 text-[rgb(245_158_11)] border border-[rgb(245_158_11)]/20",
};

const STATUS_COLORS: Record<string, string> = {
  active: "bg-[rgb(34_197_94)]",
  paused: "bg-[rgb(245_158_11)]",
  inactive: "bg-[rgb(239_68_68)]",
};

export default function DivisionsPage() {
  const { toast } = useToast();
  const [botSlug, setBotSlug] = useState<string | undefined>(undefined);
  const empire = useEmpireOverview();
  const allBots = useBots();

  const searchString = useSearch();
  const urlParams = new URLSearchParams(searchString);
  const initialDivision = urlParams.get("d") || "";
  const [selectedDivision, setSelectedDivision] = useState<string>(initialDivision);
  const [searchQuery, setSearchQuery] = useState("");
  const [tierFilter, setTierFilter] = useState<string>("all");
  const [categoryFilter, setCategoryFilter] = useState<string>("all");

  const divisionBots = useBotsByDivision(selectedDivision || null);

  const botsToShow = useMemo(() => {
    let list = selectedDivision ? (divisionBots.data ?? []) : (allBots.data ?? []);

    if (searchQuery) {
      const q = searchQuery.toLowerCase();
      list = list.filter((b: any) =>
        b.displayName.toLowerCase().includes(q) ||
        b.slug.toLowerCase().includes(q) ||
        b.description?.toLowerCase().includes(q) ||
        b.division?.toLowerCase().includes(q)
      );
    }
    if (tierFilter !== "all") {
      list = list.filter((b: any) => b.tier === tierFilter);
    }
    if (categoryFilter !== "all") {
      list = list.filter((b: any) => b.category === categoryFilter);
    }
    return list as any[];
  }, [selectedDivision, divisionBots.data, allBots.data, searchQuery, tierFilter, categoryFilter]);

  const categories = useMemo(() => {
    const bots = selectedDivision ? (divisionBots.data ?? []) : (allBots.data ?? []);
    const cats = new Set((bots as any[]).map(b => b.category));
    return Array.from(cats).sort();
  }, [selectedDivision, divisionBots.data, allBots.data]);

  const isLoading = selectedDivision ? divisionBots.isLoading : allBots.isLoading;

  // Get top 3 categories for a given division from allBots
  const getTopCategoriesForDivision = (division: string) => {
    const divBots = (allBots.data ?? []).filter((b: any) => b.division === division);
    const categoryCounts = new Map<string, number>();
    
    divBots.forEach((b: any) => {
      const cat = b.category || "Uncategorized";
      categoryCounts.set(cat, (categoryCounts.get(cat) || 0) + 1);
    });
    
    return Array.from(categoryCounts.entries())
      .sort((a, b) => b[1] - a[1])
      .slice(0, 3)
      .map(([cat]) => cat);
  };

  // Group bots by category when division is selected
  const groupedBots = useMemo(() => {
    if (!selectedDivision || botsToShow.length === 0) {
      return [];
    }
    
    const groups = new Map<string, any[]>();
    botsToShow.forEach((bot: any) => {
      const cat = bot.category || "Uncategorized";
      if (!groups.has(cat)) {
        groups.set(cat, []);
      }
      groups.get(cat)!.push(bot);
    });
    
    return Array.from(groups.entries())
      .sort((a, b) => a[0].localeCompare(b[0]))
      .map(([category, bots]) => ({ category, bots }));
  }, [selectedDivision, botsToShow]);

  return (
    <AppShell selectedBotSlug={botSlug} onBotChange={setBotSlug}>
      <Seo title="DreamCo Empire OS - Divisions" description="Browse and manage bots across all 16 divisions." />

      <div className="buddy-card buddy-noise buddy-appear overflow-hidden">
        <div className="px-5 pt-6 pb-5 md:px-8 md:pt-8 md:pb-6 border-b border-border/60">
          <div className="flex flex-wrap items-center justify-between gap-4">
            <div>
              <h1 className="text-2xl md:text-3xl" data-testid="text-divisions-title">Division Explorer</h1>
              <p className="text-sm text-muted-foreground mt-1">Browse {allBots.data?.length ?? 0} bots across {DIVISIONS.length} divisions</p>
            </div>
            <Badge variant="secondary" className="rounded-full">
              <Filter className="h-3 w-3 mr-1.5" />
              {botsToShow.length} results
            </Badge>
          </div>
        </div>

        <div className="p-5 md:p-8 space-y-6">
          {/* Filters */}
          <div className="flex flex-wrap gap-3">
            <Select value={selectedDivision || "all"} onValueChange={(v) => setSelectedDivision(v === "all" ? "" : v)}>
              <SelectTrigger className="w-[200px] rounded-xl" data-testid="filter-division">
                <Building2 className="h-3.5 w-3.5 mr-2 text-muted-foreground" />
                <SelectValue placeholder="All Divisions" />
              </SelectTrigger>
              <SelectContent className="rounded-xl">
                <SelectItem value="all">All Divisions</SelectItem>
                {DIVISIONS.map(d => (
                  <SelectItem key={d} value={d}>{d}</SelectItem>
                ))}
              </SelectContent>
            </Select>

            <Select value={tierFilter} onValueChange={setTierFilter}>
              <SelectTrigger className="w-[150px] rounded-xl" data-testid="filter-tier">
                <Sparkles className="h-3.5 w-3.5 mr-2 text-muted-foreground" />
                <SelectValue placeholder="All Tiers" />
              </SelectTrigger>
              <SelectContent className="rounded-xl">
                <SelectItem value="all">All Tiers</SelectItem>
                {BOT_TIERS.map(t => (
                  <SelectItem key={t} value={t} className="capitalize">{t}</SelectItem>
                ))}
              </SelectContent>
            </Select>

            <Select value={categoryFilter} onValueChange={setCategoryFilter}>
              <SelectTrigger className="w-[170px] rounded-xl" data-testid="filter-category">
                <SelectValue placeholder="All Categories" />
              </SelectTrigger>
              <SelectContent className="rounded-xl">
                <SelectItem value="all">All Categories</SelectItem>
                {categories.map(c => (
                  <SelectItem key={c} value={c} className="capitalize">{c}</SelectItem>
                ))}
              </SelectContent>
            </Select>

            <div className="relative flex-1 min-w-[200px]">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search bots..."
                className="pl-9 rounded-xl"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                data-testid="input-search-bots"
              />
            </div>
          </div>

          {/* Division Quick Select */}
          {!selectedDivision && (
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
              {(empire.data?.divisions ?? [])
                .filter(d => d.botCount > 0)
                .sort((a, b) => b.botCount - a.botCount)
                .map(div => {
                  const topCategories = getTopCategoriesForDivision(div.division);
                  return (
                    <button
                      key={div.division}
                      className="rounded-xl border border-border/60 p-3 text-left hover-elevate transition-all"
                      onClick={() => setSelectedDivision(div.division)}
                      data-testid={`quick-div-${div.division}`}
                    >
                      <p className="text-xs font-semibold truncate">{div.division}</p>
                      <p className="text-[10px] text-muted-foreground">{div.botCount} bots</p>
                      {topCategories.length > 0 && (
                        <div className="mt-2 space-y-0.5">
                          {topCategories.map((cat, idx) => (
                            <p key={idx} className="text-[9px] text-muted-foreground/70 capitalize line-clamp-1" data-testid={`div-category-${div.division}-${idx}`}>
                              {cat}
                            </p>
                          ))}
                        </div>
                      )}
                    </button>
                  );
                })}
            </div>
          )}

          {/* Bot Grid */}
          {isLoading ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {Array.from({ length: 6 }).map((_, i) => <Skeleton key={i} className="h-36 rounded-2xl" />)}
            </div>
          ) : botsToShow.length === 0 ? (
            <div className="text-center py-12">
              <Bot className="h-12 w-12 mx-auto text-muted-foreground/40" />
              <p className="mt-4 text-muted-foreground">No bots match your filters</p>
              <Button variant="outline" className="mt-3 rounded-xl" onClick={() => { setSearchQuery(""); setTierFilter("all"); setCategoryFilter("all"); setSelectedDivision(""); }} data-testid="button-clear-filters">
                Clear filters
              </Button>
            </div>
          ) : selectedDivision && groupedBots.length > 0 ? (
            // Grouped view by category
            <div className="space-y-6">
              {groupedBots.map(({ category, bots }) => (
                <div key={category}>
                  <div className="flex items-center gap-3 mb-3 pb-3 border-b border-border/40">
                    <h2 className="text-sm font-semibold capitalize" data-testid={`category-header-${category.toLowerCase().replace(/[^a-z0-9]+/g, "-")}`}>{category}</h2>
                    <Badge variant="outline" className="text-[10px]" data-testid={`category-count-${category.toLowerCase().replace(/[^a-z0-9]+/g, "-")}`}>{bots.length}</Badge>
                  </div>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    {bots.map((bot: any) => (
                      <Link key={bot.id} href={`/bot/${bot.id}`}>
                        <Card className="hover-elevate cursor-pointer" data-testid={`bot-card-${bot.id}`}>
                          <CardContent className="p-4">
                            <div className="flex items-start justify-between gap-3">
                              <div className="min-w-0 flex-1">
                                <div className="flex items-center gap-2 flex-wrap">
                                  <h3 className="text-sm font-semibold truncate">{bot.displayName}</h3>
                                  <span className={cn("h-2 w-2 rounded-full flex-shrink-0", STATUS_COLORS[bot.status] ?? STATUS_COLORS.active)} />
                                </div>
                                <p className="text-[11px] font-mono text-muted-foreground mt-0.5">{bot.slug}</p>
                              </div>
                              <div className="flex items-center gap-1.5 flex-shrink-0">
                                <Badge variant="outline" className={cn("rounded-full text-[10px] capitalize", TIER_COLORS[bot.tier])}>
                                  {bot.tier}
                                </Badge>
                                <ChevronRight className="h-3.5 w-3.5 text-muted-foreground" />
                              </div>
                            </div>

                            {bot.description && (
                              <p className="text-xs text-muted-foreground mt-2 line-clamp-2">{bot.description}</p>
                            )}

                            {bot.revenueModel && (
                              <div className="mt-2 flex items-center gap-1.5">
                                <CircleDollarSign className="h-3 w-3 text-muted-foreground/60 flex-shrink-0" />
                                <p className="text-[10px] text-muted-foreground/80">{bot.revenueModel}</p>
                              </div>
                            )}

                            {bot.targetUsers && (
                              <div className="mt-1.5 flex items-center gap-1.5">
                                <Users className="h-3 w-3 text-muted-foreground/60 flex-shrink-0" />
                                <p className="text-[10px] text-muted-foreground/80">{bot.targetUsers}</p>
                              </div>
                            )}

                            <div className="mt-3 flex flex-wrap items-center gap-1.5">
                              <Badge variant="secondary" className="rounded-full text-[10px]">{bot.division}</Badge>
                              {bot.priceRange && (
                                <Badge variant="outline" className="rounded-full text-[10px] text-green-600 dark:text-green-400 border-green-500/20">
                                  {bot.priceRange}
                                </Badge>
                              )}
                            </div>

                            {Array.isArray(bot.capabilities) && bot.capabilities.length > 0 && (
                              <div className="mt-2 flex flex-wrap gap-1">
                                {bot.capabilities.slice(0, 3).map((cap: string, i: number) => (
                                  <span key={i} className="text-[10px] px-1.5 py-0.5 rounded bg-muted text-muted-foreground">{cap}</span>
                                ))}
                                {bot.capabilities.length > 3 && (
                                  <span className="text-[10px] text-muted-foreground">+{bot.capabilities.length - 3}</span>
                                )}
                              </div>
                            )}
                          </CardContent>
                        </Card>
                      </Link>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            // Standard grid view
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {botsToShow.map((bot: any) => (
                <Link key={bot.id} href={`/bot/${bot.id}`}>
                  <Card className="hover-elevate cursor-pointer" data-testid={`bot-card-${bot.id}`}>
                    <CardContent className="p-4">
                      <div className="flex items-start justify-between gap-3">
                        <div className="min-w-0 flex-1">
                          <div className="flex items-center gap-2 flex-wrap">
                            <h3 className="text-sm font-semibold truncate">{bot.displayName}</h3>
                            <span className={cn("h-2 w-2 rounded-full flex-shrink-0", STATUS_COLORS[bot.status] ?? STATUS_COLORS.active)} />
                          </div>
                          <p className="text-[11px] font-mono text-muted-foreground mt-0.5">{bot.slug}</p>
                        </div>
                        <div className="flex items-center gap-1.5 flex-shrink-0">
                          <Badge variant="outline" className={cn("rounded-full text-[10px] capitalize", TIER_COLORS[bot.tier])}>
                            {bot.tier}
                          </Badge>
                          <ChevronRight className="h-3.5 w-3.5 text-muted-foreground" />
                        </div>
                      </div>

                      {bot.description && (
                        <p className="text-xs text-muted-foreground mt-2 line-clamp-2">{bot.description}</p>
                      )}

                      {bot.revenueModel && (
                        <div className="mt-2 flex items-center gap-1.5">
                          <CircleDollarSign className="h-3 w-3 text-muted-foreground/60 flex-shrink-0" />
                          <p className="text-[10px] text-muted-foreground/80">{bot.revenueModel}</p>
                        </div>
                      )}

                      {bot.targetUsers && (
                        <div className="mt-1.5 flex items-center gap-1.5">
                          <Users className="h-3 w-3 text-muted-foreground/60 flex-shrink-0" />
                          <p className="text-[10px] text-muted-foreground/80">{bot.targetUsers}</p>
                        </div>
                      )}

                      <div className="mt-3 flex flex-wrap items-center gap-1.5">
                        <Badge variant="secondary" className="rounded-full text-[10px]">{bot.division}</Badge>
                        <Badge variant="outline" className="rounded-full text-[10px] capitalize">{bot.category}</Badge>
                        {bot.priceRange && (
                          <Badge variant="outline" className="rounded-full text-[10px] text-green-600 dark:text-green-400 border-green-500/20">
                            {bot.priceRange}
                          </Badge>
                        )}
                      </div>

                      {Array.isArray(bot.capabilities) && bot.capabilities.length > 0 && (
                        <div className="mt-2 flex flex-wrap gap-1">
                          {bot.capabilities.slice(0, 3).map((cap: string, i: number) => (
                            <span key={i} className="text-[10px] px-1.5 py-0.5 rounded bg-muted text-muted-foreground">{cap}</span>
                          ))}
                          {bot.capabilities.length > 3 && (
                            <span className="text-[10px] text-muted-foreground">+{bot.capabilities.length - 3}</span>
                          )}
                        </div>
                      )}
                    </CardContent>
                  </Card>
                </Link>
              ))}
            </div>
          )}
        </div>
      </div>
    </AppShell>
  );
}
