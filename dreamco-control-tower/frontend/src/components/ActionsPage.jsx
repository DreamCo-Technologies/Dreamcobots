import { useEffect, useMemo, useRef, useState } from 'react';
import { motion } from 'framer-motion';
import { gsap } from 'gsap';
import BuddyTester from './BuddyTester.jsx';
import BuddyCommandCenter from './BuddyCommandCenter.jsx';
import EmbeddedDashboard from './EmbeddedDashboard.jsx';
import ActionsMonitor from './ActionsMonitor.jsx';
import BotMarketplace from './BotMarketplace.jsx';

const TABS = [
  { id: 'buddy-tester', label: 'Live Buddy Tester' },
  { id: 'investor-demo', label: 'Investor Demo' },
  { id: 'dashboards', label: 'All Dashboards' },
  { id: 'swarm', label: 'Swarm Monitor' },
  { id: 'marketplace', label: 'Marketplace' },
  { id: 'dreamos', label: 'DreamOS Controls' },
];

function TabButton({ tab, activeTab, setActiveTab }) {
  return (
    <button
      onClick={() => setActiveTab(tab.id)}
      className={`px-3 py-2 rounded-lg text-xs font-medium transition-colors ${
        activeTab === tab.id
          ? 'bg-dreamco-accent text-white'
          : 'bg-slate-800 text-slate-400 hover:text-white'
      }`}
    >
      {tab.label}
    </button>
  );
}

function InvestorDemoPanel() {
  const metrics = [
    { label: 'Bots running', value: '147' },
    { label: 'Revenue in sim', value: '$2.48M' },
    { label: 'Evolution progress', value: '82%' },
    { label: 'Consensus safety', value: '99.98%' },
  ];

  return (
    <div className="space-y-4">
      <div className="bg-dreamco-card rounded-xl border border-slate-700 p-4">
        <h3 className="text-sm font-semibold text-white mb-2">Investor Demo Mode</h3>
        <p className="text-sm text-slate-300 mb-3">
          Live revenue simulation, swarm visualization, BuddyAI outputs, and pitch narrative.
        </p>
        <a
          href="/investor-demo/index.html"
          target="_blank"
          rel="noreferrer"
          className="inline-flex px-4 py-2 rounded-lg bg-dreamco-accent text-white text-sm font-medium"
        >
          Launch Investor Demo
        </a>
      </div>
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
        {metrics.map((metric) => (
          <div key={metric.label} className="bg-dreamco-card rounded-xl border border-slate-700 p-4">
            <p className="text-xs text-slate-400">{metric.label}</p>
            <p className="text-lg font-semibold text-white mt-1">{metric.value}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

function SwarmMonitorPanel() {
  return (
    <div className="space-y-4">
      <div className="bg-dreamco-card rounded-xl border border-slate-700 p-4">
        <p className="text-sm text-slate-200">Stigmergy + HotStuff orchestration telemetry</p>
        <p className="text-xs text-slate-400 mt-1">
          Active traces: 421 · Consensus rounds/min: 96 · Economic feedback loop: stable
        </p>
      </div>
      <ActionsMonitor />
    </div>
  );
}

function DreamOsPanel() {
  const controls = useMemo(
    () => [
      'DreamBrowser automation bus',
      'DreamOS governance switchboard',
      'Sandbox execution policies',
      'Training roadmap event feed',
    ],
    [],
  );

  return (
    <div className="bg-dreamco-card rounded-xl border border-slate-700 p-5">
      <h3 className="text-sm font-semibold text-white mb-3">DreamBrowser / DreamOS Controls</h3>
      <ul className="list-disc ml-5 space-y-1 text-sm text-slate-300">
        {controls.map((control) => (
          <li key={control}>{control}</li>
        ))}
      </ul>
    </div>
  );
}

export default function ActionsPage() {
  const [activeTab, setActiveTab] = useState('buddy-tester');
  const [showBuddyCenter, setShowBuddyCenter] = useState(false);
  const launchRef = useRef(null);

  useEffect(() => {
    const el = launchRef.current;
    if (!el) return undefined;
    const tween = gsap.to(el, {
      boxShadow: '0 0 24px rgba(99, 102, 241, 0.85)',
      duration: 1.2,
      repeat: -1,
      yoyo: true,
      ease: 'power1.inOut',
    });
    return () => tween.kill();
  }, []);

  return (
    <div className="space-y-5">
      <div className="bg-dreamco-card rounded-xl border border-slate-700 p-5">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-3">
          <div>
            <h2 className="text-lg font-semibold text-white">⚡ Actions Command Hub</h2>
            <p className="text-sm text-slate-400 mt-1">
              Unified live Buddy testing, investor demo, swarm telemetry, and dashboards.
            </p>
          </div>
          <motion.button
            ref={launchRef}
            whileTap={{ scale: 0.98 }}
            onClick={() => setShowBuddyCenter(true)}
            className="px-4 py-2 rounded-lg bg-dreamco-accent text-white text-sm font-semibold"
          >
            Launch Full Buddy Command Center
          </motion.button>
        </div>
      </div>

      <div className="flex flex-wrap gap-2">
        {TABS.map((tab) => (
          <TabButton key={tab.id} tab={tab} activeTab={activeTab} setActiveTab={setActiveTab} />
        ))}
      </div>

      {activeTab === 'buddy-tester' && <BuddyTester />}
      {activeTab === 'investor-demo' && <InvestorDemoPanel />}
      {activeTab === 'dashboards' && <EmbeddedDashboard />}
      {activeTab === 'swarm' && <SwarmMonitorPanel />}
      {activeTab === 'marketplace' && <BotMarketplace />}
      {activeTab === 'dreamos' && <DreamOsPanel />}

      {showBuddyCenter && (
        <div className="fixed inset-0 z-40 bg-black/70 p-4 md:p-10 overflow-auto">
          <div className="max-w-7xl mx-auto bg-dreamco-dark border border-slate-700 rounded-xl p-5">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-white font-semibold">Buddy Command Center</h3>
              <button
                onClick={() => setShowBuddyCenter(false)}
                className="text-xs px-3 py-1.5 rounded bg-slate-700 text-slate-300"
              >
                Close
              </button>
            </div>
            <BuddyCommandCenter />
          </div>
        </div>
      )}
    </div>
  );
}
