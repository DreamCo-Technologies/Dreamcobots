// Standalone browser check; no external requests or running development server.
const assert = require('node:assert/strict');
const fs = require('node:fs/promises');
const path = require('node:path');
const { chromium } = require(process.env.DREAMCO_PLAYWRIGHT_MODULE || 'playwright');
(async()=>{
  const browser=await chromium.launch({headless:true,...(process.env.PLAYWRIGHT_EXECUTABLE_PATH?{executablePath:process.env.PLAYWRIGHT_EXECUTABLE_PATH}:{})});
  try {
    const page=await browser.newPage({viewport:{width:390,height:844}});
    const errors=[];page.on('pageerror',e=>errors.push(e.message));
    await page.route('**/*',async route=>{
      const url=new URL(route.request().url());
      if(url.origin!=='http://buddy.test') return route.abort();
      const file=path.resolve('website',decodeURIComponent(url.pathname.replace(/^\/Dreamcobots\//,'')));
      if(!file.startsWith(path.resolve('website')+path.sep)) return route.abort();
      try { await route.fulfill({path:file}); } catch { await route.fulfill({status:404,body:'Not found'}); }
    });
    await page.goto('http://buddy.test/Dreamcobots/buddy-setup-guide.html');
    await page.getByLabel('Me and my clients',{exact:false}).check();
    await page.getByRole('button',{name:'4. Learning sources',exact:true}).click();
    await page.getByLabel('GitHub repositories and Actions',{exact:true}).check();
    await page.getByLabel('Databases and structured data',{exact:true}).check();
    await page.reload();
    await page.getByLabel('Databases and structured data',{exact:true}).waitFor();
    assert.equal(await page.getByLabel('Databases and structured data',{exact:true}).isChecked(),true);
    await page.getByRole('button',{name:'5. Model test',exact:true}).click();
    const record={model:'HuggingFaceTB/SmolLM2-135M-Instruct',revision:'a'.repeat(40),elapsed_ms:234,created_at:'2026-09-27T10:00:00Z',execution:'local_model_inference',external_actions_executed:false,output:'<script>window.bad=true</script>',prompt:'private content'};
    await page.locator('#sg-model-record').setInputFiles({name:'test.json',mimeType:'application/json',buffer:Buffer.from(JSON.stringify(record))});
    await page.locator('#sg-model-status').filter({hasText:'Imported model'}).waitFor();
    assert.equal(await page.evaluate(()=>window.bad),undefined);
    const saved=await page.evaluate(()=>localStorage.getItem('dreamco.buddy.setup-guide.v1'));
    assert.ok(!saved.includes('private content')&&!saved.includes('<script>'));
    await page.getByRole('button',{name:'6. Readiness plan',exact:true}).click();
    await page.getByText('Plan prepared — production not verified',{exact:true}).waitFor();
    const downloadEvent=page.waitForEvent('download');
    await page.getByRole('button',{name:'Download setup plan',exact:true}).click();
    const download=await downloadEvent;const plan=JSON.parse(await fs.readFile(await download.path(),'utf8'));
    assert.equal(plan.production_ready,false);assert.equal(plan.sources.length,2);assert.equal(plan.paid_calls_enabled,false);
    assert.ok(plan.next_steps.some(x=>x.includes('separate user accounts')));
    assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth),true);
    await page.getByText("Clear this guide's saved choices",{exact:true}).click();
    await page.getByRole('button',{name:'Clear setup choices',exact:true}).click();
    assert.equal(await page.evaluate(()=>localStorage.getItem('dreamco.buddy.setup-guide.v1')),null);
    assert.deepEqual(errors,[]);
    const blocked=await browser.newPage();
    await blocked.addInitScript(()=>{Object.defineProperty(window,'localStorage',{get(){throw new Error('Storage blocked');}});});
    await blocked.route('**/*',async route=>{const url=new URL(route.request().url());if(url.origin!=='http://buddy.test')return route.abort();try{await route.fulfill({path:path.resolve('website',url.pathname.replace(/^\/Dreamcobots\//,''))});}catch{await route.fulfill({status:404,body:'Not found'});}});
    await blocked.goto('http://buddy.test/Dreamcobots/buddy-setup-guide.html');
    await blocked.getByText('Browser storage is unavailable.',{exact:false}).waitFor();
    await blocked.getByRole('button',{name:'Next step',exact:true}).click();
    await blocked.getByRole('heading',{name:'Your device',exact:true}).waitFor();
    console.log('PASS: guided setup persists, exports truthful plans, discards prompt/output, handles blocked storage and fits mobile.');
  } finally { await browser.close(); }
})().catch(error=>{console.error(error);process.exitCode=1;});
