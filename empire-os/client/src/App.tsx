import { Switch, Route, Redirect } from "wouter";
import { queryClient } from "./lib/queryClient";
import { QueryClientProvider } from "@tanstack/react-query";
import { Toaster } from "@/components/ui/toaster";
import { TooltipProvider } from "@/components/ui/tooltip";

import NotFound from "@/pages/not-found";
import ChatIndexPage from "@/pages/ChatIndexPage";
import ConversationPage from "@/pages/ConversationPage";
import AutonomyPage from "@/pages/AutonomyPage";
import BotsPage from "@/pages/BotsPage";
import DashboardPage from "@/pages/DashboardPage";
import DivisionsPage from "@/pages/DivisionsPage";
import BotDetailPage from "@/pages/BotDetailPage";
import RevenuePage from "@/pages/RevenuePage";
import PricingPage from "@/pages/PricingPage";
import DealsPage from "@/pages/DealsPage";
import DebugPage from "@/pages/DebugPage";
import EcosystemPage from "@/pages/EcosystemPage";
import OrchestrationPage from "@/pages/OrchestrationPage";
import MarketplacePage from "@/pages/MarketplacePage";
import FormulasPage from "@/pages/FormulasPage";
import LearningMatrixPage from "@/pages/LearningMatrixPage";
import BusinessPage from "@/pages/BusinessPage";
import CodeLabPage from "@/pages/CodeLabPage";
import CryptoPage from "@/pages/CryptoPage";
import PaymentsPage from "@/pages/PaymentsPage";
import LoansPage from "@/pages/LoansPage";
import ConnectionsPage from "@/pages/ConnectionsPage";
import TimeCapsulePage from "@/pages/TimeCapsulePage";
import CostTrackingPage from "@/pages/CostTrackingPage";
import AILeadersPage from "@/pages/AILeadersPage";
import AIModelsPage from "@/pages/AIModelsPage";
import BotBuilderPage from "@/pages/BotBuilderPage";
import BotActivityPage from "@/pages/BotActivityPage";

function Router() {
  return (
    <Switch>
      <Route path="/" component={ChatIndexPage} />
      <Route path="/c/:id" component={ConversationPage} />
      <Route path="/autonomy" component={AutonomyPage} />
      <Route path="/bots" component={BotsPage} />
      <Route path="/bot/:id" component={BotDetailPage} />
      <Route path="/dashboard" component={DashboardPage} />
      <Route path="/divisions" component={DivisionsPage} />
      <Route path="/revenue" component={RevenuePage} />
      <Route path="/pricing" component={PricingPage} />
      <Route path="/deals" component={DealsPage} />
      <Route path="/debug" component={DebugPage} />
      <Route path="/ecosystem" component={EcosystemPage} />
      <Route path="/orchestration" component={OrchestrationPage} />
      <Route path="/marketplace" component={MarketplacePage} />
      <Route path="/formulas" component={FormulasPage} />
      <Route path="/learning-matrix" component={LearningMatrixPage} />
      <Route path="/business" component={BusinessPage} />
      <Route path="/code-lab" component={CodeLabPage} />
      <Route path="/crypto" component={CryptoPage} />
      <Route path="/payments" component={PaymentsPage} />
      <Route path="/loans" component={LoansPage} />
      <Route path="/connections" component={ConnectionsPage} />
      <Route path="/time-capsule" component={TimeCapsulePage} />
      <Route path="/costs" component={CostTrackingPage} />
      <Route path="/ai-leaders" component={AILeadersPage} />
      <Route path="/ai-models" component={AIModelsPage} />
      <Route path="/bot-builder" component={BotBuilderPage} />
      <Route path="/bot-activity" component={BotActivityPage} />

      {/* Legacy / convenience */}
      <Route path="/chat">
        <Redirect to="/" />
      </Route>

      {/* Fallback */}
      <Route component={NotFound} />
    </Switch>
  );
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <TooltipProvider>
        <Toaster />
        <Router />
      </TooltipProvider>
    </QueryClientProvider>
  );
}

export default App;
