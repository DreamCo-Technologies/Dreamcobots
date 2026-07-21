import { useState, useRef } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { ShieldCheck, Mic, Image as ImageIcon, ScrollText, Loader2, CheckCircle2, XCircle, AlertTriangle } from "lucide-react";
import { Button } from "@/components/ui/button";

async function api<T>(path: string, init?: RequestInit): Promise<T> {
  const r = await fetch(`/api${path}`, {
    headers: { "Content-Type": "application/json" },
    ...init,
  });
  const body = r.status === 204 ? undefined : await r.json().catch(() => undefined);
  if (!r.ok) {
    const err = new Error((body as { error?: string })?.error ?? `${r.status}`) as Error & { body?: unknown; status?: number };
    err.body = body;
    err.status = r.status;
    throw err;
  }
  return body as T;
}

type Modality = "voice" | "image";
type CapStatus = "live" | "needs_key" | "needs_config";

interface LawSummary { name: string; jurisdiction: string; summary: string }
interface PolicySection { heading: string; body: string }
interface BiometricPolicy {
  key: string;
  version: string;
  title: string;
  intro: string;
  laws: LawSummary[];
  sections: PolicySection[];
  userPromises: string[];
  disclaimer: string;
}
interface PolicyResponse { policy: BiometricPolicy }

interface AckResponse {
  currentVersion: string;
  currentAccepted: boolean;
  acknowledgments: Array<{ id: string; version: string; acknowledgedAt: string }>;
}

interface CloneCapability { modality: Modality; status: CapStatus; provider: string; envVar: string; note: string }
interface CapsResponse { capabilities: CloneCapability[] }

interface Enrollment {
  id: string;
  modality: Modality;
  status: "enrolled" | "revoked";
  enrollmentMethod: string | null;
  lawsVersion: string;
  consentGivenAt: string;
  createdAt: string;
}
interface EnrollResponse { enrollments: Enrollment[] }

function badge(s: CapStatus): { label: string; cls: string } {
  if (s === "live") return { label: "LIVE", cls: "text-emerald-400 border-emerald-400/30" };
  return { label: "NEEDS_SETUP", cls: "text-amber-400 border-amber-400/30" };
}

export default function ConsentPage() {
  const qc = useQueryClient();
  const [readAll, setReadAll] = useState(false);
  const [promises, setPromises] = useState<Record<number, boolean>>({});
  const scrollRef = useRef<HTMLDivElement>(null);

  const { data: policyData } = useQuery<PolicyResponse>({ queryKey: ["bio-policy"], queryFn: () => api("/legal/biometric-policy") });
  const { data: ackData, isError: ackError } = useQuery<AckResponse>({ queryKey: ["bio-ack"], queryFn: () => api("/legal/acknowledgments"), retry: false });
  const { data: capsData } = useQuery<CapsResponse>({ queryKey: ["bio-caps"], queryFn: () => api("/biometric/capabilities") });
  const { data: enrollData } = useQuery<EnrollResponse>({ queryKey: ["bio-enroll"], queryFn: () => api("/biometric/enrollments"), retry: false });

  const policy = policyData?.policy;
  const accepted = ackData?.currentAccepted ?? false;
  const needsSignIn = ackError; // /legal/acknowledgments is 401 when not signed in
  const caps = capsData?.capabilities ?? [];
  const enrollments = enrollData?.enrollments ?? [];
  const activeFor = (m: Modality) => enrollments.find((e) => e.modality === m && e.status === "enrolled");

  const allPromisesChecked = !!policy && policy.userPromises.every((_, i) => promises[i]);

  const acknowledge = useMutation({
    mutationFn: () => api("/legal/acknowledge", { method: "POST", body: JSON.stringify({ version: policy!.version, accept: true }) }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["bio-ack"] }),
  });

  const enroll = useMutation({
    mutationFn: (modality: Modality) =>
      api("/biometric/enroll", { method: "POST", body: JSON.stringify({ modality, consent: true, enrollmentMethod: "recorded" }) }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["bio-enroll"] }),
  });

  const revoke = useMutation({
    mutationFn: (modality: Modality) => api("/biometric/revoke", { method: "POST", body: JSON.stringify({ modality }) }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["bio-enroll"] }),
  });

  function onScroll() {
    const el = scrollRef.current;
    if (!el) return;
    if (el.scrollTop + el.clientHeight >= el.scrollHeight - 24) setReadAll(true);
  }

  return (
    <div className="p-6 space-y-6 max-w-4xl">
      <header className="flex items-center gap-3">
        <ShieldCheck className="h-8 w-8 text-primary" />
        <div>
          <h1 className="text-2xl font-mono font-bold tracking-wide">Cloning_Consent &amp; Rights</h1>
          <p className="text-sm text-muted-foreground max-w-3xl">
            DreamCo can clone voices and faces at high quality — but only with verifiable, informed consent. Read the laws,
            accept the policy, then enroll your <span className="text-foreground">own</span> voice and/or image. You can only
            clone what you've personally enrolled and consented to.
          </p>
        </div>
      </header>

      {needsSignIn && (
        <div className="rounded-lg border border-amber-400/30 bg-amber-400/5 p-4 text-sm font-mono text-amber-300">
          Sign in to read the policy, enroll your biometrics, and use cloning.
        </div>
      )}

      {/* Step 1 — Read the laws */}
      <section className="rounded-lg border border-border/40 bg-card p-4 space-y-3">
        <div className="flex items-center gap-2">
          <ScrollText className="h-4 w-4 text-primary" />
          <h2 className="font-mono text-sm font-bold">Step 1 · Read the laws &amp; policy</h2>
          {accepted && <span className="ml-auto px-2 py-0.5 rounded border text-[10px] font-mono text-emerald-400 border-emerald-400/30">ACCEPTED v{ackData?.currentVersion}</span>}
        </div>

        {policy && (
          <>
            <p className="text-xs text-muted-foreground">{policy.intro}</p>
            <div
              ref={scrollRef}
              onScroll={onScroll}
              className="max-h-72 overflow-y-auto rounded-md border border-border/40 bg-background p-3 space-y-3 text-xs"
            >
              <div>
                <h3 className="font-mono font-bold text-sm mb-1">Laws that govern this</h3>
                {policy.laws.map((l) => (
                  <div key={l.name} className="mb-2">
                    <p className="font-mono text-[11px] text-foreground">{l.name} <span className="text-muted-foreground">· {l.jurisdiction}</span></p>
                    <p className="text-muted-foreground leading-snug">{l.summary}</p>
                  </div>
                ))}
              </div>
              {policy.sections.map((s) => (
                <div key={s.heading}>
                  <p className="font-mono text-[11px] text-foreground">{s.heading}</p>
                  <p className="text-muted-foreground leading-snug">{s.body}</p>
                </div>
              ))}
              <p className="text-[11px] text-amber-300/90 leading-snug border-t border-border/40 pt-2">{policy.disclaimer}</p>
            </div>

            {!accepted && (
              <div className="space-y-2">
                {policy.userPromises.map((p, i) => (
                  <label key={i} className="flex items-start gap-2 text-xs text-muted-foreground cursor-pointer select-none">
                    <input
                      type="checkbox"
                      checked={!!promises[i]}
                      disabled={!readAll || needsSignIn}
                      onChange={(e) => setPromises((prev) => ({ ...prev, [i]: e.target.checked }))}
                      className="mt-0.5"
                    />
                    <span>{p}</span>
                  </label>
                ))}
                {!readAll && <p className="text-[10px] font-mono text-amber-400">Scroll to the bottom of the policy to enable acceptance.</p>}
                <Button
                  className="font-mono"
                  disabled={!readAll || !allPromisesChecked || needsSignIn || acknowledge.isPending}
                  onClick={() => acknowledge.mutate()}
                >
                  {acknowledge.isPending ? <Loader2 className="h-4 w-4 mr-2 animate-spin" /> : null}
                  Accept policy v{policy.version}
                </Button>
              </div>
            )}
          </>
        )}
      </section>

      {/* Step 2 — Enroll your own biometrics */}
      <section className="rounded-lg border border-border/40 bg-card p-4 space-y-3">
        <div className="flex items-center gap-2">
          <ShieldCheck className="h-4 w-4 text-primary" />
          <h2 className="font-mono text-sm font-bold">Step 2 · Enroll your own voice / image</h2>
        </div>
        <p className="text-xs text-muted-foreground">
          Enrolling registers your <span className="text-foreground">own</span> voice or face as a consented reference.
          Cloning is restricted to modalities you've enrolled. {accepted ? "" : "Accept the policy above first."}
        </p>
        <div className="grid sm:grid-cols-2 gap-3">
          {(["voice", "image"] as Modality[]).map((m) => {
            const Icon = m === "voice" ? Mic : ImageIcon;
            const active = activeFor(m);
            return (
              <div key={m} className="rounded-md border border-border/40 bg-background p-3 space-y-2">
                <div className="flex items-center gap-2">
                  <Icon className="h-4 w-4 text-primary" />
                  <span className="font-mono text-sm font-bold capitalize">{m}</span>
                  {active ? (
                    <span className="ml-auto inline-flex items-center gap-1 text-[10px] font-mono text-emerald-400"><CheckCircle2 className="h-3 w-3" /> ENROLLED</span>
                  ) : (
                    <span className="ml-auto inline-flex items-center gap-1 text-[10px] font-mono text-muted-foreground"><XCircle className="h-3 w-3" /> not enrolled</span>
                  )}
                </div>
                {active ? (
                  <>
                    <p className="text-[10px] font-mono text-muted-foreground">
                      Consented {new Date(active.consentGivenAt).toLocaleDateString()} · policy v{active.lawsVersion}
                    </p>
                    <Button variant="outline" size="sm" className="font-mono" disabled={revoke.isPending} onClick={() => revoke.mutate(m)}>
                      Revoke {m} enrollment
                    </Button>
                  </>
                ) : (
                  <Button size="sm" className="font-mono" disabled={!accepted || enroll.isPending} onClick={() => enroll.mutate(m)}>
                    {enroll.isPending ? <Loader2 className="h-4 w-4 mr-2 animate-spin" /> : null}
                    Enroll my {m}
                  </Button>
                )}
              </div>
            );
          })}
        </div>
      </section>

      {/* Step 3 — Engine readiness (honest) */}
      <section className="rounded-lg border border-border/40 bg-card p-4 space-y-3">
        <div className="flex items-center gap-2">
          <AlertTriangle className="h-4 w-4 text-primary" />
          <h2 className="font-mono text-sm font-bold">Step 3 · Cloning engines</h2>
        </div>
        <div className="grid sm:grid-cols-2 gap-3">
          {caps.map((c) => {
            const b = badge(c.status);
            return (
              <div key={c.modality} className="rounded-md border border-border/40 bg-background p-3">
                <div className="flex items-center gap-2">
                  <span className="font-mono text-sm font-bold capitalize">{c.modality} clone</span>
                  <span className={`ml-auto px-2 py-0.5 rounded border text-[10px] font-mono ${b.cls}`}>{b.label}</span>
                </div>
                <p className="text-[10px] font-mono text-muted-foreground mt-1">{c.provider}</p>
                <p className="text-[11px] text-muted-foreground mt-1 leading-snug">{c.note}</p>
              </div>
            );
          })}
        </div>
        <p className="text-[10px] font-mono text-muted-foreground">
          Engines are self-hosted and owned by DreamCo (no ElevenLabs). When an engine is connected, the consent + enrollment
          + legal gates above are enforced on every clone request — automatically.
        </p>
      </section>
    </div>
  );
}
