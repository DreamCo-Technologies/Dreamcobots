import assert from 'node:assert/strict';
import { readdirSync, readFileSync } from 'node:fs';
import test from 'node:test';

const source = readFileSync('website/page-actions.js', 'utf8');
const nav = readFileSync('website/nav.js', 'utf8');
const worker = readFileSync('website/service-worker.js', 'utf8');
const pages = readdirSync('website').filter((name) => name.endsWith('.html'));

test('shared nav loads working fallback actions across public pages', () => {
  const pagesWithNav = pages.filter((name) => /nav\.js/.test(readFileSync(`website/${name}`, 'utf8')));
  assert.ok(pagesWithNav.length >= 70, `only ${pagesWithNav.length} pages load shared navigation`);
  assert.match(nav, /page-actions\.js\?v=3/);
  assert.match(source, /actionMaps\[page\] \|\| genericActions\(\)/);
  for (const label of ['Ask Buddy', 'Find Sources', 'Repository Evidence', 'Test This Area', 'Learning Evidence', 'Connect Resource']) {
    assert.match(source, new RegExp(label));
  }
});

test('previously inert contextual actions now have a real governed destination', () => {
  assert.match(source, /if \(event\.defaultPrevented\) return/);
  assert.match(source, /resource-connection-center\.html\?resource=/);
  assert.match(source, /buddy\.html\?prompt=/);
  assert.match(source, /Prepare a preview only\. Do not publish without exact approval/);
  assert.match(worker, /page-actions\.js\?v=3/);
});

