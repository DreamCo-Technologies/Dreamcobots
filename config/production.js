'use strict';

/**
 * DreamCo — Production Environment Configuration
 *
 * Strict security settings, real API keys from environment,
 * rate limiting, and production database URLs.
 */

module.exports = {
  app: {
    port: Number(process.env.PORT) || 8080,
  },
  api: {
    port: Number(process.env.API_PORT) || 8081,
    rateLimit: {
      windowMs: 15 * 60 * 1000,
      max: 100,
    },
  },
  database: {
    url: process.env.DATABASE_URL,
    ssl: true,
    poolSize: Number(process.env.DB_POOL_SIZE) || 20,
  },
  stripe: {
    secretKey: process.env.STRIPE_SECRET_KEY,
    publishableKey: process.env.STRIPE_PUBLISHABLE_KEY,
    webhookSecret: process.env.STRIPE_WEBHOOK_SECRET,
  },
  paypal: {
    clientId: process.env.PAYPAL_CLIENT_ID,
    clientSecret: process.env.PAYPAL_CLIENT_SECRET,
    mode: 'live',
  },
  logging: {
    level: 'WARN',
    file: 'logs/app.log',
  },
  cron: {
    enabled: true,
  },
  features: {
    autoFix: false, // Disable automated fixes in production
    autoDeploy: false, // Require manual deploy approvals
    monitoring: true,
  },
};
