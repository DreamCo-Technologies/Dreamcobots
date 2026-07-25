(function () {
  'use strict';

  const STORAGE_KEY = 'buddy-data-control-v1';
  const byId = (id) => document.getElementById(id);
  let state = loadState();

  function loadState() {
    try {
      const parsed = JSON.parse(localStorage.getItem(STORAGE_KEY) || '{}');
      return {
        memory: parsed.memory || null,
        sources: Array.isArray(parsed.sources) ? parsed.sources.slice(0, 30) : [],
        requests: Array.isArray(parsed.requests) ? parsed.requests.slice(0, 50) : [],
        packages: Array.isArray(parsed.packages) ? parsed.packages.slice(0, 20) : [],
      };
    } catch (_error) {
      return { memory: null, sources: [], requests: [], packages: [] };
    }
  }

  function saveState() {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
    render();
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

  function selected(name) {
    return [...document.querySelectorAll(`input[name="${name}"]:checked`)].map((input) => input.value);
  }

  function safeOfficialUrl(value) {
    try {
      const url = new URL(value);
      return url.protocol === 'https:' && !url.username && !url.password;
    } catch (_error) {
      return false;
    }
  }

  function renderLedger(targetId, rows, kind) {
    const target = byId(targetId);
    if (!rows.length) {
      target.innerHTML = '<p class="data-status">No local plans yet.</p>';
      return;
    }
    target.innerHTML = rows.map((row, index) => `
      <article class="data-ledger-item">
        <div><strong>${escapeHtml(row.label)}</strong><span>${escapeHtml(row.detail)}</span></div>
        <button type="button" data-remove-kind="${kind}" data-remove-index="${index}">Remove</button>
      </article>`).join('');
  }

  function escapeHtml(value) {
    return String(value).replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;')
      .replaceAll('"', '&quot;').replaceAll("'", '&#39;');
  }

  function render() {
    byId('data-memory-count').textContent = String(state.memory?.memoryCategories?.length || 0);
    byId('data-source-count').textContent = String(state.sources.length);
    byId('data-request-count').textContent = String(state.requests.length);
    renderLedger('data-source-list', state.sources, 'sources');
    renderLedger('privacy-request-list', state.requests, 'requests');
    document.querySelectorAll('[data-remove-kind]').forEach((button) => button.addEventListener('click', () => {
      const key = button.dataset.removeKind;
      state[key].splice(Number(button.dataset.removeIndex), 1);
      saveState();
    }));
  }

  function updateTrait(id) {
    byId(`${id}-value`).textContent = `${byId(id).value}%`;
  }

  ['trait-warmth', 'trait-directness', 'trait-patience', 'trait-curiosity'].forEach((id) => {
    byId(id).addEventListener('input', () => updateTrait(id));
  });

  byId('memory-form').addEventListener('submit', (event) => {
    event.preventDefault();
    const privateTraining = byId('memory-training').checked;
    state.memory = {
      schema: 'dreamco.buddy_memory_preference_plan.v1',
      savedAt: new Date().toISOString(),
      memoryCategories: selected('memory-category'),
      retentionDays: Number(byId('memory-retention').value),
      personalizationEnabled: byId('memory-personalization').checked,
      privateModelTrainingEnabled: privateTraining,
      explicitPrivateTrainingOptIn: privateTraining,
      adaptLanguageStyle: byId('memory-style').checked,
      professionalContextOverride: true,
      sensitiveMemoryDefault: 'off',
      personalityTraits: {
        warmth: Number(byId('trait-warmth').value) / 100,
        directness: Number(byId('trait-directness').value) / 100,
        patience: Number(byId('trait-patience').value) / 100,
        curiosity: Number(byId('trait-curiosity').value) / 100,
      },
    };
    saveState();
    byId('memory-status').textContent = 'Memory choices saved in this browser. No private model training runs from this page.';
  });

  byId('delete-buddy-memory').addEventListener('click', () => {
    state.memory = null;
    saveState();
    byId('memory-status').textContent = 'Saved Buddy memory preferences were deleted from this browser.';
  });

  byId('data-source-form').addEventListener('submit', (event) => {
    event.preventDefault();
    if (!event.currentTarget.reportValidity()) return;
    const acquisition = byId('data-acquisition').value;
    const sourceUrl = byId('data-source-url').value.trim();
    if (!byId('data-source-rights').checked) {
      byId('data-source-list').innerHTML = '<p class="data-status">Confirm that you own or are authorized to connect this data.</p>';
      return;
    }
    if (acquisition !== 'user_upload' && (!sourceUrl || !safeOfficialUrl(sourceUrl))) {
      byId('data-source-list').innerHTML = '<p class="data-status">Use a credential-free official HTTPS URL for this connection route.</p>';
      return;
    }
    state.sources.unshift({
      schema: 'dreamco.buddy_data_import_plan.v1',
      label: byId('data-source-name').value.trim(),
      detail: `${acquisition.replaceAll('_', ' ')} · ${byId('data-source-category').value} · ${byId('data-source-retention').value} days · not imported`,
      sourceUrl: sourceUrl || null,
      category: byId('data-source-category').value,
      dataImported: false,
      rawCredentialsAccepted: false,
      createdAt: new Date().toISOString(),
    });
    saveState();
    event.currentTarget.reset();
  });

  byId('privacy-request-form').addEventListener('submit', (event) => {
    event.preventDefault();
    if (!event.currentTarget.reportValidity()) return;
    const url = byId('privacy-url').value.trim();
    const rights = selected('privacy-right');
    if (!safeOfficialUrl(url) || !rights.length) {
      byId('privacy-request-list').innerHTML = '<p class="data-status">Use an official HTTPS privacy form and select at least one right.</p>';
      return;
    }
    const company = byId('privacy-company').value.trim();
    state.requests.unshift({
      schema: 'dreamco.buddy_privacy_rights_plan.v1',
      label: company,
      detail: `${rights.join(', ')} · draft ready · not submitted`,
      company,
      privacyRequestUrl: url,
      jurisdiction: byId('privacy-jurisdiction').value.trim(),
      rights,
      verification: byId('privacy-verification').value,
      requestSubmitted: false,
      companyComplianceGuaranteed: false,
      createdAt: new Date().toISOString(),
    });
    saveState();
    event.currentTarget.reset();
  });

  byId('data-package-form').addEventListener('submit', (event) => {
    event.preventDefault();
    if (!event.currentTarget.reportValidity()) return;
    const sourceReference = byId('package-source').value.trim();
    const plan = {
      schema: 'dreamco.buddy_data_package_plan.v1',
      packageName: byId('package-name').value.trim(),
      sourceReference: 'redacted',
      sourceReferenceStored: false,
      sourceReferenceFormatChecked: /^[A-Za-z][A-Za-z0-9_.:/-]{2,127}$/.test(sourceReference),
      category: byId('package-category').value,
      recipientClass: byId('package-recipient').value.trim(),
      compensationTerms: byId('package-terms').value.trim(),
      ownerCreatedData: byId('package-owner-created').checked,
      resaleRightsConfirmed: byId('package-resale-rights').checked,
      explicitLicenseOptIn: byId('package-opt-in').checked,
      manifest: ['dataset card', 'field dictionary', 'provenance ledger', 'license', 'quality report', 'withdrawal policy'],
      marketplaceListingCreated: false,
      saleCompleted: false,
      createdAt: new Date().toISOString(),
    };
    state.packages.unshift(plan);
    state.packages = state.packages.slice(0, 20);
    saveState();
    downloadJson(plan, 'buddy-data-package-plan.json');
    byId('data-package-status').textContent = 'Rights-cleared manifest prepared. No marketplace listing or sale was created.';
    event.currentTarget.reset();
  });

  byId('export-data-center').addEventListener('click', () => downloadJson({
    schema: 'dreamco.buddy_data_control_export.v1',
    exportedAt: new Date().toISOString(),
    ...state,
  }, 'buddy-data-control-export.json'));

  byId('clear-data-center').addEventListener('click', () => {
    state = { memory: null, sources: [], requests: [], packages: [] };
    try {
      localStorage.removeItem(STORAGE_KEY);
    } catch (_error) {
      // The in-memory state is still cleared when browser storage is unavailable.
    }
    render();
    byId('memory-status').textContent = 'All Data and Memory Center plans were deleted from this browser.';
  });

  render();
})();
