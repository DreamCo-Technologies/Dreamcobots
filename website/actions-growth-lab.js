(function(){'use strict';
const manifests=[
 'data/buddy-original-writing-manifest.json',
 'data/buddy-knowledge-synthesis-actions.json',
 'data/buddy-adaptive-curriculum-actions.json',
 'data/buddy-learning-economics-actions.json',
 'data/buddy-learning-memory-actions.json',
 'data/buddy-mastery-ledger-actions.json',
 'data/buddy-parenting-principles-actions.json'
];
const sleep=(ms)=>new Promise(r=>setTimeout(r,ms));
async function load(){
  const results=await Promise.allSettled(manifests.map(url=>fetch(url).then(r=>r.ok?r.json():null)));
  const actions=[]; results.forEach(result=>{if(result.status==='fulfilled'&&result.value){const items=result.value.actions||[];items.forEach(item=>actions.push(item));}});
  if(!actions.length)return;
  for(let i=0;i<20&&!document.getElementById('actions-control-cards');i++)await sleep(100);
  const host=document.getElementById('actions-control-cards');if(!host)return;
  const section=document.createElement('section');section.className='buddy-growth-lab';
  const heading=document.createElement('div');heading.className='buddy-growth-heading';
  heading.innerHTML='<div><p class="actions-kicker">Buddy growth lab</p><h3>Train, test, teach, recover and mature</h3></div><span>'+actions.length+' growth controls</span>';
  section.appendChild(heading);
  const groups=document.createElement('div');groups.className='buddy-growth-groups';
  const buckets={Learning:[],Evaluation:[],Recovery:[],Writing:[],Engineering:[]};
  actions.forEach(action=>{let key='Learning';if(/benchmark|mastery|evaluation|transfer|regression/i.test(action.id+' '+action.label))key='Evaluation';if(/failure|repair|regression|memory|remediation/i.test(action.id+' '+action.label))key='Recovery';if(/book|write|synthesis|example|exercise/i.test(action.id+' '+action.label))key='Writing';if(/specialist|sandbox|audit|approval|efficiency|budget/i.test(action.id+' '+action.label))key='Engineering';buckets[key].push(action);});
  Object.entries(buckets).forEach(([name,items])=>{if(!items.length)return;const group=document.createElement('div');group.className='buddy-growth-group';const title=document.createElement('h4');title.textContent=name;group.appendChild(title);const buttons=document.createElement('div');buttons.className='buddy-growth-buttons';items.forEach(action=>{const link=document.createElement('a');link.className='btn btn-outline';link.textContent=action.label;link.href='buddy.html?prompt='+encodeURIComponent(`Buddy growth action: ${action.label}. ${action.description||''} Use the best specialist for each step, inspect existing repository evidence first, explain the proposed plan, run bounded tests, preserve provenance, record failures and only promote improvements after repeatable evidence.`);link.title=action.description||'';buttons.appendChild(link);});group.appendChild(buttons);groups.appendChild(group);});
  section.appendChild(groups);host.parentElement?.insertBefore(section,host);
}
load().catch(()=>{});
})();