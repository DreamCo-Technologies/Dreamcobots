import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import test from 'node:test';

const root = new URL('../', import.meta.url);
const read = p => readFileSync(new URL(p, root), 'utf8');
const json = p => JSON.parse(read(p));

test('Buddy benchmark standard requires evidence before mastery', () => {
  const doc = read('docs/BUDDY_BENCHMARK_AND_PR_REVIEW_STANDARD.md');
  assert.match(doc, /truth before confidence/);
  assert.match(doc, /Mastery is multidimensional/);
  assert.match(doc, /Before/);
  assert.match(doc, /During/);
  assert.match(doc, /After/);
  assert.match(doc, /post-merge incident correlation/);
});

test('PR review system has lifecycle and safe trust ladder', () => {
  const data = json('website/data/buddy-pr-review-system.json');
  assert.deepEqual(data.lifecycle, ['pre_pr','intake','route','deterministic_checks','semantic_review','adversarial_review','synthesis','revision_watch','merge_readiness','post_merge_learning']);
  assert.deepEqual(data.trust_levels, ['observe','assist','collaborate','guarded_automation','trusted_automation']);
  assert.equal(data.promotion_policy.mastered_requires_repeatable_evidence, true);
  assert.ok(data.benchmarks.includes('false_negative_rate'));
  assert.ok(data.benchmarks.includes('post_merge_correlation'));
});

test('Money opportunity catalog covers earn, save, business and validation paths', () => {
  const data = json('website/data/buddy-money-opportunity-catalog.json');
  assert.ok(data.catalog_categories.length >= 18);
  for (const id of ['ai_services','digital_products','software','commerce','lead_generation','real_estate','logistics','education','creative','funding','employment','cost_savings']) assert.ok(data.catalog_categories.some(x => x.id === id), id);
  for (const stage of ['discovered','researched','screened','pilot_running','revenue_observed','profit_observed','repeatable']) assert.ok(data.validation_stages.includes(stage), stage);
  assert.ok(data.opportunity_record_schema.includes('observed_profit'));
  assert.match(data.truth_policy, /Predictions are opportunities/);
});

test('Actions page exposes PR and money control centers', () => {
  const html = read('website/actions.html');
  assert.match(html, /Buddy PR Review Center/);
  assert.match(html, /Before • During • After/);
  assert.match(html, /Buddy Money Opportunity Engine/);
  assert.match(html, /Find opportunities/);
  assert.match(html, /Compare opportunities/);
  assert.match(html, /Build a pilot/);
  assert.match(html, /Improve my business/);
  assert.match(html, /money-opportunity-center\.css/);
});