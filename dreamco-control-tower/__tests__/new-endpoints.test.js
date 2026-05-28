import request from 'supertest';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

process.env.NODE_ENV = 'test';

const BOTS_FILE = path.join(__dirname, '..', 'config', 'bots.json');

const SAMPLE_BOTS = [
  {
    name: 'buddy-bot',
    repoName: 'Dreamcobots',
    repoPath: './bots/buddy_bot',
    status: 'active',
    tier: 'PRO',
    category: 'AI Companion',
    description: 'The most human-like AI companion.',
    price_usd: 49,
    features: ['Emotion detection', 'Voice synthesis'],
    lastHeartbeat: null,
    lastUpdate: null,
    pendingPRs: 0,
  },
  {
    name: 'sales-bot',
    repoName: 'Dreamcobots',
    repoPath: './bots/sales_bot',
    status: 'idle',
    tier: 'FREE',
    category: 'Sales',
    description: 'Automated sales outreach.',
    price_usd: 0,
    features: ['LeadQualifier', 'EmailSequencer'],
    lastHeartbeat: null,
    lastUpdate: null,
    pendingPRs: 0,
  },
];

let app;
let originalBotsContent;

beforeAll(async () => {
  originalBotsContent = fs.readFileSync(BOTS_FILE, 'utf8');
  const module = await import('../backend/server.js');
  app = module.default;
});

afterAll(() => {
  fs.writeFileSync(BOTS_FILE, originalBotsContent);
});

beforeEach(() => {
  fs.writeFileSync(BOTS_FILE, JSON.stringify(SAMPLE_BOTS, null, 2));
});

// ---------------------------------------------------------------------------
// GET /api/catalog
// ---------------------------------------------------------------------------

describe('GET /api/catalog', () => {
  test('returns 200', async () => {
    const res = await request(app).get('/api/catalog');
    expect(res.status).toBe(200);
  });

  test('returns a JSON array', async () => {
    const res = await request(app).get('/api/catalog');
    expect(Array.isArray(res.body)).toBe(true);
  });

  test('array length matches bots.json length', async () => {
    const res = await request(app).get('/api/catalog');
    expect(res.body.length).toBe(SAMPLE_BOTS.length);
  });

  test('each item has bot_id', async () => {
    const res = await request(app).get('/api/catalog');
    res.body.forEach((item) => expect(item).toHaveProperty('bot_id'));
  });

  test('each item has display_name', async () => {
    const res = await request(app).get('/api/catalog');
    res.body.forEach((item) => expect(item).toHaveProperty('display_name'));
  });

  test('each item has tier', async () => {
    const res = await request(app).get('/api/catalog');
    res.body.forEach((item) => expect(item).toHaveProperty('tier'));
  });

  test('each item has price_usd', async () => {
    const res = await request(app).get('/api/catalog');
    res.body.forEach((item) => expect(item).toHaveProperty('price_usd'));
  });

  test('each item has features array', async () => {
    const res = await request(app).get('/api/catalog');
    res.body.forEach((item) => {
      expect(item).toHaveProperty('features');
      expect(Array.isArray(item.features)).toBe(true);
    });
  });

  test('each item has is_live boolean', async () => {
    const res = await request(app).get('/api/catalog');
    res.body.forEach((item) => {
      expect(item).toHaveProperty('is_live');
      expect(typeof item.is_live).toBe('boolean');
    });
  });

  test('active bot is_live is true', async () => {
    const res = await request(app).get('/api/catalog');
    const buddy = res.body.find((b) => b.bot_id === 'buddy_bot');
    expect(buddy.is_live).toBe(true);
  });

  test('idle bot is_live is false', async () => {
    const res = await request(app).get('/api/catalog');
    const sales = res.body.find((b) => b.bot_id === 'sales_bot');
    expect(sales.is_live).toBe(false);
  });

  test('dashes in name converted to underscores in bot_id', async () => {
    const res = await request(app).get('/api/catalog');
    res.body.forEach((item) => {
      expect(item.bot_id).not.toContain('-');
    });
  });

  test('display_name is title-cased', async () => {
    const res = await request(app).get('/api/catalog');
    const buddy = res.body.find((b) => b.bot_id === 'buddy_bot');
    // "buddy-bot" → "Buddy Bot"
    expect(buddy.display_name).toBe('Buddy Bot');
  });

  test('propagates description from bots.json', async () => {
    const res = await request(app).get('/api/catalog');
    const buddy = res.body.find((b) => b.bot_id === 'buddy_bot');
    expect(buddy.description).toBe('The most human-like AI companion.');
  });

  test('propagates features from bots.json', async () => {
    const res = await request(app).get('/api/catalog');
    const buddy = res.body.find((b) => b.bot_id === 'buddy_bot');
    expect(buddy.features).toContain('Emotion detection');
  });

  test('returns empty array when bots.json is empty', async () => {
    fs.writeFileSync(BOTS_FILE, '[]');
    const res = await request(app).get('/api/catalog');
    expect(res.status).toBe(200);
    expect(res.body).toEqual([]);
  });
});

// ---------------------------------------------------------------------------
// GET /api/orchestrator
// ---------------------------------------------------------------------------

describe('GET /api/orchestrator', () => {
  test('returns 200', async () => {
    const res = await request(app).get('/api/orchestrator');
    expect(res.status).toBe(200);
  });

  test('has orchestrator field', async () => {
    const res = await request(app).get('/api/orchestrator');
    expect(res.body).toHaveProperty('orchestrator', 'BuddyOrchestrator');
  });

  test('has github_repo field', async () => {
    const res = await request(app).get('/api/orchestrator');
    expect(res.body).toHaveProperty('github_repo');
    expect(typeof res.body.github_repo).toBe('string');
  });

  test('has catalog_size matching bots.json', async () => {
    const res = await request(app).get('/api/orchestrator');
    expect(res.body.catalog_size).toBe(SAMPLE_BOTS.length);
  });

  test('has scrape_deadline field', async () => {
    const res = await request(app).get('/api/orchestrator');
    expect(res.body).toHaveProperty('scrape_deadline', '2026-06-22');
  });

  test('has days_until_deadline as non-negative number', async () => {
    const res = await request(app).get('/api/orchestrator');
    expect(typeof res.body.days_until_deadline).toBe('number');
    expect(res.body.days_until_deadline).toBeGreaterThanOrEqual(0);
  });

  test('has scraping_active boolean', async () => {
    const res = await request(app).get('/api/orchestrator');
    expect(typeof res.body.scraping_active).toBe('boolean');
  });

  test('has timestamp as valid ISO string', async () => {
    const res = await request(app).get('/api/orchestrator');
    expect(typeof res.body.timestamp).toBe('string');
    expect(() => new Date(res.body.timestamp)).not.toThrow();
  });

  test('scraping_active is true before June 22 2026', async () => {
    // Current date (2026-05-02) is before deadline
    const res = await request(app).get('/api/orchestrator');
    expect(res.body.scraping_active).toBe(true);
  });
});

// ---------------------------------------------------------------------------
// GET /api/actions
// ---------------------------------------------------------------------------

describe('GET /api/actions', () => {
  test('returns 200', async () => {
    const res = await request(app).get('/api/actions');
    expect(res.status).toBe(200);
  });

  test('has runs array', async () => {
    const res = await request(app).get('/api/actions');
    expect(Array.isArray(res.body.runs)).toBe(true);
  });

  test('has source field', async () => {
    const res = await request(app).get('/api/actions');
    expect(res.body).toHaveProperty('source');
  });

  test('has repo field', async () => {
    const res = await request(app).get('/api/actions');
    expect(res.body).toHaveProperty('repo');
  });

  test('has fetched_at ISO timestamp', async () => {
    const res = await request(app).get('/api/actions');
    expect(res.body).toHaveProperty('fetched_at');
    expect(typeof res.body.fetched_at).toBe('string');
  });

  test('does not throw without GITHUB_TOKEN', async () => {
    const orig = process.env.GITHUB_TOKEN;
    delete process.env.GITHUB_TOKEN;
    const res = await request(app).get('/api/actions');
    expect(res.status).toBe(200);
    if (orig !== undefined) {
      process.env.GITHUB_TOKEN = orig;
    }
  });

  test('returns content-type json', async () => {
    const res = await request(app).get('/api/actions');
    expect(res.headers['content-type']).toMatch(/application\/json/);
  });
});

// ---------------------------------------------------------------------------
// GET /api/command-center
// ---------------------------------------------------------------------------

describe('GET /api/command-center', () => {
  test('returns 200', async () => {
    const res = await request(app).get('/api/command-center');
    expect(res.status).toBe(200);
  });

  test('returns target deadline', async () => {
    const res = await request(app).get('/api/command-center');
    expect(res.body).toHaveProperty('target_deadline', '2026-06-22');
  });

  test('returns must_ship list', async () => {
    const res = await request(app).get('/api/command-center');
    expect(Array.isArray(res.body.must_ship)).toBe(true);
    expect(res.body.must_ship.length).toBeGreaterThan(0);
  });

  test('returns parallel_lanes list with owner/status fields', async () => {
    const res = await request(app).get('/api/command-center');
    expect(Array.isArray(res.body.parallel_lanes)).toBe(true);
    res.body.parallel_lanes.forEach((lane) => {
      expect(lane).toHaveProperty('owner');
      expect(lane).toHaveProperty('status');
      expect(lane).toHaveProperty('validation_state');
      expect(lane).toHaveProperty('ship_decision');
    });
  });

  test('returns computed telemetry', async () => {
    const res = await request(app).get('/api/command-center');
    expect(res.body).toHaveProperty('computed');
    expect(typeof res.body.computed.days_remaining).toBe('number');
    expect(typeof res.body.computed.total_lanes).toBe('number');
  });

  test('returns swarm architecture benchmarks', async () => {
    const res = await request(app).get('/api/command-center');
    expect(Array.isArray(res.body.swarm_architectures)).toBe(true);
    expect(res.body.swarm_architectures.length).toBeGreaterThan(0);
    expect(res.body.swarm_architectures[0]).toHaveProperty('overall_score');
  });

  test('returns coordination layer governance metadata', async () => {
    const res = await request(app).get('/api/command-center');
    expect(res.body.coordination_layer).toHaveProperty('governor', 'BuddyAI');
    expect(Array.isArray(res.body.coordination_layer.communication_layers)).toBe(true);
  });

  test('computes best swarm architecture', async () => {
    const res = await request(app).get('/api/command-center');
    expect(res.body.computed.best_swarm_architecture).toBe('hybrid_llm_marl');
    expect(typeof res.body.computed.marl_ready_architectures).toBe('number');
  });

  test('returns pivot timeline and delivery estimates', async () => {
    const res = await request(app).get('/api/command-center');
    expect(Array.isArray(res.body.pivot_timeline)).toBe(true);
    expect(res.body.pivot_timeline.length).toBeGreaterThanOrEqual(9);
    expect(res.body.delivery_estimates).toMatchObject({
      aggressive_weeks: '12-14',
      realistic_weeks: '18-24',
      conservative_weeks: '26-32',
    });
    expect(res.body.fastest_enterprise_impact_path).toEqual([
      'event_bus',
      'runtime_matrix',
      'workflow_graph',
      'autonomous_ops_queue',
    ]);
  });
});

// ---------------------------------------------------------------------------
// GET /api/operations-platform
// ---------------------------------------------------------------------------

describe('GET /api/operations-platform', () => {
  test('returns 200', async () => {
    const res = await request(app).get('/api/operations-platform');
    expect(res.status).toBe(200);
  });

  test('returns event-driven architecture metadata', async () => {
    const res = await request(app).get('/api/operations-platform');
    expect(res.body).toHaveProperty('architecture_mode', 'event_driven');
    expect(res.body).toHaveProperty('core_flow', 'Event -> Workflow -> Agents -> Memory -> Actions');
    expect(res.body.central_event_bus.recommended_backends).toEqual(['NATS', 'Kafka']);
  });

  test('returns runtime matrix entries for each bot', async () => {
    const res = await request(app).get('/api/operations-platform');
    expect(Array.isArray(res.body.agent_runtime_matrix)).toBe(true);
    expect(res.body.agent_runtime_matrix).toHaveLength(SAMPLE_BOTS.length);
    res.body.agent_runtime_matrix.forEach((entry) => {
      expect(entry).toHaveProperty('bot_id');
      expect(entry).toHaveProperty('workflows_active');
      expect(entry).toHaveProperty('token_burn_today_usd');
    });
  });

  test('returns workflow graph, intelligence layers, and operations queue', async () => {
    const res = await request(app).get('/api/operations-platform');
    expect(res.body.live_workflow_graph).toHaveProperty('mode', 'event_driven');
    expect(Array.isArray(res.body.bot_intelligence_layer)).toBe(true);
    expect(res.body.bot_intelligence_layer).toHaveLength(SAMPLE_BOTS.length);
    expect(Array.isArray(res.body.autonomous_operations_queue)).toBe(true);
    expect(res.body.autonomous_operations_queue.length).toBeGreaterThan(0);
  });

  test('includes pivot timeline and fastest path from command center plan', async () => {
    const res = await request(app).get('/api/operations-platform');
    expect(Array.isArray(res.body.pivot_timeline)).toBe(true);
    expect(res.body.delivery_estimates).toMatchObject({
      aggressive_weeks: '12-14',
      realistic_weeks: '18-24',
      conservative_weeks: '26-32',
    });
    expect(res.body.fastest_enterprise_impact_path).toEqual([
      'event_bus',
      'runtime_matrix',
      'workflow_graph',
      'autonomous_ops_queue',
    ]);
  });
});
