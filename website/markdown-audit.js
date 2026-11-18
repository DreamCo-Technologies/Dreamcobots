(function(){
'use strict';
const REPO='DreamCo-Technologies/Dreamcobots';
const SOURCE='data/markdown-requirements-audit.json';
const state={manifest:null,items:[]};
const $=id=>document.getElementById(id);
const esc=s=>String(s??'');
function sourceUrl(path){return 'https://github.com/'+REPO+'/blob/main/'+path.split('/').map(encodeURIComponent).join('/');}
function editUrl(path){return 'https://github.com/'+REPO+'/edit/main/'+path.split('/').map(encodeURIComponent).join('/');}
function updateCounts(){
 const n={completed:0,in_progress:0,not_started:0,blocked:0};
 state.items.forEach(x=>{n[x.audit_state]=(n[x.audit_state]||0)+1;});
 $('metric-total').textContent=state.items.length;
 $('metric-complete').textContent=n.completed;
 $('metric-progress').textContent=n.in_progress;
 $('metric-pending').textContent=n.not_started;
 $('metric-blocked').textContent=n.blocked;
}
function deriveStatus(item){
 const vals=Object.values(item.checklist||{});
 if(item.audit_state==='blocked')return 'blocked';
 if(vals.length&&vals.every(x=>x==='complete'))return 'completed';
 if(vals.some(x=>x==='complete'||x==='in_progress'))return 'in_progress';
 return 'not_started';
}
function render(){
 const query=$('audit-search').value.trim().toLowerCase(),group=$('audit-group').value,status=$('audit-state').value;
 const host=$('audit-list');host.replaceChildren();let shown=0;
 state.items.filter(x=>(!group||x.group===group)&&(!status||x.audit_state===status)&&(!query||x.path.toLowerCase().includes(query))).forEach(item=>{
  shown++;const card=document.createElement('article');card.className='audit-item';
  const header=document.createElement('header'),left=document.createElement('div'),right=document.createElement('div'),h=document.createElement('h3'),path=document.createElement('code'),stateText=document.createElement('p');
  h.textContent=item.path;path.textContent=item.path;stateText.className='audit-status';stateText.textContent=item.audit_state.replaceAll('_',' ');left.append(h,path,stateText);
  const src=document.createElement('a');src.href=sourceUrl(item.path);src.target='_blank';src.rel='noopener';src.textContent='Open source';
  const edit=document.createElement('a');edit.href=editUrl(item.path);edit.target='_blank';edit.rel='noopener';edit.textContent='Edit source';
  right.append(src,document.createTextNode(' · '),edit);header.append(left,right);card.append(header);
  const checks=document.createElement('div');checks.className='audit-checks';
  state.manifest.criteria.forEach(criterion=>{
   const label=document.createElement('label');label.className='audit-check';const input=document.createElement('input');input.type='checkbox';input.checked=item.checklist[criterion.id]==='complete';
   input.addEventListener('change',()=>{item.checklist[criterion.id]=input.checked?'complete':'pending';item.audit_state=deriveStatus(item);state.manifest.counts=counts();state.manifest.items=state.items;updateCounts();render();});
   const text=document.createElement('span');text.textContent=criterion.label;label.append(input,text);checks.append(label);
  });
  card.append(checks);
  const notes=document.createElement('label');notes.textContent='Audit notes / evidence ';const area=document.createElement('textarea');area.rows=2;area.style.width='100%';area.value=item.notes||'';area.addEventListener('change',()=>{item.notes=area.value;});notes.append(area);card.append(notes);
  host.append(card);
 });
 $('audit-empty').hidden=shown!==0;$('audit-result').textContent='Showing '+shown+' of '+state.items.length+' files. Checklist edits are local until exported and committed.';
 updateCounts();
}
function counts(){const n={completed:0,in_progress:0,not_started:0,blocked:0};state.items.forEach(x=>n[x.audit_state]=(n[x.audit_state]||0)+1);return {markdown_files:state.items.length,...n};}
async function init(){
 const response=await fetch(SOURCE,{cache:'no-store'});if(!response.ok)throw new Error('Could not load audit registry ('+response.status+')');
 state.manifest=await response.json();state.items=state.manifest.items;
 const groups=[...new Set(state.items.map(x=>x.group))].sort();groups.forEach(g=>{const o=document.createElement('option');o.value=g;o.textContent=g;$('audit-group').append(o);});
 state.manifest.criteria.forEach(c=>{const li=document.createElement('li');li.textContent=c.label;$('criteria-list').append(li);});
 $('audit-source').textContent='Source tree '+state.manifest.source_tree_sha+' · Generated '+state.manifest.generated_at+' · Scope: '+state.items.length+' tracked Markdown files.';
 ['audit-search','audit-group','audit-state'].forEach(id=>$(id).addEventListener(id==='audit-search'?'input':'change',render));
 $('download-audit').addEventListener('click',()=>{
  state.manifest.items=state.items;state.manifest.counts=counts();state.manifest.generated_at=new Date().toISOString().slice(0,10);
  const blob=new Blob([JSON.stringify(state.manifest,null,2)+'\n'],{type:'application/json'}),url=URL.createObjectURL(blob),a=document.createElement('a');
  a.href=url;a.download='markdown-requirements-audit.json';a.click();URL.revokeObjectURL(url);
 });
 updateCounts();render();
}
init().catch(error=>{$('audit-source').textContent='Audit registry unavailable: '+error.message;});
})();