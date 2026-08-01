(function () {
  'use strict';

  const data = window.BUDDY_MODEL_BENCHMARKS || { summary: {}, suites: [], targets: [] };
  const targets = data.targets || [];
  const selected = new Set(targets.map((target) => target.id));
  let visible = [...targets];
  let latestPlan = null;

  const byId = (id) => document.getElementById(id);
  const escapeHtml = (value) => String(value)
    .replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;').replaceAll("'", '&#39;');

  function option(value, label) {
    const element = document.createElement('option');
    element.value = value;
    element.textContent = label;
    return element;
  }

  function renderMetrics() {
    byId('metric-targets').textContent = Number(data.summary.targets || 0).toLocaleString();
    byId('metric-providers').textContent = Number(data.summary.providers || 0).toLocaleString();
    byId('metric-suites').textContent = Number(data.summary.suites || 0).toLocaleString();
    byId('metric-live').textContent = Number(data.summary.liveBenchmarked || 0).toLocaleString();
    const reviewed = new Date(`${data.catalogReviewedOn}T00:00:00Z`);
    const ageDays = Math.max(0, Math.floor((Date.now() - reviewed.getTime()) / 86_400_000));
    byId('metric-review').textContent = ageDays > Number(data.staleAfterDays || 14) ? 'Refresh due' : `${ageDays}d ago`;
  }

  function renderFilters() {
    [...new Set(targets.map((target) => target.tier))].sort().forEach((tier) => byId('model-tier').append(option(tier, tier)));
    [...new Set(targets.map((target) => target.category))].sort().forEach((category) => byId('model-category').append(option(category, category)));
  }

  function renderSuites() {
    const target = byId('suite-options');
    data.suites.forEach((suite) => {
      const label = document.createElement('label');
      label.className = 'model-suite-option';
      const input = document.createElement('input');
      input.type = 'checkbox';
      input.value = suite.id;
      input.checked = true;
      label.append(input, document.createTextNode(suite.label));
      target.append(label);
    });
  }

  function filteredTargets() {
    const query = byId('model-search').value.trim().toLowerCase();
    const tier = byId('model-tier').value;
    const category = byId('model-category').value;
    return targets.filter((target) => {
      const haystack = [target.name, target.provider, target.category, target.bestFor, ...target.declaredCapabilities].join(' ').toLowerCase();
      return (!query || haystack.includes(query))
        && (tier === 'all' || target.tier === tier)
        && (category === 'all' || target.category === category);
    });
  }

  function updateSelectedCount() {
    byId('selected-count').textContent = selected.size.toLocaleString();
  }

  function renderRows() {
    visible = filteredTargets();
    const body = byId('model-rows');
    body.innerHTML = visible.map((target) => `
      <tr>
        <td><input type="checkbox" data-select-target="${target.id}" aria-label="Include ${escapeHtml(target.name)}" ${selected.has(target.id) ? 'checked' : ''} /></td>
        <td><div class="model-target-copy"><button class="model-name-button" type="button" data-model-detail="${target.id}">${escapeHtml(target.name)}</button><span class="model-tier">${escapeHtml(target.tier)}</span></div></td>
        <td>${escapeHtml(target.provider)}</td>
        <td>${escapeHtml(target.category)}</td>
        <td class="model-evidence ${target.catalogReady ? 'ready' : ''}">${target.catalogReady ? 'Ready' : 'Needs metadata'}</td>
        <td class="model-evidence">Not run</td>
      </tr>`).join('');
    body.querySelectorAll('[data-select-target]').forEach((input) => input.addEventListener('change', (event) => {
      const id = Number(event.currentTarget.dataset.selectTarget);
      if (event.currentTarget.checked) selected.add(id); else selected.delete(id);
      updateSelectedCount();
    }));
    body.querySelectorAll('[data-model-detail]').forEach((button) => button.addEventListener('click', () => showDetail(Number(button.dataset.modelDetail))));
    byId('model-count').textContent = `Showing ${visible.length.toLocaleString()} of ${targets.length.toLocaleString()} targets. ${selected.size.toLocaleString()} selected.`;
    updateSelectedCount();
  }

  function showDetail(id) {
    const target = targets.find((item) => item.id === id);
    if (!target) return;
    byId('model-detail-provider').textContent = `${target.provider} · ${target.tier}`;
    byId('model-detail-title').textContent = target.name;
    byId('model-detail-body').innerHTML = `
      <p><strong>Declared task fit:</strong> ${escapeHtml(target.bestFor)}</p>
      <h3>Declared capabilities</h3><ul>${target.declaredCapabilities.map((item) => `<li>${escapeHtml(item)}</li>`).join('')}</ul>
      <h3>Assigned benchmark suites</h3><ul>${target.benchmarkSuites.map((id) => `<li>${escapeHtml(data.suites.find((suite) => suite.id === id)?.label || id)}</li>`).join('')}</ul>
      <h3>Evidence status</h3><p>No live score exists yet. Availability, quality, latency, and cost must be recorded by an authenticated adapter using the exact provider model id.</p>`;
    byId('model-detail').showModal();
  }

  function runCatalogAudit() {
    const passed = targets.filter((target) => target.catalogReady).length;
    const failed = targets.length - passed;
    byId('benchmark-status').textContent = `Catalog audit complete: ${passed} ready, ${failed} missing metadata, 0 live models called. This validates records and suite coverage, not model quality.`;
  }

  function selectedSuites() {
    return [...document.querySelectorAll('#suite-options input:checked')].map((input) => input.value);
  }

  function renderPlan(plan) {
    const summary = byId('benchmark-plan-summary');
    summary.replaceChildren();
    [['Targets', plan.targetCount], ['Suites', plan.suiteCount], ['Repetitions', plan.repetitions], ['Total cases', plan.totalCases], ['Budget cap', `$${plan.maxBudgetUsd.toFixed(2)}`], ['Status', plan.status.replaceAll('_', ' ')]].forEach(([label, value]) => {
      const dt = document.createElement('dt'); dt.textContent = String(label);
      const dd = document.createElement('dd'); dd.textContent = String(value);
      summary.append(dt, dd);
    });
    byId('benchmark-result').hidden = false;
  }

  function preparePlan() {
    const suites = selectedSuites();
    const chosen = targets.filter((target) => selected.has(target.id));
    if (!chosen.length || !suites.length) {
      byId('benchmark-status').textContent = 'Select at least one target and one test suite.';
      return;
    }
    const repetitions = Number(byId('benchmark-repetitions').value);
    const maxBudgetUsd = Number(byId('benchmark-budget').value);
    const allowExternalNetwork = byId('benchmark-network').checked;
    const paidApproved = byId('benchmark-paid').checked;
    const hasPaidTargets = chosen.some((target) => !['free', 'discovery'].includes(target.tier));
    const hasDiscoveryTargets = chosen.some((target) => target.discoveryTarget);
    const status = !allowExternalNetwork
      ? 'local_catalog_plan_ready'
      : hasDiscoveryTargets
        ? 'official_catalog_discovery_required'
        : hasPaidTargets && (!paidApproved || maxBudgetUsd <= 0)
        ? 'paid_budget_approval_required'
        : 'live_adapters_required';
    latestPlan = {
      schema: 'dreamco.buddy_model_benchmark_plan.v1',
      createdAt: new Date().toISOString(),
      targetIds: chosen.map((target) => target.id),
      targetCount: chosen.length,
      suiteIds: suites,
      suiteCount: suites.length,
      repetitions,
      totalCases: chosen.length * suites.length * repetitions,
      maxBudgetUsd,
      allowExternalNetwork,
      paidApprovedForThisRun: paidApproved,
      status,
      liveBenchmarkExecuted: false,
      evidenceRequired: ['exact provider model id', 'fixture hash', 'response hash', 'latency', 'token usage', 'actual cost', 'grader version', 'UTC timestamp'],
    };
    renderPlan(latestPlan);
    byId('benchmark-status').textContent = status === 'official_catalog_discovery_required'
      ? 'Plan paused at official-catalog discovery. Exact model IDs and terms must be recorded before any benchmark call.'
      : status === 'paid_budget_approval_required'
      ? 'Plan paused. Paid targets require both a maximum spend and approval for this run.'
      : status === 'live_adapters_required'
        ? 'Plan ready for authenticated provider adapters. No model has been called from this static page.'
        : 'Local catalog plan ready. External networking remains off.';
  }

  function downloadPlan() {
    if (!latestPlan) return;
    const blob = new Blob([JSON.stringify(latestPlan, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url; link.download = 'buddy-model-benchmark-plan.json'; link.click();
    URL.revokeObjectURL(url);
  }

  ['model-search', 'model-tier', 'model-category'].forEach((id) => byId(id).addEventListener(id === 'model-search' ? 'input' : 'change', renderRows));
  byId('select-visible').addEventListener('click', () => { visible.forEach((target) => selected.add(target.id)); renderRows(); });
  byId('clear-selection').addEventListener('click', () => { selected.clear(); renderRows(); });
  byId('run-catalog-audit').addEventListener('click', runCatalogAudit);
  byId('prepare-live-plan').addEventListener('click', preparePlan);
  byId('download-benchmark-plan').addEventListener('click', downloadPlan);
  byId('model-detail-close').addEventListener('click', () => byId('model-detail').close());

  renderMetrics();
  renderFilters();
  renderSuites();
  renderRows();
})();
