(function () {
  'use strict';

  const STATIC_HOST = location.hostname.endsWith('github.io');
  const BACKEND_STORAGE_KEY = 'buddy-execution-backend-v1';
  const input = document.getElementById('buddy-input');
  const sendButton = document.getElementById('buddy-send');
  const thread = document.getElementById('buddy-thread');
  const welcome = document.getElementById('buddy-welcome');
  const routeStatus = document.getElementById('buddy-route-status');
  const premiumApproval = document.getElementById('premium-approval');
  const localDialog = document.getElementById('local-dialog');
  const localStatus = document.getElementById('local-status');
  const localStatusDetail = document.getElementById('local-status-detail');
  const localStatusDot = document.getElementById('local-status-dot');

  if (!input || !sendButton || !thread) return;

  function normalizeBackend(value) {
    const raw = String(value || '').trim().replace(/\/+$/, '');
    if (!raw) return '';
    try {
      const parsed = new URL(raw);
      if (parsed.protocol !== 'https:' && !(parsed.protocol === 'http:' && ['127.0.0.1', 'localhost'].includes(parsed.hostname))) return '';
      return parsed.origin;
    } catch (_error) {
      return '';
    }
  }

  function configuredBackend() {
    const params = new URLSearchParams(location.search);
    const fromQuery = normalizeBackend(params.get('backend'));
    if (fromQuery) {
      localStorage.setItem(BACKEND_STORAGE_KEY, fromQuery);
      return fromQuery;
    }
    const saved = normalizeBackend(localStorage.getItem(BACKEND_STORAGE_KEY));
    if (saved) return saved;
    return STATIC_HOST ? '' : location.origin;
  }

  async function backendHealth(base) {
    if (!base) return { ok: false, reason: 'No execution backend is configured.' };
    try {
      const controller = new AbortController();
      const timeout = setTimeout(() => controller.abort(), 5000);
      const response = await fetch(`${base}/api/health`, { signal: controller.signal, mode: 'cors' });
      clearTimeout(timeout);
      if (!response.ok) return { ok: false, reason: `Backend returned HTTP ${response.status}.` };
      const data = await response.json();
      if (!data?.ok || !data?.publicExecutionBridge) return { ok: false, reason: 'Backend is reachable but does not advertise the Buddy public execution bridge.' };
      return { ok: true, data };
    } catch (error) {
      return { ok: false, reason: error instanceof Error ? error.message : 'Backend connection failed.' };
    }
  }

  function addUserMessage(text) {
    const row = document.createElement('article');
    row.className = 'buddy-chat-row user';
    const bubble = document.createElement('div');
    bubble.className = 'buddy-chat-bubble';
    bubble.textContent = text;
    row.append(bubble);
    thread.append(row);
  }

  function addExecutionMessage(result, backend) {
    const row = document.createElement('article');
    row.className = 'buddy-chat-row assistant';
    const avatar = document.createElement('img');
    avatar.className = 'buddy-chat-avatar';
    avatar.src = 'assets/images/buddy-icon-192.png';
    avatar.alt = 'Buddy';
    const bubble = document.createElement('div');
    bubble.className = 'buddy-chat-bubble';

    const receipt = document.createElement('div');
    receipt.className = 'buddy-model-note';
    const state = result.executed ? 'EXECUTED' : result.status === 'prepared_for_approval' ? 'PREPARED — APPROVAL REQUIRED' : 'PREPARED — NOT EXECUTED';
    receipt.textContent = `${state} · ${backend}`;

    const heading = document.createElement('div');
    heading.className = 'buddy-specialist-heading';
    const title = document.createElement('strong');
    title.textContent = result.executed ? 'Buddy completed the safe response work' : 'Buddy prepared the execution path';
    heading.append(title);

    const output = document.createElement('div');
    output.className = 'buddy-execution-output';
    output.style.whiteSpace = 'pre-wrap';
    output.textContent = String(result.output || 'No output was returned.');

    bubble.append(receipt, heading, output);

    const compilation = result.compilation;
    if (compilation?.master?.displayName || compilation?.modelRoute?.selected?.modelId) {
      const meta = document.createElement('p');
      meta.className = 'buddy-role-boundary';
      const specialist = compilation?.master?.displayName || 'DreamCo master';
      const model = compilation?.modelRoute?.selected?.modelId || 'no model selected';
      meta.textContent = `Execution route: ${specialist} · model candidate: ${model} · unused bots/models remained inactive.`;
      bubble.append(meta);
    }

    row.append(avatar, bubble);
    thread.append(row);
  }

  function addPreviewOnlyMessage(objective, reason) {
    const row = document.createElement('article');
    row.className = 'buddy-chat-row assistant';
    const avatar = document.createElement('img');
    avatar.className = 'buddy-chat-avatar';
    avatar.src = 'assets/images/buddy-icon-192.png';
    avatar.alt = 'Buddy';
    const bubble = document.createElement('div');
    bubble.className = 'buddy-chat-bubble';

    const state = document.createElement('div');
    state.className = 'buddy-model-note';
    state.textContent = 'PREVIEW ONLY — NOT EXECUTED';
    const title = document.createElement('strong');
    title.textContent = 'GitHub Pages cannot execute this request by itself.';
    const explanation = document.createElement('p');
    explanation.textContent = reason || 'Connect an authenticated Buddy backend once, then this same chat page can send requests to the real execution runtime.';
    const packet = document.createElement('pre');
    packet.className = 'buddy-test-result';
    packet.textContent = JSON.stringify({ objective, status: 'waiting_for_execution_backend', source: 'github_pages' }, null, 2);
    const openSettings = document.createElement('button');
    openSettings.type = 'button';
    openSettings.textContent = 'Connect execution backend';
    openSettings.addEventListener('click', () => localDialog?.showModal());

    bubble.append(state, title, explanation, packet, openSettings);
    row.append(avatar, bubble);
    thread.append(row);
  }

  function selectedMode() {
    const active = document.querySelector('[data-buddy-mode].active');
    const mode = active?.getAttribute('data-buddy-mode') || 'Build';
    return ['Build', 'Fix', 'Create', 'Plan', 'Discover'].includes(mode) ? mode : 'Build';
  }

  async function executeFromPages(objective) {
    const backend = configuredBackend();
    const health = await backendHealth(backend);
    if (!health.ok) {
      addPreviewOnlyMessage(objective, health.reason);
      routeStatus.textContent = 'Preview only. Connect a Buddy execution backend to perform requests.';
      return;
    }

    routeStatus.textContent = 'Execution backend connected. Running request...';
    const response = await fetch(`${backend}/api/buddy/public-execute`, {
      method: 'POST',
      mode: 'cors',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        objective,
        mode: selectedMode(),
        requestedCapabilities: [],
        approvePaidModelForThisRequest: Boolean(premiumApproval?.checked),
      }),
    });
    let result;
    try {
      result = await response.json();
    } catch (_error) {
      result = { executed: false, status: 'invalid_backend_response', output: `Execution backend returned HTTP ${response.status} without JSON.` };
    }
    addExecutionMessage(result, backend);
    routeStatus.textContent = result.executed
      ? 'Request executed by the connected Buddy backend.'
      : result.status === 'prepared_for_approval'
        ? 'Work prepared. Exact approval is required for the outside action.'
        : 'Execution backend responded, but the request was not executed.';
  }

  async function handleStaticSend(event) {
    if (!STATIC_HOST) return;
    if (event.type === 'click' && event.target !== sendButton) return;
    if (event.type === 'keydown') {
      if (event.target !== input || event.key !== 'Enter' || event.shiftKey) return;
    }
    event.preventDefault();
    event.stopImmediatePropagation();
    const objective = input.value.trim();
    if (!objective) return;
    welcome.hidden = true;
    addUserMessage(objective);
    input.value = '';
    sendButton.disabled = true;
    sendButton.textContent = 'Executing...';
    try {
      await executeFromPages(objective);
    } catch (error) {
      addPreviewOnlyMessage(objective, error instanceof Error ? error.message : 'Execution bridge failed.');
      routeStatus.textContent = 'Execution failed safely; no outside action was claimed.';
    } finally {
      sendButton.disabled = false;
      sendButton.textContent = 'Send';
      if (premiumApproval) premiumApproval.checked = false;
      thread.lastElementChild?.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
      input.focus();
    }
  }

  function installBackendSettings() {
    if (!localDialog || document.getElementById('execution-backend-url')) return;
    const section = document.createElement('section');
    section.className = 'buddy-local-section';
    const title = document.createElement('h3');
    title.textContent = 'GitHub Pages execution backend';
    const description = document.createElement('p');
    description.textContent = 'GitHub Pages is static. Save the HTTPS address of your deployed Buddy server here once so chat requests can reach the real runtime.';
    const label = document.createElement('label');
    label.className = 'buddy-local-query';
    label.textContent = 'Buddy backend URL';
    const field = document.createElement('input');
    field.id = 'execution-backend-url';
    field.type = 'url';
    field.placeholder = 'https://your-buddy-backend.example.com';
    field.value = configuredBackend();
    field.autocomplete = 'off';
    label.append(field);
    const actions = document.createElement('div');
    actions.className = 'buddy-local-app-row';
    const save = document.createElement('button');
    save.type = 'button';
    save.className = 'buddy-header-link';
    save.textContent = 'Save & test';
    const clear = document.createElement('button');
    clear.type = 'button';
    clear.className = 'buddy-header-link';
    clear.textContent = 'Disconnect';
    const status = document.createElement('p');
    status.id = 'execution-backend-status';
    status.textContent = configuredBackend() ? 'Saved backend; press Save & test to verify.' : 'No execution backend connected.';
    save.addEventListener('click', async () => {
      const base = normalizeBackend(field.value);
      if (!base) {
        status.textContent = 'Enter an HTTPS backend URL.';
        return;
      }
      localStorage.setItem(BACKEND_STORAGE_KEY, base);
      status.textContent = 'Testing...';
      const health = await backendHealth(base);
      status.textContent = health.ok ? 'Connected. GitHub Pages requests can now reach Buddy execution.' : `Not connected: ${health.reason}`;
      if (health.ok && localStatus && localStatusDetail && localStatusDot) {
        localStatus.textContent = 'Execution backend connected';
        localStatusDetail.textContent = base;
        localStatusDot.classList.add('connected');
      }
    });
    clear.addEventListener('click', () => {
      localStorage.removeItem(BACKEND_STORAGE_KEY);
      field.value = '';
      status.textContent = 'Execution backend disconnected. GitHub Pages will show preview-only status.';
    });
    actions.append(save, clear);
    section.append(title, description, label, actions, status);
    const firstSection = localDialog.querySelector('.buddy-local-section');
    localDialog.insertBefore(section, firstSection || localDialog.querySelector('footer'));
  }

  document.addEventListener('click', handleStaticSend, true);
  document.addEventListener('keydown', handleStaticSend, true);
  installBackendSettings();

  if (STATIC_HOST) {
    const backend = configuredBackend();
    routeStatus.textContent = backend
      ? 'GitHub Pages execution bridge configured. Requests will verify the backend before running.'
      : 'GitHub Pages preview: connect an execution backend in “This laptop” to make Buddy perform requests.';
  }
})();
