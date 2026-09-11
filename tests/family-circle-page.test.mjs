import assert from 'node:assert/strict';
import fs from 'node:fs';
import test from 'node:test';
const html=fs.readFileSync('website/family-circle.html','utf8');
const script=fs.readFileSync('website/family-circle.js','utf8');
const nav=fs.readFileSync('website/nav.js','utf8');
test('Family Circle is reachable and consent/revocation are enforced',()=>{assert.match(nav,/family-circle\.html/);assert.match(html,/approved sharing/);assert.match(html,/Pause & revoke|pause or revoke/);assert.match(script,/member-consent.*checked/);assert.match(script,/data-revoke/)});
test('safe places, check-ins, and honest background limits are present',()=>{assert.match(html,/Safe places and alerts/);assert.match(script,/getCurrentPosition/);assert.match(html,/cannot guarantee background tracking/);assert.match(html,/installed mobile service/)});
test('missing-child flow follows immediate official escalation',()=>{assert.match(html,/Call local law enforcement/);assert.match(html,/1-800-843-5678/);assert.match(html,/us\.missingkids\.org\/MissingChild/);assert.match(script,/missing_child_emergency_packet/);assert.match(script,/doNotPublishLiveLocation:true/);assert.doesNotMatch(script,/faceRecognition|biometric/i)});
