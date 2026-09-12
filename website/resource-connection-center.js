(() => {
  const $ = (id) => document.getElementById(id);
  const key = 'dreamco.buddy.personal-connections.v1';
  const esc = (value) => String(value ?? '').replace(/[&<>"']/g, (character) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[character]));
  let catalog;
  let methods = [];
  const load = () => { try { return JSON.parse(localStorage.getItem(key) || '{}'); } catch { return { selected: {}, custom: [] }; } };
  const save = (value) => localStorage.setItem(key, JSON.stringify(value));

  function render() {
    const query = $('resource-search').value.toLowerCase();
    const visible = catalog.resources.filter((item) => !query || item.host.includes(query) || item.source_lists.join(' ').toLowerCase().includes(query));
    $('resource-summary').textContent = `${catalog.resource_count} discovered resource hosts across ${catalog.scanned_json_lists} machine-readable lists. Showing ${visible.length}.`;
    $('resource-grid').innerHTML = visible.map((item) => `<article class="card"><span class="tag">connection request required</span><h2>${esc(item.host)}</h2><p>${item.url_count} unique HTTPS reference${item.url_count === 1 ? '' : 's'} · ${item.source_lists.length} source list${item.source_lists.length === 1 ? '' : 's'}</p><select data-method="${esc(item.id)}">${methods.map((method) => `<option value="${esc(method.id)}">${esc(method.label)}</option>`).join('')}<option value="mcp_transport">MCP transport</option></select><div class="controls"><a class="btn btn-outline" target="_blank" rel="noopener noreferrer" href="${esc(item.primary_url)}">Open resource</a><button class="btn btn-primary" data-add="${esc(item.id)}">Add to My Buddy</button></div></article>`).join('') || '<p>No matching resource.</p>';
  }

  Promise.all([
    fetch('data/buddy-resource-connection-catalog.json', { cache: 'no-store' }).then((response) => response.json()),
    fetch('data/buddy-connection-catalog.json', { cache: 'no-store' }).then((response) => response.json()),
  ]).then(([resources, connections]) => {
    catalog = resources;
    methods = connections.auth_methods;
    const requestedResource = new URLSearchParams(location.search).get('resource');
    if (requestedResource) $('resource-search').value = requestedResource;
    render();
  }).catch((error) => { $('resource-summary').textContent = `Catalog unavailable: ${error.message}`; });

  $('resource-search').oninput = () => catalog && render();
  $('resource-grid').onclick = (event) => {
    const id = event.target.dataset.add;
    if (!id) return;
    const resource = catalog.resources.find((item) => item.id === id);
    const method = document.querySelector(`[data-method="${CSS.escape(id)}"]`)?.value || 'custom_rest';
    const data = load();
    data.selected ||= {};
    data.custom ||= [];
    data.custom = data.custom.filter((item) => item.id !== id);
    data.custom.push({ id, kind: 'repository resource request', name: resource.host, status: 'pending_backend_review', description: `${method} request from ${resource.source_lists.length} repository list(s).`, scope: 'Read-only and sandboxed until the user approves a narrower live scope.', setup: resource.primary_url });
    save(data);
    event.target.textContent = 'Added to My Buddy';
  };
})();
