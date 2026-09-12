import assert from 'node:assert/strict';
import fs from 'node:fs';
import test from 'node:test';

const html = fs.readFileSync('website/world-lens.html', 'utf8');
const script = fs.readFileSync('website/world-lens.js', 'utf8');
const nav = fs.readFileSync('website/nav.js', 'utf8');
const policy = JSON.parse(fs.readFileSync('config/buddy-world-lens-gps.json', 'utf8'));

test('World Lens is reachable and every visible control is wired', () => {
  assert.match(nav, /world-lens\.html/);
  const ids = [...html.matchAll(/<button[^>]+id="([^"]+)"/g)].map(match => match[1]);
  assert.deepEqual(ids.sort(), ['lens-add','lens-buddy','lens-clear','lens-export','lens-find','lens-finder-voice','lens-locate','lens-map-refresh','lens-person-clear','lens-person-save','lens-properties','lens-stop','lens-voice','lens-voice-stop','lens-watch']);
  for (const id of ids) assert.match(script, new RegExp(`\\$\\('${id}'\\)\\.addEventListener`), `missing handler for ${id}`);
});

test('location intent searches rentals, jobs, and services through an authorized provider', () => {
  for (const kind of ['rentals','property_sale','jobs','food','shelter','healthcare','government','transit']) assert.match(html, new RegExp(`value="${kind}"`));
  assert.match(script, /radiusKm/);
  assert.match(script, /credentials:'omit'/);
  assert.match(script, /Source:/);
  assert.match(script, /authorized_location_search/);
});

test('GPS is consent based, stoppable, and not started on load', () => {
  assert.match(script, /getCurrentPosition\(acceptPosition/);
  assert.match(script, /watchPosition\(acceptPosition/);
  assert.match(script, /clearWatch\(watchId\)/);
  assert.doesNotMatch(script, /^\s*navigator\.geolocation\.(getCurrentPosition|watchPosition)/m);
  assert.match(policy.privacy.background_tracking, /page_open_only/);
  assert.equal(policy.privacy.people_are_not_targets, true);
});

test('location truth and safety boundaries are visible', () => {
  assert.match(html, /not turn-by-turn navigation/);
  assert.match(html, /GPS and listings can be delayed or wrong/);
  assert.match(script, /accuracyMeters/);
  assert.match(script, /freshness/);
  assert.equal(policy.safety.emergency_use, false);
  assert.equal(policy.safety.surveillance_use, false);
});

test('external network requests require an enabled map or configured property provider', () => {
  assert.match(script, /localStorage/);
  assert.match(script, /lens-external-map.*checked/);
  assert.match(script, /https:\\\/\\\//);
  assert.match(script, /fetch\(url/);
  assert.doesNotMatch(script, /WebSocket/);
  assert.match(script, /spatial_mission_packet/);
});

test('people profiles require consent and do not use facial recognition', () => {
  assert.match(script, /lens-person-consent.*checked/);
  assert.match(html, /does not perform facial recognition/);
  assert.equal(policy.people_profiles.consent_required, true);
  assert.equal(policy.safety.facial_identification, false);
  assert.ok(policy.people_profiles.disallowed.includes('biometric templates'));
});

test('users can select World Lens, Google, or combined maps', () => {
  for (const mode of ['world_lens','google','combined']) assert.match(html, new RegExp(`value="${mode}"`));
  assert.ok(script.includes('https://www.google.com/maps'));
  assert.deepEqual(policy.map_modes, ['world_lens','google','combined']);
});

test('voice commands mark current coordinates, explicit coordinates, or geocoded places', () => {
  assert.match(script, /SpeechRecognition/);
  assert.match(script, /mark here as/);
  assert.match(script, /voice_geocoder/);
  assert.match(script, /saveWaypoint/);
  assert.ok(policy.voice_commands.length >= 3);
});

test('property history keeps unavailable fields explicit', () => {
  assert.match(html, /Homes and property history/);
  assert.match(script, /Unavailable from connected source/);
  assert.ok(policy.property_record_groups.includes('sale_history'));
  assert.ok(policy.property_record_groups.includes('permits'));
  assert.ok(policy.property_record_groups.includes('title_and_liens'));
});
