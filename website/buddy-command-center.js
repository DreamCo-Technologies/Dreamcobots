(() => {
  const $ = (id) => document.getElementById(id);
  const task = $('cc-task');
  const log = $('cc-log');
  const status = $('cc-status');
  const caps = $('cc-capabilities');
  const contract = $('cc-contract');
  const historyKey = 'dreamco.buddy.command-center.history.v1';
  const catalog = [
    ['Task Understanding','Turns natural language into a definition of done.'],
    ['Software Engineering','Design, code, tests, debugging and refactoring.'],
    ['Research','Find, compare and ground information with provenance.'],
    ['Data Analysis','Transform, analyze, visualize and validate data.'],
    ['Automation','Convert repeatable work into bounded workflows.'],
    ['Benchmarking','Measure quality against explicit baselines and criteria.'],
    ['Sandboxing','Isolate experiments from stable state.'],
    ['Recovery','Checkpoint failures and choose a new strategy.'],
    ['Open Model Engineering','Evaluate and improve locally available open models.'],
    ['Professional Training','Map tasks to skills, subjects and evidence.']
  ];

  function write(line) {
    const stamp = new Date().toLocaleTimeString();
    log.textContent += `[${stamp}] ${line}\n`;
    log.scrollTop = log.scrollHeight;
    const history = JSON.parse(localStorage.getItem(historyKey) || '[]');
    history.push({ stamp, line });
    localStorage.setItem(historyKey, JSON.stringify(history.slice(-200)));
  }

  function renderCaps(selected = []) {
    caps.innerHTML = catalog.map(([name, desc]) => `<div class="cc-card"><strong>${selected.includes(name) ? '✓ ' : ''}${name}</strong><span>${desc}</span></div>`).join('');
  }

  function infer(text) {
    const s = text.toLowerCase();
    const selected = new Set(['Task Understanding']);
    if (/code|app|software|website|api|program|debug|script/.test(s)) selected.add('Software Engineering');
    if (/research|look up|study|learn|source|compare/.test(s)) selected.add('Research');
    if (/data|csv|excel|sql|chart|analy/.test(s)) selected.add('Data Analysis');
    if (/automat|repeat|workflow|schedule|monitor/.test(s)) selected.add('Automation');
    if (/benchmark|measure|score|compare/.test(s)) selected.add('Benchmarking');
    selected.add('Sandboxing');
    selected.add('Recovery');
    return [...selected];
  }

  $('cc-plan').addEventListener('click', () => {
    const text = task.value.trim();
    if (!text) { status.textContent = 'Enter a job or task first.'; status.className = 'cc-status warn'; return; }
    const selected = infer(text);
    renderCaps(selected);
    const criteria = [
      'Clear definition of done',
      'Inputs and constraints documented',
      'Selected capabilities mapped',
      'Evidence required before completion',
      'Failure checkpoint and recovery path'
    ];
    contract.value = JSON.stringify({ task: text, acceptance_criteria: criteria, capabilities: selected, benchmark_id: `local-${Date.now()}`, runner: 'local', network: 'off-by-default', evidence_required: true }, null, 2);
    status.textContent = `Planned locally: ${selected.length} capabilities. No external model call was made.`;
    status.className = 'cc-status good';
    write(`PLANNED task with capabilities: ${selected.join(', ')}`);
  });

  $('cc-benchmark').addEventListener('click', () => {
    const text = task.value.trim();
    if (!text) { status.textContent = 'Enter a job before creating a benchmark.'; status.className = 'cc-status warn'; return; }
    const id = `local-benchmark-${Date.now()}`;
    contract.value = JSON.stringify({ benchmark_id: id, task: text, baseline: 'required', acceptance_criteria: ['defined before execution'], before_after: true, failure_cases: true, reproduction_metadata: true }, null, 2);
    status.textContent = `Benchmark contract created locally: ${id}`;
    status.className = 'cc-status good';
    write(`CREATED benchmark contract ${id}; execution not claimed.`);
  });

  $('cc-clear').addEventListener('click', () => { task.value = ''; renderCaps(); status.textContent = 'Ready — local planning mode.'; status.className = 'cc-status'; write('CLEARED current task.'); });

  $('cc-copy').addEventListener('click', async () => { await navigator.clipboard.writeText(contract.value); status.textContent = 'Contract copied to clipboard.'; status.className = 'cc-status good'; write('COPIED contract.'); });

  $('cc-download').addEventListener('click', () => {
    const blob = new Blob([contract.value], { type: 'application/json' });
    const a = document.createElement('a'); a.href = URL.createObjectURL(blob); a.download = 'buddy-task-contract.json'; a.click(); URL.revokeObjectURL(a.href);
    write('SAVED local task contract.');
  });

  renderCaps();
  const prior = JSON.parse(localStorage.getItem(historyKey) || '[]');
  if (prior.length) log.textContent += prior.slice(-20).map(x => `[${x.stamp}] ${x.line}`).join('\n') + '\n';
})();
