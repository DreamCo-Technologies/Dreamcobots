import assert from 'node:assert/strict';
import fs from 'node:fs';
import test from 'node:test';
import vm from 'node:vm';

const html = fs.readFileSync('website/buddy-command-center.html', 'utf8');
const script = fs.readFileSync('website/buddy-command-center.js', 'utf8');
const nav = fs.readFileSync('website/nav.js', 'utf8');
const index = JSON.parse(fs.readFileSync('website/data/command-center/index.json', 'utf8'));

test('command center route is navigable and loads generated JSON', () => {
  assert.match(nav, /buddy-command-center\.html/);
  assert.match(html, /id="cc-metrics"/);
  assert.match(html, /id="cc-data-status"/);
  assert.match(script, /data\/command-center\/index\.json/);
  assert.match(script, /data\/command-center\/capabilities\.json/);
  assert.equal(index.schema, 'dreamco.command_center.index.v1');
  assert.ok(index.summary.bots > 0);
  assert.ok(index.summary.divisions > 0);
});

test('every command center button has a real event handler', () => {
  const buttonIds = [...html.matchAll(/<button[^>]+id="([^"]+)"/g)].map(match => match[1]);
  assert.ok(buttonIds.length >= 5);
  for (const id of buttonIds) {
    assert.match(script, new RegExp(`\\$\\('${id.replace(/[.*+?^${}()|[\\]\\\\]/g, '\\$&')}'\\)\\.addEventListener`), `missing handler for ${id}`);
  }
});

test('deployment truth is explicit', () => {
  assert.match(html, /Real code execution happens only through an explicitly configured local runner/);
  assert.match(script, /Production readiness remains evidence-gated/);
});

function commandCenterDom(fetch) {
  const nodes = new Map();
  function element(tagName = 'div') {
    return {
      tagName, children: [], handlers: {}, textContent: '', value: '',
      append(...children) { this.children.push(...children); },
      replaceChildren(...children) { this.children = children; },
      addEventListener(name, handler) { this.handlers[name] = handler; },
      focus() { this.focused = true; },
    };
  }
  const document = {
    getElementById(id) {
      if (!nodes.has(id)) nodes.set(id, element());
      return nodes.get(id);
    },
    createElement: element,
  };
  const saved = new Map();
  const context = vm.createContext({
    document, fetch, Date, navigator: {},
    localStorage: { getItem: key => saved.get(key), setItem: (key, value) => saved.set(key, value) },
  });
  vm.runInContext(script, context, { filename: 'buddy-command-center.js' });
  return { nodes, saved };
}

test('generated capability buttons preserve literal text and create a beginner task on click', async () => {
  const name = '<img src=x onerror=alert(1)> Software Engineering';
  const data = { items: [{ name, bot_ids: ['one'], status: 'catalogued' }] };
  const { nodes } = commandCenterDom(async url => ({
    ok: true, json: async () => url.endsWith('capabilities.json') ? data : index,
  }));
  await new Promise(resolve => setImmediate(resolve));
  const [card] = nodes.get('cc-capabilities').children;
  assert.equal(card.tagName, 'button');
  assert.equal(card.type, 'button');
  assert.equal(card.children[0].textContent, name);
  assert.equal(card.children[0].innerHTML, undefined, 'catalog content must not be interpreted as markup');
  card.handlers.click();
  assert.match(nodes.get('cc-task').value, /build one small working example/);
  assert.ok(nodes.get('cc-task').value.includes(name));
  assert.equal(nodes.get('cc-task').focused, true);
  assert.match(nodes.get('cc-status').textContent, /Review the task/);
  nodes.get('cc-plan').handlers.click();
  const contract = JSON.parse(nodes.get('cc-contract').value);
  assert.equal(contract.task, nodes.get('cc-task').value);
  assert.equal(contract.network, 'off-by-default');
  assert.equal(contract.evidence_required, true);
});

test('unavailable generated data retains usable fallback capability buttons', async () => {
  const { nodes } = commandCenterDom(async () => ({ ok: false, status: 503 }));
  await new Promise(resolve => setImmediate(resolve));
  assert.match(nodes.get('cc-data-status').textContent, /unavailable.*503/);
  const card = nodes.get('cc-capabilities').children.find(item => item.children[0].textContent === 'Research');
  assert.ok(card);
  card.handlers.click();
  assert.match(nodes.get('cc-task').value, /understand Research/);
});
