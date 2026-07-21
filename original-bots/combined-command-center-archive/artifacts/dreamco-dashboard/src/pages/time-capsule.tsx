import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { History, Camera, TrendingUp, TrendingDown, Minus } from "lucide-react";
import { Button } from "@/components/ui/button";

async function api<T>(path: string, init?: RequestInit): Promise<T> {
  const r = await fetch(`/api${path}`, {
    headers: { "Content-Type": "application/json" },
    ...init,
  });
  if (!r.ok) throw new Error(`${r.status}`);
  return r.json() as Promise<T>;
}

type Metrics = Record<string, number>;
interface Snapshot {
  id: string;
  capturedAt: string;
  metrics: Metrics;
  meta: Record<string, unknown> | null;
}

const METRIC_LABELS: Record<string, string> = {
  agents: "Indexed Bots",
  activeAgents: "Active Bots",
  aiSources: "AI Sources",
  totalInvocations: "Total Runs",
  revenueGenerated: "Revenue Tracked ($)",
};

function fmt(n: number): string {
  return Number.isInteger(n) ? n.toLocaleString() : n.toFixed(2);
}

function Delta({ curr, prev }: { curr: number; prev: number | undefined }) {
  if (prev === undefined || prev === curr) return <Minus className="h-3 w-3 text-muted-foreground" />;
  const up = curr > prev;
  const Icon = up ? TrendingUp : TrendingDown;
  return (
    <span className={`flex items-center gap-1 text-xs font-mono ${up ? "text-emerald-400" : "text-red-400"}`}>
      <Icon className="h-3 w-3" />
      {up ? "+" : ""}{fmt(curr - prev)}
    </span>
  );
}

export default function TimeCapsulePage() {
  const qc = useQueryClient();
  const live = useQuery<Metrics>({ queryKey: ["snap-live"], queryFn: () => api("/snapshots/live"), refetchInterval: 30000 });
  const history = useQuery<Snapshot[]>({ queryKey: ["snap-history"], queryFn: () => api("/snapshots?limit=90") });

  const capture = useMutation({
    mutationFn: () => api<Snapshot>("/snapshots", { method: "POST", body: JSON.stringify({ note: "manual" }) }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["snap-history"] }),
  });

  const keys = Object.keys(METRIC_LABELS);
  const snaps = history.data ?? [];

  return (
    <div className="p-6 space-y-6">
      <header className="flex items-start justify-between gap-4 flex-wrap">
        <div className="flex items-center gap-3">
          <History className="h-8 w-8 text-primary" />
          <div>
            <h1 className="text-2xl font-mono font-bold tracking-wide">Time_Capsule</h1>
            <p className="text-sm text-muted-foreground">
              Real, DB-derived empire snapshots over time.{" "}
              <span className="text-emerald-400 font-mono">LIVE</span>
            </p>
          </div>
        </div>
        <Button onClick={() => capture.mutate()} disabled={capture.isPending} className="font-mono">
          <Camera className="h-4 w-4 mr-2" />
          {capture.isPending ? "Capturing..." : "Capture Snapshot"}
        </Button>
      </header>

      <section className="grid grid-cols-2 md:grid-cols-5 gap-3">
        {keys.map((k) => (
          <div key={k} className="rounded-lg border border-border/40 bg-card p-4">
            <div className="text-xs font-mono uppercase text-muted-foreground">{METRIC_LABELS[k]}</div>
            <div className="mt-1 text-2xl font-mono font-bold text-primary">
              {live.data ? fmt(live.data[k] ?? 0) : "—"}
            </div>
          </div>
        ))}
      </section>

      <section className="rounded-lg border border-border/40 bg-card">
        <div className="px-4 py-3 border-b border-border/40 flex items-center justify-between">
          <h2 className="font-mono text-sm uppercase tracking-wide">History ({snaps.length})</h2>
          <span className="text-xs text-muted-foreground font-mono">most recent first</span>
        </div>
        {snaps.length === 0 ? (
          <div className="p-8 text-center text-muted-foreground font-mono text-sm">
            No snapshots yet. Hit <span className="text-primary">Capture Snapshot</span> to record the first
            point in your empire's history.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-xs font-mono uppercase text-muted-foreground border-b border-border/40">
                  <th className="px-4 py-2">Captured</th>
                  {keys.map((k) => (
                    <th key={k} className="px-4 py-2 text-right">{METRIC_LABELS[k]}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {snaps.map((s, i) => {
                  const prev = snaps[i + 1];
                  return (
                    <tr key={s.id} className="border-b border-border/20 hover:bg-muted/30">
                      <td className="px-4 py-2 font-mono text-xs whitespace-nowrap">
                        {new Date(s.capturedAt).toLocaleString()}
                      </td>
                      {keys.map((k) => (
                        <td key={k} className="px-4 py-2 text-right font-mono">
                          <div className="flex items-center justify-end gap-2">
                            <span>{fmt(s.metrics[k] ?? 0)}</span>
                            <Delta curr={s.metrics[k] ?? 0} prev={prev?.metrics[k]} />
                          </div>
                        </td>
                      ))}
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </div>
  );
}
