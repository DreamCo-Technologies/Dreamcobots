import { useState } from "react";
import { useLocation } from "wouter";
import Seo from "@/components/Seo";
import AppShell from "@/components/AppShell";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { ScrollArea } from "@/components/ui/scroll-area";
import { useToast } from "@/hooks/use-toast";
import { useCreateConversation } from "@/hooks/use-conversations";
import { useQuery } from "@tanstack/react-query";
import { cn } from "@/lib/utils";
import {
  BrainCircuit, Code2, Zap, Map, Hammer, GraduationCap, Bug, ShieldCheck,
  Github, Search, Mic, ImageIcon, Globe, Users, Database, Terminal,
  GitPullRequest, Rocket, RefreshCw, CheckCircle2, Lock, Layers,
  Star, Sparkles, Send, ExternalLink, Copy, BookOpen, BarChart3,
  FileCode2, Cpu, ArrowRight, Activity, AlertCircle, ChevronRight,
} from "lucide-react";

type BuddyMode = "plan" | "build" | "execute" | "teach" | "vibe" | "agent" | "debug" | "security";

const MODES: { id: BuddyMode; label: string; icon: typeof Map; color: string; bg: string; badge?: string; desc: string; prompts: string[] }[] = [
  {
    id: "plan", label: "Plan", icon: Map, color: "text-blue-400",
    bg: "bg-blue-500/10 border-blue-500/30 hover:border-blue-400/60",
    desc: "Strategy & architecture",
    prompts: [
      "Design a full-stack SaaS architecture with auth, billing, and APIs.",
      "Plan a 90-day coding roadmap to ship my product.",
      "Create a technical spec for my next project.",
      "Map out the best tech stack for my use case.",
    ],
  },
  {
    id: "build", label: "Build", icon: Hammer, color: "text-amber-400",
    bg: "bg-amber-500/10 border-amber-500/30 hover:border-amber-400/60",
    desc: "Code & implement",
    prompts: [
      "Build a complete REST API with auth, rate limiting, and Swagger docs.",
      "Create a React dashboard with real-time data and dark mode.",
      "Implement a payment system with Stripe subscriptions and webhooks.",
      "Build a WebSocket chat system with rooms and message history.",
    ],
  },
  {
    id: "vibe", label: "Vibe Code", icon: Code2, color: "text-cyan-400",
    bg: "bg-cyan-500/10 border-cyan-500/30 hover:border-cyan-400/60",
    desc: "Full projects from one prompt",
    prompts: [
      "Vibe code a full SaaS dashboard with auth, billing, and analytics.",
      "Build me a complete browser game with leaderboard and sound.",
      "Generate a full React + TypeScript todo app with cloud sync.",
      "Create a real-time chat app with WebSockets and voice messages.",
    ],
  },
  {
    id: "agent", label: "Agent", icon: BrainCircuit, color: "text-violet-400",
    bg: "bg-violet-500/10 border-violet-500/30 hover:border-violet-400/60",
    badge: "NEW",
    desc: "Autonomous Plan → Execute → Ship",
    prompts: [
      "Autonomously build a full Stripe payment integration with webhooks.",
      "Plan and execute a complete OAuth 2.0 + PKCE auth system.",
      "Build and ship a complete REST API with tests and deployment config.",
      "Design and implement a multi-tenant SaaS with role-based access.",
    ],
  },
  {
    id: "debug", label: "Debug", icon: Bug, color: "text-red-400",
    bg: "bg-red-500/10 border-red-500/30 hover:border-red-400/60",
    badge: "NEW",
    desc: "Root-cause → fix → prevent",
    prompts: [
      "Debug this error: [paste your error message and stack trace here]",
      "My code runs but gives wrong output — trace the exact failure point.",
      "Find all bugs in this function and rewrite it: [paste code]",
      "My API returns 500 in production but works locally — diagnose it.",
    ],
  },
  {
    id: "security", label: "Security", icon: ShieldCheck, color: "text-emerald-400",
    bg: "bg-emerald-500/10 border-emerald-500/30 hover:border-emerald-400/60",
    badge: "NEW",
    desc: "SAST · OWASP · Zero-trust",
    prompts: [
      "Scan this code for SQL injection, XSS, and auth bypass: [paste code]",
      "Audit my Express.js auth flow for OWASP Top 10 issues.",
      "Check this env config for hardcoded secrets and insecure defaults.",
      "Generate a zero-trust security architecture for my SaaS.",
    ],
  },
  {
    id: "execute", label: "Execute", icon: Zap, color: "text-green-400",
    bg: "bg-green-500/10 border-green-500/30 hover:border-green-400/60",
    desc: "Take action & ship",
    prompts: [
      "Write unit and integration tests for my codebase.",
      "Generate a CI/CD pipeline for GitHub Actions.",
      "Create Docker and Kubernetes configs for my app.",
      "Write a complete README with badges, setup, and API docs.",
    ],
  },
  {
    id: "teach", label: "Teach", icon: GraduationCap, color: "text-purple-400",
    bg: "bg-purple-500/10 border-purple-500/30 hover:border-purple-400/60",
    desc: "Learn any library or concept",
    prompts: [
      "Teach me TypeScript generics with real-world examples.",
      "Explain React Query vs SWR — when to use which.",
      "Walk me through building a production auth system from scratch.",
      "Show me the top 10 patterns every senior engineer should know.",
    ],
  },
];

const GITHUB_CAPABILITIES = [
  { cap: "Create & manage repositories", done: true },
  { cap: "Open, review, and merge pull requests", done: true },
  { cap: "Create issues and project boards", done: true },
  { cap: "Browse and fork open-source projects", done: true },
  { cap: "Search trending repos by topic", done: true },
  { cap: "Clone & analyze any public repo", done: true },
  { cap: "Generate GitHub Actions workflows", done: true },
  { cap: "Write commit messages & changelogs", done: true },
  { cap: "Code review with inline suggestions", done: true },
  { cap: "Auto-fix and push corrected code", done: false },
  { cap: "Manage GitHub Secrets & CI vars", done: false },
  { cap: "Deploy via GitHub Pages / Releases", done: false },
];

const SUPERPOWERS = [
  { name: "GitHub Intelligence", icon: Github, color: "text-gray-400", desc: "Trending repos, code analysis, PR generation", status: "live" },
  { name: "Web Search", icon: Search, color: "text-blue-400", desc: "Real-time web results for any query", status: "live" },
  { name: "Code Execution", icon: Terminal, color: "text-green-400", desc: "Run and test code in a sandboxed environment", status: "live" },
  { name: "Security Scan", icon: Lock, color: "text-red-400", desc: "SAST, OWASP Top 10, secret detection", status: "live" },
  { name: "PR Generator", icon: GitPullRequest, color: "text-violet-400", desc: "Generate full pull requests with diffs", status: "live" },
  { name: "Image Generation", icon: ImageIcon, color: "text-pink-400", desc: "Generate images from code descriptions", status: "needs-key" },
  { name: "Voice Cloning", icon: Mic, color: "text-orange-400", desc: "Text-to-speech with custom voices", status: "needs-key" },
  { name: "Book Study", icon: BookOpen, color: "text-amber-400", desc: "Read and summarize technical books", status: "live" },
  { name: "Agent Pipeline", icon: BrainCircuit, color: "text-cyan-400", desc: "Multi-step autonomous task execution", status: "live" },
  { name: "Deep Debug", icon: Bug, color: "text-red-400", desc: "Root-cause analysis with fix suggestions", status: "live" },
  { name: "System Architect", icon: Layers, color: "text-indigo-400", desc: "Full system design and architecture", status: "live" },
  { name: "Code Translator", icon: RefreshCw, color: "text-teal-400", desc: "Convert between any programming languages", status: "live" },
  { name: "Deploy Config", icon: Rocket, color: "text-emerald-400", desc: "Docker, K8s, CI/CD, and cloud configs", status: "live" },
  { name: "Council Governance", icon: Users, color: "text-purple-400", desc: "Multi-model consensus for complex decisions", status: "live" },
  { name: "Memory System", icon: Database, color: "text-slate-400", desc: "Persistent context across sessions", status: "live" },
  { name: "Competitive Intel", icon: BarChart3, color: "text-orange-400", desc: "Analyze competitors and market trends", status: "live" },
];

export default function BuddyPage() {
  const { toast } = useToast();
  const [, setLocation] = useLocation();
  const [mode, setMode] = useState<BuddyMode>("build");
  const [prompt, setPrompt] = useState("");
  const [activeTab, setActiveTab] = useState<"chat" | "github" | "powers">("chat");
  const createConversation = useCreateConversation();

  const selectedMode = MODES.find(m => m.id === mode)!;

  const { data: features } = useQuery<{ features: any[] }>({ queryKey: ["/api/buddy/features"] });

  async function startChat(text?: string) {
    const msg = text ?? prompt.trim();
    if (!msg) {
      toast({ title: "Enter a message first", variant: "destructive" });
      return;
    }
    try {
      const conv = await createConversation.mutateAsync({ title: msg.slice(0, 60) } as any);
      setLocation(`/c/${conv.id}?bot=buddy-bot&mode=${mode}&prompt=${encodeURIComponent(msg)}`);
    } catch (e: any) {
      toast({ title: "Couldn't start chat", description: e?.message, variant: "destructive" });
    }
  }

  return (
    <AppShell selectedBotSlug="buddy-bot">
      <Seo title="Buddy Bot — Master Coder | DreamCo Empire OS" description="Buddy Bot: your all-in-one coding AI. GitHub, debugging, security, and 500+ libraries." />

      <div className="flex flex-col h-full">
        {/* Header */}
        <div className="px-5 pt-6 pb-5 md:px-8 md:pt-8 md:pb-6 border-b border-border/60">
          <div className="flex flex-wrap items-start justify-between gap-4">
            <div className="flex items-center gap-4">
              <div className="h-14 w-14 rounded-2xl bg-gradient-to-br from-primary/30 via-accent/20 to-transparent border border-primary/40 flex items-center justify-center shadow-lg shadow-primary/20">
                <BrainCircuit className="h-7 w-7 text-primary" />
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <h1 className="text-2xl md:text-3xl" data-testid="text-buddy-title">Buddy Bot</h1>
                  <Badge className="bg-primary/15 text-primary border-primary/30 rounded-full font-mono text-xs">ELITE</Badge>
                  <Badge variant="secondary" className="rounded-full text-xs">
                    <span className="h-1.5 w-1.5 rounded-full bg-green-500 mr-1.5" />
                    Online
                  </Badge>
                </div>
                <p className="text-sm text-muted-foreground mt-1">Master coder · 500+ libraries · GitHub-level intelligence · Full autonomy</p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Button variant="outline" size="sm" onClick={() => { navigator.clipboard.writeText("Buddy Bot — Master Coder | buddy-bot | DreamCo Empire OS"); toast({ title: "Buddy info copied" }); }} data-testid="button-copy-buddy-info">
                <Copy className="h-3.5 w-3.5 mr-1.5" /> Copy Info
              </Button>
              <Button size="sm" onClick={() => startChat()} disabled={!prompt.trim()} data-testid="button-start-buddy-chat">
                <Sparkles className="h-3.5 w-3.5 mr-1.5" /> Start Chat
              </Button>
            </div>
          </div>

          {/* Stats row */}
          <div className="mt-5 flex flex-wrap gap-4">
            {[
              { label: "Libraries", value: "500+" },
              { label: "Languages", value: "50+" },
              { label: "Frameworks", value: "200+" },
              { label: "Capabilities", value: `${SUPERPOWERS.length}` },
              { label: "GitHub Features", value: `${GITHUB_CAPABILITIES.filter(g => g.done).length}/${GITHUB_CAPABILITIES.length}` },
            ].map(s => (
              <div key={s.label} className="flex items-center gap-2 rounded-xl border border-border/60 bg-card/60 px-3 py-2">
                <span className="text-base font-bold text-primary">{s.value}</span>
                <span className="text-xs text-muted-foreground">{s.label}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="flex-1 overflow-auto p-5 md:p-8 space-y-6">
          {/* Tab switcher */}
          <div className="flex gap-2 border-b border-border/60 pb-4">
            {(["chat", "github", "powers"] as const).map(tab => (
              <Button
                key={tab}
                variant={activeTab === tab ? "default" : "outline"}
                size="sm"
                onClick={() => setActiveTab(tab)}
                data-testid={`tab-buddy-${tab}`}
              >
                {tab === "chat" && <Send className="h-3.5 w-3.5 mr-1.5" />}
                {tab === "github" && <Github className="h-3.5 w-3.5 mr-1.5" />}
                {tab === "powers" && <Zap className="h-3.5 w-3.5 mr-1.5" />}
                {tab === "chat" ? "Chat with Buddy" : tab === "github" ? "GitHub Capabilities" : "Superpowers"}
              </Button>
            ))}
          </div>

          {/* CHAT TAB */}
          {activeTab === "chat" && (
            <div className="space-y-6">
              {/* Mode selector */}
              <div>
                <p className="text-sm font-medium text-muted-foreground mb-3">Select Mode</p>
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
                  {MODES.map(m => {
                    const Icon = m.icon;
                    return (
                      <button
                        key={m.id}
                        onClick={() => setMode(m.id)}
                        className={cn(
                          "flex flex-col items-start gap-1 rounded-xl border p-3 text-left transition-all",
                          mode === m.id ? m.bg + " ring-2 ring-primary/30" : "border-border/60 bg-card/60 hover:bg-card"
                        )}
                        data-testid={`mode-buddy-${m.id}`}
                      >
                        <div className="flex items-center gap-2 w-full">
                          <Icon className={cn("h-4 w-4", m.color)} />
                          <span className="text-sm font-medium">{m.label}</span>
                          {m.badge && <Badge className="ml-auto text-[10px] py-0 px-1.5 rounded-md">{m.badge}</Badge>}
                        </div>
                        <span className="text-[11px] text-muted-foreground">{m.desc}</span>
                      </button>
                    );
                  })}
                </div>
              </div>

              {/* Prompt area */}
              <div className="space-y-3">
                <p className="text-sm font-medium text-muted-foreground">Tell Buddy what to build</p>
                <Textarea
                  value={prompt}
                  onChange={e => setPrompt(e.target.value)}
                  placeholder={selectedMode.prompts[0]}
                  rows={4}
                  className="resize-none rounded-xl"
                  onKeyDown={e => { if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) startChat(); }}
                  data-testid="input-buddy-prompt"
                />
                <div className="flex items-center justify-between">
                  <span className="text-xs text-muted-foreground">Cmd+Enter to send</span>
                  <Button onClick={() => startChat()} disabled={!prompt.trim() || createConversation.isPending} data-testid="button-send-buddy-prompt">
                    {createConversation.isPending ? "Starting..." : <><Send className="h-4 w-4 mr-2" /> Send to Buddy</>}
                  </Button>
                </div>
              </div>

              {/* Quick prompts */}
              <div>
                <p className="text-sm font-medium text-muted-foreground mb-3">Quick prompts for {selectedMode.label} mode</p>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                  {selectedMode.prompts.map((p, i) => (
                    <button
                      key={i}
                      onClick={() => startChat(p)}
                      className="text-left text-sm rounded-xl border border-border/60 bg-card/60 hover:bg-card hover:border-border px-4 py-3 transition-all flex items-start gap-2"
                      data-testid={`prompt-buddy-${mode}-${i}`}
                    >
                      <ChevronRight className="h-3.5 w-3.5 mt-0.5 text-muted-foreground flex-shrink-0" />
                      {p}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* GITHUB TAB */}
          {activeTab === "github" && (
            <div className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Github className="h-5 w-5" />
                    GitHub Capabilities
                    <Badge variant="secondary" className="ml-auto">{GITHUB_CAPABILITIES.filter(g => g.done).length} live</Badge>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    {GITHUB_CAPABILITIES.map((c, i) => (
                      <div key={i} className={cn("flex items-center gap-3 rounded-xl border px-3 py-2.5", c.done ? "border-green-500/30 bg-green-500/5" : "border-border/60 bg-card/40")}>
                        {c.done
                          ? <CheckCircle2 className="h-4 w-4 text-green-500 flex-shrink-0" />
                          : <AlertCircle className="h-4 w-4 text-muted-foreground flex-shrink-0" />}
                        <span className="text-sm">{c.cap}</span>
                        {!c.done && <Badge variant="outline" className="ml-auto text-[10px]">Soon</Badge>}
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <Card>
                  <CardHeader><CardTitle className="text-base">Quick GitHub Actions</CardTitle></CardHeader>
                  <CardContent className="space-y-2">
                    {[
                      "Search trending repos for artificial-intelligence",
                      "Analyze an open source project for me",
                      "Generate a GitHub Actions CI/CD workflow",
                      "Write a professional pull request description",
                      "Create a GitHub issue template for bug reports",
                      "Help me fork and contribute to a project",
                    ].map((a, i) => (
                      <Button key={i} variant="outline" size="sm" className="w-full justify-start text-left h-auto py-2 text-xs" onClick={() => startChat(a)} data-testid={`github-action-${i}`}>
                        <ArrowRight className="h-3 w-3 mr-2 flex-shrink-0" />{a}
                      </Button>
                    ))}
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader><CardTitle className="text-base">Open Source Testing</CardTitle></CardHeader>
                  <CardContent className="space-y-2">
                    <p className="text-xs text-muted-foreground mb-3">Test, explore, and contribute to any public project</p>
                    {[
                      "Clone and run a GitHub project for me",
                      "Explain how this open source project works",
                      "Find security vulnerabilities in this repo",
                      "Compare this project to its competitors",
                      "Help me contribute to an open source project",
                      "Generate tests for an open source library",
                    ].map((a, i) => (
                      <Button key={i} variant="outline" size="sm" className="w-full justify-start text-left h-auto py-2 text-xs" onClick={() => startChat(a)} data-testid={`oss-action-${i}`}>
                        <ArrowRight className="h-3 w-3 mr-2 flex-shrink-0" />{a}
                      </Button>
                    ))}
                  </CardContent>
                </Card>
              </div>
            </div>
          )}

          {/* POWERS TAB */}
          {activeTab === "powers" && (
            <div className="space-y-4">
              <p className="text-sm text-muted-foreground">All Buddy capabilities — click any to launch a chat</p>
              <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-4">
                {SUPERPOWERS.map((sp) => {
                  const Icon = sp.icon;
                  return (
                    <Card
                      key={sp.name}
                      className={cn("cursor-pointer hover:border-primary/40 transition-all hover:shadow-md", sp.status === "needs-key" && "opacity-70")}
                      onClick={() => sp.status === "live" && startChat(`Use your ${sp.name} capability to help me with: `)}
                      data-testid={`power-card-${sp.name.toLowerCase().replace(/\s+/g, "-")}`}
                    >
                      <CardContent className="p-4 flex items-start gap-3">
                        <div className="h-9 w-9 rounded-xl border border-border/60 bg-card flex items-center justify-center flex-shrink-0">
                          <Icon className={cn("h-4.5 w-4.5", sp.color)} />
                        </div>
                        <div className="min-w-0">
                          <div className="flex items-center gap-2">
                            <p className="text-sm font-medium">{sp.name}</p>
                            <Badge variant={sp.status === "live" ? "secondary" : "outline"} className="text-[10px] py-0 px-1.5 rounded-md ml-auto">
                              {sp.status === "live" ? "Live" : "Needs Key"}
                            </Badge>
                          </div>
                          <p className="text-xs text-muted-foreground mt-0.5">{sp.desc}</p>
                        </div>
                      </CardContent>
                    </Card>
                  );
                })}
              </div>
            </div>
          )}
        </div>
      </div>
    </AppShell>
  );
}
