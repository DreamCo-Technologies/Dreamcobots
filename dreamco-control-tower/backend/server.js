/**
 * DreamCo Control Tower — Express.js API Server
 *
 * Endpoints:
 *   POST /api/bot-heartbeat        — update bot status via heartbeat
 *   POST /api/github-webhook       — receive GitHub repository events
 *   GET  /api/bots                 — list all registered bots and their status
 *   GET  /api/get-bots             — list bots with metadata envelope
 *   GET  /api/status               — overall system health
 */

import express from 'express';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const BOTS_FILE = path.join(__dirname, '../config/bots.json');
const COMMAND_CENTER_FILE = path.join(__dirname, '../config/command_center.json');

const app = express();
app.use(express.json());

// ---------------------------------------------------------------------------
// Simple in-process rate limiter (sliding window)
// Protects file-system endpoints from excessive reads.
// ---------------------------------------------------------------------------

const RATE_LIMIT_WINDOW_MS = 60_000; // 1 minute
const RATE_LIMIT_MAX = 60; // max requests per window per IP

const _rateLimitStore = new Map();

function rateLimiter(req, res, next) {
  if (process.env.NODE_ENV === 'test') {
    return next();
  }

  const ip = req.ip || req.connection.remoteAddress || 'unknown';
  const now = Date.now();
  const entry = _rateLimitStore.get(ip) ?? { count: 0, resetAt: now + RATE_LIMIT_WINDOW_MS };

  if (now > entry.resetAt) {
    entry.count = 0;
    entry.resetAt = now + RATE_LIMIT_WINDOW_MS;
  }

  entry.count += 1;
  _rateLimitStore.set(ip, entry);

  if (entry.count > RATE_LIMIT_MAX) {
    return res.status(429).json({ error: 'Too many requests — please slow down.' });
  }

  return next();
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function readBots() {
  return JSON.parse(fs.readFileSync(BOTS_FILE, 'utf8'));
}

function writeBots(bots) {
  fs.writeFileSync(BOTS_FILE, JSON.stringify(bots, null, 2));
}

function readCommandCenter() {
  if (!fs.existsSync(COMMAND_CENTER_FILE)) {
    return null;
  }
  return JSON.parse(fs.readFileSync(COMMAND_CENTER_FILE, 'utf8'));
}

function computeOverallBenchmarkScore(architecture) {
  const benchmark = architecture?.benchmark ?? {};
  const values = Object.values(benchmark).filter((value) => typeof value === 'number');
  if (values.length === 0) {
    return null;
  }
  const average = values.reduce((sum, value) => sum + value, 0) / values.length;
  return Math.round(average * 100) / 100;
}

function heartbeatAgeMinutes(lastHeartbeat) {
  if (!lastHeartbeat) {
    return null;
  }
  const timestamp = new Date(lastHeartbeat).getTime();
  if (Number.isNaN(timestamp)) {
    return null;
  }
  const diffMs = Date.now() - timestamp;
  return Math.max(0, Math.round(diffMs / (1000 * 60)));
}

function botHealthScore(bot) {
  const status = String(bot.status || '').toLowerCase();
  const ageMinutes = heartbeatAgeMinutes(bot.lastHeartbeat);
  if (status === 'active') {
    if (ageMinutes === null) {
      return 80;
    }
    if (ageMinutes <= 5) {
      return 95;
    }
    if (ageMinutes <= 30) {
      return 88;
    }
    return 72;
  }
  if (status === 'idle') {
    return 70;
  }
  if (status === 'failed') {
    return 30;
  }
  return 60;
}

function botAutonomyScore(bot) {
  const features = Array.isArray(bot.features) ? bot.features.length : 0;
  const status = String(bot.status || '').toLowerCase();
  const bonus = status === 'active' ? 15 : 0;
  return Math.min(100, 30 + features * 10 + bonus);
}

function botRevenueImpactScore(bot) {
  const tier = String(bot.tier || '').toUpperCase();
  const base = bot.price_usd ?? 0;
  if (tier === 'ENTERPRISE') {
    return 95;
  }
  if (tier === 'PRO') {
    return Math.min(90, 65 + Math.round(base / 2));
  }
  if (tier === 'STARTER') {
    return Math.min(70, 40 + Math.round(base / 4));
  }
  return Math.min(55, 20 + Math.round(base / 5));
}

function duplicationScoreMap(bots) {
  const categoryCount = new Map();
  bots.forEach((bot) => {
    const category = String(bot.category || 'General');
    categoryCount.set(category, (categoryCount.get(category) ?? 0) + 1);
  });
  const scores = new Map();
  bots.forEach((bot) => {
    const category = String(bot.category || 'General');
    const duplicates = categoryCount.get(category) ?? 1;
    const score = duplicates >= 4 ? 85 : duplicates >= 3 ? 70 : duplicates === 2 ? 45 : 20;
    scores.set(bot.name, score);
  });
  return scores;
}

// ---------------------------------------------------------------------------
// Heartbeat endpoint
// Bots POST here to signal they are online and operational.
// ---------------------------------------------------------------------------
app.post('/api/bot-heartbeat', (req, res) => {
  const { botName, status = 'active' } = req.body;

  if (!botName) {
    return res.status(400).json({ error: 'botName is required' });
  }

  const bots = readBots();
  const bot = bots.find((b) => b.name === botName);

  if (!bot) {
    return res.status(404).json({ error: `Bot '${botName}' not found` });
  }

  bot.lastHeartbeat = new Date().toISOString();
  bot.status = status;
  writeBots(bots);

  console.log(`💓 Heartbeat received from ${botName} — status: ${status}`);
  return res.json({ status: 'updated', bot: botName, lastHeartbeat: bot.lastHeartbeat });
});

// ---------------------------------------------------------------------------
// GitHub webhook endpoint
// Receives events from GitHub: push, pull_request, issues, workflow_run, etc.
// ---------------------------------------------------------------------------
app.post('/api/github-webhook', (req, res) => {
  const event = req.headers['x-github-event'] || 'unknown';
  const payload = req.body;

  console.log(`🔔 GitHub Event: ${event}`);

  switch (event) {
    case 'pull_request': {
      const action = payload.action;
      const pr = payload.pull_request;
      console.log(`  PR #${pr?.number} ${action}: ${pr?.title}`);

      if (action === 'closed' && pr?.merged) {
        console.log('  ✅ PR merged — triggering dependent bot updates');
        // Future: trigger auto-upgrade for dependent bots
      }
      break;
    }

    case 'issues': {
      const issue = payload.issue;
      const label = payload.label?.name;
      if (payload.action === 'labeled' && label === 'bug') {
        console.log(`  🐛 Issue #${issue?.number} labeled 'bug' — scheduling auto-fix`);
        // Future: trigger auto-heal script
      }
      break;
    }

    case 'workflow_run': {
      const wf = payload.workflow_run;
      if (wf?.conclusion === 'failure') {
        console.log(`  ❌ Workflow '${wf?.name}' failed — triggering self-heal`);
        // Future: trigger self-healing automation
      }
      break;
    }

    case 'push': {
      const ref = payload.ref;
      const commits = payload.commits?.length ?? 0;
      console.log(`  📦 Push to ${ref}: ${commits} commit(s)`);
      break;
    }

    default:
      console.log(`  ℹ️ Unhandled event: ${event}`);
  }

  return res.sendStatus(200);
});

// ---------------------------------------------------------------------------
// GET /api/bots — list all bots with current status
// ---------------------------------------------------------------------------
app.get('/api/bots', rateLimiter, (_req, res) => {
  const bots = readBots();
  return res.json(bots);
});

// ---------------------------------------------------------------------------
// GET /api/get-bots — list bots with enriched metadata envelope
// ---------------------------------------------------------------------------
app.get('/api/get-bots', rateLimiter, (_req, res) => {
  if (!fs.existsSync(BOTS_FILE)) {
    return res.status(503).json({ success: false, error: 'bots.json not found' });
  }
  let bots;
  try {
    bots = JSON.parse(fs.readFileSync(BOTS_FILE, 'utf8'));
  } catch (err) {
    return res.status(500).json({ success: false, error: err.message });
  }
  return res.json({
    success: true,
    bots,
    count: bots.length,
    timestamp: new Date().toISOString(),
  });
});

// ---------------------------------------------------------------------------
// GET /api/status — overall system health summary
// ---------------------------------------------------------------------------
app.get('/api/status', rateLimiter, (_req, res) => {
  const bots = readBots();
  const total = bots.length;
  const active = bots.filter((b) => b.status === 'active').length;
  const stale = bots.filter((b) => {
    if (!b.lastHeartbeat) {
      return false;
    }
    const age = Date.now() - new Date(b.lastHeartbeat).getTime();
    return age > 5 * 60 * 1000; // older than 5 minutes
  }).length;

  return res.json({
    dashboard: 'DreamCo Control Tower',
    timestamp: new Date().toISOString(),
    bots: { total, active, stale },
    health: stale > 0 ? 'degraded' : 'healthy',
  });
});

// ---------------------------------------------------------------------------
// GET /api/actions — live GitHub Actions workflow runs (read-only)
//
// Fetches the most recent workflow runs from the GitHub REST API.
// Requires the GITHUB_TOKEN env variable for authenticated requests.
// Gracefully degrades when the token is absent or the API is unreachable.
// ---------------------------------------------------------------------------

const GITHUB_API_BASE = 'https://api.github.com';
const DEFAULT_REPO = process.env.GITHUB_REPO || 'DreamCo-Technologies/Dreamcobots';
const ACTIONS_PER_PAGE = 10;

async function fetchGitHubWorkflowRuns(repo, token) {
  const { default: https } = await import('https');
  return new Promise((resolve) => {
    const headers = {
      'User-Agent': 'dreamco-control-tower',
      Accept: 'application/vnd.github+json',
    };
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const url = new URL(
      `/repos/${repo}/actions/runs?per_page=${ACTIONS_PER_PAGE}`,
      GITHUB_API_BASE,
    );
    const req = https.get(
      { hostname: url.hostname, path: url.pathname + url.search, headers },
      (res) => {
        let body = '';
        res.on('data', (chunk) => (body += chunk));
        res.on('end', () => {
          try {
            const json = JSON.parse(body);
            const runs = (json.workflow_runs ?? []).map((r) => ({
              id: r.id,
              name: r.name,
              status: r.status,
              conclusion: r.conclusion,
              branch: r.head_branch,
              event: r.event,
              run_started_at: r.run_started_at,
              url: r.html_url,
            }));
            resolve({ runs, source: 'github_api' });
          } catch {
            resolve({ runs: [], source: 'parse_error' });
          }
        });
      },
    );
    req.on('error', () => resolve({ runs: [], source: 'unavailable' }));
    req.setTimeout(5000, () => {
      req.destroy();
      resolve({ runs: [], source: 'timeout' });
    });
  });
}

app.get('/api/actions', rateLimiter, async (req, res) => {
  const token = process.env.GITHUB_TOKEN || '';
  const result = await fetchGitHubWorkflowRuns(DEFAULT_REPO, token);
  return res.json({
    repo: DEFAULT_REPO,
    ...result,
    fetched_at: new Date().toISOString(),
  });
});

// ---------------------------------------------------------------------------
// GET /api/catalog — bot catalog for the marketplace UI
//
// Returns the list of bots from bots.json enriched with metadata useful for
// the build-a-bot marketplace (tier, pricing, features).
// ---------------------------------------------------------------------------

app.get('/api/catalog', rateLimiter, (_req, res) => {
  const bots = readBots();
  const catalog = bots.map((b) => ({
    bot_id: b.name.replace(/-/g, '_'),
    display_name: b.name
      .split('-')
      .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
      .join(' '),
    category: b.category || 'General',
    tier: b.tier || 'FREE',
    description: b.description || '',
    price_usd: b.price_usd ?? 0,
    features: b.features || [],
    is_live: b.status === 'active',
  }));
  return res.json(catalog);
});

// ---------------------------------------------------------------------------
// GET /api/orchestrator — BuddyOrchestrator health snapshot
//
// Returns a lightweight status payload showing scraping deadline, catalog
// size, and system health.  Does not expose sensitive data.
// ---------------------------------------------------------------------------

app.get('/api/orchestrator', rateLimiter, (_req, res) => {
  const bots = readBots();
  const deadline = '2026-06-22';
  const today = new Date();
  const deadlineDate = new Date(deadline);
  const daysRemaining = Math.max(
    0,
    Math.ceil((deadlineDate - today) / (1000 * 60 * 60 * 24)),
  );
  const scrapingActive = today <= deadlineDate;

  return res.json({
    orchestrator: 'BuddyOrchestrator',
    github_repo: DEFAULT_REPO,
    catalog_size: bots.length,
    scraping_active: scrapingActive,
    scrape_deadline: deadline,
    days_until_deadline: daysRemaining,
    timestamp: new Date().toISOString(),
  });
});

// ---------------------------------------------------------------------------
// GET /api/command-center — max-parallel execution board
//
// Returns must-ship scope, lane ownership and status, cadence, and timeline
// together with computed deadline telemetry for June 22 delivery.
// ---------------------------------------------------------------------------

app.get('/api/command-center', rateLimiter, (_req, res) => {
  const board = readCommandCenter();
  if (!board) {
    return res.status(503).json({
      error: 'command_center.json not found',
    });
  }

  const today = new Date();
  const targetDate = new Date(board.target_deadline);
  const daysRemaining = Math.max(
    0,
    Math.ceil((targetDate.getTime() - today.getTime()) / (1000 * 60 * 60 * 24)),
  );
  const overdue = today > targetDate;
  const lanes = Array.isArray(board.parallel_lanes) ? board.parallel_lanes : [];
  const architectures = Array.isArray(board.swarm_architectures) ? board.swarm_architectures : [];
  const rankedArchitectures = architectures
    .map((architecture) => ({
      ...architecture,
      overall_score: computeOverallBenchmarkScore(architecture),
    }))
    .sort((a, b) => (b.overall_score ?? -1) - (a.overall_score ?? -1));
  const coordinationLayer = board.coordination_layer ?? {};
  const blockedCount = lanes.filter((lane) => Array.isArray(lane.blockers) && lane.blockers.length > 0).length;
  const failingValidationCount = lanes.filter((lane) => lane.validation_state !== 'green').length;
  const shippableCount = lanes.filter((lane) => lane.ship_decision === 'ship').length;
  const marlReadyCount = rankedArchitectures.filter((architecture) => architecture.marl_ready).length;
  const stigmergicCount = rankedArchitectures.filter((architecture) => architecture.stigmergic).length;

  return res.json({
    ...board,
    coordination_layer: coordinationLayer,
    swarm_architectures: rankedArchitectures,
    computed: {
      days_remaining: daysRemaining,
      overdue,
      blocked_lanes: blockedCount,
      failing_validation_lanes: failingValidationCount,
      shippable_lanes: shippableCount,
      total_lanes: lanes.length,
      swarm_architecture_count: rankedArchitectures.length,
      marl_ready_architectures: marlReadyCount,
      stigmergic_architectures: stigmergicCount,
      best_swarm_architecture: rankedArchitectures[0]?.architecture_id ?? null,
      coordination_layers: (coordinationLayer.communication_layers ?? []).length,
      fetched_at: new Date().toISOString(),
    },
  });
});

// ---------------------------------------------------------------------------
// GET /api/operations-platform — AI operations mission control payload
//
// Exposes the event-driven operating model and critical sections:
// runtime matrix, workflow graph, intelligence layers, and autonomous queue.
// ---------------------------------------------------------------------------

app.get('/api/operations-platform', rateLimiter, (_req, res) => {
  const board = readCommandCenter();
  if (!board) {
    return res.status(503).json({ error: 'command_center.json not found' });
  }

  const bots = readBots();
  const duplicationScores = duplicationScoreMap(bots);
  const lanes = Array.isArray(board.parallel_lanes) ? board.parallel_lanes : [];

  const agentRuntimeMatrix = bots.map((bot) => {
    const features = Array.isArray(bot.features) ? bot.features : [];
    const workflows = Math.max(features.length, bot.pendingPRs ?? 0);
    const status = bot.status || 'unknown';
    return {
      bot_id: bot.name,
      status,
      workflows_active: workflows,
      token_burn_today_usd: Number((Math.max(0.25, workflows * 0.9)).toFixed(2)),
      avg_response_time_ms: status === 'active' ? 2100 : 2900,
      memory_load_pct: Math.min(95, 45 + features.length * 12),
      failures_24h: status === 'active' ? 0 : 1,
      retries_24h: status === 'active' ? 1 : 2,
      hallucination_risk: status === 'active' ? 'low' : 'moderate',
      event_throughput_per_min: status === 'active' ? Math.max(2, workflows * 3) : 1,
    };
  });

  const liveWorkflowGraph = {
    mode: 'event_driven',
    flow: ['event', 'workflow', 'agents', 'memory', 'actions'],
    event_origins: [
      'bot.started',
      'workflow.failed',
      'lead.created',
      'memory.updated',
      'repo.scanned',
      'deployment.failed',
      'payment.received',
    ],
    nodes: lanes.map((lane) => ({
      node_id: lane.lane_id,
      label: lane.name,
      owner: lane.owner,
      status: lane.status,
      validation_state: lane.validation_state,
    })),
    edges: lanes.map((lane) => ({
      from: 'event_bus',
      to: lane.lane_id,
      trigger: 'event.received',
    })),
    approvals_enabled: true,
    retries_visible: true,
    failures_visible: true,
  };

  const botIntelligenceLayer = bots.map((bot) => ({
    bot_id: bot.name,
    autonomy_score: botAutonomyScore(bot),
    revenue_impact_score: botRevenueImpactScore(bot),
    health_score: botHealthScore(bot),
    duplication_score: duplicationScores.get(bot.name) ?? 20,
    dependency_count: Array.isArray(bot.features) ? bot.features.length : 0,
    orphan_detected: bot.status !== 'active' && !bot.lastHeartbeat,
  }));

  const activeBots = bots.filter((bot) => bot.status === 'active').length;
  const paidBots = bots.filter((bot) => (bot.price_usd ?? 0) > 0);
  const monthlyRecurringRevenue = paidBots.reduce((sum, bot) => sum + (bot.price_usd ?? 0), 0);

  const repoIntelligence = {
    architecture_drift_risk: lanes.some((lane) => lane.validation_state !== 'green') ? 'high' : 'low',
    failing_contracts: lanes.filter((lane) => lane.validation_state !== 'green').length,
    unstable_modules: lanes.filter((lane) => lane.status !== 'in_progress').length,
    dead_bots: bots.filter((bot) => bot.status !== 'active' && !bot.lastHeartbeat).length,
    duplicate_system_clusters: [...duplicationScores.values()].filter((score) => score >= 70).length,
    conflicting_pr_risk: lanes.filter((lane) => lane.ship_decision === 'pending').length,
    unreferenced_file_risk: 'monitoring',
    ci_instability: lanes.some((lane) => lane.validation_state === 'red') ? 'high' : 'moderate',
  };

  const autonomousOperationsQueue = [
    {
      action: 'Merge dependency updates',
      priority: 'medium',
      source: 'repo_intelligence',
    },
    {
      action: 'Archive inactive bots',
      priority: bots.length - activeBots >= 5 ? 'high' : 'medium',
      source: 'bot_intelligence_layer',
    },
    {
      action: 'Refactor duplicate orchestration logic',
      priority: repoIntelligence.duplicate_system_clusters > 0 ? 'high' : 'medium',
      source: 'repo_intelligence',
    },
    {
      action: 'Restart failed workflow',
      priority: repoIntelligence.failing_contracts > 0 ? 'high' : 'low',
      source: 'live_workflow_graph',
    },
    {
      action: 'Optimize model routing for token burn',
      priority: 'medium',
      source: 'agent_runtime_matrix',
    },
    {
      action: 'Consolidate memory adapters',
      priority: 'medium',
      source: 'buddy_control_panel',
    },
  ];

  return res.json({
    platform: 'DreamCo OS',
    architecture_mode: 'event_driven',
    core_flow: 'Event -> Workflow -> Agents -> Memory -> Actions',
    pivot_timeline: board.pivot_timeline ?? [],
    delivery_estimates: board.delivery_estimates ?? {},
    fastest_enterprise_impact_path: board.fastest_enterprise_impact_path ?? [],
    central_event_bus: {
      recommended_backends: ['NATS', 'Kafka'],
      contract_model: 'canonical_event_envelope',
      producers: ['bots', 'workflows', 'repo_intelligence', 'revenue_ops'],
      consumers: ['buddy_kernel', 'workflow_engine', 'dashboard_telemetry'],
    },
    agent_runtime_matrix: agentRuntimeMatrix,
    live_workflow_graph: liveWorkflowGraph,
    bot_intelligence_layer: botIntelligenceLayer,
    buddy_control_panel: {
      systems: [
        'Planner',
        'Memory',
        'Routing',
        'Runtime',
        'Knowledge',
        'Event Bus',
        'Revenue Ops',
        'Autonomous Workflows',
      ],
      healthy_system_count: 8,
      exposed_views: ['goals', 'plans', 'task_trees', 'memory_inspection', 'reasoning_traces'],
    },
    revenue_intelligence: {
      leads: activeBots * 4,
      conversion_rate_pct: 18,
      outreach_sequences: bots.length * 2,
      proposals_open: Math.max(1, paidBots.length),
      close_rate_pct: 11,
      mrr_usd: monthlyRecurringRevenue,
      automation_savings_usd: activeBots * 120,
      ai_roi_ratio: Number((1 + activeBots / Math.max(1, bots.length)).toFixed(2)),
    },
    repo_intelligence: repoIntelligence,
    autonomous_operations_queue: autonomousOperationsQueue,
    computed: {
      total_bots: bots.length,
      active_bots: activeBots,
      automation_ratio_pct: bots.length === 0 ? 0 : Math.round((activeBots / bots.length) * 100),
      workflow_nodes: liveWorkflowGraph.nodes.length,
      recommended_actions: autonomousOperationsQueue.length,
      fetched_at: new Date().toISOString(),
    },
  });
});

// ---------------------------------------------------------------------------
// Start server (only when not in test mode)
// ---------------------------------------------------------------------------
const PORT = process.env.PORT || 4000;
if (process.env.NODE_ENV !== 'test') {
  app.listen(PORT, () => {
    console.log(`🚀 Control Tower API running on port ${PORT}`);
  });
}

export { app };
export default app;
