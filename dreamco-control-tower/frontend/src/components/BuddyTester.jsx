import { useState } from 'react';
import { motion } from 'framer-motion';

function buildOutput(prompt) {
  const promptText = prompt.trim() || 'No prompt entered';
  return {
    summary: `Executed sandbox simulation for: "${promptText}"`,
    generatedCode: 'Generated workflow scaffold with monetization-safe guardrails.',
    media: 'Prepared ad video + image edit pipeline preview.',
    swarmImpact: 'Swarm load +3%, projected revenue +$1,250/day in simulation.',
  };
}

export default function BuddyTester() {
  const [prompt, setPrompt] = useState('');
  const [status, setStatus] = useState('idle');
  const [history, setHistory] = useState([]);
  const [result, setResult] = useState(null);

  function runPrompt() {
    setStatus('thinking');
    window.setTimeout(() => {
      const output = buildOutput(prompt);
      setResult(output);
      setHistory((prev) => [{ prompt: prompt || 'Untitled prompt', output }, ...prev].slice(0, 8));
      setStatus('success');
    }, 650);
  }

  return (
    <div className="space-y-4">
      <h3 className="text-sm font-semibold text-slate-200">Live Buddy Tester</h3>
      <div className="bg-dreamco-card rounded-xl border border-slate-700 p-4 space-y-3">
        <textarea
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="Try: Create a viral real estate ad video and optimize a trading strategy for it."
          className="w-full min-h-24 bg-slate-800 border border-slate-600 rounded-lg px-3 py-2 text-sm text-white"
        />
        <div className="flex items-center gap-2">
          <button
            onClick={runPrompt}
            className="px-4 py-2 text-sm rounded-lg bg-dreamco-accent text-white hover:bg-indigo-500 transition-colors"
          >
            Run in Sandbox
          </button>
          <span className="text-xs text-slate-400">Governance + consensus gates enforced</span>
        </div>
      </div>

      {status !== 'idle' && (
        <motion.div
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-dreamco-card rounded-xl border border-slate-700 p-4"
        >
          <p className="text-xs text-slate-400 mb-2">
            {status === 'thinking' ? 'Thinking… pulsing swarm state' : 'Simulation complete'}
          </p>
          {result && (
            <div className="space-y-1 text-sm text-slate-200">
              <p>{result.summary}</p>
              <p className="text-slate-300">Code: {result.generatedCode}</p>
              <p className="text-slate-300">Media: {result.media}</p>
              <p className="text-dreamco-green">{result.swarmImpact}</p>
            </div>
          )}
        </motion.div>
      )}

      <div className="bg-dreamco-card rounded-xl border border-slate-700 p-4">
        <p className="text-xs uppercase tracking-wide text-slate-400 mb-2">Replayable History</p>
        <ul className="space-y-2">
          {history.map((entry, idx) => (
            <li key={`${entry.prompt}-${idx}`} className="text-sm text-slate-300">
              <span className="text-white font-medium">{entry.prompt}</span>
              <span className="text-slate-500"> — {entry.output.swarmImpact}</span>
            </li>
          ))}
          {history.length === 0 && <li className="text-sm text-slate-500">No runs yet.</li>}
        </ul>
      </div>
    </div>
  );
}
