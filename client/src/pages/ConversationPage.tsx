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
import { Bot, Loader2, Trash2, Wand2, Map, Hammer, Zap, GraduationCap, Sparkles, BrainCircuit, Share2, Download } from "lucide-react";

type ChatMode = "plan" | "build" | "execute" | "teach";

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
};

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
        mode,
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
          } else if (evt.type === "done") {
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
        <div className="flex flex-col md:flex-row md:items-end md:justify-between gap-4">
          <div className="min-w-0">
            <h2 className="text-3xl md:text-4xl truncate" data-testid="conversation-title">{title}</h2>
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

          <div className="flex items-center gap-2">
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

        <div className="mt-4 flex items-center gap-2" data-testid="mode-selector">
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
                    ? "bg-primary text-primary-foreground shadow-md"
                    : "bg-card/60 border border-border/60 text-muted-foreground hover:text-foreground hover:bg-card hover:shadow-sm"
                )}
                data-testid={`mode-${m}`}
              >
                <Icon className={cn("h-3.5 w-3.5", isActive ? "text-primary-foreground" : cfg.color)} />
                {cfg.label}
              </button>
            );
          })}
          <span className="text-xs text-muted-foreground ml-2 hidden md:inline" data-testid="mode-description">
            {currentModeConfig.description}
          </span>
        </div>

        <div className="mt-4 grid grid-cols-1 gap-4 md:gap-5">
          <Card className="buddy-card rounded-3xl border-border/60 overflow-hidden">
            <div className="p-4 md:p-5 border-b border-border/60 flex items-center justify-between">
              <p className="text-xs font-medium text-muted-foreground">Thread</p>
              <Badge variant="outline" className="text-xs rounded-lg">
                <Sparkles className={cn("h-3 w-3 mr-1", currentModeConfig.color)} />
                {currentModeConfig.label} Mode
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
                      <Button
                        onClick={() => convo.refetch()}
                        className="rounded-xl"
                        data-testid="retry-conversation"
                      >
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
                      <Button
                        onClick={() => navigate("/")}
                        className="rounded-xl"
                        data-testid="back-to-chat"
                      >
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
                        Bot is typing...
                      </div>
                    ) : null}
                  </div>
                </ScrollArea>
              )}
            </div>
          </Card>

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
    </AppShell>
  );
}
