(function () {
  'use strict';

  const byId = (id) => document.getElementById(id);
  const formatter = new Intl.NumberFormat('en-US');
  let registry = null;
  let latestPlan = null;
  const selectedSuites = new Set();

  function make(tag, text, className) {
    const node = document.createElement(tag);
    if (text !== undefined) node.textContent = text;
    if (className) node.className = className;
    return node;
  }

  function downloadJson(payload, filename) {
    const blob = new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    link.click();
    URL.revokeObjectURL(url);
  }

  function selectedMode() {
    return byId('test-mode-options').querySelector('input[name="test-mode"]:checked')?.value || 'contract';
  }

  function renderMetrics() {
    const summary = registry.summary || {};
    byId('test-files-count').textContent = formatter.format(summary.files_scanned || 0);
    byId('test-routes-count').textContent = formatter.format(summary.literal_api_routes || 0);
    byId('test-pages-count').textContent = formatter.format(summary.web_pages || 0);
    byId('test-tests-count').textContent = formatter.format(summary.test_files || 0);
    byId('test-suites-count').textContent = formatter.format(summary.test_suites || 0);
    byId('test-blocked-count').textContent = formatter.format(summary.blocked_suites || 0);
    byId('test-scan-id').textContent = `Scan ${registry.scan_id}`;
  }

  function renderSuites() {
    const target = byId('test-suite-list');
    const query = byId('test-suite-search').value.trim().toLowerCase();
    const level = byId('test-level-filter').value;
    const suites = registry.suites.filter((suite) => {
      const matchesText = `${suite.name} ${suite.area} ${suite.boundary} ${suite.id}`.toLowerCase().includes(query);
      return matchesText && (level === 'all' || suite.level === level);
    });
    target.replaceChildren();
    suites.forEach((suite) => {
      const row = make('label', undefined, 'test-suite-row');
      const checkbox = document.createElement('input');
      checkbox.type = 'checkbox';
      checkbox.value = suite.id;
      checkbox.checked = selectedSuites.has(suite.id);
      checkbox.addEventListener('change', () => {
        if (checkbox.checked) selectedSuites.add(suite.id);
        else selectedSuites.delete(suite.id);
        updateSelectedCount();
      });
      const name = make('div', undefined, 'test-suite-name');
      name.append(
        make('strong', suite.name),
        make('span', `${suite.area} · ${suite.tests.length} tests · ${suite.sources.length} source paths`),
      );
      row.append(
        checkbox,
        name,
        make('span', suite.level.replaceAll('_', ' '), 'test-level'),
        make('span', suite.status.replaceAll('_', ' '), 'test-status'),
        make('p', suite.boundary, 'test-suite-boundary'),
      );
      target.append(row);
    });
    if (!suites.length) target.append(make('p', 'No suites match this filter.', 'test-empty'));
  }

  function updateSelectedCount() {
    byId('selected-test-count').textContent = `${selectedSuites.size} selected`;
  }

  function readinessFor(suite, mode, allowNetwork, exactApproval) {
    if (suite.status === 'blocked_missing_evidence') return 'blocked_missing_evidence';
    if (suite.level === 'repository_sandbox') {
      return mode === 'contract' ? 'contract_checks_ready_sandbox_not_requested' : 'isolated_sandbox_runner_required';
    }
    if (suite.level === 'adapter_optional' || suite.level === 'credentials_required') {
      if (mode !== 'adapter') return 'held_adapter_mode_not_requested';
      if (!allowNetwork || !exactApproval) return 'held_network_and_exact_approval_required';
      return 'adapter_credentials_and_runner_verification_required';
    }
    return 'local_contract_ready';
  }

  function preparePlan() {
    if (!selectedSuites.size) {
      byId('test-plan-output').replaceChildren(make('p', 'Select at least one test suite.'));
      return;
    }
    const mode = selectedMode();
    const allowNetwork = byId('test-network').checked;
    const exactApproval = byId('test-external-approval').checked;
    const suites = [...selectedSuites].map((id) => registry.suites.find((suite) => suite.id === id)).filter(Boolean)
      .map((suite) => ({
        id: suite.id,
        name: suite.name,
        level: suite.level,
        readiness: readinessFor(suite, mode, allowNetwork, exactApproval),
        scriptIds: suite.scripts,
        commands: suite.scripts.map((scriptId) => `npm run ${scriptId}`),
        evidence: [...suite.sources, ...suite.tests],
        boundary: suite.boundary,
        browserExecutionAllowed: false,
      }));
    latestPlan = {
      schema: 'dreamco.repository_test_plan.v1',
      scanId: registry.scan_id,
      preparedAt: new Date().toISOString(),
      mode,
      allowNetwork,
      exactApprovalForExternalTests: exactApproval,
      maxBudgetUsd: Number(byId('test-budget').value || 0),
      suites,
      testsExecutedByPlanner: false,
      externalActionTaken: false,
      arbitraryCommandsAccepted: false,
      localRunner: 'npm run test:repository',
    };
    const output = byId('test-plan-output');
    const held = suites.filter((suite) => suite.readiness.startsWith('held')).length;
    const blocked = suites.filter((suite) => suite.readiness.startsWith('blocked')).length;
    const list = make('ul');
    suites.forEach((suite) => list.append(make('li', `${suite.name}: ${suite.readiness.replaceAll('_', ' ')}`)));
    output.replaceChildren(
      make('strong', `${suites.length} suites prepared · ${held} held · ${blocked} blocked`),
      make('p', 'The plan records allowed evidence and runner commands. Nothing ran in this browser.'),
      list,
    );
    byId('download-test-plan').disabled = false;
    const prompt = `Buddy, review repository test plan ${registry.scan_id} with ${suites.map((suite) => suite.name).join(', ')}. Explain boundaries, run only reviewed local tests, and ask before any network, paid, credentialed, or external action.`;
    byId('send-test-plan-to-buddy').href = `buddy.html?prompt=${encodeURIComponent(prompt)}`;
  }

  function renderRoutes() {
    const target = byId('test-route-list');
    const query = byId('test-route-search').value.trim().toLowerCase();
    const routes = registry.routes.filter((route) =>
      `${route.method} ${route.path} ${route.suite_id} ${route.classification}`.toLowerCase().includes(query)
    ).slice(0, 250);
    target.replaceChildren();
    routes.forEach((route) => {
      const row = make('div', undefined, 'test-route-row');
      row.append(
        make('span', route.method, 'test-route-method'),
        make('code', route.path, 'test-route-path'),
        make('span', route.suite_id, 'test-route-meta'),
        make('span', route.classification.replaceAll('_', ' '), 'test-route-meta'),
      );
      target.append(row);
    });
    if (!routes.length) target.append(make('p', 'No routes match this filter.', 'test-empty'));
  }

  async function init() {
    const response = await fetch('data/repository-test-registry.json', { cache: 'no-store' });
    if (!response.ok) throw new Error(`Test registry request failed: ${response.status}`);
    registry = await response.json();
    renderMetrics();
    renderSuites();
    renderRoutes();
  }

  byId('test-suite-search').addEventListener('input', renderSuites);
  byId('test-level-filter').addEventListener('change', renderSuites);
  byId('test-route-search').addEventListener('input', renderRoutes);
  byId('select-local-tests').addEventListener('click', () => {
    registry.suites.filter((suite) => ['local_contract', 'repository_sandbox'].includes(suite.level))
      .forEach((suite) => selectedSuites.add(suite.id));
    renderSuites();
    updateSelectedCount();
  });
  byId('clear-test-selection').addEventListener('click', () => {
    selectedSuites.clear();
    renderSuites();
    updateSelectedCount();
  });
  byId('prepare-test-plan').addEventListener('click', preparePlan);
  byId('download-test-plan').addEventListener('click', () => {
    if (latestPlan) downloadJson(latestPlan, 'buddy-repository-test-plan.json');
  });
  byId('copy-test-command').addEventListener('click', async () => {
    try {
      await navigator.clipboard.writeText('npm run test:repository');
      byId('copy-test-command').textContent = 'Copied';
    } catch (_error) {
      byId('copy-test-command').textContent = 'Copy unavailable';
    }
  });

  init().catch((error) => {
    byId('test-suite-list').replaceChildren(make('p', 'Test registry could not load. Open this site through the local server or deployed site.', 'test-empty'));
    console.error(error);
  });
})();
