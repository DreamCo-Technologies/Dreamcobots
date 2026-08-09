const manufacturers = [
  {name:'Midwest Precision Works',location:'Illinois',processes:['CNC','Sheet Metal'],certs:['ISO 9001'],moq:'25+',lead:'2–4 weeks'},
  {name:'Great Lakes Plastics',location:'Wisconsin',processes:['Injection Molding','Tooling'],certs:['ISO 9001'],moq:'500+',lead:'4–7 weeks'},
  {name:'Heartland Assembly Co.',location:'Indiana',processes:['Assembly','Packaging','Light Manufacturing'],certs:['Supplier QA'],moq:'100+',lead:'2–5 weeks'}
];
const demoQuotes = [
  {name:'Midwest Precision Works',unit:'$6.80',moq:'250',lead:'21 days',tooling:'$350',fit:'92%'},
  {name:'Great Lakes Plastics',unit:'$4.10',moq:'1,000',lead:'38 days',tooling:'$2,400',fit:'79%'},
  {name:'Heartland Assembly Co.',unit:'$7.25',moq:'200',lead:'18 days',tooling:'$150',fit:'86%'}
];
const key = 'dreamco-manufacturing-rfqs-v1';
const $ = (id) => document.getElementById(id);
function drafts(){try{return JSON.parse(localStorage.getItem(key)||'[]')}catch{return[]}}
function renderCount(){$('rfqCount').textContent=String(drafts().length)}
function renderManufacturers(){
  $('manufacturers').innerHTML=manufacturers.map(m=>`<article class="card"><h3>${m.name}</h3><p class="muted">${m.location} • MOQ ${m.moq} • ${m.lead}</p><div>${m.processes.map(x=>`<span class="pill">${x}</span>`).join('')}</div><p class="muted">${m.certs.join(' • ')}</p><button class="btn secondary" type="button" onclick="alert('Demo profile only. Live verification evidence is required before contacting or awarding work.')">View verification</button></article>`).join('');
}
function renderQuotes(){
  $('quotes').innerHTML=demoQuotes.map(q=>`<tr><td>${q.name}</td><td>${q.unit}</td><td>${q.moq}</td><td>${q.lead}</td><td>${q.tooling}</td><td>${q.fit}</td></tr>`).join('');
  $('quoteCount').textContent=String(demoQuotes.length);
}
$('postRfq').addEventListener('click',()=> $('rfqDialog').showModal());
$('closeRfq').addEventListener('click',()=> $('rfqDialog').close());
$('loadDemo').addEventListener('click',renderQuotes);
$('rfqForm').addEventListener('submit',(event)=>{
  event.preventDefault();
  const data=Object.fromEntries(new FormData(event.currentTarget).entries());
  const rows=drafts();
  rows.push({...data,id:`rfq-${Date.now()}`,status:'draft-local-only',createdAt:new Date().toISOString()});
  localStorage.setItem(key,JSON.stringify(rows));
  event.currentTarget.reset();
  $('rfqDialog').close();
  renderCount();
  alert('RFQ saved locally as a draft. No manufacturer was contacted and nothing was submitted.');
});
renderManufacturers();
renderCount();