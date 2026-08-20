#!/usr/bin/env node
import fs from 'node:fs';

const input = process.argv[2];
if (!input) {
  console.error('Usage: node tools/evaluate_buddy_pr_review.mjs <review-result.json>');
  process.exit(2);
}

const result = JSON.parse(fs.readFileSync(input, 'utf8'));
const required = ['findings', 'checks', 'requirements_coverage'];
for (const key of required) if (!(key in result)) throw new Error(`Missing ${key}`);

const findings = Array.isArray(result.findings) ? result.findings : [];
const checks = Array.isArray(result.checks) ? result.checks : [];
const coverage = Number(result.requirements_coverage);
const validFinding = f => f && typeof f.severity === 'string' && typeof f.confidence === 'number' && typeof f.evidence === 'string' && typeof f.actionable === 'boolean';
const valid = findings.filter(validFinding).length;
const highConfidence = findings.filter(f => f.confidence >= 0.85).length;
const blockers = findings.filter(f => ['critical', 'high'].includes(String(f.severity).toLowerCase()) && f.confidence >= 0.85).length;
const deterministicFailures = checks.filter(c => c && String(c.status).toLowerCase() === 'failure').length;

const score = {
  finding_schema_rate: findings.length ? valid / findings.length : 1,
  requirements_coverage: Number.isFinite(coverage) ? Math.max(0, Math.min(1, coverage)) : 0,
  deterministic_pass_rate: checks.length ? (checks.length - deterministicFailures) / checks.length : 1,
  blocker_signal: blockers > 0 ? 0 : 1,
  confidence_signal: highConfidence > 0 || findings.length === 0 ? 1 : 0.5
};
score.overall = Object.values(score).reduce((a, b) => a + b, 0) / Object.keys(score).length;

const report = {
  benchmark: 'buddy-pr-review-v1',
  generated_at: new Date().toISOString(),
  metrics: { ...score, finding_count: findings.length, blocker_count: blockers },
  status: score.overall >= 0.9 && blockers === 0 ? 'passing_candidate' : 'needs_repair',
  mastery: 'not_mastered',
  reason: 'Mastery requires repeated task-specific benchmark evidence, including false-positive/false-negative measurement and post-merge outcomes.'
};
console.log(JSON.stringify(report, null, 2));
