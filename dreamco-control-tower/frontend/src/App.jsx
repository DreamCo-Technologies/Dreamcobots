import { useState } from 'react';
import BotOverview from './components/BotOverview.jsx';
import RepoActivity from './components/RepoActivity.jsx';
import BotDeployment from './components/BotDeployment.jsx';
import Analytics from './components/Analytics.jsx';
import ActionsPage from './components/ActionsPage.jsx';
import AgentsPage from './components/AgentsPage.jsx';
import BotMarketplace from './components/BotMarketplace.jsx';
import CommandCenter from './components/CommandCenter.jsx';

const NAV_ITEMS = [
  { id: 'overview', label: '🤖 Bot Overview' },
  { id: 'activity', label: '📦 Repo Activity' },
  { id: 'deploy', label: '🚀 Bot Deployment' },
  { id: 'analytics', label: '📊 Analytics' },
  { id: 'actions', label: '⚡ Actions' },
  { id: 'agents', label: '🤝 Agents' },
  { id: 'marketplace', label: '🛒 Marketplace' },
  { id: 'command-center', label: '🧭 Command Center' },
];

export default function App() {
  const [activeTab, setActiveTab] = useState('overview');
  const [lastDispatch, setLastDispatch] = useState(null);
  const [agentsRefreshKey, setAgentsRefreshKey] = useState(0);

  async function handleBuddyCommandSubmit(command) {
    try {
      const response = await fetch('/api/agents/dispatch', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ command }),
      });
      const payload = await response.json();
      setLastDispatch(payload);
      setAgentsRefreshKey((value) => value + 1);
    } catch (error) {
      setLastDispatch({
        duplicate: false,
        command: { command },
        selected_agent: null,
        error: error.message,
      });
    }
  }

  return (
    <div className="min-h-screen flex flex-col">
      {/* Header */}
      <header className="bg-dreamco-card border-b border-slate-700 px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <span className="text-2xl">🏰</span>
          <h1 className="text-xl font-bold text-white">DreamCo Control Tower</h1>
        </div>
        <span className="text-xs text-slate-400">Autonomous Bot Management Hub</span>
      </header>

      <div className="flex flex-1">
        {/* Sidebar */}
        <nav className="w-56 bg-dreamco-card border-r border-slate-700 p-4 flex flex-col gap-1">
          {NAV_ITEMS.map((item) => (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              className={`text-left px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                activeTab === item.id
                  ? 'bg-dreamco-accent text-white'
                  : 'text-slate-400 hover:bg-slate-700 hover:text-white'
              }`}
            >
              {item.label}
            </button>
          ))}
        </nav>

        {/* Main content */}
        <main className="flex-1 p-6 overflow-auto">
          {activeTab === 'overview' && <BotOverview />}
          {activeTab === 'activity' && <RepoActivity />}
          {activeTab === 'deploy' && <BotDeployment />}
          {activeTab === 'analytics' && <Analytics />}
          {activeTab === 'actions' && (
            <ActionsPage
              onBuddyCommandSubmit={handleBuddyCommandSubmit}
              lastDispatch={lastDispatch}
              onOpenAgentsPage={() => setActiveTab('agents')}
            />
          )}
          {activeTab === 'agents' && <AgentsPage refreshKey={agentsRefreshKey} />}
          {activeTab === 'marketplace' && <BotMarketplace />}
          {activeTab === 'command-center' && <CommandCenter />}
        </main>
      </div>
    </div>
  );
}
