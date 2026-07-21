import { useMemo, useState } from "react";
import { useQueryClient } from "@tanstack/react-query";
import {
  useListBots, getListBotsQueryKey, useRunBot,
} from "@workspace/api-client-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Building2, Bot, TrendingUp, Layers, Activity, Play, Check } from "lucide-react";

type Division = {
  slug: string;
  name: string;
  description: string;
  categories: string[];
  icon: React.ReactNode;
};

const DIVISIONS: Division[] = [
  {
    slug: "dreamrealestate",
    name: "DreamRealEstate",
    description: "Foreclosure intelligence, home buyer automation, rental cashflow analytics.",
    categories: ["Real Estate"],
    icon: <Building2 className="h-6 w-6 text-primary" />,
  },
  {
    slug: "dreamsalespro",
    name: "DreamSalesPro",
    description: "Lead generation, pipeline automation, CRM orchestration, outbound at scale.",
    categories: ["Lead Generation", "Marketing", "Sales"],
    icon: <TrendingUp className="h-6 w-6 text-primary" />,
  },
  {
    slug: "dreamfinance",
    name: "DreamFinance",
    description: "Trading bots, wealth systems, payment infrastructure, billing pipelines.",
    categories: ["Finance", "Payments", "Billing"],
    icon: <Activity className="h-6 w-6 text-primary" />,
  },
  {
    slug: "dreamai",
    name: "DreamAI",
    description: "Quantum research, space AI, autonomous reasoning, voice & media synthesis.",
    categories: ["AI Research", "AI Companion", "Media", "Core"],
    icon: <Layers className="h-6 w-6 text-primary" />,
  },
  {
    slug: "dreamsoft",
    name: "DreamSoft",
    description: "SaaS platforms, software automation, infrastructure intelligence.",
    categories: ["SaaS", "Software", "Infrastructure", "Data", "Automation"],
    icon: <Bot className="h-6 w-6 text-primary" />,
  },
  {
    slug: "dreamgov",
    name: "DreamGov",
    description: "Government contracts, grants, legal pipelines, regulatory navigation.",
    categories: ["Government", "Legal", "Health", "Education"],
    icon: <Building2 className="h-6 w-6 text-primary" />,
  },
];

const tierColors: Record<string, string> = {
  FREE: "bg-muted text-muted-foreground border-border",
  PRO: "bg-blue-500/10 text-blue-400 border-blue-500/30",
  ENTERPRISE: "bg-amber-500/10 text-amber-400 border-amber-500/30",
};

const statusColors: Record<string, string> = {
  active: "bg-primary",
  idle: "bg-amber-500",
  error: "bg-destructive",
};

export default function Divisions() {
  const [justRan, setJustRan] = useState<Record<string, number>>({});
  const queryClient = useQueryClient();
  const { data: bots, isLoading } = useListBots({
    query: { queryKey: getListBotsQueryKey() },
  });
  const runBot = useRunBot({
    mutation: {
      onSuccess: (_d, vars) => {
        setJustRan((m) => ({ ...m, [vars.name]: Date.now() }));
        queryClient.invalidateQueries({ queryKey: getListBotsQueryKey() });
      },
    },
  });

  const divisionData = useMemo(() => {
    const all = bots || [];
    return DIVISIONS.map((div) => {
      const divBots = all.filter((b) =>
        b.division
          ? b.division === div.name
          : div.categories.includes(b.category),
      );
      const revenue = divBots.reduce((s, b) => s + (b.revenue || 0), 0);
      const active = divBots.filter((b) => b.status === "active").length;
      const manifestBacked = divBots.filter((b) => b.source === "manifest").length;
      return { ...div, bots: divBots, revenue, active, manifestBacked };
    });
  }, [bots]);

  const totalRevenue = divisionData.reduce((s, d) => s + d.revenue, 0);

  return (
    <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="flex flex-col gap-2">
        <h1 className="text-3xl font-mono font-bold tracking-tight text-foreground uppercase flex items-center gap-3">
          <Building2 className="h-8 w-8 text-primary" />
          Division_Command
        </h1>
        <p className="text-muted-foreground font-mono text-sm uppercase tracking-wider">
          Strategic Business Units // {DIVISIONS.length} Divisions Active
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card className="border-border/40 bg-card/50 backdrop-blur">
          <CardContent className="p-6">
            <p className="text-xs font-mono text-muted-foreground uppercase tracking-wider">Divisions</p>
            <h3 className="text-3xl font-mono font-bold text-foreground mt-2">{DIVISIONS.length}</h3>
          </CardContent>
        </Card>
        <Card className="border-border/40 bg-card/50 backdrop-blur">
          <CardContent className="p-6">
            <p className="text-xs font-mono text-muted-foreground uppercase tracking-wider">Total Bots Assigned</p>
            {isLoading ? <Skeleton className="h-8 w-16 mt-2" /> : (
              <h3 className="text-3xl font-mono font-bold text-foreground mt-2">{divisionData.reduce((s, d) => s + d.bots.length, 0)}</h3>
            )}
          </CardContent>
        </Card>
        <Card className="border-border/40 bg-card/50 backdrop-blur">
          <CardContent className="p-6">
            <p className="text-xs font-mono text-muted-foreground uppercase tracking-wider">Combined Revenue</p>
            {isLoading ? <Skeleton className="h-8 w-24 mt-2" /> : (
              <h3 className="text-3xl font-mono font-bold text-primary mt-2">${totalRevenue.toLocaleString(undefined, { maximumFractionDigits: 0 })}</h3>
            )}
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {divisionData.map((div) => (
          <Card key={div.slug} className="border-border/40 bg-card/50 backdrop-blur hover:border-primary/40 transition-colors">
            <CardHeader>
              <div className="flex items-start justify-between gap-4">
                <div className="flex items-start gap-3">
                  <div className="h-12 w-12 rounded-md bg-primary/10 flex items-center justify-center shrink-0">
                    {div.icon}
                  </div>
                  <div>
                    <CardTitle className="font-mono text-lg uppercase">{div.name}</CardTitle>
                    <p className="text-xs text-muted-foreground mt-1 max-w-md">{div.description}</p>
                  </div>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="mb-3 text-[10px] font-mono uppercase tracking-wider text-muted-foreground">
                Manifest-Backed: {div.manifestBacked} / {div.bots.length}
              </div>
              <div className="grid grid-cols-3 gap-3 mb-4">
                <div className="rounded-md border border-border/40 bg-background/50 p-3">
                  <p className="text-xs font-mono text-muted-foreground uppercase">Bots</p>
                  {isLoading ? <Skeleton className="h-6 w-10 mt-1" /> : (
                    <p className="text-xl font-mono font-bold text-foreground mt-1">{div.bots.length}</p>
                  )}
                </div>
                <div className="rounded-md border border-border/40 bg-background/50 p-3">
                  <p className="text-xs font-mono text-muted-foreground uppercase">Active</p>
                  {isLoading ? <Skeleton className="h-6 w-10 mt-1" /> : (
                    <p className="text-xl font-mono font-bold text-primary mt-1">{div.active}</p>
                  )}
                </div>
                <div className="rounded-md border border-border/40 bg-background/50 p-3">
                  <p className="text-xs font-mono text-muted-foreground uppercase">Revenue</p>
                  {isLoading ? <Skeleton className="h-6 w-16 mt-1" /> : (
                    <p className="text-xl font-mono font-bold text-foreground mt-1">${div.revenue.toLocaleString(undefined, { maximumFractionDigits: 0 })}</p>
                  )}
                </div>
              </div>

              <div className="space-y-1.5 max-h-48 overflow-y-auto pr-1">
                {isLoading ? (
                  <Skeleton className="h-24 w-full" />
                ) : div.bots.length === 0 ? (
                  <p className="text-xs font-mono text-muted-foreground text-center py-4">No bots assigned</p>
                ) : (
                  div.bots.slice(0, 8).map((bot) => {
                    const ran = justRan[bot.name] && Date.now() - justRan[bot.name]! < 4000;
                    const isRunning = runBot.isPending && runBot.variables?.name === bot.name;
                    return (
                      <div key={bot.name} className="flex items-center justify-between gap-2 px-3 py-2 rounded-md border border-border/40 bg-background/30 text-xs font-mono">
                        <div className="flex items-center gap-2 min-w-0 flex-1">
                          <div className={`h-1.5 w-1.5 rounded-full shrink-0 ${statusColors[bot.status] || "bg-muted"} ${bot.status === "active" ? "animate-pulse" : ""}`} />
                          <span className="text-foreground truncate">{bot.name}</span>
                        </div>
                        <Badge variant="outline" className={`text-[10px] uppercase ${tierColors[bot.tier] ?? tierColors.FREE}`}>{bot.tier}</Badge>
                        <Button
                          size="sm"
                          variant="ghost"
                          className="h-6 px-2 font-mono text-[10px] uppercase hover:bg-primary/10 hover:text-primary"
                          disabled={isRunning}
                          onClick={() => runBot.mutate({ name: bot.name })}
                        >
                          {ran ? <Check className="h-3 w-3 text-primary" /> : isRunning ? "…" : <Play className="h-3 w-3" />}
                        </Button>
                      </div>
                    );
                  })
                )}
                {div.bots.length > 8 && (
                  <p className="text-xs font-mono text-muted-foreground text-center pt-2">+ {div.bots.length - 8} more</p>
                )}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
