(function () {
  'use strict';

  const data = window.BUDDY_MODEL_BENCHMARKS || { summary: {}, suites: [], targets: [] };
  const demandData = window.BUDDY_DEMAND_ONTOLOGY || { summary: {}, catalogs: [], researchSources: [], reasons: [] };
  const organizationData = window.BUDDY_AI_ORGANIZATIONS || { summary: {}, existingProviders: [], allianceMembers: [], userNeedTaxonomy: [], benchmarkDimensions: [] };
  const targets = data.targets || [];
  const selected = new Set(targets.map((target) => target.id));
  const organizationRecords = [
    ...(organizationData.existingProviders || []).map((item) => ({ ...item, sourceKey: 'existing', organizationType: 'model_provider', website: item.officialCatalogs?.[0] || '' })),
    ...(organizationData.allianceMembers || []).map((item) => ({ ...item, sourceKey: 'alliance' })),
  ];
  const selectedOrganizations = new Set();
  let visible = [...targets];
  let visibleOrganizations = [...organizationRecords];
  let latestPlan = null;
  let latestOrganizationPlan = null;
  let activeDemandCatalog = 'ai_usage';

  const routingSignals = [
    ['coding', ['code', 'coding', 'debug', 'software', 'app', 'website', 'repository', 'test']],
    ['reasoning', ['reason', 'math', 'logic', 'decide', 'compare', 'analyze']],
    ['research', ['research', 'find sources', 'cite', 'citation', 'literature', 'fact check', 'evidence']],
    ['agents', ['agent', 'tool', 'workflow', 'automate', 'autonomous']],
    ['vision', ['vision', 'screenshot', 'inspect image']],
    ['image generation', ['generate image', 'create image', 'illustration', 'logo', 'art']],
    ['image editing', ['edit image', 'photo edit', 'retouch', 'inpaint', 'photoshop']],
    ['video', ['video', 'movie', 'film', 'animation', 'short']],
    ['voice and speech', ['voice', 'speech', 'transcribe', 'narrate', 'call']],
    ['music and audio', ['music', 'song', 'audio', 'sing', 'rap']],
    ['multilingual and translation', ['translate', 'translation', 'multilingual', 'localize', 'language']],
    ['safety and moderation', ['safety', 'moderate', 'guardrail', 'risk', 'policy']],
    ['ocr and documents', ['ocr', 'document', 'pdf', 'scan', 'extract']],
    ['search and retrieval', ['retrieve', 'retrieval', 'knowledge base', 'search', 'rag']],
    ['data analysis', ['data', 'analytics', 'spreadsheet', 'chart', 'sql']],
    ['embeddings', ['embedding', 'vector', 'semantic']],
    ['forecasting', ['forecast', 'predict', 'time series']],
    ['simulation', ['simulation', 'simulate', 'game', 'digital twin']],
    ['3d and spatial', ['3d', 'spatial', 'world', 'scene', 'modeling']],
    ['accessibility', ['accessibility', 'accessible', 'caption', 'screen reader']],
  ];

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
    byId('metric-sources').textContent = Number(data.summary.sourceLinked || 0).toLocaleString();
    byId('metric-setup').textContent = Number(data.summary.setupPathsReady || 0).toLocaleString();
    byId('metric-suites').textContent = Number(data.summary.suites || 0).toLocaleString();
    byId('metric-live-connections').textContent = Number(data.summary.liveConnected || 0).toLocaleString();
    byId('metric-live').textContent = Number(data.summary.liveBenchmarked || 0).toLocaleString();
    const reviewed = new Date(`${data.catalogReviewedOn}T00:00:00Z`);
    const ageDays = Math.max(0, Math.floor((Date.now() - reviewed.getTime()) / 86_400_000));
    byId('metric-review').textContent = ageDays > Number(data.staleAfterDays || 14) ? 'Refresh due' : `${ageDays}d ago`;
    byId('model-source-summary').textContent = `${Number(data.summary.sourceLinked || 0).toLocaleString()} of ${targets.length.toLocaleString()} targets have an official or owner-controlled source, and ${Number(data.summary.setupPathsReady || 0).toLocaleString()} have a secure setup path. ${Number(data.summary.liveConnected || 0).toLocaleString()} have passed an exact-model live connection probe.`;
  }

  async function hydrateBackendConnectionState() {
    const configuredBase = typeof window.BUDDY_BACKEND_API_BASE === 'string'
      ? window.BUDDY_BACKEND_API_BASE.trim()
      : '';
    const backendBase = configuredBase
      || (new URLSearchParams(location.search).get('backend') === '1' ? location.origin : '');
    if (!backendBase) return;
    try {
      const endpoint = new URL('/api/buddy/models/connections', backendBase).toString();
      const response = await fetch(endpoint, { headers: { Accept: 'application/json' } });
      if (!response.ok || !String(response.headers.get('content-type') || '').includes('application/json')) return;
      const audit = await response.json();
      const summary = audit.summary || {};
      byId('metric-live-connections').textContent = Number(summary.liveVerifiedTargets || 0).toLocaleString();
      byId('model-credential-state').textContent = `${Number(summary.credentialConfiguredTargets || 0).toLocaleString()} target routes configured`;
      byId('model-probe-state').textContent = `${Number(summary.liveVerifiedTargets || 0).toLocaleString()} passed`;
      byId('model-source-summary').textContent = `${Number(summary.sourceLinkedTargets || 0).toLocaleString()} of ${Number(summary.targets || 0).toLocaleString()} targets have a governed source; ${Number(summary.setupPathTargets || 0).toLocaleString()} have setup paths; ${Number(summary.connectorContractTargets || 0).toLocaleString()} have connector or handoff contracts. Live status still requires an exact-model probe.`;
    } catch (_) {
      // Static hosting intentionally falls back to the generated public manifest.
    }
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

  function demandCatalogLabel(catalogId) {
    return demandData.catalogs.find((catalog) => catalog.id === catalogId)?.label || catalogId.replaceAll('_', ' ');
  }

  function renderDemandTabs() {
    const tabs = byId('demand-catalog-tabs');
    tabs.replaceChildren();
    (demandData.catalogs || []).forEach((catalog) => {
      const button = document.createElement('button');
      button.type = 'button';
      button.role = 'tab';
      button.textContent = catalog.label;
      button.setAttribute('aria-selected', String(catalog.id === activeDemandCatalog));
      button.addEventListener('click', () => {
        activeDemandCatalog = catalog.id;
        renderDemandTabs();
        renderDemandCategoryOptions();
        renderDemandReasons();
      });
      tabs.append(button);
    });
  }

  function renderDemandCategoryOptions() {
    const select = byId('demand-category');
    const current = select.value;
    select.replaceChildren(option('all', 'All categories'));
    [...new Set((demandData.reasons || []).filter((reason) => reason.catalogId === activeDemandCatalog).map((reason) => reason.category))]
      .sort().forEach((category) => select.append(option(category, category)));
    select.value = [...select.options].some((item) => item.value === current) ? current : 'all';
  }

  function chooseDemandReason(reason) {
    byId('model-route-objective').value = reason.reason;
    byId('model-route-capabilities').value = reason.capabilities.join(', ');
    byId('model-route-tier').value = 'any';
    byId('model-route-count').value = '20';
    byId('model-route-discovery').checked = true;
    byId('model-route-form').dispatchEvent(new Event('submit', { bubbles: true, cancelable: true }));
    byId('model-route-status').textContent = `${reason.reason} mapped to ${reason.taskCategory} with ${reason.capabilities.join(', ')}. Choose from the 20 prepared model options; no provider has been called.`;
    byId('model-router-title').scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  function renderDemandReasons() {
    const query = byId('demand-search').value.trim().toLowerCase();
    const category = byId('demand-category').value;
    const reasons = (demandData.reasons || []).filter((reason) => reason.catalogId === activeDemandCatalog)
      .filter((reason) => category === 'all' || reason.category === category)
      .filter((reason) => !query || `${reason.reason} ${reason.category} ${reason.taskCategory} ${reason.capabilities.join(' ')}`.toLowerCase().includes(query));
    const list = byId('demand-reason-list');
    list.replaceChildren();
    reasons.forEach((reason) => {
      const button = document.createElement('button'); button.type = 'button'; button.className = 'demand-reason-row';
      const rank = document.createElement('span'); rank.className = 'demand-rank'; rank.textContent = String(reason.rank).padStart(3, '0');
      const copy = document.createElement('span'); copy.className = 'demand-reason-copy';
      const title = document.createElement('strong'); title.textContent = reason.reason;
      const meta = document.createElement('small'); meta.textContent = `${reason.category} · ${reason.taskCategory}`;
      copy.append(title, meta);
      const capabilities = document.createElement('span'); capabilities.className = 'demand-capabilities'; capabilities.textContent = reason.capabilities.join(' · ');
      const action = document.createElement('span'); action.className = 'demand-action'; action.textContent = 'Compare 20';
      button.append(rank, copy, capabilities, action);
      button.addEventListener('click', () => chooseDemandReason(reason));
      list.append(button);
    });
    byId('demand-result-count').textContent = `${reasons.length.toLocaleString()} of 100 reasons in ${demandCatalogLabel(activeDemandCatalog)}`;
    const sourceTarget = byId('demand-source-links'); sourceTarget.replaceChildren();
    (demandData.researchSources || []).filter((source) => source.catalogs.includes(activeDemandCatalog)).forEach((source) => {
      const link = document.createElement('a'); link.href = source.url; link.target = '_blank'; link.rel = 'noopener'; link.textContent = source.organization; link.title = source.title; sourceTarget.append(link);
    });
  }

  function renderDemandExplorer() {
    byId('demand-reason-count').textContent = Number(demandData.summary?.reasons || 0).toLocaleString();
    byId('demand-category-count').textContent = Number(demandData.summary?.categories || 0).toLocaleString();
    byId('demand-option-count').textContent = Number(demandData.summary?.modelOptionsPerReason || 20).toLocaleString();
    renderDemandTabs(); renderDemandCategoryOptions(); renderDemandReasons();
  }

  function targetText(target) {
    return [target.name, target.provider, target.category, target.bestFor, ...target.declaredCapabilities].join(' ').toLowerCase();
  }

  function downloadFile(filename, content, type) {
    const blob = new Blob([content], { type });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url; link.download = filename; link.click();
    URL.revokeObjectURL(url);
  }

  function exportCatalogJson() {
    downloadFile('buddy-ai-systems-encyclopedia.json', JSON.stringify(data, null, 2), 'application/json');
  }

  function exportCatalogCsv() {
    const headers = ['id', 'name', 'provider', 'category', 'tier', 'discovery_target', 'official_source', 'connection_kind', 'connection_status', 'setup_path', 'declared_task_fit', 'live_connected', 'live_score'];
    const rows = targets.map((target) => [target.id, target.name, target.provider, target.category, target.tier, target.discoveryTarget, target.sourceConnection?.officialSource || target.officialCatalog || '', target.sourceConnection?.connectionKind || '', target.sourceConnection?.status || '', target.sourceConnection?.setupPath || '', target.bestFor, target.sourceConnection?.liveProviderConnection || false, target.liveScore ?? '']);
    const csv = [headers, ...rows].map((row) => row.map((value) => `"${String(value).replaceAll('"', '""')}"`).join(',')).join('\n');
    downloadFile('buddy-ai-systems-encyclopedia.csv', `${csv}\n`, 'text/csv');
  }

  function prepareModelRoute(event) {
    event.preventDefault();
    const objective = byId('model-route-objective').value.trim();
    if (objective.length < 3) return;
    const capabilities = byId('model-route-capabilities').value.split(',').map((value) => value.trim().toLowerCase()).filter(Boolean);
    const tier = byId('model-route-tier').value;
    const maxCandidates = Number(byId('model-route-count').value);
    const includeDiscovery = byId('model-route-discovery').checked;
    const priorities = {
      quality: Number(byId('model-priority-quality').value),
      cost: Number(byId('model-priority-cost').value),
      latency: Number(byId('model-priority-latency').value),
      privacy: Number(byId('model-priority-privacy').value),
    };
    const requestText = `${objective} ${capabilities.join(' ')}`.toLowerCase();
    const signals = routingSignals.filter(([, terms]) => terms.some((term) => requestText.includes(term))).map(([id]) => id);
    if (!signals.length) signals.push('reasoning');
    const scored = targets.filter((target) => includeDiscovery || !target.discoveryTarget).map((target) => {
      const searchable = targetText(target);
      const matchedSignals = signals.filter((signal) => searchable.includes(signal));
      const matchedCapabilities = capabilities.filter((capability) => searchable.includes(capability));
      const isFree = target.tier === 'free';
      const isPremium = ['paid', 'freemium'].includes(target.tier);
      const tierFit = tier === 'any' || (tier === 'free' && isFree) || (tier === 'premium' && isPremium);
      const local = ['dreamco', 'ollama'].includes(target.provider.toLowerCase().replace(/[^a-z0-9]/g, ''));
      const objectiveTerms = [...new Set(objective.toLowerCase().split(/\W+/).filter((term) => term.length >= 4))];
      const objectiveMatches = objectiveTerms.filter((term) => searchable.includes(term)).length;
      const score = matchedSignals.length * 26 + matchedCapabilities.length * 12 + Math.min(10, objectiveMatches)
        + (tierFit ? 8 : -8) + (target.discoveryTarget ? 0 : 4)
        + (isFree ? priorities.cost * 8 : -priorities.cost * 3)
        + (local ? priorities.privacy * 10 + priorities.latency * 3 : 0);
      const coverage = Math.min(1, 0.25 + (matchedSignals.length ? 0.3 : 0)
        + (capabilities.length ? (matchedCapabilities.length / capabilities.length) * 0.3 : 0.15)
        + (target.discoveryTarget ? 0 : 0.15));
      return { target, score, coverage, matchedSignals, matchedCapabilities };
    }).sort((left, right) => right.score - left.score || left.target.id - right.target.id);
    const candidates = scored.filter((candidate, index, all) => all.findIndex((item) => item.target.provider.toLowerCase() === candidate.target.provider.toLowerCase()) === index).slice(0, maxCandidates);
    const results = byId('model-route-results');
    results.innerHTML = candidates.map((candidate, index) => `
      <article class="model-route-candidate">
        <div class="model-route-rank">${index + 1}</div>
        <div class="model-route-copy"><span>${escapeHtml(candidate.target.provider)} · ${escapeHtml(candidate.target.tier)}</span><h3>${escapeHtml(candidate.target.name)}</h3><p>${escapeHtml(candidate.target.bestFor)}</p></div>
        <dl><div><dt>Metadata fit</dt><dd>${candidate.score.toFixed(1)}</dd></div><div><dt>Coverage</dt><dd>${Math.round(candidate.coverage * 100)}%</dd></div><div><dt>Live score</dt><dd>Not run</dd></div></dl>
        <div class="model-route-tags">${candidate.matchedSignals.map((value) => `<span>${escapeHtml(value)}</span>`).join('') || '<span>general reasoning</span>'}</div>
        <div class="model-route-actions"><button class="btn btn-primary btn-sm" type="button" data-route-choose="${candidate.target.id}">Choose</button><button class="btn btn-outline btn-sm" type="button" data-route-detail="${candidate.target.id}">Inspect tests</button></div>
      </article>`).join('');
    results.hidden = false;
    results.querySelectorAll('[data-route-detail]').forEach((button) => button.addEventListener('click', () => showDetail(Number(button.dataset.routeDetail))));
    results.querySelectorAll('[data-route-choose]').forEach((button) => button.addEventListener('click', () => {
      const targetId = Number(button.dataset.routeChoose); const target = targets.find((item) => item.id === targetId);
      selected.clear(); selected.add(targetId); renderRows();
      byId('model-route-status').textContent = `${target?.name || 'Model'} selected for benchmark preparation. Selection does not call the provider, authorize payment, or prove live availability.`;
    }));
    byId('model-route-status').textContent = `${candidates.length} provider-diverse candidates prepared for ${signals.join(', ')}. Quality contributed 0 points because no live signed benchmark evidence exists.`;
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
        <td class="model-evidence ${target.sourceConnection?.sourceLinked ? 'ready' : ''}">${target.sourceConnection?.sourceLinked ? 'Linked' : 'Missing'}</td>
        <td><a class="model-connection-link" href="${escapeHtml(target.sourceConnection?.setupPath || 'connections.html')}">${escapeHtml((target.sourceConnection?.status || 'setup_required').replaceAll('_', ' '))}</a></td>
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
      <h3>Source connection</h3>
      <p><strong>Status:</strong> ${escapeHtml((target.sourceConnection?.status || 'setup_required').replaceAll('_', ' '))}. A source link or setup route is not proof of a live provider connection.</p>
      <div class="model-detail-actions"><a class="btn btn-outline btn-sm" href="${escapeHtml(target.sourceConnection?.officialSource || target.officialCatalog || 'connections.html')}" ${String(target.sourceConnection?.officialSource || '').startsWith('http') ? 'target="_blank" rel="noopener"' : ''}>Official source</a><a class="btn btn-outline btn-sm" href="${escapeHtml(target.sourceConnection?.setupPath || 'connections.html')}">Prepare connection</a></div>
      <h3>Declared capabilities</h3><ul>${target.declaredCapabilities.map((item) => `<li>${escapeHtml(item)}</li>`).join('')}</ul>
      <h3>Prompt and test library</h3><div class="model-prompt-library">${(target.promptLibrary || target.benchmarkSuites || []).map((suiteId) => data.suites.find((suite) => suite.id === suiteId)).filter(Boolean).map((prompt) => `<article><div><strong>${escapeHtml(prompt.label)}</strong><span>${escapeHtml(prompt.grader)} · ${escapeHtml(prompt.modality)}</span></div><p>${escapeHtml(prompt.prompt_fixture)}</p><button class="btn btn-outline btn-sm" type="button" data-prepare-model-test="${escapeHtml(prompt.id)}">Load test</button></article>`).join('')}</div>
      <h3>Evidence status</h3><p>No live score exists yet. Availability, quality, latency, and cost must be recorded by an authenticated adapter using the exact provider model id.</p>`;
    byId('model-detail-body').querySelectorAll('[data-prepare-model-test]').forEach((button) => button.addEventListener('click', () => {
      selected.clear(); selected.add(target.id);
      document.querySelectorAll('#suite-options input').forEach((input) => { input.checked = input.value === button.dataset.prepareModelTest; });
      byId('benchmark-status').textContent = `${target.name} and ${button.dataset.prepareModelTest.replaceAll('_', ' ')} loaded. Review network and budget controls, then prepare the run plan.`;
      byId('model-detail').close(); renderRows(); byId('runner-title').scrollIntoView({ behavior: 'smooth', block: 'start' });
    }));
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

  function renderOrganizationMetrics() {
    const summary = organizationData.summary || {};
    byId('org-existing-targets').textContent = Number(summary.existingBenchmarkTargets || 0).toLocaleString();
    byId('org-existing-providers').textContent = Number(summary.existingProviders || 0).toLocaleString();
    byId('org-alliance-members').textContent = Number(summary.allianceMembers || 0).toLocaleString();
    byId('org-records').textContent = Number(summary.organizationRecords || 0).toLocaleString();
    byId('org-live').textContent = Number(summary.liveOrganizationBenchmarks || 0).toLocaleString();
  }

  function renderOrganizationFilters() {
    [...new Set(organizationRecords.map((item) => item.organizationType).filter(Boolean))].sort().forEach((type) => {
      byId('organization-type').append(option(type, type.replaceAll('_', ' ')));
    });
    const needs = byId('organization-needs');
    (organizationData.userNeedTaxonomy || []).forEach((need, index) => {
      const label = document.createElement('label'); label.className = 'organization-need';
      const input = document.createElement('input'); input.type = 'checkbox'; input.value = need.id; input.checked = index < 5;
      const copy = document.createElement('span'); copy.textContent = need.description;
      label.append(input, copy); needs.append(label);
    });
  }

  function filteredOrganizations() {
    const query = byId('organization-search').value.trim().toLowerCase();
    const source = byId('organization-source').value;
    const type = byId('organization-type').value;
    return organizationRecords.filter((item) => {
      const haystack = [item.name, item.organizationType, ...(item.strengths || []), ...(item.commonUserJobs || []), ...(item.tools || [])].join(' ').toLowerCase();
      return (!query || haystack.includes(query)) && (source === 'all' || item.sourceKey === source) && (type === 'all' || item.organizationType === type);
    });
  }

  function organizationEvidence(item) {
    return item.capabilityEvidenceStatus || item.evidenceStatus || 'official_source_research_required';
  }

  function renderOrganizationRows() {
    visibleOrganizations = filteredOrganizations();
    const body = byId('organization-rows'); body.replaceChildren();
    visibleOrganizations.forEach((item) => {
      const row = document.createElement('tr');
      const selectCell = document.createElement('td');
      const checkbox = document.createElement('input'); checkbox.type = 'checkbox'; checkbox.checked = selectedOrganizations.has(item.id); checkbox.setAttribute('aria-label', `Include ${item.name}`);
      checkbox.addEventListener('change', () => { if (checkbox.checked) selectedOrganizations.add(item.id); else selectedOrganizations.delete(item.id); updateOrganizationSelected(); });
      selectCell.append(checkbox);

      const nameCell = document.createElement('td'); const copy = document.createElement('div'); copy.className = 'organization-copy';
      const button = document.createElement('button'); button.className = 'model-name-button'; button.type = 'button'; button.textContent = item.name; button.addEventListener('click', () => showOrganizationDetail(item.id));
      const type = document.createElement('span'); type.textContent = String(item.organizationType || 'unclassified').replaceAll('_', ' '); copy.append(button, type); nameCell.append(copy);
      const sourceCell = document.createElement('td'); const sourceTag = document.createElement('span'); sourceTag.className = 'organization-source-tag'; sourceTag.textContent = item.sourceKey === 'alliance' ? 'Alliance' : `Existing ${Number(organizationData.summary?.existingBenchmarkTargets || 0).toLocaleString()}`; sourceCell.append(sourceTag);
      const strengthCell = document.createElement('td'); strengthCell.className = 'organization-cell-note'; strengthCell.textContent = (item.strengths || []).slice(0, 3).join(', ') || 'Research required';
      const jobCell = document.createElement('td'); jobCell.className = 'organization-cell-note'; jobCell.textContent = (item.commonUserJobs || []).slice(0, 2).join('; ') || 'Research required';
      const evidenceCell = document.createElement('td'); evidenceCell.className = 'organization-cell-note organization-evidence'; evidenceCell.textContent = organizationEvidence(item).replaceAll('_', ' ');
      row.append(selectCell, nameCell, sourceCell, strengthCell, jobCell, evidenceCell); body.append(row);
    });
    byId('organization-count').textContent = `Showing ${visibleOrganizations.length.toLocaleString()} of ${organizationRecords.length.toLocaleString()} records. ${selectedOrganizations.size.toLocaleString()} selected.`;
    updateOrganizationSelected();
  }

  function updateOrganizationSelected() {
    byId('organization-selected-count').textContent = selectedOrganizations.size.toLocaleString();
  }

  function showOrganizationDetail(id) {
    const item = organizationRecords.find((record) => record.id === id);
    if (!item) return;
    byId('organization-detail-source').textContent = item.sourceKey === 'alliance' ? `Official directory snapshot · ${organizationData.snapshotDate}` : `Existing ${Number(organizationData.summary?.existingBenchmarkTargets || 0).toLocaleString()}-target catalog`;
    byId('organization-detail-title').textContent = item.name;
    const tools = (item.tools || []).length ? item.tools : ['No member-specific tool list is published in the directory; official-source research is required.'];
    const jobs = (item.commonUserJobs || []).length ? item.commonUserJobs : ['Official-source research required'];
    const strengths = (item.strengths || []).length ? item.strengths : ['Official-source research required'];
    const officialUrl = item.website || item.officialCatalogs?.[0] || '';
    const connectionUrl = officialUrl ? `connections.html?app=${encodeURIComponent(item.name)}&url=${encodeURIComponent(officialUrl)}&method=api_key` : 'connections.html';
    byId('organization-detail-body').innerHTML = `
      <p><strong>Evidence status:</strong> ${escapeHtml(organizationEvidence(item).replaceAll('_', ' '))}</p>
      <h3>Strengths to verify</h3><ul>${strengths.map((value) => `<li>${escapeHtml(value)}</li>`).join('')}</ul>
      <h3>Common user jobs</h3><ul>${jobs.map((value) => `<li>${escapeHtml(value)}</li>`).join('')}</ul>
      <h3>Known tools or targets</h3><ul>${tools.slice(0, 20).map((value) => `<li>${escapeHtml(value)}</li>`).join('')}</ul>
      <p>Membership does not prove capability, connection, access, price, or quality. Live comparison requires current official metadata and identical signed fixtures.</p>
      <a class="btn btn-outline btn-sm" href="${escapeHtml(connectionUrl)}">Prepare secure connection</a>`;
    byId('organization-detail').showModal();
  }

  function selectedOrganizationNeeds() {
    return [...document.querySelectorAll('#organization-needs input:checked')].map((input) => input.value);
  }

  function runOrganizationAudit() {
    const valid = organizationRecords.filter((item) => item.id && item.name && organizationEvidence(item) && Array.isArray(item.commonUserJobs)).length;
    const missing = organizationRecords.length - valid;
    byId('organization-status').textContent = `Catalog audit complete: ${valid} structurally ready, ${missing} invalid, ${organizationData.benchmarkDimensions?.length || 0} benchmark dimensions, and 0 live organization calls. Inferred categories remain research leads, not verified strengths.`;
  }

  function prepareOrganizationPlan() {
    const organizations = organizationRecords.filter((item) => selectedOrganizations.has(item.id));
    const needs = selectedOrganizationNeeds();
    if (!organizations.length || !needs.length) {
      byId('organization-status').textContent = 'Select at least one organization and one user need.';
      return;
    }
    const fixtures = Math.max(1, Math.min(20, Number(byId('organization-fixtures').value) || 1));
    const concurrency = Math.max(1, Math.min(32, Number(byId('organization-concurrency').value) || 1));
    const budget = Math.max(0, Math.min(10000, Number(byId('organization-budget').value) || 0));
    const allowNetwork = byId('organization-network').checked;
    const networkApproved = byId('organization-network-approval').checked;
    const paidApproved = byId('organization-paid').checked;
    const requiresResearch = organizations.some((item) => organizationEvidence(item).includes('research_required'));
    const status = allowNetwork && !networkApproved ? 'network_approval_required'
      : budget > 0 && !paidApproved ? 'paid_budget_approval_required'
      : allowNetwork && requiresResearch ? 'official_source_research_required'
      : allowNetwork ? 'configured_adapters_and_exact_versions_required' : 'local_catalog_plan_ready';
    const totalCases = organizations.length * needs.length * fixtures;
    latestOrganizationPlan = {
      schema: 'dreamco.organization_benchmark_plan.v1',
      createdAt: new Date().toISOString(),
      organizationIds: organizations.map((item) => item.id),
      userNeedIds: needs,
      organizationCount: organizations.length,
      userNeedCount: needs.length,
      signedFixturesPerNeed: fixtures,
      totalCases,
      maxConcurrency: concurrency,
      plannedWaves: Math.ceil(totalCases / concurrency),
      maximumPaidBudgetUsd: paidApproved ? budget : 0,
      networkApprovedForThisRun: allowNetwork && networkApproved,
      status,
      benchmarkDimensions: organizationData.benchmarkDimensions || [],
      rawCredentialsAccepted: false,
      executionPerformed: false,
      permanentBestClaimed: false,
    };
    const summary = byId('organization-plan-summary'); summary.replaceChildren();
    [['Organizations', organizations.length], ['User needs', needs.length], ['Total cases', totalCases], ['Concurrency', concurrency], ['Waves', latestOrganizationPlan.plannedWaves], ['Budget cap', `$${latestOrganizationPlan.maximumPaidBudgetUsd.toFixed(2)}`], ['Status', status.replaceAll('_', ' ')]].forEach(([label, value]) => {
      const dt = document.createElement('dt'); dt.textContent = String(label); const dd = document.createElement('dd'); dd.textContent = String(value); summary.append(dt, dd);
    });
    byId('organization-result').hidden = false;
    byId('organization-status').textContent = status === 'local_catalog_plan_ready' ? 'Local catalog plan ready. No network, provider, or member site was contacted.' : `Plan paused at ${status.replaceAll('_', ' ')}. No external action was performed.`;
  }

  function downloadOrganizationPlan() {
    if (!latestOrganizationPlan) return;
    const blob = new Blob([JSON.stringify(latestOrganizationPlan, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob); const link = document.createElement('a'); link.href = url; link.download = 'buddy-organization-benchmark-plan.json'; link.click(); URL.revokeObjectURL(url);
  }

  ['model-search', 'model-tier', 'model-category'].forEach((id) => byId(id).addEventListener(id === 'model-search' ? 'input' : 'change', renderRows));
  byId('select-visible').addEventListener('click', () => { visible.forEach((target) => selected.add(target.id)); renderRows(); });
  byId('clear-selection').addEventListener('click', () => { selected.clear(); renderRows(); });
  byId('run-catalog-audit').addEventListener('click', runCatalogAudit);
  byId('prepare-live-plan').addEventListener('click', preparePlan);
  byId('download-benchmark-plan').addEventListener('click', downloadPlan);
  byId('export-model-json').addEventListener('click', exportCatalogJson);
  byId('export-model-csv').addEventListener('click', exportCatalogCsv);
  byId('model-route-form').addEventListener('submit', prepareModelRoute);
  byId('demand-search').addEventListener('input', renderDemandReasons);
  byId('demand-category').addEventListener('change', renderDemandReasons);
  byId('model-detail-close').addEventListener('click', () => byId('model-detail').close());
  ['organization-search', 'organization-source', 'organization-type'].forEach((id) => byId(id).addEventListener(id === 'organization-search' ? 'input' : 'change', renderOrganizationRows));
  byId('organization-select-visible').addEventListener('click', () => { visibleOrganizations.forEach((item) => selectedOrganizations.add(item.id)); renderOrganizationRows(); });
  byId('organization-clear').addEventListener('click', () => { selectedOrganizations.clear(); renderOrganizationRows(); });
  byId('organization-audit').addEventListener('click', runOrganizationAudit);
  byId('organization-plan').addEventListener('click', prepareOrganizationPlan);
  byId('organization-download').addEventListener('click', downloadOrganizationPlan);
  byId('organization-detail-close').addEventListener('click', () => byId('organization-detail').close());

  renderMetrics();
  hydrateBackendConnectionState();
  renderDemandExplorer();
  renderFilters();
  renderSuites();
  renderRows();
  renderOrganizationMetrics();
  renderOrganizationFilters();
  renderOrganizationRows();
})();
