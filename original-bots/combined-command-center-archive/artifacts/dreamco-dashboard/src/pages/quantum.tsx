import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Atom, ExternalLink } from "lucide-react";

async function api<T>(path: string): Promise<T> {
  const r = await fetch(`/api${path}`, { headers: { "Content-Type": "application/json" } });
  if (!r.ok) throw new Error(`${r.status}`);
  return r.json() as Promise<T>;
}

interface Provider {
  id: string;
  name: string;
  hardware: string | null;
  accessModel: string | null;
  headquarters: string | null;
  url: string | null;
  summary: string | null;
  category: string;
}
interface QuantumResponse {
  total: number;
  byCategory: Record<string, number>;
  byHardware: Record<string, number>;
  providers: Provider[];
}

const HW_COLORS: Record<string, string> = {
  superconducting: "text-sky-400 border-sky-400/30",
  "trapped-ion": "text-amber-400 border-amber-400/30",
  photonic: "text-fuchsia-400 border-fuchsia-400/30",
  "neutral-atom": "text-emerald-400 border-emerald-400/30",
  annealing: "text-orange-400 border-orange-400/30",
  spin: "text-violet-400 border-violet-400/30",
  simulator: "text-teal-400 border-teal-400/30",
  software: "text-rose-400 border-rose-400/30",
};

export default function QuantumPage() {
  const { data, isLoading } = useQuery<QuantumResponse>({ queryKey: ["quantum"], queryFn: () => api("/quantum") });
  const [filter, setFilter] = useState<string>("all");

  const providers = (data?.providers ?? []).filter((p) => filter === "all" || p.hardware === filter);
  const hardwareKeys = Object.keys(data?.byHardware ?? {}).sort();

  return (
    <div className="p-6 space-y-6">
      <header className="flex items-center gap-3">
        <Atom className="h-8 w-8 text-primary" />
        <div>
          <h1 className="text-2xl font-mono font-bold tracking-wide">Quantum_Providers</h1>
          <p className="text-sm text-muted-foreground max-w-3xl">
            Curated directory of real quantum-computing companies DreamCo can resell access to or route client
            workloads toward. Factual company info only — not live capacity or pricing.{" "}
            <span className="text-sky-400 font-mono">DIRECTORY</span>
          </p>
        </div>
      </header>

      <section className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <Stat label="Providers" value={data?.total ?? 0} />
        <Stat label="Hardware Vendors" value={data?.byCategory?.["hardware"] ?? 0} />
        <Stat label="Cloud Access" value={data?.byCategory?.["cloud-access"] ?? 0} />
        <Stat label="Software" value={data?.byCategory?.["software"] ?? 0} />
      </section>

      <div className="flex flex-wrap gap-2">
        <FilterChip label="all" active={filter === "all"} onClick={() => setFilter("all")} count={data?.total ?? 0} />
        {hardwareKeys.map((hw) => (
          <FilterChip key={hw} label={hw} active={filter === hw} onClick={() => setFilter(hw)} count={data!.byHardware[hw]} />
        ))}
      </div>

      {isLoading ? (
        <div className="p-8 text-center text-muted-foreground font-mono text-sm">Loading directory…</div>
      ) : (
        <section className="grid gap-3 md:grid-cols-2 lg:grid-cols-3">
          {providers.map((p) => (
            <div key={p.id} className="rounded-lg border border-border/40 bg-card p-4 space-y-2">
              <div className="flex items-center justify-between gap-2">
                <h3 className="font-mono text-sm font-bold">{p.name}</h3>
                {p.url && (
                  <a
                    href={p.url}
                    target="_blank"
                    rel="noreferrer"
                    className="text-muted-foreground hover:text-primary flex items-center gap-1 text-xs font-mono shrink-0"
                  >
                    visit <ExternalLink className="h-3 w-3" />
                  </a>
                )}
              </div>
              <div className="flex flex-wrap gap-1.5">
                {p.hardware && (
                  <span className={`px-1.5 py-0.5 rounded border text-[10px] font-mono ${HW_COLORS[p.hardware] ?? "text-muted-foreground border-border/40"}`}>
                    {p.hardware}
                  </span>
                )}
                {p.accessModel && (
                  <span className="px-1.5 py-0.5 rounded bg-muted text-[10px] font-mono">{p.accessModel}</span>
                )}
              </div>
              {p.summary && <p className="text-xs text-muted-foreground">{p.summary}</p>}
              {p.headquarters && <p className="text-[10px] font-mono text-muted-foreground">{p.headquarters}</p>}
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

function FilterChip({ label, active, onClick, count }: { label: string; active: boolean; onClick: () => void; count: number }) {
  return (
    <button
      onClick={onClick}
      className={`px-2.5 py-1 rounded border text-xs font-mono transition-colors ${
        active ? "border-primary text-primary bg-primary/10" : "border-border/40 text-muted-foreground hover:text-foreground"
      }`}
    >
      {label} · {count}
    </button>
  );
}
