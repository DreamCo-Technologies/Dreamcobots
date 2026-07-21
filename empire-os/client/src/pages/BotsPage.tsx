import { useMemo, useState } from "react";
import Seo from "@/components/Seo";
import AppShell from "@/components/AppShell";
import EmptyState from "@/components/EmptyState";
import ConfirmDialog from "@/components/ConfirmDialog";
import { useBots, useCreateBot, useSetDefaultBot, useUpdateBot } from "@/hooks/use-bots";
import { useToast } from "@/hooks/use-toast";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Skeleton } from "@/components/ui/skeleton";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { cn } from "@/lib/utils";
import { Bot, ChevronRight, Crown, Pencil, Plus, Save, Search, Filter, Building2 } from "lucide-react";
import { Link } from "wouter";
import type { CreateBotProfileRequest, UpdateBotProfileRequest } from "@shared/schema";
import { DIVISIONS, BOT_TIERS } from "@shared/schema";

const TIER_COLORS: Record<string, string> = {
  free: "bg-muted text-muted-foreground",
  pro: "bg-[rgb(59_130_246)]/15 text-[rgb(59_130_246)] border border-[rgb(59_130_246)]/20",
  enterprise: "bg-[rgb(168_85_247)]/15 text-[rgb(168_85_247)] border border-[rgb(168_85_247)]/20",
  elite: "bg-[rgb(245_158_11)]/15 text-[rgb(245_158_11)] border border-[rgb(245_158_11)]/20",
};

function defaultSystemPrompt(name: string) {
  return `You are ${name}, a realistic, practical assistant.
Be concise, ask clarifying questions, and propose executable next steps.
Avoid hype. Prefer checklists and constraints.
When user asks about autonomous income, help them design safe, legal, repeatable systems with clear KPIs.`;
}

export default function BotsPage() {
  const { toast } = useToast();
  const bots = useBots();
  const createBot = useCreateBot();
  const updateBot = useUpdateBot();
  const setDefault = useSetDefaultBot();

  const [activeBotSlug, setActiveBotSlug] = useState<string | undefined>(undefined);

  const [createOpen, setCreateOpen] = useState(false);
  const [editOpen, setEditOpen] = useState(false);
  const [editId, setEditId] = useState<number | null>(null);

  const [confirmDefaultOpen, setConfirmDefaultOpen] = useState(false);
  const [defaultTargetId, setDefaultTargetId] = useState<number | null>(null);

  const [searchQuery, setSearchQuery] = useState("");
  const [divisionFilter, setDivisionFilter] = useState<string>("all");
  const [tierFilter, setTierFilter] = useState<string>("all");
  const [categoryFilter, setCategoryFilter] = useState<string>("all");

  const editingBot = useMemo(() => (bots.data ?? []).find((b) => b.id === editId) ?? null, [bots.data, editId]);

  const filteredBots = useMemo(() => {
    let list = bots.data ?? [];

    if (searchQuery) {
      const q = searchQuery.toLowerCase();
      list = list.filter((b) =>
        b.displayName.toLowerCase().includes(q) ||
        b.slug.toLowerCase().includes(q) ||
        b.description?.toLowerCase().includes(q) ||
        b.division?.toLowerCase().includes(q)
      );
    }

    if (divisionFilter !== "all") {
      list = list.filter((b) => b.division === divisionFilter);
    }

    if (tierFilter !== "all") {
      list = list.filter((b) => b.tier === tierFilter);
    }

    if (categoryFilter !== "all") {
      list = list.filter((b) => b.category === categoryFilter);
    }

    return list.sort((a, b) => a.displayName.localeCompare(b.displayName));
  }, [bots.data, searchQuery, divisionFilter, tierFilter, categoryFilter]);

  const availableCategories = useMemo(() => {
    const cats = new Set(filteredBots.map((b) => b.category));
    return Array.from(cats).sort();
  }, [filteredBots]);

  const isFilterActive = searchQuery || divisionFilter !== "all" || tierFilter !== "all" || categoryFilter !== "all";

  const clearFilters = () => {
    setSearchQuery("");
    setDivisionFilter("all");
    setTierFilter("all");
    setCategoryFilter("all");
  };

  const [createForm, setCreateForm] = useState<CreateBotProfileRequest>({
    slug: "dream-bot",
    displayName: "DreamBot",
    systemPrompt: defaultSystemPrompt("DreamBot"),
    traits: {},
    isDefault: false as any,
  });

  const [editForm, setEditForm] = useState<UpdateBotProfileRequest>({});

  return (
    <AppShell selectedBotSlug={activeBotSlug} onBotChange={setActiveBotSlug}>
      <Seo title="DreamCo Empire OS — Bot Fleet" description="Manage bot profiles: system prompts, traits, and default bot." />

      <ConfirmDialog
        open={confirmDefaultOpen}
        onOpenChange={setConfirmDefaultOpen}
        title="Set as default bot?"
        description="New chats will use this bot by default (you can still switch anytime)."
        confirmLabel={setDefault.isPending ? "Setting…" : "Set default"}
        onConfirm={async () => {
          if (!defaultTargetId) return;
          try {
            await setDefault.mutateAsync(defaultTargetId);
            toast({ title: "Default bot updated" });
            setConfirmDefaultOpen(false);
          } catch (e: any) {
            toast({ title: "Failed to set default", description: e?.message ?? "Unknown error", variant: "destructive" });
          }
        }}
        data-testid="confirm-default-bot"
      />

      <div className="buddy-appear">
        <div className="flex flex-col sm:flex-row sm:items-end sm:justify-between gap-4">
          <div>
            <h2 className="text-3xl md:text-4xl">Bots</h2>
            <p className="mt-2 text-muted-foreground">
              Tune personality, constraints, and realism with system prompts.
            </p>
          </div>

          <Dialog open={createOpen} onOpenChange={setCreateOpen}>
            <DialogTrigger asChild>
              <Button
                className="rounded-xl bg-gradient-to-r from-primary to-accent text-primary-foreground shadow-md shadow-primary/20 hover:shadow-lg hover:shadow-primary/25 hover:-translate-y-0.5 active:translate-y-0 transition-all"
                data-testid="open-create-bot"
                onClick={() => {
                  setCreateForm({
                    slug: "dream-" + Math.random().toString(16).slice(2, 6),
                    displayName: "DreamBot Variant",
                    systemPrompt: defaultSystemPrompt("DreamBot"),
                    traits: { tone: "calm", style: "practical" } as any,
                    isDefault: false as any,
                  });
                }}
              >
                <Plus className="h-4 w-4 mr-2" />
                New bot
              </Button>
            </DialogTrigger>

            <DialogContent className="rounded-2xl">
              <DialogHeader>
                <DialogTitle>Create bot profile</DialogTitle>
              </DialogHeader>

              <div className="grid gap-4">
                <div className="grid gap-2">
                  <p className="text-sm font-medium">Slug</p>
                  <Input
                    value={(createForm as any).slug ?? ""}
                    onChange={(e) => setCreateForm((p) => ({ ...(p as any), slug: e.target.value }))}
                    className="rounded-xl"
                    placeholder="dream-bot"
                    data-testid="create-bot-slug"
                  />
                  <p className="text-xs text-muted-foreground">Used as botSlug when chatting.</p>
                </div>

                <div className="grid gap-2">
                  <p className="text-sm font-medium">Display name</p>
                  <Input
                    value={(createForm as any).displayName ?? ""}
                    onChange={(e) => setCreateForm((p) => ({ ...(p as any), displayName: e.target.value }))}
                    className="rounded-xl"
                    placeholder="DreamBot"
                    data-testid="create-bot-displayName"
                  />
                </div>

                <div className="grid gap-2">
                  <p className="text-sm font-medium">System prompt</p>
                  <Textarea
                    value={(createForm as any).systemPrompt ?? ""}
                    onChange={(e) => setCreateForm((p) => ({ ...(p as any), systemPrompt: e.target.value }))}
                    className="rounded-2xl min-h-[160px]"
                    data-testid="create-bot-systemPrompt"
                  />
                </div>

                <div className="grid gap-2">
                  <p className="text-sm font-medium">Traits (JSON)</p>
                  <Textarea
                    value={JSON.stringify((createForm as any).traits ?? {}, null, 2)}
                    onChange={(e) => {
                      try {
                        const parsed = JSON.parse(e.target.value || "{}");
                        setCreateForm((p) => ({ ...(p as any), traits: parsed }));
                      } catch {
                        // keep typing
                      }
                    }}
                    className="rounded-2xl min-h-[120px] font-mono text-xs"
                    data-testid="create-bot-traits"
                  />
                </div>

                <Button
                  onClick={async () => {
                    try {
                      await createBot.mutateAsync(createForm);
                      toast({ title: "Bot created", description: "You can now select it in the sidebar." });
                      setCreateOpen(false);
                    } catch (e: any) {
                      toast({ title: "Create failed", description: e?.message ?? "Unknown error", variant: "destructive" });
                    }
                  }}
                  disabled={createBot.isPending}
                  className="rounded-xl bg-gradient-to-r from-primary to-accent text-primary-foreground shadow-md shadow-primary/20 hover:shadow-lg hover:shadow-primary/25 hover:-translate-y-0.5 active:translate-y-0 transition-all"
                  data-testid="create-bot-submit"
                >
                  {createBot.isPending ? "Creating…" : "Create bot"}
                </Button>
              </div>
            </DialogContent>
          </Dialog>
        </div>

        <div className="mt-6 space-y-4">
          <div className="flex flex-col gap-4">
            <div className="flex flex-col sm:flex-row gap-3 items-start sm:items-end flex-wrap">
              <div className="flex-1 min-w-[200px]">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                  <Input
                    type="text"
                    placeholder="Search bots..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="pl-9 rounded-xl"
                    data-testid="search-bots-input"
                  />
                </div>
              </div>

              <Select value={divisionFilter} onValueChange={setDivisionFilter}>
                <SelectTrigger className="w-full sm:w-[180px] rounded-xl" data-testid="filter-division-select">
                  <Building2 className="h-4 w-4 mr-2" />
                  <SelectValue placeholder="Division" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Divisions</SelectItem>
                  {DIVISIONS.map((div) => (
                    <SelectItem key={div} value={div}>
                      {div}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>

              <Select value={tierFilter} onValueChange={setTierFilter}>
                <SelectTrigger className="w-full sm:w-[140px] rounded-xl" data-testid="filter-tier-select">
                  <SelectValue placeholder="Tier" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Tiers</SelectItem>
                  {BOT_TIERS.map((tier) => (
                    <SelectItem key={tier} value={tier}>
                      {tier.charAt(0).toUpperCase() + tier.slice(1)}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>

              <Select value={categoryFilter} onValueChange={setCategoryFilter}>
                <SelectTrigger className="w-full sm:w-[160px] rounded-xl" data-testid="filter-category-select">
                  <SelectValue placeholder="Category" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Categories</SelectItem>
                  {availableCategories.map((cat) => (
                    <SelectItem key={cat} value={cat}>
                      {cat.charAt(0).toUpperCase() + cat.slice(1)}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>

              {isFilterActive && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={clearFilters}
                  className="rounded-xl border-border/70"
                  data-testid="clear-filters-button"
                >
                  <Filter className="h-4 w-4 mr-2" />
                  Clear filters
                </Button>
              )}
            </div>

            {isFilterActive && (
              <div className="flex items-center gap-2">
                <Badge variant="secondary" className="rounded-full" data-testid="result-count-badge">
                  {filteredBots.length} result{filteredBots.length !== 1 ? "s" : ""}
                </Badge>
              </div>
            )}
          </div>

            {bots.isLoading ? (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 md:gap-5">
                <Skeleton className="h-52 rounded-3xl" />
                <Skeleton className="h-52 rounded-3xl" />
                <Skeleton className="h-52 rounded-3xl" />
                <Skeleton className="h-52 rounded-3xl" />
              </div>
            ) : bots.isError ? (
              <EmptyState
              icon={<Bot className="h-6 w-6" />}
              title="Couldn’t load bots"
              description={(bots.error as any)?.message ?? "Unknown error"}
              action={
                <Button onClick={() => bots.refetch()} className="rounded-xl" data-testid="retry-bots">
                  Retry
                </Button>
              }
            />
          ) : (bots.data ?? []).length === 0 ? (
            <EmptyState
              icon={<Bot className="h-6 w-6" />}
              title="No bots yet"
              description="Create your first bot profile to control tone and behavior."
              action={
                <Button onClick={() => setCreateOpen(true)} className="rounded-xl" data-testid="empty-create-bot">
                  Create bot
                </Button>
              }
            />
          ) : filteredBots.length === 0 ? (
            <EmptyState
              icon={<Bot className="h-6 w-6" />}
              title="No bots match your filters"
              description="Try adjusting your search or filter criteria."
              action={
                <Button onClick={clearFilters} className="rounded-xl" data-testid="clear-all-filters">
                  Clear all filters
                </Button>
              }
            />
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 md:gap-5 buddy-stagger">
              {filteredBots.map((b) => (
                <Card key={b.id} className="buddy-card buddy-card-hover rounded-3xl border-border/60 p-6 md:p-7">
                  <div className="flex items-start justify-between gap-4">
                    <div className="min-w-0">
                      <div className="flex items-center gap-2">
                        <div className="h-10 w-10 rounded-2xl bg-gradient-to-br from-primary/18 via-accent/10 to-transparent border border-border/60 shadow-sm flex items-center justify-center text-primary">
                          <Bot className="h-5 w-5" />
                        </div>
                        <div className="min-w-0">
                          <p className="text-lg md:text-xl truncate">{b.displayName}</p>
                          <p className="text-xs text-muted-foreground font-mono truncate">
                            slug: {b.slug}
                          </p>
                        </div>
                      </div>

                      <div className="mt-4 flex flex-wrap gap-2">
                        {b.isDefault && (
                          <Badge className="rounded-full bg-primary/12 text-primary border border-primary/20" data-testid={`badge-default-${b.id}`}>
                            <Crown className="h-3.5 w-3.5 mr-1" />
                            Default
                          </Badge>
                        )}
                        {b.division && (
                          <Badge variant="secondary" className="rounded-full" data-testid={`badge-division-${b.id}`}>
                            <Building2 className="h-3 w-3 mr-1" />
                            {b.division}
                          </Badge>
                        )}
                        {b.tier && (
                          <Badge className={cn("rounded-full", TIER_COLORS[b.tier] || "")} data-testid={`badge-tier-${b.id}`}>
                            {b.tier.charAt(0).toUpperCase() + b.tier.slice(1)}
                          </Badge>
                        )}
                        {b.category && (
                          <Badge variant="outline" className="rounded-full border-border/70" data-testid={`badge-category-${b.id}`}>
                            {b.category}
                          </Badge>
                        )}
                        {b.priceRange && (
                          <Badge variant="outline" className="rounded-full border-border/70" data-testid={`badge-price-${b.id}`}>
                            {b.priceRange}
                          </Badge>
                        )}
                      </div>

                      {b.description && (
                        <p className={cn("mt-3 text-sm text-muted-foreground line-clamp-2")}>
                          {b.description}
                        </p>
                      )}
                    </div>

                    <div className="flex flex-col gap-2 shrink-0">
                      <Dialog
                        open={editOpen && editId === b.id}
                        onOpenChange={(v) => {
                          setEditOpen(v);
                          if (!v) {
                            setEditId(null);
                            setEditForm({});
                          }
                        }}
                      >
                        <DialogTrigger asChild>
                          <Button
                            variant="outline"
                            className="rounded-xl border-border/70 bg-card/60 hover:bg-card shadow-sm hover:shadow-md transition-all"
                            onClick={() => {
                              setEditId(b.id);
                              setEditForm({
                                slug: b.slug,
                                displayName: b.displayName,
                                systemPrompt: b.systemPrompt,
                                traits: b.traits as any,
                                isDefault: b.isDefault as any,
                              });
                            }}
                            data-testid={`edit-bot-${b.id}`}
                          >
                            <Pencil className="h-4 w-4 mr-2" />
                            Edit
                          </Button>
                        </DialogTrigger>

                        <DialogContent className="rounded-2xl">
                          <DialogHeader>
                            <DialogTitle>Edit bot</DialogTitle>
                          </DialogHeader>

                          <div className="grid gap-4">
                            <div className="grid gap-2">
                              <p className="text-sm font-medium">Display name</p>
                              <Input
                                value={(editForm as any).displayName ?? ""}
                                onChange={(e) => setEditForm((p) => ({ ...(p as any), displayName: e.target.value }))}
                                className="rounded-xl"
                                data-testid="edit-bot-displayName"
                              />
                            </div>

                            <div className="grid gap-2">
                              <p className="text-sm font-medium">System prompt</p>
                              <Textarea
                                value={(editForm as any).systemPrompt ?? ""}
                                onChange={(e) => setEditForm((p) => ({ ...(p as any), systemPrompt: e.target.value }))}
                                className="rounded-2xl min-h-[180px]"
                                data-testid="edit-bot-systemPrompt"
                              />
                            </div>

                            <div className="grid gap-2">
                              <p className="text-sm font-medium">Traits (JSON)</p>
                              <Textarea
                                value={JSON.stringify((editForm as any).traits ?? {}, null, 2)}
                                onChange={(e) => {
                                  try {
                                    const parsed = JSON.parse(e.target.value || "{}");
                                    setEditForm((p) => ({ ...(p as any), traits: parsed }));
                                  } catch {
                                    // keep typing
                                  }
                                }}
                                className="rounded-2xl min-h-[120px] font-mono text-xs"
                                data-testid="edit-bot-traits"
                              />
                            </div>

                            <Button
                              onClick={async () => {
                                try {
                                  await updateBot.mutateAsync({ id: b.id, updates: editForm });
                                  toast({ title: "Bot updated" });
                                  setEditOpen(false);
                                  setEditId(null);
                                } catch (e: any) {
                                  toast({ title: "Update failed", description: e?.message ?? "Unknown error", variant: "destructive" });
                                }
                              }}
                              disabled={updateBot.isPending}
                              className="rounded-xl bg-gradient-to-r from-primary to-accent text-primary-foreground shadow-md shadow-primary/20 hover:shadow-lg hover:shadow-primary/25 hover:-translate-y-0.5 active:translate-y-0 transition-all"
                              data-testid="edit-bot-submit"
                            >
                              <Save className="h-4 w-4 mr-2" />
                              {updateBot.isPending ? "Saving…" : "Save changes"}
                            </Button>
                          </div>
                        </DialogContent>
                      </Dialog>

                      <Link href={`/bot/${b.id}`}>
                        <Button variant="outline" className="rounded-xl border-border/70" data-testid={`view-bot-${b.id}`}>
                          Details
                          <ChevronRight className="h-4 w-4 ml-1" />
                        </Button>
                      </Link>

                      <Button
                        onClick={() => {
                          setDefaultTargetId(b.id);
                          setConfirmDefaultOpen(true);
                        }}
                        disabled={b.isDefault || setDefault.isPending}
                        className={cn(
                          "rounded-xl",
                          b.isDefault
                            ? "bg-muted text-muted-foreground cursor-not-allowed"
                            : "bg-gradient-to-r from-primary to-accent text-primary-foreground shadow-md shadow-primary/20 hover:shadow-lg hover:shadow-primary/25 hover:-translate-y-0.5 active:translate-y-0 transition-all"
                        )}
                        data-testid={`set-default-bot-${b.id}`}
                      >
                        <Crown className="h-4 w-4 mr-2" />
                        {b.isDefault ? "Default" : "Set default"}
                      </Button>
                    </div>
                  </div>
                </Card>
              ))}
            </div>
          )}
        </div>
      </div>
    </AppShell>
  );
}
