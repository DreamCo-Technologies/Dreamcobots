import assert from 'node:assert/strict';
import fs from 'node:fs';
import test from 'node:test';
import vm from 'node:vm';

const catalogSource = fs.readFileSync('website/data/buddy-setup-catalog.js', 'utf8');
const html = fs.readFileSync('website/buddy.html', 'utf8');
const buddySource = fs.readFileSync('website/buddy.js', 'utf8');
const serviceWorkerSource = fs.readFileSync('website/service-worker.js', 'utf8');
const context = { window: {} };
vm.runInNewContext(catalogSource, context);
const catalog = context.window.BUDDY_SETUP_CATALOG;

test('every Buddy launcher has exactly 30 unique setup choices', () => {
  assert.equal(catalog.schema, 'dreamco.buddy_setup_catalog.v1');
  assert.equal(catalog.launchers.length, 16);
  assert.equal(catalog.summary.setupOptionCount, 480);
  const launcherIds = new Set();
  const optionIds = new Set();
  for (const launcher of catalog.launchers) {
    assert.equal(launcher.options.length, 30, launcher.id);
    assert.equal(launcherIds.has(launcher.id), false, launcher.id);
    launcherIds.add(launcher.id);
    for (const option of launcher.options) {
      assert.equal(optionIds.has(option.id), false, option.id);
      assert.ok(option.label.length >= 8, option.id);
      optionIds.add(option.id);
    }
    assert.match(html, new RegExp(`data-buddy-launcher=["']${launcher.id}["']`));
  }
});

test('guided setup launchers are visible only in Plan mode', () => {
  assert.match(html, /id="buddy-starters"[^>]+hidden/);
  assert.match(buddySource, /starters\.hidden = mode !== 'Plan'/);
  assert.match(buddySource, /function setBuddyMode\(nextMode\)/);
  assert.match(buddySource, /button\.addEventListener\('click', \(\) => setBuddyMode\(button\.dataset\.buddyMode\)\)/);
  assert.match(buddySource, /freeformPromptAccepted: true/);
  assert.match(buddySource, /guidedSetupRequired: false/);
});

test('freeform requests are captured in a bounded owner task workspace', () => {
  assert.match(html, /id="task-dialog"/);
  assert.match(html, /id="task-create-form"/);
  assert.match(buddySource, /const taskStorageKey = 'buddy-current-tasks-v1'/);
  assert.match(buddySource, /createCurrentTask\(objective, mode\)/);
  assert.match(buddySource, /filter\(\(task\) => task\.status === 'completed'\)\.slice\(-50\)/);
  assert.match(buddySource, /status: 'ready_for_review'/);
});

test('Buddy setup catalog and page link to the owned GitHub repository', () => {
  assert.equal(catalog.repository.url, 'https://github.com/DreamCo-Technologies/Dreamcobots');
  assert.match(html, /DreamCo-Technologies\/Dreamcobots/);
  assert.match(html, /Dreamcobots\/actions/);
  assert.match(html, /Dreamcobots\/issues/);
  assert.match(html, /Dreamcobots\/pulls/);
});

test('timed tasks support indefinite recurrence without pre-approving external actions', () => {
  assert.match(html, /Continue until I stop it/);
  assert.match(html, /Call now/);
  assert.match(html, /Schedule/);
  assert.match(buddySource, /until_stopped/);
  assert.match(buddySource, /returningFromOneTime[\s\S]+endMode\.value = 'until_stopped'/);
  assert.match(buddySource, /local_sandbox_routing_only_external_actions_require_fresh_approval/);
  assert.match(buddySource, /window\.setInterval\(checkDueSchedules/);
  const cacheFirstSource = serviceWorkerSource.match(/async function cacheFirst[\s\S]+?\n}/)?.[0] || '';
  assert.doesNotMatch(cacheFirstSource, /ignoreSearch/);
});
