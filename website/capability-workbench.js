export function incomeScenario({price, cost, leads, rate, fixed}) {
  if (![price,cost,leads,rate,fixed].every(Number.isFinite) || Math.min(price,cost,leads,rate,fixed)<0 || rate>100) throw new Error('Enter valid nonnegative amounts and a conversion rate up to 100.');
  const sales=leads*rate/100, margin=price-cost;
  return {expectedSales:sales, revenue:sales*price, contributionPerSale:margin, profit:sales*margin-fixed, breakEvenSales:margin>0?Math.ceil(fixed/margin):null};
}

if (typeof document !== 'undefined') {
  const $=id=>document.getElementById(id), BR=window.BuddyRun;
  let files=[], verdicts=new Map(), bots=[], meta, fileLimit=60, botLimit=20;
  const node=(tag,text)=>{const n=document.createElement(tag);if(text!==undefined)n.textContent=text;return n;};
  const link=(text,url)=>{const a=node('a',text);a.href=url;return a;};
  async function read(url){const r=await fetch(url,{cache:'no-cache'});if(!r.ok)throw new Error(url+' HTTP '+r.status);return r.json();}
  function renderFiles(){
    const q=$('cw-search').value.toLowerCase(), kind=$('cw-filter').value;
    const filtered=files.filter(r=>(kind==='all'||r.kind===kind)&&r.path.toLowerCase().includes(q));
    $('cw-count').textContent=filtered.length+' matching files';$('cw-files').replaceChildren();
    for(const r of filtered.slice(0,fileLimit)){
      const tr=node('tr'), controls=node('td');tr.append(node('td',r.path),node('td',r.page?(verdicts.get(r.page)||'not audited'):'source indexed'));
      controls.append(link('Source',r.source));
      if(r.page){controls.append(' · ',link('Open page',r.page));const b=node('button','Verify page loads');b.type='button';b.addEventListener('click',async()=>{b.disabled=true;try{const result=await fetch(r.page,{cache:'no-cache'});b.textContent=result.ok?'HTTP '+result.status+' · loads':'HTTP '+result.status+' · failed';}catch{b.textContent='Connection failed';}finally{b.disabled=false;}});controls.append(b);}
      tr.append(controls);$('cw-files').append(tr);
    }
    $('cw-more').hidden=filtered.length<=fileLimit;
  }
  function renderBots(){
    const q=$('cw-bot-search').value.toLowerCase(), filtered=bots.filter(r=>JSON.stringify(r).toLowerCase().includes(q));
    $('cw-bot-count').textContent=filtered.length+' bots · use Prospectus to inspect runtime, permissions and evidence';$('cw-bots').replaceChildren();
    for(const r of filtered.slice(0,botLimit)){
      const card=BR.resolveBot(r,meta), article=node('article');article.className='cw-bot';article.append(node('h3',r.title),node('p',r.division+' · '+r.engine+' · '+r.readiness));
      const controls=node('div');controls.innerHTML=BR.runControls(card);article.append(controls,link('Full runtime evidence','fleet-runtime.html#bot-'+encodeURIComponent(r.id)));$('cw-bots').append(article);
    }
    $('cw-bot-more').hidden=filtered.length<=botLimit;
  }
  $('cw-search').addEventListener('input',()=>{fileLimit=60;renderFiles();});$('cw-filter').addEventListener('change',()=>{fileLimit=60;renderFiles();});$('cw-more').addEventListener('click',()=>{fileLimit+=60;renderFiles();});
  $('cw-bot-search').addEventListener('input',()=>{botLimit=20;renderBots();});$('cw-bot-more').addEventListener('click',()=>{botLimit+=20;renderBots();});
  $('cw-build').addEventListener('submit',event=>{event.preventDefault();const f=new FormData(event.target);const spec={schema:'dreamco.user_capability_spec.v1',target:f.get('target'),source:f.get('source'),behavior:f.get('behavior'),customization:f.get('customization'),acceptanceTest:f.get('test'),sourcePermissionAttested:f.get('rights')==='on',status:'specification_only',steps:['Observe authorized behavior','Implement custom version in sandbox','Run independent acceptance test','Review permissions before live use']};const text=JSON.stringify(spec,null,2);$('cw-build-result').textContent=text;const url=URL.createObjectURL(new Blob([text],{type:'application/json'}));const a=link('Download specification',url);a.download='buddy-capability-spec.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);});
  $('cw-income').addEventListener('submit',event=>{event.preventDefault();const f=new FormData(event.target);try{const input=Object.fromEntries(['price','cost','leads','rate','fixed'].map(k=>[k,Number(f.get(k))]));$('cw-income-result').textContent=JSON.stringify({offer:f.get('offer'),...incomeScenario(input),evidence:'User assumptions only; no actual earnings measured.'},null,2);}catch(error){$('cw-income-result').textContent=error.message;}});
  Promise.all([read('data/pages-connection-index.json'),read('data/pages-feature-audit.json'),BR.loadMeta(),BR.loadBots()]).then(([index,audit,m,b])=>{files=index.files;verdicts=new Map(audit.rows.map(r=>[r.page,r.verdict]));meta=m;bots=[...b.values()];$('cw-status').textContent=index.counts.tracked_files+' indexed files · '+index.counts.pages+' pages · '+bots.length+' bot profiles. Evidence is a checkout snapshot.';renderFiles();renderBots();}).catch(error=>{$('cw-status').textContent='Evidence could not load: '+error.message;});
}
