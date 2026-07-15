import { useState, useRef, useCallback, useEffect } from "react";
import Seo from "@/components/Seo";
import AppShell from "@/components/AppShell";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Progress } from "@/components/ui/progress";
import { Textarea } from "@/components/ui/textarea";
import { useLocation } from "wouter";
import { useToast } from "@/hooks/use-toast";
import { apiRequest } from "@/lib/queryClient";
import { useBots } from "@/hooks/use-bots";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Input } from "@/components/ui/input";
import {
  Activity,
  AlertTriangle,
  ArrowUpRight,
  BookOpen,
  Bot,
  Braces,
  CheckCircle2,
  Clock,
  Code2,
  Copy,
  Database,
  Eye,
  FileCode2,
  FileSearch,
  CalendarClock,
  FolderUp,
  GitBranch,
  Key,
  KeyRound,
  Layers,
  Loader2,
  Lock,
  Package,
  Play,
  RefreshCw,
  Rocket,
  RotateCcw,
  Server,
  Shield,
  ShieldCheck,
  Sparkles,
  Square,
  Terminal,
  Trash2,
  TrendingUp,
  Upload,
  Wand2,
  XCircle,
  Zap,
} from "lucide-react";

const LANGUAGES = [
  { value: "typescript", label: "TypeScript" },
  { value: "javascript", label: "JavaScript" },
  { value: "python", label: "Python" },
  { value: "go", label: "Go" },
  { value: "rust", label: "Rust" },
  { value: "java", label: "Java" },
  { value: "c++", label: "C++" },
  { value: "c#", label: "C#" },
  { value: "ruby", label: "Ruby" },
  { value: "php", label: "PHP" },
  { value: "swift", label: "Swift" },
  { value: "kotlin", label: "Kotlin" },
  { value: "sql", label: "SQL" },
  { value: "html", label: "HTML" },
  { value: "css", label: "CSS" },
  { value: "solidity", label: "Solidity" },
];

const CODE_TEMPLATES: Record<string, string> = {
  typescript: `function fibonacci(n: number): number {
  if (n <= 1) return n;
  return fibonacci(n - 1) + fibonacci(n - 2);
}

for (let i = 0; i < 10; i++) {
  console.log(\`fib(\${i}) = \${fibonacci(i)}\`);
}`,
  javascript: `const greet = (name) => {
  return \`Hello, \${name}! Welcome to DreamCodeLab.\`;
};

console.log(greet("World"));
console.log(greet("DreamCo Empire"));`,
  python: `def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)

for i in range(1, 11):
    print(f"{i}! = {factorial(i)}")`,
  go: `package main

import "fmt"

func main() {
    for i := 1; i <= 10; i++ {
        fmt.Printf("%d squared = %d\\n", i, i*i)
    }
}`,
  rust: `fn main() {
    let numbers: Vec<i32> = (1..=10).collect();
    let sum: i32 = numbers.iter().sum();
    println!("Numbers: {:?}", numbers);
    println!("Sum: {}", sum);
}`,
};

interface OutputLine {
  type: "info" | "output" | "error" | "success";
  text: string;
  timestamp: string;
}

function VibeCodeEditor({ onRunBot }: { onRunBot?: (code: string, language: string) => void }) {
  const [language, setLanguage] = useState("typescript");
  const [code, setCode] = useState(CODE_TEMPLATES["typescript"] || "");
  const [vibePrompt, setVibePrompt] = useState("");
  const [output, setOutput] = useState<OutputLine[]>([]);
  const [isRunning, setIsRunning] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [streamText, setStreamText] = useState("");
  const outputRef = useRef<HTMLDivElement>(null);
  const abortRef = useRef<AbortController | null>(null);

  const now = () => new Date().toLocaleTimeString();

  const scrollToBottom = useCallback(() => {
    if (outputRef.current) {
      outputRef.current.scrollTop = outputRef.current.scrollHeight;
    }
  }, []);

  useEffect(() => { scrollToBottom(); }, [output, streamText, scrollToBottom]);

  const handleLanguageChange = (val: string) => {
    setLanguage(val);
    if (CODE_TEMPLATES[val]) {
      setCode(CODE_TEMPLATES[val]);
    }
  };

  const addOutput = useCallback((type: OutputLine["type"], text: string) => {
    setOutput(prev => [...prev, { type, text, timestamp: now() }]);
  }, []);

  const handleRun = useCallback(async () => {
    if (!code.trim()) return;
    setIsRunning(true);
    setStreamText("");
    addOutput("info", `Running ${language} code...`);

    abortRef.current = new AbortController();

    try {
      const response = await fetch("/api/code/run", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ code, language }),
        signal: abortRef.current.signal,
      });

      if (!response.ok) {
        throw new Error("Execution failed");
      }

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      let fullText = "";

      if (reader) {
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          const chunk = decoder.decode(value, { stream: true });
          const lines = chunk.split("\n");

          for (const line of lines) {
            if (line.startsWith("data: ")) {
              try {
                const data = JSON.parse(line.slice(6));
                if (data.content) {
                  fullText += data.content;
                  setStreamText(fullText);
                }
                if (data.done) {
                  const sections = fullText.split(/---(?:OUTPUT|ANALYSIS|SUGGESTIONS)---/);
                  for (const section of sections) {
                    const trimmed = section.trim();
                    if (trimmed) {
                      addOutput("output", trimmed);
                    }
                  }
                  addOutput("success", "Execution completed");
                  setStreamText("");
                }
                if (data.error) {
                  addOutput("error", data.error);
                  setStreamText("");
                }
              } catch {}
            }
          }
        }
      }
    } catch (err: any) {
      if (err.name !== "AbortError") {
        addOutput("error", err.message || "Execution failed");
      }
    } finally {
      setIsRunning(false);
      abortRef.current = null;
    }
  }, [code, language, addOutput]);

  const handleGenerate = useCallback(async () => {
    if (!vibePrompt.trim()) return;
    setIsGenerating(true);
    setStreamText("");
    addOutput("info", `Generating ${language} code: "${vibePrompt}"`);

    abortRef.current = new AbortController();

    try {
      const response = await fetch("/api/code/run", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt: vibePrompt, language }),
        signal: abortRef.current.signal,
      });

      if (!response.ok) throw new Error("Generation failed");

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      let fullText = "";

      if (reader) {
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          const chunk = decoder.decode(value, { stream: true });
          const lines = chunk.split("\n");

          for (const line of lines) {
            if (line.startsWith("data: ")) {
              try {
                const data = JSON.parse(line.slice(6));
                if (data.content) {
                  fullText += data.content;
                  setStreamText(fullText);
                }
                if (data.done) {
                  const codeMatch = fullText.match(/```[\w]*\n([\s\S]*?)```/);
                  if (codeMatch) {
                    setCode(codeMatch[1].trim());
                    addOutput("success", "Code generated and loaded into editor");
                  } else {
                    const outputSplit = fullText.split("---OUTPUT---");
                    if (outputSplit[0]) {
                      setCode(outputSplit[0].trim());
                      addOutput("success", "Code generated and loaded into editor");
                    }
                  }
                  setStreamText("");
                  setVibePrompt("");
                }
                if (data.error) {
                  addOutput("error", data.error);
                  setStreamText("");
                }
              } catch {}
            }
          }
        }
      }
    } catch (err: any) {
      if (err.name !== "AbortError") {
        addOutput("error", err.message || "Generation failed");
      }
    } finally {
      setIsGenerating(false);
      abortRef.current = null;
    }
  }, [vibePrompt, language, addOutput]);

  const handleStop = () => {
    abortRef.current?.abort();
    addOutput("info", "Stopped");
    setIsRunning(false);
    setIsGenerating(false);
    setStreamText("");
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(code);
    addOutput("info", "Code copied to clipboard");
  };

  const handleClear = () => {
    setOutput([]);
    setStreamText("");
  };

  const getOutputColor = (type: OutputLine["type"]) => {
    switch (type) {
      case "info": return "text-blue-400";
      case "output": return "text-green-300";
      case "error": return "text-red-400";
      case "success": return "text-emerald-400";
    }
  };

  const getOutputPrefix = (type: OutputLine["type"]) => {
    switch (type) {
      case "info": return "[info]";
      case "output": return "[out]";
      case "error": return "[err]";
      case "success": return "[ok]";
    }
  };

  return (
    <div className="space-y-4">
      <Card data-testid="card-vibe-prompt">
        <CardContent className="p-4">
          <div className="flex items-center gap-2 mb-3">
            <Wand2 className="h-4 w-4 text-primary" />
            <span className="text-sm font-semibold">Vibe Prompt</span>
            <Badge variant="secondary" className="rounded-full text-[10px]">AI-Powered</Badge>
          </div>
          <div className="flex gap-2">
            <Textarea
              placeholder="Describe what you want to build... e.g. 'a REST API with CRUD operations for a todo list' or 'a sorting algorithm comparison'"
              value={vibePrompt}
              onChange={(e) => setVibePrompt(e.target.value)}
              className="resize-none text-sm min-h-[60px]"
              data-testid="input-vibe-prompt"
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  handleGenerate();
                }
              }}
            />
            <div className="flex flex-col gap-1">
              <Button
                onClick={handleGenerate}
                disabled={isGenerating || !vibePrompt.trim()}
                data-testid="button-generate"
              >
                {isGenerating ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <Sparkles className="h-4 w-4" />
                )}
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <Card data-testid="card-code-editor">
          <CardHeader className="flex flex-row items-center justify-between gap-2 space-y-0 pb-3">
            <div className="flex items-center gap-2 flex-wrap">
              <CardTitle className="text-sm font-semibold">Editor</CardTitle>
              <Select value={language} onValueChange={handleLanguageChange}>
                <SelectTrigger className="w-[140px]" data-testid="select-language">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {LANGUAGES.map((lang) => (
                    <SelectItem key={lang.value} value={lang.value} data-testid={`lang-option-${lang.value}`}>
                      {lang.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="flex items-center gap-1 flex-wrap">
              <Button size="icon" variant="ghost" onClick={handleCopy} data-testid="button-copy-code">
                <Copy className="h-4 w-4" />
              </Button>
              {isRunning ? (
                <Button size="sm" variant="destructive" onClick={handleStop} data-testid="button-stop">
                  <Square className="h-3 w-3 mr-1.5" />Stop
                </Button>
              ) : (
                <div className="flex gap-1">
                  <Button size="sm" variant="outline" onClick={() => onRunBot?.(code, language)} data-testid="button-run-bot">
                    <Sparkles className="h-3 w-3 mr-1.5" />Run via Bot
                  </Button>
                  <Button size="sm" onClick={handleRun} disabled={!code.trim()} data-testid="button-run-code">
                    <Play className="h-3 w-3 mr-1.5" />Run
                  </Button>
                </div>
              )}
            </div>
          </CardHeader>
          <CardContent className="pb-4">
            <div className="relative">
              <Textarea
                value={code}
                onChange={(e) => setCode(e.target.value)}
                className="font-mono text-sm min-h-[350px] resize-none leading-relaxed"
                placeholder="Write your code here..."
                spellCheck={false}
                data-testid="textarea-code-editor"
              />
              <div className="absolute bottom-2 right-2 text-[10px] text-muted-foreground">
                {code.split("\n").length} lines
              </div>
            </div>
          </CardContent>
        </Card>

        <Card data-testid="card-output-panel">
          <CardHeader className="flex flex-row items-center justify-between gap-2 space-y-0 pb-3">
            <CardTitle className="text-sm font-semibold flex items-center gap-2">
              <Terminal className="h-4 w-4" />
              Output
              {isRunning && <Badge variant="secondary" className="rounded-full text-[10px]"><Loader2 className="h-2.5 w-2.5 mr-1 animate-spin" />Running</Badge>}
              {isGenerating && <Badge variant="secondary" className="rounded-full text-[10px]"><Loader2 className="h-2.5 w-2.5 mr-1 animate-spin" />Generating</Badge>}
            </CardTitle>
            <Button size="icon" variant="ghost" onClick={handleClear} data-testid="button-clear-output">
              <Trash2 className="h-4 w-4" />
            </Button>
          </CardHeader>
          <CardContent className="pb-4">
            <div
              ref={outputRef}
              className="bg-zinc-950 dark:bg-zinc-950 rounded-md p-3 font-mono text-xs min-h-[350px] max-h-[350px] overflow-y-auto space-y-1"
              data-testid="output-console"
            >
              {output.length === 0 && !streamText && (
                <div className="text-zinc-500 flex items-center gap-2 py-2">
                  <Terminal className="h-3 w-3" />
                  <span>Ready. Press Run or enter a Vibe Prompt to start.</span>
                </div>
              )}
              {output.map((line, i) => (
                <div key={i} className="flex gap-2 leading-relaxed">
                  <span className="text-zinc-600 flex-shrink-0 w-[50px] text-right">{line.timestamp.split(" ")[0]}</span>
                  <span className={`flex-shrink-0 w-[36px] ${getOutputColor(line.type)}`}>{getOutputPrefix(line.type)}</span>
                  <span className={`${getOutputColor(line.type)} whitespace-pre-wrap break-all`}>{line.text}</span>
                </div>
              ))}
              {streamText && (
                <div className="flex gap-2 leading-relaxed">
                  <span className="text-zinc-600 flex-shrink-0 w-[50px] text-right">{now().split(" ")[0]}</span>
                  <span className="flex-shrink-0 w-[36px] text-yellow-400">[...]</span>
                  <span className="text-yellow-300 whitespace-pre-wrap break-all">{streamText}</span>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

interface BatchItem {
  id: string;
  name: string;
  status: "pending" | "processing" | "done" | "error";
  result?: string;
  error?: string;
}

function BatchProcessor() {
  const [files, setFiles] = useState<File[]>([]);
  const [instruction, setInstruction] = useState("");
  const [language, setLanguage] = useState("typescript");
  const [batchItems, setBatchItems] = useState<BatchItem[]>([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [totalProcessed, setTotalProcessed] = useState(0);
  const [totalItems, setTotalItems] = useState(0);
  const [expandedItem, setExpandedItem] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const selected = Array.from(e.target.files).slice(0, 20);
      setFiles(prev => [...prev, ...selected].slice(0, 20));
    }
  };

  const removeFile = (index: number) => {
    setFiles(prev => prev.filter((_, i) => i !== index));
  };

  const handleProcess = async () => {
    if (!instruction.trim() && files.length === 0) return;
    setIsProcessing(true);
    setTotalProcessed(0);
    setBatchItems([]);
    setExpandedItem(null);

    const formData = new FormData();
    if (instruction.trim()) formData.append("instruction", instruction);
    formData.append("language", language);

    files.forEach((file) => {
      formData.append("files", file);
    });

    try {
      const response = await fetch("/api/batch/process", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const err = await response.json();
        throw new Error(err.error || "Batch processing failed");
      }

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();

      if (reader) {
        let buffer = "";
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split("\n");
          buffer = lines.pop() || "";

          for (const line of lines) {
            if (line.startsWith("data: ")) {
              try {
                const event = JSON.parse(line.slice(6));

                if (event.type === "started") {
                  setTotalItems(event.total);
                  setBatchItems(
                    Array.from({ length: event.total }, (_, i) => ({
                      id: `item-${i}`,
                      name: `Item ${i + 1}`,
                      status: "pending" as const,
                    }))
                  );
                }

                if (event.type === "processing") {
                  const itemName = event.item?.name || `Item ${(event.index ?? 0) + 1}`;
                  setBatchItems(prev => prev.map((item, i) =>
                    i === event.index ? { ...item, name: itemName, status: "processing" } : item
                  ));
                }

                if (event.type === "progress") {
                  setTotalProcessed(prev => prev + 1);
                  setBatchItems(prev => prev.map((item, i) =>
                    i === event.index
                      ? {
                          ...item,
                          status: event.error ? "error" : "done",
                          result: event.result || undefined,
                          error: event.error || undefined,
                        }
                      : item
                  ));
                }

                if (event.type === "complete") {
                  setIsProcessing(false);
                }

                if (event.type === "error") {
                  setIsProcessing(false);
                }
              } catch {}
            }
          }
        }
      }
    } catch (err: any) {
      setBatchItems(prev => prev.length > 0
        ? prev
        : [{ id: "error", name: "Error", status: "error", error: err.message }]
      );
    } finally {
      setIsProcessing(false);
    }
  };

  const handleClearAll = () => {
    setFiles([]);
    setInstruction("");
    setBatchItems([]);
    setTotalProcessed(0);
    setTotalItems(0);
    setExpandedItem(null);
  };

  const progressPercent = totalItems > 0 ? (totalProcessed / totalItems) * 100 : 0;

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <Card data-testid="stat-batch-mode">
          <CardHeader className="flex flex-row items-center justify-between gap-1 space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Mode</CardTitle>
            <Layers className="h-4 w-4 text-primary" />
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold">{files.length > 0 ? "File Upload" : instruction ? "Long Request" : "Ready"}</p>
            <p className="text-xs text-muted-foreground mt-1">
              {files.length > 0 ? `${files.length} file(s) queued` : "Upload files or enter a long request"}
            </p>
          </CardContent>
        </Card>
        <Card data-testid="stat-batch-queue">
          <CardHeader className="flex flex-row items-center justify-between gap-1 space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Queue</CardTitle>
            <FolderUp className="h-4 w-4 text-violet-500" />
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold">{totalItems > 0 ? `${totalProcessed}/${totalItems}` : "0"}</p>
            <p className="text-xs text-muted-foreground mt-1">
              {isProcessing ? "Processing..." : totalItems > 0 ? "Completed" : "No items in queue"}
            </p>
          </CardContent>
        </Card>
        <Card data-testid="stat-batch-success">
          <CardHeader className="flex flex-row items-center justify-between gap-1 space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Success Rate</CardTitle>
            <CheckCircle2 className="h-4 w-4 text-green-500" />
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold">
              {totalProcessed > 0
                ? `${Math.round((batchItems.filter(i => i.status === "done").length / totalProcessed) * 100)}%`
                : "--"}
            </p>
            <p className="text-xs text-muted-foreground mt-1">
              {batchItems.filter(i => i.status === "error").length > 0
                ? `${batchItems.filter(i => i.status === "error").length} failed`
                : "No errors"}
            </p>
          </CardContent>
        </Card>
      </div>

      <Card data-testid="card-batch-upload">
        <CardContent className="p-4 space-y-4">
          <div className="flex items-center gap-2 mb-1">
            <Upload className="h-4 w-4 text-primary" />
            <span className="text-sm font-semibold">Upload Files</span>
            <Badge variant="secondary" className="rounded-full text-[10px]">Up to 20 files</Badge>
          </div>

          <div
            className="border-2 border-dashed border-border/60 rounded-md p-6 text-center cursor-pointer hover-elevate"
            onClick={() => fileInputRef.current?.click()}
            data-testid="dropzone-files"
          >
            <input
              ref={fileInputRef}
              type="file"
              multiple
              className="hidden"
              onChange={handleFileSelect}
              accept=".ts,.tsx,.js,.jsx,.py,.go,.rs,.java,.kt,.swift,.cpp,.cs,.rb,.php,.sol,.sql,.json,.csv,.tsv,.yaml,.toml,.md,.html,.css,.txt"
              data-testid="input-file-upload"
            />
            <FolderUp className="h-8 w-8 text-muted-foreground mx-auto mb-2" />
            <p className="text-sm text-muted-foreground">Click to select files - code, CSV, JSON, text, and more</p>
            <p className="text-xs text-muted-foreground mt-1">Max 500KB per file, 20 files total</p>
          </div>

          {files.length > 0 && (
            <div className="space-y-1">
              {files.map((file, i) => (
                <div key={i} className="flex items-center justify-between gap-2 p-2 rounded-md border border-border/40" data-testid={`file-item-${i}`}>
                  <div className="flex items-center gap-2 min-w-0">
                    <FileCode2 className="h-4 w-4 text-muted-foreground flex-shrink-0" />
                    <span className="text-sm truncate">{file.name}</span>
                    <span className="text-xs text-muted-foreground flex-shrink-0">
                      {(file.size / 1024).toFixed(1)}KB
                    </span>
                  </div>
                  <Button size="icon" variant="ghost" onClick={() => removeFile(i)} data-testid={`button-remove-file-${i}`}>
                    <XCircle className="h-3 w-3" />
                  </Button>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      <Card data-testid="card-batch-instruction">
        <CardContent className="p-4 space-y-3">
          <div className="flex items-center gap-2">
            <Wand2 className="h-4 w-4 text-primary" />
            <span className="text-sm font-semibold">Instruction / Long Request</span>
          </div>
          <Textarea
            placeholder="Enter your instruction for processing files, or paste a long coding request here. Long requests are automatically split into manageable chunks and processed in sequence..."
            value={instruction}
            onChange={(e) => setInstruction(e.target.value)}
            className="resize-none text-sm min-h-[120px]"
            data-testid="textarea-batch-instruction"
          />
          <div className="flex items-center gap-2 flex-wrap">
            <Select value={language} onValueChange={setLanguage}>
              <SelectTrigger className="w-[140px]" data-testid="select-batch-language">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {LANGUAGES.map((lang) => (
                  <SelectItem key={lang.value} value={lang.value}>{lang.label}</SelectItem>
                ))}
              </SelectContent>
            </Select>
            <div className="flex-1" />
            <Button variant="outline" onClick={handleClearAll} disabled={isProcessing} data-testid="button-batch-clear">
              <Trash2 className="h-4 w-4 mr-1.5" />Clear All
            </Button>
            <Button onClick={handleProcess} disabled={isProcessing || (!instruction.trim() && files.length === 0)} data-testid="button-batch-process">
              {isProcessing ? (
                <Loader2 className="h-4 w-4 mr-1.5 animate-spin" />
              ) : (
                <Play className="h-4 w-4 mr-1.5" />
              )}
              {isProcessing ? "Processing..." : "Process Batch"}
            </Button>
          </div>
        </CardContent>
      </Card>

      {batchItems.length > 0 && (
        <Card data-testid="card-batch-results">
          <CardHeader className="flex flex-row items-center justify-between gap-2 space-y-0">
            <CardTitle className="text-sm font-semibold flex items-center gap-2">
              <Terminal className="h-4 w-4" />
              Batch Results
              {isProcessing && <Badge variant="secondary" className="rounded-full text-[10px]"><Loader2 className="h-2.5 w-2.5 mr-1 animate-spin" />Processing</Badge>}
            </CardTitle>
            <span className="text-xs text-muted-foreground">{totalProcessed}/{totalItems} completed</span>
          </CardHeader>
          <CardContent className="space-y-2">
            {totalItems > 0 && (
              <Progress value={progressPercent} className="h-2 mb-3" data-testid="progress-batch" />
            )}
            <div className="space-y-2 max-h-[500px] overflow-y-auto">
              {batchItems.map((item) => (
                <div key={item.id} className="rounded-md border border-border/40" data-testid={`batch-result-${item.id}`}>
                  <div
                    className="flex items-center justify-between gap-2 p-3 cursor-pointer hover-elevate"
                    onClick={() => setExpandedItem(expandedItem === item.id ? null : item.id)}
                    data-testid={`batch-result-toggle-${item.id}`}
                  >
                    <div className="flex items-center gap-2 min-w-0">
                      {item.status === "pending" && <Clock className="h-4 w-4 text-muted-foreground flex-shrink-0" />}
                      {item.status === "processing" && <Loader2 className="h-4 w-4 text-yellow-500 animate-spin flex-shrink-0" />}
                      {item.status === "done" && <CheckCircle2 className="h-4 w-4 text-green-500 flex-shrink-0" />}
                      {item.status === "error" && <XCircle className="h-4 w-4 text-red-500 flex-shrink-0" />}
                      <span className="text-sm font-medium truncate">{item.name}</span>
                    </div>
                    <Badge
                      variant={item.status === "done" ? "default" : item.status === "error" ? "destructive" : "secondary"}
                      className="rounded-full text-[10px] flex-shrink-0"
                    >
                      {item.status === "processing" ? "Running" : item.status}
                    </Badge>
                  </div>
                  {expandedItem === item.id && (item.result || item.error) && (
                    <div className="border-t border-border/40 p-3">
                      <div className="bg-zinc-950 rounded-md p-3 font-mono text-xs max-h-[300px] overflow-y-auto whitespace-pre-wrap text-zinc-300">
                        {item.result || item.error}
                      </div>
                      {item.result && (
                        <Button
                          size="sm"
                          variant="outline"
                          className="mt-2"
                          onClick={() => navigator.clipboard.writeText(item.result || "")}
                          data-testid={`button-copy-result-${item.id}`}
                        >
                          <Copy className="h-3 w-3 mr-1.5" />Copy Result
                        </Button>
                      )}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}

const SCAN_ISSUES = [
  { severity: "critical", count: 3, color: "text-red-500" },
  { severity: "warning", count: 12, color: "text-yellow-500" },
  { severity: "info", count: 27, color: "text-blue-500" },
];

const SUPPORTED_FILE_TYPES = [
  ".ts", ".tsx", ".js", ".jsx", ".py", ".go", ".rs", ".java",
  ".kt", ".swift", ".cpp", ".cs", ".rb", ".php", ".dart", ".json",
  ".yaml", ".toml", ".sql", ".graphql", ".sol", ".md", ".html", ".css",
];

const DEPLOYMENTS = [
  { id: 1, name: "dreamco-web", env: "production", status: "deployed", time: "12 min ago", version: "v3.4.1" },
  { id: 2, name: "api-service", env: "staging", status: "building", time: "2 min ago", version: "v2.9.0-rc1" },
  { id: 3, name: "worker-queue", env: "production", status: "deployed", time: "1 hr ago", version: "v1.8.3" },
  { id: 4, name: "auth-gateway", env: "production", status: "failed", time: "35 min ago", version: "v4.0.0-beta" },
  { id: 5, name: "analytics-svc", env: "staging", status: "deployed", time: "4 hr ago", version: "v2.1.0" },
  { id: 6, name: "ml-inference", env: "development", status: "building", time: "8 min ago", version: "v0.5.2" },
];

const SECRET_TYPES = [
  { title: "API Keys", count: 24, icon: Key, rotationDays: 30, lastAccess: "2 min ago" },
  { title: "Database Credentials", count: 8, icon: Database, rotationDays: 90, lastAccess: "15 min ago" },
  { title: "OAuth Tokens", count: 12, icon: ShieldCheck, rotationDays: 14, lastAccess: "1 hr ago" },
  { title: "Encryption Keys", count: 6, icon: Lock, rotationDays: 180, lastAccess: "3 hr ago" },
];

const ACCESS_LOGS = [
  { user: "deploy-bot", secret: "STRIPE_SECRET_KEY", action: "read", time: "2 min ago" },
  { user: "ci-pipeline", secret: "DATABASE_URL", action: "read", time: "5 min ago" },
  { user: "admin", secret: "OPENAI_API_KEY", action: "rotate", time: "1 hr ago" },
  { user: "deploy-bot", secret: "AWS_ACCESS_KEY", action: "read", time: "2 hr ago" },
  { user: "ci-pipeline", secret: "GITHUB_TOKEN", action: "read", time: "3 hr ago" },
];

function getStatusBadge(status: string) {
  switch (status) {
    case "active":
      return <Badge variant="default" className="rounded-full"><Activity className="h-3 w-3 mr-1" />Active</Badge>;
    case "paused":
      return <Badge variant="secondary" className="rounded-full"><Clock className="h-3 w-3 mr-1" />Paused</Badge>;
    case "idle":
      return <Badge variant="outline" className="rounded-full"><Clock className="h-3 w-3 mr-1" />Idle</Badge>;
    case "deployed":
      return <Badge variant="default" className="rounded-full"><CheckCircle2 className="h-3 w-3 mr-1" />Deployed</Badge>;
    case "building":
      return <Badge variant="secondary" className="rounded-full"><RefreshCw className="h-3 w-3 mr-1 animate-spin" />Building</Badge>;
    case "failed":
      return <Badge variant="destructive" className="rounded-full"><XCircle className="h-3 w-3 mr-1" />Failed</Badge>;
    default:
      return <Badge variant="outline" className="rounded-full">{status}</Badge>;
  }
}

export default function CodeLabPage() {
  const [botSlug, setBotSlug] = useState<string | undefined>(undefined);
  const { toast } = useToast();
  const [, setLocation] = useLocation();
  const { data: botsList } = useBots();
  const totalSecrets = SECRET_TYPES.reduce((s, t) => s + t.count, 0);

  const handleScan = () => {
    toast({ title: "Scanning codebase...", description: "AI is analyzing your files for security issues and tech debt." });
  };

  const handleDeploy = (name: string) => {
    toast({ title: `Deploying ${name}...`, description: "Initiating build process and provisioning resources." });
  };

  const handleRunBot = async (code: string, language: string) => {
    const codeBot = botsList?.find(b => b.slug.includes("code") || b.division === "DreamCodeLab") || botsList?.[0];
    if (codeBot) {
      const res = await apiRequest("POST", "/api/conversations", { 
        title: `Code Execution: ${language}`,
      });
      const convo = await res.json();
      
      // Navigate to conversation and pass code as initial message
      setLocation(`/c/${convo.id}?bot=${codeBot.slug}&initialMessage=${encodeURIComponent("Please review and run this code:\n\n```" + language + "\n" + code + "\n```")}`);
    } else {
      toast({ title: "Code bot not found", description: "Navigating to Bot Fleet...", variant: "destructive" });
      setLocation("/bots");
    }
  };

  return (
    <AppShell selectedBotSlug={botSlug} onBotChange={setBotSlug}>
      <Seo title="Code Lab - DreamCodeLab" description="Vibe coding, code reading, and AI development tools for DreamCo." />

      <div className="buddy-card buddy-noise buddy-appear overflow-hidden">
        <div className="px-5 pt-6 pb-5 md:px-8 md:pt-8 md:pb-6 border-b border-border/60">
          <div className="flex flex-wrap items-center justify-between gap-4">
            <div>
              <h1 className="text-2xl md:text-3xl" data-testid="text-codelab-title">Code Lab</h1>
              <p className="text-sm text-muted-foreground mt-1">Vibe coding, code reading & AI development tools</p>
            </div>
            <div className="flex items-center gap-3 flex-wrap">
              <Badge variant="secondary" className="rounded-full">
                <Terminal className="h-3 w-3 mr-1.5 text-primary" />
                DreamCodeLab
              </Badge>
              <Badge variant="secondary" className="rounded-full">
                <Activity className="h-3 w-3 mr-1.5 text-green-500" />
                Online
              </Badge>
            </div>
          </div>
        </div>

        <div className="p-5 md:p-8 space-y-8 buddy-stagger">
          <Tabs defaultValue="vibe-code" data-testid="tabs-codelab">
            <TabsList className="flex flex-wrap gap-1" data-testid="tabslist-codelab">
              <TabsTrigger value="vibe-code" data-testid="tab-vibe-code">
                <Sparkles className="h-4 w-4 mr-1.5" />Vibe Code
              </TabsTrigger>
              <TabsTrigger value="code-reader" data-testid="tab-code-reader">
                <BookOpen className="h-4 w-4 mr-1.5" />Code Reader
              </TabsTrigger>
              <TabsTrigger value="deploy" data-testid="tab-deploy">
                <Rocket className="h-4 w-4 mr-1.5" />Deploy
              </TabsTrigger>
              <TabsTrigger value="secrets" data-testid="tab-secrets">
                <Shield className="h-4 w-4 mr-1.5" />Secrets
              </TabsTrigger>
              <TabsTrigger value="batch" data-testid="tab-batch">
                <Layers className="h-4 w-4 mr-1.5" />Batch
              </TabsTrigger>
            </TabsList>

            <TabsContent value="vibe-code" className="space-y-4 mt-6">
              <VibeCodeEditor onRunBot={handleRunBot} />
            </TabsContent>

            <TabsContent value="code-reader" className="space-y-6 mt-6">
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                <Card data-testid="stat-files-analyzed">
                  <CardHeader className="flex flex-row items-center justify-between gap-1 space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium text-muted-foreground">Files Analyzed</CardTitle>
                    <FileSearch className="h-4 w-4 text-primary" />
                  </CardHeader>
                  <CardContent>
                    <p className="text-2xl font-bold">8,492</p>
                  </CardContent>
                </Card>
                <Card data-testid="stat-code-quality">
                  <CardHeader className="flex flex-row items-center justify-between gap-1 space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium text-muted-foreground">Code Quality Score</CardTitle>
                    <CheckCircle2 className="h-4 w-4 text-green-500" />
                  </CardHeader>
                  <CardContent>
                    <p className="text-2xl font-bold">A-</p>
                    <p className="text-xs text-green-600 dark:text-green-400 mt-1">Top 15% of scanned repos</p>
                  </CardContent>
                </Card>
                <Card data-testid="stat-security-vulns">
                  <CardHeader className="flex flex-row items-center justify-between gap-1 space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium text-muted-foreground">Security Vulnerabilities</CardTitle>
                    <AlertTriangle className="h-4 w-4 text-yellow-500" />
                  </CardHeader>
                  <CardContent>
                    <p className="text-2xl font-bold">7</p>
                    <p className="text-xs text-muted-foreground mt-1">3 critical, 4 moderate</p>
                  </CardContent>
                </Card>
                <Card data-testid="stat-tech-debt">
                  <CardHeader className="flex flex-row items-center justify-between gap-1 space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium text-muted-foreground">Tech Debt</CardTitle>
                    <Clock className="h-4 w-4 text-orange-500" />
                  </CardHeader>
                  <CardContent>
                    <p className="text-2xl font-bold">42h</p>
                    <p className="text-xs text-muted-foreground mt-1">Estimated remediation</p>
                  </CardContent>
                </Card>
              </div>

              <Card data-testid="card-scan-results">
                <CardHeader className="flex flex-row items-center justify-between gap-2 space-y-0">
                  <CardTitle className="text-base flex items-center gap-2">
                    <FileSearch className="h-5 w-5 text-primary" />
                    Scan Results
                  </CardTitle>
                  <Button size="sm" onClick={handleScan} data-testid="button-rescan">
                    <RefreshCw className="h-4 w-4 mr-1.5" />Re-scan
                  </Button>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {SCAN_ISSUES.map((issue) => (
                      <div key={issue.severity} className="flex items-center justify-between gap-3 p-3 rounded-lg border border-border/40">
                        <div className="flex items-center gap-3">
                          <AlertTriangle className={`h-4 w-4 ${issue.color}`} />
                          <span className="text-sm font-medium capitalize">{issue.severity}</span>
                        </div>
                        <Badge variant="outline" className="rounded-full">{issue.count} issues</Badge>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              <div>
                <h3 className="text-base font-semibold mb-3" data-testid="text-supported-filetypes">Supported File Types</h3>
                <div className="flex flex-wrap gap-2">
                  {SUPPORTED_FILE_TYPES.map((ft) => (
                    <Badge key={ft} variant="outline" className="rounded-full font-mono text-xs" data-testid={`filetype-badge-${ft.replace(".", "")}`}>
                      {ft}
                    </Badge>
                  ))}
                </div>
              </div>
            </TabsContent>

            <TabsContent value="deploy" className="space-y-6 mt-6">
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <Card data-testid="stat-total-deployments">
                  <CardHeader className="flex flex-row items-center justify-between gap-1 space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium text-muted-foreground">Total Deployments</CardTitle>
                    <Package className="h-4 w-4 text-primary" />
                  </CardHeader>
                  <CardContent>
                    <p className="text-2xl font-bold">1,847</p>
                    <p className="text-xs text-muted-foreground mt-1">All time</p>
                  </CardContent>
                </Card>
                <Card data-testid="stat-success-rate">
                  <CardHeader className="flex flex-row items-center justify-between gap-1 space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium text-muted-foreground">Success Rate</CardTitle>
                    <CheckCircle2 className="h-4 w-4 text-green-500" />
                  </CardHeader>
                  <CardContent>
                    <p className="text-2xl font-bold">97.8%</p>
                    <p className="text-xs text-green-600 dark:text-green-400 mt-1 flex items-center gap-1">
                      <TrendingUp className="h-3 w-3" /> +1.2% this week
                    </p>
                  </CardContent>
                </Card>
                <Card data-testid="stat-avg-build-time">
                  <CardHeader className="flex flex-row items-center justify-between gap-1 space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium text-muted-foreground">Avg Build Time</CardTitle>
                    <Clock className="h-4 w-4 text-violet-500" />
                  </CardHeader>
                  <CardContent>
                    <p className="text-2xl font-bold">2m 14s</p>
                    <p className="text-xs text-muted-foreground mt-1">Across all environments</p>
                  </CardContent>
                </Card>
              </div>

              <div>
                <h3 className="text-base font-semibold mb-3" data-testid="text-active-deployments">Active Deployments</h3>
                <div className="space-y-2">
                  {DEPLOYMENTS.map((dep) => (
                    <Card key={dep.id} data-testid={`deploy-card-${dep.id}`}>
                      <CardContent className="p-4">
                        <div className="flex items-center justify-between gap-3">
                          <div className="flex items-center gap-3 min-w-0">
                            <Server className="h-4 w-4 text-muted-foreground flex-shrink-0" />
                            <div className="min-w-0">
                              <p className="text-sm font-semibold truncate">{dep.name}</p>
                              <div className="flex items-center gap-2 mt-0.5 flex-wrap">
                                <span className="text-xs text-muted-foreground">{dep.version}</span>
                                <Badge variant="outline" className="rounded-full text-[10px]">{dep.env}</Badge>
                              </div>
                            </div>
                          </div>
                          <div className="flex items-center gap-3 flex-shrink-0">
                            <span className="text-xs text-muted-foreground hidden sm:inline">{dep.time}</span>
                            {getStatusBadge(dep.status)}
                            <Button size="icon" variant="ghost" onClick={() => handleDeploy(dep.name)} data-testid={`button-deploy-action-${dep.id}`}>
                              <Rocket className="h-4 w-4" />
                            </Button>
                            {dep.status === "deployed" && (
                              <Button size="sm" variant="outline" onClick={() => handleDeploy(dep.name)} data-testid={`button-rollback-${dep.id}`}>
                                <RotateCcw className="h-3 w-3 mr-1" />Rollback
                              </Button>
                            )}
                            {dep.status === "failed" && (
                              <Button size="sm" onClick={() => handleDeploy(dep.name)} data-testid={`button-retry-${dep.id}`}>
                                <RefreshCw className="h-3 w-3 mr-1" />Retry
                              </Button>
                            )}
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </div>

              <Card data-testid="card-deploy-frequency">
                <CardHeader>
                  <CardTitle className="text-base flex items-center gap-2">
                    <GitBranch className="h-5 w-5 text-primary" />
                    Deployment Frequency (Last 7 Days)
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex items-end gap-2 h-32">
                    {[12, 8, 15, 22, 18, 9, 14].map((val, i) => {
                      const days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];
                      return (
                        <div key={i} className="flex-1 flex flex-col items-center gap-1">
                          <div
                            className="w-full bg-primary/20 dark:bg-primary/30 rounded-md"
                            style={{ height: `${(val / 22) * 100}%` }}
                          />
                          <span className="text-[10px] text-muted-foreground">{days[i]}</span>
                        </div>
                      );
                    })}
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="secrets" className="space-y-6 mt-6">
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <Card data-testid="stat-total-secrets">
                  <CardHeader className="flex flex-row items-center justify-between gap-1 space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium text-muted-foreground">Total Secrets</CardTitle>
                    <KeyRound className="h-4 w-4 text-primary" />
                  </CardHeader>
                  <CardContent>
                    <p className="text-2xl font-bold">{totalSecrets}</p>
                    <p className="text-xs text-muted-foreground mt-1">Across 4 categories</p>
                  </CardContent>
                </Card>
                <Card data-testid="stat-next-rotation">
                  <CardHeader className="flex flex-row items-center justify-between gap-1 space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium text-muted-foreground">Next Rotation</CardTitle>
                    <CalendarClock className="h-4 w-4 text-orange-500" />
                  </CardHeader>
                  <CardContent>
                    <p className="text-2xl font-bold">3 days</p>
                    <p className="text-xs text-muted-foreground mt-1">OAuth tokens (12 keys)</p>
                  </CardContent>
                </Card>
                <Card data-testid="stat-access-events">
                  <CardHeader className="flex flex-row items-center justify-between gap-1 space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium text-muted-foreground">Access Events (24h)</CardTitle>
                    <Eye className="h-4 w-4 text-violet-500" />
                  </CardHeader>
                  <CardContent>
                    <p className="text-2xl font-bold">284</p>
                    <p className="text-xs text-green-600 dark:text-green-400 mt-1">All authorized</p>
                  </CardContent>
                </Card>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {SECRET_TYPES.map((st) => (
                  <Card key={st.title} data-testid={`secret-type-${st.title.toLowerCase().replace(/\s+/g, "-")}`}>
                    <CardContent className="p-4">
                      <div className="flex items-start justify-between gap-3">
                        <div className="flex items-center gap-3">
                          <div className="h-9 w-9 rounded-lg bg-primary/10 flex items-center justify-center flex-shrink-0">
                            <st.icon className="h-4 w-4 text-primary" />
                          </div>
                          <div>
                            <p className="text-sm font-semibold">{st.title}</p>
                            <p className="text-xs text-muted-foreground mt-0.5">{st.count} secrets stored</p>
                          </div>
                        </div>
                        <div className="text-right flex-shrink-0">
                          <Badge variant="outline" className="rounded-full text-[10px]">
                            <RefreshCw className="h-2.5 w-2.5 mr-1" />{st.rotationDays}d cycle
                          </Badge>
                        </div>
                      </div>
                      <div className="mt-3 text-xs text-muted-foreground flex items-center gap-1">
                        <Clock className="h-3 w-3" /> Last accessed {st.lastAccess}
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>

              <Card data-testid="card-access-logs">
                <CardHeader className="flex flex-row items-center justify-between gap-2 space-y-0">
                  <CardTitle className="text-base flex items-center gap-2">
                    <Eye className="h-5 w-5 text-primary" />
                    Recent Access Logs
                  </CardTitle>
                  <Button size="sm" variant="outline" data-testid="button-view-all-logs">
                    View All
                  </Button>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    {ACCESS_LOGS.map((log, i) => (
                      <div key={i} className="flex items-center justify-between gap-3 p-3 rounded-lg border border-border/40" data-testid={`access-log-${i}`}>
                        <div className="flex items-center gap-3 min-w-0">
                          <Shield className="h-4 w-4 text-muted-foreground flex-shrink-0" />
                          <div className="min-w-0">
                            <p className="text-sm font-medium truncate">{log.secret}</p>
                            <p className="text-xs text-muted-foreground">{log.user} - {log.action}</p>
                          </div>
                        </div>
                        <span className="text-xs text-muted-foreground flex-shrink-0">{log.time}</span>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="batch" className="space-y-4 mt-6">
              <BatchProcessor />
            </TabsContent>
          </Tabs>

          <Card data-testid="card-pricing-note">
            <CardContent className="p-4 flex items-center gap-3">
              <ArrowUpRight className="h-4 w-4 text-primary flex-shrink-0" />
              <p className="text-sm text-muted-foreground">
                Same fees as Replit - transparent and fair. No hidden costs for code generation, analysis, deployments, or secret management.
              </p>
            </CardContent>
          </Card>
        </div>
      </div>
    </AppShell>
  );
}
