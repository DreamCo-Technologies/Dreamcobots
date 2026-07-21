'use strict';

/**
 * DreamCo — Fix Engine
 *
 * Runs linting and formatting fixes across the codebase so the system
 * can heal itself before each deployment or bot cycle.
 */

const { execSync } = require('child_process');
const path = require('path');

const REPO_ROOT = path.resolve(__dirname, '..', '..');

/**
 * Attempt to run a shell command, catching and logging failures gracefully.
 *
 * @param {string} cmd - Shell command to execute
 * @param {string} label - Human-readable label for logging
 */
function _safeExec(cmd, label) {
  try {
    execSync(cmd, { cwd: REPO_ROOT, stdio: 'inherit' });
    console.log(`✅ ${label} complete`);
  } catch (err) {
    console.error(`⚠️  ${label} reported issues: ${err.message}`);
    // Non-fatal — we log and continue rather than crashing the system
  }
}

/**
 * Run the full fix pipeline: lint auto-fix → format fix.
 * Errors are caught and logged; the system keeps running.
 */
function fixEverything() {
  console.log('🔧 Running DreamCo global fix engine...');

  _safeExec('npm run lint:fix --if-present', 'ESLint auto-fix');
  _safeExec('npm run format:fix --if-present', 'Prettier format');

  console.log('✅ Fix engine finished — codebase healed');
}

module.exports = { fixEverything };
