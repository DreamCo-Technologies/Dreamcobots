(function () {
  'use strict';

  const catalog = window.BUDDY_MODEL_PROGRESS_CENTER || {
    summary: {}, taskCategories: [], readinessGates: [], gateCoverage: {}, councils: [],
    benchmarkRoadmaps: [], bootcampTracks: [], datasetPackages: [], workstreams: [],
  };
  const byId = (id) => document.getElementById(id);
  let councilMode = 'free';

  function text(id, value) {
    const element = byId(id);
    if (element) element.textContent = String(value);
  }

  function titleCase(value) {
    return String(value || '').replaceAll('_', ' ').replace(/\b\w/g, (letter) => letter.toUpperCase());
  }

  function buddyHref(prompt) {
    return `buddy.html?prompt=${encodeURIComponent(prompt)}`;
  }

  function populateSummary() {
    const summary = catalog.summary || {};
    text('metric-model-targets', Number(summary.modelTargets || 0).toLocaleString());
    text('metric-target-coverage', `${Number(summary.categorized || 0).toLocaleString()} categorized`);
    text('metric-provider-sources', Number(summary.providerSources || 0).toLocaleString());
    text('metric-councils', Number(summary.councils || 0).toLocaleString());
    text('metric-benchmarks', Number(summary.benchmarkRoadmaps || 0).toLocaleString());
    text('metric-datasets', Number(summary.datasetPackageTemplates || 0).toLocaleString());
    text('metric-live', Number(summary.liveBenchmarked || 0).toLocaleString());
    text('connection-truth-copy', `${Number(summary.catalogReady || 0).toLocaleString()} targets pass the local catalog contract and ${Number(summary.setupPathsReady || 0).toLocaleString()} have setup paths. ${Number(summary.exactVersionsVerified || 0).toLocaleString()} exact versions, ${Number(summary.adapterSandboxesPassed || 0).toLocaleString()} provider adapters, and ${Number(summary.liveBenchmarked || 0).toLocaleString()} live model benchmarks are currently evidenced. Those missing gates remain visible below.`);
  }

  function renderReadiness() {
    const container = byId('readiness-gates');
    const total = Number(catalog.summary?.modelTargets || 500);
    container.replaceChildren();
    (catalog.readinessGates || []).forEach((gate) => {
      const count = Number(catalog.gateCoverage?.[gate.id] || 0);
      const row = document.createElement('div');
      row.className = 'readiness-gate';
      row.title = gate.description;
      const label = document.createElement('strong');
      label.textContent = gate.label;
      const track = document.createElement('div');
      track.className = 'readiness-track';
      const fill = document.createElement('div');
      fill.className = `readiness-fill${count < total ? ' incomplete' : ''}`;
      fill.style.width = `${Math.min(100, Math.round((count / total) * 100))}%`;
      track.append(fill);
      const value = document.createElement('span');
      value.textContent = `${count.toLocaleString()} / ${total.toLocaleString()}`;
      row.append(label, track, value);
      container.append(row);
    });
  }

  function populateTaskSelectors() {
    const councilSelect = byId('council-task');
    const datasetSelect = byId('dataset-task');
    (catalog.taskCategories || []).forEach((task) => {
      const option = document.createElement('option');
      option.value = task;
      option.textContent = task;
      councilSelect.append(option);
      datasetSelect.append(option.cloneNode(true));
    });
  }

  function renderCouncil() {
    const task = byId('council-task').value || catalog.taskCategories?.[0];
    const council = (catalog.councils || []).find((item) => item.task === task && item.mode === councilMode);
    const body = byId('council-rows');
    body.replaceChildren();
    if (!council) {
      text('council-status', 'No council found');
      return;
    }
    text('council-status', `${task} · ${councilMode === 'free' ? 'free-first' : 'premium'} · ${council.members.length} seats`);
    text('council-basis', council.selectionBasis);
    byId('council-buddy-link').href = buddyHref(`Use the ${task} ${councilMode} model council for my task. Start with a normal chatbot conversation, show the top 20 candidates and current evidence, and do not call a paid provider or external model without my exact approval.`);
    council.members.forEach((member) => {
      const row = document.createElement('tr');
      const rank = document.createElement('td');
      rank.textContent = String(member.rank).padStart(2, '0');
      const candidate = document.createElement('td');
      const candidateName = document.createElement('span');
      candidateName.className = 'candidate-name';
      candidateName.textContent = member.name;
      candidate.append(candidateName, document.createTextNode(member.category));
      const provider = document.createElement('td');
      provider.textContent = member.provider;
      const access = document.createElement('td');
      const accessLabel = document.createElement('span');
      accessLabel.className = 'access-label';
      accessLabel.textContent = titleCase(member.accessLane);
      access.append(accessLabel);
      const fit = document.createElement('td');
      fit.textContent = member.declaredBestFor;
      const readiness = document.createElement('td');
      const readinessLabel = document.createElement('span');
      readinessLabel.className = 'status-label';
      readinessLabel.textContent = titleCase(member.readiness);
      readiness.append(readinessLabel);
      row.append(rank, candidate, provider, access, fit, readiness);
      body.append(row);
    });
    renderBootcamp(task);
  }

  function renderBenchmarks() {
    const container = byId('benchmark-roadmaps');
    container.replaceChildren();
    (catalog.benchmarkRoadmaps || []).forEach((roadmap) => {
      const article = document.createElement('article');
      article.className = 'benchmark-roadmap';
      const status = document.createElement('span');
      status.textContent = titleCase(roadmap.status);
      const title = document.createElement('h3');
      title.textContent = roadmap.label;
      const details = document.createElement('dl');
      [
        ['Modality', roadmap.modality],
        ['Baseline setup', roadmap.baselineSetupEstimate],
        ['Gap cycle', roadmap.firstGapCycleEstimate],
        ['Target date', roadmap.benchmarkReachEstimate],
      ].forEach(([label, value]) => {
        const row = document.createElement('div');
        const term = document.createElement('dt');
        term.textContent = label;
        const description = document.createElement('dd');
        description.textContent = value;
        row.append(term, description);
        details.append(row);
      });
      const path = document.createElement('details');
      const summary = document.createElement('summary');
      summary.textContent = 'Gap-closing path';
      const list = document.createElement('ol');
      roadmap.path.forEach((step) => {
        const item = document.createElement('li');
        item.textContent = step;
        list.append(item);
      });
      path.append(summary, list);
      article.append(status, title, details, path);
      container.append(article);
    });
  }

  function renderBootcamp(task) {
    const track = (catalog.bootcampTracks || []).find((item) => item.task === task);
    if (!track) return;
    const steps = byId('bootcamp-steps');
    steps.replaceChildren();
    (track.path || catalog.bootcampPath || []).forEach((step) => {
      const item = document.createElement('li');
      item.textContent = step;
      steps.append(item);
    });
    text('bootcamp-track-name', track.task);
    text('bootcamp-track-status', `${titleCase(track.status)}. ${track.graduationRule}`);
    const suites = byId('bootcamp-suites');
    suites.replaceChildren();
    track.benchmarkSuites.forEach((suite) => {
      const chip = document.createElement('span');
      chip.textContent = titleCase(suite);
      suites.append(chip);
    });
    byId('bootcamp-buddy-link').href = buddyHref(`Prepare the ${task} Buddy Bootcamp path. Use synthetic or rights-cleared fixtures, capture a baseline, keep network and spending off, show every failed or blocked gate, and stop before training weights or releasing a model without my exact approval.`);
  }

  function renderWorkstreams() {
    const container = byId('workstream-list');
    container.replaceChildren();
    (catalog.workstreams || []).forEach((workstream) => {
      const article = document.createElement('article');
      article.className = 'workstream-item';
      article.dataset.kind = workstream.kind;
      const status = document.createElement('span');
      status.textContent = `${workstream.kind} · ${titleCase(workstream.status)}`;
      const title = document.createElement('h3');
      title.textContent = workstream.label;
      const description = document.createElement('p');
      description.textContent = workstream.description;
      article.append(status, title, description);
      container.append(article);
    });
  }

  function renderDatasets() {
    const query = byId('dataset-search').value.trim().toLowerCase();
    const task = byId('dataset-task').value;
    const filtered = (catalog.datasetPackages || []).filter((item) => {
      const taskMatch = task === 'all' || item.taskCategory === task;
      const searchMatch = !query || `${item.name} ${item.taskCategory} ${item.packageType} ${item.intendedUse}`.toLowerCase().includes(query);
      return taskMatch && searchMatch;
    });
    text('dataset-count', `${filtered.length} of ${catalog.datasetPackages.length} templates`);
    const container = byId('dataset-list');
    container.replaceChildren();
    filtered.forEach((item) => {
      const article = document.createElement('article');
      article.className = 'dataset-item';
      const copy = document.createElement('div');
      const title = document.createElement('h3');
      title.textContent = item.name;
      const description = document.createElement('p');
      description.textContent = `${item.intendedUse} Next gate: ${item.nextGate}`;
      copy.append(title, description);
      const metadata = document.createElement('aside');
      const state = document.createElement('strong');
      state.textContent = titleCase(item.status);
      const records = document.createElement('span');
      records.textContent = `${item.recordsIncluded} records · ${item.benchmarkSuites.length} suites`;
      metadata.append(state, records);
      article.append(copy, metadata);
      container.append(article);
    });
  }

  document.querySelectorAll('[data-council-mode]').forEach((button) => {
    button.addEventListener('click', () => {
      councilMode = button.dataset.councilMode;
      document.querySelectorAll('[data-council-mode]').forEach((item) => {
        const active = item === button;
        item.classList.toggle('active', active);
        item.setAttribute('aria-pressed', String(active));
      });
      renderCouncil();
    });
  });
  byId('council-task').addEventListener('change', renderCouncil);
  byId('dataset-search').addEventListener('input', renderDatasets);
  byId('dataset-task').addEventListener('change', renderDatasets);
  byId('export-progress').addEventListener('click', () => {
    const blob = new Blob([JSON.stringify(catalog, null, 2)], { type: 'application/json' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = 'buddy-model-progress-center.json';
    link.click();
    URL.revokeObjectURL(link.href);
  });

  populateSummary();
  renderReadiness();
  populateTaskSelectors();
  renderCouncil();
  renderBenchmarks();
  renderWorkstreams();
  renderDatasets();
})();
