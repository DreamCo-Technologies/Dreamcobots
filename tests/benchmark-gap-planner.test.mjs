import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import {execFileSync} from "node:child_process";
import os from "node:os";
import path from "node:path";

test("planner creates work for all 65 divisions",()=>{
 const dir=fs.mkdtempSync(path.join(os.tmpdir(),"dreamco-gap-"));
 const scores=path.join(dir,"scores.json"),out=path.join(dir,"queue.json");
 fs.writeFileSync(scores,JSON.stringify({results:[{scope:"masterbot",masterbot_id:1,benchmark:"reasoning",score:40,target:80,status:"failed"},{scope:"masterbot",masterbot_id:2,benchmark:"coding",score:90,target:80,status:"pass"}]}));
 execFileSync("python3",["tools/benchmark_gap_planner.py","--scores",scores,"--out",out]);
 const q=JSON.parse(fs.readFileSync(out,"utf8"));
 assert.equal(q.masterbot_count,65);\n assert.equal(q.domain_division_count,55);
 assert.ok(q.queue.some(x=>x.masterbot_id===1&&x.action==="CLOSE_GAPS"));
 assert.ok(q.queue.some(x=>x.masterbot_id===3&&x.action==="RUN_BENCHMARKS"));
});
