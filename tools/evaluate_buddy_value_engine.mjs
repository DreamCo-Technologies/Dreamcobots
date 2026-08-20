#!/usr/bin/env node
import fs from 'node:fs';

const input = process.argv[2];
if (!input) {
  console.error('Usage: node tools/evaluate_buddy_value_engine.mjs <opportunity-results.json>');
  process.exit(2);
}
const data = JSON.parse(fs.readFileSync(input, 'utf8'));
const opportunities = Array.isArray(data.opportunities) ? data.opportunities : [];
const required = ['title','stage','confidence','evidence','next_experiment'];
const valid = opportunities.filter(o => required.every(k => Object.prototype.hasOwnProperty.call(o,k)));
const observedRevenue = opportunities.filter(o => Number(o.observed_revenue) > 0).length;
const observedProfit = opportunities.filter(o => Number(o.observed_profit) > 0).length;
const actionable = opportunities.filter(o => typeof o.next_experiment === 'string' && o.next_experiment.trim()).length;
const policyChecked = opportunities.filter(o => ['policy_checked','pilot_ready','pilot_running','revenue_observed','profit_observed','repeatable','scalable'].includes(o.stage)).length;
const score = {
  record_completeness: opportunities.length ? valid.length / opportunities.length : 1,
  actionable_rate: opportunities.length ? actionable / opportunities.length : 0,
  policy_checked_rate: opportunities.length ? policyChecked / opportunities.length : 0,
  observed_result_rate: opportunities.length ? (observedRevenue + observedProfit) / (2 * opportunities.length) : 0
};
score.overall = Object.values(score).reduce((a,b)=>a+b,0)/Object.keys(score).length;
console.log(JSON.stringify({
  benchmark:'buddy-value-engine-v1',
  metrics:{...score,opportunity_count:opportunities.length,observed_revenue_count:observedRevenue,observed_profit_count:observedProfit},
  status: score.overall >= 0.75 ? 'healthy_candidate' : 'needs_repair',
  truth_rule:'Predicted revenue/profit never counts as observed revenue/profit.'
},null,2));
