'use strict';

/**
 * DreamCo — Database Connection & Query Helpers
 *
 * Provides a simulated database layer for tests and development.
 * Swap `query()` implementation when connecting to a real PostgreSQL instance.
 */

const path = require('path');
const fs = require('fs');
const crypto = require('crypto');

/** In-memory data store (replaces real DB in tests). */
const store = {
  users: [],
  leads: [],
  deals: [],
  automationLogs: [],
  revenue: [],
  botSchedules: [],
};

/**
 * Get the database connection configuration from environment variables.
 * @returns {{ host: string, port: number, database: string, user: string, ssl: boolean, poolSize: number }}
 */
function getConnection() {
  return {
    host: process.env.DB_HOST || 'localhost',
    port: Number(process.env.DB_PORT) || 5432,
    database: process.env.DB_NAME || 'dreamco',
    user: process.env.DB_USER || 'postgres',
    password: process.env.DB_PASSWORD || '',
    ssl: process.env.DB_SSL === 'true',
    poolSize: Number(process.env.DB_POOL_SIZE) || 10,
    url: process.env.DATABASE_URL || null,
  };
}

/**
 * Execute a parameterized query against the in-memory store (test/dev mode).
 * In production, replace this with a real pg.Pool.query() call.
 * @param {string} sql - SQL statement.
 * @param {Array} [params] - Positional parameters.
 * @returns {Promise<{ rows: Object[], rowCount: number }>}
 */
async function query(sql, params) {
  // Simulate a small network delay
  await new Promise((resolve) => setTimeout(resolve, 1));

  const normalized = sql.trim().toUpperCase();

  if (normalized.startsWith('SELECT')) {
    // Basic table name extraction
    const match = sql.match(/FROM\s+(\w+)/i);
    const table = match ? match[1].toLowerCase() : null;
    const rows = table && store[_tableKey(table)] ? [...store[_tableKey(table)]] : [];
    return { rows, rowCount: rows.length };
  }

  if (normalized.startsWith('INSERT')) {
    const match = sql.match(/INTO\s+(\w+)/i);
    const table = match ? match[1].toLowerCase() : null;
    const key = _tableKey(table);
    if (key && store[key] !== undefined) {
      const row = { id: store[key].length + 1, ...(params ? { _params: params } : {}) };
      store[key].push(row);
      return { rows: [row], rowCount: 1 };
    }
    return { rows: [], rowCount: 0 };
  }

  if (normalized.startsWith('UPDATE') || normalized.startsWith('DELETE')) {
    return { rows: [], rowCount: 1 };
  }

  return { rows: [], rowCount: 0 };
}

/**
 * Run all pending database migrations.
 * @returns {Promise<{ applied: number, migrations: string[] }>}
 */
async function migrateUp() {
  const migrationsDir = path.resolve(__dirname, 'migrations');
  if (!fs.existsSync(migrationsDir)) {
    return { applied: 0, migrations: [] };
  }
  const files = fs
    .readdirSync(migrationsDir)
    .filter((f) => f.endsWith('.sql'))
    .sort();

  return { applied: files.length, migrations: files };
}

/**
 * Seed the in-memory store with demo data.
 * @returns {{ users: number, leads: number }}
 */
function seed() {
  // Seed 5 demo users
  const tiers = ['FREE', 'FREE', 'PRO', 'PRO', 'ENTERPRISE'];
  for (let i = 1; i <= 5; i++) {
    store.users.push({
      id: i,
      email: `demo${i}@dreamco.ai`,
      name: `Demo User ${i}`,
      tier: tiers[i - 1],
      stripe_customer_id: `cus_${crypto.randomBytes(8).toString('hex')}`,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    });
  }

  // Seed 10 demo leads
  const categories = ['real_estate', 'crypto', 'business', 'marketing', 'general'];
  const sources = ['linkedin', 'google', 'zillow', 'indeed', 'organic'];
  for (let i = 1; i <= 10; i++) {
    store.leads.push({
      id: i,
      user_id: ((i - 1) % 5) + 1,
      name: `Lead Person ${i}`,
      email: `lead${i}@example.com`,
      phone: `555-${1000 + i}`,
      source: sources[(i - 1) % sources.length],
      category: categories[(i - 1) % categories.length],
      score: 30 + i * 6,
      status: i <= 3 ? 'sold' : 'new',
      sold_price: i <= 3 ? 50 * i : null,
      created_at: new Date().toISOString(),
    });
  }

  return { users: store.users.length, leads: store.leads.length };
}

/**
 * Return aggregate database statistics.
 * @returns {Promise<{ users: number, leads: number, deals: number, revenue: number }>}
 */
async function getStats() {
  const totalRevenue = store.revenue.reduce((sum, r) => sum + (r.amount || 0), 0);
  return {
    users: store.users.length,
    leads: store.leads.length,
    deals: store.deals.length,
    revenue: Number(totalRevenue.toFixed(2)),
  };
}

/**
 * Map SQL table name to in-memory store key.
 * @param {string} table
 * @returns {string|null}
 */
function _tableKey(table) {
  const map = {
    users: 'users',
    leads: 'leads',
    deals: 'deals',
    automation_logs: 'automationLogs',
    revenue: 'revenue',
    bot_schedules: 'botSchedules',
  };
  return map[table] || null;
}

module.exports = {
  getConnection,
  query,
  migrateUp,
  seed,
  getStats,
};
