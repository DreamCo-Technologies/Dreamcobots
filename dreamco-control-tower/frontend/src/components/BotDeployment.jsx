import { useState } from 'react';

const TEMPLATES = [
  {
    id: 'affiliate',
    label: 'Affiliate Bot',
    description: 'Tracks affiliate links and commissions.',
  },
  { id: 'mining', label: 'Mining Bot', description: 'Automates crypto mining operations.' },
  { id: 'sales', label: 'Sales Bot', description: 'Manages outreach and lead follow-ups.' },
  {
    id: 'deal_finder',
    label: 'Deal Finder Bot',
    description: 'Scans for discount deals and alerts.',
  },
  { id: 'custom', label: 'Custom Bot', description: 'Start from a blank template.' },
];

export default function BotDeployment() {
  const [form, setForm] = useState({ name: '', template: '', niche: '' });
  const [status, setStatus] = useState(null);

  function handleChange(e) {
    setForm((prev) => ({ ...prev, [e.target.name]: e.target.value }));
  }

  async function handleDeploy(e) {
    e.preventDefault();
    if (!form.name || !form.template) {
      setStatus({ type: 'error', message: 'Bot name and template are required.' });
      return;
    }

    setStatus({ type: 'loading', message: 'Deploying bot…' });

    try {
      // POST to the heartbeat endpoint to register the new bot as "active"
      const res = await fetch('/api/bot-heartbeat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ botName: form.name, status: 'active' }),
      });

      if (res.ok) {
        setStatus({ type: 'success', message: `✅ Bot "${form.name}" deployed successfully!` });
        setForm({ name: '', template: '', niche: '' });
      } else {
        const err = await res.json();
        setStatus({ type: 'error', message: err.error ?? 'Deployment failed.' });
      }
    } catch {
      setStatus({ type: 'error', message: 'Could not reach the Control Tower API.' });
    }
  }

  return (
    <div>
      <h2 className="text-lg font-semibold text-white mb-4">🚀 Bot Deployment</h2>

      <div className="bg-dreamco-card rounded-xl p-6 border border-slate-700 max-w-lg">
        <form onSubmit={handleDeploy} className="space-y-4">
          {/* Bot Name */}
          <div>
            <label className="block text-sm text-slate-300 mb-1" htmlFor="name">
              Bot Name
            </label>
            <input
              id="name"
              name="name"
              value={form.name}
              onChange={handleChange}
              placeholder="my-new-bot"
              className="w-full bg-slate-700 text-white rounded-lg px-3 py-2 text-sm border border-slate-600 focus:outline-none focus:border-dreamco-accent"
            />
          </div>

          {/* Template */}
          <div>
            <label className="block text-sm text-slate-300 mb-1" htmlFor="template">
              Template
            </label>
            <select
              id="template"
              name="template"
              value={form.template}
              onChange={handleChange}
              className="w-full bg-slate-700 text-white rounded-lg px-3 py-2 text-sm border border-slate-600 focus:outline-none focus:border-dreamco-accent"
            >
              <option value="">Select a template…</option>
              {TEMPLATES.map((t) => (
                <option key={t.id} value={t.id}>
                  {t.label}
                </option>
              ))}
            </select>
            {form.template && (
              <p className="mt-1 text-xs text-slate-400">
                {TEMPLATES.find((t) => t.id === form.template)?.description}
              </p>
            )}
          </div>

          {/* Niche */}
          <div>
            <label className="block text-sm text-slate-300 mb-1" htmlFor="niche">
              Niche <span className="text-slate-500">(optional)</span>
            </label>
            <input
              id="niche"
              name="niche"
              value={form.niche}
              onChange={handleChange}
              placeholder="e.g. fitness, crypto, real estate"
              className="w-full bg-slate-700 text-white rounded-lg px-3 py-2 text-sm border border-slate-600 focus:outline-none focus:border-dreamco-accent"
            />
          </div>

          <button
            type="submit"
            className="w-full bg-dreamco-accent text-white rounded-lg py-2 text-sm font-semibold hover:bg-indigo-500 transition-colors"
          >
            🚀 Deploy Bot
          </button>
        </form>

        {/* Status message */}
        {status && (
          <div
            className={`mt-4 px-4 py-2 rounded-lg text-sm ${
              status.type === 'success'
                ? 'bg-green-900 text-green-300'
                : status.type === 'error'
                  ? 'bg-red-900 text-red-300'
                  : 'bg-slate-700 text-slate-300'
            }`}
          >
            {status.message}
          </div>
        )}
      </div>
    </div>
  );
}
