'use strict';

/**
 * Tests for DreamCo core infrastructure modules:
 *   - config.js
 *   - botRegistry.js
 *   - database.js
 *   - queue.js
 *   - validateEnv.js
 *   - bootstrap.js
 *   - revenueEngine.js
 */

const path = require('path');
const fs = require('fs');
const os = require('os');

// ---------------------------------------------------------------------------
// config.js
// ---------------------------------------------------------------------------
describe('config', () => {
  test('exposes expected top-level keys', () => {
    const config = require('../DreamCo/core/config');
    expect(config).toHaveProperty('env');
    expect(config).toHaveProperty('port');
    expect(config).toHaveProperty('api');
    expect(config).toHaveProperty('features');
    expect(config).toHaveProperty('revenue');
    expect(config).toHaveProperty('data');
  });

  test('features defaults are all enabled', () => {
    const { features } = require('../DreamCo/core/config');
    expect(features.autoFix).toBe(true);
    expect(features.autoDeploy).toBe(true);
    expect(features.monitoring).toBe(true);
  });

  test('revenue thresholds are positive numbers', () => {
    const { revenue } = require('../DreamCo/core/config');
    expect(revenue.scaleThreshold).toBeGreaterThan(0);
    expect(revenue.maintainThreshold).toBeGreaterThan(0);
    expect(revenue.scaleThreshold).toBeGreaterThan(revenue.maintainThreshold);
  });
});

// ---------------------------------------------------------------------------
// botRegistry.js
// ---------------------------------------------------------------------------
describe('botRegistry', () => {
  const registry = require('../DreamCo/core/botRegistry');

  beforeEach(() => registry.reset());

  test('registers a bot and retrieves it', () => {
    const record = registry.registerBot({ name: 'testBot' });
    expect(record.name).toBe('testBot');
    expect(record.status).toBe('idle');
    expect(record.totalRevenue).toBe(0);
  });

  test('getBots returns all registered bots', () => {
    registry.registerBot({ name: 'botA' });
    registry.registerBot({ name: 'botB' });
    expect(registry.getBots().length).toBe(2);
  });

  test('getBot returns undefined for unknown bot', () => {
    expect(registry.getBot('ghost')).toBeUndefined();
  });

  test('updateStatus changes status and accumulates revenue', () => {
    registry.registerBot({ name: 'moneyBot' });
    registry.updateStatus('moneyBot', 'scaling', 500);
    registry.updateStatus('moneyBot', 'idle', 300);
    const bot = registry.getBot('moneyBot');
    expect(bot.status).toBe('idle');
    expect(bot.totalRevenue).toBe(800);
    expect(bot.runCount).toBe(2);
  });

  test('updateStatus throws for unregistered bot', () => {
    expect(() => registry.updateStatus('ghost', 'idle')).toThrow();
  });

  test('deregisterBot removes entry', () => {
    registry.registerBot({ name: 'tempBot' });
    registry.deregisterBot('tempBot');
    expect(registry.getBot('tempBot')).toBeUndefined();
  });

  test('registerBot throws when name is missing', () => {
    expect(() => registry.registerBot({})).toThrow();
  });

  test('category defaults to general', () => {
    const record = registry.registerBot({ name: 'noCategory' });
    expect(record.category).toBe('general');
  });
});

// ---------------------------------------------------------------------------
// queue.js
// ---------------------------------------------------------------------------
describe('queue', () => {
  const queue = require('../DreamCo/core/queue');

  beforeEach(() => queue.clear());

  test('addJob increases queue size', () => {
    queue.addJob(async () => 1);
    expect(queue.size()).toBe(1);
  });

  test('runQueue executes all jobs and returns results', async () => {
    queue.addJob(async () => 'a');
    queue.addJob(async () => 'b');
    const results = await queue.runQueue();
    expect(results.length).toBe(2);
    expect(results[0].status).toBe('fulfilled');
    expect(results[0].value).toBe('a');
    expect(queue.size()).toBe(0);
  });

  test('runQueue captures rejected jobs without throwing', async () => {
    queue.addJob(async () => {
      throw new Error('boom');
    });
    const results = await queue.runQueue();
    expect(results[0].status).toBe('rejected');
    expect(results[0].reason).toBe('boom');
  });

  test('addJob throws when given a non-function', () => {
    expect(() => queue.addJob('not-a-function')).toThrow();
  });

  test('clear empties the queue', () => {
    queue.addJob(async () => 1);
    queue.clear();
    expect(queue.size()).toBe(0);
  });
});

// ---------------------------------------------------------------------------
// validateEnv.js
// ---------------------------------------------------------------------------
describe('validateEnv', () => {
  const { validateEnv, REQUIRED_VARS } = require('../DreamCo/core/validateEnv');

  test('REQUIRED_VARS is a non-empty array', () => {
    expect(Array.isArray(REQUIRED_VARS)).toBe(true);
    expect(REQUIRED_VARS.length).toBeGreaterThan(0);
  });

  test('throws when ADMIN_KEY is missing', () => {
    const original = process.env.ADMIN_KEY;
    delete process.env.ADMIN_KEY;
    expect(() => validateEnv()).toThrow(/ADMIN_KEY/);
    if (original !== undefined) {
      process.env.ADMIN_KEY = original;
    }
  });

  test('passes when all required vars are set', () => {
    const saved = {};
    for (const key of REQUIRED_VARS) {
      saved[key] = process.env[key];
      process.env[key] = 'test-value';
    }
    expect(() => validateEnv()).not.toThrow();
    for (const key of REQUIRED_VARS) {
      if (saved[key] === undefined) {
        delete process.env[key];
      } else {
        process.env[key] = saved[key];
      }
    }
  });
});

// ---------------------------------------------------------------------------
// bootstrap.js
// ---------------------------------------------------------------------------
describe('bootstrap', () => {
  const { bootstrap } = require('../DreamCo/core/bootstrap');

  test('throws when ADMIN_KEY is missing', () => {
    const original = process.env.ADMIN_KEY;
    delete process.env.ADMIN_KEY;
    expect(() => bootstrap()).toThrow();
    if (original !== undefined) {
      process.env.ADMIN_KEY = original;
    }
  });

  test('succeeds when all required env vars are present', () => {
    const { REQUIRED_VARS } = require('../DreamCo/core/validateEnv');
    const saved = {};
    for (const key of REQUIRED_VARS) {
      saved[key] = process.env[key];
      process.env[key] = 'test-value';
    }
    expect(() => bootstrap()).not.toThrow();
    for (const key of REQUIRED_VARS) {
      if (saved[key] === undefined) {
        delete process.env[key];
      } else {
        process.env[key] = saved[key];
      }
    }
  });
});

// ---------------------------------------------------------------------------
// database.js — use a temp data directory to avoid polluting real data/
// ---------------------------------------------------------------------------
describe('database', () => {
  let tmpDir;
  let db;
  let origDataDir;

  beforeEach(() => {
    origDataDir = process.env.DATA_DIR;
    tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), 'dreamco-test-'));
    process.env.DATA_DIR = tmpDir;
    jest.resetModules();
    db = require('../DreamCo/core/database');
  });

  afterEach(() => {
    jest.resetModules();
    if (origDataDir === undefined) {
      delete process.env.DATA_DIR;
    } else {
      process.env.DATA_DIR = origDataDir;
    }
    fs.rmSync(tmpDir, { recursive: true, force: true });
  });

  test('save persists a document and load retrieves it', () => {
    db.save('bots', { name: 'testBot', revenue: 100 });
    const docs = db.load('bots');
    expect(docs.length).toBe(1);
    expect(docs[0].name).toBe('testBot');
    expect(docs[0].savedAt).toBeDefined();
  });

  test('load returns empty array for non-existent collection', () => {
    expect(db.load('nonexistent')).toEqual([]);
  });

  test('find filters documents', () => {
    db.save('events', { type: 'sale', amount: 50 });
    db.save('events', { type: 'lead', amount: 0 });
    const sales = db.find('events', (d) => d.type === 'sale');
    expect(sales.length).toBe(1);
    expect(sales[0].type).toBe('sale');
  });

  test('count returns correct document count', () => {
    db.save('runs', { bot: 'a' });
    db.save('runs', { bot: 'b' });
    expect(db.count('runs')).toBe(2);
  });
});

// ---------------------------------------------------------------------------
// revenueEngine.js
// ---------------------------------------------------------------------------
describe('revenueEngine', () => {
  let tmpDir;
  let engine;
  let origDataDir;

  beforeEach(() => {
    origDataDir = process.env.DATA_DIR;
    tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), 'dreamco-rev-'));
    process.env.DATA_DIR = tmpDir;
    jest.resetModules();
    engine = require('../DreamCo/core/revenueEngine');
  });

  afterEach(() => {
    jest.resetModules();
    if (origDataDir === undefined) {
      delete process.env.DATA_DIR;
    } else {
      process.env.DATA_DIR = origDataDir;
    }
    fs.rmSync(tmpDir, { recursive: true, force: true });
  });

  test('trackRevenue persists a record', () => {
    const record = engine.trackRevenue('realEstateBot', 250);
    expect(record.source).toBe('realEstateBot');
    expect(record.amount).toBe(250);
  });

  test('totalRevenue sums all revenue', () => {
    engine.trackRevenue('botA', 100);
    engine.trackRevenue('botB', 200);
    expect(engine.totalRevenue()).toBe(300);
  });

  test('totalRevenue filters by source', () => {
    engine.trackRevenue('botA', 100);
    engine.trackRevenue('botB', 200);
    expect(engine.totalRevenue('botA')).toBe(100);
  });

  test('revenueBySource returns breakdown', () => {
    engine.trackRevenue('botA', 100);
    engine.trackRevenue('botA', 50);
    engine.trackRevenue('botB', 200);
    const breakdown = engine.revenueBySource();
    expect(breakdown.botA).toBe(150);
    expect(breakdown.botB).toBe(200);
  });

  test('trackRevenue throws for missing source', () => {
    expect(() => engine.trackRevenue('', 100)).toThrow();
  });

  test('trackRevenue throws for negative amount', () => {
    expect(() => engine.trackRevenue('bot', -1)).toThrow();
  });
});

// ---------------------------------------------------------------------------
// monitoring/errorTracker.js
// ---------------------------------------------------------------------------
describe('errorTracker', () => {
  const tracker = require('../DreamCo/monitoring/errorTracker');

  beforeEach(() => tracker.clearErrors());

  test('trackError stores an error entry', () => {
    tracker.trackError(new Error('oops'), 'testBot');
    expect(tracker.errorCount()).toBe(1);
  });

  test('getErrors returns newest first', () => {
    tracker.trackError(new Error('first'));
    tracker.trackError(new Error('second'));
    const errors = tracker.getErrors();
    expect(errors[0].message).toBe('second');
  });

  test('errorCount filters by context', () => {
    tracker.trackError(new Error('e1'), 'botA');
    tracker.trackError(new Error('e2'), 'botB');
    expect(tracker.errorCount('botA')).toBe(1);
    expect(tracker.errorCount('botB')).toBe(1);
  });

  test('trackError accepts plain strings', () => {
    const entry = tracker.trackError('something went wrong');
    expect(entry.message).toBe('something went wrong');
  });

  test('clearErrors empties the store', () => {
    tracker.trackError(new Error('e'));
    tracker.clearErrors();
    expect(tracker.errorCount()).toBe(0);
  });
});

// ---------------------------------------------------------------------------
// api/auth.js
// ---------------------------------------------------------------------------
describe('auth', () => {
  let auth;
  let origApiKeys;

  beforeEach(() => {
    origApiKeys = process.env.DREAMCO_API_KEYS;
    process.env.DREAMCO_API_KEYS = 'valid-key-123';
    jest.resetModules();
    auth = require('../DreamCo/api/auth');
  });

  afterEach(() => {
    jest.resetModules();
    if (origApiKeys === undefined) {
      delete process.env.DREAMCO_API_KEYS;
    } else {
      process.env.DREAMCO_API_KEYS = origApiKeys;
    }
  });

  test('VALID_KEYS contains configured keys', () => {
    expect(auth.VALID_KEYS.has('valid-key-123')).toBe(true);
  });

  test('authenticate calls next() for a valid key', () => {
    const req = { headers: { 'x-api-key': 'valid-key-123' } };
    const res = { writeHead: jest.fn(), end: jest.fn() };
    const next = jest.fn();
    auth.authenticate(req, res, next);
    expect(next).toHaveBeenCalled();
  });

  test('authenticate returns 401 for missing key', () => {
    const req = { headers: {} };
    const res = { writeHead: jest.fn(), end: jest.fn() };
    const next = jest.fn();
    auth.authenticate(req, res, next);
    expect(res.writeHead).toHaveBeenCalledWith(401, expect.any(Object));
    expect(next).not.toHaveBeenCalled();
  });

  test('authenticate returns 401 for invalid key', () => {
    const req = { headers: { 'x-api-key': 'wrong-key' } };
    const res = { writeHead: jest.fn(), end: jest.fn() };
    const next = jest.fn();
    auth.authenticate(req, res, next);
    expect(res.writeHead).toHaveBeenCalledWith(401, expect.any(Object));
  });
});

// ---------------------------------------------------------------------------
// orchestrator/runAllBots.js — collectBotFiles helper
// ---------------------------------------------------------------------------
describe('runAllBots - collectBotFiles', () => {
  const { collectBotFiles } = require('../DreamCo/orchestrator/runAllBots');

  test('returns empty array for nonexistent directory', () => {
    expect(collectBotFiles('/tmp/no-such-dir-xyz')).toEqual([]);
  });

  test('collects .js files recursively', () => {
    const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), 'bots-'));
    const subDir = path.join(tmpDir, 'sub');
    fs.mkdirSync(subDir);
    fs.writeFileSync(path.join(tmpDir, 'bot1.js'), 'module.exports = {  run: async () => ({})  };');
    fs.writeFileSync(path.join(subDir, 'bot2.js'), 'module.exports = {  run: async () => ({})  };');
    fs.writeFileSync(path.join(tmpDir, 'index.js'), '// index — should be skipped');

    const files = collectBotFiles(tmpDir);
    // index.js is excluded; bot1.js and bot2.js are included
    expect(files.some((f) => f.endsWith('bot1.js'))).toBe(true);
    expect(files.some((f) => f.endsWith('bot2.js'))).toBe(true);
    expect(files.every((f) => !f.endsWith('index.js'))).toBe(true);

    fs.rmSync(tmpDir, { recursive: true, force: true });
  });
});
