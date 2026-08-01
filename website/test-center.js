(function () {
  'use strict';

  const byId = (id) => document.getElementById(id);
  const formatter = new Intl.NumberFormat('en-US');
  let registry = null;
  let latestPlan = null;
  let selectedQualityBot = null;
  const selectedSuites = new Set();
  const quality = window.BUDDY_FLEET_QUALITY_PROGRAM || { summary: {}, bots: [], quality_workers: [], release_pipeline: [] };

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

  function readable(value) {
    return String(value || '').replaceAll('_', ' ');
  }

  function renderQualityMetrics() {
    const summary = quality.summary || {};
    byId('quality-profile-count').textContent = formatter.format(summary.unique_learning_paths || summary.per_bot_learning_plans || 0);
    byId('quality-capability-count').textContent = formatter.format(summary.per_capability_benchmark_plans || 0);
    byId('quality-contract-count').textContent = formatter.format(summary.repository_capability_contracts_passed || 0);
    byId('quality-live-count').textContent = formatter.format(summary.live_competitor_benchmarks_completed || 0);
    byId('quality-production-count').textContent = formatter.format(summary.production_ready_profiles || 0);
    const reviewed = new Date(`${quality.catalog_reviewed_on || '1970-01-01'}T00:00:00Z`);
    const ageDays = Math.max(0, Math.floor((Date.now() - reviewed.getTime()) / 86_400_000));
    byId('quality-review-status').textContent = ageDays > Number(quality.stale_after_days || 14) ? 'Refresh due' : `${ageDays}d ago`;
  }

  function qualityBotMatchesStatus(bot, status) {
    if (status === 'all') return true;
    if (status === 'repository_contract_passed') {
      return bot.evidence.repository_capability_contracts_passed === bot.evidence.repository_capability_contracts_total;
    }
    if (status === 'live_end_to_end_passed') return bot.evidence.live_end_to_end_flows_passed > 0;
    if (status === 'production_ready') return bot.production_status === 'production_ready';
    return false;
  }

  function renderQualityBots() {
    const target = byId('quality-bot-list');
    const query = byId('quality-search').value.trim().toLowerCase();
    const status = byId('quality-status-filter').value;
    const matched = (quality.bots || []).filter((bot) => {
      const capabilities = bot.benchmark_plan.capabilities.map((capability) => capability.name).join(' ');
      const learningGoal = bot.learning_path?.training_goal || '';
      const text = `${bot.display_name} ${bot.bot_id} ${bot.division} ${bot.category} ${capabilities} ${learningGoal}`.toLowerCase();
      return (!query || text.includes(query)) && qualityBotMatchesStatus(bot, status);
    });
    target.replaceChildren();
    matched.slice(0, 60).forEach((bot) => {
      const row = make('button', undefined, 'quality-bot-row');
      row.type = 'button';
      const identity = make('span', undefined, 'quality-bot-name');
      identity.append(make('strong', bot.display_name), make('small', `${bot.division} · ${bot.category}`));
      const contracts = make('span', undefined, 'quality-evidence-cell');
      contracts.append(make('small', 'Repository'), make('strong', `${bot.evidence.repository_capability_contracts_passed}/${bot.evidence.repository_capability_contracts_total} passed`));
      const live = make('span', undefined, 'quality-evidence-cell');
      live.append(make('small', 'Live evidence'), make('strong', `${bot.evidence.live_end_to_end_flows_passed} flows · ${bot.evidence.live_competitor_benchmarks_passed} benchmarks`));
      row.append(identity, contracts, live, make('span', 'View plan', 'quality-view-label'));
      row.addEventListener('click', () => showQualityDetail(bot));
      target.append(row);
    });
    byId('quality-result-count').textContent = `${formatter.format(matched.length)} matching · showing ${formatter.format(Math.min(matched.length, 60))}`;
    if (!matched.length) target.append(make('p', 'No bot has evidence for this filter yet.', 'test-empty'));
  }

  function appendList(target, values, className) {
    const list = make('ul', undefined, className);
    values.forEach((value) => list.append(make('li', value)));
    target.append(list);
  }

  function showQualityDetail(bot) {
    selectedQualityBot = bot;
    byId('quality-detail-division').textContent = `${bot.division} · ${bot.bot_id}`;
    byId('quality-detail-title').textContent = bot.display_name;
    const body = byId('quality-detail-body');
    body.replaceChildren();

    const evidence = make('div', undefined, 'quality-detail-summary');
    [
      ['Buddy route', bot.evidence.buddy_route],
      ['Governed runtime', bot.evidence.governed_runtime],
      ['Repository contracts', `${bot.evidence.repository_capability_contracts_passed}/${bot.evidence.repository_capability_contracts_total} passed`],
      ['Live end-to-end', `${bot.evidence.live_end_to_end_flows_passed} passed`],
      ['Live competitor benchmarks', `${bot.evidence.live_competitor_benchmarks_passed} completed`],
      ['Learning path', bot.learning_path.path_id],
      ['Curriculum modules', `${bot.learning_path.module_count} ordered`],
      ['Competitor suite', bot.competitor_benchmark.suite_id],
      ['Production status', bot.production_status],
    ].forEach(([label, value]) => {
      const item = make('div');
      item.append(make('small', label), make('strong', readable(value)));
      evidence.append(item);
    });
    body.append(evidence, make('h3', 'Completed build phases'));
    appendList(body, bot.build_plan.completed_phases.map(readable), 'quality-phase-list complete');
    body.append(make('h3', 'Remaining evidence gates'));
    appendList(body, bot.build_plan.remaining_phases.map(readable), 'quality-phase-list remaining');
    body.append(make('h3', 'Next build actions'));
    appendList(body, bot.build_plan.next_actions, 'quality-action-list');

    body.append(make('h3', 'Separate learning path'));
    const learningSummary = make('p', bot.learning_path.training_goal, 'quality-learning-goal');
    const learningStages = make('div', undefined, 'quality-learning-stages');
    bot.learning_path.stages.forEach((stage, index) => {
      const definition = (quality.learning_path_policy?.stages || []).find((item) => item.id === stage.stage_id) || {};
      const label = definition.label || readable(stage.stage_id);
      const row = make('article', undefined, 'quality-learning-stage');
      const heading = make('div');
      heading.append(make('strong', `${index + 1}. ${label}`), make('span', readable(stage.status), 'test-status'));
      row.append(
        heading,
        make('p', `${label} for ${bot.display_name}'s ${bot.category} specialization and ordered capability curriculum.`),
        make('small', `Gate: ${definition.evidence_gate || 'Evidence required before progression.'}`),
      );
      learningStages.append(row);
    });
    body.append(learningSummary, learningStages);

    body.append(make('h3', 'Competitor benchmark suite'));
    const benchmarkSummary = make('div', undefined, 'quality-benchmark-summary');
    [
      ['Suite', bot.competitor_benchmark.suite_id],
      ['Baseline', bot.competitor_benchmark.baseline],
      ['Capability benchmarks', String(bot.competitor_benchmark.benchmark_count)],
      ['Candidates verified', String(bot.competitor_benchmark.current_candidates_verified)],
      ['Live results', String(bot.competitor_benchmark.live_results_completed)],
      ['State', readable(bot.competitor_benchmark.status)],
    ].forEach(([label, value]) => {
      const item = make('div');
      item.append(make('small', label), make('strong', value));
      benchmarkSummary.append(item);
    });
    body.append(benchmarkSummary);

    body.append(make('h3', 'Capability benchmark fixtures'));
    const capabilityList = make('div', undefined, 'quality-capability-list');
    bot.benchmark_plan.capabilities.forEach((capability) => {
      const row = make('div', undefined, 'quality-capability-row');
      const copy = make('span');
      copy.append(
        make('strong', `${capability.learning_order}. ${capability.name}`),
        make('code', capability.module_id),
        make('code', capability.benchmark_id),
      );
      row.append(
        copy,
        make('span', `Repository: ${readable(capability.repository_contract_status)}`),
        make('span', `Competitor: ${readable(capability.live_competitor_benchmark_status)}`),
        make('span', `Live E2E: ${readable(capability.live_end_to_end_status)}`),
      );
      row.title = `Benchmark ${capability.name} against current task-specific competitors using identical signed fixtures.`;
      capabilityList.append(row);
    });
    body.append(capabilityList, make('h3', 'Assigned quality team'));
    appendList(body, quality.quality_workers.map((worker) => `${worker.slug}: ${worker.role}`), 'quality-worker-list');
    byId('quality-send-buddy').href = `buddy.html?prompt=${encodeURIComponent(bot.buddy_prompts.improvement)}`;
    byId('quality-detail').showModal();
  }

  function downloadQualityPlan() {
    if (!selectedQualityBot) return;
    downloadJson({
      schema: 'dreamco.buddy_fleet_quality_handoff.v1',
      preparedAt: new Date().toISOString(),
      bot: selectedQualityBot,
      benchmarkDimensions: quality.benchmark_dimensions,
      competitorDiscovery: quality.competitor_discovery,
      qualityWorkers: quality.quality_workers,
      releasePipeline: quality.release_pipeline,
      dependencyGates: quality.dependency_gates,
      continuousLearning: quality.continuous_learning,
      learningPathPolicy: quality.learning_path_policy,
      externalActionTaken: false,
      liveBenchmarkExecuted: false,
    }, `${selectedQualityBot.bot_id}-quality-plan.json`);
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
  byId('quality-search').addEventListener('input', renderQualityBots);
  byId('quality-status-filter').addEventListener('change', renderQualityBots);
  byId('quality-detail-close').addEventListener('click', () => byId('quality-detail').close());
  byId('quality-download-plan').addEventListener('click', downloadQualityPlan);
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

  renderQualityMetrics();
  renderQualityBots();
  init().catch((error) => {
    byId('test-suite-list').replaceChildren(make('p', 'Test registry could not load. Open this site through the local server or deployed site.', 'test-empty'));
    console.error(error);
  });
})();
