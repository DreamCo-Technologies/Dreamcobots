(function () {
  'use strict';

  const REPOSITORY = 'DreamCo-Technologies/Dreamcobots';
  const REPORT_URL = 'data/actions-health-report.json';
  const benchmarkIndex = window.BUDDY_BENCHMARK_INDEX || { programs: [] };
  const state = { report: null, runs: new Map(), liveLoaded: false };
  const byId = (id) => document.getElementById(id);
  const readable = (value) => String(value || '').replaceAll('_', ' ');

  function make(tag, text, className) {
    const node = document.createElement(tag);
    if (text !== undefined) node.textContent = text;
    if (className) node.className = className;
    return node;
  }

  function latestEvidence(workflow) {
    const run = state.runs.get(workflow.workflow);
    if (!run) return { key: 'unknown', label: 'Not loaded', run: null };
    if (run.status === 'in_progress' || run.status === 'queued') return { key: 'running', label: readable(run.status), run };
    if (run.conclusion === 'success') return { key: 'passing', label: 'Passing', run };
    if (['failure', 'cancelled', 'timed_out', 'action_required', 'startup_failure'].includes(run.conclusion)) {
      return { key: 'attention', label: readable(run.conclusion), run };
    }
    return { key: 'unknown', label: readable(run.conclusion || run.status || 'unknown'), run };
  }

  function benchmarkPrograms(workflow) {
    return (benchmarkIndex.programs || []).filter((program) => workflow.npm_scripts.some((script) => program.check_command.includes(`npm run ${script}`)));
  }

  function buddyUpgradeUrl(workflow, evidence) {
    const upgrades = workflow.upgrades.map((item, index) => `${index + 1}. ${item}`).join('\n');
    const runState = evidence.run
      ? `${evidence.label}; run ${evidence.run.id}; commit ${String(evidence.run.head_sha || '').slice(0, 12) || 'unknown'}`
      : 'No public live run was loaded. Start with repository evidence.';
    const prompt = `Debug and upgrade the GitHub Actions workflow ${workflow.workflow}. Purpose: ${workflow.purpose} Latest evidence: ${runState}. Static findings: ${workflow.errors.length} errors and ${workflow.warnings.length} warnings. Upgrade plan:\n${upgrades}\nReproduce failures first, use a clean dependency install, run the smallest relevant tests, preserve logs, and stop before any external write or paid action that needs my approval.`;
    return `buddy.html?prompt=${encodeURIComponent(prompt)}`;
  }

  function addCell(row, label, value, statusClass) {
    const cell = make('div', undefined, 'workflow-cell');
    cell.append(make('span', label));
    if (statusClass) cell.append(make('strong', value, `workflow-status ${statusClass}`));
    else cell.append(make('strong', value));
    row.append(cell);
  }

  function showDetail(workflow) {
    const evidence = latestEvidence(workflow);
    const programs = benchmarkPrograms(workflow);
    byId('detail-path').textContent = workflow.workflow;
    byId('detail-title').textContent = workflow.display_name;
    byId('detail-github-link').href = evidence.run?.html_url || workflow.github_url;
    byId('detail-buddy-link').href = buddyUpgradeUrl(workflow, evidence);
    const body = byId('workflow-detail-body');
    body.replaceChildren();

    const summary = make('div', undefined, 'detail-summary');
    [
      ['Static status', readable(workflow.static_status)],
      ['Latest run', evidence.label],
      ['Runner jobs', String(workflow.controls.runner_jobs)],
      ['Timeouts', String(workflow.controls.job_timeouts_declared)],
      ['Artifacts', workflow.controls.artifacts_declared ? 'Declared' : 'Not declared'],
      ['Concurrency', workflow.controls.concurrency_declared ? 'Declared' : 'Not declared'],
    ].forEach(([label, value]) => {
      const item = make('div'); item.append(make('span', label), make('strong', value)); summary.append(item);
    });
    body.append(summary, make('h3', 'What this action protects'), make('p', workflow.purpose));

    body.append(make('h3', 'Next three upgrades'));
    const upgrades = make('ol'); workflow.upgrades.forEach((item) => upgrades.append(make('li', item))); body.append(upgrades);

    body.append(make('h3', 'Repository evidence'));
    const evidenceList = make('div', undefined, 'detail-code-list');
    const evidenceValues = [...workflow.npm_scripts.map((script) => `npm run ${script}`), ...workflow.referenced_files, ...workflow.actions];
    (evidenceValues.length ? evidenceValues : ['No executable references were detected by the static scanner.']).forEach((item) => evidenceList.append(make('code', item)));
    body.append(evidenceList);

    body.append(make('h3', 'Connected benchmark programs'));
    const programList = make('ul', undefined, 'detail-benchmark-list');
    if (programs.length) {
      programs.forEach((program) => {
        const item = make('li'); const link = make('a', program.name); link.href = program.public_page; item.append(link, document.createTextNode(`: ${readable(program.status)}`)); programList.append(item);
      });
    } else {
      programList.append(make('li', 'This workflow is tracked by Actions health; no dedicated benchmark program is mapped yet.'));
    }
    body.append(programList);
    byId('workflow-detail').showModal();
  }

  function render() {
    if (!state.report) return;
    const query = byId('actions-search').value.trim().toLowerCase();
    const status = byId('actions-status-filter').value;
    const trigger = byId('actions-trigger-filter').value;
    const workflows = state.report.findings
      .map((workflow) => ({ workflow, evidence: latestEvidence(workflow) }))
      .filter(({ workflow, evidence }) => {
        const searchText = `${workflow.display_name} ${workflow.purpose} ${workflow.workflow} ${workflow.npm_scripts.join(' ')} ${workflow.upgrades.join(' ')}`.toLowerCase();
        return (!query || searchText.includes(query))
          && (status === 'all' || evidence.key === status)
          && (trigger === 'all' || workflow.triggers.includes(trigger));
      })
      .sort((a, b) => {
        const rank = { attention: 0, running: 1, unknown: 2, passing: 3 };
        return rank[a.evidence.key] - rank[b.evidence.key] || a.workflow.display_name.localeCompare(b.workflow.display_name);
      });

    const list = byId('workflow-list'); list.replaceChildren();
    workflows.forEach(({ workflow, evidence }) => {
      const item = make('article', undefined, 'workflow-item');
      item.dataset.attention = String(evidence.key === 'attention' || workflow.static_status === 'blocked');
      const row = make('div', undefined, 'workflow-row');
      const identity = make('div', undefined, 'workflow-name');
      identity.append(make('strong', workflow.display_name), make('p', workflow.purpose));
      const triggers = make('div', undefined, 'workflow-triggers');
      workflow.triggers.forEach((value) => triggers.append(make('span', value)));
      identity.append(triggers); row.append(identity);
      addCell(row, 'Static evidence', readable(workflow.static_status), workflow.static_status === 'static_checks_passed' ? 'passing' : 'attention');
      addCell(row, 'Latest run', evidence.label, evidence.key);
      addCell(row, 'Controls', `${workflow.controls.job_timeouts_declared} timeout · ${workflow.controls.artifacts_declared ? 'artifacts' : 'no artifact'}`);

      const commands = make('div', undefined, 'workflow-commands');
      const inspect = make('button', 'Inspect', 'btn btn-outline'); inspect.type = 'button'; inspect.addEventListener('click', () => showDetail(workflow));
      const github = make('a', evidence.run ? 'Open run' : 'Open workflow', 'btn btn-outline'); github.href = evidence.run?.html_url || workflow.github_url; github.target = '_blank'; github.rel = 'noopener';
      const buddy = make('a', 'Ask Buddy', 'btn btn-primary'); buddy.href = buddyUpgradeUrl(workflow, evidence);
      commands.append(inspect, github, buddy); row.append(commands); item.append(row);

      const upgrades = make('details', undefined, 'workflow-upgrades');
      upgrades.append(make('summary', `${workflow.upgrades.length} upgrades for this workflow`));
      const plan = make('ol'); workflow.upgrades.forEach((upgrade) => plan.append(make('li', upgrade))); upgrades.append(plan); item.append(upgrades);
      list.append(item);
    });
    if (!workflows.length) list.append(make('p', 'No workflows match these filters.', 'actions-empty'));

    const allEvidence = state.report.findings.map(latestEvidence);
    byId('metric-workflows').textContent = String(state.report.workflow_count);
    byId('metric-static').textContent = `${state.report.workflow_count - state.report.critical_error_count}/${state.report.workflow_count}`;
    byId('metric-passing').textContent = String(allEvidence.filter((item) => item.key === 'passing').length);
    byId('metric-attention').textContent = String(allEvidence.filter((item) => item.key === 'attention').length + state.report.critical_error_count);
    byId('metric-upgrades').textContent = String(state.report.findings.reduce((sum, workflow) => sum + workflow.upgrades.length, 0));
    byId('metric-benchmarks').textContent = String(benchmarkIndex.summary?.trackedBenchmarkSurfaces || 0);
    byId('workflow-result-count').textContent = `${workflows.length} of ${state.report.workflow_count} workflows shown`;
  }

  async function refreshRuns() {
    const button = byId('refresh-actions'); button.disabled = true; button.textContent = 'Refreshing...';
    byId('actions-refresh-status').textContent = 'Reading public GitHub run evidence...';
    try {
      const response = await fetch(`https://api.github.com/repos/${REPOSITORY}/actions/runs?per_page=100`, { headers: { Accept: 'application/vnd.github+json' } });
      if (!response.ok) throw new Error(`GitHub returned ${response.status}`);
      const payload = await response.json();
      state.runs.clear();
      (payload.workflow_runs || []).forEach((run) => {
        if (run.path && !state.runs.has(run.path)) state.runs.set(run.path, run);
      });
      state.liveLoaded = true;
      const seen = state.report.findings.filter((workflow) => state.runs.has(workflow.workflow)).length;
      byId('actions-refresh-status').textContent = `Public run evidence loaded for ${seen} workflows. Status reflects each workflow's latest returned run, not a guarantee of future success.`;
    } catch (error) {
      byId('actions-refresh-status').textContent = `Static evidence is available. Public run refresh was unavailable: ${error.message}`;
    } finally {
      button.disabled = false; button.textContent = 'Refresh runs'; render();
    }
  }

  async function initialize() {
    try {
      const response = await fetch(REPORT_URL);
      if (!response.ok) throw new Error(`Actions catalog returned ${response.status}`);
      state.report = await response.json();
      const triggerFilter = byId('actions-trigger-filter');
      [...new Set(state.report.findings.flatMap((workflow) => workflow.triggers))].sort().forEach((trigger) => {
        const option = document.createElement('option'); option.value = trigger; option.textContent = trigger; triggerFilter.append(option);
      });
      render();
      await refreshRuns();
    } catch (error) {
      byId('actions-refresh-status').textContent = `Actions catalog could not load: ${error.message}`;
      byId('workflow-list').append(make('p', 'Run the repository Actions health generator before opening this page.', 'actions-empty'));
    }
  }

  byId('actions-search').addEventListener('input', render);
  byId('actions-status-filter').addEventListener('change', render);
  byId('actions-trigger-filter').addEventListener('change', render);
  byId('refresh-actions').addEventListener('click', refreshRuns);
  byId('close-workflow-detail').addEventListener('click', () => byId('workflow-detail').close());
  byId('workflow-detail').addEventListener('click', (event) => {
    if (event.target === byId('workflow-detail')) byId('workflow-detail').close();
  });
  initialize();
})();
