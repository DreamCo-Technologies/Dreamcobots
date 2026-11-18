(() => {
  'use strict';
  const STORAGE_KEY = 'dreamco.buddy-bootcamp.resources.v1';
  const byId = (id) => document.getElementById(id);
  const readState = () => {
    try {
      const value = JSON.parse(localStorage.getItem(STORAGE_KEY) || '{}');
      return {
        selected: Array.isArray(value.selected) ? value.selected.filter((id) => typeof id === 'string') : [],
        custom: Array.isArray(value.custom) ? value.custom.filter((item) => item && typeof item.id === 'string' && typeof item.name === 'string' && isSafeResourceUrl(item.url)) : [],
      };
    } catch {
      return { selected: [], custom: [] };
    }
  };
  const writeState = (state) => localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
  const download = (filename, payload) => {
    const blob = new Blob([JSON.stringify(payload, null, 2) + '\n'], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement('a');
    anchor.href = url;
    anchor.download = filename;
    anchor.click();
    URL.revokeObjectURL(url);
  };

  function isSafeResourceUrl(raw) {
    try {
      const url = new URL(raw);
      const sensitiveParameters = /^(?:api[_-]?key|access[_-]?token|auth|authorization|code|credential|password|secret|signature|token)$/i;
      return url.protocol === 'https:' && !url.username && !url.password && !url.hash &&
        ![...url.searchParams.keys()].some((key) => sensitiveParameters.test(key));
    } catch { return false; }
  }

  let catalog = null;
  let renderedRows = [];
  let visibleRows = [];
  let visibleLimit = 180;
  const state = readState();
  const list = byId('bootcamp-resource-list');
  const categoryFilter = byId('bootcamp-resource-category');
  const search = byId('bootcamp-resource-search');
  const summary = byId('bootcamp-resource-summary');
  const CATEGORIES = new Set();

  function selectedResources() {
    const byResource = new Map([...(catalog?.resources || []), ...state.custom].map((resource) => [resource.id, resource]));
    return state.selected.map((id) => byResource.get(id)).filter(Boolean);
  }

  function render() {
    if (!catalog) return;
    const query = search.value.trim().toLowerCase();
    const category = categoryFilter.value;
    const allResources = [...catalog.resources, ...state.custom];
    renderedRows = allResources.filter((resource) => isSafeResourceUrl(resource.url) &&
      (category === 'all' || resource.category === category) &&
      (!query || `${resource.name} ${resource.url} ${resource.category_label} ${(resource.source_lists || []).join(' ')}`.toLowerCase().includes(query))
    );
    visibleRows = renderedRows.slice(0, visibleLimit);
    list.replaceChildren();
    visibleRows.forEach((resource) => {
      const card = document.createElement('article');
      card.className = 'card';
      const label = document.createElement('label');
      const checkbox = document.createElement('input');
      checkbox.type = 'checkbox';
      checkbox.value = resource.id;
      checkbox.checked = state.selected.includes(resource.id);
      checkbox.dataset.resourceId = resource.id;
      const heading = document.createElement('strong');
      heading.textContent = ` ${resource.name}`;
      label.append(checkbox, heading);
      const categoryText = document.createElement('p');
      categoryText.textContent = resource.category_label;
      const status = document.createElement('p');
      status.textContent = `Connection: ${resource.connection_status || 'reference only'} · rights: ${resource.rights_status || 'unknown'} · live verified: ${resource.live_verified ? 'yes' : 'no'}`;
      const link = document.createElement('a');
      link.href = resource.url;
      link.target = '_blank';
      link.rel = 'noopener noreferrer';
      link.textContent = 'Review source';
      card.append(label, categoryText, status, link);
      list.append(card);
    });
    const more = byId('bootcamp-resource-more');
    more.hidden = renderedRows.length <= visibleLimit;
    if (renderedRows.length > visibleLimit) {
      const notice = document.createElement('p');
      notice.textContent = `Showing ${visibleRows.length} of ${renderedRows.length} matches.`;
      list.append(notice);
    }
    const picked = selectedResources();
    summary.textContent = `${catalog.resource_count + state.custom.length} resources in ${catalog.category_count} categories. ${renderedRows.length} match this filter; ${picked.length} selected. Choices save in this browser only.`;
  }

  fetch('data/buddy-bootcamp-resource-catalog.json', { cache: 'no-store' })
    .then((response) => { if (!response.ok) throw new Error('catalog unavailable'); return response.json(); })
    .then((data) => {
      catalog = data;
      data.categories.forEach((category) => {
        CATEGORIES.add(category.id);
        const option = document.createElement('option');
        option.value = category.id;
        option.textContent = `${category.label} (${category.count})`;
        categoryFilter.append(option);
        const customOption = option.cloneNode(true);
        byId('bootcamp-custom-category').append(customOption);
      });
      state.custom = state.custom.filter((resource) => isSafeResourceUrl(resource.url) && CATEGORIES.has(resource.category));
      state.selected = state.selected.filter((id) => data.resources.some((resource) => resource.id === id) || state.custom.some((resource) => resource.id === id));
      writeState(state);
      render();
    })
    .catch(() => { summary.textContent = 'Resource catalog unavailable. No bootcamp choices were changed.'; });

  const resetAndRender = () => { visibleLimit = 180; render(); };
  search.addEventListener('input', resetAndRender);
  categoryFilter.addEventListener('change', resetAndRender);
  byId('bootcamp-resource-more').addEventListener('click', () => { visibleLimit += 180; render(); });
  list.addEventListener('change', (event) => {
    const id = event.target.dataset.resourceId;
    if (!id) return;
    state.selected = event.target.checked
      ? [...new Set([...state.selected, id])]
      : state.selected.filter((item) => item !== id);
    writeState(state);
    render();
  });
  byId('bootcamp-select-visible').addEventListener('click', () => {
    state.selected = [...new Set([...state.selected, ...visibleRows.map((resource) => resource.id)])];
    writeState(state);
    render();
  });
  byId('bootcamp-clear-selection').addEventListener('click', () => {
    state.selected = [];
    writeState(state);
    render();
  });
  byId('bootcamp-add-custom').addEventListener('click', () => {
    const name = byId('bootcamp-custom-name').value.replace(/\s+/g, ' ').trim();
    const url = byId('bootcamp-custom-url').value.trim();
    const category = byId('bootcamp-custom-category').value;
    if (!name || name.length > 100 || !isSafeResourceUrl(url) || !CATEGORIES.has(category)) {
      summary.textContent = 'Enter a short name, an HTTPS URL without credentials, and a listed category. Do not enter secrets.';
      return;
    }
    if (state.custom.some((resource) => resource.url === url)) {
      summary.textContent = 'That custom URL is already in your browser catalog.';
      return;
    }
    const categoryLabel = catalog.categories.find((item) => item.id === category)?.label || 'Other / needs review';
    const id = `custom:${globalThis.crypto?.randomUUID?.() || Date.now()}`;
    state.custom.push({
      id, name, url, category, category_label: categoryLabel, category_evidence: 'user_labeled',
      resource_kind: 'user_added_reference', connection_status: 'local_reference_only', rights_status: 'unknown',
      training_allowed: false, live_verified: false, selection_available: true, source_lists: [],
    });
    state.selected = [...new Set([...state.selected, id])];
    writeState(state);
    byId('bootcamp-custom-name').value = '';
    byId('bootcamp-custom-url').value = '';
    render();
    summary.textContent = `${name} added to this browser and selected. It remains an unverified reference until separately reviewed.`;
  });
  byId('bootcamp-export-resources').addEventListener('click', () => {
    if (!catalog) return;
    download('buddy-bootcamp-resource-selection.json', {
      schema: 'dreamco.buddy_bootcamp_resource_selection.v1',
      selected_at: new Date().toISOString(),
      selected_resources: selectedResources().map(({ id, name, url, category, connection_status, rights_status }) =>
        ({ id, name, url, category, connection_status, rights_status })),
      training_enabled: false,
      external_actions_enabled: false,
    });
  });
  byId('bootcamp-export-plan').addEventListener('click', () => {
    if (!catalog) return;
    const goals = byId('bootcamp-goals').value.split('\n').map((value) => value.trim()).filter(Boolean);
    if (!goals.length) {
      byId('bootcamp-plan-status').textContent = 'Enter at least one learning goal before exporting the plan.';
      return;
    }
    const resources = selectedResources();
    const benchmarkIds = byId('bootcamp-benchmarks').value.split(',').map((value) => value.trim()).filter(Boolean);
    download('buddy-bootcamp-plan.json', {
      schema: 'dreamco.buddy_bootcamp_user_plan.v1',
      goals,
      selected_resources: resources.map(({ id, name, url, category, connection_status }) => ({ id, name, url, category, connection_status })),
      benchmark_ids: [...new Set(benchmarkIds)],
      learning_stages: ['goal_intake', 'capability_gap_review', 'selected_source_review', 'original_lesson_and_practice', 'sandbox_benchmark', 'holdout_and_regression_review'],
      training_enabled: false,
      external_actions_enabled: false,
      user_namespace: 'local_browser_export_only',
      truth_boundary: 'This export records choices. It does not fetch sources, connect accounts, execute training, or prove mastery.',
    });
    byId('bootcamp-plan-status').textContent = `Exported a plan with ${goals.length} goal(s), ${resources.length} selected resource(s), and ${benchmarkIds.length} benchmark(s). No account was connected and no training was run.`;
  });

  byId('reconstruction-form').addEventListener('submit', (event) => {
    event.preventDefault();
    const target = byId('reconstruction-target').value.trim();
    let safeTarget = false;
    try {
      const parsed = new URL(target);
      safeTarget = parsed.protocol === 'https:' && !parsed.username && !parsed.password;
    } catch { /* invalid target stays blocked */ }
    const choices = [...document.querySelectorAll('input[name="customization"]:checked')].map((input) => input.value);
    const differentiator = byId('reconstruction-differentiator').value.replace(/\s+/g, ' ').trim();
    const ownerAuthorized = byId('reconstruction-owner-authorized').checked;
    const cleanRoom = byId('reconstruction-clean-room').checked;
    const reaReviewed = byId('reconstruction-rea-reviewed').checked;
    const reaSelected = state.selected.includes('project:rea_reverse_engineer_anything');
    const customizationComplete = choices.length >= 2 && differentiator.length >= 30;
    const blockers = [];
    if (!safeTarget) blockers.push('valid_https_target_required');
    if (!ownerAuthorized) blockers.push('target_owner_authorization_required');
    if (!cleanRoom) blockers.push('clean_room_implementation_required');
    if (!reaReviewed) blockers.push('review_REA_current_code_license_dependencies_and_security');
    if (!reaSelected) blockers.push('select_REA_in_the_resource_catalog');
    if (!customizationComplete) blockers.push('choose_two_customizations_and_describe_your_differentiator');
    const plan = {
      schema: 'dreamco.clean_room_reconstruction_plan.v1',
      target_url: safeTarget ? target : null,
      analysis_tool_id: reaSelected ? 'project:rea_reverse_engineer_anything' : null,
      status: blockers.length ? 'blocked' : 'ready_for_authorized_review',
      blockers,
      customization: { required: true, selected_changes: choices, original_differentiator: differentiator, minimum_distinct_changes: 2, customization_complete: customizationComplete },
      stages: ['confirm_scope_and_rights', 'inspect_authorized_artifacts_or_observed_behavior', 'record_evidence_and_uncertainty', 'write_independent_behavior_spec', 'implement_original_code', 'compare_against_owner_provided_fixtures', 'security_license_and_regression_review'],
      prohibited: ['copying proprietary source or assets', 'bypassing access controls or DRM', 'using stolen credentials or private user data', 'claiming compatibility without test evidence'],
      execution_started: false,
      source_code_copied: false,
    };
    byId('reconstruction-status').textContent = plan.status === 'blocked'
      ? `Blocked: ${blockers.join(', ')}.`
      : 'Plan is ready for owner review. It remains a plan; nothing was cloned, installed, or run.';
    download('buddy-clean-room-reconstruction-plan.json', plan);
  });
})();
