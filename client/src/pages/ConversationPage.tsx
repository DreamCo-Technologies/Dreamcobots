import { useEffect, useMemo, useRef, useState } from "react";
import { useLocation, useRoute } from "wouter";
import Seo from "@/components/Seo";
import AppShell from "@/components/AppShell";
import ChatMessageBubble from "@/components/ChatMessageBubble";
import ChatComposer from "@/components/ChatComposer";
import ConfirmDialog from "@/components/ConfirmDialog";
import EmptyState from "@/components/EmptyState";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import { Skeleton } from "@/components/ui/skeleton";
import { Badge } from "@/components/ui/badge";
import { useToast } from "@/hooks/use-toast";
import {
  streamAssistantReply,
  useConversation,
  useDeleteConversation,
} from "@/hooks/use-conversations";
import { useBots } from "@/hooks/use-bots";
import { cn } from "@/lib/utils";
import type { Message } from "@shared/schema";
import { api } from "@shared/routes";
import {
  Bot, Loader2, Trash2, Wand2, Map, Hammer, Zap, GraduationCap,
  Sparkles, BrainCircuit, Share2, Download, Mic, Search, Github,
  BookOpen, Gamepad2, GraduationCap as CourseIcon, Code2, Cpu,
  CheckCircle2, AlertCircle, ChevronRight, Terminal, FileCode2,
  Globe, Users, ShieldCheck, BarChart3, Music, ImageIcon, X,
} from "lucide-react";
import { useQuery } from "@tanstack/react-query";

type ChatMode = "plan" | "build" | "execute" | "teach" | "vibe";

const MODE_CONFIG: Record<ChatMode, { label: string; icon: typeof Map; color: string; description: string; suggestions: string[] }> = {
  plan: {
    label: "Plan",
    icon: Map,
    color: "text-blue-500",
    description: "Strategic thinking & roadmaps",
    suggestions: [
      "Map out a 90-day revenue plan for my AI-powered SaaS business.",
      "Design the architecture for an autonomous content empire.",
      "Break down my business idea into phases with revenue milestones.",
      "Create a competitive analysis of the top 10 players in my niche.",
    ],
  },
  build: {
    label: "Build",
    icon: Hammer,
    color: "text-amber-500",
    description: "Create & implement solutions",
    suggestions: [
      "Build me an automation pipeline that generates passive income.",
      "Help me create a full landing page for my AI product launch.",
      "Set up an automated lead generation system for my business.",
      "Design a bot workflow that handles customer onboarding end-to-end.",
    ],
  },
  execute: {
    label: "Execute",
    icon: Zap,
    color: "text-green-500",
    description: "Take action & get results",
    suggestions: [
      "Write 5 high-converting email sequences for my product launch.",
      "Generate a week of social media content for my AI startup.",
      "Create a pitch deck outline that closes investors.",
      "Draft a partnership proposal for a strategic alliance.",
    ],
  },
  teach: {
    label: "Teach",
    icon: GraduationCap,
    color: "text-purple-500",
    description: "Learn & master new skills",
    suggestions: [
      "Teach me how to use AI to automate my entire business workflow.",
      "Explain prompt engineering like I'm a beginner entrepreneur.",
      "Walk me through building my first revenue-generating bot.",
      "Show me the top money-making strategies using AI tools today.",
    ],
  },
  vibe: {
    label: "Vibe Code",
    icon: Code2,
    color: "text-cyan-500",
    description: "Build full projects from a single prompt",
    suggestions: [
      "Vibe code a full SaaS dashboard with auth, billing, and analytics.",
      "Build me a complete browser game — snake with leaderboard and sound.",
      "Generate a full React + TypeScript todo app with cloud sync.",
      "Create a real-time chat app with WebSockets and voice messages.",
    ],
  },
};

interface BuddyFeature {
  name: string;
  route: string;
  status: "live" | "needs-key";
  description: string;
  setup?: string;
  icon?: typeof Mic;
  testPayload?: Record<string, unknown>;
  testRoute?: string;
}

const FEATURE_ICONS: Record<string, typeof Mic> = {
  "Vibe Coding": Code2,
  "Image Generation": ImageIcon,
  "Voice Cloning": Mic,
  "Web Search": Search,
  "GitHub Intelligence": Github,
  "Council Governance": Users,
  "Self Training": Cpu,
  "Book Study": BookOpen,
  "Game Builder": Gamepad2,
  "Course Simulator": CourseIcon,
  "Competitive Intel": BarChart3,
  "Data Packages": ShieldCheck,
};

function BuddySuperpowersPanel({ onInjectPrompt }: { onInjectPrompt: (p: string) => void }) {
  const { data, isLoading } = useQuery<{ features: BuddyFeature[] }>({
    queryKey: ["/api/buddy/features"],
  });
  const { toast } = useToast();
  const [testing, setTesting] = useState<string | null>(null);
  const [results, setResults] = useState<Record<string, string>>({});

  const quickTests: Record<string, () => Promise<string>> = {
    "Web Search": async () => {
      const r = await fetch("/api/search/web", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ query: "best AI tools 2024", numResults: 2 }) });
      const d = await r.json() as any;
      return d.synthesis ? `✅ Search works! Source: ${d.source}\n\n${(d.synthesis as string).slice(0, 200)}...` : `❌ ${d.error}`;
    },
    "GitHub Intelligence": async () => {
      const r = await fetch("/api/github-intel/trending?topic=artificial-intelligence");
      const d = await r.json() as any;
      const top3 = (d.repos ?? []).slice(0, 3).map((repo: any) => `⭐${repo.stars} ${repo.name}`).join("\n");
      return top3 ? `✅ GitHub Intel live!\n\n${top3}` : `✅ Connected (no repos for topic)`;
    },
    "Council Governance": async () => {
      const r = await fetch("/api/council/proposals");
      const d = await r.json() as any;
      return `✅ Council active! ${d.total} pending proposals\n\n${(d.proposals ?? []).slice(0, 2).map((p: any) => `• [${p.priority.toUpperCase()}] ${p.title}`).join("\n")}`;
    },
    "Voice Cloning": async () => {
      const r = await fetch("/api/voice/clone", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ text: "Hello" }) });
      const d = await r.json() as any;
      if (r.status === 503) return `⚠️ Needs setup: ${d.setup}`;
      if (r.ok) return "✅ Voice cloning live!";
      return `❌ ${d.error}`;
    },
    "Image Generation": async () => {
      const r = await fetch("/api/generate-image", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ prompt: "" }) });
      const d = await r.json() as any;
      return d.error === "Prompt is required" ? "✅ Image gen route live! (provide a prompt to generate)" : `Status: ${JSON.stringify(d).slice(0, 100)}`;
    },
    "Book Study": async () => {
      const r = await fetch("/api/buddy/study-book", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ title: "Think and Grow Rich", author: "Napoleon Hill" }) });
      const d = await r.json() as any;
      return d.content ? `✅ Book study works!\n\n${(d.content as string).slice(0, 250)}...` : `❌ ${d.error}`;
    },
    "Competitive Intel": async () => {
      const r = await fetch("/api/intel/competitive", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ competitor: "ChatGPT", category: "ai-chat" }) });
      const d = await r.json() as any;
      return d.analysis ? `✅ Competitive intel live!\n\n${(d.analysis as string).slice(0, 250)}...` : `❌ ${d.error}`;
    },
  };

  async function runTest(featureName: string) {
    const testFn = quickTests[featureName];
    if (!testFn) {
      onInjectPrompt(`Test the ${featureName} capability and show me what it can do.`);
      return;
    }
    setTesting(featureName);
    try {
      const result = await testFn();
      setResults(prev => ({ ...prev, [featureName]: result }));
      toast({ title: `${featureName} tested`, description: result.split("\n")[0] });
    } catch (e: any) {
      setResults(prev => ({ ...prev, [featureName]: `❌ Error: ${e.message}` }));
    } finally {
      setTesting(null);
    }
  }

  const features = data?.features ?? [];
  const live = features.filter(f => f.status === "live").length;
  const total = features.length;

  return (
    <Card className="rounded-2xl border-cyan-500/20 bg-gradient-to-b from-cyan-950/20 to-card/40 overflow-hidden">
      <div className="p-4 border-b border-border/60 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <BrainCircuit className="h-4 w-4 text-cyan-400" />
          <span className="text-sm font-semibold text-cyan-300">Buddy Superpowers</span>
          {!isLoading && (
            <Badge variant="outline" className="text-xs border-cyan-500/40 text-cyan-400">
              {live}/{total} live
            </Badge>
          )}
        </div>
        <Terminal className="h-4 w-4 text-muted-foreground" />
      </div>

      {isLoading ? (
        <div className="p-4 space-y-2">
          {[1,2,3,4].map(i => <Skeleton key={i} className="h-10 rounded-xl" />)}
        </div>
      ) : (
        <div className="p-3 grid grid-cols-1 gap-1.5 max-h-96 overflow-y-auto">
          {features.map((feature) => {
            const Icon = FEATURE_ICONS[feature.name] ?? Sparkles;
            const isLive = feature.status === "live";
            const isTesting = testing === feature.name;
            const result = results[feature.name];
            return (
              <div key={feature.name} className="group">
                <button
                  onClick={() => runTest(feature.name)}
                  disabled={isTesting}
                  className={cn(
                    "w-full text-left flex items-center gap-3 px-3 py-2.5 rounded-xl transition-all text-sm",
                    "border hover:shadow-sm",
                    isLive
                      ? "border-green-500/20 bg-green-950/10 hover:bg-green-950/20 hover:border-green-500/30"
                      : "border-amber-500/20 bg-amber-950/10 hover:bg-amber-950/20"
                  )}
                  data-testid={`buddy-feature-${feature.name.toLowerCase().replace(/\s+/g,"-")}`}
                >
                  <div className={cn(
                    "flex-shrink-0 h-7 w-7 rounded-lg flex items-center justify-center",
                    isLive ? "bg-green-500/15" : "bg-amber-500/15"
                  )}>
                    {isTesting ? (
                      <Loader2 className="h-3.5 w-3.5 animate-spin text-cyan-400" />
                    ) : isLive ? (
                      <Icon className="h-3.5 w-3.5 text-green-400" />
                    ) : (
                      <Icon className="h-3.5 w-3.5 text-amber-400" />
                    )}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-1.5">
                      <span className="font-medium text-foreground">{feature.name}</span>
                      {isLive
                        ? <CheckCircle2 className="h-3 w-3 text-green-500" />
                        : <AlertCircle className="h-3 w-3 text-amber-500" />
                      }
                    </div>
                    <p className="text-xs text-muted-foreground truncate">{feature.description}</p>
                  </div>
                  <ChevronRight className="h-3.5 w-3.5 text-muted-foreground group-hover:text-foreground transition-colors flex-shrink-0" />
                </button>
                {result && (
                  <div className={cn(
                    "mx-1 mb-1 p-2.5 rounded-xl text-xs font-mono whitespace-pre-wrap border",
                    result.startsWith("✅") ? "bg-green-950/20 border-green-500/20 text-green-300" :
                    result.startsWith("⚠️") ? "bg-amber-950/20 border-amber-500/20 text-amber-300" :
                    "bg-red-950/20 border-red-500/20 text-red-300"
                  )}>
                    {result}
                    <button onClick={() => setResults(prev => { const n = {...prev}; delete n[feature.name]; return n; })} className="float-right text-muted-foreground hover:text-foreground">
                      <X className="h-3 w-3" />
                    </button>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}

      <div className="p-3 border-t border-border/60">
        <p className="text-xs text-muted-foreground text-center">Click any feature to test it live → results appear above</p>
      </div>
    </Card>
  );
}

function buildSuggestedPrompt(mode: ChatMode) {
  const suggestions = MODE_CONFIG[mode].suggestions;
  return suggestions[Math.floor(Math.random() * suggestions.length)];
}

export default function ConversationPage() {
  const [, params] = useRoute("/c/:id");
  const [, navigate] = useLocation();
  const id = useMemo(() => Number(params?.id), [params?.id]);

  const { toast } = useToast();

  const bots = useBots();
  const [botSlug, setBotSlug] = useState<string | undefined>(undefined);
  const [mode, setMode] = useState<ChatMode>("build");
  const [showSuperpowers, setShowSuperpowers] = useState(false);

  const convo = useConversation(Number.isFinite(id) ? id : undefined);
  const del = useDeleteConversation();

  const [composer, setComposer] = useState("");
  const [streaming, setStreaming] = useState(false);
  const [streamError, setStreamError] = useState<string | null>(null);

  const [confirmDeleteOpen, setConfirmDeleteOpen] = useState(false);

  const [localMessages, setLocalMessages] = useState<Message[] | null>(null);
  const messages = localMessages ?? convo.data?.messages ?? [];

  const scrollRef = useRef<HTMLDivElement | null>(null);
  const abortRef = useRef<AbortController | null>(null);

  const title = convo.data?.conversation?.title ?? `Conversation #${id}`;

  const isBuddy = effectiveBotSlugRef();

  function effectiveBotSlugRef() {
    const list = bots.data ?? [];
    const slug = botSlug ?? (list.find((b) => b.isDefault)?.slug ?? list[0]?.slug);
    return slug === "buddy-bot";
  }

  useEffect(() => {
    setLocalMessages(null);
  }, [id]);

  useEffect(() => {
    const el = scrollRef.current;
    if (!el) return;
    el.scrollTo({ top: el.scrollHeight, behavior: "smooth" });
  }, [messages.length, streaming]);

  const effectiveBotSlug = useMemo(() => {
    if (botSlug) return botSlug;
    const list = bots.data ?? [];
    return list.find((b) => b.isDefault)?.slug ?? list[0]?.slug;
  }, [botSlug, bots.data]);

  // Auto-show superpowers when Buddy is selected
  useEffect(() => {
    if (effectiveBotSlug === "buddy-bot") {
      setShowSuperpowers(true);
    }
  }, [effectiveBotSlug]);

  async function handleSend() {
    const content = composer.trim();
    if (!content || !Number.isFinite(id)) return;

    setStreamError(null);
    setStreaming(true);

    abortRef.current?.abort();
    const controller = new AbortController();
    abortRef.current = controller;

    const base = convo.data?.messages ?? [];
    const now = new Date().toISOString();
    const tempUserId = -Math.floor(Math.random() * 1000000);
    const tempAssistantId = -Math.floor(Math.random() * 1000000) - 1;

    const userMsg: Message = {
      id: tempUserId as any,
      conversationId: id,
      role: "user",
      content,
      createdAt: now as any,
    };

    const assistantMsg: Message = {
      id: tempAssistantId as any,
      conversationId: id,
      role: "assistant",
      content: "",
      createdAt: now as any,
    };

    setLocalMessages([...base, userMsg, assistantMsg]);
    setComposer("");

    try {
      const input = api.conversations.stream.input.parse({
        content,
        botSlug: effectiveBotSlug,
        mode: mode === "vibe" ? "build" : mode,
      });

      await streamAssistantReply({
        conversationId: id,
        input,
        signal: controller.signal,
        onEvent: (evt) => {
          if (evt.type === "delta") {
            const delta = evt.content ?? "";
            setLocalMessages((prev) => {
              const list = prev ?? [...base, userMsg, assistantMsg];
              const next = [...list];
              const lastIdx = [...next].reverse().findIndex((m) => m.role === "assistant");
              const idx = lastIdx === -1 ? -1 : next.length - 1 - lastIdx;
              if (idx >= 0) {
                next[idx] = { ...next[idx], content: (next[idx].content ?? "") + delta };
              }
              return next;
            });
          } else if (evt.type === "error") {
            setStreamError(evt.error ?? "Stream error");
          }
        },
      });

      await convo.refetch();
      setLocalMessages(null);
    } catch (e: any) {
      if (e?.name === "AbortError") return;
      setStreamError(e?.message ?? "Failed to stream response");
      toast({
        title: "Streaming failed",
        description: e?.message ?? "Unknown error",
        variant: "destructive",
      });
    } finally {
      setStreaming(false);
    }
  }

  const currentModeConfig = MODE_CONFIG[mode];

  const handleExport = () => {
    const text = messages.map(m => `${m.role.toUpperCase()}: ${m.content}`).join("\n\n");
    const blob = new Blob([text], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `conversation-${id}.txt`;
    a.click();
    URL.revokeObjectURL(url);
    toast({ title: "Conversation exported", description: "Downloaded as text file." });
  };

  const handleShare = () => {
    navigator.clipboard.writeText(window.location.href);
    toast({ title: "Link copied", description: "Conversation link copied to clipboard." });
  };

  return (
    <AppShell selectedBotSlug={botSlug} onBotChange={setBotSlug}>
      <Seo title={`DreamCo Empire OS — ${title}`} description="Chat thread with AI bot, streaming responses in real time." />

      <ConfirmDialog
        open={confirmDeleteOpen}
        onOpenChange={setConfirmDeleteOpen}
        title="Delete conversation?"
        description="This will permanently remove the conversation and its messages."
        confirmLabel={del.isPending ? "Deleting…" : "Delete"}
        onConfirm={async () => {
          try {
            await del.mutateAsync(id);
            setConfirmDeleteOpen(false);
            toast({ title: "Conversation deleted" });
            navigate("/");
          } catch (e: any) {
            toast({
              title: "Delete failed",
              description: e?.message ?? "Unknown error",
              variant: "destructive",
            });
          }
        }}
        destructive
        data-testid="delete-conversation-dialog"
      />

      <div className="buddy-appear">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-end md:justify-between gap-4">
          <div className="min-w-0">
            <div className="flex items-center gap-2">
              <h2 className="text-3xl md:text-4xl truncate" data-testid="conversation-title">{title}</h2>
              {effectiveBotSlug === "buddy-bot" && (
                <Badge className="bg-cyan-500/20 text-cyan-300 border-cyan-500/30 text-xs rounded-lg">
                  <BrainCircuit className="h-3 w-3 mr-1" />
                  Buddy
                </Badge>
              )}
            </div>
            <div className="mt-2 flex flex-wrap items-center gap-2 text-sm text-muted-foreground">
              <span className="inline-flex items-center gap-2">
                <span className={cn("h-2 w-2 rounded-full", streaming ? "bg-amber-400 animate-pulse" : "bg-[rgb(34_197_94)]")} />
                {streaming ? "Bot is responding..." : "Ready"}
              </span>
              <Separator orientation="vertical" className="h-4" />
              <span className="font-mono">#{id}</span>
              <Separator orientation="vertical" className="h-4" />
              <span className="inline-flex items-center gap-2">
                <Bot className="h-4 w-4 text-primary" />
                {effectiveBotSlug ? `Bot: ${effectiveBotSlug}` : "Bot: —"}
              </span>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-2">
            <Button
              variant="outline"
              className="rounded-xl border-border/70 bg-card/60 hover:bg-card shadow-sm hover:shadow-md transition-all"
              onClick={handleExport}
              data-testid="export-conversation"
            >
              <Download className="h-4 w-4 mr-2" />
              Export
            </Button>

            <Button
              variant="outline"
              className="rounded-xl border-border/70 bg-card/60 hover:bg-card shadow-sm hover:shadow-md transition-all"
              onClick={handleShare}
              data-testid="share-conversation"
            >
              <Share2 className="h-4 w-4 mr-2" />
              Share
            </Button>

            <Button
              variant="outline"
              className="rounded-xl border-border/70 bg-card/60 hover:bg-card shadow-sm hover:shadow-md transition-all"
              onClick={() => {
                setComposer(buildSuggestedPrompt(mode));
                toast({ title: "Suggestion inserted", description: "Tweak it, then send." });
              }}
              data-testid="insert-suggestion"
            >
              <Wand2 className="h-4 w-4 mr-2" />
              Suggest
            </Button>

            {effectiveBotSlug === "buddy-bot" ? (
              <Button
                variant="outline"
                className={cn(
                  "rounded-xl shadow-sm hover:shadow-md transition-all font-medium",
                  showSuperpowers
                    ? "border-cyan-500/60 bg-cyan-950/30 text-cyan-300 hover:bg-cyan-950/40"
                    : "border-cyan-500/30 bg-cyan-950/10 hover:bg-cyan-950/20 text-cyan-400"
                )}
                onClick={() => setShowSuperpowers(v => !v)}
                data-testid="toggle-superpowers"
              >
                <Cpu className="h-4 w-4 mr-2" />
                {showSuperpowers ? "Hide Powers" : "Superpowers"}
              </Button>
            ) : (
              <Button
                variant="outline"
                className="rounded-xl border-primary/40 bg-primary/8 hover:bg-primary/14 text-primary shadow-sm hover:shadow-md transition-all font-medium"
                onClick={() => {
                  const buddySlug = (bots.data ?? []).find(b => b.slug === "buddy-bot")?.slug;
                  if (buddySlug) {
                    setBotSlug(buddySlug);
                    toast({ title: "🧠 Buddy Bot activated", description: "Buddy has mastered every coding library. Ask him anything." });
                  } else {
                    toast({ title: "Buddy Bot not found", description: "Try selecting him from the bot dropdown.", variant: "destructive" });
                  }
                }}
                data-testid="call-buddy-bot"
              >
                <BrainCircuit className="h-4 w-4 mr-2" />
                Call Buddy
              </Button>
            )}

            <Button
              variant="outline"
              className="rounded-xl border-destructive/30 bg-destructive/5 hover:bg-destructive/10 text-destructive shadow-sm hover:shadow-md transition-all"
              onClick={() => setConfirmDeleteOpen(true)}
              data-testid="delete-conversation"
            >
              <Trash2 className="h-4 w-4 mr-2" />
              Delete
            </Button>
          </div>
        </div>

        {/* Mode Selector */}
        <div className="mt-4 flex items-center gap-2 flex-wrap" data-testid="mode-selector">
          {(Object.keys(MODE_CONFIG) as ChatMode[]).map((m) => {
            const cfg = MODE_CONFIG[m];
            const Icon = cfg.icon;
            const isActive = mode === m;
            return (
              <button
                key={m}
                onClick={() => setMode(m)}
                className={cn(
                  "inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-sm font-medium transition-all",
                  isActive
                    ? m === "vibe"
                      ? "bg-cyan-500 text-white shadow-md shadow-cyan-500/20"
                      : "bg-primary text-primary-foreground shadow-md"
                    : "bg-card/60 border border-border/60 text-muted-foreground hover:text-foreground hover:bg-card hover:shadow-sm"
                )}
                data-testid={`mode-${m}`}
              >
                <Icon className={cn("h-3.5 w-3.5", isActive ? (m === "vibe" ? "text-white" : "text-primary-foreground") : cfg.color)} />
                {cfg.label}
                {m === "vibe" && !isActive && (
                  <span className="ml-0.5 text-[10px] font-bold text-cyan-500 uppercase tracking-tight">NEW</span>
                )}
              </button>
            );
          })}
          <span className="text-xs text-muted-foreground ml-2 hidden md:inline" data-testid="mode-description">
            {currentModeConfig.description}
          </span>
        </div>

        {/* Vibe Code bar — shown when vibe mode is active */}
        {mode === "vibe" && (
          <div className="mt-3 flex items-center gap-2 p-3 rounded-2xl border border-cyan-500/20 bg-cyan-950/10">
            <Terminal className="h-4 w-4 text-cyan-400 flex-shrink-0" />
            <span className="text-xs text-cyan-300 font-medium">Vibe Code Mode —</span>
            <span className="text-xs text-muted-foreground">Describe any project and Buddy builds every file from scratch. Works in React, Python, Rust, Go, n8n, and more.</span>
            <div className="ml-auto flex items-center gap-1.5 text-xs">
              {["React","Python","n8n","Rust","Game"].map(lang => (
                <button
                  key={lang}
                  onClick={() => setComposer(`Build a complete ${lang} project: `)}
                  className="px-2 py-1 rounded-lg bg-cyan-950/40 border border-cyan-500/20 text-cyan-400 hover:bg-cyan-950/60 transition-colors text-[11px] font-mono"
                >
                  {lang}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Main layout — chat + superpowers panel */}
        <div className={cn("mt-4 gap-4 md:gap-5", showSuperpowers && effectiveBotSlug === "buddy-bot" ? "grid grid-cols-1 md:grid-cols-3" : "grid grid-cols-1")}>

          {/* Chat card */}
          <div className={showSuperpowers && effectiveBotSlug === "buddy-bot" ? "md:col-span-2" : ""}>
            <Card className="buddy-card rounded-3xl border-border/60 overflow-hidden">
              <div className="p-4 md:p-5 border-b border-border/60 flex items-center justify-between">
                <div className="flex items-center gap-2">
                  {mode === "vibe" ? (
                    <FileCode2 className="h-4 w-4 text-cyan-400" />
                  ) : (
                    <p className="text-xs font-medium text-muted-foreground">Thread</p>
                  )}
                  {mode === "vibe" && <p className="text-xs font-medium text-cyan-300">Vibe Coding Session</p>}
                </div>
                <Badge variant="outline" className={cn(
                  "text-xs rounded-lg",
                  mode === "vibe" && "border-cyan-500/40 text-cyan-400"
                )}>
                  {mode === "vibe" ? (
                    <><Terminal className="h-3 w-3 mr-1 text-cyan-400" /> Vibe Mode</>
                  ) : (
                    <><Sparkles className={cn("h-3 w-3 mr-1", currentModeConfig.color)} /> {currentModeConfig.label} Mode</>
                  )}
                </Badge>
              </div>

              <div className="relative">
                {convo.isLoading ? (
                  <div className="p-5 space-y-3">
                    <Skeleton className="h-20 rounded-2xl" />
                    <Skeleton className="h-16 rounded-2xl" />
                    <Skeleton className="h-24 rounded-2xl" />
                  </div>
                ) : convo.isError ? (
                  <div className="p-5">
                    <EmptyState
                      icon={<Loader2 className="h-6 w-6" />}
                      title="Couldn't load this conversation"
                      description={(convo.error as any)?.message ?? "Unknown error"}
                      action={
                        <Button onClick={() => convo.refetch()} className="rounded-xl" data-testid="retry-conversation">
                          Retry
                        </Button>
                      }
                    />
                  </div>
                ) : convo.data === null ? (
                  <div className="p-5">
                    <EmptyState
                      icon={<Bot className="h-6 w-6" />}
                      title="Conversation not found"
                      description="It may have been deleted."
                      action={
                        <Button onClick={() => navigate("/")} className="rounded-xl" data-testid="back-to-chat">
                          Back to chats
                        </Button>
                      }
                    />
                  </div>
                ) : (
                  <ScrollArea className="h-[46vh] md:h-[56vh]">
                    <div ref={scrollRef} className="p-4 md:p-6 space-y-4">
                      {messages.length === 0 ? (
                        <div className="space-y-6" data-testid="thread-empty">
                          {mode === "vibe" ? (
                            <div className="space-y-4">
                              <div className="flex items-center gap-3 p-4 rounded-2xl border border-cyan-500/20 bg-cyan-950/10">
                                <div className="h-10 w-10 rounded-xl bg-cyan-500/20 flex items-center justify-center flex-shrink-0">
                                  <Code2 className="h-5 w-5 text-cyan-400" />
                                </div>
                                <div>
                                  <p className="font-semibold text-cyan-300">Vibe Code Mode Active</p>
                                  <p className="text-xs text-muted-foreground">Describe any project. Buddy will build every file, every function, ready to run.</p>
                                </div>
                              </div>
                              <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                                {currentModeConfig.suggestions.map((s, i) => (
                                  <button
                                    key={i}
                                    onClick={() => setComposer(s)}
                                    className="text-left text-sm p-3 rounded-xl border border-cyan-500/20 bg-cyan-950/5 hover:bg-cyan-950/15 hover:shadow-sm transition-all text-muted-foreground hover:text-cyan-300"
                                    data-testid={`suggestion-${i}`}
                                  >
                                    <FileCode2 className="h-3 w-3 inline mr-1.5 text-cyan-500" />
                                    {s}
                                  </button>
                                ))}
                              </div>
                            </div>
                          ) : (
                            <div className="space-y-6">
                              <EmptyState
                                icon={<Bot className="h-6 w-6" />}
                                title={`${currentModeConfig.label} Mode Active`}
                                description={currentModeConfig.description + " — pick a suggestion below or type your own."}
                              />
                              <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                                {currentModeConfig.suggestions.map((s, i) => (
                                  <button
                                    key={i}
                                    onClick={() => setComposer(s)}
                                    className="text-left text-sm p-3 rounded-xl border border-border/60 bg-card/40 hover:bg-card hover:shadow-sm transition-all text-muted-foreground hover:text-foreground"
                                    data-testid={`suggestion-${i}`}
                                  >
                                    {s}
                                  </button>
                                ))}
                              </div>
                            </div>
                          )}
                        </div>
                      ) : (
                        <div className="space-y-4">
                          {messages.map((m, idx) => (
                            <ChatMessageBubble key={`${m.id}-${idx}`} message={m} index={idx} />
                          ))}
                        </div>
                      )}

                      {streamError ? (
                        <div className="rounded-2xl border border-destructive/30 bg-destructive/5 p-4">
                          <p className="text-sm font-medium text-destructive">Stream error</p>
                          <p className="text-sm text-muted-foreground mt-1">{streamError}</p>
                        </div>
                      ) : null}

                      {streaming ? (
                        <div className="flex items-center gap-2 text-sm text-muted-foreground">
                          <span className="inline-flex h-8 w-8 items-center justify-center rounded-2xl border border-border/60 bg-card/70">
                            <Loader2 className="h-4 w-4 animate-spin text-primary" />
                          </span>
                          {mode === "vibe" ? "Buddy is writing code..." : "Bot is typing..."}
                        </div>
                      ) : null}
                    </div>
                  </ScrollArea>
                )}
              </div>
            </Card>

            <div className="mt-4">
              <ChatComposer
                value={composer}
                onChange={setComposer}
                onSend={handleSend}
                onSuggest={() => setComposer(buildSuggestedPrompt(mode))}
                disabled={convo.isLoading || convo.data === null}
                sending={streaming}
              />
            </div>
          </div>

          {/* Superpowers panel */}
          {showSuperpowers && effectiveBotSlug === "buddy-bot" && (
            <div className="md:col-span-1">
              <BuddySuperpowersPanel onInjectPrompt={(p) => { setComposer(p); }} />
            </div>
          )}
        </div>
      </div>
    </AppShell>
  );
}
