(function () {
  'use strict';

  const CATALOG_URL = 'data/buddy-connection-catalog.json';
  const AUDIT_KEY = 'dreamco.buddy.connection.audit.v1';
  const LOCK_KEY = 'dreamco.buddy.connection.locked.v1';
  const SECRET_NAME = /^[A-Za-z][A-Za-z0-9_.:/-]{2,127}$/;
  const TOKEN_LIKE = /(?:github_pat_|ghs_|(?:sk|rk)_(?:live|test)_|BEGIN .*PRIVATE KEY)/i;
  const state = { catalog: null, audit: loadAudit(), locked: localStorage.getItem(LOCK_KEY) === 'true' };

  const byId = (id) => document.getElementById(id);

  function element(tag, className, text) {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (text !== undefined) node.textContent = text;
    return node;
  }

  function loadAudit() {
    try {
      const value = JSON.parse(localStorage.getItem(AUDIT_KEY) || '[]');
      return Array.isArray(value) ? value.slice(0, 40) : [];
    } catch (_error) {
      return [];
    }
  }

  function saveAudit() {
    localStorage.setItem(AUDIT_KEY, JSON.stringify(state.audit.slice(0, 40)));
  }

  function addAudit(event) {
    state.audit.unshift({ ...event, at: new Date().toISOString() });
    state.audit = state.audit.slice(0, 40);
    saveAudit();
    renderAudit();
  }

  function officialUrl(raw) {
    const url = new URL(raw);
    if (url.protocol !== 'https:' || url.username || url.password) {
      throw new Error('Use an official HTTPS URL without embedded credentials.');
    }
    return url;
  }

  function setError(id, message) {
    const target = byId(id);
    target.textContent = message || '';
    target.hidden = !message;
  }

  function validatedSecretReference(raw, provider) {
    const value = String(raw || '').trim();
    const highEntropyValue = value.length >= 32 && /^[A-Za-z0-9_-]+$/.test(value);
    const invalidEnvironmentName = provider === 'environment' && !/^[A-Z][A-Z0-9_]{2,127}$/.test(value);
    if (!SECRET_NAME.test(value) || TOKEN_LIKE.test(value) || highEntropyValue || invalidEnvironmentName) {
      throw new Error('Enter a secret reference name, not a key or token value.');
    }
    return value;
  }

  function statusLabel(method) {
    if (method.status === 'adapter_ready') return 'Adapter ready';
    if (method.status === 'user_handoff') return 'User handoff';
    return 'Configuration required';
  }

  function statusBadge(method) {
    if (method.status === 'adapter_ready') return 'badge badge-green';
    if (method.status === 'user_handoff') return 'badge badge-amber';
    return 'badge badge-gray';
  }

  function renderCatalog() {
    const methods = state.catalog.auth_methods;
    byId('auth-method-count').textContent = String(methods.length);
    byId('gate-count').textContent = String(state.catalog.user_presence_gates.length);
    byId('catalog-status').textContent = 'Registry loaded';
    byId('catalog-status').className = 'badge badge-green';

    const methodGrid = byId('auth-method-grid');
    methodGrid.replaceChildren();
    methods.forEach((method) => {
      const card = element('article', 'auth-method-card');
      const heading = element('div', 'auth-method-heading');
      heading.append(element('strong', '', method.label));
      heading.append(element('span', statusBadge(method), statusLabel(method)));
      card.append(heading, element('p', '', method.description));
      const controls = element('div', 'auth-method-controls');
      controls.append(
        element('span', method.user_presence ? 'control-chip control-chip-user' : 'control-chip', method.user_presence ? 'User present' : 'Backend'),
        element('span', 'control-chip', method.secret_reference_required ? 'Secret reference' : 'No raw secret')
      );
      card.append(controls);
      methodGrid.append(card);
    });

    const methodSelect = byId('connection-method');
    methodSelect.replaceChildren();
    methods.forEach((method) => {
      const option = element('option', '', method.label);
      option.value = method.id;
      methodSelect.append(option);
    });
    updateSecretFields();

    const gateList = byId('gate-list');
    gateList.replaceChildren();
    state.catalog.user_presence_gates.forEach((gate) => {
      const row = element('div', 'connection-list-row');
      row.append(element('span', 'gate-mark', 'User'), element('strong', '', gate.label));
      gateList.append(row);
    });

    const contractList = byId('contract-list');
    contractList.replaceChildren();
    state.catalog.connector_contracts.forEach((contract) => {
      const row = element('div', 'connection-list-row connection-contract-row');
      const copy = element('div');
      copy.append(element('strong', '', contract.label), element('span', '', contract.minimum_scope));
      row.append(copy);
      contractList.append(row);
    });
  }

  function updateSecretFields() {
    if (!state.catalog) return;
    const method = state.catalog.auth_methods.find((item) => item.id === byId('connection-method').value);
    const visible = Boolean(method && method.secret_reference_required);
    byId('secret-reference-fields').hidden = !visible;
    byId('secret-reference').required = visible;
  }

  function appendPlanHeading(target, label, status, badgeClass) {
    const heading = element('div', 'connection-section-heading');
    heading.append(element('strong', '', label), element('span', badgeClass, status));
    target.append(heading);
  }

  function appendPlanList(target, label, items) {
    target.append(element('h3', '', label));
    const list = element('ol', 'connection-plan-list');
    items.forEach((item) => list.append(element('li', '', item)));
    target.append(list);
  }

  function appendOfficialLink(target, url, label) {
    const link = element('a', 'btn btn-outline btn-sm connection-official-link', label);
    link.href = url.href;
    link.target = '_blank';
    link.rel = 'noopener noreferrer';
    target.append(link);
  }

  function renderConnectionPlan({ app, url, method, scopes, secretProvider, secretReference }) {
    const target = byId('connection-result');
    target.replaceChildren();
    appendPlanHeading(target, app, 'User approval required', 'badge badge-amber');

    const summary = element('dl', 'connection-plan-summary');
    [
      ['Official host', url.hostname],
      ['Method', method.label],
      ['Scopes', scopes.length ? scopes.join(', ') : 'Provider minimum'],
      ['Secret handling', method.secret_reference_required ? `${secretProvider}:${secretReference}` : 'No raw credential collected'],
    ].forEach(([label, value]) => {
      summary.append(element('dt', '', label), element('dd', '', value));
    });
    target.append(summary);

    const steps = [];
    if (method.id === 'oauth_pkce') {
      steps.push('Backend loads the official authorization endpoint and public client id.');
      steps.push('User signs in and reviews the exact scopes on the provider domain.');
      steps.push('Backend validates state and exchanges the code with a session-only PKCE verifier.');
    } else if (method.id === 'oauth_device') {
      steps.push('Backend requests a short-lived device code.');
      steps.push('User verifies the code on the official provider domain.');
      steps.push('Backend stores the resulting scoped token in the approved vault.');
    } else if (method.user_presence) {
      steps.push('Buddy opens the official authentication route.');
      steps.push('User completes SSO, passkey, MFA, or session verification.');
      steps.push('Buddy receives connection status without receiving the credential.');
    } else {
      steps.push('Backend resolves the named secret reference.');
      steps.push('Connector passes its sandbox health check.');
      steps.push('User approves write, publish, account, or money-moving actions when requested.');
    }
    appendPlanList(target, 'Connection path', steps);
    appendOfficialLink(target, url, 'Open official app');

    const footer = element('div', 'connection-plan-footer');
    footer.append(element('span', 'status-dot status-dot-warn'), element('span', '', 'Static preview: backend execution is not connected here.'));
    target.append(footer);
  }

  function handleConnection(event) {
    event.preventDefault();
    setError('connection-error', '');
    if (state.locked) {
      setError('connection-error', 'Unlock the planner before creating a connection plan.');
      return;
    }
    try {
      const form = new FormData(event.currentTarget);
      const app = String(form.get('app') || '').trim();
      const url = officialUrl(String(form.get('url') || ''));
      const method = state.catalog.auth_methods.find((item) => item.id === form.get('method'));
      if (!method) throw new Error('Choose a supported authentication method.');
      const scopes = String(form.get('scopes') || '')
        .split(',')
        .map((value) => value.trim())
        .filter(Boolean);
      if (scopes.some((scope) => !/^[A-Za-z0-9._:/-]{1,80}$/.test(scope))) {
        throw new Error('Scopes may use letters, numbers, dots, slashes, colons, dashes, and underscores.');
      }

      const secretProvider = String(form.get('secretProvider') || '');
      const secretReference = method.secret_reference_required
        ? validatedSecretReference(String(form.get('secretReference') || ''), secretProvider)
        : '';

      renderConnectionPlan({ app, url, method, scopes, secretProvider, secretReference });
      addAudit({ type: 'connection_plan', app, host: url.hostname, method: method.id, status: 'user_action_required' });
    } catch (error) {
      setError('connection-error', error.message || 'Unable to prepare the connection plan.');
    }
  }

  function renderTransferPlan({ connector, kind, sourceProvider, destinationProvider, audience, scopes, reason, ttl }) {
    const target = byId('transfer-result');
    target.replaceChildren();
    appendPlanHeading(target, connector, 'Backend vault required', 'badge badge-amber');

    const summary = element('dl', 'connection-plan-summary');
    [
      ['Token class', kind.replaceAll('_', ' ')],
      ['App audience', audience.origin],
      ['Scopes', scopes.length ? scopes.join(', ') : 'Provider minimum'],
      ['Source', `${sourceProvider} reference configured`],
      ['Destination', `${destinationProvider} reference configured`],
      ['Expires', `${ttl} seconds after creation`],
      ['Approval', 'Recorded for this handoff only'],
      ['Reason', reason],
    ].forEach(([label, value]) => {
      summary.append(element('dt', '', label), element('dd', '', value));
    });
    target.append(summary);
    appendPlanList(target, 'Secure transfer path', [
      'Trusted backend resolves the source reference without returning the token.',
      'Backend writes directly to the approved destination for the same app audience.',
      'The one-time plan is consumed and source memory is cleared.',
      'Only transfer metadata is retained; rotate the source token after a migration.',
    ]);

    const footer = element('div', 'connection-plan-footer');
    footer.append(element('span', 'status-dot status-dot-warn'), element('span', '', 'Static preview: a configured backend vault performs the transfer.'));
    target.append(footer);
  }

  function handleTransfer(event) {
    event.preventDefault();
    setError('transfer-error', '');
    if (state.locked) {
      setError('transfer-error', 'Unlock the planner before preparing a token handoff.');
      return;
    }
    try {
      const form = new FormData(event.currentTarget);
      const connector = String(form.get('connector') || '').trim();
      if (!/^[a-z][a-z0-9-]{2,63}$/.test(connector)) {
        throw new Error('Connector id must be a lowercase app slug.');
      }
      const kind = String(form.get('kind') || '');
      const allowedKinds = state.catalog.token_transfer.allowed_token_kinds;
      if (!allowedKinds.includes(kind)) throw new Error('Choose an approved transferable token class.');

      const sourceProvider = String(form.get('sourceProvider') || '');
      const destinationProvider = String(form.get('destinationProvider') || '');
      const sourceReference = validatedSecretReference(form.get('sourceReference'), sourceProvider);
      const destinationReference = validatedSecretReference(form.get('destinationReference'), destinationProvider);
      if (sourceProvider === destinationProvider && sourceReference === destinationReference) {
        throw new Error('Source and destination references must be different.');
      }
      if (!state.catalog.token_transfer.writable_destinations.includes(destinationProvider)) {
        throw new Error('Destination must be a writable keychain or managed vault.');
      }

      const sourceAudience = officialUrl(String(form.get('sourceAudience') || ''));
      const destinationAudience = officialUrl(String(form.get('destinationAudience') || ''));
      if (sourceAudience.origin !== destinationAudience.origin) {
        throw new Error('Tokens cannot move between apps. Authorize the destination app separately.');
      }
      const scopes = String(form.get('scopes') || '')
        .split(',')
        .map((value) => value.trim())
        .filter(Boolean);
      if (scopes.some((scope) => !/^[A-Za-z0-9._:/-]{1,80}$/.test(scope))) {
        throw new Error('Scopes may use letters, numbers, dots, slashes, colons, dashes, and underscores.');
      }
      const reason = String(form.get('reason') || '').trim();
      const ttl = Number(form.get('ttl'));
      if (reason.length < 5) throw new Error('A clear transfer reason is required.');
      if (TOKEN_LIKE.test(reason) || /[A-Za-z0-9_-]{32,}/.test(reason)) {
        throw new Error('Transfer reason must not contain a key or token value.');
      }
      if (sourceAudience.search || sourceAudience.hash || destinationAudience.search || destinationAudience.hash) {
        throw new Error('App audiences must not contain query parameters or fragments.');
      }
      if (![60, 120, 300].includes(ttl)) throw new Error('Choose an approved short plan lifetime.');
      if (form.get('approval') !== 'on') throw new Error('Explicit approval is required for this handoff.');

      renderTransferPlan({ connector, kind, sourceProvider, destinationProvider, audience: sourceAudience, scopes, reason, ttl });
      addAudit({
        type: 'token_handoff',
        app: connector,
        host: sourceAudience.hostname,
        method: kind,
        status: 'backend_vault_execution_required',
      });
    } catch (error) {
      setError('transfer-error', error.message || 'Unable to prepare the token handoff.');
    }
  }

  function renderSignupPlan({ app, url, purpose }) {
    const target = byId('signup-result');
    target.replaceChildren();
    appendPlanHeading(target, app, 'User handoff', 'badge badge-amber');

    const summary = element('dl', 'connection-plan-summary');
    [['Official host', url.hostname], ['Purpose', purpose], ['Automatic submission', 'Disabled']].forEach(([label, value]) => {
      summary.append(element('dt', '', label), element('dd', '', value));
    });
    target.append(summary);
    appendPlanList(
      target,
      'Required handoffs',
      state.catalog.user_presence_gates.map((gate) => gate.label)
    );
    appendOfficialLink(target, url, 'Open official signup');
    const footer = element('div', 'connection-plan-footer');
    footer.append(element('span', 'status-dot status-dot-warn'), element('span', '', 'Buddy may prepare fields; only the user can submit protected steps.'));
    target.append(footer);
  }

  function handleSignup(event) {
    event.preventDefault();
    setError('signup-error', '');
    if (state.locked) {
      setError('signup-error', 'Unlock the planner before creating a sign-up handoff.');
      return;
    }
    try {
      const form = new FormData(event.currentTarget);
      const app = String(form.get('app') || '').trim();
      const url = officialUrl(String(form.get('url') || ''));
      const purpose = String(form.get('purpose') || '').trim();
      if (app.length < 2 || purpose.length < 5) throw new Error('App label and account purpose are required.');
      renderSignupPlan({ app, url, purpose });
      addAudit({ type: 'signup_handoff', app, host: url.hostname, method: 'user_handoff', status: 'user_action_required' });
    } catch (error) {
      setError('signup-error', error.message || 'Unable to prepare the sign-up handoff.');
    }
  }

  function renderAudit() {
    const target = byId('connection-audit');
    target.replaceChildren();
    if (!state.audit.length) {
      target.append(element('div', 'empty-audit', 'No connection plans recorded in this browser.'));
      return;
    }
    state.audit.forEach((event) => {
      const row = element('article', 'audit-row');
      const copy = element('div');
      copy.append(element('strong', '', event.app), element('span', '', `${event.host} · ${event.method}`));
      const time = element('time', '', new Date(event.at).toLocaleString());
      time.dateTime = event.at;
      row.append(copy, time);
      target.append(row);
    });
  }

  function renderLock() {
    const button = byId('planner-lock');
    button.textContent = state.locked ? 'Unlock planner' : 'Lock planner';
    button.classList.toggle('connection-locked', state.locked);
  }

  function toggleLock() {
    if (state.locked && !window.confirm('Unlock connection planning in this browser?')) return;
    state.locked = !state.locked;
    localStorage.setItem(LOCK_KEY, String(state.locked));
    addAudit({
      type: 'planner_lock',
      app: 'Buddy connection planner',
      host: location.hostname || 'local-file',
      method: 'policy',
      status: state.locked ? 'locked' : 'unlocked',
    });
    renderLock();
  }

  function wireTabs() {
    document.querySelectorAll('[data-panel]').forEach((button) => {
      button.addEventListener('click', () => {
        document.querySelectorAll('[data-panel]').forEach((tab) => tab.classList.toggle('active', tab === button));
        document.querySelectorAll('.connection-panel').forEach((panel) => { panel.hidden = panel.id !== button.dataset.panel; });
      });
    });
  }

  async function start() {
    wireTabs();
    renderAudit();
    renderLock();
    byId('planner-lock').addEventListener('click', toggleLock);
    byId('connection-method').addEventListener('change', updateSecretFields);
    byId('connection-form').addEventListener('submit', handleConnection);
    byId('transfer-form').addEventListener('submit', handleTransfer);
    byId('signup-form').addEventListener('submit', handleSignup);
    byId('clear-connection-audit').addEventListener('click', () => {
      state.audit = [];
      saveAudit();
      renderAudit();
    });

    try {
      const response = await fetch(CATALOG_URL, { cache: 'no-store' });
      if (!response.ok) throw new Error(`Catalog request failed (${response.status}).`);
      state.catalog = await response.json();
      renderCatalog();
    } catch (error) {
      byId('catalog-status').textContent = 'Catalog unavailable';
      byId('catalog-status').className = 'badge badge-amber';
      byId('auth-method-grid').append(element('div', 'connection-error', error.message || 'Catalog unavailable.'));
    }
  }

  start();
})();
