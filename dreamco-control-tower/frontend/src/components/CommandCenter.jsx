import { useEffect, useState } from 'react';

function Badge({ value }) {
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

  useEffect(() => {
    fetch('/api/command-center')
      .then((r) => r.json())
      .then((data) => {
        if (data.error) throw new Error(data.error);
        setBoard(data);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  if (loading) return <p className="text-slate-400">Loading command center…</p>;
  if (error) return <p className="text-dreamco-red">Error: {error}</p>;

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
                  <Badge value={lane.status} />
                </td>
                <td className="py-3 pr-4 text-slate-300">{lane.blockers?.length || 0}</td>
                <td className="py-3 pr-4">
                  <Badge value={lane.validation_state} />
                </td>
                <td className="py-3 pr-4">
                  <Badge value={lane.ship_decision} />
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
    </div>
  );
}
