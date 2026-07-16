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
const LEGACY_BOTS_FILE = path.join(__dirname, '../config/bots.json');
const GENERATED_BOTS_FILE = path.join(__dirname, '../config/generated/bots.catalog.json');
const SYSTEM_LIBRARY_INDEX_FILE = path.join(
  __dirname,
  '../../config/generated/system_libraries/index.json',
);
const BUDDY_CAPABILITY_INVENTORY_FILE = path.join(
  __dirname,
  '../../reports/buddy_capability_inventory.json',
);
const BUDDY_PRODUCTIVITY_TRACKER_FILE = path.join(
  __dirname,
  '../../reports/buddy_productivity_tracker.json',
);
const DREAMCO_RELEASE_READINESS_FILE = path.join(
  __dirname,
  '../../reports/dreamco_release_readiness.json',
);
const APP_FOUNDRY_READINESS_FILE = path.join(
  __dirname,
  '../../reports/app_foundry_readiness.json',
);
const APP_CATEGORY_CATALOG_FILE = path.join(
  __dirname,
  '../../reports/app_category_catalog.json',
);
const BOT_FOUNDER_APP_STORE_REPORT_FILE = path.join(
  __dirname,
  '../../reports/bot_founder_app_store_report.json',
);
const DREAMCO_24_HOUR_SCALING_REPORT_FILE = path.join(
  __dirname,
  '../../reports/dreamco_24_hour_scaling_report.json',
);
const BUDDY_24_HOUR_CLIENT_PACKAGE_FILE = path.join(
  __dirname,
  '../../reports/buddy_24_hour_client_package.json',
);
const BOT_AUTONOMOUS_REVENUE_PRACTICE_FILE = path.join(
  __dirname,
  '../../reports/bot_autonomous_revenue_practice.json',
);
const SPECIALIZED_BOT_KNOWLEDGE_REPORT_FILE = path.join(
  __dirname,
  '../../reports/specialized_bot_knowledge_report.json',
);
const BUDDY_AI_AGENT_MODEL_LIBRARY_REPORT_FILE = path.join(
  __dirname,
  '../../reports/buddy_ai_agent_model_library_report.json',
);
const BUSINESS_LAUNCH_EXPANSION_REPORT_FILE = path.join(
  __dirname,
  '../../reports/business_launch_expansion_report.json',
);
const BOT_CONTRACT_DISCOVERY_REPORT_FILE = path.join(
  __dirname,
  '../../reports/bot_contract_discovery_report.json',
);
const AI_DATA_PACKAGE_LIBRARY_REPORT_FILE = path.join(
  __dirname,
  '../../reports/ai_data_package_library_report.json',
);
const PEOPLE_JOB_QUALIFICATION_REPORT_FILE = path.join(
  __dirname,
  '../../reports/people_job_qualification_report.json',
);
const BOT_OWNER_SETTINGS_REPORT_FILE = path.join(
  __dirname,
  '../../reports/bot_owner_settings_report.json',
);
const GITHUB_TRIAGE_REPORT_FILE = path.join(
  __dirname,
  '../../reports/github_triage_report.json',
);
const REPOSITORY_STEWARDSHIP_REPORT_FILE = path.join(
  __dirname,
  '../../reports/repository_stewardship_report.json',
);
const STORAGE_GUARD_REPORT_FILE = path.join(
  __dirname,
  '../../reports/storage_guard_report.json',
);
const STRIPE_REVENUE_RESCUE_REPORT_FILE = path.join(
  __dirname,
  '../../reports/stripe_revenue_rescue_report.json',
);
const PRODUCTION_APPROVAL_PACKETS_FILE = path.join(
  __dirname,
  '../../reports/production_approval_packets.json',
);
const BUDDY_BOT_CONNECTION_REPORT_FILE = path.join(
  __dirname,
  '../../reports/buddy_bot_connection_report.json',
);
const COMMAND_CENTER_FILE = path.join(__dirname, '../config/command_center.json');
const PRODUCTION_MEDIA_ROADMAP_FILE = path.join(
  __dirname,
  '../config/production_media_roadmap.json',
);
const BUDDY_OPS_QUEUE_FILE = path.join(__dirname, '../../reports/buddy_ops_queue.json');

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
  if (process.env.NODE_ENV === 'test') {
    return JSON.parse(fs.readFileSync(LEGACY_BOTS_FILE, 'utf8'));
  }

  if (fs.existsSync(GENERATED_BOTS_FILE)) {
    const generated = JSON.parse(fs.readFileSync(GENERATED_BOTS_FILE, 'utf8'));
    const generatedBots = Array.isArray(generated) ? generated : generated.bots ?? [];
    if (!fs.existsSync(LEGACY_BOTS_FILE)) {
      return generatedBots;
    }
    const runtimeBots = JSON.parse(fs.readFileSync(LEGACY_BOTS_FILE, 'utf8'));
    const runtimeByName = new Map(runtimeBots.map((bot) => [bot.name, bot]));
    return generatedBots.map((bot) => ({ ...bot, ...(runtimeByName.get(bot.name) ?? {}) }));
  }

  return JSON.parse(fs.readFileSync(LEGACY_BOTS_FILE, 'utf8'));
}

function writeBots(bots) {
  fs.writeFileSync(LEGACY_BOTS_FILE, JSON.stringify(bots, null, 2));
}

function readCommandCenter() {
  if (!fs.existsSync(COMMAND_CENTER_FILE)) {
    return null;
  }
  return JSON.parse(fs.readFileSync(COMMAND_CENTER_FILE, 'utf8'));
}

function readProductionMediaRoadmap() {
  if (!fs.existsSync(PRODUCTION_MEDIA_ROADMAP_FILE)) {
    return null;
  }
  return JSON.parse(fs.readFileSync(PRODUCTION_MEDIA_ROADMAP_FILE, 'utf8'));
}

function readSystemLibraryIndex() {
  if (!fs.existsSync(SYSTEM_LIBRARY_INDEX_FILE)) {
    return null;
  }
  return JSON.parse(fs.readFileSync(SYSTEM_LIBRARY_INDEX_FILE, 'utf8'));
}

function readBuddyCapabilityInventory() {
  if (!fs.existsSync(BUDDY_CAPABILITY_INVENTORY_FILE)) {
    return null;
  }
  return JSON.parse(fs.readFileSync(BUDDY_CAPABILITY_INVENTORY_FILE, 'utf8'));
}

function readBuddyProductivityTracker() {
  if (!fs.existsSync(BUDDY_PRODUCTIVITY_TRACKER_FILE)) {
    return null;
  }
  return JSON.parse(fs.readFileSync(BUDDY_PRODUCTIVITY_TRACKER_FILE, 'utf8'));
}

function readDreamCoReleaseReadiness() {
  if (!fs.existsSync(DREAMCO_RELEASE_READINESS_FILE)) {
    return null;
  }
  return JSON.parse(fs.readFileSync(DREAMCO_RELEASE_READINESS_FILE, 'utf8'));
}

function readAppFoundryReadiness() {
  if (!fs.existsSync(APP_FOUNDRY_READINESS_FILE)) {
    return null;
  }
  return JSON.parse(fs.readFileSync(APP_FOUNDRY_READINESS_FILE, 'utf8'));
}

function readAppCategoryCatalog() {
  if (!fs.existsSync(APP_CATEGORY_CATALOG_FILE)) {
    return null;
  }
  return JSON.parse(fs.readFileSync(APP_CATEGORY_CATALOG_FILE, 'utf8'));
}

function readBotFounderAppStoreReport() {
  if (!fs.existsSync(BOT_FOUNDER_APP_STORE_REPORT_FILE)) {
    return null;
  }
  return JSON.parse(fs.readFileSync(BOT_FOUNDER_APP_STORE_REPORT_FILE, 'utf8'));
}

function readDreamCo24HourScalingReport() {
  if (!fs.existsSync(DREAMCO_24_HOUR_SCALING_REPORT_FILE)) {
    return null;
  }
  return JSON.parse(fs.readFileSync(DREAMCO_24_HOUR_SCALING_REPORT_FILE, 'utf8'));
}

function readBuddy24HourClientPackage() {
  if (!fs.existsSync(BUDDY_24_HOUR_CLIENT_PACKAGE_FILE)) {
    return null;
  }
  return JSON.parse(fs.readFileSync(BUDDY_24_HOUR_CLIENT_PACKAGE_FILE, 'utf8'));
}

function readBotAutonomousRevenuePractice() {
  if (!fs.existsSync(BOT_AUTONOMOUS_REVENUE_PRACTICE_FILE)) {
    return null;
  }
  return JSON.parse(fs.readFileSync(BOT_AUTONOMOUS_REVENUE_PRACTICE_FILE, 'utf8'));
}

function readSpecializedBotKnowledgeReport() {
  if (!fs.existsSync(SPECIALIZED_BOT_KNOWLEDGE_REPORT_FILE)) {
    return null;
  }
  return JSON.parse(fs.readFileSync(SPECIALIZED_BOT_KNOWLEDGE_REPORT_FILE, 'utf8'));
}

function readBuddyAiAgentModelLibraryReport() {
  if (!fs.existsSync(BUDDY_AI_AGENT_MODEL_LIBRARY_REPORT_FILE)) {
    return null;
  }
  return JSON.parse(fs.readFileSync(BUDDY_AI_AGENT_MODEL_LIBRARY_REPORT_FILE, 'utf8'));
}

function readBusinessLaunchExpansionReport() {
  if (!fs.existsSync(BUSINESS_LAUNCH_EXPANSION_REPORT_FILE)) {
    return null;
  }
  return JSON.parse(fs.readFileSync(BUSINESS_LAUNCH_EXPANSION_REPORT_FILE, 'utf8'));
}

function readBotContractDiscoveryReport() {
  if (!fs.existsSync(BOT_CONTRACT_DISCOVERY_REPORT_FILE)) {
    return null;
  }
  return JSON.parse(fs.readFileSync(BOT_CONTRACT_DISCOVERY_REPORT_FILE, 'utf8'));
}

function readAiDataPackageLibraryReport() {
  if (!fs.existsSync(AI_DATA_PACKAGE_LIBRARY_REPORT_FILE)) {
    return null;
  }
  return JSON.parse(fs.readFileSync(AI_DATA_PACKAGE_LIBRARY_REPORT_FILE, 'utf8'));
}

function readPeopleJobQualificationReport() {
  if (!fs.existsSync(PEOPLE_JOB_QUALIFICATION_REPORT_FILE)) {
    return null;
  }
  return JSON.parse(fs.readFileSync(PEOPLE_JOB_QUALIFICATION_REPORT_FILE, 'utf8'));
}

function readBotOwnerSettingsReport() {
  if (!fs.existsSync(BOT_OWNER_SETTINGS_REPORT_FILE)) {
    return null;
  }
  return JSON.parse(fs.readFileSync(BOT_OWNER_SETTINGS_REPORT_FILE, 'utf8'));
}

function readGitHubTriageReport() {
  if (!fs.existsSync(GITHUB_TRIAGE_REPORT_FILE)) {
    return null;
  }
  return JSON.parse(fs.readFileSync(GITHUB_TRIAGE_REPORT_FILE, 'utf8'));
}

function readRepositoryStewardshipReport() {
  if (!fs.existsSync(REPOSITORY_STEWARDSHIP_REPORT_FILE)) {
    return null;
  }
  return JSON.parse(fs.readFileSync(REPOSITORY_STEWARDSHIP_REPORT_FILE, 'utf8'));
}

function readStorageGuardReport() {
  if (!fs.existsSync(STORAGE_GUARD_REPORT_FILE)) {
    return null;
  }
  return JSON.parse(fs.readFileSync(STORAGE_GUARD_REPORT_FILE, 'utf8'));
}

function readStripeRevenueRescueReport() {
  if (!fs.existsSync(STRIPE_REVENUE_RESCUE_REPORT_FILE)) {
    return null;
  }
  return JSON.parse(fs.readFileSync(STRIPE_REVENUE_RESCUE_REPORT_FILE, 'utf8'));
}

function readProductionApprovalPackets() {
  if (!fs.existsSync(PRODUCTION_APPROVAL_PACKETS_FILE)) {
    return null;
  }
  return JSON.parse(fs.readFileSync(PRODUCTION_APPROVAL_PACKETS_FILE, 'utf8'));
}

function readBuddyBotConnectionReport() {
  if (!fs.existsSync(BUDDY_BOT_CONNECTION_REPORT_FILE)) {
    return null;
  }
  return JSON.parse(fs.readFileSync(BUDDY_BOT_CONNECTION_REPORT_FILE, 'utf8'));
}

function readBuddyOpsQueue() {
  if (!fs.existsSync(BUDDY_OPS_QUEUE_FILE)) {
    return [];
  }
  return JSON.parse(fs.readFileSync(BUDDY_OPS_QUEUE_FILE, 'utf8'));
}

function writeBuddyOpsQueue(queue) {
  fs.mkdirSync(path.dirname(BUDDY_OPS_QUEUE_FILE), { recursive: true });
  fs.writeFileSync(BUDDY_OPS_QUEUE_FILE, `${JSON.stringify(queue, null, 2)}\n`);
}

function slugify(value) {
  return String(value || 'buddy-operation')
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '')
    .slice(0, 64) || 'buddy-operation';
}

function classifyBuddyOperation(prompt) {
  const text = String(prompt || '').toLowerCase();
  if (/(stripe|payment|checkout|invoice|subscription|payout|money|revenue)/.test(text)) {
    return {
      type: 'revenue_operation',
      builder: 'Stripe Revenue Rescue Builder',
      tests: ['npm run report:stripe-rescue', 'backend endpoint tests', 'Actions page payment panel test'],
    };
  }
  if (/(video|music|course|lesson|game|simulation|vibe|image|photo|photoshop|design|brand|document|presentation|dashboard|3d|ar|audio|voice|research|writing)/.test(text)) {
    return {
      type: 'vibe_studio_operation',
      builder: 'Buddy AI Creation Studio Builder',
      tests: ['rights review checklist', 'content safety review', 'sandbox prototype test'],
    };
  }
  if (/(bot|agent|tool|api|webhook|workflow|skill|library)/.test(text)) {
    return {
      type: 'bot_system_operation',
      builder: 'Full Bot System Builder',
      tests: ['npm run check:system-libraries', 'npm run test:generated-bots', 'backend endpoint tests'],
    };
  }
  if (/(deploy|host|pages|hostinger|github pages|production)/.test(text)) {
    return {
      type: 'deployment_operation',
      builder: 'Deployment Gate Builder',
      tests: ['build command', 'deployment readiness gate', 'rollback plan check'],
    };
  }
  return {
    type: 'general_buddy_operation',
    builder: 'Buddy Operations Builder',
    tests: ['repository stewardship scan', 'storage guard', 'Actions page smoke test'],
  };
}

function buildBuddyOperationPacket(prompt, options = {}) {
  const trimmedPrompt = String(prompt || '').trim().slice(0, 2000);
  const now = new Date().toISOString();
  const classification = classifyBuddyOperation(trimmedPrompt);
  const id = `buddy-op-${Date.now()}-${slugify(trimmedPrompt).slice(0, 24)}`;
  return {
    schema: 'dreamco.buddy_operation_packet.v1',
    id,
    created_at: now,
    prompt: trimmedPrompt,
    requested_by: options.requested_by || 'actions_page',
    operation_type: classification.type,
    builder: classification.builder,
    mode: 'sandbox_first_pull_request_review',
    status: 'queued_for_supervised_execution',
    target: options.target || 'dreamcobots',
    branch_hint: `codex/${slugify(trimmedPrompt).slice(0, 32)}`,
    outputs: [
      'implementation plan',
      'changed files list',
      'sandbox test evidence',
      'rollback plan',
      'pull request summary',
    ],
    approval_gates: [
      'owner approval before external outreach',
      'owner approval before money movement',
      'owner approval before production deploy',
      'owner approval before credential changes',
      'pull request review before merge',
    ],
    blocked_live_actions: [
      'payments or payouts',
      'customer messaging',
      'social posting',
      'production deployment',
      'destructive file or git operations',
    ],
    recommended_tests: classification.tests,
    next_actions: [
      'Review the packet scope in the Actions page.',
      'Run the recommended sandbox tests.',
      'Convert the packet into a branch and pull request after owner approval.',
    ],
  };
}

function parseDurationToDays(duration) {
  if (typeof duration !== 'string') {
    return null;
  }
  const normalized = duration.replace(/\s+/g, '').toLowerCase();
  const match = normalized.match(/^(\d+)-(\d+\+?)(weeks?|months?)$/);
  if (!match) {
    return null;
  }
  const [, startRaw, endRaw, unitRaw] = match;
  const start = Number.parseInt(startRaw, 10);
  const end = Number.parseInt(endRaw.replace('+', ''), 10);
  const multiplier = unitRaw.startsWith('month') ? 30 : 7;
  return { minDays: start * multiplier, maxDays: end * multiplier };
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
  let bots;
  try {
    bots = readBots();
  } catch (err) {
    if (err.code === 'ENOENT') {
      return res.status(503).json({ success: false, error: 'bot registry not found' });
    }
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
// GET /api/system-libraries — generated builder and library coverage
// ---------------------------------------------------------------------------
app.get('/api/system-libraries', rateLimiter, (_req, res) => {
  const index = readSystemLibraryIndex();
  if (!index) {
    return res.status(503).json({ error: 'system library index not found' });
  }
  return res.json(index);
});

// ---------------------------------------------------------------------------
// GET /api/buddy-capabilities — latest generated Buddy capability inventory
// ---------------------------------------------------------------------------
app.get('/api/buddy-capabilities', rateLimiter, (_req, res) => {
  const inventory = readBuddyCapabilityInventory();
  if (!inventory) {
    return res.status(503).json({ error: 'buddy capability inventory not found' });
  }
  return res.json(inventory);
});

// ---------------------------------------------------------------------------
// GET /api/buddy-productivity — owner, client, and bot productivity tracking
// ---------------------------------------------------------------------------
app.get('/api/buddy-productivity', rateLimiter, (_req, res) => {
  const tracker = readBuddyProductivityTracker();
  if (!tracker) {
    return res.status(503).json({ error: 'buddy productivity tracker not found' });
  }
  return res.json(tracker);
});

// ---------------------------------------------------------------------------
// GET /api/release-readiness — DreamCo 1.0 plan-versus-proof comparison
// ---------------------------------------------------------------------------
app.get('/api/release-readiness', rateLimiter, (_req, res) => {
  const report = readDreamCoReleaseReadiness();
  if (!report) {
    return res.status(503).json({ error: 'release readiness report not found' });
  }
  return res.json(report);
});

// ---------------------------------------------------------------------------
// GET /api/app-foundry — in-house A-to-Z build, host, and deploy readiness
// ---------------------------------------------------------------------------
app.get('/api/app-foundry', rateLimiter, (_req, res) => {
  const report = readAppFoundryReadiness();
  if (!report) {
    return res.status(503).json({ error: 'app foundry readiness report not found' });
  }
  return res.json(report);
});

// ---------------------------------------------------------------------------
// GET /api/app-category-catalog — app comparison and Buddy management catalog
// ---------------------------------------------------------------------------
app.get('/api/app-category-catalog', rateLimiter, (_req, res) => {
  const report = readAppCategoryCatalog();
  if (!report) {
    return res.status(503).json({ error: 'app category catalog report not found' });
  }
  return res.json(report);
});

// ---------------------------------------------------------------------------
// GET /api/bot-founder-app-store — per-bot founder/app-store readiness
// ---------------------------------------------------------------------------
app.get('/api/bot-founder-app-store', rateLimiter, (_req, res) => {
  const report = readBotFounderAppStoreReport();
  if (!report) {
    return res.status(503).json({ error: 'bot founder app store report not found' });
  }
  return res.json(report);
});

// ---------------------------------------------------------------------------
// GET /api/24-hour-scaling — safe always-on scaling cycle readiness
// ---------------------------------------------------------------------------
app.get('/api/24-hour-scaling', rateLimiter, (_req, res) => {
  const report = readDreamCo24HourScalingReport();
  if (!report) {
    return res.status(503).json({ error: '24-hour scaling report not found' });
  }
  return res.json(report);
});

// ---------------------------------------------------------------------------
// GET /api/buddy-24-hour-package — sellable supervised all-bot client package
// ---------------------------------------------------------------------------
app.get('/api/buddy-24-hour-package', rateLimiter, (_req, res) => {
  const report = readBuddy24HourClientPackage();
  if (!report) {
    return res.status(503).json({ error: 'Buddy 24-hour client package report not found' });
  }
  return res.json(report);
});

// ---------------------------------------------------------------------------
// GET /api/revenue-practice — all-bot sandbox revenue practice system
// ---------------------------------------------------------------------------
app.get('/api/revenue-practice', rateLimiter, (_req, res) => {
  const report = readBotAutonomousRevenuePractice();
  if (!report) {
    return res.status(503).json({ error: 'bot autonomous revenue practice report not found' });
  }
  return res.json(report);
});

// ---------------------------------------------------------------------------
// GET /api/specialized-bot-knowledge — per-bot knowledge profile coverage
// ---------------------------------------------------------------------------
app.get('/api/specialized-bot-knowledge', rateLimiter, (_req, res) => {
  const report = readSpecializedBotKnowledgeReport();
  if (!report) {
    return res.status(503).json({ error: 'specialized bot knowledge report not found' });
  }
  return res.json(report);
});

// ---------------------------------------------------------------------------
// GET /api/ai-agent-model-library — prompt, tool, agent, and model routing
// ---------------------------------------------------------------------------
app.get('/api/ai-agent-model-library', rateLimiter, (_req, res) => {
  const report = readBuddyAiAgentModelLibraryReport();
  if (!report) {
    return res.status(503).json({ error: 'AI agent model library report not found' });
  }
  return res.json(report);
});

// ---------------------------------------------------------------------------
// GET /api/business-launch-expansion — full business start/improve/expand system
// ---------------------------------------------------------------------------
app.get('/api/business-launch-expansion', rateLimiter, (_req, res) => {
  const report = readBusinessLaunchExpansionReport();
  if (!report) {
    return res.status(503).json({ error: 'business launch expansion report not found' });
  }
  return res.json(report);
});

// ---------------------------------------------------------------------------
// GET /api/bot-contract-discovery — continuous contract opportunity search
// ---------------------------------------------------------------------------
app.get('/api/bot-contract-discovery', rateLimiter, (_req, res) => {
  const report = readBotContractDiscoveryReport();
  if (!report) {
    return res.status(503).json({ error: 'bot contract discovery report not found' });
  }
  return res.json(report);
});

// ---------------------------------------------------------------------------
// GET /api/ai-data-package-library — rights-cleared data products for AI buyers
// ---------------------------------------------------------------------------
app.get('/api/ai-data-package-library', rateLimiter, (_req, res) => {
  const report = readAiDataPackageLibraryReport();
  if (!report) {
    return res.status(503).json({ error: 'AI data package library report not found' });
  }
  return res.json(report);
});

// ---------------------------------------------------------------------------
// GET /api/people-job-qualification — privacy-safe people and job fit lookup
// ---------------------------------------------------------------------------
app.get('/api/people-job-qualification', rateLimiter, (_req, res) => {
  const report = readPeopleJobQualificationReport();
  if (!report) {
    return res.status(503).json({ error: 'people job qualification report not found' });
  }
  return res.json(report);
});

// ---------------------------------------------------------------------------
// GET /api/bot-owner-settings — per-bot business owner settings and toggles
// ---------------------------------------------------------------------------
app.get('/api/bot-owner-settings', rateLimiter, (_req, res) => {
  const report = readBotOwnerSettingsReport();
  if (!report) {
    return res.status(503).json({ error: 'bot owner settings report not found' });
  }
  return res.json(report);
});

// ---------------------------------------------------------------------------
// GET /api/github-triage — PR, issue, comment, and workflow scan snapshot
// ---------------------------------------------------------------------------
app.get('/api/github-triage', rateLimiter, (_req, res) => {
  const report = readGitHubTriageReport();
  if (!report) {
    return res.status(503).json({ error: 'github triage report not found' });
  }
  return res.json(report);
});

// ---------------------------------------------------------------------------
// GET /api/repository-stewardship — cleanroom status for PRs, issues, and syntax
// ---------------------------------------------------------------------------
app.get('/api/repository-stewardship', rateLimiter, (_req, res) => {
  const report = readRepositoryStewardshipReport();
  if (!report) {
    return res.status(503).json({ error: 'repository stewardship report not found' });
  }
  return res.json(report);
});

// ---------------------------------------------------------------------------
// GET /api/storage-guard — local-first memory and generated-library budgets
// ---------------------------------------------------------------------------
app.get('/api/storage-guard', rateLimiter, (_req, res) => {
  const report = readStorageGuardReport();
  if (!report) {
    return res.status(503).json({ error: 'storage guard report not found' });
  }
  return res.json(report);
});

// ---------------------------------------------------------------------------
// GET /api/stripe-revenue-rescue — Stripe no-money diagnosis and fix queue
// ---------------------------------------------------------------------------
app.get('/api/stripe-revenue-rescue', rateLimiter, (_req, res) => {
  const report = readStripeRevenueRescueReport();
  if (!report) {
    return res.status(503).json({ error: 'stripe revenue rescue report not found' });
  }
  return res.json(report);
});

// ---------------------------------------------------------------------------
// GET /api/production-approval-packets — final high-risk live-action gate
// ---------------------------------------------------------------------------
app.get('/api/production-approval-packets', rateLimiter, (_req, res) => {
  const report = readProductionApprovalPackets();
  if (!report) {
    return res.status(503).json({ error: 'production approval packets report not found' });
  }
  return res.json(report);
});

// ---------------------------------------------------------------------------
// GET /api/buddy-bot-connections — all-bot Buddy routing/test/resource proof
// ---------------------------------------------------------------------------
app.get('/api/buddy-bot-connections', rateLimiter, (_req, res) => {
  const report = readBuddyBotConnectionReport();
  if (!report) {
    return res.status(503).json({ error: 'buddy bot connection report not found' });
  }
  return res.json(report);
});

// ---------------------------------------------------------------------------
// GET /api/buddy-ops — supervised Buddy operation packet queue
// ---------------------------------------------------------------------------
app.get('/api/buddy-ops', rateLimiter, (_req, res) => {
  const queue = readBuddyOpsQueue();
  return res.json({
    schema: 'dreamco.buddy_ops_queue.v1',
    generated_at: new Date().toISOString(),
    count: queue.length,
    operations: queue.slice(-25).reverse(),
  });
});

// ---------------------------------------------------------------------------
// POST /api/buddy-ops/prompt — create a governed operation packet from a prompt
// ---------------------------------------------------------------------------
app.post('/api/buddy-ops/prompt', rateLimiter, (req, res) => {
  const prompt = String(req.body?.prompt || '').trim();
  if (!prompt) {
    return res.status(400).json({ error: 'prompt is required' });
  }
  if (prompt.length > 2000) {
    return res.status(400).json({ error: 'prompt must be 2000 characters or fewer' });
  }

  const packet = buildBuddyOperationPacket(prompt, {
    requested_by: req.body?.requested_by || 'actions_page',
    target: req.body?.target || 'dreamcobots',
  });
  const queue = readBuddyOpsQueue();
  queue.push(packet);
  writeBuddyOpsQueue(queue.slice(-250));
  return res.status(201).json({ packet });
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
// GET /api/production-media-roadmap — phased implementation timeline
//
// Serves the approved roadmap for voice/image cloning and production media
// features together with computed duration telemetry.
// ---------------------------------------------------------------------------
app.get('/api/production-media-roadmap', rateLimiter, (_req, res) => {
  const roadmap = readProductionMediaRoadmap();
  if (!roadmap) {
    return res.status(503).json({
      error: 'production_media_roadmap.json not found',
    });
  }

  const phases = Array.isArray(roadmap.phases) ? roadmap.phases : [];
  const enrichedPhases = phases.map((phase, index) => {
    const durationDays = parseDurationToDays(phase.duration);
    return {
      ...phase,
      order: index + 1,
      duration_days: durationDays,
    };
  });

  const totals = enrichedPhases.reduce(
    (acc, phase) => {
      if (!phase.duration_days) {
        return acc;
      }
      return {
        minDays: acc.minDays + phase.duration_days.minDays,
        maxDays: acc.maxDays + phase.duration_days.maxDays,
      };
    },
    { minDays: 0, maxDays: 0 },
  );

  return res.json({
    ...roadmap,
    phases: enrichedPhases,
    computed: {
      phase_count: enrichedPhases.length,
      total_duration_days: totals,
      total_duration_months: {
        minMonths: Number((totals.minDays / 30).toFixed(1)),
        maxMonths: Number((totals.maxDays / 30).toFixed(1)),
      },
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
