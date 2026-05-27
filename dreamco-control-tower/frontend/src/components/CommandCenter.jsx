import { useEffect, useState } from 'react';

function renderBadge(value) {
  const normalized = String(value || 'unknown').toLowerCase();
  const cls =
    normalized === 'green' || normalized === 'ship' || normalized === 'in_progress'
      ? 'bg-green-900 text-green-300'
      : normalized === 'blocked' || normalized === 'hold' || normalized === 'red'
        ? 'bg-red-900 text-red-300'
        : 'bg-slate-700 text-slate-300';

  return <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${cls}`}>{value}</span>;
}

export default function CommandCenter() {
  const [board, setBoard] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [prospectusList, setProspectusList] = useState([]);
  const [selectedBot, setSelectedBot] = useState('');
  const [botDetails, setBotDetails] = useState(null);
  const [actionStatus, setActionStatus] = useState(null);

  useEffect(() => {
    fetch('/api/command-center')
      .then((r) => r.json())
      .then((data) => {
        if (data.error) {
          throw new Error(data.error);
        }
        setBoard(data);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });

    fetch('/api/command-center/prospectus')
      .then((r) => r.json())
      .then((data) => {
        const bots = Array.isArray(data?.bots) ? data.bots : [];
        setProspectusList(bots);
        if (bots.length > 0) {
          setSelectedBot(bots[0].bot_id);
        }
      })
      .catch(() => setProspectusList([]));
  }, []);

  useEffect(() => {
    if (!selectedBot) {
      setBotDetails(null);
      return;
    }
    fetch(`/api/command-center/prospectus/${selectedBot}`)
      .then((r) => r.json())
      .then((data) => setBotDetails(data))
      .catch(() => setBotDetails(null));
  }, [selectedBot]);

  function runBotAction(action) {
    if (!selectedBot) return;
    fetch(`/api/command-center/bots/${selectedBot}/${action}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ initiated_from: 'command_center_ui' }),
    })
      .then((r) => r.json())
      .then((data) => setActionStatus(data))
      .catch((err) => setActionStatus({ error: err.message }));
  }

  if (loading) {
    return <p className="text-slate-400">Loading command center…</p>;
  }
  if (error) {
    return <p className="text-dreamco-red">Error: {error}</p>;
  }

  return (
    <div>
      <h2 className="text-lg font-semibold text-white mb-4">🧭 Max-Parallel Command Center</h2>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-dreamco-card rounded-xl p-4 border border-slate-700">
          <p className="text-xs text-slate-400">Target deadline</p>
          <p className="text-white font-semibold mt-1">{board.target_deadline}</p>
        </div>
        <div className="bg-dreamco-card rounded-xl p-4 border border-slate-700">
          <p className="text-xs text-slate-400">Days remaining</p>
          <p className="text-white font-semibold mt-1">{board.computed?.days_remaining ?? 0}</p>
        </div>
        <div className="bg-dreamco-card rounded-xl p-4 border border-slate-700">
          <p className="text-xs text-slate-400">Blocked lanes</p>
          <p className="text-white font-semibold mt-1">{board.computed?.blocked_lanes ?? 0}</p>
        </div>
        <div className="bg-dreamco-card rounded-xl p-4 border border-slate-700">
          <p className="text-xs text-slate-400">Failing validations</p>
          <p className="text-white font-semibold mt-1">
            {board.computed?.failing_validation_lanes ?? 0}
          </p>
        </div>
        <div className="bg-dreamco-card rounded-xl p-4 border border-slate-700">
          <p className="text-xs text-slate-400">Swarm architectures</p>
          <p className="text-white font-semibold mt-1">
            {board.computed?.swarm_architecture_count ?? 0}
          </p>
        </div>
        <div className="bg-dreamco-card rounded-xl p-4 border border-slate-700">
          <p className="text-xs text-slate-400">MARL-ready models</p>
          <p className="text-white font-semibold mt-1">
            {board.computed?.marl_ready_architectures ?? 0}
          </p>
        </div>
        <div className="bg-dreamco-card rounded-xl p-4 border border-slate-700">
          <p className="text-xs text-slate-400">Live stigmergy traces</p>
          <p className="text-white font-semibold mt-1">
            {board.computed?.live_stigmergy_traces ?? '—'}
          </p>
        </div>
      </div>

      <div className="bg-dreamco-card rounded-xl p-5 border border-slate-700 mb-6">
        <h3 className="text-sm font-semibold text-slate-200 mb-3">Must-Ship Scope</h3>
        <ul className="list-disc ml-5 text-sm text-slate-300 space-y-1">
          {(board.must_ship || []).map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      </div>

      <div className="bg-dreamco-card rounded-xl p-5 border border-slate-700 mb-6 overflow-x-auto">
        <h3 className="text-sm font-semibold text-slate-200 mb-3">Parallel Lane Board</h3>
        <table className="w-full text-sm text-left">
          <thead className="text-xs uppercase text-slate-400">
            <tr>
              <th className="py-2 pr-4">Lane</th>
              <th className="py-2 pr-4">Owner</th>
              <th className="py-2 pr-4">Status</th>
              <th className="py-2 pr-4">Blockers</th>
              <th className="py-2 pr-4">Validation</th>
              <th className="py-2 pr-4">Ship decision</th>
            </tr>
          </thead>
          <tbody>
            {(board.parallel_lanes || []).map((lane) => (
              <tr key={lane.lane_id} className="border-t border-slate-700">
                <td className="py-3 pr-4 text-white">{lane.name}</td>
                <td className="py-3 pr-4 text-slate-300">{lane.owner}</td>
                <td className="py-3 pr-4">
                  {renderBadge(lane.status)}
                </td>
                <td className="py-3 pr-4 text-slate-300">{lane.blockers?.length || 0}</td>
                <td className="py-3 pr-4">
                  {renderBadge(lane.validation_state)}
                </td>
                <td className="py-3 pr-4">
                  {renderBadge(lane.ship_decision)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-dreamco-card rounded-xl p-5 border border-slate-700">
          <h3 className="text-sm font-semibold text-slate-200 mb-3">Execution Cadence</h3>
          <ul className="list-disc ml-5 text-sm text-slate-300 space-y-1">
            {(board.cadence?.daily_cycle || []).map((step) => (
              <li key={step}>{step}</li>
            ))}
          </ul>
          <p className="mt-3 text-xs text-slate-400">{board.cadence?.every_change_policy}</p>
          <p className="mt-1 text-xs text-slate-400">{board.cadence?.weekly_policy}</p>
        </div>

        <div className="bg-dreamco-card rounded-xl p-5 border border-slate-700">
          <h3 className="text-sm font-semibold text-slate-200 mb-3">June 22 Timeline</h3>
          <ul className="space-y-2 text-sm text-slate-300">
            {(board.timeline || []).map((phase) => (
              <li key={phase.phase}>
                <span className="font-semibold text-white">{phase.phase}:</span> {phase.goal}
              </li>
            ))}
          </ul>
        </div>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-2 gap-6 mt-6">
        <div className="bg-dreamco-card rounded-xl p-5 border border-slate-700 overflow-x-auto">
          <h3 className="text-sm font-semibold text-slate-200 mb-3">
            Swarm Architecture Benchmark
          </h3>
          <table className="w-full text-sm text-left">
            <thead className="text-xs uppercase text-slate-400">
              <tr>
                <th className="py-2 pr-4">Architecture</th>
                <th className="py-2 pr-4">Origin</th>
                <th className="py-2 pr-4">Mode</th>
                <th className="py-2 pr-4">MARL</th>
                <th className="py-2 pr-4">Score</th>
              </tr>
            </thead>
            <tbody>
              {(board.swarm_architectures || []).map((architecture) => (
                <tr key={architecture.architecture_id} className="border-t border-slate-700">
                  <td className="py-3 pr-4 text-white">{architecture.name}</td>
                  <td className="py-3 pr-4 text-slate-300">{architecture.origin}</td>
                  <td className="py-3 pr-4">
                    {renderBadge(architecture.coordination_mode)}
                  </td>
                  <td className="py-3 pr-4">
                    {renderBadge(architecture.marl_ready ? 'ready' : 'planned')}
                  </td>
                  <td className="py-3 pr-4 text-slate-300">
                    {architecture.overall_score ?? '—'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="bg-dreamco-card rounded-xl p-5 border border-slate-700">
          <h3 className="text-sm font-semibold text-slate-200 mb-3">Coordination Layer</h3>
          <p className="text-sm text-slate-300 mb-3">
            <span className="text-white font-semibold">
              {board.coordination_layer?.governor ?? 'BuddyAI'}
            </span>{' '}
            — {board.coordination_layer?.control_model}
          </p>
          <div className="space-y-4">
            <div>
              <p className="text-xs uppercase tracking-wide text-slate-400 mb-2">
                Live Stigmergy Metrics
              </p>
              <p className="text-sm text-slate-300">
                Active traces: {board.stigmergy_metrics?.active_trace_count ?? '—'} · Total strength:{' '}
                {board.stigmergy_metrics?.total_strength ?? '—'}
              </p>
            </div>
            <div>
              <p className="text-xs uppercase tracking-wide text-slate-400 mb-2">
                Communication Layers
              </p>
              <ul className="list-disc ml-5 text-sm text-slate-300 space-y-1">
                {(board.coordination_layer?.communication_layers || []).map((layer) => (
                  <li key={layer}>{layer}</li>
                ))}
              </ul>
            </div>
            <div>
              <p className="text-xs uppercase tracking-wide text-slate-400 mb-2">
                Resilience Features
              </p>
              <ul className="list-disc ml-5 text-sm text-slate-300 space-y-1">
                {(board.coordination_layer?.resilience_features || []).map((feature) => (
                  <li key={feature}>{feature}</li>
                ))}
              </ul>
            </div>
            <div>
              <p className="text-xs uppercase tracking-wide text-slate-400 mb-2">
                Monetization Modes
              </p>
              <ul className="list-disc ml-5 text-sm text-slate-300 space-y-1">
                {(board.coordination_layer?.monetization_modes || []).map((mode) => (
                  <li key={mode}>{mode}</li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      </div>

      <div className="bg-dreamco-card rounded-xl p-5 border border-slate-700 mt-6">
        <h3 className="text-sm font-semibold text-slate-200 mb-3">Per-Bot Prospectus & Operator Surfaces</h3>
        <div className="grid grid-cols-1 lg:grid-cols-[280px_1fr] gap-4">
          <aside className="space-y-2">
            {prospectusList.map((item) => (
              <button
                key={item.bot_id}
                onClick={() => setSelectedBot(item.bot_id)}
                className={`w-full text-left rounded-lg px-3 py-2 text-sm border ${
                  selectedBot === item.bot_id
                    ? 'border-dreamco-accent text-white bg-slate-800'
                    : 'border-slate-700 text-slate-300 bg-slate-900/40'
                }`}
              >
                <p className="font-medium">{item.display_name}</p>
                <p className="text-xs text-slate-400 mt-1">{item.tier}</p>
              </button>
            ))}
          </aside>
          <section className="space-y-3">
            {!botDetails && <p className="text-sm text-slate-400">Select a bot to load runtime prospectus.</p>}
            {botDetails && (
              <>
                <div className="border border-slate-700 rounded-lg p-3 bg-slate-900/30">
                  <p className="text-white font-medium">{botDetails.display_name}</p>
                  <p className="text-xs text-slate-400 mt-1">{botDetails.description || 'No description'}</p>
                  <p className="text-xs text-slate-300 mt-2">
                    Runtime: {botDetails.runtime_manifest?.swarm_runtime} · Semantic stigmergy:{' '}
                    {botDetails.runtime_manifest?.semantic_stigmergy ? 'enabled' : 'disabled'}
                  </p>
                </div>
                <div className="flex flex-wrap gap-2">
                  <button
                    onClick={() => runBotAction('test')}
                    className="px-3 py-1.5 rounded-lg text-xs bg-indigo-700 text-white"
                  >
                    Run Test Surface
                  </button>
                  <button
                    onClick={() => runBotAction('train')}
                    className="px-3 py-1.5 rounded-lg text-xs bg-purple-700 text-white"
                  >
                    Run Train Surface
                  </button>
                  <button
                    onClick={() => runBotAction('run')}
                    className="px-3 py-1.5 rounded-lg text-xs bg-dreamco-accent text-white"
                  >
                    Run Live Surface
                  </button>
                </div>
                {actionStatus && (
                  <div className="border border-slate-700 rounded-lg p-3 bg-slate-900/30 text-xs text-slate-300">
                    {actionStatus.error ? (
                      <span className="text-dreamco-red">{actionStatus.error}</span>
                    ) : (
                      <span>
                        {actionStatus.action} queued · queue id {actionStatus.queue_id} · ETA{' '}
                        {actionStatus.estimated_completion_seconds}s
                      </span>
                    )}
                  </div>
                )}
              </>
            )}
          </section>
        </div>
      </div>
    </div>
  );
}
