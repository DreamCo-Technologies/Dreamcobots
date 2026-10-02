const {chromium}=require(process.env.DREAMCO_PLAYWRIGHT_MODULE || 'playwright');
const assert=require('node:assert/strict');
(async()=>{const browser=await chromium.launch({executablePath:process.env.PLAYWRIGHT_EXECUTABLE_PATH});const page=await browser.newPage();const errors=[];page.on('pageerror',e=>errors.push(e.message));
await page.goto('http://127.0.0.1:8765/project-conversations.html');await page.waitForFunction(()=>document.getElementById('chat-count').textContent.includes('49'));await page.fill('#chat-search','Gov Website Integration Plan');assert.equal(await page.locator('#chat-list>details').count(),1);await page.click('#chat-list>details>summary');assert.ok((await page.locator('#chat-list').innerText()).includes('corrupt conversation'));
await page.goto('http://127.0.0.1:8765/repositories.html');await page.waitForFunction(()=>document.querySelector('#repo-select').options.length===6);await page.selectOption('#repo-select','DreamCo-Technologies/Dreamcobots');await page.fill('#repos-search','README');assert.ok(await page.locator('#repos-files a').count()>0);await page.route('https://api.github.com/**',r=>r.fulfill({status:403,body:'{}'}));await page.click('#repos-refresh');await page.waitForFunction(()=>document.getElementById('repos-status').textContent.includes('403'));assert.ok(await page.locator('#repos-files a').count()>0);

const fleet=await (await page.request.get('http://127.0.0.1:8765/data/bot-fleet-catalog.json')).json();
assert.equal(fleet.bots.length,1101);
for(const bot of [fleet.bots[0],...fleet.supplemental_bots.filter((_,i)=>i%5===0)]){
 await page.goto('http://127.0.0.1:8765/bots.html?prospectus='+encodeURIComponent(bot.identity.slug));
 await page.waitForFunction(()=>document.getElementById('fleet-profile-count').textContent==='1,101');
 await page.locator('#bot-prospectus[open] #bot-questionnaire-section').waitFor();
 assert.ok((await page.locator('#prospectus-content').innerText()).includes(bot.identity.display_name));
}
console.log('All 10 supplemental divisions opened their bot prospectuses.');
await page.goto('http://127.0.0.1:8765/buddy-model-lab.html');assert.equal(await page.locator('#model-run').isDisabled(),true);await page.click('#model-example');assert.ok((await page.inputValue('#model-prompt')).includes('JavaScript'));await page.click('#model-load');await page.waitForFunction(()=>document.getElementById('model-state').textContent.includes('ready on this device')||document.getElementById('model-state').textContent.includes('error'),null,{timeout:300000});console.log('MODEL_LOAD:',await page.locator('#model-state').innerText());assert.equal(await page.locator('#model-run').isEnabled(),true,'The real model must load successfully');{await page.click('#model-run');await page.waitForFunction(()=>document.getElementById('model-export').disabled===false,null,{timeout:120000});console.log('MODEL_OUTPUT:',await page.locator('#model-output').innerText());}await page.click('#model-stop');await browser.close();assert.deepEqual(errors,[]);console.log('Page interactions passed');})().catch(e=>{console.error(e);process.exit(1);});
