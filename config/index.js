'use strict';

/**
 * DreamCo — Master Configuration Loader
 *
 * Merges base configuration with environment-specific overrides.
 * All values are frozen to prevent accidental mutation at runtime.
 */

require('dotenv').config();

const env = process.env.NODE_ENV || 'development';

let envConfig = {};
try {
  envConfig = require(`./${env}`);
} catch (_err) {
  // Fall back to empty overrides if environment file doesn't exist
  envConfig = {};
}

/** Base configuration shared across all environments. */
const base = {
  env,

  app: {
    name: 'DreamCo Money OS',
    version: '1.0.0',
    port: Number(process.env.PORT) || 3000,
    host: process.env.HOST || '0.0.0.0',
  },

  api: {
    port: Number(process.env.API_PORT) || 3001,
    prefix: '/api',
    rateLimit: {
      windowMs: 15 * 60 * 1000,
      max: 100,
    },
    keys: (process.env.DREAMCO_API_KEYS || '')
      .split(',')
      .map((k) => k.trim())
      .filter(Boolean),
  },

  database: {
    url: process.env.DATABASE_URL || 'postgresql://user:password@localhost:5432/dreamco',
    host: process.env.DB_HOST || 'localhost',
    port: Number(process.env.DB_PORT) || 5432,
    name: process.env.DB_NAME || 'dreamco',
    user: process.env.DB_USER || 'postgres',
    password: process.env.DB_PASSWORD || '',
    poolSize: Number(process.env.DB_POOL_SIZE) || 10,
    ssl: process.env.DB_SSL === 'true',
  },

  redis: {
    url: process.env.REDIS_URL || 'redis://localhost:6379/0',
  },

  stripe: {
    secretKey: process.env.STRIPE_SECRET_KEY || '',
    publishableKey: process.env.STRIPE_PUBLISHABLE_KEY || '',
    webhookSecret: process.env.STRIPE_WEBHOOK_SECRET || '',
  },

  paypal: {
    clientId: process.env.PAYPAL_CLIENT_ID || '',
    clientSecret: process.env.PAYPAL_CLIENT_SECRET || '',
    mode: process.env.PAYPAL_MODE || 'sandbox',
  },

  openai: {
    apiKey: process.env.OPENAI_API_KEY || '',
    model: process.env.OPENAI_MODEL || 'gpt-4o-mini',
  },

  email: {
    host: process.env.SMTP_HOST || 'smtp.gmail.com',
    port: Number(process.env.SMTP_PORT) || 587,
    user: process.env.SMTP_USER || '',
    pass: process.env.SMTP_PASS || '',
    from: process.env.EMAIL_FROM || 'noreply@dreamco.ai',
  },

  bots: {
    defaultTier: 'FREE',
    maxConcurrent: 5,
    timeoutMs: 300000,
  },

  cron: {
    enabled: process.env.CRON_ENABLED !== 'false',
    botRunIntervalMs: Number(process.env.BOT_RUN_INTERVAL_MS) || 3600000,
    leadScrapeIntervalMs: Number(process.env.LEAD_SCRAPE_INTERVAL_MS) || 21600000,
    emailSendIntervalMs: Number(process.env.EMAIL_SEND_INTERVAL_MS) || 86400000,
  },

  logging: {
    level: process.env.LOG_LEVEL || 'INFO',
    file: 'logs/app.log',
    maxFileSizeMb: 10,
  },

  features: {
    autoFix: process.env.FEATURE_AUTO_FIX !== 'false',
    autoDeploy: process.env.FEATURE_AUTO_DEPLOY !== 'false',
    monitoring: process.env.FEATURE_MONITORING !== 'false',
  },

  revenue: {
    scaleThreshold: Number(process.env.REVENUE_SCALE_THRESHOLD) || 1000,
    maintainThreshold: Number(process.env.REVENUE_MAINTAIN_THRESHOLD) || 100,
  },

  data: {
    dir: process.env.DATA_DIR || './data',
  },
};

module.exports = Object.freeze({ ...base, ...envConfig });
