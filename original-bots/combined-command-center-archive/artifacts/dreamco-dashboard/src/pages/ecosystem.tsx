import { useQuery } from "@tanstack/react-query";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Globe, BookOpen } from "lucide-react";

interface Library { id: string; name: string; ecosystem: string; summary: string }
interface VibeStats { librariesLearned: number; ideasGenerated: number; buildsCompleted: number; avgImpactScore: number; ecosystems: { ecosystem: string; n: number }[] }

async function api<T = unknown>(path: string): Promise<T> {
  const r = await fetch(`/api${path}`, { headers: { "Content-Type": "application/json" } });
  if (!r.ok) throw new Error(`${r.status}: ${await r.text()}`);
  return r.json();
}

export default function EcosystemPage() {
  const stats = useQuery<VibeStats>({ queryKey: ["vstats"], queryFn: () => api("/vibe/stats"), refetchInterval: 10000 });
  const libs = useQuery<Library[]>({ queryKey: ["libs"], queryFn: () => api("/vibe/libraries") });

  const grouped = (libs.data || []).reduce<Record<string, Library[]>>((acc, l) => {
    (acc[l.ecosystem] ||= []).push(l);
    return acc;
  }, {});

  return (
    <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="flex flex-col gap-2">
        <h1 className="text-3xl font-mono font-bold tracking-tight text-foreground uppercase flex items-center gap-3">
          <Globe className="h-8 w-8 text-primary" />AI_Ecosystem
        </h1>
        <p className="text-muted-foreground font-mono text-sm uppercase tracking-wider">Libraries the fleet has learned · live</p>
      </div>

      <div className="grid gap-4 sm:grid-cols-3">
        {stats.isLoading ? [0, 1, 2].map((i) => <Skeleton key={i} className="h-24" />) : (
          <>
            <Card className="p-4 border-border/40 bg-card/50"><div className="font-mono text-xs text-muted-foreground uppercase">Libraries</div><div className="text-3xl font-mono font-bold text-foreground">{stats.data?.librariesLearned ?? 0}</div></Card>
            <Card className="p-4 border-border/40 bg-card/50"><div className="font-mono text-xs text-muted-foreground uppercase">Ideas</div><div className="text-3xl font-mono font-bold text-foreground">{stats.data?.ideasGenerated ?? 0}</div></Card>
            <Card className="p-4 border-border/40 bg-card/50"><div className="font-mono text-xs text-muted-foreground uppercase">Ecosystems</div><div className="text-3xl font-mono font-bold text-foreground">{stats.data?.ecosystems.length ?? 0}</div></Card>
          </>
        )}
      </div>

      {libs.isLoading ? (
        <Skeleton className="h-48" />
      ) : Object.keys(grouped).length === 0 ? (
        <Card className="p-6 border-border/40 font-mono text-sm text-muted-foreground">No libraries learned yet. Use the Vibe Engine's "learn" action to index one.</Card>
      ) : (
        Object.entries(grouped).map(([eco, items]) => (
          <div key={eco} className="space-y-2">
            <div className="font-mono text-xs uppercase tracking-wider text-primary flex items-center gap-2">
              <Badge variant="outline" className="font-mono text-[10px]">{eco}</Badge>
              <span className="text-muted-foreground">{items.length} libraries</span>
            </div>
            <div className="grid gap-3 md:grid-cols-2">
              {items.map((l) => (
                <Card key={l.id} className="p-4 border-border/40 bg-card/50 backdrop-blur">
                  <div className="flex items-center gap-2 mb-1 font-mono text-sm font-bold text-foreground"><BookOpen className="h-4 w-4 text-primary/70" />{l.name}</div>
                  <p className="font-mono text-xs text-muted-foreground line-clamp-3">{l.summary}</p>
                </Card>
              ))}
            </div>
          </div>
        ))
      )}
    </div>
  );
}
