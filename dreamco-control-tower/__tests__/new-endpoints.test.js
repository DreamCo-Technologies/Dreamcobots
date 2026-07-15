import request from 'supertest';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

process.env.NODE_ENV = 'test';

const BOTS_FILE = path.join(__dirname, '..', 'config', 'bots.json');
const BUDDY_OPS_QUEUE_FILE = path.join(__dirname, '..', '..', 'reports', 'buddy_ops_queue.json');

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
let originalBuddyOpsQueueContent;

beforeAll(async () => {
  originalBotsContent = fs.readFileSync(BOTS_FILE, 'utf8');
  originalBuddyOpsQueueContent = fs.existsSync(BUDDY_OPS_QUEUE_FILE)
    ? fs.readFileSync(BUDDY_OPS_QUEUE_FILE, 'utf8')
    : null;
  const module = await import('../backend/server.js');
  app = module.default;
});

afterAll(() => {
  fs.writeFileSync(BOTS_FILE, originalBotsContent);
  if (originalBuddyOpsQueueContent === null) {
    if (fs.existsSync(BUDDY_OPS_QUEUE_FILE)) {
      fs.unlinkSync(BUDDY_OPS_QUEUE_FILE);
    }
  } else {
    fs.writeFileSync(BUDDY_OPS_QUEUE_FILE, originalBuddyOpsQueueContent);
  }
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

  test('scraping_active matches current date against deadline', async () => {
    const res = await request(app).get('/api/orchestrator');
    const expected = new Date() <= new Date(res.body.scrape_deadline);
    expect(res.body.scraping_active).toBe(expected);
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

describe('GET /api/system-libraries', () => {
  test('returns complete per-bot library coverage', async () => {
    const res = await request(app).get('/api/system-libraries');

    expect(res.status).toBe(200);
    expect(res.body.bot_count).toBeGreaterThanOrEqual(1248);
    expect(res.body.builders).toHaveLength(8);
    expect(res.body.libraries).toHaveLength(7);
    Object.values(res.body.coverage).forEach((count) => expect(count).toBe(res.body.bot_count));
    expect(res.body.libraries.some((library) => library.id === 'resources')).toBe(true);
    expect(res.body.coverage.bots_with_api_sandbox_bootcamps).toBe(res.body.bot_count);
    expect(res.body.coverage.bots_with_custom_api_contracts).toBe(res.body.bot_count);
    expect(res.body.coverage.bots_with_sandbox_workflow_generators).toBe(res.body.bot_count);
    expect(res.body.coverage.bots_with_owner_buddy_client_bootcamp_tracks).toBe(res.body.bot_count);
    expect(res.body.bootcamp_baseline.top_ai_company_resource_seed_count).toBe(100);
  });

  test('returns the security baseline', async () => {
    const res = await request(app).get('/api/system-libraries');

    expect(res.body.security_baseline.webhooks).toContain('hmac_sha256');
    expect(res.body.security_baseline.apis).toContain('rate_limit_backoff');
    expect(res.body.security_baseline.github_actions).toContain(
      'least_privilege_permissions',
    );
  });
});

describe('GET /api/buddy-capabilities', () => {
  test('returns generated Buddy capability inventory', async () => {
    const res = await request(app).get('/api/buddy-capabilities');

    expect(res.status).toBe(200);
    expect(res.body.schema).toBe('dreamco.buddy_capability_inventory.v1');
    expect(res.body.summary.bot_profiles_scanned).toBeGreaterThanOrEqual(1248);
    expect(res.body.summary.buddy_related_bots).toBeGreaterThanOrEqual(10);
    expect(res.body.summary.test_states.ready_for_test_run).toBeGreaterThan(0);
    expect(res.body.summary.bots_with_full_coding_path).toBe(res.body.summary.bot_profiles_scanned);
    expect(res.body.summary.all_bots_have_full_coding_path).toBe(true);
    expect(res.body.summary.production_ready_bots).toBeGreaterThan(0);
    expect(res.body.summary.all_bots_production_ready).toBe(false);
  });

  test('returns attention list and direct Buddy systems', async () => {
    const res = await request(app).get('/api/buddy-capabilities');

    expect(Array.isArray(res.body.buddy_bots)).toBe(true);
    expect(res.body.buddy_bots.some((bot) => bot.slug === 'buddy_core')).toBe(true);
    expect(Array.isArray(res.body.attention.needs_implementation)).toBe(true);
    expect(Array.isArray(res.body.attention.needs_direct_test_coverage)).toBe(true);
    expect(Array.isArray(res.body.attention.needs_existing_system_mapping)).toBe(true);
  });
});

describe('GET /api/buddy-productivity', () => {
  test('returns productivity tracking for owner, clients, and bots', async () => {
    const res = await request(app).get('/api/buddy-productivity');

    expect(res.status).toBe(200);
    expect(res.body.schema).toBe('dreamco.buddy_productivity_tracker.v1');
    expect(res.body.summary).toHaveProperty('productivity_score');
    expect(res.body.summary.bot_count).toBeGreaterThanOrEqual(1248);
    expect(res.body.owner_productivity.tracks).toContain('next best build task');
    expect(res.body.client_productivity.tracks).toContain('demo-ready bots');
    expect(res.body.bot_productivity.tracks).toContain('runtime readiness');
    expect(Array.isArray(res.body.learning_loops)).toBe(true);
  });
});

describe('GET /api/release-readiness', () => {
  test('returns DreamCo 1.0 plan versus proof comparison', async () => {
    const res = await request(app).get('/api/release-readiness');

    expect(res.status).toBe(200);
    expect(res.body.schema).toBe('dreamco.release_readiness.v1');
    expect(res.body.summary).toHaveProperty('release_readiness_score');
    expect(res.body.summary).toHaveProperty('first_ten_complete');
    expect(Array.isArray(res.body.first_ten_updates)).toBe(true);
    expect(Array.isArray(res.body.top_100_groups)).toBe(true);
    expect(res.body.sources).toHaveProperty('repository_stewardship');
  });
});

describe('GET /api/app-foundry', () => {
  test('returns in-house build, host, and deploy readiness', async () => {
    const res = await request(app).get('/api/app-foundry');

    expect(res.status).toBe(200);
    expect(res.body.schema).toBe('dreamco.app_foundry_readiness.v1');
    expect(res.body.summary.creation_lanes).toBeGreaterThanOrEqual(8);
    expect(res.body.summary.deployment_targets).toBeGreaterThanOrEqual(4);
    expect(res.body.ownership_rule).toMatch(/source of truth/i);
    expect(res.body.lanes.map((lane) => lane.id)).toEqual(
      expect.arrayContaining(['games', 'websites', 'apps', 'school_courses', 'simulations']),
    );
    expect(res.body.deployment_targets.map((target) => target.id)).toContain('github_pages');
    expect(res.body.quality_gates).toContain('owner_approval_before_live_money_outreach_or_deploy');
  });
});

describe('GET /api/github-triage', () => {
  test('returns generated GitHub triage report', async () => {
    const res = await request(app).get('/api/github-triage');

    expect(res.status).toBe(200);
    expect(res.body.schema).toBe('dreamco.github_triage.v1');
    expect(res.body.repo).toBe('DreamCo-Technologies/Dreamcobots');
    expect(res.body.summary).toHaveProperty('open_prs');
    expect(res.body.summary).toHaveProperty('open_issues');
    expect(res.body.summary).toHaveProperty('issue_comments_scanned');
    expect(res.body.summary).toHaveProperty('pr_review_comments_scanned');
    expect(res.body.summary).toHaveProperty('failed_workflow_runs');
    expect(Array.isArray(res.body.pr_restart_queue)).toBe(true);
    expect(Array.isArray(res.body.failed_workflow_runs)).toBe(true);
  });
});

describe('GET /api/repository-stewardship', () => {
  test('returns cleanroom status and quality gates', async () => {
    const res = await request(app).get('/api/repository-stewardship');

    expect(res.status).toBe(200);
    expect(res.body.schema).toBe('dreamco.repository_steward.v1');
    expect(res.body.summary).toHaveProperty('cleanroom_ready');
    expect(res.body.summary.failed_quality_checks).toBe(0);
    expect(res.body.quality_checks.map((check) => check.name)).toEqual(
      expect.arrayContaining(['json_parse', 'python_syntax', 'javascript_syntax']),
    );
    expect(res.body.policy.auto_close_without_owner_approval).toBe(false);
  });
});

describe('GET /api/storage-guard', () => {
  test('returns storage budgets and sharding health', async () => {
    const res = await request(app).get('/api/storage-guard');

    expect(res.status).toBe(200);
    expect(res.body.schema).toBe('dreamco.storage_guard.v1');
    expect(res.body.summary).toHaveProperty('storage_ready', true);
    expect(res.body.summary.failed_checks).toBe(0);
    expect(res.body.summary.resource_shard_count).toBeGreaterThanOrEqual(45);
    expect(res.body.budgets).toHaveProperty('generated_resource_shard_max_mb');
    expect(res.body.checks.map((check) => check.name)).toContain('resource_sharding_integrity');
  });
});

describe('GET /api/stripe-revenue-rescue', () => {
  test('returns Stripe no-money diagnosis and priority fixes', async () => {
    const res = await request(app).get('/api/stripe-revenue-rescue');

    expect(res.status).toBe(200);
    expect(res.body.schema).toBe('dreamco.stripe_revenue_rescue.v1');
    expect(res.body.summary).toHaveProperty('checkout_ready_offers');
    expect(res.body.summary).toHaveProperty('tracked_events');
    expect(Array.isArray(res.body.revenue_blockers)).toBe(true);
    expect(Array.isArray(res.body.priority_fixes)).toBe(true);
    expect(res.body.safety_note).toMatch(/never prints secret values/i);
  });
});

describe('GET /api/production-approval-packets', () => {
  test('returns high-risk production approval packets', async () => {
    const res = await request(app).get('/api/production-approval-packets');

    expect(res.status).toBe(200);
    expect(res.body.schema).toBe('dreamco.production_approval_packets.v1');
    expect(res.body.summary.approval_packets).toBeGreaterThan(0);
    expect(res.body.summary.smoke_tests_failed).toBe(0);
    expect(res.body.required_buddy_money_request).toContain('Buddy, help me make money');
    expect(Array.isArray(res.body.packets)).toBe(true);
  });
});

describe('GET /api/buddy-bot-connections', () => {
  test('returns all-bot Buddy routing, test, and resource coverage', async () => {
    const res = await request(app).get('/api/buddy-bot-connections');

    expect(res.status).toBe(200);
    expect(res.body.schema).toBe('dreamco.buddy_bot_connection_guard.v1');
    expect(res.body.summary.bot_count).toBeGreaterThanOrEqual(1248);
    expect(res.body.summary.all_bots_connected_to_buddy).toBe(true);
    expect(res.body.summary.all_bots_testable_from_actions_page).toBe(true);
    expect(res.body.summary.all_bots_have_custom_resources).toBe(true);
    expect(res.body.summary.failed_bots).toBe(0);
  });
});

describe('Buddy operation prompt API', () => {
  test('returns the supervised operation queue', async () => {
    const res = await request(app).get('/api/buddy-ops');

    expect(res.status).toBe(200);
    expect(res.body.schema).toBe('dreamco.buddy_ops_queue.v1');
    expect(Array.isArray(res.body.operations)).toBe(true);
  });

  test('creates a governed operation packet from an Actions page prompt', async () => {
    const res = await request(app)
      .post('/api/buddy-ops/prompt')
      .send({ prompt: 'Fix Stripe checkout and make sure I get GitHub notifications for payments' });

    expect(res.status).toBe(201);
    expect(res.body.packet.schema).toBe('dreamco.buddy_operation_packet.v1');
    expect(res.body.packet.operation_type).toBe('revenue_operation');
    expect(res.body.packet.mode).toBe('sandbox_first_pull_request_review');
    expect(res.body.packet.approval_gates).toContain('owner approval before money movement');
    expect(res.body.packet.blocked_live_actions).toContain('payments or payouts');
  });

  test('routes image, game, and simulation prompts to the AI creation studio', async () => {
    const res = await request(app)
      .post('/api/buddy-ops/prompt')
      .send({ prompt: 'Build a Photoshop style product mockup, video game prototype, and business simulation' });

    expect(res.status).toBe(201);
    expect(res.body.packet.operation_type).toBe('vibe_studio_operation');
    expect(res.body.packet.builder).toBe('Buddy AI Creation Studio Builder');
    expect(res.body.packet.recommended_tests).toContain('rights review checklist');
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

  // ---------------------------------------------------------------------------
  // GET /api/production-media-roadmap
  // ---------------------------------------------------------------------------

  describe('GET /api/production-media-roadmap', () => {
    test('returns 200', async () => {
      const res = await request(app).get('/api/production-media-roadmap');
      expect(res.status).toBe(200);
    });

    test('returns roadmap metadata', async () => {
      const res = await request(app).get('/api/production-media-roadmap');
      expect(res.body).toHaveProperty('program', 'Buddy Production Media Roadmap');
      expect(res.body).toHaveProperty('estimated_total');
      expect(res.body.estimated_total).toHaveProperty('strong_mvp', '2-3 months');
    });

    test('returns six phases with computed order and duration days', async () => {
      const res = await request(app).get('/api/production-media-roadmap');
      expect(Array.isArray(res.body.phases)).toBe(true);
      expect(res.body.phases).toHaveLength(6);
      expect(res.body.phases[0]).toHaveProperty('order', 1);
      expect(res.body.phases[0]).toHaveProperty('duration_days');
      expect(res.body.phases[0].duration_days).toEqual({ minDays: 14, maxDays: 28 });
    });

    test('returns computed totals', async () => {
      const res = await request(app).get('/api/production-media-roadmap');
      expect(res.body).toHaveProperty('computed');
      expect(res.body.computed).toHaveProperty('phase_count', 6);
      expect(res.body.computed).toHaveProperty('total_duration_days');
      expect(res.body.computed.total_duration_days).toEqual({ minDays: 274, maxDays: 520 });
      expect(res.body.computed.total_duration_months).toEqual({ minMonths: 9.1, maxMonths: 17.3 });
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
});
