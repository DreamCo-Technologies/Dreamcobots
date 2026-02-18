import { useMemo } from "react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { cn } from "@/lib/utils";
import { CornerDownLeft, Loader2, Send, Sparkles } from "lucide-react";

export default function ChatComposer(props: {
  value: string;
  onChange: (v: string) => void;
  onSend: () => void;
  onSuggest: () => void;
  disabled?: boolean;
  sending?: boolean;
  placeholder?: string;
}) {
  const hint = useMemo(() => {
    const len = props.value.trim().length;
    if (len === 0) return "Ask for a plan, an automation, or a next action.";
    if (len < 60) return "Tip: include your goal + constraints + timeframe.";
    return "Looks good. Send when ready.";
  }, [props.value]);

  return (
    <div className="buddy-card buddy-noise rounded-3xl border-border/60 overflow-hidden">
      <div className="p-4 md:p-5">
        <div className="flex items-center justify-between gap-4">
          <p className="text-xs font-medium text-muted-foreground">Message your bot</p>
          <p className="text-xs text-muted-foreground">
            <span className="inline-flex items-center gap-1">
              <CornerDownLeft className="h-3.5 w-3.5" />
              Enter to send • Shift+Enter for newline
            </span>
          </p>
        </div>

        <div className="mt-3">
          <Textarea
            value={props.value}
            onChange={(e) => props.onChange(e.target.value)}
            placeholder={props.placeholder ?? "What are we building today?"}
            className={cn(
              "min-h-[108px] md:min-h-[120px] rounded-2xl border-2 border-border/60 bg-background/40",
              "focus:border-primary focus:ring-4 focus:ring-ring/15 transition-all",
              "text-[15px] md:text-base leading-relaxed"
            )}
            disabled={props.disabled}
            data-testid="chat-input"
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                props.onSend();
              }
            }}
          />
          <p className="mt-2 text-xs text-muted-foreground">{hint}</p>
        </div>

        <div className="mt-4 flex flex-col sm:flex-row gap-2 sm:items-center sm:justify-between">
          <Button
            type="button"
            variant="outline"
            onClick={props.onSuggest}
            disabled={props.disabled || props.sending}
            className="rounded-xl border-border/70 bg-card/60 hover:bg-card shadow-sm hover:shadow-md transition-all"
            data-testid="suggest-prompt"
          >
            <Sparkles className="h-4 w-4 mr-2" />
            Suggest a prompt
          </Button>

          <Button
            type="button"
            onClick={props.onSend}
            disabled={props.disabled || props.sending || props.value.trim().length === 0}
            className={cn(
              "rounded-xl px-6 py-3 font-semibold",
              "bg-gradient-to-r from-primary to-accent text-primary-foreground",
              "shadow-md shadow-primary/20 hover:shadow-lg hover:shadow-primary/25 hover:-translate-y-0.5",
              "active:translate-y-0 transition-all"
            )}
            data-testid="send-message"
          >
            {props.sending ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                Sending…
              </>
            ) : (
              <>
                <Send className="h-4 w-4 mr-2" />
                Send
              </>
            )}
          </Button>
        </div>
      </div>
    </div>
  );
}
