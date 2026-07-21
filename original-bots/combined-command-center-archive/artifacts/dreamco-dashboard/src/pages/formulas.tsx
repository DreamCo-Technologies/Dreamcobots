import { useQuery } from "@tanstack/react-query";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { FlaskConical, BookOpen } from "lucide-react";

interface Library { id: string; name: string; ecosystem: string; summary: string }

async function api<T = unknown>(path: string): Promise<T> {
  const r = await fetch(`/api${path}`, { headers: { "Content-Type": "application/json" } });
  if (!r.ok) throw new Error(`${r.status}: ${await r.text()}`);
  return r.json();
}

export default function FormulasPage() {
  const libs = useQuery<Library[]>({ queryKey: ["libs"], queryFn: () => api("/vibe/libraries") });

  return (
    <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="flex flex-col gap-2">
        <h1 className="text-3xl font-mono font-bold tracking-tight text-foreground uppercase flex items-center gap-3">
          <FlaskConical className="h-8 w-8 text-primary" />Formula_Vault
        </h1>
        <p className="text-muted-foreground font-mono text-sm uppercase tracking-wider">Learned library knowledge · reusable building blocks</p>
      </div>

      {libs.isLoading ? (
        <div className="grid gap-3 md:grid-cols-2">{[0, 1, 2, 3].map((i) => <Skeleton key={i} className="h-32" />)}</div>
      ) : libs.isError ? (
        <Card className="p-6 border-destructive/40 font-mono text-sm text-destructive">Failed to load.</Card>
      ) : libs.data!.length === 0 ? (
        <Card className="p-6 border-border/40 font-mono text-sm text-muted-foreground">
          The vault is empty. Use the Vibe Engine's "learn" action to add a library — each one becomes a reusable formula here.
        </Card>
      ) : (
        <div className="grid gap-3 md:grid-cols-2">
          {libs.data!.map((l) => (
            <Card key={l.id} className="p-4 border-border/40 bg-card/50 backdrop-blur">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2 font-mono text-sm font-bold text-foreground"><BookOpen className="h-4 w-4 text-primary/70" />{l.name}</div>
                <Badge variant="outline" className="font-mono text-[10px]">{l.ecosystem}</Badge>
              </div>
              <p className="font-mono text-xs text-muted-foreground line-clamp-4">{l.summary}</p>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
