import { useEffect, useState } from 'react';

function renderBadge(value) {
  const normalized = String(value || 'unknown').toLowerCase();
  const cls =
    normalized === 'green' || normalized === 'ship' || normalized === 'in_progress'
      ? 'border border-emerald-400/30 bg-emerald-950/50 text-emerald-200'
      : normalized === 'blocked' || normalized === 'hold' || normalized === 'red'
        ? 'border border-red-400/30 bg-red-950/50 text-red-200'
        : 'border border-amber-500/20 bg-slate-950/60 text-slate-300';

  return <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${cls}`}>{value}</span>;
}

const royalPanel = 'border border-amber-500/30 bg-[radial-gradient(circle_at_top_left,rgba(245,158,11,0.12),transparent_32%),linear-gradient(135deg,rgba(15,23,42,0.98),rgba(6,78,59,0.36),rgba(15,23,42,0.98))] shadow-xl shadow-black/30';
const royalCard = 'border border-amber-500/20 bg-slate-950/70 shadow-inner shadow-amber-950/20';

export default function CommandCenter() {
  const [board, setBoard] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

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
  }, []);

  if (loading) {
    return <p className="text-slate-400">Loading command center…</p>;
  }
  if (error) {
    return <p className="text-dreamco-red">Error: {error}</p>;
  }

  return (
    <div>
      <section className={`relative mb-6 overflow-hidden p-5 ${royalPanel}`}>
        <div className="pointer-events-none absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-amber-300/80 to-transparent" />
        <p className="text-xs font-bold uppercase tracking-[0.18em] text-amber-200">Royal operations command</p>
        <h2 className="mt-2 bg-gradient-to-r from-amber-200 via-yellow-100 to-emerald-200 bg-clip-text text-2xl font-black text-transparent">
          🧭 Max-Parallel Command Center
        </h2>
        <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-300">
          A premium command board for coordinating lanes, blockers, validations, swarm architecture, and ship decisions with Buddy as the supervised governor.
        </p>
      </section>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <div className={`rounded-xl p-4 ${royalCard}`}>
          <p className="text-xs uppercase tracking-wide text-amber-200/70">Target deadline</p>
          <p className="text-amber-100 font-semibold mt-1">{board.target_deadline}</p>
        </div>
        <div className={`rounded-xl p-4 ${royalCard}`}>
          <p className="text-xs uppercase tracking-wide text-amber-200/70">Days remaining</p>
          <p className="text-amber-100 font-semibold mt-1">{board.computed?.days_remaining ?? 0}</p>
        </div>
        <div className={`rounded-xl p-4 ${royalCard}`}>
          <p className="text-xs uppercase tracking-wide text-amber-200/70">Blocked lanes</p>
          <p className="text-amber-100 font-semibold mt-1">{board.computed?.blocked_lanes ?? 0}</p>
        </div>
        <div className={`rounded-xl p-4 ${royalCard}`}>
          <p className="text-xs uppercase tracking-wide text-amber-200/70">Failing validations</p>
          <p className="text-amber-100 font-semibold mt-1">
            {board.computed?.failing_validation_lanes ?? 0}
          </p>
        </div>
        <div className={`rounded-xl p-4 ${royalCard}`}>
          <p className="text-xs uppercase tracking-wide text-amber-200/70">Swarm architectures</p>
          <p className="text-amber-100 font-semibold mt-1">
            {board.computed?.swarm_architecture_count ?? 0}
          </p>
        </div>
        <div className={`rounded-xl p-4 ${royalCard}`}>
          <p className="text-xs uppercase tracking-wide text-amber-200/70">MARL-ready models</p>
          <p className="text-amber-100 font-semibold mt-1">
            {board.computed?.marl_ready_architectures ?? 0}
          </p>
        </div>
      </div>

      <div className={`rounded-xl p-5 mb-6 ${royalPanel}`}>
        <h3 className="text-sm font-semibold text-amber-100 mb-3">Must-Ship Scope</h3>
        <ul className="list-disc ml-5 text-sm text-slate-300 space-y-1">
          {(board.must_ship || []).map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      </div>

      <div className={`rounded-xl p-5 mb-6 overflow-x-auto ${royalPanel}`}>
        <h3 className="text-sm font-semibold text-amber-100 mb-3">Parallel Lane Board</h3>
        <table className="w-full text-sm text-left">
          <thead className="text-xs uppercase tracking-wide text-amber-200/70">
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
              <tr key={lane.lane_id} className="border-t border-amber-500/20">
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
        <div className={`rounded-xl p-5 ${royalCard}`}>
          <h3 className="text-sm font-semibold text-amber-100 mb-3">Execution Cadence</h3>
          <ul className="list-disc ml-5 text-sm text-slate-300 space-y-1">
            {(board.cadence?.daily_cycle || []).map((step) => (
              <li key={step}>{step}</li>
            ))}
          </ul>
          <p className="mt-3 text-xs text-slate-400">{board.cadence?.every_change_policy}</p>
          <p className="mt-1 text-xs text-slate-400">{board.cadence?.weekly_policy}</p>
        </div>

        <div className={`rounded-xl p-5 ${royalCard}`}>
          <h3 className="text-sm font-semibold text-amber-100 mb-3">June 22 Timeline</h3>
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
        <div className={`rounded-xl p-5 overflow-x-auto ${royalCard}`}>
          <h3 className="text-sm font-semibold text-amber-100 mb-3">
            Swarm Architecture Benchmark
          </h3>
          <table className="w-full text-sm text-left">
            <thead className="text-xs uppercase tracking-wide text-amber-200/70">
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
                <tr key={architecture.architecture_id} className="border-t border-amber-500/20">
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

        <div className={`rounded-xl p-5 ${royalCard}`}>
          <h3 className="text-sm font-semibold text-amber-100 mb-3">Coordination Layer</h3>
          <p className="text-sm text-slate-300 mb-3">
            <span className="text-white font-semibold">
              {board.coordination_layer?.governor ?? 'BuddyAI'}
            </span>{' '}
            — {board.coordination_layer?.control_model}
          </p>
          <div className="space-y-4">
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
    </div>
  );
}
