import { useState } from "react";
import { useQueryClient } from "@tanstack/react-query";
import {
  useListBots,
  getListBotsQueryKey,
  useRunBot,
} from "@workspace/api-client-react";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Skeleton } from "@/components/ui/skeleton";
import { Search, Bot, GitPullRequest, DollarSign, FileCheck2, Play, Check } from "lucide-react";

export default function Bots() {
  const [search, setSearch] = useState("");
  const [tierFilter, setTierFilter] = useState<string>("ALL");
  const [statusFilter, setStatusFilter] = useState<string>("ALL");
  const [justRan, setJustRan] = useState<Record<string, number>>({});

  const queryClient = useQueryClient();
  const { data: bots, isLoading } = useListBots({
    query: { queryKey: getListBotsQueryKey() }
  });
  const runBot = useRunBot({
    mutation: {
      onSuccess: (_data, vars) => {
        setJustRan((m) => ({ ...m, [vars.name]: Date.now() }));
        queryClient.invalidateQueries({ queryKey: getListBotsQueryKey() });
      },
    },
  });

  const manifestCount = bots?.filter(b => b.source === "manifest").length ?? 0;

  const filteredBots = bots?.filter(bot => {
    const matchesSearch = bot.name.toLowerCase().includes(search.toLowerCase()) ||
                          bot.category.toLowerCase().includes(search.toLowerCase());
    const matchesTier = tierFilter === "ALL" || bot.tier === tierFilter;
    const matchesStatus = statusFilter === "ALL" || bot.status === statusFilter.toLowerCase();

    return matchesSearch && matchesTier && matchesStatus;
  });

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-primary';
      case 'idle': return 'bg-amber-500';
      case 'error': return 'bg-destructive';
      default: return 'bg-muted';
    }
  };

  const getTierColor = (tier: string) => {
    switch (tier) {
      case 'FREE': return 'bg-muted text-muted-foreground border-muted-foreground/20';
      case 'PRO': return 'bg-blue-500/10 text-blue-500 border-blue-500/20';
      case 'ENTERPRISE': return 'bg-purple-500/10 text-purple-400 border-purple-500/20';
      default: return 'bg-muted';
    }
  };

  return (
    <div className="space-y-6 animate-in fade-in duration-500">
      <div className="flex flex-col gap-2">
        <h1 className="text-3xl font-mono font-bold tracking-tight text-foreground uppercase flex items-center gap-3">
          <Bot className="h-8 w-8 text-primary" />
          Bot_Registry
        </h1>
        <p className="text-muted-foreground font-mono text-sm uppercase tracking-wider">
          Total Fleet: {bots?.length || 0} // Active: {bots?.filter(b => b.status === 'active').length || 0} // Manifest-Backed: {manifestCount}
        </p>
      </div>

      <div className="flex flex-col md:flex-row gap-4 items-center bg-card/30 p-4 border border-border/40 rounded-lg backdrop-blur">
        <div className="relative w-full md:w-96">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search by name or category..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-9 font-mono bg-background/50 border-border/40"
          />
        </div>

        <Select value={tierFilter} onValueChange={setTierFilter}>
          <SelectTrigger className="w-full md:w-48 font-mono bg-background/50 border-border/40">
            <SelectValue placeholder="Filter by Tier" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="ALL">All Tiers</SelectItem>
            <SelectItem value="FREE">FREE</SelectItem>
            <SelectItem value="PRO">PRO</SelectItem>
            <SelectItem value="ENTERPRISE">ENTERPRISE</SelectItem>
          </SelectContent>
        </Select>

        <Select value={statusFilter} onValueChange={setStatusFilter}>
          <SelectTrigger className="w-full md:w-48 font-mono bg-background/50 border-border/40">
            <SelectValue placeholder="Filter by Status" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="ALL">All Statuses</SelectItem>
            <SelectItem value="ACTIVE">Active</SelectItem>
            <SelectItem value="IDLE">Idle</SelectItem>
            <SelectItem value="ERROR">Error</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {[1, 2, 3, 4, 5, 6].map(i => (
            <Skeleton key={i} className="h-40 w-full rounded-xl" />
          ))}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          {filteredBots?.map((bot, i) => (
            <Card key={bot.name} className="border-border/40 bg-card/50 backdrop-blur hover:border-primary/50 transition-all duration-300 group overflow-hidden relative">
              <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-primary/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
              <CardContent className="p-5">
                <div className="flex justify-between items-start mb-4">
                  <div className="min-w-0">
                    <h3 className="font-mono font-bold text-lg text-foreground truncate max-w-[180px]">{bot.displayName || bot.name}</h3>
                    <p className="font-mono text-xs text-muted-foreground uppercase truncate">{bot.category}{bot.division ? ` // ${bot.division}` : ""}</p>
                  </div>
                  <div className="flex items-center gap-2">
                    {bot.source === "manifest" && (
                      <div className="flex items-center gap-1 bg-primary/10 px-1.5 py-1 rounded-md border border-primary/30" title="Backed by bot.manifest.json">
                        <FileCheck2 className="h-3 w-3 text-primary" />
                      </div>
                    )}
                    <div className="flex items-center gap-1.5 bg-background/50 px-2 py-1 rounded-md border border-border/40">
                      <div className={`h-2 w-2 rounded-full ${getStatusColor(bot.status)} ${bot.status === 'active' ? 'animate-pulse' : ''}`} />
                      <span className="font-mono text-[10px] uppercase text-muted-foreground">{bot.status}</span>
                    </div>
                  </div>
                </div>

                {bot.capabilities && bot.capabilities.length > 0 && (
                  <div className="mt-3 flex flex-wrap gap-1">
                    {bot.capabilities.slice(0, 4).map((cap) => (
                      <span key={cap} className="text-[9px] font-mono uppercase tracking-wider px-1.5 py-0.5 rounded border border-primary/20 bg-primary/5 text-primary/80">
                        {cap.replace(/_/g, " ")}
                      </span>
                    ))}
                    {bot.capabilities.length > 4 && (
                      <span className="text-[9px] font-mono uppercase tracking-wider px-1.5 py-0.5 text-muted-foreground">
                        +{bot.capabilities.length - 4}
                      </span>
                    )}
                  </div>
                )}

                <div className="flex justify-between items-center mt-6">
                  <Badge variant="outline" className={`font-mono text-[10px] uppercase rounded-sm border ${getTierColor(bot.tier)}`}>
                    {bot.tier}
                  </Badge>

                  <div className="flex gap-3 text-muted-foreground">
                    <div className="flex items-center gap-1" title="Revenue">
                      <DollarSign className="h-3.5 w-3.5" />
                      <span className="font-mono text-xs">{bot.revenue?.toLocaleString() || 0}</span>
                    </div>
                    <div className="flex items-center gap-1" title="Pending PRs">
                      <GitPullRequest className="h-3.5 w-3.5" />
                      <span className="font-mono text-xs">{bot.pendingPRs || 0}</span>
                    </div>
                  </div>
                </div>

                <div className="mt-4 pt-4 border-t border-border/40">
                  <Button
                    size="sm"
                    variant="outline"
                    className="w-full font-mono text-xs uppercase tracking-wider border-primary/30 hover:border-primary hover:bg-primary/10"
                    disabled={runBot.isPending && runBot.variables?.name === bot.name}
                    onClick={() => runBot.mutate({ name: bot.name })}
                  >
                    {justRan[bot.name] && Date.now() - justRan[bot.name]! < 4000 ? (
                      <><Check className="h-3 w-3 mr-1.5 text-primary" />Ran</>
                    ) : runBot.isPending && runBot.variables?.name === bot.name ? (
                      <>Running…</>
                    ) : (
                      <><Play className="h-3 w-3 mr-1.5" />Run</>
                    )}
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
