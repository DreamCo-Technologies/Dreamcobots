'use strict';

/**
 * DreamCo — Development Environment Configuration
 *
 * Overrides base config for local development:
 * verbose logging, local databases, test API keys.
 */

module.exports = {
  app: {
    port: 3000,
  },
  api: {
    port: 3001,
    rateLimit: {
      windowMs: 15 * 60 * 1000,
      max: 1000, // Relaxed for dev
    },
  },
  database: {
    url: 'postgresql://postgres:postgres@localhost:5432/dreamco_dev',
    name: 'dreamco_dev',
    ssl: false,
  },
  stripe: {
    secretKey: 'sk_test_dreamco_dev',
    publishableKey: 'pk_test_dreamco_dev',
    webhookSecret: 'whsec_test',
  },
  paypal: {
    mode: 'sandbox',
  },
  logging: {
    level: 'DEBUG',
    file: 'logs/app.log',
  },
  cron: {
    enabled: false, // Disable cron by default in dev
  },
};
