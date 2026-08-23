import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import {execFileSync} from "node:child_process";
import os from "node:os";
import path from "node:path";

test("planner creates work for all 65 divisions",()=>{
 const dir=fs.mkdtempSync(path.join(os.tmpdir(),"dreamco-gap-"));
 const scores=path.join(dir,"scores.json"),out=path.join(dir,"queue.json");
 fs.writeFileSync(scores,JSON.stringify({results:[{division:1,benchmark:"reasoning",score:40,target:80,status:"failed"},{division:2,benchmark:"coding",score:90,target:80,status:"pass"}]}));
 execFileSync("python3",["tools/benchmark_gap_planner.py","--scores",scores,"--out",out]);
 const q=JSON.parse(fs.readFileSync(out,"utf8"));
 assert.equal(q.divisions,65);
 assert.ok(q.queue.some(x=>x.division===1&&x.action==="CLOSE_GAPS"));
 assert.ok(q.queue.some(x=>x.division===3&&x.action==="RUN_BENCHMARKS"));
});
