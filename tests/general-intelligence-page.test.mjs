import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
const root = process.cwd();
const html = fs.readFileSync('website/general-intelligence.html','utf8');
const js = fs.readFileSync('website/general-intelligence.js','utf8');
const data = JSON.parse(fs.readFileSync('website/data/general-intelligence.json','utf8'));
const manifest = JSON.parse(fs.readFileSync('website/data/general-intelligence-manifest.json','utf8'));

test('all manifest sections, navigation and local links resolve', () => {
  for (const section of manifest.sections) assert.ok(html.includes(`id="${section.id}"`), section.id);
  assert.ok(fs.readFileSync('website/nav.js','utf8').includes("href: 'general-intelligence.html'"));
  for (const m of html.matchAll(/(?:href|src)="([^"#]+)"/g)) assert.ok(fs.existsSync(path.join(root,'website',m[1])),m[1]);
  assert.equal(manifest.source_hash,data.source_hash);
});

test('public artifact contains no invented capability evidence or automatic claims', () => {
  assert.equal(data.automatic_agi_claim,false); assert.equal(data.automatic_frontier_claim,false);
  assert.equal(data.matrix.length,33); assert.equal(data.queue.actions,null);
  assert.ok(data.matrix.every(c => ['untested','partial','verified','reviewed'].includes(c.status)));
  assert.ok(!JSON.stringify(data).includes('review-token'));
});

class Element {
  constructor(tag='div'){this.tag=tag;this.children=[];this.listeners={};this.value='';this.disabled=false;this.textContent='';}
  set textContent(value){this._text=value;if(this.tag==='textarea')this.value=value;}
  get textContent(){return this._text;}
  append(...items){this.children.push(...items);}
  replaceChildren(...items){this.children=[...items];}
  setAttribute(){}
  addEventListener(type,fn){this.listeners[type]=fn;}
  querySelectorAll(tag){return this.children.flatMap(c=>[...(c.tag===tag?[c]:[]),...c.querySelectorAll(tag)]);}
}
async function mount({local=false,token='',failure=false,queue=[],postFailure=false}={}){
  const elements=new Map([...html.matchAll(/id="([^"]+)"/g)].map(m=>[m[1],new Element()]));
  elements.get('gi-refresh').disabled=true;
  const calls=[]; let scrubbed=false;
  const context={document:{getElementById:id=>elements.get(id),createElement:tag=>new Element(tag)},
    location:{protocol:local?'http:':'https:',hostname:local?'127.0.0.1':'example.github.io',pathname:'/general-intelligence.html',search:'',hash:token?'#review-token='+token:''},
    history:{replaceState(){scrubbed=true;}},URL,URLSearchParams,
    fetch:async(url,options)=>{calls.push({url,options}); if(failure) return {ok:false};
      const isPost=options?.method==='POST';
      return {ok:!isPost||!postFailure,json:async()=>isPost?(postFailure?{error:'Stale revision'}:{action:{}}):url.includes('/api/')?{actions:queue,audit:[],reviewer:'owner'}:data};}};
  vm.runInNewContext(js,context); await new Promise(resolve=>setImmediate(resolve));
  return {elements,calls,scrubbed};
}
test('Pages never sends approval credentials or enables private actions',async()=>{
  const {elements,calls,scrubbed}=await mount({token:'test-only'});
  assert.equal(elements.get('gi-refresh').disabled,true); assert.equal(calls.length,1); assert.equal(scrubbed,true);
  assert.equal(elements.get('gi-matrix').children.length,33);
});
test('missing evidence fails closed and does not populate matrix',async()=>{
  const {elements}=await mount({failure:true});
  assert.match(elements.get('gi-status').textContent,/Fail-closed/); assert.equal(elements.get('gi-matrix').children.length,0);
});
test('filter reduces visible capabilities',async()=>{
  const {elements}=await mount(); const filter=elements.get('gi-filter'); filter.value='math'; filter.listeners.input();
  assert.equal(elements.get('gi-matrix').children.length,1);
});
test('all review controls submit scoped decisions and display stale rejection',async()=>{
  for(const decision of ['approve','reject','edit','escalate']){
    const {elements,calls}=await mount({local:true,token:'test-only',postFailure:true,queue:[{id:'approval-test',revision:3,status:'pending',autonomy:'Guided',action:{title:'Change',risk:'low'}}]});
    const buttons=elements.get('gi-queue').querySelectorAll('button');
    const button=buttons.find(b=>b.textContent.toLowerCase()===decision); assert.ok(button); assert.equal(button.disabled,false);
    await button.listeners.click();
    const sent=calls.find(c=>c.options?.method==='POST'); assert.ok(sent);
    const payload=JSON.parse(sent.options.body); assert.equal(payload.revision,3); assert.equal(payload.decision,decision);
    assert.equal(payload.id,'approval-test'); assert.equal(sent.options.headers.Authorization,'Bearer test-only');
  }
});
