'use strict';

/**
 * DreamCo — Central Configuration System
 *
 * Single source of truth for all runtime settings.  Reads values from
 * environment variables (populated via .env) and exposes them as a
 * frozen config object so no other module can accidentally mutate them.
 */

require('dotenv').config();

const config = Object.freeze({
  env: process.env.NODE_ENV || 'development',
  port: Number(process.env.PORT) || 3000,

  api: {
    port: Number(process.env.API_PORT) || 3001,
    keys: (process.env.DREAMCO_API_KEYS || '')
      .split(',')
      .map((k) => k.trim())
      .filter(Boolean),
  },

  dashboard: {
    port: Number(process.env.DASHBOARD_PORT) || 5001,
  },

  features: Object.freeze({
    autoFix: process.env.FEATURE_AUTO_FIX !== 'false',
    autoDeploy: process.env.FEATURE_AUTO_DEPLOY !== 'false',
    monitoring: process.env.FEATURE_MONITORING !== 'false',
  }),

  revenue: Object.freeze({
    scaleThreshold: Number(process.env.REVENUE_SCALE_THRESHOLD) || 1000,
    maintainThreshold: Number(process.env.REVENUE_MAINTAIN_THRESHOLD) || 100,
  }),

  data: Object.freeze({
    dir: process.env.DATA_DIR || 'data',
  }),
});

module.exports = config;
