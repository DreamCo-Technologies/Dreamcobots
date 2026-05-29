import { useEffect, useState } from 'react';

export default function AgentsPage({ refreshKey = 0 }) {
  const [agents, setAgents] = useState([]);
  const [commands, setCommands] = useState([]);
  const [connectivity, setConnectivity] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    Promise.all([
      fetch('/api/agents').then((res) => res.json()),
      fetch('/api/agents/commands').then((res) => res.json()),
      fetch('/api/global-sources/connectivity').then((res) => res.json()),
    ])
      .then(([agentsRes, commandsRes, connectivityRes]) => {
        setAgents(agentsRes.agents ?? []);
        setCommands(commandsRes.commands ?? []);
        setConnectivity(connectivityRes);
        setError(null);
      })
      .catch((err) => setError(err.message));
  }, [refreshKey]);

  return (
    <section>
      <h2 className="mb-4 text-lg font-semibold text-white">🤝 Agents</h2>
      {error && <p className="mb-4 text-sm text-dreamco-red">Error: {error}</p>}

      <div className="mb-6 rounded-xl border border-slate-700 bg-dreamco-card p-4">
        <h3 className="text-sm font-semibold text-slate-200">Actions ↔ Agents Command Queue</h3>
        <p className="mt-1 text-xs text-slate-400">{commands.length} tracked commands</p>
        <ul className="mt-3 space-y-2 text-xs text-slate-300">
          {commands.slice(0, 5).map((entry) => (
            <li key={entry.command_id} className="rounded-lg border border-slate-700 p-2">
              <p className="text-white">{entry.command}</p>
              <p className="mt-1 text-slate-400">
                {entry.status} • {entry.selected_agent?.name || 'unassigned'}
              </p>
            </li>
          ))}
          {commands.length === 0 && <li className="text-slate-500">No commands dispatched yet.</li>}
        </ul>
      </div>

      <div className="mb-6 rounded-xl border border-slate-700 bg-dreamco-card p-4">
        <h3 className="text-sm font-semibold text-slate-200">Available Agents</h3>
        <div className="mt-3 grid grid-cols-1 gap-2 md:grid-cols-2">
          {agents.map((agent) => (
            <div key={agent.agent_id} className="rounded-lg border border-slate-700 p-3 text-xs">
              <p className="font-medium text-white">{agent.name}</p>
              <p className="text-slate-400">
                {agent.category} • {agent.status}
              </p>
            </div>
          ))}
        </div>
      </div>

      <div className="rounded-xl border border-slate-700 bg-dreamco-card p-4">
        <h3 className="text-sm font-semibold text-slate-200">Buddy Global Sources Connectivity</h3>
        <p className="mt-1 text-xs text-slate-400">
          {connectivity?.connected_modules ?? 0}/{connectivity?.total_modules ?? 0} modules connected
        </p>
        <ul className="mt-3 space-y-2 text-xs text-slate-300">
          {(connectivity?.modules ?? []).map((module) => (
            <li key={module.module} className="rounded-lg border border-slate-700 p-2">
              <p className="text-white">{module.module}</p>
              <p className="mt-1 text-slate-400">{module.status}</p>
            </li>
          ))}
        </ul>
      </div>
    </section>
  );
}
