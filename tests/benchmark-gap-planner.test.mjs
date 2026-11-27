import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import {execFileSync} from "node:child_process";
import os from "node:os";
import path from "node:path";

test("planner preserves the 65-MasterBot and 55-domain scopes",()=>{
 const dir=fs.mkdtempSync(path.join(os.tmpdir(),"dreamco-gap-"));
 const scores=path.join(dir,"scores.json"),out=path.join(dir,"queue.json");
 fs.writeFileSync(scores,JSON.stringify({results:[
  {scope:"masterbot",masterbot_id:1,benchmark:"reasoning",score:40,target:80,status:"failed"},
  {scope:"masterbot",masterbot_id:2,benchmark:"coding",score:90,target:80,status:"pass"}
 ]}));
 execFileSync("python3",["tools/benchmark_gap_planner.py","--scores",scores,"--out",out]);
 const q=JSON.parse(fs.readFileSync(out,"utf8"));
 assert.equal(q.schema,"dreamco.benchmark_gap_queue.v2");
 assert.equal(q.masterbot_count,65);
 assert.equal(q.domain_division_count,55);
 assert.equal(q.summary.masterbots_measured,2);
 assert.equal(q.summary.masterbots_unmeasured,63);
 assert.equal(q.summary.domain_divisions_measured,0);
 assert.equal(q.summary.domain_divisions_unmeasured,55);
 assert.ok(q.queue.some(x=>x.scope==="masterbot"&&x.masterbot_id===1&&x.action==="CLOSE_GAPS"));
 assert.ok(q.queue.some(x=>x.scope==="domain_division"&&x.action==="RUN_BENCHMARKS"));
 assert.ok(q.queue.some(x=>x.scope==="masterbot"&&x.masterbot_id===3&&x.action==="RUN_BENCHMARKS"));
 assert.equal(q.queue.filter(x=>x.scope==="masterbot").length,65);
 assert.equal(q.queue.filter(x=>x.scope==="domain_division").length,55);
});
