import { useState } from "react";
import { useQuery, useMutation } from "@tanstack/react-query";
import AppShell from "@/components/AppShell";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useToast } from "@/hooks/use-toast";
import { apiRequest } from "@/lib/queryClient";
import {
  GitBranch, RefreshCw, CheckCircle2, XCircle, Clock, Zap, CreditCard,
  Globe, Terminal, TestTube2, Wifi, WifiOff, Play, RotateCcw, Shield,
  ChevronRight, Copy, ExternalLink, AlertTriangle, Activity, Github,
  FlaskConical, Code, DollarSign, Lock, Key, Database,
} from "lucide-react";

const STRIPE_TEST_CARDS = [
  { label: "Visa — Success", number: "4242 4242 4242 4242", expires: "Any future", cvc: "Any 3 digits", result: "✅ Payment succeeds" },
  { label: "Mastercard — Success", number: "5555 5555 5555 4444", expires: "Any future", cvc: "Any 3 digits", result: "✅ Payment succeeds" },
  { label: "Amex — Success", number: "3782 822463 10005", expires: "Any future", cvc: "Any 4 digits", result: "✅ Payment succeeds" },
  { label: "Visa — Declined", number: "4000 0000 0000 0002", expires: "Any future", cvc: "Any 3 digits", result: "❌ Card declined" },
  { label: "Insufficient Funds", number: "4000 0000 0000 9995", expires: "Any future", cvc: "Any 3 digits", result: "❌ Insufficient funds" },
  { label: "3D Secure (Auth Required)", number: "4000 0025 0000 3155", expires: "Any future", cvc: "Any 3 digits", result: "🔐 Requires 3DS auth" },
  { label: "3D Secure — Always Auth", number: "4000 0027 6000 3184", expires: "Any future", cvc: "Any 3 digits", result: "🔐 Always authenticates" },
  { label: "Dispute (Fraudulent)", number: "4000 0000 0000 0259", expires: "Any future", cvc: "Any 3 digits", result: "⚠️ Triggers dispute" },
  { label: "Expired Card", number: "4000 0000 0000 0069", expires: "Any future", cvc: "Any 3 digits", result: "❌ Expired card" },
  { label: "Incorrect CVC", number: "4000 0000 0000 0127", expires: "Any future", cvc: "Any 3 digits", result: "❌ Incorrect CVC" },
];

const FREE_SANDBOX_APIS = [
  { name: "Stripe Test Mode", category: "Payments", url: "https://stripe.com/docs/testing", description: "Full payment sandbox. Use test keys (sk_test_) with the cards above. Zero real money.", tier: "elite", docs: "https://stripe.com/docs/testing" },
  { name: "OpenAI API", category: "AI / LLM", url: "https://platform.openai.com", description: "GPT-4o, embeddings, DALL-E, Whisper, TTS. $5 free credit on new accounts.", tier: "pro", docs: "https://platform.openai.com/docs" },
  { name: "Anthropic Claude", category: "AI / LLM", url: "https://console.anthropic.com", description: "Claude 3.5 Sonnet / Haiku. $5 free credit. Best for long-context and coding.", tier: "pro", docs: "https://docs.anthropic.com" },
  { name: "Groq (Free)", category: "AI / LLM", url: "https://console.groq.com", description: "Llama 3.3, Mixtral, Gemma2 at 6,000 req/day FREE. Fastest inference (750 tok/s).", tier: "free", docs: "https://console.groq.com/docs" },
  { name: "Together AI", category: "AI / LLM", url: "https://api.together.xyz", description: "70+ open-source models. $5 free credit. Llama, Mistral, Qwen, DeepSeek.", tier: "free", docs: "https://docs.together.ai" },
  { name: "HuggingFace Inference", category: "AI / ML", url: "https://api-inference.huggingface.co", description: "500k+ models free via Inference API. Image, text, audio, embeddings.", tier: "free", docs: "https://huggingface.co/docs/api-inference" },
  { name: "Replicate", category: "AI / Media", url: "https://replicate.com", description: "Run Stable Diffusion, Llama, Whisper. Pay-per-run. Free trial credits.", tier: "free", docs: "https://replicate.com/docs" },
  { name: "ElevenLabs", category: "AI / Voice", url: "https://elevenlabs.io", description: "Text-to-speech. 10,000 chars/mo FREE. Voice cloning, 29+ languages.", tier: "free", docs: "https://elevenlabs.io/docs" },
  { name: "AssemblyAI", category: "AI / Voice", url: "https://www.assemblyai.com", description: "Speech-to-text, sentiment analysis, speaker diarization. $50 free credit.", tier: "free", docs: "https://www.assemblyai.com/docs" },
  { name: "SendGrid Sandbox", category: "Email", url: "https://sendgrid.com", description: "Email delivery sandbox mode — no real emails sent. 100/day free in production.", tier: "free", docs: "https://docs.sendgrid.com/for-developers/sending-email/sandbox-mode" },
  { name: "Resend", category: "Email", url: "https://resend.com", description: "Developer-first email API. 3,000 emails/mo FREE. React Email templates.", tier: "free", docs: "https://resend.com/docs" },
  { name: "Twilio Sandbox", category: "SMS / Voice", url: "https://twilio.com/console", description: "SMS/voice sandbox. Send to verified numbers for free. $15 free trial credit.", tier: "free", docs: "https://www.twilio.com/docs/usage/tutorials/how-to-use-your-free-trial-account" },
  { name: "CoinGecko", category: "Crypto / Finance", url: "https://api.coingecko.com/api/v3", description: "Crypto prices, market data, 10,000+ coins. 30 calls/min FREE. No key needed.", tier: "free", docs: "https://docs.coingecko.com" },
  { name: "Alpha Vantage", category: "Stocks / Finance", url: "https://www.alphavantage.co", description: "Stock prices, forex, crypto, indicators. 25 req/day FREE. 500 req/day paid.", tier: "free", docs: "https://www.alphavantage.co/documentation" },
  { name: "NewsAPI", category: "News / Data", url: "https://newsapi.org", description: "100 news sources, 5M articles. 100 req/day FREE. Headlines, everything.", tier: "free", docs: "https://newsapi.org/docs" },
  { name: "OpenWeather", category: "Weather / Data", url: "https://api.openweathermap.org", description: "Weather for 200k+ cities. 60 calls/min FREE. Forecasts, historical data.", tier: "free", docs: "https://openweathermap.org/api" },
  { name: "GitHub API", category: "Developer", url: "https://api.github.com", description: "Repos, issues, PRs, Actions, users. 5,000 req/hr authenticated. No key for public.", tier: "free", docs: "https://docs.github.com/rest" },
  { name: "ReqRes.in", category: "Testing / Mock", url: "https://reqres.in", description: "Hosted fake REST API. Users, login, register. Perfect for frontend testing. 100% free.", tier: "free", docs: "https://reqres.in" },
  { name: "JSONPlaceholder", category: "Testing / Mock", url: "https://jsonplaceholder.typicode.com", description: "Fake REST API — posts, todos, users, albums. No signup. Unlimited free.", tier: "free", docs: "https://jsonplaceholder.typicode.com/guide" },
  { name: "httpbin.org", category: "Testing / HTTP", url: "https://httpbin.org", description: "HTTP request & response inspector. Test headers, auth, status codes, delays.", tier: "free", docs: "https://httpbin.org/#/" },
  { name: "Mockoon", category: "Testing / Local", url: "https://mockoon.com", description: "Local API mocking with GUI. Run any REST/GraphQL endpoint locally. Free & open source.", tier: "free", docs: "https://mockoon.com/docs" },
  { name: "Webhook.site", category: "Webhooks", url: "https://webhook.site", description: "Inspect & debug webhook payloads in real-time. Unique URL, no signup needed.", tier: "free", docs: "https://docs.webhook.site" },
  { name: "Airtable API", category: "Database / No-code", url: "https://airtable.com", description: "Spreadsheet + database API. 1,000 records/base FREE. Perfect for MVP data.", tier: "free", docs: "https://airtable.com/developers/web/api/introduction" },
  { name: "Supabase", category: "Database / Auth", url: "https://supabase.com", description: "Postgres + Auth + Storage + Realtime. 500MB FREE forever. Best OSS Firebase alternative.", tier: "free", docs: "https://supabase.com/docs" },
  { name: "Upstash Redis", category: "Cache / Queue", url: "https://upstash.com", description: "Serverless Redis & Kafka. 10,000 commands/day FREE. Per-request pricing after.", tier: "free", docs: "https://docs.upstash.com" },
  { name: "Posthog", category: "Analytics", url: "https://posthog.com", description: "Product analytics, session recording, feature flags, A/B tests. 1M events/mo FREE.", tier: "free", docs: "https://posthog.com/docs" },
  { name: "Sentry", category: "Error Tracking", url: "https://sentry.io", description: "Error monitoring + performance tracing. 5,000 errors/mo FREE. All languages.", tier: "free", docs: "https://docs.sentry.io" },
  { name: "Cloudinary", category: "Media / Storage", url: "https://cloudinary.com", description: "Image/video upload, transform, optimize, CDN deliver. 25 credits/mo FREE.", tier: "free", docs: "https://cloudinary.com/documentation" },
];

const SANDBOX_TESTS = [
  { id: "stripe-ping", name: "Stripe API Connection", endpoint: "/api/stripe/products", method: "GET", description: "Verify Stripe is connected and products load" },
  { id: "openai-ping", name: "OpenAI Connection", endpoint: "/api/modules/status", method: "GET", description: "Verify OpenAI API key is valid" },
  { id: "bots-load", name: "Bot Fleet Health", endpoint: "/api/bots?limit=5", method: "GET", description: "Load 5 bots from the database" },
  { id: "empire-overview", name: "Empire Overview", endpoint: "/api/empire/overview", method: "GET", description: "Full empire stats: bots, divisions, revenue" },
  { id: "github-status", name: "GitHub Sync Status", endpoint: "/api/github/status", method: "GET", description: "Check GitHub connection and last push time" },
  { id: "conversations", name: "Conversations DB", endpoint: "/api/conversations", method: "GET", description: "Verify database and conversation history" },
  { id: "costs", name: "Cost Tracking", endpoint: "/api/costs/summary", method: "GET", description: "Load cost tracking data" },
  { id: "snapshots", name: "Time Capsule", endpoint: "/api/snapshots", method: "GET", description: "Load system snapshots" },
];

type TestResult = { id: string; status: "idle" | "running" | "pass" | "fail"; responseTime?: number; data?: unknown; error?: string; };

const TIER_COLOR: Record<string, string> = {
  elite: "bg-amber-500/15 text-amber-400 border-amber-500/30",
  pro: "bg-blue-500/15 text-blue-400 border-blue-500/30",
  free: "bg-green-500/15 text-green-400 border-green-500/30",
};

export default function SandboxPage() {
  const { toast } = useToast();
  const [testResults, setTestResults] = useState<Record<string, TestResult>>({});
  const [runningAll, setRunningAll] = useState(false);
  const [copiedCard, setCopiedCard] = useState<string | null>(null);
  const [apiFilter, setApiFilter] = useState("All");

  const githubStatus = useQuery<any>({
    queryKey: ["/api/github/status"],
    refetchInterval: 30000,
  });

  const syncMutation = useMutation({
    mutationFn: () => apiRequest("POST", "/api/github/sync", {}),
    onSuccess: (data: any) => {
      setLastSyncResult(data);
      toast({ title: "✅ GitHub Synced", description: `Pushed ${data?.sha?.slice(0,7) || "latest"} — ${data?.message || "all commits pushed"}` });
      githubStatus.refetch();
    },
    onError: () => toast({ title: "Sync failed", description: "Check GITHUB_TOKEN in environment secrets.", variant: "destructive" }),
  });

  const runTest = async (test: typeof SANDBOX_TESTS[number]) => {
    setTestResults(prev => ({ ...prev, [test.id]: { id: test.id, status: "running" } }));
    const start = Date.now();
    try {
      const res = await fetch(test.endpoint);
      const data = await res.json();
      setTestResults(prev => ({ ...prev, [test.id]: { id: test.id, status: res.ok ? "pass" : "fail", responseTime: Date.now() - start, data } }));
    } catch (e: any) {
      setTestResults(prev => ({ ...prev, [test.id]: { id: test.id, status: "fail", responseTime: Date.now() - start, error: e.message } }));
    }
  };

  const runAllTests = async () => {
    setRunningAll(true);
    for (const test of SANDBOX_TESTS) {
      await runTest(test);
    }
    setRunningAll(false);
  };

  const copyCard = (number: string) => {
    navigator.clipboard.writeText(number.replace(/\s/g, ""));
    setCopiedCard(number);
    setTimeout(() => setCopiedCard(null), 2000);
  };

  const cats = ["All", ...Array.from(new Set(FREE_SANDBOX_APIS.map(a => a.category.split(" / ")[0])))];
  const filteredApis = apiFilter === "All" ? FREE_SANDBOX_APIS : FREE_SANDBOX_APIS.filter(a => a.category.startsWith(apiFilter));

  const [lastSyncResult, setLastSyncResult] = useState<any>(null);
  const githubData = githubStatus.data as any;
  const lastPush = lastSyncResult?.lastSync || githubData?.repo?.updatedAt;
  const isSynced = githubData?.connected === true || lastSyncResult?.success === true;

  const passCount = Object.values(testResults).filter(r => r.status === "pass").length;
  const failCount = Object.values(testResults).filter(r => r.status === "fail").length;
  const totalRan = passCount + failCount;

  return (
    <AppShell>
      <div className="space-y-6 pb-10">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold tracking-tight flex items-center gap-2">
              <FlaskConical className="h-6 w-6 text-primary" />
              Sandbox Factory
            </h1>
            <p className="text-muted-foreground text-sm mt-1">
              Test APIs, inspect payloads, run live health checks — and keep GitHub in sync
            </p>
          </div>
          <div className="flex items-center gap-2">
            {isSynced ? (
              <Badge variant="outline" className="bg-green-500/10 text-green-400 border-green-500/30 gap-1">
                <Wifi className="h-3 w-3" /> GitHub Live
              </Badge>
            ) : (
              <Badge variant="outline" className="bg-amber-500/10 text-amber-400 border-amber-500/30 gap-1">
                <WifiOff className="h-3 w-3" /> GitHub Offline
              </Badge>
            )}
            <Button size="sm" variant="outline" onClick={() => syncMutation.mutate()} disabled={syncMutation.isPending} data-testid="button-sync-github">
              {syncMutation.isPending ? <RefreshCw className="h-3.5 w-3.5 animate-spin mr-1" /> : <Github className="h-3.5 w-3.5 mr-1" />}
              Sync Now
            </Button>
          </div>
        </div>

        <Tabs defaultValue="github">
          <TabsList className="w-full flex flex-wrap h-auto gap-1 p-1" data-testid="tabs-sandbox">
            <TabsTrigger value="github" data-testid="tab-github"><Github className="h-3.5 w-3.5 mr-1" />GitHub Sync</TabsTrigger>
            <TabsTrigger value="stripe" data-testid="tab-stripe"><CreditCard className="h-3.5 w-3.5 mr-1" />Stripe Sandbox</TabsTrigger>
            <TabsTrigger value="tests" data-testid="tab-tests"><TestTube2 className="h-3.5 w-3.5 mr-1" />Live Tests</TabsTrigger>
            <TabsTrigger value="apis" data-testid="tab-apis"><Globe className="h-3.5 w-3.5 mr-1" />Free Sandbox APIs</TabsTrigger>
          </TabsList>

          {/* ── GITHUB SYNC TAB ── */}
          <TabsContent value="github" className="space-y-4 mt-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <Card className="border-border/50 bg-card/50">
                <CardContent className="pt-5">
                  <div className="flex items-center gap-3">
                    <div className="h-10 w-10 rounded-xl bg-green-500/10 flex items-center justify-center">
                      <Github className="h-5 w-5 text-green-400" />
                    </div>
                    <div>
                      <p className="text-xs text-muted-foreground">Repository</p>
                      <p className="font-semibold text-sm">DreamCo-Technologies/Dreamcobots</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
              <Card className="border-border/50 bg-card/50">
                <CardContent className="pt-5">
                  <div className="flex items-center gap-3">
                    <div className="h-10 w-10 rounded-xl bg-blue-500/10 flex items-center justify-center">
                      <GitBranch className="h-5 w-5 text-blue-400" />
                    </div>
                    <div>
                      <p className="text-xs text-muted-foreground">Branch</p>
                      <p className="font-semibold text-sm">main</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
              <Card className="border-border/50 bg-card/50">
                <CardContent className="pt-5">
                  <div className="flex items-center gap-3">
                    <div className="h-10 w-10 rounded-xl bg-purple-500/10 flex items-center justify-center">
                      <Clock className="h-5 w-5 text-purple-400" />
                    </div>
                    <div>
                      <p className="text-xs text-muted-foreground">Last Synced</p>
                      <p className="font-semibold text-sm">{lastPush ? new Date(lastPush).toLocaleString() : "Syncing..."}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>

            <Card className="border-border/50">
              <CardHeader className="pb-3">
                <CardTitle className="text-base flex items-center gap-2">
                  <Activity className="h-4 w-4 text-primary" />
                  Sync Status
                </CardTitle>
                <CardDescription>Push all commits from this DreamCo to GitHub instantly</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                {githubStatus.isLoading ? (
                  <div className="flex items-center gap-2 text-sm text-muted-foreground">
                    <RefreshCw className="h-4 w-4 animate-spin" /> Checking GitHub connection...
                  </div>
                ) : githubData ? (
                  <div className="space-y-3">
                    <div className="flex items-center gap-2">
                      {isSynced ? <CheckCircle2 className="h-5 w-5 text-green-400" /> : <AlertTriangle className="h-5 w-5 text-amber-400" />}
                      <span className="text-sm font-medium">{isSynced ? "GitHub connected and in sync" : "GitHub connection needs verification"}</span>
                    </div>
                    {githubData.sha && (
                      <div className="font-mono text-xs bg-muted/40 rounded-lg p-3 space-y-1">
                        <div className="flex justify-between"><span className="text-muted-foreground">Remote SHA</span><span>{String(githubData.sha).slice(0,7)}</span></div>
                        {githubData.message && <div className="flex justify-between"><span className="text-muted-foreground">Last commit</span><span className="truncate max-w-[200px]">{githubData.message}</span></div>}
                      </div>
                    )}
                  </div>
                ) : (
                  <p className="text-sm text-muted-foreground">Could not fetch GitHub status</p>
                )}

                <div className="flex flex-wrap gap-2 pt-2">
                  <Button onClick={() => syncMutation.mutate()} disabled={syncMutation.isPending} data-testid="button-force-sync">
                    {syncMutation.isPending ? <RefreshCw className="h-4 w-4 animate-spin mr-2" /> : <Github className="h-4 w-4 mr-2" />}
                    {syncMutation.isPending ? "Pushing..." : "Force Push to GitHub"}
                  </Button>
                  <Button variant="outline" onClick={() => githubStatus.refetch()} data-testid="button-refresh-status">
                    <RefreshCw className="h-4 w-4 mr-2" />Refresh Status
                  </Button>
                  <Button variant="ghost" size="sm" onClick={() => window.open("https://github.com/DreamCo-Technologies/Dreamcobots", "_blank")} data-testid="button-open-github">
                    <ExternalLink className="h-4 w-4 mr-2" />Open on GitHub
                  </Button>
                </div>
              </CardContent>
            </Card>

            <Card className="border-border/50">
              <CardHeader className="pb-3">
                <CardTitle className="text-base flex items-center gap-2">
                  <Terminal className="h-4 w-4 text-primary" />
                  Auto-Sync Instructions
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3 text-sm">
                  <p className="text-muted-foreground">Every change made in the AI agent is automatically committed. To keep GitHub in sync, click <strong>Force Push</strong> above or run this from the Shell tab:</p>
                  <div className="bg-muted/40 rounded-lg p-3 font-mono text-xs">
                    bash scripts/sync-github.sh
                  </div>
                  <p className="text-muted-foreground text-xs">The sync script reads your <code>GITHUB_TOKEN</code> secret at runtime — it never stores the token in any file.</p>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* ── STRIPE SANDBOX TAB ── */}
          <TabsContent value="stripe" className="space-y-4 mt-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Card className="border-amber-500/20 bg-amber-500/5">
                <CardContent className="pt-5">
                  <div className="flex items-start gap-3">
                    <Shield className="h-5 w-5 text-amber-400 mt-0.5 shrink-0" />
                    <div className="space-y-1">
                      <p className="font-semibold text-sm">Test Mode Active</p>
                      <p className="text-xs text-muted-foreground">All payments use test keys (sk_test_). No real money is charged. Use the cards below to simulate any payment scenario.</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
              <Card className="border-border/50 bg-card/50">
                <CardContent className="pt-5">
                  <div className="flex items-start gap-3">
                    <Key className="h-5 w-5 text-blue-400 mt-0.5 shrink-0" />
                    <div className="space-y-1">
                      <p className="font-semibold text-sm">API Keys Setup</p>
                      <p className="text-xs text-muted-foreground">Add <code className="bg-muted px-1 rounded">STRIPE_SECRET_KEY</code> and <code className="bg-muted px-1 rounded">STRIPE_PUBLISHABLE_KEY</code> to environment secrets to activate checkout.</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>

            <Card className="border-border/50">
              <CardHeader className="pb-3">
                <CardTitle className="text-base flex items-center gap-2">
                  <CreditCard className="h-4 w-4 text-primary" />
                  Test Cards — Click to Copy Card Number
                </CardTitle>
                <CardDescription>Use any future expiry date (e.g. 12/34) and any CVC</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                  {STRIPE_TEST_CARDS.map((card) => (
                    <button
                      key={card.number}
                      data-testid={`card-stripe-${card.number.replace(/\s/g, "").slice(-4)}`}
                      onClick={() => copyCard(card.number)}
                      className="text-left p-3 rounded-lg border border-border/50 hover:border-primary/50 hover:bg-muted/30 transition-all group"
                    >
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-xs font-medium text-foreground">{card.label}</span>
                        <span className="text-xs text-muted-foreground flex items-center gap-1">
                          {copiedCard === card.number ? <CheckCircle2 className="h-3 w-3 text-green-400" /> : <Copy className="h-3 w-3 opacity-0 group-hover:opacity-100" />}
                        </span>
                      </div>
                      <div className="font-mono text-xs text-muted-foreground">{card.number}</div>
                      <div className="text-xs mt-1">{card.result}</div>
                    </button>
                  ))}
                </div>
              </CardContent>
            </Card>

            <Card className="border-border/50">
              <CardHeader className="pb-3">
                <CardTitle className="text-base flex items-center gap-2">
                  <Zap className="h-4 w-4 text-primary" />
                  Stripe Webhook Testing
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3 text-sm">
                <p className="text-muted-foreground">Use the Stripe CLI to forward webhook events to your local server:</p>
                <div className="bg-muted/40 rounded-lg p-3 font-mono text-xs space-y-2">
                  <div># Install Stripe CLI (Mac)</div>
                  <div className="text-green-400">brew install stripe/stripe-cli/stripe</div>
                  <div className="mt-2"># Login and forward webhooks</div>
                  <div className="text-green-400">stripe login</div>
                  <div className="text-green-400">stripe listen --forward-to localhost:5000/api/stripe/webhook</div>
                  <div className="mt-2"># Trigger test events</div>
                  <div className="text-green-400">stripe trigger payment_intent.succeeded</div>
                  <div className="text-green-400">stripe trigger customer.subscription.created</div>
                </div>
                <div className="flex gap-2 pt-1">
                  <Button variant="outline" size="sm" onClick={() => window.open("https://stripe.com/docs/stripe-cli", "_blank")} data-testid="button-stripe-cli-docs">
                    <ExternalLink className="h-3.5 w-3.5 mr-1" />Stripe CLI Docs
                  </Button>
                  <Button variant="outline" size="sm" onClick={() => window.open("https://dashboard.stripe.com/test/webhooks", "_blank")} data-testid="button-stripe-dashboard">
                    <ExternalLink className="h-3.5 w-3.5 mr-1" />Test Webhooks Dashboard
                  </Button>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* ── LIVE TESTS TAB ── */}
          <TabsContent value="tests" className="space-y-4 mt-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                {totalRan > 0 && (
                  <>
                    <Badge variant="outline" className="bg-green-500/10 text-green-400 border-green-500/30">{passCount} passed</Badge>
                    {failCount > 0 && <Badge variant="outline" className="bg-red-500/10 text-red-400 border-red-500/30">{failCount} failed</Badge>}
                  </>
                )}
              </div>
              <div className="flex gap-2">
                <Button variant="outline" size="sm" onClick={() => setTestResults({})} data-testid="button-reset-tests">
                  <RotateCcw className="h-3.5 w-3.5 mr-1" />Reset
                </Button>
                <Button size="sm" onClick={runAllTests} disabled={runningAll} data-testid="button-run-all-tests">
                  {runningAll ? <RefreshCw className="h-3.5 w-3.5 animate-spin mr-1" /> : <Play className="h-3.5 w-3.5 mr-1" />}
                  {runningAll ? "Running..." : "Run All Tests"}
                </Button>
              </div>
            </div>

            <div className="space-y-2">
              {SANDBOX_TESTS.map((test) => {
                const result = testResults[test.id];
                return (
                  <Card key={test.id} className="border-border/50 hover:border-border transition-colors" data-testid={`card-test-${test.id}`}>
                    <CardContent className="py-3 px-4">
                      <div className="flex items-center gap-3">
                        <div className="shrink-0">
                          {!result || result.status === "idle" ? <div className="h-5 w-5 rounded-full border-2 border-muted-foreground/30" /> :
                           result.status === "running" ? <RefreshCw className="h-5 w-5 text-blue-400 animate-spin" /> :
                           result.status === "pass" ? <CheckCircle2 className="h-5 w-5 text-green-400" /> :
                           <XCircle className="h-5 w-5 text-red-400" />}
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2">
                            <span className="text-sm font-medium">{test.name}</span>
                            {result?.responseTime && <span className="text-xs text-muted-foreground">{result.responseTime}ms</span>}
                          </div>
                          <div className="text-xs text-muted-foreground font-mono">{test.method} {test.endpoint}</div>
                          {result?.error && <div className="text-xs text-red-400 mt-1">{result.error}</div>}
                        </div>
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={() => runTest(test)}
                          disabled={result?.status === "running"}
                          data-testid={`button-run-test-${test.id}`}
                        >
                          <Play className="h-3.5 w-3.5" />
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                );
              })}
            </div>
          </TabsContent>

          {/* ── FREE SANDBOX APIS TAB ── */}
          <TabsContent value="apis" className="space-y-4 mt-4">
            <div className="flex items-center gap-2 flex-wrap">
              {cats.map(cat => (
                <Button
                  key={cat}
                  size="sm"
                  variant={apiFilter === cat ? "default" : "outline"}
                  onClick={() => setApiFilter(cat)}
                  data-testid={`filter-api-${cat.toLowerCase().replace(/\s/g, "-")}`}
                >
                  {cat}
                </Button>
              ))}
              <Badge variant="outline" className="ml-auto">{filteredApis.length} APIs</Badge>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-3">
              {filteredApis.map((api) => (
                <Card key={api.name} className="border-border/50 hover:border-primary/30 transition-colors group" data-testid={`card-api-${api.name.toLowerCase().replace(/\s/g, "-")}`}>
                  <CardContent className="pt-4 pb-4">
                    <div className="flex items-start justify-between gap-2 mb-2">
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 flex-wrap">
                          <span className="font-semibold text-sm">{api.name}</span>
                          <Badge variant="outline" className={`text-xs ${TIER_COLOR[api.tier]}`}>{api.tier}</Badge>
                        </div>
                        <span className="text-xs text-muted-foreground">{api.category}</span>
                      </div>
                      <Button
                        size="sm"
                        variant="ghost"
                        className="h-7 w-7 p-0 opacity-0 group-hover:opacity-100"
                        onClick={() => window.open(api.docs, "_blank")}
                        data-testid={`button-api-docs-${api.name.toLowerCase().replace(/\s/g, "-")}`}
                      >
                        <ExternalLink className="h-3.5 w-3.5" />
                      </Button>
                    </div>
                    <p className="text-xs text-muted-foreground leading-relaxed">{api.description}</p>
                    <div className="mt-3">
                      <Button
                        size="sm"
                        variant="outline"
                        className="h-7 text-xs w-full"
                        onClick={() => window.open(api.docs, "_blank")}
                        data-testid={`button-open-api-${api.name.toLowerCase().replace(/\s/g, "-")}`}
                      >
                        View Docs <ChevronRight className="h-3 w-3 ml-1" />
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </AppShell>
  );
}
