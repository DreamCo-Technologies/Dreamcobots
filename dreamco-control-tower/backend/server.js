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
const REPLIT_BOTS_DIR = path.join(__dirname, '../../bots');
const MAX_COMMAND_LOG = 200;

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
  const botsFromConfig = JSON.parse(fs.readFileSync(BOTS_FILE, 'utf8'));
  const forceSync = process.env.INCLUDE_REPLIT_PROFILE_SYNC === '1';
  if ((!forceSync && process.env.NODE_ENV === 'test') || process.env.INCLUDE_REPLIT_PROFILE_SYNC === '0') {
    return botsFromConfig;
  }

  const mergedBots = new Map();
  for (const bot of botsFromConfig) {
    if (bot?.name) {
      mergedBots.set(String(bot.name).toLowerCase(), bot);
    }
  }
  for (const bot of readReplitProfileBots()) {
    const key = String(bot.name).toLowerCase();
    if (!mergedBots.has(key)) {
      mergedBots.set(key, bot);
    }
  }

  return [...mergedBots.values()];
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

  function normaliseStatus(status) {
    const value = String(status || '').toLowerCase();
    if (value === 'active' || value === 'idle') {
      return value;
    }
    if (value === 'inactive' || value === 'paused') {
      return 'idle';
    }
    return 'active';
  }

  function readReplitProfileBots() {
    if (!fs.existsSync(REPLIT_BOTS_DIR)) {
      return [];
    }

    const bots = [];
    let directories = [];
    try {
      directories = fs.readdirSync(REPLIT_BOTS_DIR, { withFileTypes: true });
    } catch {
      return [];
    }

    for (const entry of directories) {
      if (!entry.isDirectory()) {
        continue;
      }
      const profilePath = path.join(REPLIT_BOTS_DIR, entry.name, 'replit_profile.json');
      if (!fs.existsSync(profilePath)) {
        continue;
      }
      try {
        const profile = JSON.parse(fs.readFileSync(profilePath, 'utf8'));
        const slug = String(profile.slug || entry.name);
        bots.push({
          name: slug,
          repoName: 'Dreamcobots',
          repoPath: `./bots/${slug}`,
          status: normaliseStatus(profile.status),
          tier: String(profile.tier || 'FREE').toUpperCase(),
          category: profile.category || 'General',
          description: profile.description || '',
          price_usd: 0,
          features: Array.isArray(profile.capabilities) ? profile.capabilities : [],
          lastHeartbeat: null,
          lastUpdate: null,
          pendingPRs: 0,
        });
      } catch {
        continue;
      }
    }
    return bots;
  }
  const average = values.reduce((sum, value) => sum + value, 0) / values.length;
  return Math.round(average * 100) / 100;
}

const agentCommandLog = [];

const GLOBAL_SOURCES_CONNECTIVITY_CHECKLIST = [
  { module: 'bots/global_sources_ai_bot/global_sources_ai_bot.py', status: 'connected' },
  { module: 'bots/global_sources_ai_bot/benchmarks.py', status: 'connected' },
  { module: 'bots/global_sources_ai_bot/task_router.py', status: 'connected' },
  { module: 'bots/global_sources_ai_bot/model_registry.py', status: 'connected' },
  { module: 'bots/global_sources_ai_bot/tiers.py', status: 'connected' },
  { module: 'framework/global_ai_sources_flow.py', status: 'connected' },
];

function normaliseCommand(command) {
  return command.toLowerCase().replace(/\s+/g, ' ').trim();
}

function tokenizeCommand(command) {
  return new Set(normaliseCommand(command).split(' ').filter((token) => token.length > 2));
}

function scoreAgentForCommand(agent, tokens) {
  const haystack = [
    agent.name,
    agent.category,
    agent.description,
    ...(Array.isArray(agent.features) ? agent.features : []),
  ]
    .join(' ')
    .toLowerCase();

  let score = 0;
  for (const token of tokens) {
    if (haystack.includes(token)) {
      score += 2;
    }
  }

  if (agent.status === 'active') {
    score += 1.5;
  }
  if (String(agent.name || '').toLowerCase().includes('buddy')) {
    score += 1;
  }
  return score;
}

function rankAgentsForCommand(command, agents) {
  const tokens = tokenizeCommand(command);
  return [...agents]
    .map((agent) => ({
      ...agent,
      orchestration_score: Math.round(scoreAgentForCommand(agent, tokens) * 100) / 100,
    }))
    .sort((a, b) => b.orchestration_score - a.orchestration_score);
}

function trimCommandLog() {
  if (agentCommandLog.length > MAX_COMMAND_LOG) {
    agentCommandLog.splice(MAX_COMMAND_LOG);
  }
}

export function resetAgentDispatchState() {
  agentCommandLog.length = 0;
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
// GET /api/agents — list agents that can receive Actions commands
// ---------------------------------------------------------------------------

app.get('/api/agents', rateLimiter, (_req, res) => {
  const agents = readBots().map((bot) => ({
    agent_id: bot.name.replace(/-/g, '_'),
    name: bot.name,
    category: bot.category || 'General',
    status: bot.status || 'idle',
    tier: bot.tier || 'FREE',
    description: bot.description || '',
    features: bot.features || [],
  }));
  return res.json({
    count: agents.length,
    agents,
    fetched_at: new Date().toISOString(),
  });
});

// ---------------------------------------------------------------------------
// GET /api/agents/commands — command dispatch history
// ---------------------------------------------------------------------------

app.get('/api/agents/commands', rateLimiter, (_req, res) => {
  return res.json({
    count: agentCommandLog.length,
    commands: agentCommandLog,
    fetched_at: new Date().toISOString(),
  });
});

// ---------------------------------------------------------------------------
// POST /api/agents/dispatch — duplicate-safe command dispatch
// ---------------------------------------------------------------------------

app.post('/api/agents/dispatch', (req, res) => {
  const command = String(req.body?.command || '').trim();
  if (!command) {
    return res.status(400).json({ error: 'command is required' });
  }

  const normalized = normaliseCommand(command);
  const duplicate = agentCommandLog.find((entry) => entry.normalized_command === normalized);
  const bots = readBots();
  const rankedCandidates = rankAgentsForCommand(command, bots).slice(0, 5);
  const selected = rankedCandidates[0];

  if (duplicate) {
    return res.json({
      dispatched: false,
      duplicate: true,
      duplicate_of: duplicate.command_id,
      command: duplicate,
      selected_agent: duplicate.selected_agent,
      ranked_candidates: rankedCandidates.map((agent) => ({
        agent_id: agent.name.replace(/-/g, '_'),
        name: agent.name,
        score: agent.orchestration_score,
      })),
    });
  }

  const commandEntry = {
    command_id: `cmd_${Date.now()}`,
    command,
    normalized_command: normalized,
    status: 'queued',
    selected_agent: selected
      ? {
          agent_id: selected.name.replace(/-/g, '_'),
          name: selected.name,
          status: selected.status,
          tier: selected.tier,
        }
      : null,
    ranked_candidates: rankedCandidates.map((agent) => ({
      agent_id: agent.name.replace(/-/g, '_'),
      name: agent.name,
      score: agent.orchestration_score,
    })),
    dispatched_at: new Date().toISOString(),
  };

  agentCommandLog.unshift(commandEntry);
  trimCommandLog();

  return res.status(201).json({
    dispatched: true,
    duplicate: false,
    command: commandEntry,
    selected_agent: commandEntry.selected_agent,
  });
});

// ---------------------------------------------------------------------------
// GET /api/global-sources/connectivity — Buddy module connectivity checklist
// ---------------------------------------------------------------------------

app.get('/api/global-sources/connectivity', rateLimiter, (_req, res) => {
  const modules = GLOBAL_SOURCES_CONNECTIVITY_CHECKLIST.map((item) => ({
    ...item,
    buddy_channel: 'buddy_global_sources',
  }));
  const connectedModules = modules.filter((module) => module.status === 'connected').length;

  return res.json({
    buddy_channel: 'buddy_global_sources',
    total_modules: modules.length,
    connected_modules: connectedModules,
    all_connected: connectedModules === modules.length,
    modules,
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
