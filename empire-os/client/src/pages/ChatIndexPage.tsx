import Seo from "@/components/Seo";
import AppShell from "@/components/AppShell";
import EmptyState from "@/components/EmptyState";
import { Button } from "@/components/ui/button";
import { useCreateConversation } from "@/hooks/use-conversations";
import { useToast } from "@/hooks/use-toast";
import { MessageSquarePlus } from "lucide-react";
import { useEffect, useState } from "react";
import { useLocation } from "wouter";

export default function ChatIndexPage() {
  const [, navigate] = useLocation();
  const { toast } = useToast();
  const createConversation = useCreateConversation();

  const [botSlug, setBotSlug] = useState<string | undefined>(undefined);

  useEffect(() => {
    // default: keep on chat index; user can create new chat
  }, []);

  return (
    <AppShell selectedBotSlug={botSlug} onBotChange={setBotSlug}>
      <Seo
        title="DreamCo Empire OS — Chat"
        description="Chat with DreamCo Empire OS: your AI-powered autonomous wealth-generation system."
      />

      <div className="buddy-appear">
        <EmptyState
          icon={<MessageSquarePlus className="h-6 w-6" />}
          title="Start a conversation"
          description="Create a new chat, describe your goal, and your AI bots will help turn it into an autonomous plan."
          action={
            <Button
              onClick={async () => {
                try {
                  const created = await createConversation.mutateAsync({ title: "New chat" } as any);
                  toast({ title: "Chat created", description: "Opening your new thread…" });
                  navigate(`/c/${created.id}`);
                } catch (e: any) {
                  toast({
                    title: "Couldn't create chat",
                    description: e?.message ?? "Unknown error",
                    variant: "destructive",
                  });
                }
              }}
              disabled={createConversation.isPending}
              className="rounded-xl px-6 py-3 font-semibold bg-gradient-to-r from-primary to-accent text-primary-foreground shadow-md shadow-primary/20 hover:shadow-lg hover:shadow-primary/25 hover:-translate-y-0.5 active:translate-y-0 transition-all"
              data-testid="create-first-chat"
            >
              {createConversation.isPending ? "Creating…" : "New chat"}
            </Button>
          }
          data-testid="chat-empty"
        />
      </div>
    </AppShell>
  );
}
