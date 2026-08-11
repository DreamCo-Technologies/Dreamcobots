import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import test from 'node:test';

const runtime = readFileSync(new URL('../server/public-buddy-execution.ts', import.meta.url), 'utf8');
const routes = readFileSync(new URL('../server/intelligent-routing-routes.ts', import.meta.url), 'utf8');
const index = readFileSync(new URL('../server/index.ts', import.meta.url), 'utf8');

test('public execution route exists and is wired to the execution worker', () => {
  assert.match(routes, /\/api\/buddy\/public-execute/);
  assert.match(routes, /executePublicBuddyRequest/);
});

test('execution worker never labels an external consequential action executed', () => {
  assert.match(runtime, /prepared_for_approval/);
  assert.match(runtime, /externalActionsExecuted:\s*false/);
  assert.match(runtime, /Never fabricate tool use or execution receipts/);
});

test('safe response work requires a configured and request-approved model execution route', () => {
  assert.match(runtime, /model_approval_required/);
  assert.match(runtime, /backend_model_not_configured/);
  assert.match(runtime, /executed_safe_response_work/);
  assert.match(runtime, /approvePaidModelForThisRequest/);
});

test('GitHub Pages origin is explicitly allowlisted without wildcard CORS', () => {
  assert.match(index, /https:\/\/dreamco-technologies\.github\.io/);
  assert.doesNotMatch(index, /Access-Control-Allow-Origin["']?,\s*["']\*["']/);
  assert.match(index, /publicExecutionBridge:\s*true/);
});
