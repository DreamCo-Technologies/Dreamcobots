import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Globe, RefreshCw, ExternalLink } from "lucide-react";
import { Button } from "@/components/ui/button";

async function api<T>(path: string, init?: RequestInit): Promise<T> {
  const r = await fetch(`/api${path}`, {
    headers: { "Content-Type": "application/json" },
    ...init,
  });
  if (!r.ok) throw new Error(`${r.status}`);
  return r.json() as Promise<T>;
}

interface Signals {
  models?: number;
  useCases?: number;
  functions?: number;
  classCount?: number;
  providers?: string[];
}
interface Source {
  id: string;
  name: string;
  role: string;
  language: string;
  summary: string | null;
  repoPath: string;
  sizeBytes: number;
  signals: Signals;
}
interface SourcesResponse {
  total: number;
  byRole: Record<string, number>;
  totalModels: number;
  totalUseCases: number;
  sources: Source[];
}

const ROLE_COLORS: Record<string, string> = {
  registry: "text-amber-400 border-amber-400/30",
  router: "text-sky-400 border-sky-400/30",
  flow: "text-fuchsia-400 border-fuchsia-400/30",
  capability: "text-emerald-400 border-emerald-400/30",
  connector: "text-orange-400 border-orange-400/30",
  orchestrator: "text-violet-400 border-violet-400/30",
  benchmark: "text-teal-400 border-teal-400/30",
  module: "text-muted-foreground border-border/40",
};

export default function SourcesPage() {
  const qc = useQueryClient();
  const { data, isLoading } = useQuery<SourcesResponse>({ queryKey: ["sources"], queryFn: () => api("/sources") });

  const reindex = useMutation({
    mutationFn: () => api("/sources/index", { method: "POST", body: JSON.stringify({ limit: 60 }) }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["sources"] }),
  });

  const sources = data?.sources ?? [];

  return (
    <div className="p-6 space-y-6">
      <header className="flex items-start justify-between gap-4 flex-wrap">
        <div className="flex items-center gap-3">
          <Globe className="h-8 w-8 text-primary" />
          <div>
            <h1 className="text-2xl font-mono font-bold tracking-wide">Global_AI_Sources</h1>
            <p className="text-sm text-muted-foreground">
              The AI-infrastructure modules indexed from{" "}
              <span className="font-mono">DreamCo-Technologies/Dreamcobots</span>. Buddy reads this catalog to
              route and reason. <span className="text-emerald-400 font-mono">LIVE</span>
            </p>
          </div>
        </div>
        <Button onClick={() => reindex.mutate()} disabled={reindex.isPending} className="font-mono">
          <RefreshCw className={`h-4 w-4 mr-2 ${reindex.isPending ? "animate-spin" : ""}`} />
          {reindex.isPending ? "Indexing..." : "Re-index Sources"}
        </Button>
      </header>

      <section className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <Stat label="Source Modules" value={data?.total ?? 0} />
        <Stat label="Model Entries" value={data?.totalModels ?? 0} />
        <Stat label="Use-Case Entries" value={data?.totalUseCases ?? 0} />
        <Stat label="Roles" value={Object.keys(data?.byRole ?? {}).length} />
      </section>

      {Object.keys(data?.byRole ?? {}).length > 0 && (
        <div className="flex flex-wrap gap-2">
          {Object.entries(data!.byRole).map(([role, count]) => (
            <span key={role} className={`px-2 py-1 rounded border text-xs font-mono ${ROLE_COLORS[role] ?? ROLE_COLORS.module}`}>
              {role} · {count}
            </span>
          ))}
        </div>
      )}

      {isLoading ? (
        <div className="p-8 text-center text-muted-foreground font-mono text-sm">Loading catalog…</div>
      ) : sources.length === 0 ? (
        <div className="rounded-lg border border-border/40 bg-card p-8 text-center text-muted-foreground font-mono text-sm">
          No sources indexed yet. Hit <span className="text-primary">Re-index Sources</span> to scan the
          Dreamcobots repo for model registries, routers, and the global-ai-sources flow.
        </div>
      ) : (
        <section className="grid gap-3 md:grid-cols-2">
          {sources.map((s) => (
            <div key={s.id} className="rounded-lg border border-border/40 bg-card p-4 space-y-2">
              <div className="flex items-center justify-between gap-2">
                <span className={`px-2 py-0.5 rounded border text-xs font-mono ${ROLE_COLORS[s.role] ?? ROLE_COLORS.module}`}>
                  {s.role}
                </span>
                <a
                  href={`https://github.com/DreamCo-Technologies/Dreamcobots/blob/main/${s.repoPath}`}
                  target="_blank"
                  rel="noreferrer"
                  className="text-muted-foreground hover:text-primary flex items-center gap-1 text-xs font-mono"
                >
                  source <ExternalLink className="h-3 w-3" />
                </a>
              </div>
              <h3 className="font-mono text-sm font-bold">{s.name}</h3>
              <p className="text-xs font-mono text-muted-foreground break-all">{s.repoPath}</p>
              {s.summary && <p className="text-xs text-muted-foreground line-clamp-3">{s.summary}</p>}
              <div className="flex flex-wrap gap-2 pt-1 text-xs font-mono text-muted-foreground">
                {!!s.signals?.models && <span className="text-amber-400">{s.signals.models} models</span>}
                {!!s.signals?.useCases && <span className="text-sky-400">{s.signals.useCases} use-cases</span>}
                {!!s.signals?.functions && <span>{s.signals.functions} fns</span>}
                {!!s.signals?.classCount && <span>{s.signals.classCount} classes</span>}
              </div>
              {s.signals?.providers && s.signals.providers.length > 0 && (
                <div className="flex flex-wrap gap-1">
                  {s.signals.providers.map((p) => (
                    <span key={p} className="px-1.5 py-0.5 rounded bg-muted text-[10px] font-mono">{p}</span>
                  ))}
                </div>
              )}
            </div>
          ))}
        </section>
      )}
    </div>
  );
}

function Stat({ label, value }: { label: string; value: number }) {
  return (
    <div className="rounded-lg border border-border/40 bg-card p-4">
      <div className="text-xs font-mono uppercase text-muted-foreground">{label}</div>
      <div className="mt-1 text-2xl font-mono font-bold text-primary">{value.toLocaleString()}</div>
    </div>
  );
}
