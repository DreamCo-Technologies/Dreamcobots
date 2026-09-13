(() => {
  'use strict';
  const catalog = window.BUDDY_EXPERT_MODE;
  const $ = (id) => document.getElementById(id);
  const esc = (value) => String(value ?? '').replace(/[&<>"']/g, (character) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[character]));
  const readable = (value) => String(value || '').replaceAll('_', ' ');
  const dayForResource = new Map(catalog.days.flatMap((day) => day.resource_ids.map((id) => [id, day.day])));
  let resources = [];
  let sprint = null;
  let resourceLimit = 120;
  const incomingGoal = new URLSearchParams(location.search).get('goal');
  if (incomingGoal) $('sprint-goal').value = incomingGoal;

  $('metric-days').textContent = catalog.summary.days;
  $('metric-resources').textContent = catalog.summary.repository_resources;
  $('metric-sections').textContent = catalog.summary.resource_sections;
  $('metric-live').textContent = catalog.summary.runtime_verified_external_connections;

  $('day-grid').innerHTML = catalog.days.map((day) => `<article class="card day"><div class="day-meta"><strong>Day ${day.day}</strong><span>${day.resource_count} resources</span></div><h3>${esc(day.label)}</h3><p>${esc(day.outcome)}</p><p class="muted">Evidence: ${day.evidence_required.map(esc).join(' · ')}</p><a href="#resources" data-filter-day="${day.day}">Show this day</a></article>`).join('');
  $('day-filter').innerHTML += catalog.days.map((day) => `<option value="${day.day}">Day ${day.day}: ${esc(day.label)}</option>`).join('');
  $('connection-methods').innerHTML = catalog.connections.methods.map((method) => `<code>${esc(readable(method))}</code>`).join('');
  $('learning-source-grid').innerHTML = catalog.learning_sources.sources.map((source) => `<article class="card"><span class="tag">${esc(readable(source.readiness))}</span><h3>${esc(source.label)}</h3><p>${esc(source.learning_output)}</p><p class="muted">Permission: ${esc(source.permission)}</p></article>`).join('');

  const buildSprint = () => {
    const hours = Number($('hours-day').value);
    const days = catalog.days.map((day) => ({
      day: day.day,
      id: day.id,
      label: day.label,
      resourceCount: day.resource_count,
      resourceIds: day.resource_ids,
      minutesAvailable: hours * 60,
      minutesPerResource: day.resource_count ? (hours * 60) / day.resource_count : 0,
      protocol: day.protocol,
      evidenceRequired: day.evidence_required,
      status: 'scheduled_not_executed',
    }));
    const privateWorkspace = $('private-workspace').checked;
    const publicRetrieval = $('external-retrieval').checked;
    sprint = {
      schema: 'dreamco.buddy_expert_sprint.v1',
      sprintId: `expert-week-${new Date().toISOString().slice(0, 10)}`,
      goal: $('sprint-goal').value.trim(),
      learningStyle: $('learning-style').value,
      status: !privateWorkspace ? 'private_workspace_confirmation_required' : !publicRetrieval ? 'external_retrieval_approval_required' : 'retrieval_adapter_and_daily_execution_required',
      days,
      resourceCount: resources.length,
      includesEveryRepositoryResource: true,
      feasibility: Math.min(...days.filter((day) => day.resourceCount).map((day) => day.minutesPerResource)) < 5 ? 'routing_and_indexing_sprint_not_content_mastery' : 'bounded_study_sprint_mastery_still_requires_evidence',
      evidenceGates: catalog.evidence_gates,
      learningStarted: false,
      externalRequestsStarted: false,
      masteryClaimed: false,
      productionPromotionPerformed: false,
    };
    $('download-sprint').disabled = false;
    $('sprint-status').textContent = `${resources.length} resources scheduled across 7 days. Status: ${readable(sprint.status)}. No retrieval, training, or external connection has started.`;
  };

  $('sprint-form').addEventListener('submit', (event) => { event.preventDefault(); buildSprint(); });
  $('speak-sprint').addEventListener('click', () => {
    const Recognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!Recognition) { $('sprint-status').textContent = 'Voice recognition is unavailable in this browser. Type the goal instead.'; return; }
    const recognition = new Recognition();
    recognition.lang = navigator.language || 'en-US';
    recognition.interimResults = false;
    recognition.onresult = (event) => { $('sprint-goal').value = event.results[0][0].transcript.trim(); buildSprint(); };
    recognition.onerror = (event) => { $('sprint-status').textContent = `Voice error: ${event.error}`; };
    $('sprint-status').textContent = 'Listening for your Expert Mode goal…';
    recognition.start();
  });
  $('download-sprint').addEventListener('click', () => {
    if (!sprint) return;
    const link = document.createElement('a');
    link.href = URL.createObjectURL(new Blob([JSON.stringify(sprint, null, 2)], { type: 'application/json' }));
    link.download = `${sprint.sprintId}.json`; link.click();
    setTimeout(() => URL.revokeObjectURL(link.href), 500);
  });

  const renderResources = () => {
    const query = $('resource-search').value.trim().toLowerCase();
    const day = $('day-filter').value;
    const visible = resources.filter((resource) => {
      const text = `${resource.host} ${resource.connection_status} ${resource.source_lists.join(' ')}`.toLowerCase();
      return (!query || text.includes(query)) && (day === 'all' || String(dayForResource.get(resource.id)) === day);
    });
    $('resource-status').textContent = `Showing ${visible.length} of ${resources.length} resources. Live runtime connections proven: ${catalog.summary.runtime_verified_external_connections}.`;
    $('resource-grid').innerHTML = visible.slice(0, resourceLimit).map((resource) => `<article class="card resource-card"><span class="tag">${esc(readable(resource.connection_status))}</span><h3>${esc(resource.host)}</h3><p class="muted">Day ${dayForResource.get(resource.id)} · ${resource.url_count} URL · ${resource.source_lists.length} source list${resource.source_lists.length === 1 ? '' : 's'}</p><div class="actions"><a target="_blank" rel="noopener noreferrer" href="${esc(resource.primary_url)}">Open source</a><a href="resource-connection-center.html?resource=${encodeURIComponent(resource.host)}">Add connection</a></div></article>`).join('') || '<p>No matching resource.</p>';
    $('load-more-resources').hidden = visible.length <= resourceLimit;
    if (visible.length > resourceLimit) $('resource-status').textContent += ` ${resourceLimit} are displayed; use Show more or narrow the search.`;
  };
  $('resource-search').addEventListener('input', () => { resourceLimit = 120; renderResources(); });
  $('day-filter').addEventListener('change', () => { resourceLimit = 120; renderResources(); });
  $('load-more-resources').addEventListener('click', () => { resourceLimit += 120; renderResources(); });
  $('day-grid').addEventListener('click', (event) => {
    const day = event.target.dataset.filterDay;
    if (!day) return;
    $('day-filter').value = day; renderResources();
  });
  fetch(catalog.resource_catalog_url, { cache: 'no-store' })
    .then((response) => { if (!response.ok) throw new Error(`resource catalog returned ${response.status}`); return response.json(); })
    .then((resourceCatalog) => { resources = resourceCatalog.resources || []; renderResources(); })
    .catch((error) => { $('resource-status').textContent = `Resource catalog unavailable: ${error.message}`; });
})();
