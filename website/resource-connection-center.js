(() => {
  'use strict';
  const $ = (id) => document.getElementById(id);
  const STORAGE_KEY = 'dreamco.buddy.personal-connections.v1';
  const PAGE_SIZE = 60;
  const PURPOSES = {
    research: { label: 'Research/current data', scope: 'Read public or owner-authorized data; return citations, timestamps, and source limitations.' },
    account: { label: 'Connect account', scope: 'Read connection status first; request the minimum account scope through the official authorization flow.' },
    draft: { label: 'Create drafts', scope: 'Create a local draft and preview; do not send, upload, or publish.' },
    publish: { label: 'Post or publish', scope: 'Draft and preview locally; require an authenticated destination, exact owner approval, and an audit receipt before publishing.' },
  };
  const esc = (value) => String(value ?? '').replace(/[&<>"']/g, (character) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[character]));
  let catalog = { resources: [], resource_count: 0, scanned_json_lists: 0 };
  let methods = [];
  let visible = [];
  let page = 1;

  function load() {
    try {
      const value = JSON.parse(localStorage.getItem(STORAGE_KEY) || '{}');
      return { selected: value.selected || {}, custom: value.custom || [] };
    } catch {
      return { selected: {}, custom: [] };
    }
  }

  const save = (value) => localStorage.setItem(STORAGE_KEY, JSON.stringify(value));
  const selectedRequests = () => Object.values(load().selected).filter((item) => item && typeof item === 'object');
  const purposeOptions = (selected = 'research') => Object.entries(PURPOSES).map(([id, item]) => `<option value="${id}" ${selected === id ? 'selected' : ''}>${esc(item.label)}</option>`).join('');
  const methodOptions = (selected = 'browser_session_handoff') => [
    ...methods,
    { id: 'mcp_transport', label: 'MCP transport' },
  ].map((method) => `<option value="${esc(method.id)}" ${selected === method.id ? 'selected' : ''}>${esc(method.label)}</option>`).join('');

  function requestFor(resource, method, purpose, custom = false) {
    return {
      id: resource.id,
      kind: custom ? 'custom resource request' : 'repository resource request',
      name: resource.host || resource.name,
      status: 'pending_backend_review',
      purpose,
      purpose_label: PURPOSES[purpose].label,
      auth_method: method,
      description: `${method} request for ${PURPOSES[purpose].label.toLowerCase()}.`,
      scope: resource.scope || PURPOSES[purpose].scope,
      setup: resource.primary_url || resource.setup,
      source_lists: resource.source_lists || [],
      verified_live: false,
      health_check_evidence: null,
      external_write_allowed: false,
      exact_approval_required_for_write: true,
      created_at: new Date().toISOString(),
    };
  }

  function buddyUrl(resource, purpose) {
    const prompt = `Use ${resource.host} only as an owner-selected source for ${PURPOSES[purpose].label.toLowerCase()}. Official source: ${resource.primary_url}. First inspect its documented access method and terms. For current data, cite the source and retrieval time. Do not collect a password or raw secret. Do not send, buy, upload, or publish without a configured adapter, an exact preview, and separate owner approval.`;
    return `buddy.html?prompt=${encodeURIComponent(prompt)}`;
  }

  function renderCards() {
    const state = load();
    const query = $('resource-search').value.trim().toLowerCase();
    const stateFilter = $('resource-state').value;
    visible = catalog.resources.filter((item) => {
      const matchesQuery = !query || `${item.host} ${item.source_lists.join(' ')}`.toLowerCase().includes(query);
      const planned = Boolean(state.selected[item.id]);
      return matchesQuery && (stateFilter === 'all' || (stateFilter === 'planned' ? planned : !planned));
    });
    const totalPages = Math.max(1, Math.ceil(visible.length / PAGE_SIZE));
    page = Math.min(page, totalPages);
    const rows = visible.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE);
    const defaultPurpose = $('resource-purpose').value === 'all' ? 'research' : $('resource-purpose').value;
    $('resource-summary').textContent = `${catalog.resource_count} discovered HTTPS hosts across ${catalog.scanned_json_lists} machine-readable lists. Showing ${rows.length} on page ${page} of ${totalPages}; ${selectedRequests().length} connection request(s) selected.`;
    $('resource-grid').innerHTML = rows.map((item) => {
      const saved = state.selected[item.id];
      const purpose = saved?.purpose || defaultPurpose;
      const method = saved?.auth_method || 'browser_session_handoff';
      return `<article class="card" data-resource-card="${esc(item.id)}"><span class="tag">${saved ? 'planned · not live' : 'reference only'}</span><h2>${esc(item.host)}</h2><p>${item.url_count} unique HTTPS reference${item.url_count === 1 ? '' : 's'} · ${item.source_lists.length} repository source list${item.source_lists.length === 1 ? '' : 's'}</p><label>Purpose<select data-purpose="${esc(item.id)}">${purposeOptions(purpose)}</select></label><label>Authorization<select data-method="${esc(item.id)}">${methodOptions(method)}</select></label><div class="controls"><a class="btn btn-outline" target="_blank" rel="noopener noreferrer" href="${esc(item.primary_url)}">Open official source</a><a class="btn btn-outline" data-research="${esc(item.id)}" href="${buddyUrl(item, purpose)}">Use with Buddy</a><button class="btn btn-primary" data-add="${esc(item.id)}" type="button">${saved ? 'Update request' : 'Add to My Buddy'}</button></div></article>`;
    }).join('') || '<p>No matching resource.</p>';
    $('resource-page').textContent = `Page ${page} of ${totalPages}`;
    $('resource-prev').disabled = page <= 1;
    $('resource-next').disabled = page >= totalPages;
    renderConnections();
  }

  function renderConnections() {
    const state = load();
    const rows = [...Object.values(state.selected), ...state.custom]
      .filter((item) => item && typeof item === 'object' && item.name)
      .sort((a, b) => a.name.localeCompare(b.name));
    $('connection-list').innerHTML = rows.map((item) => `<article class="connection-row"><strong>${esc(item.name)}</strong><span>${esc(item.purpose_label || item.purpose || 'connection')}</span><span>${esc(item.auth_method || item.description)} · ${esc(item.status)} · live: no</span><button class="btn btn-outline" data-remove="${esc(item.id)}" type="button">Remove</button></article>`).join('') || '<p>No connection requests yet. Choose a repository resource or add your own.</p>';
  }

  Promise.all([
    fetch('data/buddy-resource-connection-catalog.json', { cache: 'no-store' }).then((response) => response.json()),
    fetch('data/buddy-connection-catalog.json', { cache: 'no-store' }).then((response) => response.json()),
  ]).then(([resources, connections]) => {
    catalog = resources;
    methods = connections.auth_methods;
    const requestedResource = new URLSearchParams(location.search).get('resource');
    if (requestedResource) $('resource-search').value = requestedResource;
    renderCards();
  }).catch((error) => { $('resource-summary').textContent = `Catalog unavailable: ${error.message}`; });

  ['resource-search', 'resource-purpose', 'resource-state'].forEach((id) => $(id).addEventListener(id === 'resource-search' ? 'input' : 'change', () => { page = 1; renderCards(); }));
  $('resource-prev').addEventListener('click', () => { page -= 1; renderCards(); });
  $('resource-next').addEventListener('click', () => { page += 1; renderCards(); });
  $('resource-grid').addEventListener('change', (event) => {
    const id = event.target.dataset.purpose;
    if (!id) return;
    const resource = catalog.resources.find((item) => item.id === id);
    const link = document.querySelector(`[data-research="${CSS.escape(id)}"]`);
    if (resource && link) link.href = buddyUrl(resource, event.target.value);
  });
  $('resource-grid').addEventListener('click', (event) => {
    const id = event.target.dataset.add;
    if (!id) return;
    const resource = catalog.resources.find((item) => item.id === id);
    const method = document.querySelector(`[data-method="${CSS.escape(id)}"]`)?.value || 'custom_rest';
    const purpose = document.querySelector(`[data-purpose="${CSS.escape(id)}"]`)?.value || 'research';
    const data = load();
    data.selected[id] = requestFor(resource, method, purpose);
    save(data);
    renderCards();
  });
  $('connection-list').addEventListener('click', (event) => {
    const id = event.target.dataset.remove;
    if (!id) return;
    const data = load();
    delete data.selected[id];
    data.custom = data.custom.filter((item) => item.id !== id);
    save(data);
    renderCards();
  });
  $('custom-add').addEventListener('click', () => {
    const name = $('custom-name').value.trim();
    const url = $('custom-url').value.trim();
    const scope = $('custom-scope').value.trim();
    if (!name || !/^https:\/\//i.test(url) || !scope) {
      $('resource-summary').textContent = 'Enter a name, an HTTPS official URL, and the smallest approved scope. Do not enter a credential.';
      return;
    }
    const data = load();
    const id = `custom:${Date.now()}`;
    data.custom.push(requestFor({ id, name, setup: url, scope }, $('custom-method').value, $('custom-purpose').value, true));
    save(data);
    ['custom-name', 'custom-url', 'custom-scope'].forEach((field) => { $(field).value = ''; });
    renderCards();
    $('resource-summary').textContent = 'Custom request saved locally. It remains offline and unverified until a reviewed adapter passes a health check.';
  });
  $('resource-export').addEventListener('click', () => {
    const packet = { schema: 'dreamco.buddy.connection_and_publishing_requests.v1', exported_at: new Date().toISOString(), live_connections_claimed: 0, raw_credentials_included: false, exact_approval_required_for_external_writes: true, ...load() };
    const url = URL.createObjectURL(new Blob([JSON.stringify(packet, null, 2)], { type: 'application/json' }));
    const anchor = document.createElement('a');
    anchor.href = url;
    anchor.download = 'buddy-connection-publishing-requests.json';
    anchor.click();
    URL.revokeObjectURL(url);
  });
})();
