import { Switch, Route, Router as WouterRouter } from "wouter";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { Toaster } from "@/components/ui/toaster";
import { TooltipProvider } from "@/components/ui/tooltip";
import NotFound from "@/pages/not-found";
import { ThemeProvider } from "@/components/theme-provider";
import { Layout } from "@/components/layout/layout";

// Pages
import Dashboard from "@/pages/dashboard";
import Bots from "@/pages/bots";
import Buddy from "@/pages/buddy";
import Revenue from "@/pages/revenue";
import Github from "@/pages/github";
import Divisions from "@/pages/divisions";
import Copilot from "@/pages/copilot";
import SystemPage from "@/pages/system";
import VibePage from "@/pages/vibe";
import ActionsPage from "@/pages/actions";
import CapabilitiesPage from "@/pages/capabilities";
import DealsPage from "@/pages/deals";
import FormulasPage from "@/pages/formulas";
import LearningMatrixPage from "@/pages/learning-matrix";
import AILeadersPage from "@/pages/ai-leaders";
import EcosystemPage from "@/pages/ecosystem";
import MarketplacePage from "@/pages/marketplace";
import CryptoPage from "@/pages/crypto";
import BusinessPage from "@/pages/business";
import LoansPage from "@/pages/loans";
import PricingPage from "@/pages/pricing";
import TimeCapsulePage from "@/pages/time-capsule";
import CostsPage from "@/pages/costs";
import AutonomyPage from "@/pages/autonomy";
import SourcesPage from "@/pages/sources";
import MemoryPage from "@/pages/memory";
import QuantumPage from "@/pages/quantum";
import StudioPage from "@/pages/studio";
import ConsentPage from "@/pages/consent";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
    },
  },
});

function Router() {
  return (
    <Layout>
      <Switch>
        <Route path="/" component={Dashboard} />
        <Route path="/dashboard" component={Dashboard} />
        <Route path="/bots" component={Bots} />
        <Route path="/buddy" component={Buddy} />
        <Route path="/chat" component={Buddy} />
        <Route path="/revenue" component={Revenue} />
        <Route path="/payments" component={Revenue} />
        <Route path="/github" component={Github} />
        <Route path="/divisions" component={Divisions} />
        <Route path="/copilot" component={Copilot} />
        <Route path="/system" component={SystemPage} />
        <Route path="/debug" component={SystemPage} />
        <Route path="/vibe" component={VibePage} />
        <Route path="/code-lab" component={VibePage} />
        <Route path="/actions" component={ActionsPage} />
        <Route path="/orchestration" component={ActionsPage} />
        <Route path="/capabilities" component={CapabilitiesPage} />
        <Route path="/ai-models" component={CapabilitiesPage} />
        <Route path="/connections" component={CapabilitiesPage} />
        <Route path="/deals" component={DealsPage} />
        <Route path="/formulas" component={FormulasPage} />
        <Route path="/learning-matrix" component={LearningMatrixPage} />
        <Route path="/ai-leaders" component={AILeadersPage} />
        <Route path="/ecosystem" component={EcosystemPage} />
        <Route path="/marketplace" component={MarketplacePage} />
        <Route path="/crypto" component={CryptoPage} />
        <Route path="/business" component={BusinessPage} />
        <Route path="/loans" component={LoansPage} />
        <Route path="/pricing" component={PricingPage} />
        <Route path="/time-capsule" component={TimeCapsulePage} />
        <Route path="/sources" component={SourcesPage} />
        <Route path="/ai-sources" component={SourcesPage} />
        <Route path="/memory" component={MemoryPage} />
        <Route path="/quantum" component={QuantumPage} />
        <Route path="/studio" component={StudioPage} />
        <Route path="/media" component={StudioPage} />
        <Route path="/consent" component={ConsentPage} />
        <Route path="/cloning" component={ConsentPage} />
        <Route path="/costs" component={CostsPage} />
        <Route path="/autonomy" component={AutonomyPage} />
        <Route component={NotFound} />
      </Switch>
    </Layout>
  );
}

function App() {
  return (
    <ThemeProvider defaultTheme="dark" storageKey="vite-ui-theme">
      <QueryClientProvider client={queryClient}>
        <TooltipProvider>
          <WouterRouter base={import.meta.env.BASE_URL.replace(/\/$/, "")}>
            <Router />
          </WouterRouter>
          <Toaster />
        </TooltipProvider>
      </QueryClientProvider>
    </ThemeProvider>
  );
}

export default App;
