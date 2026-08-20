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
const reviewActions=[
 ['Review before coding','Inspect intent, repository health, architecture, risk, dependencies, prior incidents and acceptance criteria before implementation.'],
 ['Review latest commit','Review the newest commit incrementally and identify new risk before it accumulates.'],
 ['Run review council','Route the exact task through the smallest set of evidence-matched specialist reviewers, in parallel or sequence as needed.'],
 ['Security review','Threat-model changed behavior, secrets, permissions, dependencies and attack surface.'],
 ['Dependency review','Check dependency changes, provenance, compatibility, vulnerabilities and blast radius.'],
 ['Test-gap review','Find missing tests and propose targeted regression coverage.'],
 ['Benchmark review','Compare relevant quality, speed, reliability and regression evidence.'],
 ['Architecture review','Check boundaries, contracts, coupling, duplication and long-term maintainability.'],
 ['Explain finding','Turn a finding into a beginner-friendly explanation with evidence and verification steps.'],
 ['Verify fix','Re-check the exact finding after a change and require evidence before marking it resolved.'],
 ['Compare previous review','Detect recurring findings and whether review quality is improving.'],
 ['Find duplicate finding','Cluster semantically duplicate findings into one canonical issue.'],
 ['Generate regression test','Convert a confirmed defect into durable automated coverage.'],
 ['Build repair plan','Create the smallest safe repair plan and route each step to the best specialist.'],
 ['Show evidence','Expose source locations, tests, logs, benchmark runs and provenance behind conclusions.'],
 ['Show reviewer disagreement','Surface conflicting specialist opinions instead of hiding disagreement.'],
 ['Audit Buddy review','Measure precision, recall, false positives, misses, severity calibration and developer acceptance.'],
 ['Promote automation tier','Evaluate whether task-specific evidence supports a higher automation tier.'],
 ['Roll back automation tier','Reduce autonomy when evidence shows degraded reliability or policy risk.']
];
const sleep=(ms)=>new Promise(r=>setTimeout(r,ms));
function reviewLink(label,description){const link=document.createElement('a');link.className='btn btn-outline';link.textContent=label;link.href='buddy.html?prompt='+encodeURIComponent(`Buddy PR review action: ${label}. ${description} Use evidence-driven multi-agent routing. Inspect existing repository evidence first. Never claim a finding without evidence. Preserve finding IDs, provenance, confidence and verification requirements. Keep consequential writes, merges and permission changes approval-gated unless the repository's explicit automation policy authorizes them.`);link.title=description;return link}
async function load(){
 const results=await Promise.allSettled(manifests.map(url=>fetch(url).then(r=>r.ok?r.json():null)));
 const actions=[];results.forEach(result=>{if(result.status==='fulfilled'&&result.value){(result.value.actions||[]).forEach(item=>actions.push(item));}});
 for(let i=0;i<20&&!document.getElementById('actions-control-cards');i++)await sleep(100);
 const host=document.getElementById('actions-control-cards');if(!host)return;
 const section=document.createElement('section');section.className='buddy-growth-lab';
 const heading=document.createElement('div');heading.className='buddy-growth-heading';heading.innerHTML='<div><p class="actions-kicker">Buddy growth lab</p><h3>Train, test, teach, recover, mature and review PRs</h3></div><span>'+actions.length+' growth controls + '+reviewActions.length+' PR review controls</span>';section.appendChild(heading);
 const review=document.createElement('div');review.className='buddy-growth-group';const reviewTitle=document.createElement('h4');reviewTitle.textContent='Professional Pull Request Review';review.appendChild(reviewTitle);const reviewButtons=document.createElement('div');reviewButtons.className='buddy-growth-buttons';reviewActions.forEach(([label,description])=>reviewButtons.appendChild(reviewLink(label,description)));review.appendChild(reviewButtons);section.appendChild(review);
 const policy=document.createElement('div');policy.className='buddy-growth-policy';policy.innerHTML='<strong>Review lifecycle:</strong> Before PR → During development → Submission → After changes → Post-merge learning. <strong>Automation:</strong> Observe → Suggest → Assist → Guarded automation → Trusted automation → Scaled review service. Promotion requires measured evidence; no tier may bypass required checks or repository authorization.';section.appendChild(policy);
 const groups=document.createElement('div');groups.className='buddy-growth-groups';const buckets={Learning:[],Evaluation:[],Recovery:[],Writing:[],Engineering:[]};actions.forEach(action=>{let key='Learning';if(/benchmark|mastery|evaluation|transfer|regression/i.test(action.id+' '+action.label))key='Evaluation';if(/failure|repair|regression|memory|remediation/i.test(action.id+' '+action.label))key='Recovery';if(/book|write|synthesis|example|exercise/i.test(action.id+' '+action.label))key='Writing';if(/specialist|sandbox|audit|approval|efficiency|budget/i.test(action.id+' '+action.label))key='Engineering';buckets[key].push(action);});Object.entries(buckets).forEach(([name,items])=>{if(!items.length)return;const group=document.createElement('div');group.className='buddy-growth-group';const title=document.createElement('h4');title.textContent=name;group.appendChild(title);const buttons=document.createElement('div');buttons.className='buddy-growth-buttons';items.forEach(action=>{const link=document.createElement('a');link.className='btn btn-outline';link.textContent=action.label;link.href='buddy.html?prompt='+encodeURIComponent(`Buddy growth action: ${action.label}. ${action.description||''} Use the best specialist for each step, inspect existing repository evidence first, explain the proposed plan, run bounded tests, preserve provenance, record failures and only promote improvements after repeatable evidence.`);link.title=action.description||'';buttons.appendChild(link);});group.appendChild(buttons);groups.appendChild(group);});section.appendChild(groups);host.parentElement?.insertBefore(section,host);
}
load().catch(()=>{});
})();