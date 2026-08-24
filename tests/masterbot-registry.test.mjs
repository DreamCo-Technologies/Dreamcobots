import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
const registry=JSON.parse(fs.readFileSync("config/masterbot-65-registry.json","utf8"));
const featured=JSON.parse(fs.readFileSync("website/data/masterbot-homepage-featured.json","utf8"));
test("canonical registry has 65 unique divisions",()=>{assert.equal(registry.canonical_count,65);assert.equal(registry.divisions.length,65);assert.equal(new Set(registry.divisions.map(d=>d.id)).size,65);});
test("homepage registry has 20 new MasterBots",()=>{assert.equal(featured.items.length,20);assert.deepEqual(featured.items.map(x=>x.id),Array.from({length:20},(_,i)=>i+46));assert.equal(new Set(featured.items.map(x=>x.slug)).size,20);});
test("homepage names match canonical divisions 46-65",()=>{assert.deepEqual(featured.items.map(x=>x.name),registry.divisions.slice(45).map(d=>d.name));});
