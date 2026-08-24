import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
const spec=JSON.parse(fs.readFileSync("config/benchmark-65-loop.json","utf8"));
test("benchmark loop covers all 65 MasterBots",()=>{assert.equal(spec.division_contract.every_masterbot,true);assert.equal(spec.cycle.length,10);assert.ok(spec.runtime_policy.use_matrix_parallelism);assert.ok(spec.runtime_policy.respect_provider_limits);});
test("mastery requires evidence rather than activity",()=>{assert.equal(spec.evidence_policy.mastery_requires_repeatable_results,true);assert.equal(spec.evidence_policy.training_activity_is_not_mastery,true);});
