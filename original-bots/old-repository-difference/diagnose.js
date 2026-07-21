'use strict';

/**
 * diagnose.js — Quick system diagnostic.
 *
 * Checks environment variables, bot registry, and error history
 * so developers can spot problems without reading raw logs.
 *
 * Run:  node diagnose.js
 */

const { REQUIRED_VARS } = require('./DreamCo/core/validateEnv');
const registry = require('./DreamCo/core/botRegistry');
const { getErrors } = require('./DreamCo/monitoring/errorTracker');

console.log('\n🔍 DreamCo System Diagnostic\n');

// --- Environment check ---
console.log('📋 Environment:');
for (const key of REQUIRED_VARS) {
  const present = !!process.env[key];
  console.log(`  ${present ? '✅' : '❌'} ${key}: ${present ? 'set' : 'MISSING'}`);
}

// --- Bot registry ---
const bots = registry.getBots();
console.log(`\n🤖 Registered bots: ${bots.length}`);
for (const bot of bots) {
  console.log(
    `  • ${bot.name} [${bot.status}] — runs: ${bot.runCount}, revenue: $${bot.totalRevenue}`
  );
}

// --- Recent errors ---
const errors = getErrors().slice(0, 10);
console.log(`\n🚨 Recent errors (last ${errors.length}):`);
if (errors.length === 0) {
  console.log('  ✅ No errors recorded');
} else {
  for (const e of errors) {
    console.log(`  [${e.time}] (${e.context}) ${e.message}`);
  }
}

console.log('\n✅ Diagnostic complete\n');
