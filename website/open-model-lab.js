(function () {
  'use strict';

  const catalog = window.BUDDY_OPEN_MODEL_CODING_LAB || {
    summary: {}, model_families: [], coding_tasks: [], local_runtimes: [], evidence_fields: [],
  };
  const selected = new Set(catalog.model_families.slice(0, 3).map((model) => model.id));
  let comparisonPlan = null;
  let sourcePlan = null;
  const byId = (id) => document.getElementById(id);
  const escapeHtml = (value) => String(value)
    .replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;').replaceAll("'", '&#39;');

  function makeOption(value, label) {
    const option = document.createElement('option');
    option.value = value;
    option.textContent = label;
    return option;
  }

  function renderSummary() {
    byId('open-model-count').textContent = Number(catalog.summary.model_families || 0).toLocaleString();
    byId('open-region-count').textContent = Number(catalog.summary.developer_regions || 0).toLocaleString();
    byId('open-task-count').textContent = Number(catalog.summary.coding_tasks || 0).toLocaleString();
    byId('open-live-count').textContent = Number(catalog.summary.live_models_called || 0).toLocaleString();
  }

  function renderFilters() {
    [...new Set(catalog.model_families.map((model) => model.developer_region))].sort()
      .forEach((region) => byId('open-region-filter').append(makeOption(region, region)));
    [...new Set(catalog.model_families.map((model) => model.access))].sort()
      .forEach((access) => byId('open-access-filter').append(makeOption(access, access.replaceAll('_', ' '))));
    catalog.local_runtimes.forEach((runtime) => byId('open-runtime').append(makeOption(runtime.id, runtime.label)));
  }

  function visibleModels() {
    const query = byId('open-model-search').value.trim().toLowerCase();
    const region = byId('open-region-filter').value;
    const access = byId('open-access-filter').value;
    return catalog.model_families.filter((model) => {
      const haystack = [
        model.label, model.developer, model.developer_region, model.access,
        model.license, model.hardware_note, ...model.coding_fit,
      ].join(' ').toLowerCase();
      return (!query || haystack.includes(query))
        && (region === 'all' || model.developer_region === region)
        && (access === 'all' || model.access === access);
    });
  }

  function renderModels() {
    const models = visibleModels();
    byId('open-model-grid').innerHTML = models.map((model) => `
      <article class="open-model-card ${selected.has(model.id) ? 'selected' : ''}">
        <header>
          <div><h3>${escapeHtml(model.label)}</h3><p class="developer">${escapeHtml(model.developer)} · ${escapeHtml(model.developer_region)}</p></div>
          <input type="checkbox" data-open-model="${escapeHtml(model.id)}" aria-label="Compare ${escapeHtml(model.label)}" ${selected.has(model.id) ? 'checked' : ''} />
        </header>
        <div class="open-model-tags"><span>${escapeHtml(model.access.replaceAll('_', ' '))}</span>${model.coding_fit.slice(0, 2).map((fit) => `<span>${escapeHtml(fit)}</span>`).join('')}</div>
        <p class="license">${escapeHtml(model.license)}</p>
        <a href="${escapeHtml(model.official_source)}" target="_blank" rel="noopener noreferrer">Official source</a>
      </article>`).join('');
    byId('open-model-grid').querySelectorAll('[data-open-model]').forEach((input) => input.addEventListener('change', (event) => {
      const id = event.currentTarget.dataset.openModel;
      if (event.currentTarget.checked) selected.add(id); else selected.delete(id);
      byId('open-selected-count').textContent = selected.size.toLocaleString();
      renderModels();
    }));
    byId('open-model-status').textContent = `Showing ${models.length} cataloged families. Catalog metadata is not a benchmark score.`;
    byId('open-selected-count').textContent = selected.size.toLocaleString();
  }

  function renderTasks() {
    byId('open-task-options').innerHTML = catalog.coding_tasks.map((task) => `
      <label><input type="checkbox" value="${escapeHtml(task.id)}" checked />${escapeHtml(task.label)}</label>`).join('');
  }

  function selectedTaskIds() {
    return [...document.querySelectorAll('#open-task-options input:checked')].map((input) => input.value);
  }

  function appendSummary(target, rows) {
    target.replaceChildren();
    rows.forEach(([label, value]) => {
      const dt = document.createElement('dt');
      const dd = document.createElement('dd');
      dt.textContent = String(label);
      dd.textContent = String(value);
      target.append(dt, dd);
    });
  }

  function prepareComparison() {
    const modelIds = [...selected];
    const taskIds = selectedTaskIds();
    if (modelIds.length < 2 || !taskIds.length) {
      byId('open-comparison-status').textContent = 'Select at least two model families and one coding fixture.';
      return;
    }
    const repetitions = Number(byId('open-repetitions').value);
    const maxBudgetUsd = Number(byId('open-budget').value);
    const allowExternalNetwork = byId('open-network').checked;
    const paidApproved = byId('open-paid-approval').checked;
    const status = !allowExternalNetwork
      ? 'local_evaluation_plan_ready'
      : maxBudgetUsd > 0 && !paidApproved
        ? 'paid_adapter_approval_required'
        : 'live_sandbox_and_adapters_required';
    comparisonPlan = {
      schema: 'dreamco.buddy_open_model_comparison_plan.v1',
      createdAt: new Date().toISOString(),
      modelFamilyIds: modelIds,
      taskIds,
      repetitions,
      totalCases: modelIds.length * taskIds.length * repetitions,
      localRuntimeId: byId('open-runtime').value,
      maxBudgetUsd,
      allowExternalNetwork,
      paidAdaptersApprovedForThisRun: paidApproved,
      status,
      liveExecutionPerformed: false,
      developerRegionUsedForScoring: false,
      comparisonUnit: 'exact model checkpoint',
      evidenceRequired: catalog.evidence_fields,
    };
    appendSummary(byId('open-comparison-summary'), [
      ['Models', modelIds.length],
      ['Fixtures', taskIds.length],
      ['Repetitions', repetitions],
      ['Total cases', comparisonPlan.totalCases],
      ['Budget cap', `$${maxBudgetUsd.toFixed(2)}`],
      ['Status', status.replaceAll('_', ' ')],
    ]);
    byId('open-comparison-result').hidden = false;
    byId('open-comparison-status').textContent = status === 'paid_adapter_approval_required'
      ? 'Plan paused. A paid adapter needs approval for this run.'
      : status === 'live_sandbox_and_adapters_required'
        ? 'Plan ready for configured model and sandbox adapters. No live model was called here.'
        : 'Local comparison plan ready. Network access remains off.';
  }

  function isFloatingRevision(revision) {
    return ['main', 'master', 'latest', 'head', 'stable', 'dev', 'develop'].includes(revision.trim().toLowerCase());
  }

  function approvedHost(value) {
    try {
      const url = new URL(value);
      return url.protocol === 'https:'
        && !url.username && !url.password && !url.search && !url.hash
        && catalog.open_source_sandbox.supported_hosts.includes(url.hostname);
    } catch (error) {
      return false;
    }
  }

  function prepareSourcePlan(event) {
    event.preventDefault();
    const form = byId('open-source-form');
    if (!form.reportValidity()) return;
    const sourceKind = byId('source-kind').value;
    const sourceUrl = byId('source-url').value.trim();
    const revision = byId('source-revision').value.trim();
    if (!approvedHost(sourceUrl)) {
      byId('open-source-status').textContent = 'Use a credential-free HTTPS URL from GitHub, GitLab, Codeberg, or Hugging Face.';
      return;
    }
    if (isFloatingRevision(revision)) {
      byId('open-source-status').textContent = 'Use an exact commit, immutable tag, or model revision instead of a floating branch.';
      return;
    }
    if (!byId('source-rights').checked) {
      byId('open-source-status').textContent = 'Confirm the source license and usage rights before creating a plan.';
      return;
    }
    const allowNetwork = byId('source-network').checked;
    sourcePlan = {
      schema: 'dreamco.buddy_open_source_sandbox_plan.v1',
      createdAt: new Date().toISOString(),
      source: {
        kind: sourceKind,
        url: sourceUrl,
        revision,
        declaredLicense: byId('source-license').value.trim(),
        weightFormat: sourceKind === 'model_weights' ? byId('weight-format').value : null,
      },
      objective: byId('source-objective').value.trim(),
      liveExecutionPerformed: false,
      sandboxAdapterRequired: true,
      status: allowNetwork ? 'network_approval_and_sandbox_adapter_required' : 'sandbox_adapter_required',
      controls: {
        sourceMount: 'read_only',
        workingDirectory: 'ephemeral',
        user: 'non_root',
        hostSockets: 'none',
        secrets: 'none',
        network: allowNetwork ? 'one_run_approval_required' : 'off',
        trustRemoteCode: false,
        limits: {
          timeoutSeconds: Number(byId('source-timeout').value),
          cpuCores: Number(byId('source-cpu').value),
          memoryMb: Number(byId('source-memory').value),
          diskMb: Number(byId('source-disk').value),
          processCount: 64,
        },
        outputs: 'quarantined_until_tests_and_owner_review',
      },
      stages: [
        'Verify the exact revision, publisher, license, and file hashes.',
        'Scan secrets, malware, unsafe serialization, dependencies, and provenance.',
        'Generate an SBOM and open-source security scorecard evidence.',
        'Build from locked dependencies in a disposable non-root sandbox.',
        'Run upstream, compatibility, mutation, security, and adversarial tests.',
        'Record failures, resource use, logs, and reproducible artifact hashes.',
        'Show source, behavior, license, and dependency diffs.',
        'Request owner approval for a reversible integration checkpoint.',
      ],
      automaticMerge: false,
      automaticPublish: false,
    };
    byId('open-source-result-title').textContent = allowNetwork
      ? 'Network approval and sandbox adapter required'
      : 'Sandbox adapter required';
    byId('open-source-stages').innerHTML = sourcePlan.stages.map((stage) => `<li>${escapeHtml(stage)}</li>`).join('');
    byId('open-source-result').hidden = false;
    byId('open-source-status').textContent = 'Plan created. Nothing was cloned, loaded, built, or executed.';
  }

  function downloadJson(value, filename) {
    if (!value) return;
    const blob = new Blob([JSON.stringify(value, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    link.click();
    URL.revokeObjectURL(url);
  }

  ['open-model-search', 'open-region-filter', 'open-access-filter'].forEach((id) => {
    byId(id).addEventListener(id === 'open-model-search' ? 'input' : 'change', renderModels);
  });
  byId('prepare-open-comparison').addEventListener('click', prepareComparison);
  byId('download-open-comparison').addEventListener('click', () => downloadJson(comparisonPlan, 'buddy-open-model-comparison-plan.json'));
  byId('source-kind').addEventListener('change', () => {
    byId('weight-format-field').hidden = byId('source-kind').value !== 'model_weights';
  });
  byId('open-source-form').addEventListener('submit', prepareSourcePlan);
  byId('prepare-source-plan').setAttribute('aria-describedby', 'open-source-status');
  byId('download-source-plan').addEventListener('click', () => downloadJson(sourcePlan, 'buddy-open-source-sandbox-plan.json'));

  renderSummary();
  renderFilters();
  renderTasks();
  renderModels();
})();
