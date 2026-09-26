import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import test from 'node:test';
import vm from 'node:vm';
import {buildFleetCatalog,compactCatalog} from '../tools/generate_bot_fleet_catalog.ts';
import {loadSupplementalBotSources,buildSupplementalBotSeeds} from '../server/seed-supplemental-bots.ts';
import {FleetRuntimeRegistry} from '../server/fleet-runtime.ts';
test('all 50 original growth specifications survive supplemental routing without promoting readiness',()=>{
 const sources=loadSupplementalBotSources(), seeds=buildSupplementalBotSeeds(), catalog=buildFleetCatalog();
 assert.equal(sources.length,50);assert.equal(seeds.length,50);assert.equal(catalog.bots.length,1051);assert.equal(catalog.supplemental_bots.length,50);
 const runtime=FleetRuntimeRegistry.fromFile();
 for(const {profile,source} of sources){
  const raw=JSON.parse(readFileSync(source,'utf8')).bots.find((b:any)=>b.slug===profile.slug);
  assert.deepEqual(profile.capabilities,raw.capabilities);assert.equal(profile.description,raw.description);
  const seed=seeds.find(b=>b.slug===profile.slug)!;assert.equal(seed.status,'sandbox');assert.deepEqual(seed.capabilities,profile.capabilities);
  const bot=runtime.get(profile.slug);assert.ok(bot,profile.slug);
  for(const c of profile.capabilities){const result=bot.testCapability(c);assert.equal(result.status,'sandbox_contract_passed');assert.equal(result.liveExternalActionTaken,false);}
  const result=bot.execute({objective:'Prepare a sandbox acceptance test for this original specification.',input:{},requestedCapabilities:profile.capabilities,liveActionRequested:true});assert.equal(result.status,'approval_required');assert.equal(result.liveExternalActionTaken,false);
 }
});
test('supplemental count mismatch and duplicate identities are rejected',()=>{
 const catalog=JSON.parse(readFileSync('config/generated/bots.catalog.json','utf8'));
 const bad=structuredClone(catalog);bad.summary.supplemental_profiles++;assert.throws(()=>new FleetRuntimeRegistry(bad),/Supplemental/);
 const duplicate=structuredClone(catalog);duplicate.supplemental_bots[0].identity.slug=duplicate.bots[0].identity.slug;assert.throws(()=>new FleetRuntimeRegistry(duplicate),/Duplicate/);
});
test('compact published fleet preserves every canonical and supplemental profile',()=>{
 const catalog=buildFleetCatalog();
 const publicCatalog=JSON.parse(readFileSync('website/data/bot-fleet-catalog.json','utf8'));
 assert.deepEqual(publicCatalog,compactCatalog(catalog,{includeSupplemental:true}));
 assert.equal(publicCatalog.bots.length,1101);
 assert.equal(publicCatalog.summary.profiles,1101);
 assert.equal(publicCatalog.summary.canonical_profiles,1051);
 assert.equal(publicCatalog.divisions.length,55);
 assert.equal(publicCatalog.summary.declared_capability_slots,8460);
 for(const bot of [...catalog.bots,...catalog.supplemental_bots]){
  const shard=JSON.parse(readFileSync(`website/data/bot-fleet/${bot.identity.division}.json`,'utf8'));
  assert.deepEqual(shard.bots.find((item:any)=>item.identity.slug===bot.identity.slug),bot);
 }
});
test('published routing and sandbox certifications agree for every fleet profile',()=>{
 const context={window:{} as Record<string,any>};
 for(const path of ['website/data/buddy-routing-index.js','website/data/buddy-capability-certifications.js'])vm.runInNewContext(readFileSync(path,'utf8'),context);
 const routing=context.window.BUDDY_ROUTING_INDEX;
 const certification=context.window.BUDDY_CAPABILITY_CERTIFICATIONS;
 const catalog=JSON.parse(readFileSync('website/data/bot-fleet-catalog.json','utf8'));
 assert.equal(routing.summary.profiles,catalog.summary.profiles);
 assert.equal(certification.summary.profilesTested,catalog.summary.profiles);
 assert.equal(certification.summary.declaredCapabilitiesTested,catalog.summary.declared_capability_slots);
 assert.equal(certification.summary.liveExternalFlowComplete,false);
 const routes=new Set(routing.bots.map((row:any[])=>row[0]));
 for(const bot of catalog.bots){
  assert.ok(routes.has(bot.identity.slug),bot.identity.slug);
  const evidence=certification.bots[bot.identity.slug];assert.ok(evidence,bot.identity.slug);
  assert.equal(evidence.declaredCapabilityCount,bot.capability_count);
  assert.equal(evidence.capabilityTestsPassed,bot.capability_count);
  assert.equal(evidence.capabilityTestsFailed,0);
 }
});
