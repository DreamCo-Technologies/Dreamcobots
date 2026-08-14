(function(){'use strict';
async function loadJson(path){const r=await fetch(path);if(!r.ok)throw new Error(`${path}: ${r.status}`);return r.json();}
function el(tag,text,cls){const x=document.createElement(tag);if(text!==undefined)x.textContent=text;if(cls)x.className=cls;return x;}
function card(title,body,href,label){const c=el('article',undefined,'actions-control-card');c.id=`division-${title.toLowerCase().replace(/[^a-z0-9]+/g,'-')}`;c.append(el('p','Bot division','actions-kicker'),el('h3',title),el('p',body));if(href){const a=el('a',label||'Open prospectus','btn btn-outline');a.href=href;c.append(a);}return c;}
async function init(){
 const host=document.getElementById('bootcamp-command-center'); if(!host)return;
 try{
  const [boot,divisions]=await Promise.all([loadJson('data/onet-buddy-bootcamp.json'),loadJson('data/bot-division-prospectus.json')]);
  host.replaceChildren();host.append(el('p','Training + benchmark coverage','actions-kicker'),el('h2','Buddy Bootcamp: O*NET + repository mastery'),el('p',`Generated ${boot.counts.generated.toLocaleString()} sandbox cases across ${Object.keys(boot.counts.by_kind).length} O*NET/repository categories. Generated cases are not mastery evidence.`));
  const actions=el('div',undefined,'actions-command-buttons');
  [['Run O*NET Bootcamp','https://github.com/DreamCo-Technologies/Dreamcobots/actions/workflows/onet-buddy-bootcamp.yml','btn btn-primary'],['Open Bootcamp Plan','../docs/BUDDY_BOOTCAMP_ONET_PLAN.md','btn btn-outline'],['Open Generated Curriculum','data/onet-buddy-bootcamp.json','btn btn-outline'],['Refresh Actions Evidence','https://github.com/DreamCo-Technologies/Dreamcobots/actions','btn btn-outline']].forEach(([t,h,c])=>{const a=el('a',t,c);a.href=h;a.target='_blank';a.rel='noopener';actions.append(a);});host.append(actions);
  const stats=el('div',undefined,'actions-metrics');[['Generated cases',boot.counts.generated],['Raw mapped cases',boot.counts.raw],['Bot divisions',divisions.division_count],['Mastered cases',0]].forEach(([k,v])=>{const d=el('div');d.append(el('span',k),el('strong',String(v)));stats.append(d);});host.append(stats);
  const list=el('div',undefined,'actions-control-cards');divisions.divisions.forEach(d=>{const c=card(d.name,`${d.file_count} discovered files. Capabilities: ${d.capabilities.join(', ')}. Status: ${d.status}.`,d.prospectus_url,'Open division prospectus');c.id=`division-${d.id}`;list.append(c);});host.append(el('h3','Bot divisions'),list);
 }catch(e){host.replaceChildren(el('p',`Bootcamp evidence unavailable: ${e.message}`,'actions-empty'),el('p','Run the O*NET Bootcamp workflow to generate the public-safe curriculum artifact.'))}
}
init();})();
