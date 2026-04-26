import { useState } from "react";
import AppShell from "@/components/AppShell";
import Seo from "@/components/Seo";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useToast } from "@/hooks/use-toast";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { apiRequest } from "@/lib/queryClient";
import { DIVISIONS } from "@shared/schema";
import { Sparkles, X, Plus, Loader2, Save, Code, BrainCircuit, Wrench, ChevronDown, ChevronUp } from "lucide-react";
import { cn } from "@/lib/utils";

const LIBRARY_CATEGORIES: Record<string, string[]> = {
  "JavaScript / TypeScript": ["TypeScript","JavaScript ES2024","Node.js","Deno","Bun","RxJS","Zod","Lodash","Ramda","fp-ts","date-fns","Day.js","Axios","Socket.io","WebSockets","WebRTC"],
  "React Ecosystem": ["React 19","Next.js 15","React Native","Expo","TanStack Query","Redux Toolkit","Zustand","Jotai","Valtio","XState","React Navigation","Reanimated","React Three Fiber"],
  "Vue / Nuxt": ["Vue 3","Nuxt 4","Pinia","Vuex","VueUse","Vue Router","Vite Plugin Vue"],
  "Other Frontend": ["Angular 17","Svelte 5","SvelteKit","SolidJS","Qwik","Astro","Lit","Alpine.js","HTMX","Preact","Ember.js"],
  "Styling": ["TailwindCSS 4","Styled Components","Emotion","CSS Modules","Sass/SCSS","Vanilla Extract","UnoCSS","Panda CSS","StyleX"],
  "UI Libraries": ["shadcn/ui","Radix UI","Material UI","Chakra UI","Mantine","Ant Design","DaisyUI","PrimeReact","NextUI","Tremor","Headless UI"],
  "Animation / 3D": ["Framer Motion","GSAP","AnimeJS","Lottie","Three.js","Babylon.js","Pixi.js","p5.js","React Spring"],
  "Build Tools": ["Vite","Webpack 5","Rollup","esbuild","Turbopack","SWC","Babel","Biome","Parcel"],
  "Testing": ["Vitest","Jest","Playwright","Cypress","Testing Library","Storybook","MSW","k6","Supertest"],
  "Node.js Backend": ["Express 5","Fastify","NestJS","Hono","ElysiaJS","Koa","Hapi","AdonisJS","Feathers.js"],
  "Python Web": ["FastAPI","Django 5","Flask 3","Starlette","Litestar","Tornado","Sanic","aiohttp"],
  "Python Data / ML": ["NumPy","Pandas","Polars","Scikit-learn","PyTorch","TensorFlow","Keras","JAX","FastAI","XGBoost","LightGBM","Matplotlib","Seaborn","Plotly"],
  "AI / LLM SDKs": ["OpenAI SDK","Anthropic SDK","Vercel AI SDK","LangChain","LlamaIndex","Hugging Face Transformers","Diffusers","TensorFlow.js","Transformers.js","AutoGen","CrewAI","DSPy"],
  "Databases & ORMs": ["Drizzle ORM","Prisma","Mongoose","TypeORM","Sequelize","Kysely","SQLAlchemy","Diesel (Rust)","GORM (Go)","SQLx"],
  "Databases Direct": ["PostgreSQL","MySQL","SQLite","MongoDB","Redis","DynamoDB","Supabase","Firebase","Neon","Turso","ClickHouse"],
  "GraphQL": ["Apollo Client","Apollo Server","GraphQL Yoga","tRPC","urql","Pothos","TypeGraphQL","Hasura"],
  "Auth": ["Auth.js / NextAuth","Lucia","Clerk","Supabase Auth","Firebase Auth","Passport.js","Better Auth","WorkOS","Auth0"],
  "Payments": ["Stripe","Paddle","LemonSqueezy","PayPal SDK","Square","RevenueCat"],
  "Cloud SDKs": ["AWS SDK v3","Azure SDK","GCP Client Libraries","Cloudflare Workers","Vercel SDK","Supabase JS","Firebase Admin"],
  "DevOps": ["Docker","Kubernetes","Helm","Terraform","Pulumi","Ansible","GitHub Actions","ArgoCD","Flux CD"],
  "Rust": ["Tokio","Axum","Actix-web","Serde","SQLx (Rust)","Diesel","Tauri","Bevy","wasm-bindgen"],
  "Go": ["Gin","Echo","Fiber","Chi","GORM","grpc-go","Cobra","Bubble Tea"],
  "Java / Kotlin": ["Spring Boot","Spring WebFlux","Hibernate","Ktor","Jetpack Compose","Coroutines","Retrofit","Room"],
  "C# / .NET": ["ASP.NET Core","Entity Framework Core","SignalR","Blazor","MAUI","MediatR","FastEndpoints"],
  "Mobile": ["SwiftUI","UIKit","Jetpack Compose","Flutter","MAUI","Capacitor","Ionic","React Native"],
  "Desktop": ["Electron","Tauri","NW.js","Flutter Desktop"],
  "Blockchain / Web3": ["ethers.js","viem","wagmi","Hardhat","Foundry","Anchor (Solana)","OpenZeppelin","Chainlink"],
  "Game Dev": ["Phaser.js","Babylon.js","Unity (C#)","Godot","Pygame","Bevy"],
  "Observability": ["OpenTelemetry","Sentry","Datadog","PostHog","Prometheus","Grafana"],
  "Search": ["Elasticsearch","Algolia","MeiliSearch","Typesense","Fuse.js","Pinecone","Weaviate"],
  "Queues / Cache": ["Redis (ioredis)","BullMQ","RabbitMQ","Kafka (kafkajs)","Upstash","BullMQ"],
  "Rich Text / Editors": ["TipTap","Lexical","ProseMirror","CodeMirror 6","Monaco Editor","Quill"],
  "Visualization": ["D3.js","Recharts","Chart.js","ECharts","Plotly.js","Highcharts","Victory"],
  "CLI Tools": ["commander.js","clack","yargs","inquirer","chalk","ora","zx"],
  "File / Media": ["Sharp","FFmpeg","PDFKit","Puppeteer","ExcelJS","pdf-lib","docx","Multer"],
};

export default function BotBuilderPage() {
  const { toast } = useToast();
  const qc = useQueryClient();

  const [selectedBotSlug, setSelectedBotSlug] = useState<string | undefined>();
  const [botName, setBotName] = useState("");
  const [division, setDivision] = useState<string>("DreamCodeLab");
  const [description, setDescription] = useState("");
  const [selectedLibs, setSelectedLibs] = useState<string[]>([]);
  const [generatedBot, setGeneratedBot] = useState<any>(null);
  const [expandedCats, setExpandedCats] = useState<Record<string, boolean>>({ "JavaScript / TypeScript": true, "React Ecosystem": true });

  const generate = useMutation({
    mutationFn: () => apiRequest("POST", "/api/bot-builder/generate", { name: botName, division, description, libraries: selectedLibs }),
    onSuccess: (data: any) => {
      setGeneratedBot(data.bot);
      toast({ title: "Bot generated!", description: `${data.bot.displayName} is ready to save.` });
    },
    onError: (e: any) => toast({ title: "Generation failed", description: e.message, variant: "destructive" }),
  });

  const save = useMutation({
    mutationFn: () => apiRequest("POST", "/api/bot-builder/save", { bot: generatedBot }),
    onSuccess: (data: any) => {
      toast({ title: `Bot ${data.action}!`, description: `${generatedBot?.displayName} added to your fleet.` });
      qc.invalidateQueries({ queryKey: ["/api/bots"] });
      setGeneratedBot(null);
      setBotName("");
      setDescription("");
      setSelectedLibs([]);
    },
    onError: (e: any) => toast({ title: "Save failed", description: e.message, variant: "destructive" }),
  });

  function toggleLib(lib: string) {
    setSelectedLibs(prev => prev.includes(lib) ? prev.filter(l => l !== lib) : [...prev, lib]);
  }

  function toggleCat(cat: string) {
    setExpandedCats(prev => ({ ...prev, [cat]: !prev[cat] }));
  }

  return (
    <AppShell selectedBotSlug={selectedBotSlug} onBotChange={setSelectedBotSlug}>
      <Seo title="Bot Builder — DreamCo Empire OS" description="Build AI bots from any coding library" />

      <div className="buddy-appear space-y-6">
        <div>
          <h2 className="text-3xl md:text-4xl" data-testid="bot-builder-title">Bot Builder</h2>
          <p className="mt-1 text-muted-foreground">Select libraries → configure → AI generates a production-ready bot → deploy to your fleet</p>
        </div>

        <div className="grid grid-cols-1 xl:grid-cols-[1fr_380px] gap-6">

          {/* LEFT — Library Browser */}
          <div className="space-y-4">
            <Card className="buddy-card rounded-2xl border-border/60 p-4">
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2">
                  <Code className="h-4 w-4 text-primary" />
                  <span className="font-semibold text-sm">Library Browser</span>
                  <Badge variant="secondary" className="rounded-full text-xs">{Object.values(LIBRARY_CATEGORIES).flat().length}+ libs</Badge>
                </div>
                {selectedLibs.length > 0 && (
                  <button onClick={() => setSelectedLibs([])} className="text-xs text-muted-foreground hover:text-destructive transition-colors">
                    Clear all ({selectedLibs.length})
                  </button>
                )}
              </div>

              {/* Selected chips */}
              {selectedLibs.length > 0 && (
                <div className="flex flex-wrap gap-1.5 mb-4 p-3 rounded-xl bg-primary/5 border border-primary/20">
                  {selectedLibs.map(lib => (
                    <button key={lib} onClick={() => toggleLib(lib)} className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg bg-primary text-primary-foreground text-xs font-medium hover:bg-primary/80 transition-colors" data-testid={`selected-lib-${lib}`}>
                      {lib} <X className="h-3 w-3" />
                    </button>
                  ))}
                </div>
              )}

              <div className="space-y-2 max-h-[520px] overflow-y-auto pr-1">
                {Object.entries(LIBRARY_CATEGORIES).map(([cat, libs]) => (
                  <div key={cat} className="rounded-xl border border-border/50 overflow-hidden">
                    <button onClick={() => toggleCat(cat)} className="w-full flex items-center justify-between px-3 py-2.5 bg-card/60 hover:bg-card transition-colors text-sm font-medium" data-testid={`category-${cat}`}>
                      <span>{cat}</span>
                      <div className="flex items-center gap-2">
                        <span className="text-xs text-muted-foreground">{libs.filter(l => selectedLibs.includes(l)).length}/{libs.length}</span>
                        {expandedCats[cat] ? <ChevronUp className="h-3.5 w-3.5 text-muted-foreground" /> : <ChevronDown className="h-3.5 w-3.5 text-muted-foreground" />}
                      </div>
                    </button>
                    {expandedCats[cat] && (
                      <div className="p-2 flex flex-wrap gap-1.5">
                        {libs.map(lib => (
                          <button key={lib} onClick={() => toggleLib(lib)} className={cn("px-2.5 py-1 rounded-lg text-xs font-medium border transition-all", selectedLibs.includes(lib) ? "bg-primary text-primary-foreground border-primary shadow-sm" : "bg-card/40 border-border/60 text-muted-foreground hover:text-foreground hover:border-border hover:bg-card")} data-testid={`lib-${lib}`}>
                            {lib}
                          </button>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </Card>
          </div>

          {/* RIGHT — Bot Config + Preview */}
          <div className="space-y-4">
            <Card className="buddy-card rounded-2xl border-border/60 p-5">
              <div className="flex items-center gap-2 mb-4">
                <Wrench className="h-4 w-4 text-primary" />
                <span className="font-semibold text-sm">Bot Configuration</span>
              </div>

              <div className="space-y-3">
                <div>
                  <label className="text-xs font-medium text-muted-foreground mb-1.5 block">Bot Name *</label>
                  <Input value={botName} onChange={e => setBotName(e.target.value)} placeholder="e.g. FastAPI + PyTorch Expert" className="rounded-xl" data-testid="bot-name-input" />
                </div>

                <div>
                  <label className="text-xs font-medium text-muted-foreground mb-1.5 block">Division</label>
                  <Select value={division} onValueChange={setDivision}>
                    <SelectTrigger className="rounded-xl" data-testid="division-select">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent className="max-h-[200px]">
                      {DIVISIONS.map(d => <SelectItem key={d} value={d}>{d}</SelectItem>)}
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <label className="text-xs font-medium text-muted-foreground mb-1.5 block">Description (optional)</label>
                  <Textarea value={description} onChange={e => setDescription(e.target.value)} placeholder="What should this bot specialise in?" className="rounded-xl resize-none" rows={3} data-testid="bot-description-input" />
                </div>

                <div className="p-3 rounded-xl bg-muted/40 border border-border/50">
                  <p className="text-xs font-medium text-muted-foreground mb-1">Selected libraries ({selectedLibs.length})</p>
                  {selectedLibs.length === 0
                    ? <p className="text-xs text-muted-foreground/60">Pick libraries from the browser →</p>
                    : <p className="text-xs text-foreground/80">{selectedLibs.slice(0, 6).join(", ")}{selectedLibs.length > 6 ? ` +${selectedLibs.length - 6} more` : ""}</p>
                  }
                </div>

                <Button onClick={() => generate.mutate()} disabled={!botName || selectedLibs.length === 0 || generate.isPending} className="w-full rounded-xl bg-gradient-to-r from-primary to-accent text-primary-foreground shadow-md" data-testid="generate-bot-btn">
                  {generate.isPending ? <><Loader2 className="h-4 w-4 mr-2 animate-spin" />Generating...</> : <><Sparkles className="h-4 w-4 mr-2" />Generate Bot</>}
                </Button>
              </div>
            </Card>

            {/* Generated preview */}
            {generatedBot && (
              <Card className="buddy-card rounded-2xl border-primary/30 bg-primary/4 p-5 space-y-3" data-testid="bot-preview">
                <div className="flex items-center gap-2">
                  <BrainCircuit className="h-4 w-4 text-primary" />
                  <span className="font-semibold text-sm text-primary">Generated Bot Preview</span>
                </div>
                <div>
                  <p className="font-semibold">{generatedBot.displayName}</p>
                  <p className="text-xs text-muted-foreground mt-0.5">{generatedBot.division} · {generatedBot.tier}</p>
                </div>
                <p className="text-sm text-muted-foreground">{generatedBot.description}</p>
                <div className="flex flex-wrap gap-1">
                  {(generatedBot.capabilities ?? []).slice(0, 6).map((c: string, i: number) => (
                    <Badge key={i} variant="secondary" className="text-xs rounded-lg">{c}</Badge>
                  ))}
                </div>
                <div className="flex gap-2 pt-1">
                  <Button onClick={() => save.mutate()} disabled={save.isPending} className="flex-1 rounded-xl" data-testid="save-bot-btn">
                    {save.isPending ? <><Loader2 className="h-4 w-4 mr-2 animate-spin" />Saving...</> : <><Save className="h-4 w-4 mr-2" />Add to Fleet</>}
                  </Button>
                  <Button variant="outline" onClick={() => setGeneratedBot(null)} className="rounded-xl" data-testid="discard-bot-btn">Discard</Button>
                </div>
              </Card>
            )}
          </div>
        </div>
      </div>
    </AppShell>
  );
}
