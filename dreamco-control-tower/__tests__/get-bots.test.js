import request from 'supertest';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Set test environment before importing server
process.env.NODE_ENV = 'test';

const BOTS_FILE = path.join(__dirname, '..', 'config', 'bots.json');

const SAMPLE_BOTS = [
  {
    name: 'TestBot',
    repoName: 'test-bot',
    repoPath: './bots/test_bot',
    status: 'active',
    tier: 'PRO',
    lastHeartbeat: null,
    lastUpdate: null,
    pendingPRs: 0,
    description: 'A test bot',
  },
  {
    name: 'IdleBot',
    repoName: 'idle-bot',
    repoPath: './bots/idle_bot',
    status: 'idle',
    tier: 'FREE',
    lastHeartbeat: '2026-01-01T00:00:00.000Z',
    lastUpdate: null,
    pendingPRs: 2,
    description: 'An idle bot',
  },
];

let app;
let originalBotsContent;

beforeAll(async () => {
  // Backup the original bots.json content
  originalBotsContent = fs.readFileSync(BOTS_FILE, 'utf8');

  // Import app — server uses ESM
  const module = await import('../backend/server.js');
  app = module.default;
});

afterAll(() => {
  // Restore original bots.json
  fs.writeFileSync(BOTS_FILE, originalBotsContent);
});

// ---------------------------------------------------------------------------
// GET /api/get-bots
// ---------------------------------------------------------------------------

describe('GET /api/get-bots', () => {
  describe('with valid bots.json', () => {
    beforeEach(() => {
      fs.writeFileSync(BOTS_FILE, JSON.stringify(SAMPLE_BOTS, null, 2));
    });

    test('returns 200 status', async () => {
      const res = await request(app).get('/api/get-bots');
      expect(res.status).toBe(200);
    });

    test('returns success: true', async () => {
      const res = await request(app).get('/api/get-bots');
      expect(res.body.success).toBe(true);
    });

    test('returns bots array', async () => {
      const res = await request(app).get('/api/get-bots');
      expect(Array.isArray(res.body.bots)).toBe(true);
    });

    test('returns correct bot count', async () => {
      const res = await request(app).get('/api/get-bots');
      expect(res.body.count).toBe(SAMPLE_BOTS.length);
    });

    test('bots array length matches count field', async () => {
      const res = await request(app).get('/api/get-bots');
      expect(res.body.bots.length).toBe(res.body.count);
    });

    test('returns all expected bot names', async () => {
      const res = await request(app).get('/api/get-bots');
      const names = res.body.bots.map((b) => b.name);
      expect(names).toContain('TestBot');
      expect(names).toContain('IdleBot');
    });

    test('includes bot status field', async () => {
      const res = await request(app).get('/api/get-bots');
      res.body.bots.forEach((bot) => {
        expect(bot).toHaveProperty('status');
      });
    });

    test('includes bot tier field', async () => {
      const res = await request(app).get('/api/get-bots');
      res.body.bots.forEach((bot) => {
        expect(bot).toHaveProperty('tier');
      });
    });

    test('includes pendingPRs field', async () => {
      const res = await request(app).get('/api/get-bots');
      res.body.bots.forEach((bot) => {
        expect(bot).toHaveProperty('pendingPRs');
      });
    });

    test('includes lastHeartbeat field', async () => {
      const res = await request(app).get('/api/get-bots');
      res.body.bots.forEach((bot) => {
        expect(bot).toHaveProperty('lastHeartbeat');
      });
    });

    test('includes lastUpdate field', async () => {
      const res = await request(app).get('/api/get-bots');
      res.body.bots.forEach((bot) => {
        expect(bot).toHaveProperty('lastUpdate');
      });
    });

    test('includes timestamp in response', async () => {
      const res = await request(app).get('/api/get-bots');
      expect(res.body).toHaveProperty('timestamp');
      expect(typeof res.body.timestamp).toBe('string');
    });

    test('timestamp is a valid ISO date', async () => {
      const res = await request(app).get('/api/get-bots');
      expect(() => new Date(res.body.timestamp)).not.toThrow();
      expect(new Date(res.body.timestamp).toISOString()).toBe(res.body.timestamp);
    });

    test('returns content-type application/json', async () => {
      const res = await request(app).get('/api/get-bots');
      expect(res.headers['content-type']).toMatch(/application\/json/);
    });

    test('re-reads file on each request (data freshness)', async () => {
      // First request: SAMPLE_BOTS
      const res1 = await request(app).get('/api/get-bots');
      expect(res1.body.count).toBe(2);

      // Update file with a single bot
      const updatedBots = [SAMPLE_BOTS[0]];
      fs.writeFileSync(BOTS_FILE, JSON.stringify(updatedBots, null, 2));

      // Second request must reflect the updated file
      const res2 = await request(app).get('/api/get-bots');
      expect(res2.body.count).toBe(1);
    });

    test('reflects bot status correctly', async () => {
      const res = await request(app).get('/api/get-bots');
      const testBot = res.body.bots.find((b) => b.name === 'TestBot');
      expect(testBot.status).toBe('active');
      const idleBot = res.body.bots.find((b) => b.name === 'IdleBot');
      expect(idleBot.status).toBe('idle');
    });

    test('reflects lastHeartbeat value', async () => {
      const res = await request(app).get('/api/get-bots');
      const idleBot = res.body.bots.find((b) => b.name === 'IdleBot');
      expect(idleBot.lastHeartbeat).toBe('2026-01-01T00:00:00.000Z');
    });

    test('handles empty bots array', async () => {
      fs.writeFileSync(BOTS_FILE, JSON.stringify([], null, 2));
      const res = await request(app).get('/api/get-bots');
      expect(res.status).toBe(200);
      expect(res.body.success).toBe(true);
      expect(res.body.count).toBe(0);
      expect(res.body.bots).toEqual([]);
    });
  });

  describe('with missing bots.json', () => {
    let tempBotsFile;

    beforeEach(() => {
      // Temporarily rename the file
      tempBotsFile = BOTS_FILE + '.bak';
      fs.renameSync(BOTS_FILE, tempBotsFile);
    });

    afterEach(() => {
      // Restore the file
      if (fs.existsSync(tempBotsFile)) {
        fs.renameSync(tempBotsFile, BOTS_FILE);
      }
    });

    test('returns 503 when bots.json is missing', async () => {
      const res = await request(app).get('/api/get-bots');
      expect(res.status).toBe(503);
    });

    test('returns success: false when bots.json is missing', async () => {
      const res = await request(app).get('/api/get-bots');
      expect(res.body.success).toBe(false);
    });

    test('returns descriptive error when bots.json is missing', async () => {
      const res = await request(app).get('/api/get-bots');
      expect(typeof res.body.error).toBe('string');
      expect(res.body.error.length).toBeGreaterThan(0);
    });
  });

  describe('with malformed bots.json', () => {
    beforeEach(() => {
      fs.writeFileSync(BOTS_FILE, '{ this is not valid JSON ]]]');
    });

    test('returns 500 when bots.json is malformed', async () => {
      const res = await request(app).get('/api/get-bots');
      expect(res.status).toBe(500);
    });

    test('returns success: false when bots.json is malformed', async () => {
      const res = await request(app).get('/api/get-bots');
      expect(res.body.success).toBe(false);
    });

    test('returns descriptive error when bots.json is malformed', async () => {
      const res = await request(app).get('/api/get-bots');
      expect(typeof res.body.error).toBe('string');
      expect(res.body.error.length).toBeGreaterThan(0);
    });
  });
});

// ---------------------------------------------------------------------------
// POST /api/bot-heartbeat
// ---------------------------------------------------------------------------

describe('POST /api/bot-heartbeat', () => {
  beforeEach(() => {
    fs.writeFileSync(BOTS_FILE, JSON.stringify(SAMPLE_BOTS, null, 2));
  });

  test('returns 200 for a valid bot', async () => {
    const res = await request(app).post('/api/bot-heartbeat').send({ botName: 'TestBot' });
    expect(res.status).toBe(200);
  });

  test('updates lastHeartbeat in bots.json', async () => {
    await request(app).post('/api/bot-heartbeat').send({ botName: 'TestBot' });
    const bots = JSON.parse(fs.readFileSync(BOTS_FILE, 'utf8'));
    const bot = bots.find((b) => b.name === 'TestBot');
    expect(bot.lastHeartbeat).not.toBeNull();
  });

  test('returns status updated', async () => {
    const res = await request(app).post('/api/bot-heartbeat').send({ botName: 'TestBot' });
    expect(res.body.status).toBe('updated');
  });

  test('returns 404 for unknown bot', async () => {
    const res = await request(app).post('/api/bot-heartbeat').send({ botName: 'UnknownBot' });
    expect(res.status).toBe(404);
  });

  test('returns 400 when botName is missing', async () => {
    const res = await request(app).post('/api/bot-heartbeat').send({});
    expect(res.status).toBe(400);
  });
});
