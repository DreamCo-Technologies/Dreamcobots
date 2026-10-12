/** Offline browser audit of every HTML page under the real Pages project prefix. */
import { chromium } from 'playwright';
import { createServer } from 'node:http';
import { readFile, readdir, stat, writeFile } from 'node:fs/promises';
import { resolve, extname, sep } from 'node:path';

const root = resolve(process.argv[2] || 'website');
const reportPath = process.argv[3] || 'tmp/pages-browser.json';
const prefix = '/Dreamcobots/';
const types = { '.html':'text/html', '.js':'text/javascript', '.mjs':'text/javascript', '.css':'text/css', '.json':'application/json', '.svg':'image/svg+xml', '.wasm':'application/wasm' };
const server = createServer(async (req,res) => {
  try {
    const url = new URL(req.url, 'http://localhost');
    if (!url.pathname.startsWith(prefix)) { res.writeHead(404).end(); return; }
    const file = resolve(root, decodeURIComponent(url.pathname.slice(prefix.length)) || 'index.html');
    if (!file.startsWith(root + sep)) { res.writeHead(403).end(); return; }
    const target = (await stat(file)).isDirectory() ? resolve(file, 'index.html') : file;
    res.writeHead(200, { 'content-type':types[extname(target)] || 'application/octet-stream', 'content-security-policy':"worker-src 'none'" });
    res.end(await readFile(target));
  } catch { res.writeHead(404).end(); }
});
await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
const origin = `http://127.0.0.1:${server.address().port}`;
const browser = await chromium.launch({ headless:true, executablePath:process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE || undefined });
const rows = [];
async function pages(dir, relative='') {
  const result=[];
  for (const item of await readdir(dir, {withFileTypes:true})) {
    const path = relative + item.name;
    if(item.isDirectory()) result.push(...await pages(resolve(dir,item.name),path+'/'));
    else if(item.name.endsWith('.html')) result.push(path);
  }
  return result;
}
try {
  const queue=await pages(root);
  async function worker() {
    while(queue.length) {
      const file=queue.shift();
      // CSP blocks workers without injecting Playwright's service-worker shim
      // into opaque sandboxed frames, where navigator.serviceWorker throws.
      const context=await browser.newContext();
      const row={page:file,status:null,errors:[],missing_assets:[],backend_requests:[],external_requests:[]};
      await context.route('**/*', route => {
        const url=new URL(route.request().url());
        if(url.origin!==origin) { row.external_requests.push(url.origin+url.pathname); return route.abort(); }
        if(url.pathname.startsWith('/api/')) { row.backend_requests.push(url.pathname); return route.fulfill({status:503,contentType:'application/json',body:'{"error":"Backend unavailable in static preview"}'}); }
        return route.continue();
      });
      const page=await context.newPage();
      page.on('pageerror', error=>row.errors.push(error.message));
      page.on('response', response=> {if(response.status()>=400 && new URL(response.url()).origin===origin && !new URL(response.url()).pathname.startsWith('/api/')) row.missing_assets.push(new URL(response.url()).pathname);});
      try {
        const response=await page.goto(origin+prefix+file,{waitUntil:'domcontentloaded',timeout:15000});
        row.status=response?.status();
        await page.waitForTimeout(200);
        if(file==='teach-plans.html') {
          await page.locator('#train-note').click();
          if(!(await page.locator('#teach-status').textContent()).includes('stays local')) row.errors.push('Training note control did not update status');
          await page.locator('#compare-methods').click();
          if(!(await page.locator('#teach-status').textContent()).includes('No winner')) row.errors.push('Compare methods control did not update status');
        }
        if(file==='buddy-live-demos.html') {
          await page.locator('#alias').waitFor({state:'attached',timeout:5000});
          if(await page.locator('.stub').count()) row.errors.push('Demo data failed to load');
        }
        row.title=await page.title();
        row.final_path=new URL(page.url()).pathname;
      } catch(error) {row.errors.push(error.message);}
      rows.push(row);
      await context.close();
    }
  }
  await Promise.all(Array.from({length:4},worker));
} finally { await browser.close(); await new Promise(resolve=>server.close(resolve)); }
rows.sort((a,b)=>a.page.localeCompare(b.page));
const failed=rows.filter(r=>r.status!==200 || r.errors.length || r.missing_assets.length);
await writeFile(reportPath,JSON.stringify({root,prefix,pages:rows.length,failed:failed.length,network:'external blocked; backend simulated unavailable',rows},null,2));
console.log(JSON.stringify({pages:rows.length,failed:failed.map(r=>({page:r.page,errors:r.errors,missing_assets:r.missing_assets}))},null,2));
process.exitCode=failed.length?1:0;
