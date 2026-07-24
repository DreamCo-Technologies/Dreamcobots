const PAGE_SIZE = 36;
const state = {
  catalog: null,
  filtered: [],
  page: 1,
  divisionCache: new Map(),
  capabilityShardCache: new Map(),
  certifications: new Map(),
  capabilityContract: null,
  activeBot: null,
  activeCertification: null,
};
const numberFormat = new Intl.NumberFormat('en-US');

const grid = document.getElementById('bots-grid');
const results = document.getElementById('fleet-results');
const empty = document.getElementById('fleet-empty');
const pagination = document.getElementById('fleet-pagination');
const dialog = document.getElementById('bot-prospectus');
const dialogContent = document.getElementById('prospectus-content');

function escapeHtml(value) {
  return String(value ?? '')
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#39;');
}

function logoStyle(logo) {
  const radius = logo.shape === 'circle' ? '50%' : logo.shape === 'hex' ? '16px 6px' : logo.shape === 'shield' ? '8px 8px 18px 18px' : '8px';
  return `--logo-primary:${logo.colors.primary};--logo-accent:${logo.colors.accent};--logo-surface:${logo.colors.surface};--logo-radius:${radius}`;
}

function botLogo(bot) {
  return `<div class="fleet-logo" style="${logoStyle(bot.logo)}" role="img" aria-label="${escapeHtml(bot.logo.accessibility_label)}">${escapeHtml(bot.logo.monogram)}<span aria-hidden="true">${bot.logo.emoji}</span></div>`;
}

function testUrl(bot) {
  return `buddy.html?bot=${encodeURIComponent(bot.identity.slug)}&prompt=${encodeURIComponent(bot.sample_test_prompt)}`;
}

function capabilityTestUrl(bot, capability) {
  const prompt = `Test ${bot.identity.display_name} capability "${capability}" in sandbox mode. Use synthetic data, show inputs, execution steps, output, and test evidence. Stop before any live external action.`;
  return `buddy.html?bot=${encodeURIComponent(bot.identity.slug)}&prompt=${encodeURIComponent(prompt)}`;
}

function calculatorUrl(bot) {
  return `calculator.html?bot=${encodeURIComponent(bot.identity.slug)}`;
}

function renderCard(bot) {
  const apiLabel = bot.api_candidate_count ? `${bot.api_candidate_count} candidates` : 'No API catalog';
  const certification = state.certifications.get(bot.identity.slug);
  const passedTests = certification?.capabilityTestsPassed ?? 0;
  const expectedTests = certification?.declaredCapabilityCount ?? bot.capability_count;
  const testLabel = certification ? `${passedTests}/${expectedTests}` : 'Unavailable';
  const certificationReady = certification?.status === 'sandbox_certified' && passedTests === expectedTests;
  return `<article class="fleet-card" data-slug="${escapeHtml(bot.identity.slug)}">
    <div class="fleet-card-head">
      ${botLogo(bot)}
      <div class="fleet-card-title"><h2>${escapeHtml(bot.identity.display_name)}</h2><p>${escapeHtml(bot.identity.division)} · ${escapeHtml(bot.identity.category)}</p></div>
      <span class="fleet-tier">${escapeHtml(bot.identity.tier)}</span>
    </div>
    <p class="fleet-call-sign">${escapeHtml(bot.logo.call_sign)}</p>
    <p class="fleet-mission">${escapeHtml(bot.mission)}</p>
    <div class="fleet-evidence">
      <div><span>Capabilities</span><strong>${bot.capability_count}</strong></div>
      <div><span>Tests passed</span><strong>${escapeHtml(testLabel)}</strong></div>
      <div><span>Tools</span><strong>${bot.tool_summary.length}</strong></div>
      <div><span>APIs</span><strong title="${escapeHtml(apiLabel)}">${escapeHtml(apiLabel)}</strong></div>
    </div>
    <div class="fleet-readiness ${certificationReady ? '' : 'is-warning'}"><span></span> ${certificationReady ? 'Every capability contract passed' : 'Capability evidence unavailable or incomplete'}</div>
    <div class="fleet-card-actions">
      <button class="btn btn-outline btn-sm" type="button" data-action="prospectus" data-slug="${escapeHtml(bot.identity.slug)}">Capabilities</button>
      <a class="btn btn-outline btn-sm" href="${calculatorUrl(bot)}">Calculator</a>
      <a class="btn btn-primary btn-sm" href="${testUrl(bot)}">Test with Buddy</a>
    </div>
  </article>`;
}

function filterCatalog() {
  if (!state.catalog) return;
  const query = document.getElementById('bot-search').value.trim().toLowerCase();
  const division = document.getElementById('division-filter').value;
  const tier = document.getElementById('tier-filter').value;
  const readiness = document.getElementById('readiness-filter').value;
  state.filtered = state.catalog.bots.filter((bot) => {
    const haystack = `${bot.identity.display_name} ${bot.identity.slug} ${bot.identity.division} ${bot.identity.category} ${bot.mission} ${bot.capability_search} ${bot.api_candidate_names.join(' ')}`.toLowerCase();
    if (query && !haystack.includes(query)) return false;
    if (division !== 'all' && bot.identity.division !== division) return false;
    if (tier !== 'all' && bot.identity.tier !== tier) return false;
    if (readiness === 'routed' && bot.readiness.buddy_chat_route !== 'verified') return false;
    if (readiness === 'adapter' && bot.readiness.external_integrations !== 'configuration_required') return false;
    if (readiness === 'no-api' && bot.readiness.external_integrations !== 'no_division_api_catalog') return false;
    return true;
  });
  state.page = 1;
  renderPage();
}

function renderPage() {
  const totalPages = Math.max(1, Math.ceil(state.filtered.length / PAGE_SIZE));
  state.page = Math.min(state.page, totalPages);
  const start = (state.page - 1) * PAGE_SIZE;
  const visible = state.filtered.slice(start, start + PAGE_SIZE);
  grid.innerHTML = visible.map(renderCard).join('');
  empty.hidden = state.filtered.length !== 0;
  results.textContent = state.filtered.length
    ? `Showing ${numberFormat.format(start + 1)}-${numberFormat.format(start + visible.length)} of ${numberFormat.format(state.filtered.length)} matching profiles`
    : 'No matching profiles';
  renderPagination(totalPages);
}

function renderPagination(totalPages) {
  if (state.filtered.length <= PAGE_SIZE) {
    pagination.innerHTML = '';
    return;
  }
  const candidates = new Set([1, totalPages, state.page - 1, state.page, state.page + 1]);
  const pages = [...candidates].filter((page) => page >= 1 && page <= totalPages).sort((a, b) => a - b);
  const controls = [`<button class="fleet-page-button" data-page="${state.page - 1}" ${state.page === 1 ? 'disabled' : ''} aria-label="Previous page">‹</button>`];
  let previous = 0;
  for (const page of pages) {
    if (page - previous > 1) controls.push('<span aria-hidden="true">…</span>');
    controls.push(`<button class="fleet-page-button" data-page="${page}" ${page === state.page ? 'aria-current="page"' : ''}>${page}</button>`);
    previous = page;
  }
  controls.push(`<button class="fleet-page-button" data-page="${state.page + 1}" ${state.page === totalPages ? 'disabled' : ''} aria-label="Next page">›</button>`);
  pagination.innerHTML = controls.join('');
}

async function loadDivision(name) {
  if (!state.divisionCache.has(name)) {
    state.divisionCache.set(name, fetch(`data/bot-fleet/${encodeURIComponent(name)}.json`, { cache: 'no-store' })
      .then((response) => {
        if (!response.ok) throw new Error(`Prospectus data returned ${response.status}`);
        return response.json();
      }));
  }
  return state.divisionCache.get(name);
}

async function loadCapabilityDivision(name) {
  if (!state.capabilityShardCache.has(name)) {
    state.capabilityShardCache.set(name, fetch(`data/bot-capability-tests/${encodeURIComponent(name)}.json`, { cache: 'no-store' })
      .then((response) => {
        if (!response.ok) throw new Error(`Capability certification data returned ${response.status}`);
        return response.json();
      }));
  }
  return state.capabilityShardCache.get(name);
}

function list(items) {
  return `<div class="prospectus-list">${items.map((item) => `<span>${escapeHtml(typeof item === 'string' ? item : item.name)}</span>`).join('')}</div>`;
}

function keyValues(entries) {
  return `<dl class="prospectus-kv">${entries.map(([key, value]) => `<dt>${escapeHtml(key)}</dt><dd>${escapeHtml(value)}</dd>`).join('')}</dl>`;
}

function humanize(value) {
  return String(value)
    .replace(/([a-z])([A-Z])/g, '$1 $2')
    .replaceAll('_', ' ')
    .replace(/^./, (letter) => letter.toUpperCase());
}

function capabilityRows(bot, certification) {
  const tests = new Map((certification?.capabilityTests ?? []).map((test) => [test.capability, test]));
  return bot.capabilities.map((capability) => {
    const test = tests.get(capability.name);
    const passed = test?.status === 'sandbox_contract_passed';
    return `<tr data-capability="${encodeURIComponent(capability.name)}">
      <td class="capability-name"><strong>${escapeHtml(capability.name)}</strong><small>${escapeHtml(capability.source)}</small></td>
      <td><span class="capability-test-state ${passed ? 'passed' : 'failed'}">${passed ? 'Sandbox contract passed' : 'Test evidence unavailable'}</span></td>
      <td><button class="capability-test-button" type="button" data-action="test-capability" data-capability="${encodeURIComponent(capability.name)}">Run test</button></td>
    </tr>`;
  }).join('');
}

function renderProspectus(bot, certification) {
  const apiRows = bot.api_candidates.length ? bot.api_candidates.map((api) => `<tr><td>${escapeHtml(api.name)}</td><td>${escapeHtml(api.category)}</td><td>Configuration + sandbox required</td></tr>`).join('') : '<tr><td colspan="3">This division does not yet have an API candidate catalog.</td></tr>';
  const toolRows = bot.tools.map((tool) => `<tr><td>${escapeHtml(tool.name)}</td><td>${escapeHtml(tool.status.replaceAll('_', ' '))}</td><td>${escapeHtml(tool.evidence)}</td></tr>`).join('');
  const passedTests = certification?.capabilityTests.filter((test) => test.status === 'sandbox_contract_passed').length ?? 0;
  const totalTests = certification?.declaredCapabilityCount ?? bot.capabilities.length;
  state.activeBot = bot;
  state.activeCertification = certification ?? null;
  dialogContent.innerHTML = `<div class="prospectus-hero">
      ${botLogo(bot)}
      <div><h2>${escapeHtml(bot.identity.display_name)}</h2><p>${escapeHtml(bot.prospectus.mission)}</p><p class="fleet-call-sign">${escapeHtml(bot.logo.call_sign)} · ${escapeHtml(bot.identity.division)} / ${escapeHtml(bot.identity.category)}</p></div>
      <span class="prospectus-status ${passedTests === totalTests ? 'passed' : ''}">${passedTests}/${totalTests} sandbox contracts passed</span>
    </div>
    <div class="prospectus-sections">
      <section class="prospectus-section">
        <h3>Business prospectus</h3>
        ${keyValues([
          ['Target users', bot.prospectus.target_users],
          ['Catalog model', bot.prospectus.catalog_business_model],
          ['Catalog price', bot.prospectus.catalog_price_range],
          ['Pricing evidence', 'Plan only; revenue is not verified'],
        ])}
      </section>
      <section class="prospectus-section">
        <h3>Readiness evidence</h3>
        ${keyValues([
          ['Profile schema', bot.readiness.profile_schema],
          ['Buddy chat route', bot.readiness.buddy_chat_route],
          ['Executable runtime instance', bot.readiness.executable_runtime_instance],
          ['Runtime architecture', bot.readiness.standalone_native_runtime],
          ['External integrations', bot.readiness.external_integrations],
          ['Catalog source', bot.evidence.catalog_source],
        ])}
      </section>
      <section class="prospectus-section wide capability-lab">
        <h3>Capabilities and sandbox contract tests</h3>
        <p class="prospectus-note">These tests verify each declared capability is registered, routed through the governed runtime, evidence-gated, network-off by default, and unable to take a live external action. Provider behavior still requires a configured adapter and provider sandbox.</p>
        <div class="capability-table-wrap">
          <table class="prospectus-table capability-table"><thead><tr><th>Capability</th><th>Repository test</th><th>Action</th></tr></thead><tbody>${capabilityRows(bot, certification)}</tbody></table>
        </div>
        <div id="capability-test-result" class="capability-test-result" aria-live="polite">
          <strong>Select a capability test</strong>
          <p>Each result is checked against the generated fleet certificate. Nothing is sent or published.</p>
        </div>
      </section>
      <section class="prospectus-section wide">
        <h3>Platform tools</h3>
        <table class="prospectus-table"><thead><tr><th>Tool</th><th>State</th><th>Evidence</th></tr></thead><tbody>${toolRows}</tbody></table>
      </section>
      <section class="prospectus-section wide">
        <h3>API candidates</h3>
        <p class="prospectus-note">Candidates are not connected APIs. Each one requires an owner-selected provider, backend secret reference, contract test, rate-limit handling, and explicit approval for live actions.</p>
        <table class="prospectus-table"><thead><tr><th>API</th><th>Category</th><th>State</th></tr></thead><tbody>${apiRows}</tbody></table>
      </section>
      <section class="prospectus-section">
        <h3>Data contract</h3>
        ${keyValues([
          ['Sensitivity', bot.data_contract.sensitivity],
          ['Storage', bot.data_contract.storage_policy],
          ['Retention', bot.data_contract.retention],
        ])}
      </section>
      <section class="prospectus-section">
        <h3>Approval policy</h3>
        ${keyValues([
          ['Default', bot.approvals.default_mode],
          ['Approval needed', bot.approvals.approval_required ? 'Yes for matched high-impact work' : 'Yes for any live external write or publish'],
          ['Channels', bot.approvals.channels_supported.join(', ')],
          ['Contact rule', bot.approvals.contact_requirement],
        ])}
      </section>
      <section class="prospectus-section wide">
        <h3>Sandbox bootcamp</h3>
        ${list(bot.sandbox.checks)}
        <p class="prospectus-note">Release gate: ${escapeHtml(bot.sandbox.release_gate)}. Production gate: ${escapeHtml(bot.readiness.production_gate)}</p>
      </section>
    </div>
    <div class="prospectus-actions">
      <a class="btn btn-outline" href="${testUrl(bot)}">Load test prompt</a>
      <a class="btn btn-outline" href="${calculatorUrl(bot)}">Open calculator</a>
      <a class="btn btn-primary" href="${testUrl(bot)}">Test with Buddy</a>
    </div>`;
}

function runCapabilityTest(capability) {
  const bot = state.activeBot;
  const certification = state.activeCertification;
  const result = document.getElementById('capability-test-result');
  if (!bot || !result) return;
  const declared = bot.capabilities.find((item) => item.name === capability);
  const test = certification?.capabilityTests.find((item) => item.capability === capability);
  const passed = Boolean(
    declared &&
    test &&
    declared.test_id === test.testId &&
    test.status === 'sandbox_contract_passed' &&
    !test.failures?.length &&
    test.liveExternalActionTaken === false &&
    state.capabilityContract?.checks?.length > 0
  );
  const checks = test && state.capabilityContract
    ? state.capabilityContract.checks.map((check) => {
      const value = !test.failures?.includes(check.id);
      return `<li><span class="${value ? 'passed' : 'failed'}">${value ? 'Passed' : 'Failed'}</span><strong>${escapeHtml(check.label ?? humanize(check.id))}</strong></li>`;
    }).join('')
    : '<li><span class="failed">Failed</span><strong>Certification record found</strong></li>';
  result.className = `capability-test-result ${passed ? 'passed' : 'failed'}`;
  result.innerHTML = `<div class="capability-result-head">
      <div><span>${passed ? 'Sandbox contract passed' : 'Sandbox contract failed'}</span><strong>${escapeHtml(capability)}</strong></div>
      <a class="btn btn-primary btn-sm" href="${capabilityTestUrl(bot, capability)}">Test with Buddy</a>
    </div>
    <ul class="capability-checks">${checks}</ul>
    <p>Test ID: <code>${escapeHtml(test?.testId ?? declared?.test_id ?? 'missing')}</code>. Evidence contract: <code>${escapeHtml(state.capabilityContract?.requiredEvidence?.join(', ') ?? 'missing')}</code>. Live external action taken: <strong>${test?.liveExternalActionTaken === false ? 'No' : 'Unknown'}</strong>.</p>`;
  const row = dialogContent.querySelector(`tr[data-capability="${CSS.escape(encodeURIComponent(capability))}"]`);
  row?.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

async function openProspectus(slug) {
  const indexBot = state.catalog.bots.find((bot) => bot.identity.slug === slug);
  if (!indexBot) return;
  dialogContent.innerHTML = '<p>Loading repository prospectus...</p>';
  dialog.showModal();
  try {
    const [division, capabilityDivision] = await Promise.all([
      loadDivision(indexBot.identity.division),
      loadCapabilityDivision(indexBot.identity.division),
    ]);
    const bot = division.bots.find((item) => item.identity.slug === slug);
    const certification = capabilityDivision.profiles.find((item) => item.slug === slug);
    if (!bot) throw new Error('Bot prospectus was not found in its division shard.');
    if (!certification) throw new Error('Bot capability certification was not found in its division shard.');
    renderProspectus(bot, certification);
  } catch (error) {
    dialogContent.innerHTML = `<p class="prospectus-note">${escapeHtml(error.message)}</p>`;
  }
}

async function initialize() {
  try {
    const [catalogResponse, certificationResponse] = await Promise.all([
      fetch('data/bot-fleet-catalog.json', { cache: 'no-store' }),
      fetch('data/bot-fleet-e2e.json', { cache: 'no-store' }),
    ]);
    if (!catalogResponse.ok) throw new Error(`Fleet catalog returned ${catalogResponse.status}`);
    if (!certificationResponse.ok) throw new Error(`Fleet certification returned ${certificationResponse.status}`);
    state.catalog = await catalogResponse.json();
    const certification = await certificationResponse.json();
    state.certifications = new Map(certification.profiles.map((profile) => [profile.slug, profile]));
    state.capabilityContract = certification.capabilityTestContract;
    const summary = state.catalog.summary;
    if (summary.profiles !== certification.summary.profilesTested) throw new Error('Fleet catalog and certification profile counts do not match');
    if (summary.declared_capability_slots !== certification.summary.declaredCapabilitiesTested) throw new Error('Fleet capability counts do not match certification evidence');
    document.getElementById('fleet-profile-count').textContent = numberFormat.format(summary.profiles);
    document.getElementById('fleet-division-count').textContent = numberFormat.format(summary.divisions);
    document.getElementById('fleet-capability-count').textContent = numberFormat.format(summary.declared_capability_slots);
    document.getElementById('fleet-capability-test-count').textContent = numberFormat.format(certification.summary.sandboxCapabilityTestsPassed);
    document.getElementById('fleet-route-count').textContent = numberFormat.format(summary.runtime_routed_profiles);
    document.getElementById('fleet-capability-failure-count').textContent = numberFormat.format(certification.summary.sandboxCapabilityTestsFailed);
    const divisionFilter = document.getElementById('division-filter');
    divisionFilter.insertAdjacentHTML('beforeend', state.catalog.divisions.map((division) => `<option value="${escapeHtml(division.name)}">${escapeHtml(division.name)} (${division.profile_count})</option>`).join(''));
    state.filtered = [...state.catalog.bots];
    renderPage();
    const requestedProspectus = new URLSearchParams(location.search).get('prospectus');
    if (requestedProspectus) openProspectus(requestedProspectus);
  } catch (error) {
    results.textContent = `Fleet catalog unavailable: ${error.message}`;
    empty.hidden = false;
  }
}

['bot-search', 'division-filter', 'tier-filter', 'readiness-filter'].forEach((id) => {
  document.getElementById(id).addEventListener(id === 'bot-search' ? 'input' : 'change', filterCatalog);
});
document.getElementById('clear-filters').addEventListener('click', () => {
  document.getElementById('bot-search').value = '';
  document.getElementById('division-filter').value = 'all';
  document.getElementById('tier-filter').value = 'all';
  document.getElementById('readiness-filter').value = 'all';
  filterCatalog();
});
grid.addEventListener('click', (event) => {
  const button = event.target.closest('[data-action="prospectus"]');
  if (button) openProspectus(button.dataset.slug);
});
pagination.addEventListener('click', (event) => {
  const button = event.target.closest('[data-page]');
  if (!button || button.disabled) return;
  state.page = Number(button.dataset.page);
  renderPage();
  document.querySelector('.fleet-results-bar').scrollIntoView({ behavior: 'smooth', block: 'start' });
});
document.getElementById('close-prospectus').addEventListener('click', () => dialog.close());
dialog.addEventListener('click', (event) => {
  if (event.target === dialog) dialog.close();
});
dialogContent.addEventListener('click', (event) => {
  const button = event.target.closest('[data-action="test-capability"]');
  if (!button) return;
  runCapabilityTest(decodeURIComponent(button.dataset.capability));
});

initialize();
