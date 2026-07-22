import { Switch, Route, Redirect } from "wouter";
import { lazy, Suspense, type ComponentType } from "react";
import { queryClient } from "./lib/queryClient";
import { QueryClientProvider } from "@tanstack/react-query";
import { Toaster } from "@/components/ui/toaster";
import { TooltipProvider } from "@/components/ui/tooltip";
import { ErrorBoundary } from "@/components/ErrorBoundary";

const NotFound = lazy(() => import("@/pages/not-found"));
const ChatIndexPage = lazy(() => import("@/pages/ChatIndexPage"));
const ConversationPage = lazy(() => import("@/pages/ConversationPage"));
const AutonomyPage = lazy(() => import("@/pages/AutonomyPage"));
const BotsPage = lazy(() => import("@/pages/BotsPage"));
const DashboardPage = lazy(() => import("@/pages/DashboardPage"));
const DivisionsPage = lazy(() => import("@/pages/DivisionsPage"));
const BotDetailPage = lazy(() => import("@/pages/BotDetailPage"));
const RevenuePage = lazy(() => import("@/pages/RevenuePage"));
const PricingPage = lazy(() => import("@/pages/PricingPage"));
const DealsPage = lazy(() => import("@/pages/DealsPage"));
const DebugPage = lazy(() => import("@/pages/DebugPage"));
const EcosystemPage = lazy(() => import("@/pages/EcosystemPage"));
const OrchestrationPage = lazy(() => import("@/pages/OrchestrationPage"));
const MarketplacePage = lazy(() => import("@/pages/MarketplacePage"));
const FormulasPage = lazy(() => import("@/pages/FormulasPage"));
const LearningMatrixPage = lazy(() => import("@/pages/LearningMatrixPage"));
const BusinessPage = lazy(() => import("@/pages/BusinessPage"));
const CodeLabPage = lazy(() => import("@/pages/DreamCodeLabPage"));
const CryptoPage = lazy(() => import("@/pages/CryptoCommandCenter"));
const PaymentsPage = lazy(() => import("@/pages/PaymentsPage"));
const LoansPage = lazy(() => import("@/pages/LoansPage"));
const ConnectionsPage = lazy(() => import("@/pages/ConnectionsPage"));
const TimeCapsulePage = lazy(() => import("@/pages/TimeCapsulePage"));
const CostTrackingPage = lazy(() => import("@/pages/CostTrackingPage"));
const AILeadersPage = lazy(() => import("@/pages/AILeadersPage"));
const AIModelsPage = lazy(() => import("@/pages/AIModelsPage"));
const BotBuilderPage = lazy(() => import("@/pages/BotBuilderPage"));
const BotActivityPage = lazy(() => import("@/pages/BotActivityPage"));
const SandboxPage = lazy(() => import("@/pages/SandboxPage"));
const ActionsPage = lazy(() => import("@/pages/ActionsPage"));
const HarnessPage = lazy(() => import("@/pages/HarnessPage"));
const GovernancePage = lazy(() => import("@/pages/GovernancePage"));
const BuddyPage = lazy(() => import("@/pages/BuddyPage"));
const SettingsPage = lazy(() => import("@/pages/SettingsPage"));

function wrap(Page: ComponentType, name: string) {
  return function WrappedPage(props: any) {
    return (
      <ErrorBoundary pageName={name}>
        <Suspense fallback={<div className="min-h-screen bg-background" aria-label={`Loading ${name}`} />}>
          <Page {...props} />
        </Suspense>
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
      <Route path="/sandbox" component={wrap(SandboxPage, "Sandbox Factory")} />
      <Route path="/actions" component={wrap(ActionsPage, "Actions & Agents")} />
      <Route path="/harness" component={wrap(HarnessPage, "Harness Tester")} />
      <Route path="/governance" component={wrap(GovernancePage, "Governance")} />
      <Route path="/buddy" component={wrap(BuddyPage, "Buddy Bot")} />
      <Route path="/settings" component={wrap(SettingsPage, "Settings")} />

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
