import { useQuery } from "@tanstack/react-query";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { GraduationCap, Lightbulb, BookOpen, Hammer } from "lucide-react";

interface VibeStats { librariesLearned: number; ideasGenerated: number; buildsCompleted: number; avgImpactScore: number; ecosystems: { ecosystem: string; n: number }[] }
interface Idea { id: string; title?: string; summary?: string; impactScore?: number }

async function api<T = unknown>(path: string): Promise<T> {
  const r = await fetch(`/api${path}`, { headers: { "Content-Type": "application/json" } });
  if (!r.ok) throw new Error(`${r.status}: ${await r.text()}`);
  return r.json();
}

export default function LearningMatrixPage() {
  const stats = useQuery<VibeStats>({ queryKey: ["vstats"], queryFn: () => api("/vibe/stats"), refetchInterval: 10000 });
  const ideas = useQuery<Idea[]>({ queryKey: ["ideas"], queryFn: () => api("/vibe/ideas") });

  const s = stats.data;
  const metrics = [
    { label: "Libraries Learned", value: s?.librariesLearned ?? 0, icon: BookOpen },
    { label: "Ideas Generated", value: s?.ideasGenerated ?? 0, icon: Lightbulb },
    { label: "Builds Completed", value: s?.buildsCompleted ?? 0, icon: Hammer },
    { label: "Avg Impact", value: s ? `${Math.round((s.avgImpactScore || 0) * 100)}%` : "0%", icon: GraduationCap },
  ];

  return (
    <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="flex flex-col gap-2">
        <h1 className="text-3xl font-mono font-bold tracking-tight text-foreground uppercase flex items-center gap-3">
          <GraduationCap className="h-8 w-8 text-primary" />Learning_Matrix
        </h1>
        <p className="text-muted-foreground font-mono text-sm uppercase tracking-wider">What the fleet is learning · live from Vibe Engine</p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {stats.isLoading ? [0, 1, 2, 3].map((i) => <Skeleton key={i} className="h-24" />) : metrics.map((m) => (
          <Card key={m.label} className="p-4 border-border/40 bg-card/50 backdrop-blur">
            <div className="flex items-center gap-2 font-mono text-xs text-muted-foreground uppercase"><m.icon className="h-4 w-4 text-primary/70" />{m.label}</div>
            <div className="text-3xl font-mono font-bold text-foreground mt-1">{m.value}</div>
          </Card>
        ))}
      </div>

      <div className="space-y-2">
        <div className="font-mono text-xs uppercase tracking-wider text-primary">// generated ideas</div>
        {ideas.isLoading ? (
          <Skeleton className="h-40" />
        ) : (ideas.data || []).length === 0 ? (
          <Card className="p-6 border-border/40 font-mono text-sm text-muted-foreground">No ideas generated yet. Run the Vibe Engine sweep to generate build ideas from learned libraries.</Card>
        ) : (
          <div className="grid gap-3 md:grid-cols-2">
            {ideas.data!.map((idea, i) => (
              <Card key={idea.id || i} className="p-4 border-border/40 bg-card/50 backdrop-blur">
                <div className="flex items-center justify-between mb-1">
                  <div className="font-mono text-sm font-bold text-foreground">{idea.title || `Idea #${i + 1}`}</div>
                  {typeof idea.impactScore === "number" ? <Badge variant="outline" className="font-mono text-[10px]">{Math.round(idea.impactScore * 100)}%</Badge> : null}
                </div>
                {idea.summary ? <p className="font-mono text-xs text-muted-foreground line-clamp-3">{idea.summary}</p> : null}
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
