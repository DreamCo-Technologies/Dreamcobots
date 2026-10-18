import test from 'node:test';
import assert from 'node:assert/strict';
import {spawn} from 'node:child_process';
import {mkdtemp,rm} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import path from 'node:path';
import {chromium} from '@playwright/test';

test('real browser: responsive evidence page and authenticated review lifecycle', {timeout:60000}, async () => {
  const temp=await mkdtemp(path.join(tmpdir(),'buddy-review-test-'));
  const server=spawn('python3',['-u','-c',`
import sys
from http.server import ThreadingHTTPServer
from tools.buddy_local_bridge import BuddyLocalHandler, BridgeState, WEBSITE
from buddy_os.evaluation.review import ReviewStore
handler=lambda *a,**kw: BuddyLocalHandler(*a,directory=str(WEBSITE),**kw)
server=ThreadingHTTPServer(('127.0.0.1',0),handler)
server.bridge_state=BridgeState(token='test-agent-only',review_token='test-review-only',reviewer_id='test-owner',review_store=ReviewStore(sys.argv[1]))
print(server.server_port,flush=True)
server.serve_forever()
`,path.join(temp,'review.db')],{stdio:['ignore','pipe','pipe']});
  let browser;
  try {
    const port=await new Promise((resolve,reject)=>{server.once('error',reject);server.stdout.once('data',v=>resolve(Number(String(v).trim())));server.once('exit',code=>reject(new Error('Server exited '+code)));});
    const base='http://127.0.0.1:'+port;
    browser=await chromium.launch({headless:true});
    const page=await browser.newPage(); const errors=[]; page.on('pageerror',e=>errors.push(e.stack));
    await page.goto(base+'/general-intelligence.html');
    await page.waitForFunction(()=>document.querySelectorAll('#gi-matrix tr').length===33);
    assert.equal(await page.locator('#gi-refresh').isDisabled(),true);
    await page.locator('#gi-filter').fill('math'); assert.equal(await page.locator('#gi-matrix tr').count(),1);
    for(const width of [390,1280]){
      await page.setViewportSize({width,height:900});
      assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));
    }
    await page.locator('#gi-filter').fill('');
    if(process.env.GI_SCREENSHOT) await page.screenshot({path:process.env.GI_SCREENSHOT,fullPage:true});
    await page.goto(base+'/general-intelligence.html?session=test#review-token=test-review-only');
    await page.waitForFunction(()=>document.querySelector('#gi-review-status').textContent.includes('test-owner'));
    assert.ok(!page.url().includes('review-token'));
    for(const [label,status] of [['Approve','approved'],['Reject','rejected'],['Edit','pending'],['Escalate','escalated']]){
      const action={action_class:'code_change',title:'Browser test '+label,rationale:'Test scoped human review',evidence:['test-fixture'],risk:'low',reversible:true,expected_cost_usd:0,tools:['sandbox'],data:['fixture'],preview:'Test-only concrete diff',verification:'Local assertion',rollback:'Restore fixture',parameters:{}};
      const result=await fetch(base+'/api/local/evaluation/propose',{method:'POST',headers:{Authorization:'Bearer test-agent-only','Content-Type':'application/json'},body:JSON.stringify({action})});
      assert.equal(result.status,201); const {id}=await result.json();
      await page.locator('#gi-refresh').click();
      const card=page.locator('#gi-queue article').filter({hasText:action.title});
      await card.getByRole('button',{name:label,exact:true}).click();
      await page.waitForFunction(async ({base,id,status})=>{
        const r=await fetch(base+'/api/local/evaluation/queue',{headers:{Authorization:'Bearer test-review-only'}});const d=await r.json();return d.actions.some(a=>a.id===id && a.status===status && a.revision===2);
      },{base,id,status});
    }
    assert.deepEqual(errors,[]);
  } finally {
    await browser?.close();server.kill('SIGTERM');await rm(temp,{recursive:true,force:true});
  }
});
