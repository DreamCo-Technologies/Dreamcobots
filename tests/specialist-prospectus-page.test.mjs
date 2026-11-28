import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import test from 'node:test';

const botsHtml = readFileSync('website/bots.html', 'utf8');
const botsSource = readFileSync('website/bots.js', 'utf8');
const divisionsHtml = readFileSync('website/divisions.html', 'utf8');
const divisionsSource = readFileSync('website/divisions.js', 'utf8');
const fleet = JSON.parse(readFileSync('website/data/bot-fleet-catalog.json', 'utf8'));
const fleetE2E = JSON.parse(readFileSync('website/data/bot-fleet-e2e.json', 'utf8'));
const divisions = JSON.parse(readFileSync('website/data/command-center/divisions.json', 'utf8'));
const worker = readFileSync('website/service-worker.js', 'utf8');

test('every registered bot has a prospectus and shares the local specialist questionnaire', () => {
  const expectedProfiles = fleet.summary.canonical_profiles + fleet.summary.supplemental_profiles;
  assert.equal(fleet.summary.profiles, 1120);
  assert.equal(fleet.summary.canonical_profiles, 1051);
  assert.equal(fleet.summary.supplemental_profiles, 69);
  assert.equal(fleet.bots.length, expectedProfiles);
  assert.equal(expectedProfiles, 1120);
  assert.equal(fleetE2E.summary.profilesTested, expectedProfiles);
  assert.equal(fleetE2E.summary.declaredCapabilitiesTested, fleet.summary.declared_capability_slots);
  assert.equal(fleet.summary.declared_capability_slots, fleet.bots.reduce((total, bot) => total + bot.capability_count, 0));
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
  assert.equal(divisions.items.length, 56);
  assert.equal(fleet.divisions.length + fleet.supplemental_divisions.length, 56);
  assert.ok(divisions.items.every((division) => division.bot_ids.length > 0 && division.evidence_refs.length > 0));
  assert.match(divisionsHtml, /Every division, one prospectus and questionnaire/);
  assert.match(divisionsSource, /data-division-prospectus/);
  assert.match(divisionsSource, /id="division-questionnaire"/);
  assert.match(divisionsSource, /verified adapter plus exact approval/);
  assert.match(worker, /\.\/bots\.js\?v=3/);
  assert.match(worker, /\.\/buddy-run\.css/);
  assert.match(worker, /\.\/buddy-run\.js/);
  assert.match(worker, /\.\/divisions\.js\?v=2/);
  assert.match(worker, /\.\/data\/bot-fleet-catalog\.json/);
  assert.match(worker, /\.\/data\/command-center\/divisions\.json/);
});
