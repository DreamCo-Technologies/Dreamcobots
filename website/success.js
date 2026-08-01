(function () {
  'use strict';

  const program = window.BUDDY_SUCCESS_PROGRAM || { summary: {}, questionnaire: [], divisions: [], resource_inventory: { resources: [] }, model_program: { sources: [] }, weighted_ontology: { presets: {}, dimensions: [] } };
  const byId = (id) => document.getElementById(id);
  const profileKey = 'buddy-success-profile-v1';
  const trackerKey = 'buddy-growth-tracker-v1';
  const ontologyKey = 'buddy-weighted-ontology-v1';
  const money = new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 2 });
  let selectedPreset = 'balanced';

  function safeParse(key, fallback) {
    try { return JSON.parse(localStorage.getItem(key) || '') || fallback; } catch (_error) { return fallback; }
  }

  function controlFor(question, savedValue) {
    const label = document.createElement('label');
    label.className = 'success-field';
    label.append(document.createTextNode(question.label));
    let control;
    if (question.type === 'textarea') {
      control = document.createElement('textarea');
      control.rows = 3;
    } else if (question.type === 'select') {
      control = document.createElement('select');
      control.append(new Option('Choose one', ''));
      (question.options || []).forEach((value) => control.append(new Option(value, value)));
    } else {
      control = document.createElement('input');
      control.type = question.type === 'number' ? 'number' : 'text';
      if (control.type === 'number') { control.min = '0'; control.step = '1'; }
    }
    control.id = `question-${question.id}`;
    control.name = question.id;
    control.maxLength = 1000;
    control.required = Boolean(question.required);
    control.value = savedValue === undefined ? '' : String(savedValue);
    const help = document.createElement('small');
    help.textContent = question.help;
    label.append(control, help);
    return label;
  }

  function updateProfileProgress() {
    const answered = program.questionnaire.filter((question) => String(byId(`question-${question.id}`)?.value || '').trim()).length;
    byId('profile-progress').textContent = `${answered} of ${program.questionnaire.length} answered`;
  }

  function renderQuestionnaire() {
    const saved = safeParse(profileKey, { answers: {} });
    const target = byId('success-questionnaire');
    let section = '';
    program.questionnaire.forEach((question) => {
      if (question.section !== section) {
        section = question.section;
        const heading = document.createElement('h3');
        heading.className = 'questionnaire-section';
        heading.textContent = section;
        target.append(heading);
      }
      const field = controlFor(question, saved.answers?.[question.id]);
      field.querySelector('input, select, textarea').addEventListener('input', updateProfileProgress);
      target.append(field);
    });
    byId('profile-share').checked = Boolean(saved.shareWithBots);
    updateProfileProgress();
    if (saved.savedAt) byId('profile-status').textContent = `Saved on this device ${new Date(saved.savedAt).toLocaleString()}.`;
  }

  function profileAnswers() {
    return Object.fromEntries(program.questionnaire.flatMap((question) => {
      const raw = byId(`question-${question.id}`).value.trim();
      if (!raw) return [];
      return [[question.id, question.type === 'number' ? Number(raw) : raw]];
    }));
  }

  function saveProfile(event) {
    event.preventDefault();
    if (!byId('profile-no-secrets').checked) return;
    const answers = profileAnswers();
    const serialized = JSON.stringify(answers);
    if (/(password|passcode|secret|token|api.?key|social.?security|ssn|account.?number|private.?key)/i.test(serialized)) {
      byId('profile-status').textContent = 'Remove credentials, identifiers, account numbers, and secret keys before saving.';
      return;
    }
    const profile = {
      schema: 'dreamco.buddy_success_profile.v1',
      profileId: safeParse(profileKey, {}).profileId || `profile-${crypto.randomUUID()}`,
      answers,
      shareWithBots: byId('profile-share').checked,
      savedAt: new Date().toISOString(),
      storage: 'this_browser_only',
    };
    localStorage.setItem(profileKey, JSON.stringify(profile));
    byId('profile-status').textContent = profile.shareWithBots
      ? 'Saved locally. Buddy may include a short non-sensitive summary when routing specialists.'
      : 'Saved locally. Sharing with specialist routes is off.';
  }

  function growthRecords() {
    const rows = safeParse(trackerKey, []);
    return Array.isArray(rows) ? rows : [];
  }

  function saveGrowthRecords(rows) {
    localStorage.setItem(trackerKey, JSON.stringify(rows.slice(-500)));
    renderGrowthRecords();
  }

  function renderGrowthRecords() {
    const rows = growthRecords().sort((a, b) => String(b.createdAt).localeCompare(String(a.createdAt)));
    byId('tracker-ideas').textContent = rows.filter((row) => row.type === 'opportunity idea').length.toLocaleString();
    byId('tracker-assets').textContent = rows.filter((row) => row.type === 'owned asset').length.toLocaleString();
    byId('tracker-tests').textContent = rows.filter((row) => row.type === 'validation experiment' && !['completed', 'rejected', 'paused'].includes(row.status)).length.toLocaleString();
    const confirmedRevenue = rows.filter((row) => row.type === 'user-confirmed revenue' && row.evidence).reduce((sum, row) => sum + Number(row.confirmedValue || 0), 0);
    const timeSaved = rows.filter((row) => row.type === 'time saved').reduce((sum, row) => sum + Number(row.timeSavedHours || 0), 0);
    byId('tracker-revenue').textContent = money.format(confirmedRevenue);
    byId('tracker-time').textContent = `${timeSaved.toLocaleString()}h`;
    const target = byId('growth-record-list');
    target.replaceChildren();
    if (!rows.length) {
      const empty = document.createElement('p');
      empty.className = 'success-note';
      empty.textContent = 'No records yet. Start with one opportunity idea or an asset you already own.';
      target.append(empty);
      return;
    }
    rows.forEach((row) => {
      const article = document.createElement('article'); article.className = 'growth-record';
      const copy = document.createElement('div');
      const tag = document.createElement('span'); tag.className = 'record-tag'; tag.textContent = `${row.type} · ${row.status}`;
      const heading = document.createElement('h3'); heading.textContent = row.title;
      const evidence = document.createElement('p'); evidence.textContent = row.evidence || 'No evidence recorded yet.';
      const next = document.createElement('p'); next.textContent = row.nextAction ? `Next: ${row.nextAction}` : 'Next action not set.';
      const values = document.createElement('div'); values.className = 'record-values';
      values.textContent = `Estimate ${money.format(row.estimatedValue || 0)} · Confirmed ${money.format(row.confirmedValue || 0)} · Time ${Number(row.timeSavedHours || 0)}h`;
      copy.append(tag, heading, evidence, next, values);
      const remove = document.createElement('button'); remove.type = 'button'; remove.className = 'record-delete'; remove.textContent = 'Delete';
      remove.addEventListener('click', () => saveGrowthRecords(growthRecords().filter((item) => item.id !== row.id)));
      article.append(copy, remove); target.append(article);
    });
  }

  function addGrowthRecord(event) {
    event.preventDefault();
    const row = {
      schema: 'dreamco.buddy_growth_record.v1', id: `growth-${crypto.randomUUID()}`,
      type: byId('growth-type').value, title: byId('growth-title').value.trim(), status: byId('growth-status').value,
      estimatedValue: Number(byId('growth-estimate').value || 0), confirmedValue: Number(byId('growth-confirmed').value || 0),
      timeSavedHours: Number(byId('growth-hours').value || 0), evidence: byId('growth-evidence').value.trim(),
      nextAction: byId('growth-next').value.trim(), createdAt: new Date().toISOString(),
    };
    if (row.type === 'user-confirmed revenue' && row.confirmedValue > 0 && !row.evidence) {
      byId('growth-form-status').textContent = 'Add evidence or a source before recording confirmed revenue.';
      return;
    }
    saveGrowthRecords([...growthRecords(), row]);
    event.currentTarget.reset();
    byId('growth-estimate').value = '0'; byId('growth-confirmed').value = '0'; byId('growth-hours').value = '0';
    byId('growth-form-status').textContent = 'Record saved on this device.';
  }

  function downloadJson(name, value) {
    const url = URL.createObjectURL(new Blob([JSON.stringify(value, null, 2)], { type: 'application/json' }));
    const link = document.createElement('a'); link.href = url; link.download = name; link.click(); URL.revokeObjectURL(url);
  }

  function ontologyValues() {
    return Object.fromEntries(program.weighted_ontology.dimensions.map((dimension) => [dimension, Number(byId(`weight-${dimension}`).value)]));
  }

  function updateOntologyTotal() {
    const total = Object.values(ontologyValues()).reduce((sum, value) => sum + value, 0);
    byId('ontology-total').textContent = `${total} total`;
    program.weighted_ontology.dimensions.forEach((dimension) => { byId(`weight-output-${dimension}`).value = byId(`weight-${dimension}`).value; });
  }

  function applyPreset(name) {
    const weights = program.weighted_ontology.presets[name];
    if (!weights) return;
    selectedPreset = name;
    Object.entries(weights).forEach(([dimension, value]) => { byId(`weight-${dimension}`).value = String(value); });
    document.querySelectorAll('[data-ontology-preset]').forEach((button) => button.classList.toggle('active', button.dataset.ontologyPreset === name));
    updateOntologyTotal();
  }

  function renderOntology() {
    const presets = byId('ontology-presets');
    Object.keys(program.weighted_ontology.presets).forEach((name) => {
      const button = document.createElement('button'); button.type = 'button'; button.dataset.ontologyPreset = name;
      button.textContent = name.replaceAll('_', ' '); button.addEventListener('click', () => applyPreset(name)); presets.append(button);
    });
    const saved = safeParse(ontologyKey, null);
    const weights = saved?.weights || program.weighted_ontology.presets.balanced;
    selectedPreset = saved?.mode || 'balanced';
    const target = byId('ontology-weights');
    program.weighted_ontology.dimensions.forEach((dimension) => {
      const row = document.createElement('div'); row.className = 'ontology-weight';
      const label = document.createElement('label'); label.htmlFor = `weight-${dimension}`; label.textContent = dimension.replaceAll('_', ' ');
      const range = document.createElement('input'); range.id = `weight-${dimension}`; range.type = 'range'; range.min = ['evidence', 'safety'].includes(dimension) ? '10' : '0'; range.max = '50'; range.value = String(weights[dimension]);
      const output = document.createElement('output'); output.id = `weight-output-${dimension}`; output.htmlFor = range.id; output.value = range.value;
      range.addEventListener('input', () => { selectedPreset = 'custom'; document.querySelectorAll('[data-ontology-preset]').forEach((button) => button.classList.remove('active')); updateOntologyTotal(); });
      row.append(label, range, output); target.append(row);
    });
    document.querySelector(`[data-ontology-preset="${selectedPreset}"]`)?.classList.add('active');
    updateOntologyTotal();
  }

  function saveOntology(event) {
    event.preventDefault();
    const weights = ontologyValues();
    const total = Object.values(weights).reduce((sum, value) => sum + value, 0);
    if (total !== 100 || weights.evidence < 10 || weights.safety < 10) {
      byId('ontology-status').textContent = 'Weights must total 100; evidence and safety must each be at least 10.';
      return;
    }
    localStorage.setItem(ontologyKey, JSON.stringify({ schema: 'dreamco.buddy_weighted_ontology.v1', mode: selectedPreset, weights, savedAt: new Date().toISOString() }));
    byId('ontology-status').textContent = 'Weights saved on this device.';
  }

  function renderDivisionOptions() {
    program.divisions.forEach((division) => byId('division-program-select').append(new Option(division.name, division.name)));
    renderDivision();
  }

  function renderDivision() {
    const division = program.divisions.find((item) => item.name === byId('division-program-select').value) || program.divisions[0];
    if (!division) return;
    const kind = byId('division-program-kind').value;
    const query = byId('division-program-search').value.trim().toLowerCase();
    const definition = division[kind];
    const rows = (program.improvement_templates[kind] || []).map((template) => ({
      ...template,
      id: `${definition.id_prefix}-${template.id}`,
      objective: template.objective.replace('{division}', division.name),
    })).filter((row) => !query || `${row.title} ${row.objective}`.toLowerCase().includes(query));
    byId('division-name').textContent = division.name;
    byId('division-meta').textContent = `${division.profile_count} bot profiles · ${division.api_candidate_count} API candidates · ${division.top_categories.map((item) => item.name).join(', ')}`;
    byId('division-benchmark-status').textContent = 'Benchmark fixtures are defined. Live competitor runs have not started and no permanent best-in-category claim is made.';
    byId('division-program-count').textContent = `${rows.length} of 100 shown`;
    window.DREAMCO_ROBOT_AVATAR.renderInto(byId('division-robot'), { seed: division.robot_identity.deterministic_seed, division: division.name, category: division.top_categories[0]?.name || 'system' });
    const dimensions = byId('division-benchmark-dimensions'); dimensions.replaceChildren();
    division.benchmark_system.dimensions.forEach((name) => { const chip = document.createElement('span'); chip.textContent = name; dimensions.append(chip); });
    const target = byId('division-improvement-list'); target.replaceChildren();
    rows.forEach((row) => {
      const article = document.createElement('article'); article.className = 'improvement-row';
      const number = document.createElement('span'); number.textContent = String(row.number).padStart(3, '0');
      const copy = document.createElement('div'); const heading = document.createElement('h4'); heading.textContent = row.title;
      const detail = document.createElement('p'); detail.textContent = row.objective; copy.append(heading, detail); article.append(number, copy); target.append(article);
    });
  }

  function renderModels() {
    const modelProgram = program.model_program;
    byId('model-program-summary').textContent = `${modelProgram.curated_catalog_targets} curated catalog targets plus ${modelProgram.dynamic_discovery_targets} task-specific discovery lanes from ${modelProgram.sources.length} official catalogs. Exact model IDs, access, versions, prices, and quality are refreshed at run time; this is not a permanent ranking.`;
    const target = byId('model-source-list');
    modelProgram.sources.forEach((source) => {
      const row = document.createElement('a'); row.className = 'model-source-row'; row.href = source.catalog; row.target = '_blank'; row.rel = 'noopener';
      const name = document.createElement('strong'); name.textContent = source.provider;
      const detail = document.createElement('span'); detail.textContent = `${source.region} · official catalog · 10 task lanes`; row.append(name, detail); target.append(row);
    });
  }

  function renderResources() {
    const query = byId('resource-search').value.trim().toLowerCase();
    const status = byId('resource-status').value;
    const rows = program.resource_inventory.resources.filter((resource) => (!query || resource.host.includes(query)) && (status === 'all' || resource.status === status));
    byId('resource-ledger-count').textContent = `${rows.length} of ${program.resource_inventory.resources.length} shown`;
    const target = byId('resource-list'); target.replaceChildren();
    rows.forEach((resource) => {
      const row = document.createElement('article'); row.className = 'resource-row';
      const name = document.createElement('strong'); name.textContent = resource.host;
      const state = document.createElement('span'); state.className = 'resource-status'; state.textContent = resource.status.replaceAll('_', ' ');
      const detail = document.createElement('span'); detail.textContent = `${resource.mention_count} repository mentions · ${resource.next_step}`;
      row.append(name, state, detail); target.append(row);
    });
  }

  function renderSummary() {
    byId('success-profile-count').textContent = Number(program.summary.profiles_routed || 0).toLocaleString();
    byId('success-division-count').textContent = Number(program.summary.divisions || 0).toLocaleString();
    byId('success-model-count').textContent = Number(program.summary.model_benchmark_targets || 0).toLocaleString();
    byId('success-resource-count').textContent = Number(program.summary.referenced_resource_hosts || 0).toLocaleString();
    byId('success-live-count').textContent = Number(program.summary.verified_live_resource_hosts || 0).toLocaleString();
  }

  byId('success-profile-form').addEventListener('submit', saveProfile);
  byId('profile-clear').addEventListener('click', () => { localStorage.removeItem(profileKey); location.reload(); });
  byId('growth-record-form').addEventListener('submit', addGrowthRecord);
  byId('tracker-export').addEventListener('click', () => downloadJson('buddy-growth-tracker.json', growthRecords()));
  byId('ontology-form').addEventListener('submit', saveOntology);
  ['division-program-select', 'division-program-kind'].forEach((id) => byId(id).addEventListener('change', renderDivision));
  byId('division-program-search').addEventListener('input', renderDivision);
  byId('resource-search').addEventListener('input', renderResources);
  byId('resource-status').addEventListener('change', renderResources);

  renderSummary(); renderQuestionnaire(); renderGrowthRecords(); renderOntology(); renderDivisionOptions(); renderModels(); renderResources();
})();
