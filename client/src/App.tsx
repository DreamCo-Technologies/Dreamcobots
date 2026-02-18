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
