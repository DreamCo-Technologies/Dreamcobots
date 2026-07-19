import { useState } from "react";
import AppShell from "@/components/AppShell";
import Seo from "@/components/Seo";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Separator } from "@/components/ui/separator";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useToast } from "@/hooks/use-toast";
import { useBots } from "@/hooks/use-bots";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiRequest } from "@/lib/queryClient";
import { cn } from "@/lib/utils";
import {
  Plus, Trash2, Play, FlaskConical, CheckCircle2, XCircle,
  Clock, Loader2, ChevronDown, ChevronUp, Save, RefreshCw,
  Zap, BarChart3, AlertCircle, Terminal, ClipboardList,
} from "lucide-react";

interface TestCase {
  id: string;
  name: string;
  prompt: string;
  expectedKeywords: string;
  mustNotContain: string;
}

interface TestSuite {
  id: string;
  name: string;
  botSlug: string;
  cases: TestCase[];
  createdAt: string;
}

interface TestResult {
  caseId: string;
  caseName: string;
  prompt: string;
  response: string;
  passed: boolean;
  failReasons: string[];
  latencyMs: number;
  runAt: string;
}

interface RunSuiteResult {
  suiteId: string;
  suiteName: string;
  botSlug: string;
  passed: number;
  failed: number;
  total: number;
  avgLatencyMs: number;
  results: TestResult[];
  ranAt: string;
}

function newCase(): TestCase {
  return { id: crypto.randomUUID(), name: "", prompt: "", expectedKeywords: "", mustNotContain: "" };
}

function SuiteBuilder({
  suites, onSaved,
}: {
  suites: TestSuite[];
  onSaved: () => void;
}) {
  const { toast } = useToast();
  const qc = useQueryClient();
  const bots = useBots();

  const [suiteName, setSuiteName] = useState("My Test Suite");
  const [botSlug, setBotSlug] = useState("");
  const [cases, setCases] = useState<TestCase[]>([newCase()]);
  const [expanded, setExpanded] = useState<Record<string, boolean>>({});

  const saveMutation = useMutation({
    mutationFn: (payload: { name: string; botSlug: string; cases: TestCase[] }) =>
      apiRequest("POST", "/api/harness/suites", payload),
    onSuccess: () => {
      toast({ title: "Suite saved", description: `"${suiteName}" is ready to run.` });
      qc.invalidateQueries({ queryKey: ["/api/harness/suites"] });
      onSaved();
    },
    onError: (e: any) => toast({ title: "Save failed", description: e.message, variant: "destructive" }),
  });

  function updateCase(id: string, field: keyof TestCase, val: string) {
    setCases(prev => prev.map(c => c.id === id ? { ...c, [field]: val } : c));
  }

  function addCase() {
    const nc = newCase();
    setCases(prev => [...prev, nc]);
    setExpanded(prev => ({ ...prev, [nc.id]: true }));
  }

  function removeCase(id: string) {
    setCases(prev => prev.filter(c => c.id !== id));
  }

  function handleSave() {
    if (!suiteName.trim()) return toast({ title: "Name required", variant: "destructive" });
    if (!botSlug) return toast({ title: "Select a bot", variant: "destructive" });
    if (cases.some(c => !c.prompt.trim())) return toast({ title: "All test cases need a prompt", variant: "destructive" });
    saveMutation.mutate({ name: suiteName, botSlug, cases });
  }

  return (
    <div className="space-y-5">
      {/* Suite meta */}
      <Card className="rounded-2xl border-border/60 p-5 space-y-4">
        <h3 className="font-semibold text-sm text-muted-foreground uppercase tracking-wider">Suite Configuration</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-1.5">
            <label className="text-xs font-medium text-muted-foreground">Suite Name</label>
            <Input
              value={suiteName}
              onChange={e => setSuiteName(e.target.value)}
              placeholder="e.g. Lead Bot Smoke Tests"
              className="rounded-xl border-border/60"
              data-testid="suite-name-input"
            />
          </div>
          <div className="space-y-1.5">
            <label className="text-xs font-medium text-muted-foreground">Bot to Test</label>
            <Select value={botSlug} onValueChange={setBotSlug}>
              <SelectTrigger className="rounded-xl border-border/60" data-testid="suite-bot-select">
                <SelectValue placeholder="Select a bot…" />
              </SelectTrigger>
              <SelectContent className="rounded-xl max-h-60">
                {(bots.data ?? []).map(b => (
                  <SelectItem key={b.slug} value={b.slug} className="rounded-lg">
                    {b.displayName}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </div>
      </Card>

      {/* Test cases */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <h3 className="font-semibold text-sm text-muted-foreground uppercase tracking-wider">
            Test Cases <span className="text-primary">({cases.length})</span>
          </h3>
          <Button size="sm" variant="outline" onClick={addCase} className="rounded-xl gap-1.5" data-testid="add-test-case">
            <Plus className="h-3.5 w-3.5" /> Add Case
          </Button>
        </div>

        {cases.map((tc, idx) => {
          const open = expanded[tc.id] ?? idx === 0;
          return (
            <Card key={tc.id} className="rounded-2xl border-border/60 overflow-hidden">
              <button
                className="w-full flex items-center gap-3 p-4 hover:bg-muted/30 transition-colors text-left"
                onClick={() => setExpanded(prev => ({ ...prev, [tc.id]: !open }))}
              >
                <span className="h-6 w-6 rounded-lg bg-primary/10 text-primary text-xs font-bold flex items-center justify-center flex-shrink-0">
                  {idx + 1}
                </span>
                <span className="flex-1 font-medium text-sm">{tc.name || `Test Case ${idx + 1}`}</span>
                {tc.prompt && <Badge variant="outline" className="text-xs rounded-lg">Prompt set</Badge>}
                {open ? <ChevronUp className="h-4 w-4 text-muted-foreground" /> : <ChevronDown className="h-4 w-4 text-muted-foreground" />}
              </button>

              {open && (
                <div className="px-4 pb-4 space-y-3 border-t border-border/40 pt-3">
                  <div className="space-y-1.5">
                    <label className="text-xs font-medium text-muted-foreground">Case Name</label>
                    <Input
                      value={tc.name}
                      onChange={e => updateCase(tc.id, "name", e.target.value)}
                      placeholder="e.g. Greets user correctly"
                      className="rounded-xl border-border/60 text-sm"
                    />
                  </div>
                  <div className="space-y-1.5">
                    <label className="text-xs font-medium text-muted-foreground">Prompt to Send</label>
                    <Textarea
                      value={tc.prompt}
                      onChange={e => updateCase(tc.id, "prompt", e.target.value)}
                      placeholder="What should be sent to the bot?"
                      className="rounded-xl border-border/60 text-sm min-h-[80px] resize-none"
                    />
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    <div className="space-y-1.5">
                      <label className="text-xs font-medium text-green-400">✓ Must Contain (keywords, comma-separated)</label>
                      <Input
                        value={tc.expectedKeywords}
                        onChange={e => updateCase(tc.id, "expectedKeywords", e.target.value)}
                        placeholder="hello, welcome, help"
                        className="rounded-xl border-green-500/20 text-sm"
                      />
                    </div>
                    <div className="space-y-1.5">
                      <label className="text-xs font-medium text-red-400">✗ Must Not Contain (comma-separated)</label>
                      <Input
                        value={tc.mustNotContain}
                        onChange={e => updateCase(tc.id, "mustNotContain", e.target.value)}
                        placeholder="error, sorry, cannot"
                        className="rounded-xl border-red-500/20 text-sm"
                      />
                    </div>
                  </div>
                  {cases.length > 1 && (
                    <Button
                      size="sm" variant="ghost"
                      onClick={() => removeCase(tc.id)}
                      className="text-destructive hover:text-destructive rounded-xl gap-1.5"
                    >
                      <Trash2 className="h-3.5 w-3.5" /> Remove case
                    </Button>
                  )}
                </div>
              )}
            </Card>
          );
        })}
      </div>

      <Button
        onClick={handleSave}
        disabled={saveMutation.isPending}
        className="w-full rounded-xl h-11 font-semibold gap-2"
        data-testid="save-suite"
      >
        {saveMutation.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : <Save className="h-4 w-4" />}
        Save Test Suite
      </Button>
    </div>
  );
}

function SuiteRunner({ suites, onRefresh }: { suites: TestSuite[]; onRefresh: () => void }) {
  const { toast } = useToast();
  const qc = useQueryClient();
  const [selectedSuiteId, setSelectedSuiteId] = useState<string>("");
  const [runResult, setRunResult] = useState<RunSuiteResult | null>(null);
  const [running, setRunning] = useState(false);
  const [expandedResult, setExpandedResult] = useState<Record<string, boolean>>({});

  const selectedSuite = suites.find(s => s.id === selectedSuiteId);

  const deleteMutation = useMutation({
    mutationFn: (id: string) => apiRequest("DELETE", `/api/harness/suites/${id}`),
    onSuccess: () => {
      toast({ title: "Suite deleted" });
      qc.invalidateQueries({ queryKey: ["/api/harness/suites"] });
      setSelectedSuiteId("");
      setRunResult(null);
    },
  });

  async function runSuite() {
    if (!selectedSuite) return;
    setRunning(true);
    setRunResult(null);
    try {
      const r = await fetch("/api/harness/run-suite", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ suiteId: selectedSuite.id }),
      });
      const data = await r.json() as RunSuiteResult;
      setRunResult(data);
      if (data.passed === data.total) {
        toast({ title: `✅ All ${data.total} tests passed!`, description: `Avg latency: ${data.avgLatencyMs}ms` });
      } else {
        toast({ title: `⚠️ ${data.failed} of ${data.total} tests failed`, description: "See results below.", variant: "destructive" });
      }
    } catch (e: any) {
      toast({ title: "Run failed", description: e.message, variant: "destructive" });
    } finally {
      setRunning(false);
    }
  }

  const passRate = runResult ? Math.round((runResult.passed / runResult.total) * 100) : null;

  return (
    <div className="space-y-5">
      {/* Suite picker */}
      <Card className="rounded-2xl border-border/60 p-5 space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="font-semibold text-sm text-muted-foreground uppercase tracking-wider">Select Suite to Run</h3>
          <Button size="sm" variant="ghost" onClick={onRefresh} className="rounded-xl gap-1.5 text-muted-foreground">
            <RefreshCw className="h-3.5 w-3.5" /> Refresh
          </Button>
        </div>

        {suites.length === 0 ? (
          <p className="text-sm text-muted-foreground text-center py-4">No suites saved yet. Build one in the Builder tab.</p>
        ) : (
          <div className="space-y-2">
            {suites.map(s => (
              <button
                key={s.id}
                onClick={() => { setSelectedSuiteId(s.id); setRunResult(null); }}
                className={cn(
                  "w-full text-left flex items-center gap-3 p-3 rounded-xl border transition-all",
                  selectedSuiteId === s.id
                    ? "border-primary/50 bg-primary/8"
                    : "border-border/60 hover:border-border hover:bg-muted/30"
                )}
                data-testid={`suite-${s.id}`}
              >
                <FlaskConical className={cn("h-4 w-4 flex-shrink-0", selectedSuiteId === s.id ? "text-primary" : "text-muted-foreground")} />
                <div className="flex-1 min-w-0">
                  <p className="font-medium text-sm">{s.name}</p>
                  <p className="text-xs text-muted-foreground">{s.botSlug} · {s.cases.length} cases</p>
                </div>
                {selectedSuiteId === s.id && (
                  <Badge className="bg-primary/15 text-primary border-primary/20 text-xs">Selected</Badge>
                )}
              </button>
            ))}
          </div>
        )}

        {selectedSuite && (
          <div className="flex gap-2 pt-1">
            <Button
              onClick={runSuite}
              disabled={running}
              className="flex-1 rounded-xl h-10 font-semibold gap-2"
              data-testid="run-suite"
            >
              {running ? <Loader2 className="h-4 w-4 animate-spin" /> : <Play className="h-4 w-4" />}
              {running ? "Running…" : `Run "${selectedSuite.name}"`}
            </Button>
            <Button
              variant="outline"
              size="icon"
              onClick={() => deleteMutation.mutate(selectedSuite.id)}
              className="rounded-xl border-destructive/30 text-destructive hover:bg-destructive/10"
            >
              <Trash2 className="h-4 w-4" />
            </Button>
          </div>
        )}
      </Card>

      {/* Results */}
      {runResult && (
        <div className="space-y-4">
          {/* Summary */}
          <Card className={cn(
            "rounded-2xl border p-5",
            passRate === 100 ? "border-green-500/30 bg-green-950/10" : "border-amber-500/30 bg-amber-950/10"
          )}>
            <div className="flex items-center justify-between mb-3">
              <h3 className="font-semibold">Run Results — {runResult.suiteName}</h3>
              <Badge className={cn(
                "text-sm font-bold",
                passRate === 100 ? "bg-green-500/20 text-green-300 border-green-500/30" : "bg-amber-500/20 text-amber-300 border-amber-500/30"
              )}>
                {passRate}% Pass Rate
              </Badge>
            </div>
            <div className="grid grid-cols-4 gap-3">
              {[
                { label: "Total", val: runResult.total, color: "text-foreground" },
                { label: "Passed", val: runResult.passed, color: "text-green-400" },
                { label: "Failed", val: runResult.failed, color: "text-red-400" },
                { label: "Avg ms", val: runResult.avgLatencyMs, color: "text-blue-400" },
              ].map(s => (
                <div key={s.label} className="text-center">
                  <p className={cn("text-2xl font-bold", s.color)}>{s.val}</p>
                  <p className="text-xs text-muted-foreground">{s.label}</p>
                </div>
              ))}
            </div>
          </Card>

          {/* Per-case results */}
          <div className="space-y-2">
            {runResult.results.map(r => {
              const open = expandedResult[r.caseId] ?? !r.passed;
              return (
                <Card key={r.caseId} className={cn(
                  "rounded-2xl border overflow-hidden",
                  r.passed ? "border-green-500/20" : "border-red-500/20"
                )}>
                  <button
                    className="w-full flex items-center gap-3 p-3.5 hover:bg-muted/20 transition-colors text-left"
                    onClick={() => setExpandedResult(prev => ({ ...prev, [r.caseId]: !open }))}
                  >
                    {r.passed
                      ? <CheckCircle2 className="h-4 w-4 text-green-500 flex-shrink-0" />
                      : <XCircle className="h-4 w-4 text-red-500 flex-shrink-0" />
                    }
                    <span className="flex-1 font-medium text-sm">{r.caseName}</span>
                    <span className="text-xs text-muted-foreground flex items-center gap-1">
                      <Clock className="h-3 w-3" />{r.latencyMs}ms
                    </span>
                    {open ? <ChevronUp className="h-4 w-4 text-muted-foreground" /> : <ChevronDown className="h-4 w-4 text-muted-foreground" />}
                  </button>
                  {open && (
                    <div className="px-4 pb-4 space-y-3 border-t border-border/40 pt-3">
                      <div>
                        <p className="text-xs font-medium text-muted-foreground mb-1">Prompt</p>
                        <p className="text-xs font-mono bg-muted/40 rounded-lg p-2">{r.prompt}</p>
                      </div>
                      <div>
                        <p className="text-xs font-medium text-muted-foreground mb-1">Response</p>
                        <ScrollArea className="h-28">
                          <p className="text-xs bg-muted/40 rounded-lg p-2 whitespace-pre-wrap">{r.response}</p>
                        </ScrollArea>
                      </div>
                      {r.failReasons.length > 0 && (
                        <div className="space-y-1">
                          {r.failReasons.map((reason, i) => (
                            <div key={i} className="flex items-start gap-2 text-xs text-red-400">
                              <XCircle className="h-3.5 w-3.5 mt-0.5 flex-shrink-0" />
                              {reason}
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  )}
                </Card>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}

export default function HarnessPage() {
  const qc = useQueryClient();
  const suitesQuery = useQuery<{ suites: TestSuite[] }>({
    queryKey: ["/api/harness/suites"],
  });
  const suites = suitesQuery.data?.suites ?? [];
  const [tab, setTab] = useState("builder");

  function refresh() {
    qc.invalidateQueries({ queryKey: ["/api/harness/suites"] });
    suitesQuery.refetch();
  }

  const passedTotal = 0;

  return (
    <AppShell>
      <Seo title="DreamCo Empire OS — Harness Tester & Builder" description="Build and run automated test suites for any bot in the Empire." />

      <div className="buddy-appear space-y-6">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-end md:justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-3xl md:text-4xl">Harness Tester</h2>
              <Badge className="bg-amber-500/20 text-amber-300 border-amber-500/30 text-xs rounded-lg">
                <FlaskConical className="h-3 w-3 mr-1" />
                QA Lab
              </Badge>
            </div>
            <p className="mt-2 text-muted-foreground text-sm max-w-xl">
              Build automated test suites for any bot. Define prompts, expected keywords, and blocklists — then run full suites and see pass/fail results with latency metrics.
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Card className="rounded-2xl border-border/60 px-4 py-2.5 flex items-center gap-2">
              <BarChart3 className="h-4 w-4 text-primary" />
              <div>
                <p className="text-xs text-muted-foreground">Saved Suites</p>
                <p className="text-lg font-bold leading-none">{suites.length}</p>
              </div>
            </Card>
            <Card className="rounded-2xl border-border/60 px-4 py-2.5 flex items-center gap-2">
              <ClipboardList className="h-4 w-4 text-green-400" />
              <div>
                <p className="text-xs text-muted-foreground">Total Cases</p>
                <p className="text-lg font-bold leading-none">{suites.reduce((a, s) => a + s.cases.length, 0)}</p>
              </div>
            </Card>
          </div>
        </div>

        <Separator className="opacity-40" />

        <Tabs value={tab} onValueChange={setTab}>
          <TabsList className="rounded-2xl bg-muted/40 p-1 h-auto">
            {[
              { val: "builder", label: "Builder", icon: Plus },
              { val: "runner", label: "Runner", icon: Play },
            ].map(({ val, label, icon: Icon }) => (
              <TabsTrigger
                key={val} value={val}
                className="rounded-xl gap-2 px-4 py-2 data-[state=active]:bg-background data-[state=active]:shadow-sm"
                data-testid={`tab-${val}`}
              >
                <Icon className="h-4 w-4" />{label}
              </TabsTrigger>
            ))}
          </TabsList>

          <TabsContent value="builder" className="mt-5">
            <SuiteBuilder suites={suites} onSaved={() => { refresh(); setTab("runner"); }} />
          </TabsContent>
          <TabsContent value="runner" className="mt-5">
            <SuiteRunner suites={suites} onRefresh={refresh} />
          </TabsContent>
        </Tabs>
      </div>
    </AppShell>
  );
}
