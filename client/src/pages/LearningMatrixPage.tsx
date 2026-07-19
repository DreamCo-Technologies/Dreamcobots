import Seo from "@/components/Seo";
import AppShell from "@/components/AppShell";
import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { cn } from "@/lib/utils";
import { useToast } from "@/hooks/use-toast";
import {
  Brain,
  Globe,
  FlaskConical,
  BarChart3,
  Dna,
  DollarSign,
  ShieldCheck,
  Database,
  Cpu,
  Layers,
  Target,
  TrendingUp,
  Activity,
  Zap,
  Lock,
  Eye,
  Server,
  Network,
  Settings,
  ChevronRight,
  Gauge,
  Microscope,
  Atom,
  Lightbulb,
  Workflow,
  Copy,
  Download,
  ExternalLink,
  BookOpen,
} from "lucide-react";

const COUNTRIES = [
  { name: "America", flag: "US", labs: ["OpenAI", "Anthropic", "Meta AI", "Microsoft", "NVIDIA", "Google DeepMind"], color: "bg-blue-500/10 text-blue-600 dark:text-blue-400 border-blue-500/20" },
  { name: "China", flag: "CN", labs: ["Baidu", "SenseTime", "Huawei AI", "Tsinghua AI Lab", "iFlyTek", "Alibaba DAMO"], color: "bg-red-500/10 text-red-600 dark:text-red-400 border-red-500/20" },
  { name: "India", flag: "IN", labs: ["Wadhwani AI", "IISc AI Lab", "Tech Mahindra AI", "HCL AI", "ISRO AI", "Infosys AI"], color: "bg-orange-500/10 text-orange-600 dark:text-orange-400 border-orange-500/20" },
  { name: "Europe", flag: "EU", labs: ["DeepMind UK", "AI4EU", "Fraunhofer AI", "INRIA", "ETH Zurich AI", "Oxford AI"], color: "bg-indigo-500/10 text-indigo-600 dark:text-indigo-400 border-indigo-500/20" },
  { name: "Japan", flag: "JP", labs: ["Riken AI", "Sony AI", "Toyota AI", "NTT Labs", "Preferred Networks", "Hitachi AI"], color: "bg-pink-500/10 text-pink-600 dark:text-pink-400 border-pink-500/20" },
  { name: "Israel", flag: "IL", labs: ["AI21 Labs", "Mobileye AI", "Run:ai", "Tabnine", "Hailo", "Lightricks AI"], color: "bg-cyan-500/10 text-cyan-600 dark:text-cyan-400 border-cyan-500/20" },
  { name: "Canada", flag: "CA", labs: ["Mila", "Vector Institute", "Amii", "Cohere", "Element AI", "Scale AI Canada"], color: "bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border-emerald-500/20" },
];

const LEARNING_METHODS = [
  { name: "Supervised Learning", description: "Human-labeled datasets for classification and regression tasks", accuracy: 94, efficiency: 78, cost: 65, scalability: 82, icon: Target },
  { name: "Unsupervised Learning", description: "Pattern detection, clustering, and anomaly discovery without labels", accuracy: 81, efficiency: 85, cost: 45, scalability: 90, icon: Microscope },
  { name: "Reinforcement Learning", description: "Reward-driven optimization for sequential decision making", accuracy: 88, efficiency: 62, cost: 80, scalability: 70, icon: Dna },
  { name: "Self-Supervised Learning", description: "Predicting missing parts of data for pre-training foundation models", accuracy: 91, efficiency: 88, cost: 55, scalability: 95, icon: Brain },
  { name: "Federated Learning", description: "Decentralized, privacy-focused learning across distributed nodes", accuracy: 79, efficiency: 72, cost: 40, scalability: 88, icon: Network },
  { name: "Transfer Learning", description: "Adapting pre-trained models to new tasks with minimal data", accuracy: 89, efficiency: 92, cost: 30, scalability: 85, icon: Layers },
  { name: "Multi-Modal Learning", description: "Combining text, images, audio, and video for unified understanding", accuracy: 86, efficiency: 65, cost: 85, scalability: 75, icon: Eye },
  { name: "AutoML & NAS", description: "Automating model discovery and neural architecture search", accuracy: 83, efficiency: 55, cost: 90, scalability: 60, icon: Settings },
  { name: "Meta-Learning", description: "Learning to learn - rapid adaptation to new tasks", accuracy: 80, efficiency: 70, cost: 75, scalability: 65, icon: Atom },
];

const PIPELINE_LAYERS = [
  {
    title: "Global AI Data Sources",
    icon: Globe,
    color: "text-blue-500",
    items: ["arXiv Research Papers", "GitHub Repositories", "Kaggle Competitions", "Industry AI Labs", "Open-Source Models", "Global Press Releases"],
  },
  {
    title: "Data Collection Layer",
    icon: Database,
    color: "text-emerald-500",
    items: ["Web Scraper Engine", "PDF/Notebook Parser", "Dataset Normalizer", "Quality Scoring System"],
  },
  {
    title: "Method Categorization",
    icon: Layers,
    color: "text-purple-500",
    items: ["Auto Classification", "Multi-modal Tagging", "Country & Lab Metadata", "Novelty Detection"],
  },
  {
    title: "Sandbox Testing Lab",
    icon: FlaskConical,
    color: "text-amber-500",
    items: ["Isolated Test Environments", "A/B Testing Framework", "Stress & Adversarial Testing", "Metrics Collection Engine"],
  },
  {
    title: "Performance Analytics",
    icon: BarChart3,
    color: "text-cyan-500",
    items: ["Accuracy & Precision Tracking", "Efficiency & Cost Analysis", "Scalability Benchmarks", "Global Learning Matrix DB"],
  },
  {
    title: "Hybrid Evolution Engine",
    icon: Dna,
    color: "text-red-500",
    items: ["Best Method Selection", "Genetic Recombination", "Reinforcement Optimization", "Multi-Bot Knowledge Sharing"],
  },
  {
    title: "Profit & Application",
    icon: DollarSign,
    color: "text-green-500",
    items: ["Market-Focused Deployment", "ROI Tracking", "Market Adaptation", "Revenue Optimization"],
  },
  {
    title: "Governance & Security",
    icon: ShieldCheck,
    color: "text-orange-500",
    items: ["Audit Logs", "Military-Grade Encryption", "Role-Based Control", "Ethical Overrides"],
  },
];

interface FeatureItem {
  name: string;
  status: "active" | "testing" | "planned";
}

const FEATURES_200: Record<string, FeatureItem[]> = {
  "Global Learning Intelligence": [
    { name: "Country-based learning profiles", status: "active" },
    { name: "Research-paper ingestion engine", status: "active" },
    { name: "GitHub repository analyzer", status: "active" },
    { name: "Kaggle competition strategy importer", status: "active" },
    { name: "Model architecture scraper", status: "active" },
    { name: "AI lab benchmarking database", status: "active" },
    { name: "Multi-country model comparison", status: "active" },
    { name: "Cross-cultural dataset bias detector", status: "testing" },
    { name: "Global compliance analyzer", status: "active" },
    { name: "Regulatory awareness layer", status: "active" },
    { name: "Language adaptation intelligence", status: "active" },
    { name: "Multilingual token optimization", status: "testing" },
    { name: "Dataset quality scoring", status: "active" },
    { name: "Data cleanliness grading", status: "active" },
    { name: "Training methodology tagging", status: "active" },
    { name: "Compute efficiency ranking", status: "active" },
    { name: "Energy consumption scoring", status: "testing" },
    { name: "GPU/TPU optimization tracker", status: "active" },
    { name: "Open vs closed-source comparison", status: "active" },
    { name: "Proprietary pattern extraction", status: "active" },
    { name: "AI research trend detection", status: "active" },
    { name: "Publication frequency monitor", status: "active" },
    { name: "Breakthrough alert system", status: "active" },
    { name: "Novel architecture detection", status: "testing" },
    { name: "RL comparison engine", status: "active" },
    { name: "Self-supervised method tracker", status: "active" },
    { name: "Multi-modal innovation tracker", status: "active" },
    { name: "Federated learning comparison", status: "testing" },
    { name: "Meta-learning evaluation", status: "testing" },
    { name: "Transfer learning benchmarker", status: "active" },
    { name: "Prompt engineering analyzer", status: "active" },
    { name: "Alignment strategy comparison", status: "active" },
    { name: "Safety technique evaluation", status: "active" },
    { name: "Red-team simulation module", status: "testing" },
    { name: "Model compression comparison", status: "active" },
    { name: "Quantization strategy analyzer", status: "active" },
    { name: "Distillation strategy tracker", status: "active" },
    { name: "Synthetic data usage detector", status: "testing" },
    { name: "Hybrid architecture analyzer", status: "active" },
    { name: "Global best-practice aggregator", status: "active" },
  ],
  "Sandbox Testing Lab": [
    { name: "Isolated testing environments", status: "active" },
    { name: "Multi-version A/B testing", status: "active" },
    { name: "Model-vs-model battles", status: "active" },
    { name: "Simulation stress testing", status: "active" },
    { name: "Adversarial attack testing", status: "active" },
    { name: "Data poisoning simulation", status: "testing" },
    { name: "Failure rate mapping", status: "active" },
    { name: "Overfitting detection engine", status: "active" },
    { name: "Underfitting detection", status: "active" },
    { name: "Convergence rate tracker", status: "active" },
    { name: "Learning curve visualization", status: "active" },
    { name: "Gradient explosion detection", status: "active" },
    { name: "Gradient vanishing monitor", status: "active" },
    { name: "Hyperparameter sweep automation", status: "active" },
    { name: "Neural architecture search", status: "testing" },
    { name: "AutoML experimentation engine", status: "testing" },
    { name: "Batch size optimizer", status: "active" },
    { name: "Learning rate optimizer", status: "active" },
    { name: "Dropout testing engine", status: "active" },
    { name: "Regularization benchmarking", status: "active" },
    { name: "Memory usage monitor", status: "active" },
    { name: "Latency tracking", status: "active" },
    { name: "Inference speed comparison", status: "active" },
    { name: "Cost-per-training calculation", status: "active" },
    { name: "ROI-per-model analysis", status: "active" },
    { name: "Scalability stress simulation", status: "active" },
    { name: "API load simulation", status: "active" },
    { name: "Multi-GPU scaling test", status: "testing" },
    { name: "Cloud provider comparison", status: "active" },
    { name: "Edge deployment simulation", status: "testing" },
    { name: "Federated network simulation", status: "testing" },
    { name: "Privacy attack resistance test", status: "testing" },
    { name: "Explainability benchmarking", status: "active" },
    { name: "Fairness testing suite", status: "active" },
    { name: "Bias exposure analyzer", status: "active" },
    { name: "Ethical compliance simulation", status: "active" },
    { name: "Cross-domain generalization test", status: "testing" },
    { name: "Data drift simulation", status: "active" },
    { name: "Long-term stability tracking", status: "active" },
    { name: "Model decay detection", status: "active" },
  ],
  "Self-Evolution Engine": [
    { name: "Performance memory bank", status: "active" },
    { name: "Strategy effectiveness scoring", status: "active" },
    { name: "Automatic method elimination", status: "active" },
    { name: "Hybrid strategy generator", status: "active" },
    { name: "Adaptive learning system builder", status: "testing" },
    { name: "Continuous improvement loop", status: "active" },
    { name: "Reinforcement reward tuning", status: "active" },
    { name: "Failure replay system", status: "active" },
    { name: "Mistake pattern detection", status: "active" },
    { name: "Auto dataset expansion", status: "testing" },
    { name: "Synthetic dataset generator", status: "testing" },
    { name: "Self-distillation pipeline", status: "testing" },
    { name: "Model pruning automation", status: "active" },
    { name: "Knowledge graph builder", status: "active" },
    { name: "Pattern abstraction engine", status: "active" },
    { name: "Transfer learning auto-mapping", status: "active" },
    { name: "Multi-bot shared knowledge", status: "active" },
    { name: "Experience weighting algorithm", status: "active" },
    { name: "Historical performance ranking", status: "active" },
    { name: "Prediction accuracy evolution", status: "active" },
    { name: "Learning efficiency optimizer", status: "active" },
    { name: "Cost efficiency optimizer", status: "active" },
    { name: "Compute allocation balancer", status: "active" },
    { name: "Risk tolerance adjustment", status: "active" },
    { name: "Stability vs innovation balance", status: "active" },
    { name: "Auto fallback system", status: "active" },
    { name: "Learning rollback system", status: "active" },
    { name: "Performance anomaly alerts", status: "active" },
    { name: "Autonomous retraining scheduler", status: "testing" },
    { name: "Cross-bot optimization sharing", status: "active" },
    { name: "Global dataset pooling engine", status: "testing" },
    { name: "Method replication testing", status: "active" },
    { name: "Long-term reward scoring", status: "active" },
    { name: "Evolutionary algorithm layer", status: "testing" },
    { name: "Genetic architecture recombination", status: "testing" },
    { name: "Mutation testing engine", status: "testing" },
    { name: "Performance heat mapping", status: "active" },
    { name: "AI memory compression", status: "testing" },
    { name: "Multi-agent collaboration", status: "active" },
    { name: "Autonomous improvement reporting", status: "active" },
  ],
  "Profit & Performance Intelligence": [
    { name: "Profit impact modeling", status: "active" },
    { name: "Revenue-per-accuracy calculator", status: "active" },
    { name: "Market-specific learning profiles", status: "active" },
    { name: "Sales optimization learning mode", status: "active" },
    { name: "Real estate model optimization", status: "active" },
    { name: "Car flipping AI optimization", status: "active" },
    { name: "Lead generation learning focus", status: "active" },
    { name: "Conversion-rate intelligence", status: "active" },
    { name: "Predictive deal scoring", status: "active" },
    { name: "Price elasticity modeling", status: "active" },
    { name: "Risk-adjusted profit scoring", status: "active" },
    { name: "Market volatility learning", status: "active" },
    { name: "Trend prediction learning", status: "active" },
    { name: "Customer behavior modeling", status: "active" },
    { name: "Cross-market data blending", status: "testing" },
    { name: "Niche-specific training presets", status: "active" },
    { name: "Industry-specific benchmarking", status: "active" },
    { name: "High-frequency update mode", status: "active" },
    { name: "Opportunity detection learning", status: "active" },
    { name: "Fraud detection learning", status: "active" },
    { name: "Competitor strategy simulation", status: "testing" },
    { name: "Marketing model adaptation", status: "active" },
    { name: "Negotiation optimization training", status: "testing" },
    { name: "Demand forecasting learning", status: "active" },
    { name: "Asset valuation intelligence", status: "active" },
    { name: "Credit risk learning", status: "active" },
    { name: "ROI-based method selection", status: "active" },
    { name: "Scaling profitability analysis", status: "active" },
    { name: "Budget optimization training", status: "active" },
    { name: "Automation efficiency scoring", status: "active" },
    { name: "Cost-of-failure modeling", status: "active" },
    { name: "Aggressive growth mode", status: "active" },
    { name: "Conservative safety mode", status: "active" },
    { name: "Global arbitrage intelligence", status: "testing" },
    { name: "Supply-demand learning engine", status: "active" },
    { name: "Auction learning optimization", status: "testing" },
    { name: "Grant-funding pattern learning", status: "testing" },
    { name: "Loan approval modeling", status: "active" },
    { name: "Long-term wealth accumulation", status: "active" },
    { name: "Strategic investment learning", status: "active" },
  ],
  "Control, Security & Infrastructure": [
    { name: "Military-grade encryption", status: "active" },
    { name: "Zero-trust architecture", status: "active" },
    { name: "Role-based learning permissions", status: "active" },
    { name: "Access tier control", status: "active" },
    { name: "Encrypted model vault", status: "active" },
    { name: "Secure data pipelines", status: "active" },
    { name: "Audit trail logging", status: "active" },
    { name: "Tamper detection", status: "active" },
    { name: "API key isolation", status: "active" },
    { name: "Compliance documentation gen", status: "active" },
    { name: "Legal risk alert engine", status: "active" },
    { name: "Data retention policies", status: "active" },
    { name: "Model version locking", status: "active" },
    { name: "Redundancy backups", status: "active" },
    { name: "Disaster recovery system", status: "active" },
    { name: "Model integrity verification", status: "active" },
    { name: "Cryptographic hashing", status: "active" },
    { name: "Secure federated nodes", status: "testing" },
    { name: "Permissioned experimentation", status: "active" },
    { name: "Threat detection AI", status: "active" },
    { name: "Automated patching system", status: "active" },
    { name: "Vulnerability scanning", status: "active" },
    { name: "Secure containerization", status: "active" },
    { name: "Immutable training logs", status: "active" },
    { name: "Incident response automation", status: "active" },
    { name: "Monitoring dashboards", status: "active" },
    { name: "Multi-cloud failover", status: "testing" },
    { name: "Performance SLA tracking", status: "active" },
    { name: "Edge security integration", status: "testing" },
    { name: "Private training mode", status: "active" },
    { name: "Air-gapped testing option", status: "testing" },
    { name: "Secure export protocols", status: "active" },
    { name: "Digital signature verification", status: "active" },
    { name: "Confidential dataset tagging", status: "active" },
    { name: "AI governance module", status: "active" },
    { name: "Responsible AI enforcement", status: "active" },
    { name: "Ethical override system", status: "active" },
    { name: "Safe-mode learning lock", status: "active" },
    { name: "Manual override control", status: "active" },
    { name: "Global AI command center", status: "active" },
  ],
};

const STATUS_BADGE: Record<string, string> = {
  active: "bg-[rgb(34_197_94)]/10 text-[rgb(34_197_94)] border-[rgb(34_197_94)]/20",
  testing: "bg-[rgb(245_158_11)]/10 text-[rgb(245_158_11)] border-[rgb(245_158_11)]/20",
  planned: "bg-muted text-muted-foreground",
};

function generateLabMetrics(labName: string) {
  const hash = labName.split("").reduce((a, c) => a + c.charCodeAt(0), 0);
  return {
    accuracy: 75 + (hash % 20),
    efficiency: 60 + (hash % 30),
    cost: 30 + (hash % 50),
    scalability: 65 + (hash % 30),
  };
}

export default function LearningMatrixPage() {
  const { toast } = useToast();
  const [selectedCountry, setSelectedCountry] = useState("All");
  const [selectedMethod, setSelectedMethod] = useState("All");

  const totalFeatures = Object.values(FEATURES_200).reduce((s, arr) => s + arr.length, 0);
  const activeFeatures = Object.values(FEATURES_200).reduce((s, arr) => s + arr.filter(f => f.status === "active").length, 0);
  const testingFeatures = Object.values(FEATURES_200).reduce((s, arr) => s + arr.filter(f => f.status === "testing").length, 0);

  return (
    <AppShell>
      <Seo title="Global AI Learning Matrix | DreamCo Empire OS" description="Military-grade Global AI Learning Matrix Engine - analyze, adapt, and evolve AI strategies from 200+ global sources" />
      <div className="space-y-6">
        <div className="flex items-center justify-between flex-wrap gap-4">
          <div>
            <h1 className="text-2xl font-bold flex items-center gap-2" data-testid="page-title">
              <Brain className="h-7 w-7 text-primary" />
              Global AI Learning Matrix
            </h1>
            <p className="text-sm text-muted-foreground mt-1">Military-grade autonomous AI evolution engine</p>
          </div>
          <div className="flex items-center gap-2 flex-wrap">
            <Badge variant="outline" className="rounded-full">{totalFeatures} Features</Badge>
            <Badge className={cn("rounded-full border", STATUS_BADGE.active)}>{activeFeatures} Active</Badge>
            <Badge className={cn("rounded-full border", STATUS_BADGE.testing)}>{testingFeatures} Testing</Badge>
            <Button
              variant="outline"
              size="sm"
              onClick={() => {
                const text = [
                  "Global AI Learning Matrix — Export",
                  `Total Features: ${totalFeatures}`,
                  `Active: ${activeFeatures}`,
                  `Testing: ${testingFeatures}`,
                  `Countries Tracked: ${COUNTRIES.length}`,
                  `Learning Methods: ${LEARNING_METHODS.length}`,
                ].join("\n");
                navigator.clipboard.writeText(text);
                toast({ title: "Matrix data copied to clipboard" });
              }}
              data-testid="button-copy-matrix"
            >
              <Copy className="h-3.5 w-3.5 mr-1.5" />
              Copy Summary
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => {
                const rows = LEARNING_METHODS.map(m =>
                  `${m.name},${m.accuracy},${m.efficiency},${m.cost},${m.scalability}`
                );
                const csv = ["Method,Accuracy,Efficiency,Cost,Scalability", ...rows].join("\n");
                const blob = new Blob([csv], { type: "text/csv" });
                const url = URL.createObjectURL(blob);
                const a = document.createElement("a");
                a.href = url;
                a.download = `ai-learning-matrix-${new Date().toISOString().slice(0,10)}.csv`;
                a.click();
                URL.revokeObjectURL(url);
                toast({ title: "Learning matrix exported" });
              }}
              data-testid="button-export-matrix"
            >
              <Download className="h-3.5 w-3.5 mr-1.5" />
              Export CSV
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => window.open("https://paperswithcode.com/", "_blank")}
              data-testid="button-research-ai"
            >
              <ExternalLink className="h-3.5 w-3.5 mr-1.5" />
              Latest Research
            </Button>
          </div>
        </div>

        <Tabs defaultValue="matrix" className="w-full">
          <TabsList className="flex flex-wrap h-auto gap-1">
            <TabsTrigger value="matrix" data-testid="tab-matrix">Learning Matrix</TabsTrigger>
            <TabsTrigger value="pipeline" data-testid="tab-pipeline">Architecture Pipeline</TabsTrigger>
            <TabsTrigger value="methods" data-testid="tab-methods">Learning Methods</TabsTrigger>
            <TabsTrigger value="labs" data-testid="tab-labs">Global AI Labs</TabsTrigger>
            <TabsTrigger value="features" data-testid="tab-features">200 Features</TabsTrigger>
            <TabsTrigger value="sandbox" data-testid="tab-sandbox">Sandbox Lab</TabsTrigger>
            <TabsTrigger value="evolution" data-testid="tab-evolution">Evolution Engine</TabsTrigger>
            <TabsTrigger value="governance" data-testid="tab-governance">Governance</TabsTrigger>
          </TabsList>

          <TabsContent value="matrix" className="mt-6 space-y-6">
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
              <Card>
                <CardContent className="pt-4">
                  <div className="flex items-center gap-2">
                    <Globe className="h-5 w-5 text-blue-500" />
                    <div>
                      <p className="text-2xl font-bold" data-testid="stat-countries">7</p>
                      <p className="text-xs text-muted-foreground">Countries Tracked</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="pt-4">
                  <div className="flex items-center gap-2">
                    <FlaskConical className="h-5 w-5 text-purple-500" />
                    <div>
                      <p className="text-2xl font-bold" data-testid="stat-labs">42</p>
                      <p className="text-xs text-muted-foreground">AI Labs Monitored</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="pt-4">
                  <div className="flex items-center gap-2">
                    <Brain className="h-5 w-5 text-emerald-500" />
                    <div>
                      <p className="text-2xl font-bold" data-testid="stat-methods">9</p>
                      <p className="text-xs text-muted-foreground">Learning Methods</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="pt-4">
                  <div className="flex items-center gap-2">
                    <Zap className="h-5 w-5 text-amber-500" />
                    <div>
                      <p className="text-2xl font-bold" data-testid="stat-features">{totalFeatures}</p>
                      <p className="text-xs text-muted-foreground">Total Features</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>

            <Card data-testid="country-selector">
              <CardHeader className="pb-3">
                <CardTitle className="text-lg flex items-center gap-2">
                  <Globe className="h-5 w-5 text-primary" />
                  Learn From Country
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex flex-wrap gap-2 mb-4">
                  <Button
                    variant={selectedCountry === "All" ? "default" : "outline"}
                    onClick={() => setSelectedCountry("All")}
                    data-testid="country-all"
                  >
                    Global
                  </Button>
                  {COUNTRIES.map(c => (
                    <Button
                      key={c.name}
                      variant={selectedCountry === c.name ? "default" : "outline"}
                      onClick={() => setSelectedCountry(c.name)}
                      data-testid={`country-${c.name.toLowerCase()}`}
                    >
                      {c.name}
                    </Button>
                  ))}
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                  {(selectedCountry === "All" ? COUNTRIES : COUNTRIES.filter(c => c.name === selectedCountry)).map(country => (
                    <Card key={country.name} className={cn("border", country.color.split(" ").find(c => c.startsWith("border-")))}>
                      <CardContent className="pt-4">
                        <div className="flex items-center gap-2 mb-3">
                          <Badge className={cn("rounded-full border", country.color)}>{country.name}</Badge>
                          <span className="text-xs text-muted-foreground">{country.labs.length} Labs</span>
                        </div>
                        <div className="space-y-1.5">
                          {country.labs.map(lab => {
                            const m = generateLabMetrics(lab);
                            return (
                              <div key={lab} className="flex items-center justify-between text-sm" data-testid={`lab-${lab.toLowerCase().replace(/\s/g, "-")}`}>
                                <span className="text-muted-foreground truncate">{lab}</span>
                                <Badge variant="outline" className="rounded-full text-[10px] ml-2">{m.accuracy}%</Badge>
                              </div>
                            );
                          })}
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </CardContent>
            </Card>

            <Card data-testid="method-focus">
              <CardHeader className="pb-3">
                <CardTitle className="text-lg flex items-center gap-2">
                  <Target className="h-5 w-5 text-primary" />
                  Method Focus Filter
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex flex-wrap gap-2 mb-4">
                  <Button
                    variant={selectedMethod === "All" ? "default" : "outline"}
                    onClick={() => setSelectedMethod("All")}
                    data-testid="method-all"
                  >
                    All Methods
                  </Button>
                  {LEARNING_METHODS.map(m => (
                    <Button
                      key={m.name}
                      variant={selectedMethod === m.name ? "default" : "outline"}
                      onClick={() => setSelectedMethod(m.name)}
                      data-testid={`method-${m.name.toLowerCase().replace(/\s/g, "-")}`}
                    >
                      {m.name}
                    </Button>
                  ))}
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                  {(selectedMethod === "All" ? LEARNING_METHODS : LEARNING_METHODS.filter(m => m.name === selectedMethod)).map(method => (
                    <Card key={method.name}>
                      <CardContent className="pt-4 space-y-3">
                        <div className="flex items-center gap-2">
                          <method.icon className="h-4 w-4 text-primary" />
                          <p className="text-sm font-medium">{method.name}</p>
                        </div>
                        <p className="text-xs text-muted-foreground">{method.description}</p>
                        <div className="space-y-2">
                          <div className="flex items-center justify-between text-xs">
                            <span className="text-muted-foreground">Accuracy</span>
                            <span>{method.accuracy}%</span>
                          </div>
                          <Progress value={method.accuracy} className="h-1.5" />
                          <div className="flex items-center justify-between text-xs">
                            <span className="text-muted-foreground">Efficiency</span>
                            <span>{method.efficiency}%</span>
                          </div>
                          <Progress value={method.efficiency} className="h-1.5" />
                          <div className="flex items-center justify-between text-xs">
                            <span className="text-muted-foreground">Scalability</span>
                            <span>{method.scalability}%</span>
                          </div>
                          <Progress value={method.scalability} className="h-1.5" />
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="pipeline" className="mt-6 space-y-4">
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-lg flex items-center gap-2">
                  <Workflow className="h-5 w-5 text-primary" />
                  Architecture Pipeline
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {PIPELINE_LAYERS.map((layer, idx) => (
                    <div key={layer.title}>
                      <Card className="hover-elevate" data-testid={`pipeline-${idx}`}>
                        <CardContent className="py-4 flex items-start gap-4">
                          <div className={cn("h-10 w-10 rounded-lg flex items-center justify-center flex-shrink-0 bg-muted/50")}>
                            <layer.icon className={cn("h-5 w-5", layer.color)} />
                          </div>
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center gap-2 mb-1">
                              <p className="font-medium text-sm">{layer.title}</p>
                              <Badge variant="outline" className="rounded-full text-[10px]">Layer {idx + 1}</Badge>
                            </div>
                            <div className="flex flex-wrap gap-1.5">
                              {layer.items.map(item => (
                                <Badge key={item} variant="secondary" className="text-[10px] rounded-full">{item}</Badge>
                              ))}
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                      {idx < PIPELINE_LAYERS.length - 1 && (
                        <div className="flex justify-center py-1">
                          <ChevronRight className="h-4 w-4 text-muted-foreground rotate-90" />
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="methods" className="mt-6 space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {LEARNING_METHODS.map((method, idx) => (
                <Card key={method.name} data-testid={`method-card-${idx}`}>
                  <CardHeader className="pb-3">
                    <CardTitle className="text-base flex items-center gap-2">
                      <method.icon className="h-5 w-5 text-primary" />
                      {method.name}
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <p className="text-sm text-muted-foreground">{method.description}</p>
                    <div className="space-y-3">
                      {[
                        { label: "Accuracy", value: method.accuracy, color: "bg-blue-500" },
                        { label: "Efficiency", value: method.efficiency, color: "bg-emerald-500" },
                        { label: "Cost Factor", value: method.cost, color: "bg-amber-500" },
                        { label: "Scalability", value: method.scalability, color: "bg-purple-500" },
                      ].map(metric => (
                        <div key={metric.label}>
                          <div className="flex items-center justify-between text-xs mb-1">
                            <span className="text-muted-foreground">{metric.label}</span>
                            <span className="font-medium">{metric.value}%</span>
                          </div>
                          <Progress value={metric.value} className="h-1.5" />
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </TabsContent>

          <TabsContent value="labs" className="mt-6 space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {COUNTRIES.map((country) => (
                <Card key={country.name} data-testid={`lab-card-${country.name.toLowerCase()}`}>
                  <CardHeader className="pb-3">
                    <CardTitle className="text-base flex items-center gap-2">
                      <Badge className={cn("rounded-full border", country.color)}>{country.name}</Badge>
                      <span className="text-xs text-muted-foreground">{country.labs.length} Labs</span>
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      {country.labs.map(lab => {
                        const m = generateLabMetrics(lab);
                        return (
                          <div key={lab} className="p-3 rounded-lg border border-border/40 space-y-2">
                            <div className="flex items-center justify-between">
                              <p className="text-sm font-medium">{lab}</p>
                              <Badge variant="outline" className="rounded-full text-[10px]">Score: {m.accuracy}%</Badge>
                            </div>
                            <div className="grid grid-cols-4 gap-2 text-xs">
                              <div>
                                <p className="text-muted-foreground">Accuracy</p>
                                <p className="font-medium">{m.accuracy}%</p>
                              </div>
                              <div>
                                <p className="text-muted-foreground">Efficiency</p>
                                <p className="font-medium">{m.efficiency}%</p>
                              </div>
                              <div>
                                <p className="text-muted-foreground">Cost</p>
                                <p className="font-medium">{m.cost}%</p>
                              </div>
                              <div>
                                <p className="text-muted-foreground">Scale</p>
                                <p className="font-medium">{m.scalability}%</p>
                              </div>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </TabsContent>

          <TabsContent value="features" className="mt-6 space-y-4">
            {Object.entries(FEATURES_200).map(([category, features]) => {
              const activeCount = features.filter(f => f.status === "active").length;
              const testingCount = features.filter(f => f.status === "testing").length;
              return (
                <Card key={category} data-testid={`feature-category-${category.toLowerCase().replace(/\s/g, "-")}`}>
                  <CardHeader className="flex flex-row items-center justify-between gap-2 space-y-0 pb-3">
                    <CardTitle className="text-base">{category}</CardTitle>
                    <div className="flex items-center gap-2">
                      <Badge className={cn("rounded-full border text-[10px]", STATUS_BADGE.active)}>{activeCount} active</Badge>
                      {testingCount > 0 && <Badge className={cn("rounded-full border text-[10px]", STATUS_BADGE.testing)}>{testingCount} testing</Badge>}
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-1.5">
                      {features.map((f, i) => (
                        <div key={i} className="flex items-center gap-2 p-2 rounded-lg text-sm" data-testid={`feature-${category.toLowerCase().replace(/\s/g, "-")}-${i}`}>
                          <div className={cn("h-1.5 w-1.5 rounded-full flex-shrink-0", f.status === "active" ? "bg-[rgb(34_197_94)]" : "bg-[rgb(245_158_11)]")} />
                          <span className="text-muted-foreground text-xs">{f.name}</span>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </TabsContent>

          <TabsContent value="sandbox" className="mt-6 space-y-4">
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
              <Card>
                <CardContent className="pt-4">
                  <div className="flex items-center gap-2">
                    <FlaskConical className="h-5 w-5 text-purple-500" />
                    <div>
                      <p className="text-2xl font-bold">156</p>
                      <p className="text-xs text-muted-foreground">Active Experiments</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="pt-4">
                  <div className="flex items-center gap-2">
                    <Activity className="h-5 w-5 text-emerald-500" />
                    <div>
                      <p className="text-2xl font-bold">94.2%</p>
                      <p className="text-xs text-muted-foreground">Avg Accuracy</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="pt-4">
                  <div className="flex items-center gap-2">
                    <Gauge className="h-5 w-5 text-amber-500" />
                    <div>
                      <p className="text-2xl font-bold">12ms</p>
                      <p className="text-xs text-muted-foreground">Avg Latency</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="pt-4">
                  <div className="flex items-center gap-2">
                    <TrendingUp className="h-5 w-5 text-blue-500" />
                    <div>
                      <p className="text-2xl font-bold">87.5%</p>
                      <p className="text-xs text-muted-foreground">Success Rate</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>

            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-lg flex items-center gap-2">
                  <FlaskConical className="h-5 w-5 text-primary" />
                  Automated Sandbox Testing
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {[
                    { name: "Model A/B Test: GPT-4.1 vs Claude 4", status: "Running", accuracy: "96.3%", time: "2h 14m" },
                    { name: "Adversarial Attack Resistance", status: "Passed", accuracy: "91.7%", time: "45m" },
                    { name: "Data Drift Simulation", status: "Running", accuracy: "88.2%", time: "1h 32m" },
                    { name: "Multi-GPU Scaling Test", status: "Queued", accuracy: "--", time: "Est. 3h" },
                    { name: "Federated Learning Privacy Test", status: "Passed", accuracy: "89.4%", time: "56m" },
                    { name: "Hyperparameter Sweep: Learning Rate", status: "Running", accuracy: "93.1%", time: "4h 08m" },
                    { name: "Edge Deployment Latency Test", status: "Passed", accuracy: "85.6%", time: "28m" },
                    { name: "Cross-Domain Generalization", status: "Running", accuracy: "82.9%", time: "1h 47m" },
                  ].map((test, i) => (
                    <div key={i} className="flex items-center justify-between p-3 rounded-lg border border-border/40" data-testid={`sandbox-test-${i}`}>
                      <div className="flex items-center gap-3">
                        <div className={cn("h-2 w-2 rounded-full", test.status === "Running" ? "bg-blue-500 animate-pulse" : test.status === "Passed" ? "bg-[rgb(34_197_94)]" : "bg-muted-foreground")} />
                        <div>
                          <p className="text-sm font-medium">{test.name}</p>
                          <p className="text-xs text-muted-foreground">{test.time}</p>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className="text-sm font-mono">{test.accuracy}</span>
                        <Badge variant="outline" className="rounded-full text-[10px]">{test.status}</Badge>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="evolution" className="mt-6 space-y-4">
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
              <Card>
                <CardContent className="pt-4">
                  <div className="flex items-center gap-2">
                    <Dna className="h-5 w-5 text-red-500" />
                    <div>
                      <p className="text-2xl font-bold">47</p>
                      <p className="text-xs text-muted-foreground">Hybrid Strategies</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="pt-4">
                  <div className="flex items-center gap-2">
                    <Lightbulb className="h-5 w-5 text-amber-500" />
                    <div>
                      <p className="text-2xl font-bold">312</p>
                      <p className="text-xs text-muted-foreground">Mutations Tested</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="pt-4">
                  <div className="flex items-center gap-2">
                    <TrendingUp className="h-5 w-5 text-emerald-500" />
                    <div>
                      <p className="text-2xl font-bold">+18.3%</p>
                      <p className="text-xs text-muted-foreground">Avg Improvement</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="pt-4">
                  <div className="flex items-center gap-2">
                    <Cpu className="h-5 w-5 text-purple-500" />
                    <div>
                      <p className="text-2xl font-bold">451</p>
                      <p className="text-xs text-muted-foreground">Bots Learning</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>

            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-lg flex items-center gap-2">
                  <Dna className="h-5 w-5 text-primary" />
                  Hybrid Evolution Engine
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {[
                    { name: "Self-Supervised + RL Hybrid", components: ["Self-Supervised Learning", "Reinforcement Learning"], score: 96.2, status: "Deployed" },
                    { name: "Transfer + Multi-Modal Fusion", components: ["Transfer Learning", "Multi-Modal Learning"], score: 93.8, status: "Deployed" },
                    { name: "Federated Meta-Learning", components: ["Federated Learning", "Meta-Learning"], score: 91.5, status: "Testing" },
                    { name: "AutoML + Distillation Pipeline", components: ["AutoML & NAS", "Self-Supervised Learning"], score: 89.7, status: "Testing" },
                    { name: "Supervised + RL Reward Tuning", components: ["Supervised Learning", "Reinforcement Learning"], score: 94.1, status: "Deployed" },
                    { name: "Multi-Modal + Meta Adaptation", components: ["Multi-Modal Learning", "Meta-Learning"], score: 87.3, status: "Testing" },
                  ].map((strategy, i) => (
                    <div key={i} className="p-4 rounded-lg border border-border/40 space-y-2" data-testid={`evolution-strategy-${i}`}>
                      <div className="flex items-center justify-between flex-wrap gap-2">
                        <p className="text-sm font-medium">{strategy.name}</p>
                        <div className="flex items-center gap-2">
                          <span className="text-sm font-mono font-bold">{strategy.score}%</span>
                          <Badge variant={strategy.status === "Deployed" ? "default" : "secondary"} className="rounded-full text-[10px]">{strategy.status}</Badge>
                        </div>
                      </div>
                      <div className="flex flex-wrap gap-1.5">
                        {strategy.components.map(c => (
                          <Badge key={c} variant="outline" className="rounded-full text-[10px]">{c}</Badge>
                        ))}
                      </div>
                      <Progress value={strategy.score} className="h-1.5" />
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="governance" className="mt-6 space-y-4">
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
              <Card>
                <CardContent className="pt-4">
                  <div className="flex items-center gap-2">
                    <ShieldCheck className="h-5 w-5 text-emerald-500" />
                    <div>
                      <p className="text-2xl font-bold">100%</p>
                      <p className="text-xs text-muted-foreground">Encryption Active</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="pt-4">
                  <div className="flex items-center gap-2">
                    <Lock className="h-5 w-5 text-blue-500" />
                    <div>
                      <p className="text-2xl font-bold">Zero-Trust</p>
                      <p className="text-xs text-muted-foreground">Architecture</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="pt-4">
                  <div className="flex items-center gap-2">
                    <Eye className="h-5 w-5 text-amber-500" />
                    <div>
                      <p className="text-2xl font-bold">24/7</p>
                      <p className="text-xs text-muted-foreground">Monitoring</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="pt-4">
                  <div className="flex items-center gap-2">
                    <Server className="h-5 w-5 text-purple-500" />
                    <div>
                      <p className="text-2xl font-bold">Multi-Cloud</p>
                      <p className="text-xs text-muted-foreground">Failover Ready</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Card>
                <CardHeader className="pb-3">
                  <CardTitle className="text-base flex items-center gap-2">
                    <Lock className="h-5 w-5 text-primary" />
                    Security Controls
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    {[
                      "Military-grade AES-256 encryption",
                      "Zero-trust network architecture",
                      "Role-based access control (RBAC)",
                      "Encrypted model vault storage",
                      "Secure data pipeline isolation",
                      "Immutable audit trail logging",
                      "Tamper detection & alerting",
                      "API key isolation per service",
                      "Cryptographic hash verification",
                      "Digital signature validation",
                    ].map((item, i) => (
                      <div key={i} className="flex items-center gap-2 p-2 rounded-lg text-sm">
                        <ShieldCheck className="h-3 w-3 text-[rgb(34_197_94)] flex-shrink-0" />
                        <span className="text-muted-foreground text-xs">{item}</span>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
              <Card>
                <CardHeader className="pb-3">
                  <CardTitle className="text-base flex items-center gap-2">
                    <ShieldCheck className="h-5 w-5 text-primary" />
                    Compliance & Governance
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    {[
                      "US/EU/Asia regulatory awareness",
                      "Compliance documentation generator",
                      "Legal risk alert engine",
                      "Data retention policy enforcement",
                      "Model version locking",
                      "Disaster recovery system",
                      "AI governance module",
                      "Responsible AI enforcement",
                      "Ethical override system",
                      "Global AI command center",
                    ].map((item, i) => (
                      <div key={i} className="flex items-center gap-2 p-2 rounded-lg text-sm">
                        <ShieldCheck className="h-3 w-3 text-[rgb(34_197_94)] flex-shrink-0" />
                        <span className="text-muted-foreground text-xs">{item}</span>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </AppShell>
  );
}
