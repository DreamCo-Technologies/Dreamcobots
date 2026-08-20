(function(){'use strict';
const host=document.getElementById('agi-goals-grid');if(!host)return;
const loadJson=(url)=>fetch(url).then(r=>{if(!r.ok)throw new Error(`${url} returned ${r.status}`);return r.json()});
const makeButton=(goal,action)=>{const a=document.createElement('a');a.className='btn btn-outline';a.textContent=action;a.href=`buddy.html?prompt=${encodeURIComponent(`Buddy mission: ${goal}. Action: ${action}. Choose the best specialist for this exact step using benchmark evidence, correctness, quality, reliability, speed, cost, safety, permissions and compatibility. Explain the plan and evidence before consequential actions.`)}`;return a};
const makeCard=(name,description,actions)=>{const card=document.createElement('article');card.className='agi-goal-card';const h=document.createElement('h3');h.textContent=name;const p=document.createElement('p');p.textContent=description;const box=document.createElement('div');box.className='agi-goal-actions';actions.slice(0,8).forEach(action=>box.appendChild(makeButton(name,action)));const maturity=document.createElement('p');maturity.className='agi-goal-maturity';maturity.textContent='Status: evidence required';card.append(h,p,box,maturity);return card};
Promise.all([loadJson('data/buddy-agi-actions-goals.json'),loadJson('data/buddy-repository-mission-map.json')]).then(([base,repo])=>{
  host.replaceChildren();
  base.goals.forEach(goal=>host.appendChild(makeCard(goal.name,goal.description,goal.actions)));
  const section=document.createElement('section');section.className='agi-repository-map';
  const heading=document.createElement('div');heading.className='actions-workspace-heading';heading.innerHTML='<div><p class="actions-kicker">Repository-wide mission map</p><h2>All approved Buddy goals, organized for action</h2></div><p>'+repo.categories.length+' categories • '+repo.categories.reduce((n,c)=>n+c.goals.length,0)+' mapped goals</p>';section.appendChild(heading);
  const grid=document.createElement('div');grid.className='agi-repository-category-grid';
  repo.categories.forEach(category=>{const card=document.createElement('article');card.className='agi-category-card';const h=document.createElement('h3');h.textContent=category.name;const p=document.createElement('p');p.textContent=`${category.goals.length} mission goals`;const actions=document.createElement('div');actions.className='agi-goal-actions';category.goals.forEach(goal=>actions.appendChild(makeButton(category.name,goal)));card.append(h,p,actions);grid.appendChild(card)});
  section.appendChild(grid);host.parentElement?.appendChild(section);
  const status=document.getElementById('agi-goals-status');if(status)status.textContent=`${base.goals.length} core areas + ${repo.categories.reduce((n,c)=>n+c.goals.length,0)} repository goals mapped`;
  const rule=document.getElementById('agi-mastery-rule');if(rule)rule.textContent=base.mastery_rule;
}).catch(e=>{host.textContent=`AGI mission registry unavailable: ${e.message}`});
})();