import { ReactNode, useMemo, useState } from "react";
import { Link, useLocation } from "wouter";
import {
  Bot,
  Bug,
  Building2,
  Scale,
  FlaskConical as HarnessIcon,
  Calculator,
  ChevronDown,
  CircleDollarSign,
  Code,
  CreditCard,
  Globe,
  Landmark,
  LayoutDashboard,
  MessageSquareText,
  Network,
  Plug,
  Rocket,
  Shield,
  Sparkles,
  Store,
  Tag,
  Wallet,
  Workflow,
  Zap,
  FlaskConical,
  Brain,
  Clock,
  DollarSign,
  Trophy,
  Cpu,
  BrainCircuit,
  Github,
  Wrench,
  Activity,
  TestTube2,
  ListTodo,
} from "lucide-react";
import ThemeToggle from "@/components/ThemeToggle";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import { useBots } from "@/hooks/use-bots";
import { useConversations, useCreateConversation } from "@/hooks/use-conversations";
import { useEmpireOverview, useAutonomyMode } from "@/hooks/use-empire";
import { useToast } from "@/hooks/use-toast";
import { Skeleton } from "@/components/ui/skeleton";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";

const AUTONOMY_LABELS: Record<string, { label: string; color: string }> = {
  guided: { label: "Guided", color: "bg-[rgb(59_130_246)]" },
  "semi-autonomous": { label: "Semi-Auto", color: "bg-[rgb(245_158_11)]" },
  "full-autonomy": { label: "Full Auto", color: "bg-[rgb(34_197_94)]" },
};

export default function AppShell(props: {
  children: ReactNode;
  selectedBotSlug?: string;
  onBotChange?: (slug?: string) => void;
}) {
  const [location] = useLocation();
  const { toast } = useToast();

  const bots = useBots();
  const conversations = useConversations();
  const createConversation = useCreateConversation();
  const empire = useEmpireOverview();
  const autonomyQuery = useAutonomyMode();

  const autonomyMode = (autonomyQuery.data as any)?.mode ?? "guided";
  const modeInfo = AUTONOMY_LABELS[autonomyMode] ?? AUTONOMY_LABELS.guided;

  const defaultBotSlug = useMemo(() => {
    const list = bots.data ?? [];
    return list.find((b) => b.isDefault)?.slug ?? list[0]?.slug;
  }, [bots.data]);

  const [botSelectOpen, setBotSelectOpen] = useState(false);

  const nav = [
    { href: "/", label: "Chat", icon: MessageSquareText },
    { href: "/dashboard", label: "Empire HQ", icon: LayoutDashboard },
    { href: "/divisions", label: "Divisions", icon: Building2 },
    { href: "/bots", label: "Bot Fleet", icon: Bot },
    { href: "/deals", label: "Deal Analyzer", icon: Calculator },
    { href: "/formulas", label: "Formula Vault", icon: FlaskConical },
    { href: "/learning-matrix", label: "Learning Matrix", icon: Brain },
    { href: "/ai-leaders", label: "AI Leaders", icon: Trophy },
    { href: "/ai-models", label: "AI Models Hub", icon: Cpu },
    { href: "/ecosystem", label: "AI Ecosystem", icon: Globe },
    { href: "/orchestration", label: "Orchestration", icon: Network },
    { href: "/marketplace", label: "Marketplace", icon: Store },
    { href: "/crypto", label: "Crypto", icon: Wallet },
    { href: "/payments", label: "Payments", icon: CreditCard },
    { href: "/business", label: "Biz Launch", icon: Rocket },
    { href: "/bot-builder", label: "Bot Builder", icon: Wrench },
    { href: "/actions", label: "Actions & Agents", icon: ListTodo },
    { href: "/bot-activity", label: "Bot Activity & GitHub", icon: Activity },
    { href: "/harness", label: "Harness Tester", icon: HarnessIcon },
    { href: "/governance", label: "Governance", icon: Scale },
    { href: "/sandbox", label: "Sandbox Factory", icon: TestTube2 },
    { href: "/code-lab", label: "Code Lab", icon: Code },
    { href: "/loans", label: "Loans & Deals", icon: Landmark },
    { href: "/debug", label: "Debug Intel", icon: Bug },
    { href: "/revenue", label: "Revenue", icon: CircleDollarSign },
    { href: "/pricing", label: "Pricing", icon: Tag },
    { href: "/connections", label: "Connections", icon: Plug },
    { href: "/time-capsule", label: "Time Capsule", icon: Clock },
    { href: "/costs", label: "Cost Tracking", icon: DollarSign },
    { href: "/autonomy", label: "Autonomy", icon: Workflow },
  ] as const;

  const activeHref = (href: string) => (href === "/" ? location === "/" : location.startsWith(href));

  const totalBots = empire.data?.totalBots ?? 0;

  return (
    <div className="min-h-screen buddy-glow">
      <div className="buddy-container py-6 md:py-8">
        <div className="grid grid-cols-1 lg:grid-cols-[340px_1fr] gap-6 lg:gap-8">
          <aside className="buddy-card buddy-noise buddy-gradient-border overflow-hidden">
            <div className="p-5 md:p-6">
              <div className="flex items-start justify-between gap-3">
                <div className="min-w-0">
                  <div className="flex items-center gap-2">
                    <span className="inline-flex h-9 w-9 items-center justify-center rounded-2xl bg-gradient-to-br from-primary/18 via-accent/12 to-transparent border border-border/60 shadow-sm">
                      <Zap className="h-4 w-4 text-primary" />
                    </span>
                    <div className="min-w-0">
                      <p className="text-sm text-muted-foreground leading-none">DreamCo</p>
                      <h1 className="text-xl md:text-2xl leading-tight">
                        Empire OS
                      </h1>
                    </div>
                  </div>
                  <div className="mt-3 flex flex-wrap items-center gap-2">
                    <Badge variant="secondary" className="rounded-full">
                      <span className={cn("h-2 w-2 rounded-full mr-1.5", modeInfo.color)} />
                      {modeInfo.label}
                    </Badge>
                    <Badge variant="outline" className="rounded-full border-border/70">
                      {totalBots} bots
                    </Badge>
                  </div>
                </div>
                <ThemeToggle />
              </div>

              <div className="mt-5">
                <div className="flex items-center justify-between mb-2">
                  <p className="text-xs font-medium text-muted-foreground">Active bot</p>
                </div>

                <Select
                  open={botSelectOpen}
                  onOpenChange={setBotSelectOpen}
                  value={props.selectedBotSlug ?? defaultBotSlug ?? ""}
                  onValueChange={(v) => props.onBotChange?.(v || undefined)}
                >
                  <SelectTrigger
                    className="w-full rounded-xl border-border/70 bg-card/60 backdrop-blur shadow-sm focus:ring-4 focus:ring-ring/15"
                    data-testid="bot-selector"
                  >
                    <SelectValue placeholder={bots.isLoading ? "Loading bots..." : "Select a bot"} />
                  </SelectTrigger>
                  <SelectContent className="rounded-xl max-h-[300px]">
                    {(bots.data ?? []).slice(0, 50).map((b) => (
                      <SelectItem key={b.id} value={b.slug} className="rounded-lg">
                        <div className="flex items-center justify-between gap-3">
                          <span className="font-medium">{b.displayName}</span>
                          {b.isDefault ? (
                            <span className="text-xs px-2 py-0.5 rounded-full bg-primary/12 text-primary border border-primary/20">
                              default
                            </span>
                          ) : null}
                        </div>
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="mt-5 flex gap-2">
                <Button
                  onClick={async () => {
                    try {
                      const created = await createConversation.mutateAsync({ title: "New chat" } as any);
                      toast({ title: "New chat created", description: `#${created.id} ready.` });
                    } catch (e: any) {
                      toast({ title: "Couldn't create chat", description: e?.message ?? "Unknown error", variant: "destructive" });
                    }
                  }}
                  className="flex-1 rounded-xl bg-gradient-to-r from-primary to-accent text-primary-foreground shadow-md shadow-primary/20"
                  data-testid="new-chat"
                  disabled={createConversation.isPending}
                >
                  {createConversation.isPending ? "Creating..." : "New chat"}
                </Button>
              </div>

              {/* Buddy Bot quick-switch */}
              <button
                onClick={() => props.onBotChange?.("buddy-bot")}
                className="mt-3 w-full flex items-center gap-2.5 rounded-xl border border-primary/30 bg-primary/8 hover:bg-primary/14 px-3 py-2.5 text-sm font-medium text-primary transition-all hover:shadow-sm"
                data-testid="buddy-shortcut"
              >
                <span className="inline-flex h-6 w-6 items-center justify-center rounded-lg bg-primary/15 flex-shrink-0">
                  <BrainCircuit className="h-3.5 w-3.5 text-primary" />
                </span>
                <div className="min-w-0 text-left">
                  <div className="leading-none">Buddy Bot</div>
                  <div className="text-[10px] text-primary/70 mt-0.5 font-normal">Master coder · All 500+ libraries</div>
                </div>
                <span className="ml-auto text-[10px] px-1.5 py-0.5 rounded-md bg-primary/15 text-primary/80 font-mono">ELITE</span>
              </button>

              <Separator className="my-5" />

              <nav className="grid gap-1.5">
                {nav.map((item) => {
                  const Icon = item.icon;
                  const active = activeHref(item.href);
                  return (
                    <Link
                      key={item.href}
                      href={item.href}
                      className={cn(
                        "group flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition-all",
                        "border border-transparent",
                        active
                          ? "bg-gradient-to-r from-primary/14 via-accent/10 to-transparent border-border/70 shadow-sm"
                          : "text-foreground/90 hover-elevate"
                      )}
                      data-testid={`nav-${item.label.toLowerCase().replace(/\s/g, "-")}`}
                    >
                      <Icon
                        className={cn(
                          "h-4 w-4 transition-transform duration-300",
                          active ? "text-primary" : "text-muted-foreground group-hover:text-foreground",
                        )}
                      />
                      <span className="truncate">{item.label}</span>
                    </Link>
                  );
                })}
              </nav>

              <Separator className="my-5" />

              <div className="flex items-center justify-between">
                <p className="text-xs font-medium text-muted-foreground">Recent chats</p>
                <Link
                  href="/"
                  className="text-xs text-primary hover:underline underline-offset-4"
                  data-testid="view-all-chats"
                >
                  View
                </Link>
              </div>
            </div>

            <ScrollArea className="h-[220px] border-t border-border/60">
              <div className="p-4 md:p-5 space-y-2">
                {conversations.isLoading ? (
                  <div className="space-y-2">
                    <Skeleton className="h-10 rounded-xl" />
                    <Skeleton className="h-10 rounded-xl" />
                    <Skeleton className="h-10 rounded-xl" />
                  </div>
                ) : conversations.isError ? (
                  <div className="buddy-card p-4 rounded-2xl border border-destructive/30 bg-destructive/5">
                    <p className="text-sm font-medium">Couldn't load chats</p>
                    <Button
                      variant="outline"
                      className="mt-3 rounded-xl"
                      onClick={() => conversations.refetch()}
                      data-testid="retry-conversations"
                    >
                      Retry
                    </Button>
                  </div>
                ) : (conversations.data ?? []).length === 0 ? (
                  <div className="text-sm text-muted-foreground">
                    No conversations yet. Create one to start.
                  </div>
                ) : (
                  (conversations.data ?? []).slice(0, 20).map((c) => (
                    <Link
                      key={c.id}
                      href={`/c/${c.id}`}
                      className={cn(
                        "block rounded-xl border border-border/60 bg-card/40 backdrop-blur px-3 py-2.5",
                        "shadow-sm hover-elevate",
                        location === `/c/${c.id}` && "ring-2 ring-ring/20 border-border"
                      )}
                      data-testid={`conversation-${c.id}`}
                    >
                      <div className="flex items-center justify-between gap-3">
                        <p className="text-sm font-medium truncate">{c.title}</p>
                        <span className="text-[11px] font-mono text-muted-foreground">
                          #{c.id}
                        </span>
                      </div>
                    </Link>
                  ))
                )}
              </div>
            </ScrollArea>
          </aside>

          <main className="min-w-0">{props.children}</main>
        </div>
      </div>
    </div>
  );
}
