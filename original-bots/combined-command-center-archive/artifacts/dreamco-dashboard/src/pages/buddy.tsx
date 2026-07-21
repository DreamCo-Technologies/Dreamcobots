import { useState, useRef, useEffect } from "react";
import { useGetBuddyHistory, getGetBuddyHistoryQueryKey, useSendBuddyMessage } from "@workspace/api-client-react";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Terminal, Send, Cpu, Network, Zap, Volume2, VolumeX, Square } from "lucide-react";
import { useDreamcoVoice } from "@/lib/speech";

export default function Buddy() {
  const [sessionId] = useState(() => `session-${Math.random().toString(36).substring(2, 9)}`);
  const [message, setMessage] = useState("");
  const scrollRef = useRef<HTMLDivElement>(null);
  const voice = useDreamcoVoice();
  const [lastLatencyMs, setLastLatencyMs] = useState<number | null>(null);

  const { data: history, isLoading } = useGetBuddyHistory({
    query: { queryKey: getGetBuddyHistoryQueryKey() }
  });

  const [localMessages, setLocalMessages] = useState<{role: 'user'|'buddy', content: string, emotion?: string|null}[]>([]);

  // Initialize with history
  useEffect(() => {
    if (history && localMessages.length === 0) {
      setLocalMessages(history.map(h => ({ role: h.role as 'user'|'buddy', content: h.content, emotion: h.emotion })));
    }
  }, [history]);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [localMessages]);

  const sendMessage = useSendBuddyMessage();

  const handleSend = (e?: React.FormEvent) => {
    e?.preventDefault();
    if (!message.trim() || sendMessage.isPending) return;

    const newMsg = message;
    setMessage("");

    // Add user message immediately
    setLocalMessages(prev => [...prev, { role: 'user', content: newMsg }]);

    const t0 = performance.now();
    sendMessage.mutate({ data: { message: newMsg, sessionId } }, {
      onSuccess: (res) => {
        setLastLatencyMs(Math.round(performance.now() - t0));
        setLocalMessages(prev => [...prev, { role: 'buddy', content: res.message, emotion: res.emotion }]);
        if (voice.enabled) voice.speak(res.message);
      },
      onError: () => {
        setLocalMessages(prev => [...prev, { role: 'buddy', content: "SYSTEM ERROR: Connection to neural core failed.", emotion: "error" }]);
      }
    });
  };

  const getEmotionColor = (emotion?: string | null) => {
    switch(emotion?.toLowerCase()) {
      case 'analytical': return 'text-blue-400 border-blue-400/20 bg-blue-400/10';
      case 'alert': return 'text-amber-400 border-amber-400/20 bg-amber-400/10';
      case 'error': return 'text-destructive border-destructive/20 bg-destructive/10';
      case 'success': return 'text-primary border-primary/20 bg-primary/10';
      default: return 'text-primary border-primary/20 bg-primary/10';
    }
  };

  return (
    <div className="h-full flex flex-col gap-6 animate-in fade-in duration-500">
      <div className="flex flex-col gap-2 shrink-0">
        <h1 className="text-3xl font-mono font-bold tracking-tight text-foreground uppercase flex items-center gap-3">
          <Terminal className="h-8 w-8 text-primary" />
          Buddy_Command
        </h1>
        <p className="text-muted-foreground font-mono text-sm uppercase tracking-wider">
          Neural Interface Active // Session ID: {sessionId}
        </p>

        {voice.supported && (
          <div className="flex flex-wrap items-center gap-2 mt-1">
            <Button
              type="button"
              size="sm"
              variant={voice.enabled ? "default" : "outline"}
              onClick={() => { if (voice.enabled) voice.stop(); voice.setEnabled(!voice.enabled); }}
              className="font-mono text-xs h-8 gap-2"
              title="DreamCo Voice — Buddy speaks replies aloud (free, built-in, no third party)"
            >
              {voice.enabled ? <Volume2 className="h-3.5 w-3.5" /> : <VolumeX className="h-3.5 w-3.5" />}
              {voice.enabled ? "DreamCo Voice: ON" : "DreamCo Voice: OFF"}
            </Button>

            {voice.enabled && (
              <>
                <select
                  value={voice.voiceURI}
                  onChange={(e) => voice.setVoiceURI(e.target.value)}
                  className="h-8 rounded-md border border-border/50 bg-card px-2 font-mono text-xs text-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-primary/50 max-w-[220px]"
                  title="Choose Buddy's voice"
                >
                  <option value="">System default</option>
                  {voice.voices.map((v) => (
                    <option key={v.voiceURI} value={v.voiceURI}>
                      {v.name} ({v.lang})
                    </option>
                  ))}
                </select>

                {voice.speaking && (
                  <Button type="button" size="sm" variant="ghost" onClick={voice.stop} className="font-mono text-xs h-8 gap-2 text-destructive">
                    <Square className="h-3.5 w-3.5" /> Stop
                  </Button>
                )}
              </>
            )}
          </div>
        )}
      </div>

      <div className="flex flex-col lg:flex-row gap-6 flex-1 min-h-0">
        {/* Left Panel - Specs */}
        <div className="w-full lg:w-64 flex flex-col gap-4 shrink-0 hidden lg:flex">
          <Card className="border-border/40 bg-card/50 backdrop-blur flex-1">
            <CardContent className="p-4 space-y-6">
              <div>
                <h3 className="font-mono text-xs text-muted-foreground uppercase mb-3 flex items-center gap-2">
                  <Cpu className="h-4 w-4" /> Core Systems
                </h3>
                <div className="space-y-2">
                  <div className="flex justify-between items-center text-xs font-mono">
                    <span className="text-muted-foreground">Logic Engine</span>
                    <span className="text-primary">gpt-5-mini</span>
                  </div>
                  <div className="flex justify-between items-center text-xs font-mono">
                    <span className="text-muted-foreground">Last Response</span>
                    <span className="text-primary">{lastLatencyMs !== null ? `${lastLatencyMs}ms` : "—"}</span>
                  </div>
                  <div className="flex justify-between items-center text-xs font-mono">
                    <span className="text-muted-foreground">Session Msgs</span>
                    <span className="text-primary">{localMessages.length}</span>
                  </div>
                  <div className="flex justify-between items-center text-xs font-mono">
                    <span className="text-muted-foreground">Voice</span>
                    <span className="text-primary">{voice.supported ? (voice.enabled ? "On" : "Off") : "N/A"}</span>
                  </div>
                </div>
              </div>

              <div>
                <h3 className="font-mono text-xs text-muted-foreground uppercase mb-3 flex items-center gap-2">
                  <Network className="h-4 w-4" /> Capabilities
                </h3>
                <div className="space-y-2">
                  {['Fleet Orchestration', 'Revenue Analysis', 'Repo Diagnostics', 'Threat Mitigation'].map(cap => (
                    <div key={cap} className="bg-background/50 border border-border/40 rounded px-2 py-1.5 text-xs font-mono flex items-center gap-2">
                      <Zap className="h-3 w-3 text-primary" />
                      {cap}
                    </div>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Chat Interface */}
        <Card className="flex-1 flex flex-col border-border/40 bg-card/50 backdrop-blur relative overflow-hidden">
          <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-primary/0 via-primary/30 to-primary/0" />

          <div
            ref={scrollRef}
            className="flex-1 overflow-y-auto p-4 space-y-6"
          >
            {isLoading ? (
              <div className="flex items-center justify-center h-full">
                <div className="flex flex-col items-center gap-4 text-primary">
                  <Terminal className="h-8 w-8 animate-pulse" />
                  <span className="font-mono text-sm uppercase animate-pulse">Initializing Neural Link...</span>
                </div>
              </div>
            ) : (
              <>
                <div className="flex justify-center my-4">
                  <span className="text-[10px] font-mono uppercase text-muted-foreground tracking-widest border border-border/40 px-3 py-1 rounded-full bg-background/50">
                    Connection Established
                  </span>
                </div>

                {localMessages.map((msg, i) => (
                  <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                    <div className={`max-w-[80%] flex flex-col gap-1 ${msg.role === 'user' ? 'items-end' : 'items-start'}`}>
                      {msg.role === 'buddy' && (
                        <div className="flex items-center gap-2 mb-1">
                          <span className="font-mono text-[10px] text-primary uppercase">BuddyBot</span>
                          {msg.emotion && (
                            <span className={`font-mono text-[9px] uppercase px-1.5 py-0.5 border rounded-sm ${getEmotionColor(msg.emotion)}`}>
                              {msg.emotion}
                            </span>
                          )}
                        </div>
                      )}
                      <div className={`p-3 rounded-lg font-mono text-sm ${
                        msg.role === 'user'
                          ? 'bg-primary/20 text-primary-foreground border border-primary/30 rounded-tr-none'
                          : 'bg-background/80 text-foreground border border-border/50 rounded-tl-none'
                      }`}>
                        {msg.content}
                      </div>
                    </div>
                  </div>
                ))}

                {sendMessage.isPending && (
                  <div className="flex justify-start">
                    <div className="max-w-[80%] flex flex-col gap-1 items-start">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="font-mono text-[10px] text-primary uppercase">BuddyBot</span>
                        <span className="font-mono text-[9px] uppercase px-1.5 py-0.5 border rounded-sm text-primary border-primary/20 bg-primary/10">
                          Processing
                        </span>
                      </div>
                      <div className="p-3 rounded-lg font-mono text-sm bg-background/80 text-foreground border border-border/50 rounded-tl-none flex gap-1 items-center h-[46px]">
                        <div className="w-2 h-4 bg-primary/50 animate-pulse" />
                        <div className="w-2 h-4 bg-primary/50 animate-pulse delay-75" />
                        <div className="w-2 h-4 bg-primary/50 animate-pulse delay-150" />
                      </div>
                    </div>
                  </div>
                )}
              </>
            )}
          </div>

          <div className="p-4 bg-background/80 border-t border-border/40 backdrop-blur">
            <form onSubmit={handleSend} className="relative">
              <Terminal className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-primary/50" />
              <Input
                value={message}
                onChange={e => setMessage(e.target.value)}
                placeholder="Enter command directive..."
                className="pl-10 pr-12 font-mono bg-card border-border/50 h-12 focus-visible:ring-primary/50"
                disabled={sendMessage.isPending || isLoading}
              />
              <Button
                type="submit"
                size="icon"
                variant="ghost"
                className="absolute right-1 top-1/2 -translate-y-1/2 h-10 w-10 text-primary hover:bg-primary/20 hover:text-primary"
                disabled={!message.trim() || sendMessage.isPending || isLoading}
              >
                <Send className="h-4 w-4" />
              </Button>
            </form>
          </div>
        </Card>
      </div>
    </div>
  );
}
