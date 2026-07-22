import { useMemo, useState } from "react";
import Seo from "@/components/Seo";
import AppShell from "@/components/AppShell";
import EmptyState from "@/components/EmptyState";
import ConfirmDialog from "@/components/ConfirmDialog";
import { useToast } from "@/hooks/use-toast";
import { useCreateTask, useDeleteTask, useRunTask, useTaskRuns, useTasks, useUpdateTask } from "@/hooks/use-tasks";
import { useAutonomyMode, useSetAutonomyMode } from "@/hooks/use-empire";
import { TASK_STATUSES, type TaskStatus, type AutonomyMode } from "@shared/schema";
import type { CreateAutonomousTaskRequest, UpdateAutonomousTaskRequest } from "@shared/schema";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Skeleton } from "@/components/ui/skeleton";
import { Textarea } from "@/components/ui/textarea";
import { cn } from "@/lib/utils";
import { CheckCircle2, ClipboardList, Eye, Flame, Play, Plus, RefreshCcw, Shield, Trash2, Zap } from "lucide-react";

const AUTONOMY_OPTIONS: Array<{
  mode: AutonomyMode;
  label: string;
  sublabel: string;
  description: string;
  icon: typeof Zap;
  color: string;
  ring: string;
  bg: string;
  permissions: string[];
  autoRuns: string[];
}> = [
  {
    mode: "guided",
    label: "No AI",
    sublabel: "Manual / Human-first",
    description: "You approve every action before it runs. Best for high-stakes or sensitive workflows where you want full review.",
    icon: Eye,
    color: "text-sky-500",
    ring: "ring-sky-500/40",
    bg: "bg-sky-500/10",
    permissions: ["Every task requires your approval", "All bot responses reviewed by you", "No auto-runs ever", "Full audit trail"],
    autoRuns: [],
  },
  {
    mode: "semi-autonomous",
    label: "Semi-Auto",
    sublabel: "Balanced — low risk auto, you approve high risk",
    description: "Routine, low-risk tasks run automatically. High-risk actions (payments, emails, API calls) pause for your approval.",
    icon: Shield,
    color: "text-amber-500",
    ring: "ring-amber-500/40",
    bg: "bg-amber-500/10",
    permissions: ["High-risk actions pause for approval", "New payment/send actions reviewed", "You can override any decision"],
    autoRuns: ["Research & analysis", "Report generation", "Draft creation", "Data processing", "Score calculations"],
  },
  {
    mode: "full-autonomy",
    label: "Full Auto",
    sublabel: "Maximum throughput with protected actions gated",
    description: "Routine sandbox and approved workflows run continuously. Money, publishing, outreach, account, deployment, and sensitive-data actions still require scoped owner approval.",
    icon: Zap,
    color: "text-green-500",
    ring: "ring-green-500/40",
    bg: "bg-green-500/10",
    permissions: ["Protected actions always pause", "Bots self-coordinate in approved scopes", "Every live action remains auditable"],
    autoRuns: ["Research and analysis", "Sandbox tests", "Drafts and simulations", "Bot-to-bot delegation", "Local maintenance"],
  },
];

function priorityLabel(p: number) {
  if (p >= 5) return "Critical";
  if (p === 4) return "High";
  if (p === 3) return "Normal";
  if (p === 2) return "Low";
  return "Very low";
}

export default function AutonomyPage() {
  const { toast } = useToast();
  const tasks = useTasks();
  const createTask = useCreateTask();
  const updateTask = useUpdateTask();
  const delTask = useDeleteTask();
  const runTask = useRunTask();
  const autonomyQuery = useAutonomyMode();
  const setAutonomy = useSetAutonomyMode();

  const currentMode: AutonomyMode = (autonomyQuery.data?.mode as AutonomyMode) ?? "guided";

  const [activeBotSlug, setActiveBotSlug] = useState<string | undefined>(undefined);

  const [createOpen, setCreateOpen] = useState(false);
  const [selectedTaskId, setSelectedTaskId] = useState<number | null>(null);

  const runs = useTaskRuns(selectedTaskId ?? undefined);

  const [deleteOpen, setDeleteOpen] = useState(false);

  const selectedTask = useMemo(
    () => (tasks.data ?? []).find((t) => t.id === selectedTaskId) ?? null,
    [tasks.data, selectedTaskId]
  );

  const [createForm, setCreateForm] = useState<CreateAutonomousTaskRequest>({
    title: "Prospecting bot",
    objective: "Find 20 leads for a niche, draft outreach messages, and summarize next steps.",
    status: "pending" as any,
    priority: 3 as any,
  } as any);

  const [editOpen, setEditOpen] = useState(false);
  const [editForm, setEditForm] = useState<UpdateAutonomousTaskRequest>({});

  const sortedTasks = useMemo(() => {
    const list = [...(tasks.data ?? [])];
    list.sort((a, b) => {
      const pa = (a.priority as any) ?? 3;
      const pb = (b.priority as any) ?? 3;
      if (pb !== pa) return pb - pa;
      return (b.id ?? 0) - (a.id ?? 0);
    });
    return list;
  }, [tasks.data]);

  return (
    <AppShell selectedBotSlug={activeBotSlug} onBotChange={setActiveBotSlug}>
      <Seo title="DreamCo Empire OS — Autonomy" description="Create autonomous tasks, run them, and review recent runs." />

      <ConfirmDialog
        open={deleteOpen}
        onOpenChange={setDeleteOpen}
        title="Delete task?"
        description="This removes the task and its run history."
        confirmLabel={delTask.isPending ? "Deleting…" : "Delete"}
        destructive
        onConfirm={async () => {
          if (!selectedTaskId) return;
          try {
            await delTask.mutateAsync(selectedTaskId);
            toast({ title: "Task deleted" });
            setSelectedTaskId(null);
            setDeleteOpen(false);
          } catch (e: any) {
            toast({ title: "Delete failed", description: e?.message ?? "Unknown error", variant: "destructive" });
          }
        }}
        data-testid="delete-task-dialog"
      />

      <div className="buddy-appear space-y-6">

        {/* ── GLOBAL MODE SELECTOR ── */}
        <div>
          <div className="mb-4">
            <h2 className="text-3xl md:text-4xl">Autonomy</h2>
            <p className="mt-2 text-muted-foreground">
              Set your global AI permission level once — bots will follow it on every task automatically.
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            {AUTONOMY_OPTIONS.map((opt) => {
              const Icon = opt.icon;
              const isActive = currentMode === opt.mode;
              return (
                <button
                  key={opt.mode}
                  onClick={async () => {
                    try {
                      await setAutonomy.mutateAsync(opt.mode);
                      toast({ title: `Mode set: ${opt.label}`, description: opt.sublabel });
                    } catch {
                      toast({ title: "Failed to update mode", variant: "destructive" });
                    }
                  }}
                  disabled={setAutonomy.isPending}
                  data-testid={`autonomy-option-${opt.mode}`}
                  className={cn(
                    "w-full text-left rounded-2xl border p-5 transition-all hover:-translate-y-0.5 hover:shadow-lg",
                    isActive
                      ? `${opt.bg} border-transparent ring-2 ${opt.ring} shadow-md`
                      : "bg-card/60 border-border/60 hover:bg-card"
                  )}
                >
                  <div className="flex items-center justify-between mb-3">
                    <div className={cn("h-11 w-11 rounded-xl flex items-center justify-center", opt.bg)}>
                      <Icon className={cn("h-6 w-6", opt.color)} />
                    </div>
                    {isActive && (
                      <Badge className={cn("rounded-full text-xs", opt.bg, opt.color, "border-0")}>
                        <CheckCircle2 className="h-3 w-3 mr-1" />Active
                      </Badge>
                    )}
                  </div>
                  <p className="font-bold text-lg leading-tight">{opt.label}</p>
                  <p className={cn("text-xs font-medium mt-0.5", opt.color)}>{opt.sublabel}</p>
                  <p className="text-xs text-muted-foreground mt-2 leading-relaxed">{opt.description}</p>
                  <div className="mt-3 space-y-1">
                    {opt.permissions.map(p => (
                      <p key={p} className="text-xs text-muted-foreground flex items-start gap-1.5">
                        <span className={cn("mt-0.5 flex-shrink-0", opt.color)}>•</span>{p}
                      </p>
                    ))}
                    {opt.autoRuns.length > 0 && (
                      <p className="text-xs text-muted-foreground flex items-start gap-1.5 mt-2">
                        <Zap className={cn("h-3 w-3 mt-0.5 flex-shrink-0", opt.color)} />
                        <span>Auto-runs: {opt.autoRuns.join(", ")}</span>
                      </p>
                    )}
                  </div>
                </button>
              );
            })}
          </div>
        </div>

        <div className="flex flex-col md:flex-row md:items-end md:justify-between gap-4">
          <div>
            <h3 className="text-2xl md:text-3xl">Task Queue</h3>
            <p className="mt-1 text-sm text-muted-foreground">
              Capture repeatable objectives, then run them like a disciplined operator.
            </p>
          </div>

          <div className="flex gap-2">
            <Button
              variant="outline"
              className="rounded-xl border-border/70 bg-card/60 hover:bg-card shadow-sm hover:shadow-md transition-all"
              onClick={() => tasks.refetch()}
              data-testid="refresh-tasks"
            >
              <RefreshCcw className="h-4 w-4 mr-2" />
              Refresh
            </Button>

            <Dialog open={createOpen} onOpenChange={setCreateOpen}>
              <DialogTrigger asChild>
                <Button
                  onClick={() => {
                    setCreateForm({
                      title: "Revenue experiment",
                      objective:
                        "Design one simple autonomous workflow that produces measurable leads in 7 days. Include KPIs and risk checks.",
                      status: "pending" as any,
                      priority: 3 as any,
                    } as any);
                  }}
                  className="rounded-xl bg-gradient-to-r from-primary to-accent text-primary-foreground shadow-md shadow-primary/20 hover:shadow-lg hover:shadow-primary/25 hover:-translate-y-0.5 active:translate-y-0 transition-all"
                  data-testid="open-create-task"
                >
                  <Plus className="h-4 w-4 mr-2" />
                  New task
                </Button>
              </DialogTrigger>

              <DialogContent className="rounded-2xl">
                <DialogHeader>
                  <DialogTitle>Create autonomous task</DialogTitle>
                </DialogHeader>

                <div className="grid gap-4">
                  <div className="grid gap-2">
                    <p className="text-sm font-medium">Title</p>
                    <Input
                      value={(createForm as any).title ?? ""}
                      onChange={(e) => setCreateForm((p) => ({ ...(p as any), title: e.target.value }))}
                      className="rounded-xl"
                      data-testid="create-task-title"
                    />
                  </div>

                  <div className="grid gap-2">
                    <p className="text-sm font-medium">Objective</p>
                    <Textarea
                      value={(createForm as any).objective ?? ""}
                      onChange={(e) => setCreateForm((p) => ({ ...(p as any), objective: e.target.value }))}
                      className="rounded-2xl min-h-[160px]"
                      data-testid="create-task-objective"
                    />
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    <div className="grid gap-2">
                      <p className="text-sm font-medium">Status</p>
                      <Select
                        value={String((createForm as any).status ?? "pending")}
                        onValueChange={(v) => setCreateForm((p) => ({ ...(p as any), status: v }))}
                      >
                        <SelectTrigger className="rounded-xl" data-testid="create-task-status">
                          <SelectValue placeholder="Select status" />
                        </SelectTrigger>
                        <SelectContent className="rounded-xl">
                          {TASK_STATUSES.map((s) => (
                            <SelectItem key={s} value={s} className="rounded-lg capitalize">
                              {s}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>

                    <div className="grid gap-2">
                      <p className="text-sm font-medium">Priority (1–5)</p>
                      <Select
                        value={String((createForm as any).priority ?? 3)}
                        onValueChange={(v) => setCreateForm((p) => ({ ...(p as any), priority: Number(v) }))}
                      >
                        <SelectTrigger className="rounded-xl" data-testid="create-task-priority">
                          <SelectValue placeholder="Select priority" />
                        </SelectTrigger>
                        <SelectContent className="rounded-xl">
                          {[1, 2, 3, 4, 5].map((p) => (
                            <SelectItem key={p} value={String(p)} className="rounded-lg">
                              {p} — {priorityLabel(p)}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                  </div>

                  <Button
                    onClick={async () => {
                      try {
                        const created = await createTask.mutateAsync(createForm);
                        toast({ title: "Task created", description: `#${created.id} ready.` });
                        setCreateOpen(false);
                        setSelectedTaskId(created.id);
                      } catch (e: any) {
                        toast({ title: "Create failed", description: e?.message ?? "Unknown error", variant: "destructive" });
                      }
                    }}
                    disabled={createTask.isPending}
                    className="rounded-xl bg-gradient-to-r from-primary to-accent text-primary-foreground shadow-md shadow-primary/20 hover:shadow-lg hover:shadow-primary/25 hover:-translate-y-0.5 active:translate-y-0 transition-all"
                    data-testid="create-task-submit"
                  >
                    {createTask.isPending ? "Creating…" : "Create task"}
                  </Button>
                </div>
              </DialogContent>
            </Dialog>
          </div>
        </div>

        <div className="mt-6 grid grid-cols-1 lg:grid-cols-[420px_1fr] gap-4 md:gap-5">
          <Card className="buddy-card rounded-3xl border-border/60 overflow-hidden">
            <div className="p-5 md:p-6 border-b border-border/60">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs font-medium text-muted-foreground">Tasks</p>
                  <h3 className="text-xl md:text-2xl mt-1">Your queue</h3>
                </div>
                <Badge variant="secondary" className="rounded-full">
                  {(tasks.data ?? []).length} total
                </Badge>
              </div>
            </div>

            <div className="p-4 md:p-5 space-y-2">
              {tasks.isLoading ? (
                <div className="space-y-2">
                  <Skeleton className="h-14 rounded-2xl" />
                  <Skeleton className="h-14 rounded-2xl" />
                  <Skeleton className="h-14 rounded-2xl" />
                </div>
              ) : tasks.isError ? (
                <EmptyState
                  icon={<ClipboardList className="h-6 w-6" />}
                  title="Couldn’t load tasks"
                  description={(tasks.error as any)?.message ?? "Unknown error"}
                  action={
                    <Button onClick={() => tasks.refetch()} className="rounded-xl" data-testid="retry-tasks">
                      Retry
                    </Button>
                  }
                />
              ) : sortedTasks.length === 0 ? (
                <EmptyState
                  icon={<ClipboardList className="h-6 w-6" />}
                  title="No tasks yet"
                  description="Create a task to turn a recurring workflow into something runnable."
                  action={
                    <Button onClick={() => setCreateOpen(true)} className="rounded-xl" data-testid="empty-create-task">
                      Create task
                    </Button>
                  }
                />
              ) : (
                sortedTasks.map((t) => {
                  const active = selectedTaskId === t.id;
                  return (
                    <button
                      key={t.id}
                      onClick={() => setSelectedTaskId(t.id)}
                      className={cn(
                        "w-full text-left rounded-2xl border px-4 py-3 shadow-sm transition-all",
                        "hover:shadow-md hover:-translate-y-0.5 active:translate-y-0",
                        active
                          ? "bg-gradient-to-r from-primary/14 via-accent/10 to-transparent border-border/70 ring-2 ring-ring/15"
                          : "bg-card/60 border-border/60"
                      )}
                      data-testid={`task-item-${t.id}`}
                    >
                      <div className="flex items-start justify-between gap-3">
                        <div className="min-w-0">
                          <p className="font-semibold truncate">{t.title}</p>
                          <p className="text-xs text-muted-foreground mt-1 line-clamp-2">
                            {t.objective}
                          </p>
                        </div>
                        <div className="shrink-0 flex flex-col items-end gap-2">
                          <Badge
                            variant="outline"
                            className="rounded-full border-border/70 capitalize"
                          >
                            {t.status}
                          </Badge>
                          <Badge
                            className={cn(
                              "rounded-full",
                              (t.priority as any) >= 4
                                ? "bg-destructive/10 text-destructive border border-destructive/20"
                                : "bg-primary/10 text-primary border border-primary/20"
                            )}
                          >
                            <Flame className="h-3.5 w-3.5 mr-1" />
                            P{t.priority}
                          </Badge>
                        </div>
                      </div>
                    </button>
                  );
                })
              )}
            </div>
          </Card>

          <div className="space-y-4 md:space-y-5 min-w-0">
            {!selectedTask ? (
              <EmptyState
                icon={<Play className="h-6 w-6" />}
                title="Select a task"
                description="Pick a task on the left to run it and review history."
                data-testid="no-task-selected"
              />
            ) : (
              <>
                <Card className="buddy-card rounded-3xl border-border/60 p-6 md:p-7">
                  <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-4">
                    <div className="min-w-0">
                      <div className="flex items-center gap-2 flex-wrap">
                        <h3 className="text-2xl md:text-3xl truncate">{selectedTask.title}</h3>
                        <Badge variant="secondary" className="rounded-full font-mono">
                          #{selectedTask.id}
                        </Badge>
                        <Badge variant="outline" className="rounded-full capitalize">
                          {selectedTask.status}
                        </Badge>
                      </div>
                      <p className="mt-3 text-sm md:text-base text-muted-foreground whitespace-pre-wrap">
                        {selectedTask.objective}
                      </p>

                      <div className="mt-4 flex flex-wrap gap-2">
                        <Badge className="rounded-full bg-primary/10 text-primary border border-primary/20">
                          Priority {selectedTask.priority} — {priorityLabel(selectedTask.priority as any)}
                        </Badge>
                        {selectedTask.lastRunAt ? (
                          <Badge variant="outline" className="rounded-full border-border/70">
                            Last run: {new Date(selectedTask.lastRunAt as any).toLocaleString()}
                          </Badge>
                        ) : (
                          <Badge variant="outline" className="rounded-full border-border/70">
                            Never run
                          </Badge>
                        )}
                      </div>
                    </div>

                    <div className="flex flex-col sm:flex-row md:flex-col gap-2">
                      <Button
                        onClick={async () => {
                          try {
                            await runTask.mutateAsync({ id: selectedTask.id, dryRun: false });
                            toast({ title: "Task started", description: "A run record was created." });
                            await runs.refetch();
                            await tasks.refetch();
                          } catch (e: any) {
                            toast({ title: "Run failed", description: e?.message ?? "Unknown error", variant: "destructive" });
                          }
                        }}
                        disabled={runTask.isPending}
                        className="rounded-xl bg-gradient-to-r from-primary to-accent text-primary-foreground shadow-md shadow-primary/20 hover:shadow-lg hover:shadow-primary/25 hover:-translate-y-0.5 active:translate-y-0 transition-all"
                        data-testid="run-task"
                      >
                        <Play className="h-4 w-4 mr-2" />
                        {runTask.isPending ? "Running…" : "Run task"}
                      </Button>

                      <Button
                        variant="outline"
                        onClick={() => {
                          setEditForm({
                            title: selectedTask.title,
                            objective: selectedTask.objective,
                            status: selectedTask.status as any,
                            priority: selectedTask.priority as any,
                          });
                          setEditOpen(true);
                        }}
                        className="rounded-xl border-border/70 bg-card/60 hover:bg-card shadow-sm hover:shadow-md transition-all"
                        data-testid="edit-task"
                      >
                        Edit
                      </Button>

                      <Button
                        variant="outline"
                        onClick={() => setDeleteOpen(true)}
                        className="rounded-xl border-destructive/30 bg-destructive/5 hover:bg-destructive/10 text-destructive shadow-sm hover:shadow-md transition-all"
                        data-testid="delete-task"
                      >
                        <Trash2 className="h-4 w-4 mr-2" />
                        Delete
                      </Button>
                    </div>
                  </div>
                </Card>

                <Dialog open={editOpen} onOpenChange={setEditOpen}>
                  <DialogContent className="rounded-2xl">
                    <DialogHeader>
                      <DialogTitle>Edit task</DialogTitle>
                    </DialogHeader>

                    <div className="grid gap-4">
                      <div className="grid gap-2">
                        <p className="text-sm font-medium">Title</p>
                        <Input
                          value={(editForm as any).title ?? ""}
                          onChange={(e) => setEditForm((p) => ({ ...(p as any), title: e.target.value }))}
                          className="rounded-xl"
                          data-testid="edit-task-title"
                        />
                      </div>

                      <div className="grid gap-2">
                        <p className="text-sm font-medium">Objective</p>
                        <Textarea
                          value={(editForm as any).objective ?? ""}
                          onChange={(e) => setEditForm((p) => ({ ...(p as any), objective: e.target.value }))}
                          className="rounded-2xl min-h-[160px]"
                          data-testid="edit-task-objective"
                        />
                      </div>

                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                        <div className="grid gap-2">
                          <p className="text-sm font-medium">Status</p>
                          <Select
                            value={String((editForm as any).status ?? selectedTask.status)}
                            onValueChange={(v) => setEditForm((p) => ({ ...(p as any), status: v as TaskStatus }))}
                          >
                            <SelectTrigger className="rounded-xl" data-testid="edit-task-status">
                              <SelectValue placeholder="Select status" />
                            </SelectTrigger>
                            <SelectContent className="rounded-xl">
                              {TASK_STATUSES.map((s) => (
                                <SelectItem key={s} value={s} className="rounded-lg capitalize">
                                  {s}
                                </SelectItem>
                              ))}
                            </SelectContent>
                          </Select>
                        </div>

                        <div className="grid gap-2">
                          <p className="text-sm font-medium">Priority</p>
                          <Select
                            value={String((editForm as any).priority ?? selectedTask.priority)}
                            onValueChange={(v) => setEditForm((p) => ({ ...(p as any), priority: Number(v) }))}
                          >
                            <SelectTrigger className="rounded-xl" data-testid="edit-task-priority">
                              <SelectValue placeholder="Select priority" />
                            </SelectTrigger>
                            <SelectContent className="rounded-xl">
                              {[1, 2, 3, 4, 5].map((p) => (
                                <SelectItem key={p} value={String(p)} className="rounded-lg">
                                  {p} — {priorityLabel(p)}
                                </SelectItem>
                              ))}
                            </SelectContent>
                          </Select>
                        </div>
                      </div>

                      <Button
                        onClick={async () => {
                          try {
                            await updateTask.mutateAsync({ id: selectedTask.id, updates: editForm });
                            toast({ title: "Task updated" });
                            setEditOpen(false);
                          } catch (e: any) {
                            toast({ title: "Update failed", description: e?.message ?? "Unknown error", variant: "destructive" });
                          }
                        }}
                        disabled={updateTask.isPending}
                        className="rounded-xl bg-gradient-to-r from-primary to-accent text-primary-foreground shadow-md shadow-primary/20 hover:shadow-lg hover:shadow-primary/25 hover:-translate-y-0.5 active:translate-y-0 transition-all"
                        data-testid="edit-task-submit"
                      >
                        {updateTask.isPending ? "Saving…" : "Save changes"}
                      </Button>
                    </div>
                  </DialogContent>
                </Dialog>

                <Card className="buddy-card rounded-3xl border-border/60 overflow-hidden">
                  <div className="p-5 md:p-6 border-b border-border/60 flex items-center justify-between gap-3">
                    <div>
                      <p className="text-xs font-medium text-muted-foreground">Runs</p>
                      <h3 className="text-xl md:text-2xl mt-1">Recent history</h3>
                    </div>
                    <Badge variant="secondary" className="rounded-full">
                      {(runs.data ?? []).length || 0}
                    </Badge>
                  </div>

                  <div className="p-4 md:p-5 space-y-3">
                    {runs.isLoading ? (
                      <div className="space-y-2">
                        <Skeleton className="h-16 rounded-2xl" />
                        <Skeleton className="h-16 rounded-2xl" />
                        <Skeleton className="h-16 rounded-2xl" />
                      </div>
                    ) : runs.data === null ? (
                      <EmptyState
                        icon={<ClipboardList className="h-6 w-6" />}
                        title="No runs found"
                        description="This task might have been removed, or runs aren’t available."
                      />
                    ) : (runs.data ?? []).length === 0 ? (
                      <EmptyState
                        icon={<Play className="h-6 w-6" />}
                        title="No runs yet"
                        description="Run this task to create the first run record."
                      />
                    ) : (
                      <div className="space-y-3">
                        {(runs.data ?? []).slice(0, 12).map((r) => (
                          <div
                            key={r.id}
                            className="rounded-2xl border border-border/60 bg-card/60 shadow-sm p-4"
                            data-testid={`task-run-${r.id}`}
                          >
                            <div className="flex items-start justify-between gap-3">
                              <div className="min-w-0">
                                <p className="text-sm font-semibold capitalize">{r.status}</p>
                                <p className="text-xs text-muted-foreground mt-1">
                                  {new Date(r.createdAt as any).toLocaleString()}
                                </p>
                              </div>
                              <Badge variant="outline" className="rounded-full font-mono border-border/70">
                                run#{r.id}
                              </Badge>
                            </div>
                            {r.summary ? (
                              <p className="mt-3 text-sm text-muted-foreground whitespace-pre-wrap">
                                {r.summary}
                              </p>
                            ) : null}
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </Card>
              </>
            )}
          </div>
        </div>
      </div>
    </AppShell>
  );
}
