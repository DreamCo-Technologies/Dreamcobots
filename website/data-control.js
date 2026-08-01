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
        apps: Array.isArray(parsed.apps) ? parsed.apps.slice(0, 100) : [],
        appWorkflows: Array.isArray(parsed.appWorkflows) ? parsed.appWorkflows.slice(0, 50) : [],
        social: Array.isArray(parsed.social) ? parsed.social.slice(0, 50) : [],
        subscriptions: Array.isArray(parsed.subscriptions) ? parsed.subscriptions.slice(0, 500) : [],
        bills: Array.isArray(parsed.bills) ? parsed.bills.slice(0, 500) : [],
      };
    } catch (_error) {
      return { memory: null, sources: [], requests: [], packages: [], apps: [], appWorkflows: [], social: [], subscriptions: [], bills: [] };
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

  async function fingerprintReference(reference) {
    if (!window.crypto?.subtle) throw new Error('Secure browser fingerprinting is unavailable.');
    const bytes = new TextEncoder().encode(reference);
    const digest = await window.crypto.subtle.digest('SHA-256', bytes);
    return [...new Uint8Array(digest)].map((byte) => byte.toString(16).padStart(2, '0')).join('').slice(0, 20);
  }

  function renderLedger(targetId, rows, kind) {
    const target = byId(targetId);
    if (!rows.length) {
      target.innerHTML = '<p class="data-status">No local plans yet.</p>';
      return;
    }
    target.innerHTML = rows.map((row, index) => {
      const requestStatus = kind === 'requests' ? `
        <label class="data-request-status">Status
          <select data-request-status-index="${index}">
            ${[
              ['draft_ready_for_user_review', 'Draft ready'],
              ['submitted_by_user', 'Submitted by user'],
              ['company_confirmed', 'Company confirmed'],
              ['fulfilled', 'Fulfilled'],
              ['partially_fulfilled', 'Partially fulfilled'],
              ['denied', 'Denied'],
              ['no_response', 'No response'],
            ].map(([value, label]) => `<option value="${value}"${row.status === value ? ' selected' : ''}>${label}</option>`).join('')}
          </select>
        </label>` : '';
      return `
      <article class="data-ledger-item">
        <div><strong>${escapeHtml(row.label)}</strong><span>${escapeHtml(row.detail)}</span></div>
        <div class="data-ledger-actions">
          ${requestStatus}
          <button type="button" data-remove-kind="${kind}" data-remove-index="${index}">Remove</button>
        </div>
      </article>`;
    }).join('');
  }

  function escapeHtml(value) {
    return String(value).replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;')
      .replaceAll('"', '&quot;').replaceAll("'", '&#39;');
  }

  function monthlyAmount(amount, cadence) {
    const value = Number(amount);
    const monthly = cadence === 'weekly' ? value * 52 / 12
      : cadence === 'quarterly' ? value / 3
        : cadence === 'annual' ? value / 12
          : value;
    return Math.round(monthly * 100) / 100;
  }

  function renderFinance() {
    const totals = state.subscriptions.reduce((result, item) => {
      result[item.currency] = (result[item.currency] || 0) + monthlyAmount(item.amount, item.cadence);
      return result;
    }, {});
    const groups = new Map();
    state.subscriptions.forEach((item) => {
      const key = `${item.merchant.toLowerCase()}:${item.amount}:${item.currency}`;
      groups.set(key, [...(groups.get(key) || []), item]);
    });
    const duplicates = [...groups.values()].filter(items => items.length > 1);
    const formatTotals = (multiplier) => Object.entries(totals).length
      ? Object.entries(totals).map(([currency, value]) => `${currency} ${(value * multiplier).toFixed(2)}`).join(' · ')
      : 'USD 0.00';
    byId('finance-monthly').textContent = formatTotals(1);
    byId('finance-annual').textContent = formatTotals(12);
    byId('finance-duplicates').textContent = String(duplicates.length);
    const rows = [
      ...state.subscriptions.map((item, index) => ({
        ...item,
        key: 'subscriptions',
        index,
        label: item.merchant,
        detail: `${item.currency} ${Number(item.amount).toFixed(2)} · ${item.cadence} · renews ${item.renewalAt} · cancellation not submitted`,
      })),
      ...state.bills.map((item, index) => ({
        ...item,
        key: 'bills',
        index,
        label: item.payee,
        detail: `${item.currency} ${Number(item.amount).toFixed(2)} · due ${item.dueAt} · payment not executed`,
      })),
    ];
    const target = byId('finance-plan-list');
    target.innerHTML = rows.length ? rows.map(row => `
      <article class="data-ledger-item">
        <div><strong>${escapeHtml(row.label)}</strong><span>${escapeHtml(row.detail)}</span></div>
        <div class="data-ledger-actions"><button type="button" data-remove-kind="${row.key}" data-remove-index="${row.index}">Remove</button></div>
      </article>
    `).join('') : '<p class="data-status">No local bill or subscription plans yet.</p>';
  }

  function renderAppPlans() {
    const rows = [
      ...state.apps.map((item, index) => ({ ...item, key: 'apps', index })),
      ...state.appWorkflows.map((item, index) => ({ ...item, key: 'appWorkflows', index })),
    ];
    const target = byId('app-plan-list');
    target.innerHTML = rows.length ? rows.map(row => `
      <article class="data-ledger-item">
        <div><strong>${escapeHtml(row.label)}</strong><span>${escapeHtml(row.detail)}</span></div>
        <div class="data-ledger-actions"><button type="button" data-remove-kind="${row.key}" data-remove-index="${row.index}">Remove</button></div>
      </article>
    `).join('') : '<p class="data-status">No local app or grouped workflow plans yet.</p>';
  }

  function render() {
    byId('data-memory-count').textContent = String(state.memory?.memoryCategories?.length || 0);
    byId('data-source-count').textContent = String(state.sources.length);
    byId('data-request-count').textContent = String(state.requests.length);
    byId('data-app-count').textContent = String(state.apps.length);
    renderLedger('data-source-list', state.sources, 'sources');
    renderLedger('privacy-request-list', state.requests, 'requests');
    renderAppPlans();
    renderLedger('social-plan-list', state.social, 'social');
    renderFinance();
    document.querySelectorAll('[data-remove-kind]').forEach((button) => button.addEventListener('click', () => {
      const key = button.dataset.removeKind;
      state[key].splice(Number(button.dataset.removeIndex), 1);
      saveState();
    }));
    document.querySelectorAll('[data-request-status-index]').forEach((select) => select.addEventListener('change', () => {
      const row = state.requests[Number(select.dataset.requestStatusIndex)];
      if (!row) return;
      const rights = Array.isArray(row.rights) && row.rights.length ? row.rights : ['privacy request'];
      row.status = select.value;
      row.updatedAt = new Date().toISOString();
      row.detail = `${rights.join(', ')} · ${select.options[select.selectedIndex].text.toLowerCase()} · outside result recorded by user`;
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

  const connectedLife = window.BUDDY_CONNECTED_LIFE || { app_categories: [] };
  connectedLife.app_categories.forEach((category) => {
    const option = document.createElement('option');
    option.value = category.id;
    option.textContent = category.label;
    byId('app-category').append(option);
  });

  byId('app-plan-form').addEventListener('submit', (event) => {
    event.preventDefault();
    if (!event.currentTarget.reportValidity()) return;
    const url = byId('app-url').value.trim();
    const actions = selected('app-action');
    const accessLevel = byId('app-access').value;
    if (!safeOfficialUrl(url) || !actions.length) {
      byId('app-plan-list').innerHTML = '<p class="data-status">Use an official HTTPS app URL and choose at least one requested action.</p>';
      return;
    }
    if (accessLevel === 'catalog_only' && actions.some(action => action !== 'catalog')) {
      byId('app-plan-list').innerHTML = '<p class="data-status">Catalog-only apps can organize metadata but cannot request data or action access.</p>';
      return;
    }
    if (!byId('app-owner-authorized').checked) return;
    const parsed = new URL(url);
    const highImpact = actions.filter(action => ['schedule', 'publish', 'send', 'pay', 'transfer', 'license_data'].includes(action));
    state.apps.unshift({
      schema: 'dreamco.buddy_app_connection_plan.v1',
      planId: `app-plan-${window.crypto?.randomUUID?.() || Date.now()}`,
      label: byId('app-name').value.trim(),
      detail: `${byId('app-category').value} · ${byId('app-group').value.trim()} · ${accessLevel.replaceAll('_', ' ')} · ${highImpact.length ? 'exact action approvals required' : 'read-only first'} · not connected`,
      officialOrigin: parsed.origin,
      officialPath: parsed.pathname,
      category: byId('app-category').value,
      groupName: byId('app-group').value.trim(),
      authMethod: byId('app-auth').value,
      accessLevel,
      actions,
      highImpactActions: highImpact,
      rawCredentialsAccepted: false,
      connected: false,
      createdAt: new Date().toISOString(),
    });
    state.apps = state.apps.slice(0, 100);
    saveState();
    event.currentTarget.reset();
  });

  byId('app-group-form').addEventListener('submit', (event) => {
    event.preventDefault();
    const objective = byId('app-group-objective').value.trim();
    if (state.apps.length < 2 || objective.length < 10) {
      byId('app-plan-list').innerHTML = '<p class="data-status">Add at least two app plans and describe the grouped workflow.</p>';
      return;
    }
    state.appWorkflows.unshift({
      schema: 'dreamco.buddy_app_group_workflow_plan.v1',
      label: 'Grouped app workflow',
      detail: `${state.apps.length} selected app plans · sandbox first · no live actions taken`,
      objective,
      appPlanIds: state.apps.map(item => item.planId),
      previewBeforeWrite: true,
      freshApprovalPerHighImpactAction: true,
      dataJoinRequiresCompatiblePurposeGrants: true,
      liveActionsTaken: false,
      createdAt: new Date().toISOString(),
    });
    state.appWorkflows = state.appWorkflows.slice(0, 50);
    saveState();
    event.currentTarget.reset();
  });

  byId('social-plan-form').addEventListener('submit', (event) => {
    event.preventDefault();
    if (!event.currentTarget.reportValidity()) return;
    const mode = byId('social-mode').value;
    const contentTypes = selected('social-content');
    const synthetic = byId('social-synthetic').checked;
    if (!contentTypes.length) {
      byId('social-plan-list').innerHTML = '<p class="data-status">Choose at least one social content type.</p>';
      return;
    }
    if (['live_rehearsal', 'live_show'].includes(mode) && !contentTypes.includes('livestream')) {
      byId('social-plan-list').innerHTML = '<p class="data-status">Live modes require Livestream as a content type.</p>';
      return;
    }
    if (mode === 'live_show' && !byId('social-moderation').checked) {
      byId('social-plan-list').innerHTML = '<p class="data-status">Live shows require moderation and emergency-stop controls.</p>';
      return;
    }
    if (synthetic && !byId('social-rights').checked) {
      byId('social-plan-list').innerHTML = '<p class="data-status">Synthetic owner or performer media requires adult consent and confirmed rights.</p>';
      return;
    }
    state.social.unshift({
      schema: 'dreamco.buddy_social_workspace_plan.v1',
      label: `${byId('social-platform').value.trim()} · ${mode.replaceAll('_', ' ')}`,
      detail: `${contentTypes.join(', ')} · ${['schedule', 'publish_once', 'live_show'].includes(mode) ? 'owner action approval required' : 'draft or rehearsal ready'} · no external action taken`,
      accountReference: byId('social-account-ref').value.trim(),
      objective: byId('social-objective').value.trim(),
      mode,
      contentTypes,
      syntheticMediaLabelRequired: synthetic,
      moderationEnabled: byId('social-moderation').checked,
      rawCredentialsAccepted: false,
      liveExternalActionTaken: false,
      createdAt: new Date().toISOString(),
    });
    state.social = state.social.slice(0, 50);
    saveState();
    event.currentTarget.reset();
  });

  byId('subscription-form').addEventListener('submit', (event) => {
    event.preventDefault();
    if (!event.currentTarget.reportValidity()) return;
    const cancelUrl = byId('subscription-cancel-url').value.trim();
    if (cancelUrl && !safeOfficialUrl(cancelUrl)) {
      byId('finance-plan-list').innerHTML = '<p class="data-status">Use a credential-free official HTTPS cancellation URL.</p>';
      return;
    }
    state.subscriptions.unshift({
      schema: 'dreamco.buddy_subscription_record.v1',
      merchant: byId('subscription-merchant').value.trim(),
      amount: Number(byId('subscription-amount').value).toFixed(2),
      currency: byId('subscription-currency').value.trim().toUpperCase(),
      cadence: byId('subscription-cadence').value,
      renewalAt: byId('subscription-renewal').value,
      cancellationUrl: cancelUrl || null,
      cancellationSubmitted: false,
      paymentCredentialsStored: false,
      createdAt: new Date().toISOString(),
    });
    state.subscriptions = state.subscriptions.slice(0, 500);
    saveState();
    event.currentTarget.reset();
  });

  byId('bill-form').addEventListener('submit', (event) => {
    event.preventDefault();
    if (!event.currentTarget.reportValidity()) return;
    state.bills.unshift({
      schema: 'dreamco.buddy_bill_record.v1',
      payee: byId('bill-payee').value.trim(),
      amount: Number(byId('bill-amount').value).toFixed(2),
      currency: byId('bill-currency').value.trim().toUpperCase(),
      dueAt: byId('bill-due').value,
      accountReference: 'redacted',
      accountReferenceStored: false,
      paymentExecuted: false,
      createdAt: new Date().toISOString(),
    });
    state.bills = state.bills.slice(0, 500);
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
      status: 'draft_ready_for_user_review',
      requestSubmitted: false,
      companyComplianceGuaranteed: false,
      createdAt: new Date().toISOString(),
    });
    saveState();
    event.currentTarget.reset();
  });

  byId('data-package-form').addEventListener('submit', async (event) => {
    event.preventDefault();
    if (!event.currentTarget.reportValidity()) return;
    const references = {
      source: byId('package-source').value.trim(),
      ownership: byId('package-ownership-evidence').value.trim(),
      resaleRights: byId('package-resale-evidence').value.trim(),
      consentReceipt: byId('package-consent-receipt').value.trim(),
      provenance: byId('package-provenance').value.trim(),
    };
    const validReference = /^[A-Za-z][A-Za-z0-9_.:/-]{2,127}$/;
    if (Object.values(references).some((reference) => !validReference.test(reference))) {
      byId('data-package-status').textContent = 'Use valid encrypted-vault or receipt references. Do not enter raw data.';
      return;
    }
    if (new Set(Object.values(references)).size !== Object.keys(references).length) {
      byId('data-package-status').textContent = 'Use a distinct reference for the source, ownership, resale rights, consent, and provenance.';
      return;
    }
    let evidence;
    try {
      const fingerprints = await Promise.all(Object.values(references).map(fingerprintReference));
      evidence = Object.fromEntries(Object.keys(references).map((key, index) => [key, fingerprints[index]]));
    } catch (error) {
      byId('data-package-status').textContent = error instanceof Error ? error.message : 'Evidence fingerprinting failed.';
      return;
    }
    const plan = {
      schema: 'dreamco.buddy_data_package_plan.v1',
      packageName: byId('package-name').value.trim(),
      sourceReference: 'redacted',
      sourceReferenceStored: false,
      evidenceFingerprints: evidence,
      rawEvidenceReferencesStored: false,
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
    byId('data-package-status').textContent = 'Manifest prepared with evidence fingerprints. No marketplace listing or sale was created.';
    event.currentTarget.reset();
  });

  byId('export-data-center').addEventListener('click', () => downloadJson({
    schema: 'dreamco.buddy_data_control_export.v1',
    exportedAt: new Date().toISOString(),
    ...state,
  }, 'buddy-data-control-export.json'));

  byId('clear-data-center').addEventListener('click', () => {
    state = {
      memory: null,
      sources: [],
      requests: [],
      packages: [],
      apps: [],
      appWorkflows: [],
      social: [],
      subscriptions: [],
      bills: [],
    };
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
