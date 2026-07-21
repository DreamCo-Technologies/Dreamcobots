import { cn } from "@/lib/utils";
import { Bot, User } from "lucide-react";
import type { Message } from "@shared/schema";

function formatTime(ts: any) {
  try {
    const d = new Date(ts);
    return d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  } catch {
    return "";
  }
}

export default function ChatMessageBubble(props: {
  message: Message;
  index: number;
}) {
  const isUser = props.message.role === "user";
  return (
    <div
      className={cn(
        "flex w-full gap-3",
        isUser ? "justify-end" : "justify-start"
      )}
      data-testid={`message-${props.message.id}`}
    >
      {!isUser ? (
        <div className="hidden sm:flex h-9 w-9 items-center justify-center rounded-2xl border border-border/60 bg-card/70 shadow-sm">
          <Bot className="h-4 w-4 text-primary" />
        </div>
      ) : null}

      <div
        className={cn(
          "max-w-[92%] sm:max-w-[78%] md:max-w-[70%]",
          "rounded-2xl px-4 py-3 border shadow-sm",
          "transition-all duration-300",
          isUser
            ? "bg-gradient-to-br from-primary/14 via-accent/10 to-transparent border-border/60"
            : "bg-card/70 backdrop-blur border-border/60"
        )}
      >
        <div className="flex items-center justify-between gap-3 mb-1">
          <p className={cn("text-xs font-medium", isUser ? "text-primary" : "text-muted-foreground")}>
            {isUser ? "You" : "Bot"}
          </p>
          <p className="text-[11px] text-muted-foreground font-mono">
            {formatTime(props.message.createdAt as any)}
          </p>
        </div>
        <div className="prose prose-sm dark:prose-invert max-w-none prose-p:my-2 prose-pre:rounded-xl prose-pre:border prose-pre:border-border/60 prose-pre:bg-muted/40">
          <p className="whitespace-pre-wrap leading-relaxed text-[15px] md:text-base">
            {props.message.content}
          </p>
        </div>
      </div>

      {isUser ? (
        <div className="hidden sm:flex h-9 w-9 items-center justify-center rounded-2xl border border-border/60 bg-card/70 shadow-sm">
          <User className="h-4 w-4 text-foreground/80" />
        </div>
      ) : null}
    </div>
  );
}
