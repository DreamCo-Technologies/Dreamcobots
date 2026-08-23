(function () {
  'use strict';

  const REPOSITORY = 'DreamCo-Technologies/Dreamcobots';
  const REPORT_URL = 'data/actions-health-report.json';
  const PROSPECTUS_URL = 'data/actions-prospectus.json';
  const benchmarkIndex = window.BUDDY_BENCHMARK_INDEX || { programs: [], summary: {} };
  const state = { report: null, prospectus: null, runs: new Map() };

  const byId = (id) => document.getElementById(id);
  const make = (tag, text, className) => {
    const node = document.createElement(tag);
    if (text !== undefined) node.textContent = text;
    if (className) node.className = className;
    return node;
  };
  const readable = (value) => String(value || '').replaceAll('_', ' ');

  function latestEvidence(workflow) {
    const run = state.runs.get(workflow.workflow);
    if (!run) return { key: 'unknown', label: 'Not loaded', run: null };
    if (run.status === 'in_progress' || run.status === 'queued') {
      return { key: 'running', label: readable(run.status), run };
    }
    if (run.conclusion === 'success') return { key: 'passing', label: 'Passing', run };
    if (['failure', 'cancelled', 'timed_out', 'action_required', 'startup_failure', 'stale'].includes(run.conclusion)) {
      return { key: 'attention', label: readable(run.conclusion), run };
    }
    return { key: 'unknown', label: readable(run.conclusion || run.status || 'unknown'), run };
  }

  function prospectusFor(id) {
    return state.prospectus?.controls?.find((item) => item.id === id) || null;
  }

  function benchmarkPrograms(workflow) {
    return (benchmarkIndex.programs || []).filter((program) =>
      (workflow.npm_scripts || []).some((script) => program.check_command?.includes(`npm run ${script}`))
    );
  }

  function buddyUpgradeUrl(workflow, evidence) {
    const repair = prospectusFor('repair');
    const upgrades = (workflow.upgrades || []).map((item, index) => `${index + 1}. ${item}`).join('\n');
    const runState = evidence.run
      ? `${evidence.label}; run ${evidence.run.id}; commit ${String(evidence.run.head_sha || '').slice(0, 12) || 'unknown'}`
      : 'No public live run was loaded.';
    const prompt = [
      `Debug and upgrade ${workflow.workflow}.`,
      `Purpose: ${workflow.purpose}.`,
      `Evidence: ${runState}.`,
      `Static findings: ${(workflow.errors || []).length} errors, ${(workflow.warnings || []).length} warnings.`,
      `Repository upgrades:\n${upgrades}`,
      `Repair policy: ${repair?.truth_boundary || 'reproduce first; smallest safe repair; targeted test; dependent regression; never fabricate evidence.'}`,
    ].join('\n');
    return `buddy.html?prompt=${encodeURIComponent(prompt)}`;
  }

  function renderProspectusCards() {
    const host = byId('actions-control-cards');
    host.replaceChildren();
    const controls = state.prospectus?.controls || [];
    controls.forEach((control) => {
      const card = make('article', undefined, 'actions-control-card');
      card.append(
        make('p', control.category || 'control', 'actions-kicker'),
        make('h3', control.name),
        make('p', control.purpose)
      );
      const grid = make('div', undefined, 'prospectus-meta');
      [['Progress', control.progress || 'configured'], ['Planning horizon', control.planning_horizon || 'Re-estimate from evidence'], ['Investor value', control.investor_value || 'Operational value']].forEach(([key, value]) => {
        const item = make('div');
        item.append(make('span', key), make('strong', value));
        grid.append(item);
      });
      card.append(grid);
      const details = make('details');
      details.append(make('summary', 'View upgrade plan + evidence rules'));
      details.append(make('h4', 'Upgrade plan'));
      const plan = make('ol');
      (control.upgrade_plan || []).forEach((step) => {
        const li = make('li');
        li.append(make('strong', step.step), make('span', ` — ${step.estimate}`));
        plan.append(li);
      });
      details.append(plan, make('h4', 'Evidence'));
      const evidenceList = make('ul');
      (control.evidence || []).forEach((item) => evidenceList.append(make('li', item)));
      details.append(evidenceList, make('h4', 'Success'), make('p', control.success || ''), make('h4', 'Fallback'), make('p', control.fallback || ''));
      card.append(details);
      host.append(card);
    });
    byId('prospectus-status').textContent = `${controls.length} Action controls documented with upgrade plans and planning ranges.`;
  }

  function showDetail(workflow) {
    const evidence = latestEvidence(workflow);
    const programs = benchmarkPrograms(workflow);
    const repair = prospectusFor('repair');
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
      ['Runner jobs', String(workflow.controls?.runner_jobs || 0)],
      ['Timeouts', String(workflow.controls?.job_timeouts_declared || 0)],
      ['Artifacts', workflow.controls?.artifacts_declared ? 'Declared' : 'Not declared'],
      ['Concurrency', workflow.controls?.concurrency_declared ? 'Declared' : 'Not declared'],
    ].forEach(([label, value]) => {
      const item = make('div');
      item.append(make('span', label), make('strong', value));
      summary.append(item);
    });
    body.append(summary, make('h3', 'What this action protects'), make('p', workflow.purpose));

    body.append(make('h3', 'Repository upgrade plan'));
    const upgrades = make('ol');
    (workflow.upgrades || []).forEach((item) => upgrades.append(make('li', item)));
    body.append(upgrades);

    if (repair) {
      body.append(make('h3', 'Repair planning timeframe'), make('p', repair.planning_horizon || 'Re-estimated after reproduction'));
      const repairPlan = make('ol');
      (repair.upgrade_plan || []).forEach((item) => {
        const li = make('li');
        li.append(make('strong', item.step), make('span', ` — ${item.estimate}`));
        repairPlan.append(li);
      });
      body.append(repairPlan);
    }

    body.append(make('h3', 'Repository evidence'));
    const evidenceList = make('div', undefined, 'detail-code-list');
    [...(workflow.npm_scripts || []).map((script) => `npm run ${script}`), ...(workflow.referenced_files || []), ...(workflow.actions || [])]
      .forEach((item) => evidenceList.append(make('code', item)));
    body.append(evidenceList, make('h3', 'Connected benchmark programs'));

    const list = make('ul', undefined, 'detail-benchmark-list');
    if (programs.length) {
      programs.forEach((program) => {
        const item = make('li');
        const link = make('a', program.name);
        link.href = program.public_page;
        item.append(link, document.createTextNode(`: ${readable(program.status)}`));
        list.append(item);
      });
    } else {
      list.append(make('li', 'Tracked by Actions health; no dedicated benchmark program mapped yet.'));
    }
    body.append(list);
    byId('workflow-detail').showModal();
  }

  function render() {
    if (!state.report) return;

    const query = byId('actions-search').value.trim().toLowerCase();
    const status = byId('actions-status-filter').value;
    const trigger = byId('actions-trigger-filter').value;

    const rows = state.report.findings.map((workflow) => ({ workflow, evidence: latestEvidence(workflow) }));
    const workflows = rows.filter(({ workflow, evidence }) => {
      const text = [workflow.display_name, workflow.purpose, workflow.workflow, ...(workflow.npm_scripts || []), ...(workflow.upgrades || [])].join(' ').toLowerCase();
      const matchesQuery = !query || text.includes(query);
      const matchesStatus = status === 'all' || evidence.key === status;
      const matchesTrigger = trigger === 'all' || (workflow.triggers || []).includes(trigger);
      return matchesQuery && matchesStatus && matchesTrigger;
    });

    const rank = { attention: 0, running: 1, unknown: 2, passing: 3 };
    workflows.sort((a, b) => {
      const statusDelta = rank[a.evidence.key] - rank[b.evidence.key];
      return statusDelta || a.workflow.display_name.localeCompare(b.workflow.display_name);
    });

    const list = byId('workflow-list');
    list.replaceChildren();
    workflows.forEach(({ workflow, evidence }) => {
      const item = make('article', undefined, 'workflow-item');
      const row = make('div', undefined, 'workflow-row');
      const identity = make('div', undefined, 'workflow-name');
      identity.append(make('strong', workflow.display_name), make('p', workflow.purpose));
      row.append(identity);

      const addCell = (label, value, statusClass) => {
        const cell = make('div', undefined, 'workflow-cell');
        const strong = make('strong', value, statusClass ? `workflow-status ${statusClass}` : undefined);
        cell.append(make('span', label), strong);
        row.append(cell);
      };

      addCell('Static evidence', readable(workflow.static_status), workflow.static_status === 'static_checks_passed' ? 'passing' : 'attention');
      addCell('Latest run', evidence.label, evidence.key);
      addCell('Controls', `${workflow.controls?.job_timeouts_declared || 0} timeout · ${workflow.controls?.artifacts_declared ? 'artifacts' : 'no artifact'}`);

      const commands = make('div', undefined, 'workflow-commands');
      const inspect = make('button', 'Prospectus', 'btn btn-outline');
      inspect.type = 'button';
      inspect.addEventListener('click', () => showDetail(workflow));
      const github = make('a', evidence.run ? 'Open run' : 'Open workflow', 'btn btn-outline');
      github.href = evidence.run?.html_url || workflow.github_url;
      github.target = '_blank';
      github.rel = 'noopener';
      const buddy = make('a', 'Plan with Buddy', 'btn btn-primary');
      buddy.href = buddyUpgradeUrl(workflow, evidence);
      commands.append(inspect, github, buddy);
      row.append(commands);

      item.append(row);
      const upgrades = make('details', undefined, 'workflow-upgrades');
      upgrades.append(make('summary', `${(workflow.upgrades || []).length} repository upgrade steps`));
      const plan = make('ol');
      (workflow.upgrades || []).forEach((upgrade) => plan.append(make('li', upgrade)));
      upgrades.append(plan);
      item.append(upgrades);
      list.append(item);
    });

    if (!workflows.length) list.append(make('p', 'No workflows match these filters.', 'actions-empty'));

    const allEvidence = state.report.findings.map(latestEvidence);
    byId('metric-workflows').textContent = String(state.report.workflow_count);
    byId('metric-static').textContent = `${state.report.workflow_count - state.report.critical_error_count}/${state.report.workflow_count}`;
    byId('metric-passing').textContent = String(allEvidence.filter((item) => item.key === 'passing').length);
    byId('metric-attention').textContent = String(allEvidence.filter((item) => item.key === 'attention').length + state.report.critical_error_count);
    byId('metric-upgrades').textContent = String(state.report.findings.reduce((sum, workflow) => sum + (workflow.upgrades || []).length, 0));
    byId('metric-benchmarks').textContent = String(benchmarkIndex.summary?.trackedBenchmarkSurfaces || 0);
    byId('workflow-result-count').textContent = `${workflows.length} of ${state.report.workflow_count} workflows shown`;
  }

  async function refreshRuns() {
    const button = byId('refresh-actions');
    button.disabled = true;
    button.textContent = 'Refreshing...';
    byId('actions-refresh-status').textContent = 'Reading public GitHub run evidence...';
    try {
      const response = await fetch(`https://api.github.com/repos/${REPOSITORY}/actions/runs?per_page=100`, {
        headers: { Accept: 'application/vnd.github+json' },
      });
      if (!response.ok) throw new Error(`GitHub returned ${response.status}`);
      const payload = await response.json();
      state.runs.clear();
      (payload.workflow_runs || []).forEach((run) => {
        if (run.path && !state.runs.has(run.path)) state.runs.set(run.path, run);
      });
      const seen = state.report.findings.filter((workflow) => state.runs.has(workflow.workflow)).length;
      byId('actions-refresh-status').textContent = `Public run evidence loaded for ${seen} workflows. Observed evidence is not a guarantee of future success.`;
    } catch (error) {
      byId('actions-refresh-status').textContent = `Static evidence is available. Public run refresh unavailable: ${error.message}`;
    } finally {
      button.disabled = false;
      button.textContent = 'Refresh GitHub Runs';
      render();
    }
  }

  const LOCAL_COMMANDS = {
    doctor: { label: 'Doctor', description: 'Check repository structure, runtime bindings, dependencies, and common configuration problems.' },
    test: { label: 'Tests', description: 'Run repository tests and preserve the first failing test.' },
    lint: { label: 'Lint', description: 'Run formatting, lint, imports, and types without modifying source.' },
    security: { label: 'Security', description: 'Run dependency and secret-boundary checks without exposing credentials.' },
    benchmark: { label: 'Local benchmark', description: 'Measure quality, latency, throughput, efficiency, and reliability on the current device.' },
    repair: { label: 'Repair planner', description: 'Turn observed failures into a smallest-safe repair plan with rollback and regression tests.' },
    pages: { label: 'Pages verification', description: 'Verify repository evidence and generated data are present in the public dashboard.' },
    bundle: { label: 'Device bundle', description: 'Validate downloadable launcher/package and local build artifacts.' },
  };

  function setupLocalCommands() {
    document.querySelectorAll('[data-local-command]').forEach((button) => {
      button.addEventListener('click', () => {
        const command = LOCAL_COMMANDS[button.dataset.localCommand];
        byId('actions-command-output').textContent = `${command.label}\n\n${command.description}\n\nSafe boundary: browser actions do not execute arbitrary shell commands. Use the downloadable Buddy launcher for approved local execution or open the GitHub workflow for remote execution.\n\nNext: evidence → root cause → smallest repair → targeted test → dependent regression.`;
      });
    });
  }

  async function initialize() {
    try {
      const [reportResponse, prospectusResponse] = await Promise.all([fetch(REPORT_URL), fetch(PROSPECTUS_URL)]);
      if (!reportResponse.ok) throw new Error(`Actions catalog returned ${reportResponse.status}`);
      state.report = await reportResponse.json();
      if (prospectusResponse.ok) state.prospectus = await prospectusResponse.json();
      renderProspectusCards();
      const triggerFilter = byId('actions-trigger-filter');
      [...new Set(state.report.findings.flatMap((workflow) => workflow.triggers || []))].sort().forEach((trigger) => {
        const option = document.createElement('option');
        option.value = trigger;
        option.textContent = trigger;
        triggerFilter.append(option);
      });
      render();
      setupLocalCommands();
      await refreshRuns();
    } catch (error) {
      byId('actions-refresh-status').textContent = `Actions catalog could not load: ${error.message}`;
      byId('workflow-list').append(make('p', 'Run the repository Actions health generator before opening this page.', 'actions-empty'));
      setupLocalCommands();
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
