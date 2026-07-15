import { Switch, Route, Redirect } from "wouter";
import { queryClient } from "./lib/queryClient";
import { QueryClientProvider } from "@tanstack/react-query";
import { Toaster } from "@/components/ui/toaster";
import { TooltipProvider } from "@/components/ui/tooltip";
import { ErrorBoundary } from "@/components/ErrorBoundary";

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
import CodeLabPage from "@/pages/DreamCodeLabPage";
import CryptoPage from "@/pages/CryptoCommandCenter";
import PaymentsPage from "@/pages/PaymentsPage";
import LoansPage from "@/pages/LoansPage";
import ConnectionsPage from "@/pages/ConnectionsPage";
import TimeCapsulePage from "@/pages/TimeCapsulePage";
import CostTrackingPage from "@/pages/CostTrackingPage";
import AILeadersPage from "@/pages/AILeadersPage";
import AIModelsPage from "@/pages/AIModelsPage";
import BotBuilderPage from "@/pages/BotBuilderPage";
import BotActivityPage from "@/pages/BotActivityPage";

function wrap(Page: React.ComponentType, name: string) {
  return function WrappedPage(props: any) {
    return (
      <ErrorBoundary pageName={name}>
        <Page {...props} />
      </ErrorBoundary>
    );
  };
}

function Router() {
  return (
    <Switch>
      <Route path="/" component={wrap(ChatIndexPage, "Chat")} />
      <Route path="/c/:id" component={wrap(ConversationPage, "Conversation")} />
      <Route path="/autonomy" component={wrap(AutonomyPage, "Autonomy")} />
      <Route path="/bots" component={wrap(BotsPage, "Bots")} />
      <Route path="/bot/:id" component={wrap(BotDetailPage, "Bot Detail")} />
      <Route path="/dashboard" component={wrap(DashboardPage, "Dashboard")} />
      <Route path="/divisions" component={wrap(DivisionsPage, "Divisions")} />
      <Route path="/revenue" component={wrap(RevenuePage, "Revenue")} />
      <Route path="/pricing" component={wrap(PricingPage, "Pricing")} />
      <Route path="/deals" component={wrap(DealsPage, "Deals")} />
      <Route path="/debug" component={wrap(DebugPage, "Debug")} />
      <Route path="/ecosystem" component={wrap(EcosystemPage, "Ecosystem")} />
      <Route path="/orchestration" component={wrap(OrchestrationPage, "Orchestration")} />
      <Route path="/marketplace" component={wrap(MarketplacePage, "Marketplace")} />
      <Route path="/formulas" component={wrap(FormulasPage, "Formulas")} />
      <Route path="/learning-matrix" component={wrap(LearningMatrixPage, "Learning Matrix")} />
      <Route path="/business" component={wrap(BusinessPage, "Business")} />
      <Route path="/code-lab" component={wrap(CodeLabPage, "Code Lab")} />
      <Route path="/crypto" component={wrap(CryptoPage, "Crypto")} />
      <Route path="/payments" component={wrap(PaymentsPage, "Payments")} />
      <Route path="/loans" component={wrap(LoansPage, "Loans")} />
      <Route path="/connections" component={wrap(ConnectionsPage, "Connections")} />
      <Route path="/time-capsule" component={wrap(TimeCapsulePage, "Time Capsule")} />
      <Route path="/costs" component={wrap(CostTrackingPage, "Cost Tracking")} />
      <Route path="/ai-leaders" component={wrap(AILeadersPage, "AI Leaders")} />
      <Route path="/ai-models" component={wrap(AIModelsPage, "AI Models")} />
      <Route path="/bot-builder" component={wrap(BotBuilderPage, "Bot Builder")} />
      <Route path="/bot-activity" component={wrap(BotActivityPage, "Bot Activity")} />

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
        <ErrorBoundary pageName="Application">
          <Router />
        </ErrorBoundary>
      </TooltipProvider>
    </QueryClientProvider>
  );
}

export default App;
