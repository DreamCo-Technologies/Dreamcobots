import { ReactNode, useMemo, useState } from "react";
import { Link, useLocation } from "wouter";
import {
  Bot,
  ChevronsUpDown,
  LayoutDashboard,
  MessageSquareText,
  Sparkles,
  Workflow,
} from "lucide-react";
import ThemeToggle from "@/components/ThemeToggle";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { ScrollArea } from "@/components/ui/scroll-area";
import { cn } from "@/lib/utils";
import { useBots } from "@/hooks/use-bots";
import { useConversations, useCreateConversation } from "@/hooks/use-conversations";
import { useToast } from "@/hooks/use-toast";
import { Skeleton } from "@/components/ui/skeleton";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";

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

  const defaultBotSlug = useMemo(() => {
    const list = bots.data ?? [];
    return list.find((b) => b.isDefault)?.slug ?? list[0]?.slug;
  }, [bots.data]);

  const [botSelectOpen, setBotSelectOpen] = useState(false);

  const nav = [
    { href: "/", label: "Chat", icon: MessageSquareText },
    { href: "/autonomy", label: "Autonomy", icon: Workflow },
    { href: "/bots", label: "Bots", icon: Bot },
    { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  ] as const;

  const activeHref = (href: string) => (href === "/" ? location === "/" : location.startsWith(href));

  return (
    <div className="min-h-screen buddy-glow">
      <div className="buddy-container py-6 md:py-8">
        <div className="grid grid-cols-1 lg:grid-cols-[340px_1fr] gap-6 lg:gap-8">
          {/* Sidebar */}
          <aside className="buddy-card buddy-noise buddy-gradient-border overflow-hidden">
            <div className="p-5 md:p-6">
              <div className="flex items-start justify-between gap-3">
                <div className="min-w-0">
                  <div className="flex items-center gap-2">
                    <span className="inline-flex h-9 w-9 items-center justify-center rounded-2xl bg-gradient-to-br from-primary/18 via-accent/12 to-transparent border border-border/60 shadow-sm">
                      <Sparkles className="h-4 w-4 text-primary" />
                    </span>
                    <div className="min-w-0">
                      <p className="text-sm text-muted-foreground leading-none">Buddy</p>
                      <h1 className="text-xl md:text-2xl leading-tight">
                        Calm autonomy studio
                      </h1>
                    </div>
                  </div>
                  <p className="mt-3 text-sm text-muted-foreground max-w-[34ch]">
                    Talk with a realistic assistant and turn ideas into autonomous runs.
                  </p>
                </div>

                <ThemeToggle />
              </div>

              <div className="mt-5">
                <div className="flex items-center justify-between mb-2">
                  <p className="text-xs font-medium text-muted-foreground">Active bot</p>
                  <button
                    onClick={() => setBotSelectOpen((v) => !v)}
                    className="hidden"
                    aria-hidden="true"
                  />
                </div>

                <Select
                  open={botSelectOpen}
                  onOpenChange={setBotSelectOpen}
                  value={props.selectedBotSlug ?? defaultBotSlug ?? ""}
                  onValueChange={(v) => props.onBotChange?.(v || undefined)}
                >
                  <SelectTrigger
                    className="w-full rounded-xl border-border/70 bg-card/60 backdrop-blur hover:bg-card transition-all shadow-sm focus:ring-4 focus:ring-ring/15"
                    data-testid="bot-selector"
                  >
                    <SelectValue placeholder={bots.isLoading ? "Loading bots..." : "Select a bot"} />
                    <ChevronsUpDown className="h-4 w-4 opacity-60" />
                  </SelectTrigger>
                  <SelectContent className="rounded-xl">
                    {(bots.data ?? []).map((b) => (
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
                      // navigation handled by page via Link list; we just toast
                      toast({ title: "New chat created", description: `#${created.id} ready.` });
                    } catch (e: any) {
                      toast({ title: "Couldn't create chat", description: e?.message ?? "Unknown error", variant: "destructive" });
                    }
                  }}
                  className="flex-1 rounded-xl bg-gradient-to-r from-primary to-accent text-primary-foreground shadow-md shadow-primary/20 hover:shadow-lg hover:shadow-primary/25 hover:-translate-y-0.5 active:translate-y-0 transition-all"
                  data-testid="new-chat"
                  disabled={createConversation.isPending}
                >
                  {createConversation.isPending ? "Creating…" : "New chat"}
                </Button>

                <Button
                  variant="outline"
                  onClick={() => {
                    toast({
                      title: "Quick tip",
                      description:
                        "Use Autonomy to create tasks. Use Bots to tune Buddy’s tone and system prompt.",
                    });
                  }}
                  className="rounded-xl border-border/70 bg-card/60 hover:bg-card shadow-sm hover:shadow-md transition-all"
                  data-testid="quick-tip"
                >
                  <Sparkles className="h-4 w-4" />
                </Button>
              </div>

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
                        "border border-transparent hover:border-border/70 hover:bg-card/60",
                        active
                          ? "bg-gradient-to-r from-primary/14 via-accent/10 to-transparent border-border/70 shadow-sm"
                          : "text-foreground/90"
                      )}
                      data-testid={`nav-${item.label.toLowerCase()}`}
                    >
                      <Icon
                        className={cn(
                          "h-4 w-4 transition-transform duration-300",
                          active ? "text-primary" : "text-muted-foreground group-hover:text-foreground",
                          "group-hover:translate-x-0.5"
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

            <ScrollArea className="h-[280px] border-t border-border/60">
              <div className="p-4 md:p-5 space-y-2">
                {conversations.isLoading ? (
                  <div className="space-y-2">
                    <Skeleton className="h-10 rounded-xl" />
                    <Skeleton className="h-10 rounded-xl" />
                    <Skeleton className="h-10 rounded-xl" />
                  </div>
                ) : conversations.isError ? (
                  <div className="buddy-card p-4 rounded-2xl border border-destructive/30 bg-destructive/5">
                    <p className="text-sm font-medium">Couldn’t load chats</p>
                    <p className="text-sm text-muted-foreground mt-1">
                      {(conversations.error as any)?.message ?? "Unknown error"}
                    </p>
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
                  (conversations.data ?? []).slice(0, 30).map((c) => (
                    <Link
                      key={c.id}
                      href={`/c/${c.id}`}
                      className={cn(
                        "block rounded-xl border border-border/60 bg-card/40 backdrop-blur px-3 py-2.5",
                        "shadow-sm hover:shadow-md hover:bg-card transition-all",
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
                      <p className="text-xs text-muted-foreground mt-1">
                        Created {new Date(c.createdAt as any).toLocaleDateString()}
                      </p>
                    </Link>
                  ))
                )}
              </div>
            </ScrollArea>
          </aside>

          {/* Main content */}
          <main className="min-w-0">{props.children}</main>
        </div>
      </div>
    </div>
  );
}
