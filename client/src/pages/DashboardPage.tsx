import Seo from "@/components/Seo";
import AppShell from "@/components/AppShell";
import { useMemo, useState } from "react";
import { useBots } from "@/hooks/use-bots";
import { useConversations } from "@/hooks/use-conversations";
import { useTasks } from "@/hooks/use-tasks";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { cn } from "@/lib/utils";
import { Activity, Bot, MessageSquareText, Workflow } from "lucide-react";
import { Skeleton } from "@/components/ui/skeleton";

function StatCard(props: {
  icon: React.ReactNode;
  label: string;
  value: string;
  hint?: string;
  accent?: "primary" | "accent" | "muted";
}) {
  const ring =
    props.accent === "accent"
      ? "from-accent/18 via-primary/10"
      : props.accent === "primary"
        ? "from-primary/18 via-accent/10"
        : "from-muted/80 via-muted/50";

  return (
    <Card className={cn("buddy-card buddy-card-hover rounded-3xl p-6 md:p-7 border-border/60")}>
      <div className={cn("h-11 w-11 rounded-2xl bg-gradient-to-br border border-border/60 shadow-sm flex items-center justify-center", ring)}>
        {props.icon}
      </div>
      <p className="mt-4 text-xs font-medium text-muted-foreground">{props.label}</p>
      <p className="mt-1 text-3xl md:text-4xl tracking-tight">{props.value}</p>
      {props.hint ? <p className="mt-2 text-sm text-muted-foreground">{props.hint}</p> : null}
    </Card>
  );
}

export default function DashboardPage() {
  const [botSlug, setBotSlug] = useState<string | undefined>(undefined);
  const bots = useBots();
  const conversations = useConversations();
  const tasks = useTasks();

  const activeTaskCounts = useMemo(() => {
    const list = tasks.data ?? [];
    const byStatus = new Map<string, number>();
    for (const t of list) byStatus.set(t.status, (byStatus.get(t.status) ?? 0) + 1);
    return byStatus;
  }, [tasks.data]);

  return (
    <AppShell selectedBotSlug={botSlug} onBotChange={setBotSlug}>
      <Seo
        title="Buddy — Dashboard"
        description="Overview of conversations, bots, and autonomous tasks."
      />

      <div className="buddy-appear">
        <div className="flex items-end justify-between gap-4 flex-col sm:flex-row">
          <div>
            <h2 className="text-3xl md:text-4xl">Dashboard</h2>
            <p className="mt-2 text-muted-foreground">
              A calm snapshot of what’s happening across chat + autonomy.
            </p>
          </div>
          <div className="flex items-center gap-2">
            <Badge variant="secondary" className="rounded-full px-3 py-1">
              <Activity className="h-3.5 w-3.5 mr-1" />
              Live
            </Badge>
          </div>
        </div>

        <div className="mt-6 grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4 md:gap-5">
          <StatCard
            icon={<MessageSquareText className="h-5 w-5 text-primary" />}
            label="Conversations"
            value={conversations.isLoading ? "—" : String((conversations.data ?? []).length)}
            hint="Chats you’ve started with Buddy."
            accent="primary"
          />
          <StatCard
            icon={<Bot className="h-5 w-5 text-accent" />}
            label="Bot profiles"
            value={bots.isLoading ? "—" : String((bots.data ?? []).length)}
            hint="Personalities and system prompts."
            accent="accent"
          />
          <StatCard
            icon={<Workflow className="h-5 w-5 text-primary" />}
            label="Tasks"
            value={tasks.isLoading ? "—" : String((tasks.data ?? []).length)}
            hint="Objectives you can run repeatedly."
            accent="primary"
          />
          <StatCard
            icon={<Activity className="h-5 w-5 text-accent" />}
            label="Running / pending"
            value={
              tasks.isLoading
                ? "—"
                : String((activeTaskCounts.get("running") ?? 0) + (activeTaskCounts.get("pending") ?? 0))
            }
            hint="What’s queued or in progress."
            accent="accent"
          />
        </div>

        <div className="mt-6 grid grid-cols-1 lg:grid-cols-2 gap-4 md:gap-5">
          <Card className="buddy-card rounded-3xl border-border/60 p-6 md:p-7">
            <h3 className="text-xl md:text-2xl">Task status</h3>
            <p className="mt-1 text-sm text-muted-foreground">
              A simple breakdown to help you focus.
            </p>

            <div className="mt-5 space-y-3">
              {tasks.isLoading ? (
                <div className="space-y-2">
                  <Skeleton className="h-10 rounded-xl" />
                  <Skeleton className="h-10 rounded-xl" />
                  <Skeleton className="h-10 rounded-xl" />
                </div>
              ) : (
                ["pending", "running", "paused", "complete", "failed"].map((s) => (
                  <div
                    key={s}
                    className="flex items-center justify-between rounded-2xl border border-border/60 bg-card/60 px-4 py-3 shadow-sm"
                  >
                    <div className="flex items-center gap-3">
                      <span className={cn("h-2.5 w-2.5 rounded-full",
                        s === "running" ? "bg-[rgb(34_197_94)]" :
                        s === "pending" ? "bg-[rgb(245_158_11)]" :
                        s === "paused" ? "bg-[rgb(59_130_246)]" :
                        s === "complete" ? "bg-[rgb(34_197_94)]" :
                        "bg-[rgb(239_68_68)]"
                      )} />
                      <p className="text-sm font-medium capitalize">{s}</p>
                    </div>
                    <p className="text-sm text-muted-foreground font-mono">
                      {String(activeTaskCounts.get(s) ?? 0)}
                    </p>
                  </div>
                ))
              )}
            </div>
          </Card>

          <Card className="buddy-card rounded-3xl border-border/60 p-6 md:p-7">
            <h3 className="text-xl md:text-2xl">How to use Buddy</h3>
            <p className="mt-1 text-sm text-muted-foreground">
              A lightweight workflow that keeps you moving.
            </p>

            <ol className="mt-5 space-y-3 text-sm">
              {[
                { t: "Start a chat", d: "Describe your income idea or automation you want." },
                { t: "Pick a bot", d: "Switch profiles for different styles and constraints." },
                { t: "Turn it into a task", d: "Capture the objective in Autonomy and run it." },
                { t: "Review runs", d: "Keep the summaries; iterate the prompt." },
              ].map((step, i) => (
                <li
                  key={step.t}
                  className="rounded-2xl border border-border/60 bg-card/60 px-4 py-3 shadow-sm"
                >
                  <div className="flex items-start gap-3">
                    <span className="mt-0.5 inline-flex h-6 w-6 items-center justify-center rounded-full bg-primary/12 text-primary border border-primary/20 font-mono text-xs">
                      {i + 1}
                    </span>
                    <div>
                      <p className="font-semibold">{step.t}</p>
                      <p className="text-muted-foreground mt-1">{step.d}</p>
                    </div>
                  </div>
                </li>
              ))}
            </ol>
          </Card>
        </div>
      </div>
    </AppShell>
  );
}
