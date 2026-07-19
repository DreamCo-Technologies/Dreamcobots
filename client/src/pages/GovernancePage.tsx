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
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiRequest } from "@/lib/queryClient";
import { cn } from "@/lib/utils";
import {
  Plus, Trash2, ShieldCheck, Users, Loader2, CheckCircle2,
  XCircle, AlertCircle, ChevronDown, ChevronUp, Gavel, Scale,
  BarChart3, RefreshCw, Zap, BookOpen, TestTube2, ArrowRight,
  Clock, Shield, Activity,
} from "lucide-react";

interface GovernanceRule {
  id: string;
  name: string;
  description: string;
  trigger: string;
  condition: string;
  action: string;
  severity: "info" | "warning" | "critical";
  scope: "all-bots" | "division" | "specific-bot";
  scopeTarget: string;
  enabled: boolean;
  createdAt: string;
}

interface Proposal {
  id: string;
  botSlug: string;
  division: string;
  type: string;
  title: string;
  description: string;
  priority: "low" | "medium" | "high" | "critical";
  status: "pending" | "approved" | "rejected";
  submittedAt: string;
}

interface RuleTestResult {
  ruleId: string;
  ruleName: string;
  scenario: string;
  triggered: boolean;
  reasoning: string;
  suggestedAction: string;
  severity: string;
  testedAt: string;
}

const PRIORITY_COLORS: Record<string, string> = {
  low: "bg-blue-500/15 text-blue-300 border-blue-500/20",
  medium: "bg-amber-500/15 text-amber-300 border-amber-500/20",
  high: "bg-orange-500/15 text-orange-300 border-orange-500/20",
  critical: "bg-red-500/15 text-red-300 border-red-500/20",
};

const SEVERITY_COLORS: Record<string, string> = {
  info: "bg-blue-500/15 text-blue-300 border-blue-500/20",
  warning: "bg-amber-500/15 text-amber-300 border-amber-500/20",
  critical: "bg-red-500/15 text-red-300 border-red-500/20",
};

function CouncilTab() {
  const { toast } = useToast();
  const qc = useQueryClient();
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ botSlug: "", division: "", type: "upgrade", title: "", description: "", priority: "medium" });

  const proposalsQuery = useQuery<{ proposals: Proposal[]; total: number }>({
    queryKey: ["/api/council/proposals"],
  });
  const proposals = proposalsQuery.data?.proposals ?? [];

  const voteMutation = useMutation({
    mutationFn: ({ id, status }: { id: string; status: string }) =>
      apiRequest("PATCH", `/api/council/proposals/${id}`, { status }),
    onSuccess: () => {
      toast({ title: "Vote recorded" });
      qc.invalidateQueries({ queryKey: ["/api/council/proposals"] });
    },
  });

  const submitMutation = useMutation({
    mutationFn: (payload: typeof form) => apiRequest("POST", "/api/council/report", payload),
    onSuccess: () => {
      toast({ title: "Proposal submitted to council" });
      qc.invalidateQueries({ queryKey: ["/api/council/proposals"] });
      setShowForm(false);
      setForm({ botSlug: "", division: "", type: "upgrade", title: "", description: "", priority: "medium" });
    },
    onError: (e: any) => toast({ title: "Submit failed", description: e.message, variant: "destructive" }),
  });

  const pending = proposals.filter(p => p.status === "pending");
  const approved = proposals.filter(p => p.status === "approved");
  const rejected = proposals.filter(p => p.status === "rejected");

  return (
    <div className="space-y-5">
      {/* Stats */}
      <div className="grid grid-cols-3 gap-3">
        {[
          { label: "Pending", val: pending.length, color: "text-amber-400", bg: "bg-amber-500/10 border-amber-500/20" },
          { label: "Approved", val: approved.length, color: "text-green-400", bg: "bg-green-500/10 border-green-500/20" },
          { label: "Rejected", val: rejected.length, color: "text-red-400", bg: "bg-red-500/10 border-red-500/20" },
        ].map(s => (
          <Card key={s.label} className={cn("rounded-2xl border p-4 text-center", s.bg)}>
            <p className={cn("text-2xl font-bold", s.color)}>{s.val}</p>
            <p className="text-xs text-muted-foreground">{s.label}</p>
          </Card>
        ))}
      </div>

      <div className="flex items-center justify-between">
        <h3 className="font-semibold text-sm text-muted-foreground uppercase tracking-wider">
          Active Proposals ({proposals.length})
        </h3>
        <div className="flex gap-2">
          <Button size="sm" variant="ghost" onClick={() => proposalsQuery.refetch()} className="rounded-xl gap-1.5 text-muted-foreground">
            <RefreshCw className="h-3.5 w-3.5" />
          </Button>
          <Button size="sm" variant="outline" onClick={() => setShowForm(v => !v)} className="rounded-xl gap-1.5" data-testid="submit-proposal-toggle">
            <Plus className="h-3.5 w-3.5" /> Submit Proposal
          </Button>
        </div>
      </div>

      {/* Submit form */}
      {showForm && (
        <Card className="rounded-2xl border-primary/30 bg-primary/5 p-5 space-y-3">
          <h4 className="font-semibold text-sm">New Council Proposal</h4>
          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1.5">
              <label className="text-xs font-medium text-muted-foreground">Bot Slug</label>
              <Input value={form.botSlug} onChange={e => setForm(p => ({ ...p, botSlug: e.target.value }))} placeholder="buddy-bot" className="rounded-xl" />
            </div>
            <div className="space-y-1.5">
              <label className="text-xs font-medium text-muted-foreground">Division</label>
              <Input value={form.division} onChange={e => setForm(p => ({ ...p, division: e.target.value }))} placeholder="CommandCore" className="rounded-xl" />
            </div>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1.5">
              <label className="text-xs font-medium text-muted-foreground">Type</label>
              <Select value={form.type} onValueChange={v => setForm(p => ({ ...p, type: v }))}>
                <SelectTrigger className="rounded-xl"><SelectValue /></SelectTrigger>
                <SelectContent className="rounded-xl">
                  {["upgrade","integration","security","policy","removal"].map(t => (
                    <SelectItem key={t} value={t} className="rounded-lg capitalize">{t}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-1.5">
              <label className="text-xs font-medium text-muted-foreground">Priority</label>
              <Select value={form.priority} onValueChange={v => setForm(p => ({ ...p, priority: v }))}>
                <SelectTrigger className="rounded-xl"><SelectValue /></SelectTrigger>
                <SelectContent className="rounded-xl">
                  {["low","medium","high","critical"].map(t => (
                    <SelectItem key={t} value={t} className="rounded-lg capitalize">{t}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
          <div className="space-y-1.5">
            <label className="text-xs font-medium text-muted-foreground">Title</label>
            <Input value={form.title} onChange={e => setForm(p => ({ ...p, title: e.target.value }))} placeholder="Brief proposal title" className="rounded-xl" />
          </div>
          <div className="space-y-1.5">
            <label className="text-xs font-medium text-muted-foreground">Description</label>
            <Textarea value={form.description} onChange={e => setForm(p => ({ ...p, description: e.target.value }))} placeholder="Describe what change is needed and why…" className="rounded-xl min-h-[80px] resize-none" />
          </div>
          <div className="flex gap-2">
            <Button onClick={() => submitMutation.mutate(form)} disabled={submitMutation.isPending} className="flex-1 rounded-xl gap-2" data-testid="submit-proposal">
              {submitMutation.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : <Gavel className="h-4 w-4" />}
              Submit to Council
            </Button>
            <Button variant="ghost" onClick={() => setShowForm(false)} className="rounded-xl">Cancel</Button>
          </div>
        </Card>
      )}

      {/* Proposal list */}
      <ScrollArea className="h-[500px] pr-2">
        <div className="space-y-3">
          {proposals.map(p => (
            <Card key={p.id} className={cn(
              "rounded-2xl border overflow-hidden",
              p.status === "approved" ? "border-green-500/20" :
              p.status === "rejected" ? "border-red-500/20 opacity-60" :
              "border-border/60"
            )}>
              <div className="p-4 space-y-2">
                <div className="flex items-start justify-between gap-3">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 flex-wrap">
                      <Badge variant="outline" className={cn("text-xs rounded-lg", PRIORITY_COLORS[p.priority])}>
                        {p.priority.toUpperCase()}
                      </Badge>
                      <Badge variant="outline" className="text-xs rounded-lg">{p.type}</Badge>
                      {p.status !== "pending" && (
                        <Badge variant="outline" className={cn("text-xs rounded-lg",
                          p.status === "approved" ? "bg-green-500/15 text-green-300 border-green-500/20" : "bg-red-500/15 text-red-300 border-red-500/20"
                        )}>
                          {p.status === "approved" ? <CheckCircle2 className="h-3 w-3 mr-1" /> : <XCircle className="h-3 w-3 mr-1" />}
                          {p.status}
                        </Badge>
                      )}
                    </div>
                    <h4 className="font-semibold mt-2">{p.title}</h4>
                    <p className="text-sm text-muted-foreground mt-1">{p.description}</p>
                    <p className="text-xs text-muted-foreground mt-2">
                      By <span className="text-foreground">{p.botSlug}</span> · {p.division} · {new Date(p.submittedAt).toLocaleDateString()}
                    </p>
                  </div>
                </div>
                {p.status === "pending" && (
                  <div className="flex gap-2 pt-1">
                    <Button
                      size="sm" variant="outline"
                      onClick={() => voteMutation.mutate({ id: p.id, status: "approved" })}
                      disabled={voteMutation.isPending}
                      className="flex-1 rounded-xl border-green-500/30 text-green-400 hover:bg-green-950/20 gap-1.5"
                      data-testid={`approve-${p.id}`}
                    >
                      <CheckCircle2 className="h-3.5 w-3.5" /> Approve
                    </Button>
                    <Button
                      size="sm" variant="outline"
                      onClick={() => voteMutation.mutate({ id: p.id, status: "rejected" })}
                      disabled={voteMutation.isPending}
                      className="flex-1 rounded-xl border-red-500/30 text-red-400 hover:bg-red-950/20 gap-1.5"
                      data-testid={`reject-${p.id}`}
                    >
                      <XCircle className="h-3.5 w-3.5" /> Reject
                    </Button>
                  </div>
                )}
              </div>
            </Card>
          ))}
        </div>
      </ScrollArea>
    </div>
  );
}

function RulesTab() {
  const { toast } = useToast();
  const qc = useQueryClient();
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({
    name: "", description: "", trigger: "", condition: "", action: "",
    severity: "warning", scope: "all-bots", scopeTarget: "",
  });

  const rulesQuery = useQuery<{ rules: GovernanceRule[] }>({
    queryKey: ["/api/governance/rules"],
  });
  const rules = rulesQuery.data?.rules ?? [];

  const createMutation = useMutation({
    mutationFn: (payload: typeof form) => apiRequest("POST", "/api/governance/rules", payload),
    onSuccess: () => {
      toast({ title: "Rule created" });
      qc.invalidateQueries({ queryKey: ["/api/governance/rules"] });
      setShowForm(false);
      setForm({ name: "", description: "", trigger: "", condition: "", action: "", severity: "warning", scope: "all-bots", scopeTarget: "" });
    },
    onError: (e: any) => toast({ title: "Failed", description: e.message, variant: "destructive" }),
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => apiRequest("DELETE", `/api/governance/rules/${id}`),
    onSuccess: () => {
      toast({ title: "Rule deleted" });
      qc.invalidateQueries({ queryKey: ["/api/governance/rules"] });
    },
  });

  const toggleMutation = useMutation({
    mutationFn: ({ id, enabled }: { id: string; enabled: boolean }) =>
      apiRequest("PATCH", `/api/governance/rules/${id}`, { enabled }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["/api/governance/rules"] }),
  });

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <h3 className="font-semibold text-sm text-muted-foreground uppercase tracking-wider">
          Governance Rules ({rules.length})
        </h3>
        <Button size="sm" variant="outline" onClick={() => setShowForm(v => !v)} className="rounded-xl gap-1.5" data-testid="create-rule">
          <Plus className="h-3.5 w-3.5" /> New Rule
        </Button>
      </div>

      {showForm && (
        <Card className="rounded-2xl border-primary/30 bg-primary/5 p-5 space-y-3">
          <h4 className="font-semibold text-sm">Build Governance Rule</h4>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            <div className="space-y-1.5">
              <label className="text-xs font-medium text-muted-foreground">Rule Name</label>
              <Input value={form.name} onChange={e => setForm(p => ({ ...p, name: e.target.value }))} placeholder="e.g. Block offensive output" className="rounded-xl" />
            </div>
            <div className="space-y-1.5">
              <label className="text-xs font-medium text-muted-foreground">Severity</label>
              <Select value={form.severity} onValueChange={v => setForm(p => ({ ...p, severity: v }))}>
                <SelectTrigger className="rounded-xl"><SelectValue /></SelectTrigger>
                <SelectContent className="rounded-xl">
                  {["info","warning","critical"].map(s => (
                    <SelectItem key={s} value={s} className="rounded-lg capitalize">{s}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
          <div className="space-y-1.5">
            <label className="text-xs font-medium text-muted-foreground">Description</label>
            <Input value={form.description} onChange={e => setForm(p => ({ ...p, description: e.target.value }))} placeholder="What does this rule do?" className="rounded-xl" />
          </div>
          <div className="space-y-1.5">
            <label className="text-xs font-medium text-amber-400">⚡ Trigger — When does this activate?</label>
            <Input value={form.trigger} onChange={e => setForm(p => ({ ...p, trigger: e.target.value }))} placeholder="e.g. Bot generates a response, Bot is tasked with financial advice" className="rounded-xl" />
          </div>
          <div className="space-y-1.5">
            <label className="text-xs font-medium text-blue-400">🔍 Condition — What must be true?</label>
            <Textarea value={form.condition} onChange={e => setForm(p => ({ ...p, condition: e.target.value }))} placeholder="e.g. Response contains explicit content OR promises guaranteed returns" className="rounded-xl min-h-[70px] resize-none" />
          </div>
          <div className="space-y-1.5">
            <label className="text-xs font-medium text-green-400">🎯 Action — What should happen?</label>
            <Textarea value={form.action} onChange={e => setForm(p => ({ ...p, action: e.target.value }))} placeholder="e.g. Block response, Log to audit trail, Alert council, Downgrade bot autonomy" className="rounded-xl min-h-[70px] resize-none" />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1.5">
              <label className="text-xs font-medium text-muted-foreground">Scope</label>
              <Select value={form.scope} onValueChange={v => setForm(p => ({ ...p, scope: v }))}>
                <SelectTrigger className="rounded-xl"><SelectValue /></SelectTrigger>
                <SelectContent className="rounded-xl">
                  {["all-bots","division","specific-bot"].map(s => (
                    <SelectItem key={s} value={s} className="rounded-lg">{s.replace(/-/g," ")}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            {form.scope !== "all-bots" && (
              <div className="space-y-1.5">
                <label className="text-xs font-medium text-muted-foreground">{form.scope === "division" ? "Division Name" : "Bot Slug"}</label>
                <Input value={form.scopeTarget} onChange={e => setForm(p => ({ ...p, scopeTarget: e.target.value }))} placeholder={form.scope === "division" ? "CommandCore" : "buddy-bot"} className="rounded-xl" />
              </div>
            )}
          </div>
          <div className="flex gap-2">
            <Button onClick={() => createMutation.mutate(form)} disabled={createMutation.isPending} className="flex-1 rounded-xl gap-2" data-testid="save-rule">
              {createMutation.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : <Shield className="h-4 w-4" />}
              Create Rule
            </Button>
            <Button variant="ghost" onClick={() => setShowForm(false)} className="rounded-xl">Cancel</Button>
          </div>
        </Card>
      )}

      {rules.length === 0 ? (
        <Card className="rounded-2xl border-border/60 p-8 text-center text-muted-foreground">
          <Scale className="h-8 w-8 mx-auto mb-2 opacity-40" />
          <p className="text-sm">No governance rules yet. Create your first rule above.</p>
        </Card>
      ) : (
        <div className="space-y-3">
          {rules.map(rule => (
            <Card key={rule.id} className={cn(
              "rounded-2xl border overflow-hidden transition-all",
              rule.enabled ? "border-border/60" : "border-border/30 opacity-50"
            )}>
              <div className="p-4 space-y-3">
                <div className="flex items-start justify-between gap-3">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 flex-wrap mb-1">
                      <Badge variant="outline" className={cn("text-xs rounded-lg", SEVERITY_COLORS[rule.severity])}>
                        {rule.severity}
                      </Badge>
                      <Badge variant="outline" className="text-xs rounded-lg">{rule.scope.replace(/-/g," ")}</Badge>
                      {rule.scopeTarget && <Badge variant="outline" className="text-xs rounded-lg font-mono">{rule.scopeTarget}</Badge>}
                      {rule.enabled
                        ? <Badge className="text-xs rounded-lg bg-green-500/15 text-green-300 border-green-500/20">Active</Badge>
                        : <Badge className="text-xs rounded-lg bg-muted/50 text-muted-foreground">Disabled</Badge>
                      }
                    </div>
                    <h4 className="font-semibold">{rule.name}</h4>
                    <p className="text-xs text-muted-foreground mt-0.5">{rule.description}</p>
                  </div>
                  <div className="flex gap-1.5 flex-shrink-0">
                    <Button size="sm" variant="ghost"
                      onClick={() => toggleMutation.mutate({ id: rule.id, enabled: !rule.enabled })}
                      className="rounded-xl h-8 w-8 p-0"
                      title={rule.enabled ? "Disable" : "Enable"}
                    >
                      <Activity className={cn("h-3.5 w-3.5", rule.enabled ? "text-green-400" : "text-muted-foreground")} />
                    </Button>
                    <Button size="sm" variant="ghost"
                      onClick={() => deleteMutation.mutate(rule.id)}
                      className="rounded-xl h-8 w-8 p-0 text-destructive hover:bg-destructive/10"
                    >
                      <Trash2 className="h-3.5 w-3.5" />
                    </Button>
                  </div>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-2 text-xs">
                  {[
                    { label: "⚡ Trigger", val: rule.trigger, color: "text-amber-400" },
                    { label: "🔍 Condition", val: rule.condition, color: "text-blue-400" },
                    { label: "🎯 Action", val: rule.action, color: "text-green-400" },
                  ].map(f => (
                    <div key={f.label} className="bg-muted/30 rounded-xl p-2.5">
                      <p className={cn("font-medium mb-1", f.color)}>{f.label}</p>
                      <p className="text-muted-foreground leading-relaxed">{f.val || "—"}</p>
                    </div>
                  ))}
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}

function TesterTab() {
  const { toast } = useToast();
  const [scenario, setScenario] = useState("");
  const [selectedRuleId, setSelectedRuleId] = useState("all");
  const [testing, setTesting] = useState(false);
  const [result, setResult] = useState<RuleTestResult | null>(null);

  const rulesQuery = useQuery<{ rules: GovernanceRule[] }>({
    queryKey: ["/api/governance/rules"],
  });
  const rules = rulesQuery.data?.rules ?? [];

  async function runTest() {
    if (!scenario.trim()) return toast({ title: "Describe a scenario first", variant: "destructive" });
    setTesting(true);
    setResult(null);
    try {
      const r = await fetch("/api/governance/test", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ scenario, ruleId: selectedRuleId === "all" ? null : selectedRuleId }),
      });
      const data = await r.json() as RuleTestResult;
      setResult(data);
      toast({
        title: data.triggered ? "⚠️ Rule triggered!" : "✅ No violations detected",
        description: data.triggered ? `Rule: ${data.ruleName}` : "Scenario passed governance checks.",
      });
    } catch (e: any) {
      toast({ title: "Test failed", description: e.message, variant: "destructive" });
    } finally {
      setTesting(false);
    }
  }

  const EXAMPLE_SCENARIOS = [
    "A sales bot promises a user guaranteed 50% returns on investment",
    "A research bot refuses to provide any information and says it cannot help",
    "A bot outputs personal data of another user in its response",
    "A coding bot generates SQL with a raw string interpolation vulnerability",
  ];

  return (
    <div className="space-y-5">
      <Card className="rounded-2xl border-border/60 p-5 space-y-4">
        <h3 className="font-semibold text-sm text-muted-foreground uppercase tracking-wider">Rule Tester</h3>

        <div className="space-y-1.5">
          <label className="text-xs font-medium text-muted-foreground">Rule to Test Against</label>
          <Select value={selectedRuleId} onValueChange={setSelectedRuleId}>
            <SelectTrigger className="rounded-xl" data-testid="rule-select">
              <SelectValue />
            </SelectTrigger>
            <SelectContent className="rounded-xl">
              <SelectItem value="all" className="rounded-lg">All active rules</SelectItem>
              {rules.filter(r => r.enabled).map(r => (
                <SelectItem key={r.id} value={r.id} className="rounded-lg">{r.name}</SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <div className="space-y-1.5">
          <label className="text-xs font-medium text-muted-foreground">Describe the Scenario</label>
          <Textarea
            value={scenario}
            onChange={e => setScenario(e.target.value)}
            placeholder="Describe a bot behavior or scenario to test against the governance rules…"
            className="rounded-xl min-h-[100px] resize-none"
            data-testid="scenario-input"
          />
        </div>

        <div>
          <p className="text-xs text-muted-foreground mb-2">Quick scenarios:</p>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
            {EXAMPLE_SCENARIOS.map((s, i) => (
              <button
                key={i}
                onClick={() => setScenario(s)}
                className="text-left text-xs p-2.5 rounded-xl border border-border/60 bg-muted/20 hover:bg-muted/40 transition-colors text-muted-foreground hover:text-foreground"
              >
                <ArrowRight className="h-3 w-3 inline mr-1.5 text-primary" />
                {s}
              </button>
            ))}
          </div>
        </div>

        <Button
          onClick={runTest}
          disabled={testing}
          className="w-full rounded-xl h-11 font-semibold gap-2"
          data-testid="run-governance-test"
        >
          {testing ? <Loader2 className="h-4 w-4 animate-spin" /> : <TestTube2 className="h-4 w-4" />}
          {testing ? "Testing scenario…" : "Test Scenario"}
        </Button>
      </Card>

      {result && (
        <Card className={cn(
          "rounded-2xl border p-5 space-y-4",
          result.triggered ? "border-red-500/30 bg-red-950/10" : "border-green-500/30 bg-green-950/10"
        )}>
          <div className="flex items-center gap-3">
            {result.triggered
              ? <AlertCircle className="h-5 w-5 text-red-400 flex-shrink-0" />
              : <CheckCircle2 className="h-5 w-5 text-green-400 flex-shrink-0" />
            }
            <div>
              <h4 className="font-semibold">
                {result.triggered ? "⚠️ Governance Violation Detected" : "✅ Scenario Cleared"}
              </h4>
              {result.triggered && <p className="text-xs text-muted-foreground">Rule: {result.ruleName}</p>}
            </div>
            <Badge variant="outline" className={cn("ml-auto text-xs rounded-lg", SEVERITY_COLORS[result.severity] ?? "")}>
              {result.severity}
            </Badge>
          </div>

          <Separator className="opacity-40" />

          <div className="space-y-3">
            <div>
              <p className="text-xs font-medium text-muted-foreground mb-1">AI Reasoning</p>
              <p className="text-sm leading-relaxed">{result.reasoning}</p>
            </div>
            {result.triggered && (
              <div>
                <p className="text-xs font-medium text-amber-400 mb-1">Suggested Action</p>
                <p className="text-sm leading-relaxed">{result.suggestedAction}</p>
              </div>
            )}
            <p className="text-xs text-muted-foreground flex items-center gap-1">
              <Clock className="h-3 w-3" />
              Tested at {new Date(result.testedAt).toLocaleTimeString()}
            </p>
          </div>
        </Card>
      )}
    </div>
  );
}

export default function GovernancePage() {
  const rulesQuery = useQuery<{ rules: GovernanceRule[] }>({ queryKey: ["/api/governance/rules"] });
  const proposalsQuery = useQuery<{ proposals: Proposal[] }>({ queryKey: ["/api/council/proposals"] });

  const totalRules = rulesQuery.data?.rules?.length ?? 0;
  const activeRules = rulesQuery.data?.rules?.filter(r => r.enabled).length ?? 0;
  const pendingProposals = proposalsQuery.data?.proposals?.filter(p => p.status === "pending").length ?? 0;

  return (
    <AppShell>
      <Seo title="DreamCo Empire OS — Governance" description="Build and test governance rules. Manage council proposals." />

      <div className="buddy-appear space-y-6">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-end md:justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-3xl md:text-4xl">Governance</h2>
              <Badge className="bg-blue-500/20 text-blue-300 border-blue-500/30 text-xs rounded-lg">
                <Scale className="h-3 w-3 mr-1" />
                Council OS
              </Badge>
            </div>
            <p className="mt-2 text-muted-foreground text-sm max-w-xl">
              Write governance rules that define how bots should behave — triggers, conditions, and actions. Test any scenario against your rules and manage council proposals from all 1,051 bots.
            </p>
          </div>
          <div className="flex items-center gap-3">
            {[
              { label: "Active Rules", val: activeRules, icon: Shield, color: "text-green-400" },
              { label: "Total Rules", val: totalRules, icon: BookOpen, color: "text-primary" },
              { label: "Pending Votes", val: pendingProposals, icon: Gavel, color: "text-amber-400" },
            ].map(s => (
              <Card key={s.label} className="rounded-2xl border-border/60 px-4 py-2.5 flex items-center gap-2">
                <s.icon className={cn("h-4 w-4", s.color)} />
                <div>
                  <p className="text-xs text-muted-foreground">{s.label}</p>
                  <p className="text-lg font-bold leading-none">{s.val}</p>
                </div>
              </Card>
            ))}
          </div>
        </div>

        <Separator className="opacity-40" />

        <Tabs defaultValue="council">
          <TabsList className="rounded-2xl bg-muted/40 p-1 h-auto">
            {[
              { val: "council", label: "Council", icon: Users },
              { val: "rules", label: "Rules Builder", icon: Scale },
              { val: "tester", label: "Rule Tester", icon: TestTube2 },
            ].map(({ val, label, icon: Icon }) => (
              <TabsTrigger
                key={val} value={val}
                className="rounded-xl gap-2 px-4 py-2 data-[state=active]:bg-background data-[state=active]:shadow-sm"
                data-testid={`tab-${val}`}
              >
                <Icon className="h-4 w-4" />{label}
                {val === "council" && pendingProposals > 0 && (
                  <Badge className="ml-1 h-5 w-5 p-0 text-[10px] flex items-center justify-center bg-amber-500 text-white border-0 rounded-full">
                    {pendingProposals}
                  </Badge>
                )}
              </TabsTrigger>
            ))}
          </TabsList>

          <TabsContent value="council" className="mt-5"><CouncilTab /></TabsContent>
          <TabsContent value="rules" className="mt-5"><RulesTab /></TabsContent>
          <TabsContent value="tester" className="mt-5"><TesterTab /></TabsContent>
        </Tabs>
      </div>
    </AppShell>
  );
}
