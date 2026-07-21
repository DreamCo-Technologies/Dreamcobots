'use strict';

/**
 * DreamCo — Startup Bootstrap
 *
 * Runs all pre-flight checks before any bot or server starts.
 * Import and call bootstrap() as the very first thing in your entry point.
 */

const { validateEnv } = require('./validateEnv');

/**
 * Run the full startup sequence.
 * Throws if any critical check fails (environment, config, etc.).
 */
function bootstrap() {
  console.log('⚙️  Bootstrapping DreamCo system...');

  validateEnv();
  console.log('✅ Environment validated');

  console.log('✅ Bootstrap complete — system ready');
}

module.exports = { bootstrap };
