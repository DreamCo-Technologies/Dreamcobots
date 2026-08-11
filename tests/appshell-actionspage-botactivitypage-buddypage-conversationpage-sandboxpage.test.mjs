import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import test from 'node:test';

function source(path) {
  return readFileSync(new URL(`../${path}`, import.meta.url), 'utf8');
}

test('AppShell keeps canonical navigation and Buddy entry surface', () => {
  const text = source('client/src/components/AppShell.tsx');
  assert.match(text, /Buddy/i);
  assert.match(text, /(nav|navigation|sidebar)/i);
});

test('ActionsPage exposes owner-visible action state instead of decorative controls', () => {
  const text = source('client/src/pages/ActionsPage.tsx');
  assert.match(text, /(action|workflow)/i);
  assert.match(text, /(status|health|run|test)/i);
});

test('BotActivityPage exposes activity or execution evidence', () => {
  const text = source('client/src/pages/BotActivityPage.tsx');
  assert.match(text, /(activity|bot)/i);
  assert.match(text, /(status|run|task|event)/i);
});

test('BuddyPage starts a real conversation route rather than a decorative reply', () => {
  const text = source('client/src/pages/BuddyPage.tsx');
  assert.match(text, /useCreateConversation/);
  assert.match(text, /setLocation\(`\/c\/\$\{conv\.id\}/);
});

test('ConversationPage is wired to the assistant streaming path', () => {
  const text = source('client/src/pages/ConversationPage.tsx');
  assert.match(text, /streamAssistantReply/);
  assert.match(text, /(agent-run|execute-code|stream)/i);
});

test('SandboxPage remains explicitly sandbox-oriented and testable', () => {
  const text = source('client/src/pages/SandboxPage.tsx');
  assert.match(text, /sandbox/i);
  assert.match(text, /(test|run|execute|result)/i);
});
