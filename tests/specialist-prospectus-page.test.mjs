import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import test from 'node:test';

const botsHtml = readFileSync('website/bots.html', 'utf8');
const botsSource = readFileSync('website/bots.js', 'utf8');
const divisionsHtml = readFileSync('website/divisions.html', 'utf8');
const divisionsSource = readFileSync('website/divisions.js', 'utf8');
const fleet = JSON.parse(readFileSync('website/data/bot-fleet-catalog.json', 'utf8'));
const fleetE2E = JSON.parse(readFileSync("website/data/bot-fleet-e2e.json", "utf8"));
const divisions = JSON.parse(readFileSync('website/data/command-center/divisions.json', 'utf8'));
const worker = readFileSync('website/service-worker.js', 'utf8');

test('every registered bot has a prospectus and shares the local specialist questionnaire', () => {
  assert.equal(fleet.summary.profiles, 1120);
  assert.equal(fleet.summary.canonical_profiles, 1051);
  assert.equal(fleet.summary.supplemental_profiles, 69);
  assert.equal(fleet.bots.length, 1120);
  assert.equal(fleet.summary.declared_capability_slots, 8555);
  assert.equal(fleet.bots.length, fleet.summary.profiles);
  assert.ok(fleet.bots.every((bot) => bot.identity?.slug && bot.mission && bot.capability_search));
  assert.match(botsHtml, /id="specialist-matcher-form"/);
  assert.match(botsSource, /data-bot-questionnaire/);
  assert.match(botsSource, /Prepare specialist task/);
  assert.match(botsSource, /live_execution_claimed: false/);
  assert.match(botsSource, /Do not claim a live connection or completed outside action without evidence/);
  assert.match(botsSource, /function renderOfflineProspectus\(bot, reason\)/);
  assert.match(botsSource, /Offline catalog prospectus/);
});

test('specialist matching is deterministic and supports direct division links', () => {
  assert.match(botsSource, /function specialistText\(bot\)/);
  assert.match(botsSource, /SPECIALIST_STOP_WORDS/);
  assert.match(botsSource, /SPECIALIST_SYNONYMS/);
  assert.match(botsSource, /ranked_specialists/);
  assert.match(botsSource, /requestedDivision/);
  assert.doesNotMatch(botsSource, /Math\.random/);
});

test('every generated division gets a prospectus, roster, and questionnaire', () => {
  assert.equal(divisions.summary.registered_divisions, 56);
  assert.equal(divisions.items.length, fleetE2E.summary.divisionsTested);
  assert.deepEqual(divisions.items.map((division) => division.name).sort(), fleetE2E.divisions.map((division) => division.division).sort());
  assert.ok(divisions.items.every((division) => division.bot_ids.length > 0 && division.evidence_refs.length > 0));
  assert.match(divisionsHtml, /id="division-summary"/);
  assert.match(divisionsHtml, /id="division-search"/);
  assert.match(divisionsHtml, /id="division-count"/);
  assert.match(divisionsHtml, /id="divisions-grid"/);
  assert.match(divisionsHtml, /id="division-dialog"/);
  assert.match(divisionsHtml, /id="close-division-dialog"/);
  assert.match(divisionsHtml, /href="buddy-run.css"/);
  assert.match(divisionsHtml, /src="buddy-run.js"/);
  assert.match(divisionsHtml, /src="divisions\.js\?v=2"/);
  assert.match(divisionsSource, /prospectus and local questionnaire for every division/);
  assert.match(divisionsSource, /data-division-prospectus/);
  assert.match(divisionsSource, /id="division-questionnaire"/);
  assert.match(divisionsSource, /verified adapter plus exact approval/);
  assert.match(worker, /\.\/bots\.js\?v=3/);
  assert.match(worker, /\.\/divisions\.js\?v=2/);
  assert.match(worker, /\.\/data\/bot-fleet-catalog\.json/);
  assert.match(worker, /\.\/data\/command-center\/divisions\.json/);
});
