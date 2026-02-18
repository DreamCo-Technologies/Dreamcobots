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
import { Bot, Loader2, Trash2, Wand2 } from "lucide-react";

function buildSuggestedPrompt() {
  const suggestions = [
    "Help me design an autonomous bot to generate recurring income. Ask me 5 questions first, then propose a 7-day execution plan.",
    "I want to automate YouTube content. Give me a realistic pipeline: scripts, voice, thumbnails, upload schedule, and risk checks.",
    "Turn my idea into a task list with priorities and a minimal MVP I can ship this week.",
    "Act as a pragmatic operator. Challenge my assumptions, estimate effort, and propose the simplest profitable experiment.",
  ];
  return suggestions[Math.floor(Math.random() * suggestions.length)];
}

export default function ConversationPage() {
  const [, params] = useRoute("/c/:id");
  const [, navigate] = useLocation();
  const id = useMemo(() => Number(params?.id), [params?.id]);

  const { toast } = useToast();

  const bots = useBots();
  const [botSlug, setBotSlug] = useState<string | undefined>(undefined);

  const convo = useConversation(Number.isFinite(id) ? id : undefined);
  const del = useDeleteConversation();

  const [composer, setComposer] = useState("");
  const [streaming, setStreaming] = useState(false);
  const [streamError, setStreamError] = useState<string | null>(null);

  const [confirmDeleteOpen, setConfirmDeleteOpen] = useState(false);

  // Local optimistic message list for streaming
  const [localMessages, setLocalMessages] = useState<Message[] | null>(null);
  const messages = localMessages ?? convo.data?.messages ?? [];

  const scrollRef = useRef<HTMLDivElement | null>(null);
  const abortRef = useRef<AbortController | null>(null);

  const title = convo.data?.conversation?.title ?? `Conversation #${id}`;

  useEffect(() => {
    setLocalMessages(null);
  }, [id]);

  useEffect(() => {
    // autoscroll when new messages arrive
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

    // Cancel any previous stream
    abortRef.current?.abort();
    const controller = new AbortController();
    abortRef.current = controller;

    // Seed local messages from server messages to ensure smooth append
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
              // last assistant message is the last item
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
            // Done - refetch canonical messages
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
            <h2 className="text-3xl md:text-4xl truncate">{title}</h2>
            <div className="mt-2 flex flex-wrap items-center gap-2 text-sm text-muted-foreground">
              <span className="inline-flex items-center gap-2">
                <span className="h-2 w-2 rounded-full bg-[rgb(34_197_94)]" />
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
              onClick={() => {
                setComposer(buildSuggestedPrompt());
                toast({ title: "Suggestion inserted", description: "Tweak it, then send." });
              }}
              data-testid="insert-suggestion"
            >
              <Wand2 className="h-4 w-4 mr-2" />
              Suggest
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

        <div className="mt-6 grid grid-cols-1 gap-4 md:gap-5">
          <Card className="buddy-card rounded-3xl border-border/60 overflow-hidden">
            <div className="p-4 md:p-5 border-b border-border/60">
              <p className="text-xs font-medium text-muted-foreground">Thread</p>
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
                    title="Couldn’t load this conversation"
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
                      <EmptyState
                        icon={<Bot className="h-6 w-6" />}
                        title="Start your conversation"
                        description="Ask for an automation plan, a system design, or a focused next action."
                        data-testid="thread-empty"
                      />
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
            onSuggest={() => setComposer(buildSuggestedPrompt())}
            disabled={convo.isLoading || convo.data === null}
            sending={streaming}
          />
        </div>
      </div>
    </AppShell>
  );
}
