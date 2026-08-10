import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import test from 'node:test';

const read = (path) => readFileSync(new URL(`../${path}`, import.meta.url), 'utf8');

test('Lucide GitHub call sites use the supported GitFork alias', () => {
  const files = [
    'client/src/components/AppShell.tsx',
    'client/src/pages/ActionsPage.tsx',
    'client/src/pages/BotActivityPage.tsx',
    'client/src/pages/BuddyPage.tsx',
    'client/src/pages/ConversationPage.tsx',
    'client/src/pages/SandboxPage.tsx',
  ];
  for (const file of files) {
    assert.match(read(file), /GitFork as Github/, file);
  }
});

test('UI wrappers use the installed major-version component APIs', () => {
  const calendar = read('client/src/components/ui/calendar.tsx');
  assert.match(calendar, /button_previous:/);
  assert.match(calendar, /day_button:/);
  assert.match(calendar, /Chevron: \(\{ className, orientation/);
  assert.doesNotMatch(calendar, /IconLeft|IconRight/);

  const chart = read('client/src/components/ui/chart.tsx');
  assert.match(chart, /RechartsPrimitive\.TooltipContentProps/);
  assert.match(chart, /RechartsPrimitive\.TooltipValueType/);

  const resizable = read('client/src/components/ui/resizable.tsx');
  assert.match(resizable, /ResizablePrimitive\.Group/);
  assert.match(resizable, /ResizablePrimitive\.Separator/);
  assert.doesNotMatch(resizable, /ResizablePrimitive\.(?:PanelGroup|PanelResizeHandle)/);
});

test('Actions surfaces keep truthful repository and provider language', () => {
  const actions = read('client/src/pages/ActionsPage.tsx');
  assert.match(actions, /Governed repository workspace/);
  assert.match(actions, /Revenue Provider Candidates/);
  assert.match(actions, />\s*Open docs\s*</);

  const nav = read('website/nav.js');
  assert.match(nav, /href: 'actions\.html'/);
});
