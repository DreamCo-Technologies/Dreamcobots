(() => {
  'use strict';
  const navigatorCatalog = window.BUDDY_EXPERT_MODE.invention_navigator;
  const $ = (id) => document.getElementById(id);
  const esc = (value) => String(value ?? '').replace(/[&<>"']/g, (character) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[character]));
  const readable = (value) => String(value || '').replaceAll('_', ' ');
  const resourceMap = new Map(navigatorCatalog.resources.map((item) => [item.id, item]));
  let project = null;
  const incomingIdea = new URLSearchParams(location.search).get('idea');
  if (incomingIdea) $('idea-summary').value = incomingIdea;

  $('metric-stages').textContent = navigatorCatalog.stages.length;
  $('metric-resources').textContent = navigatorCatalog.resources.length;
  $('metric-filings').textContent = navigatorCatalog.truth.live_filings_performed;
  $('metric-contacts').textContent = navigatorCatalog.truth.manufacturers_contacted;

  $('stage-grid').innerHTML = navigatorCatalog.stages.map((stage, index) => `<article class="card"><span class="stage-number">${index + 1}</span><h3>${esc(stage.label)}</h3><p><strong>Outputs</strong><br>${stage.outputs.map(esc).join(' · ')}</p><p class="muted">${stage.resource_ids.length} supporting resources · Not started</p></article>`).join('');
  $('invention-resource-grid').innerHTML = navigatorCatalog.resources.map((resource) => `<article class="card resource"><span class="tag">${esc(readable(resource.connection_status))}</span><h3>${esc(resource.name)}</h3><p>${esc(readable(resource.kind))}</p><p class="muted">${esc(resource.cost)}</p><div class="actions"><a target="_blank" rel="noopener noreferrer" href="${esc(resource.url)}">Open resource</a><a href="resource-connection-center.html?resource=${encodeURIComponent(new URL(resource.url).host)}">Prepare connection</a></div></article>`).join('');

  const regulatorIds = (type) => {
    const ids = new Set();
    if (['electronics', 'mixed'].includes(type)) ids.add('fcc-equipment-authorization');
    if (['consumer_product', 'child_product', 'electronics', 'mixed'].includes(type)) ids.add('cpsc-business-guidance');
    if (type === 'medical_device') ids.add('fda-device-advice');
    return [...ids];
  };

  const buildProject = () => {
    const confidentiality = $('confidentiality').value;
    const publicResearch = $('public-research').checked;
    const prototypeType = $('prototype-type').value;
    project = {
      schema: 'dreamco.buddy_invention_project.v1',
      projectId: $('project-id').value.trim(),
      title: $('project-title').value.trim(),
      ideaSummary: $('idea-summary').value.trim(),
      targetUser: $('target-user').value.trim(),
      jurisdiction: $('country').value.trim(),
      prototypeType,
      budgetUsd: Number($('budget').value),
      confidentiality,
      status: confidentiality === 'private' && publicResearch ? 'confidentiality_conflict_owner_review_required' : 'private_project_plan_ready',
      disclosureRule: navigatorCatalog.confidentiality_warning,
      jurisdictionRule: navigatorCatalog.jurisdiction_rule,
      productSpecificRegulatorResources: regulatorIds(prototypeType).map((id) => resourceMap.get(id)),
      stages: navigatorCatalog.stages.map((stage) => ({ id: stage.id, label: stage.label, status: 'not_started', requiredOutputs: stage.outputs, resources: stage.resource_ids.map((id) => resourceMap.get(id)), ownerApprovalRequiredBeforeExternalAction: true })),
      approvalGates: navigatorCatalog.approval_gates,
      autonomousAllowed: navigatorCatalog.autonomous_allowed,
      externalResearchStarted: false,
      filingsSubmitted: false,
      peopleContacted: false,
      purchasesMade: false,
      legalAdviceProvided: false,
      storeLaunchPerformed: false,
    };
    $('download-project').disabled = false;
    $('ask-buddy').href = `buddy.html?prompt=${encodeURIComponent(`Help me advance ${project.title} through the Idea-to-Store stages. Start privately with the next evidence-backed step. Country: ${project.jurisdiction}. Prototype: ${readable(project.prototypeType)}. Do not file, contact, buy, publish, or claim legal conclusions without my exact approval.`)}`;
    $('project-status').textContent = `${navigatorCatalog.stages.length} stages prepared. Status: ${readable(project.status)}. Held only in this page's memory and cleared on reload; no research, filing, outreach, purchase, or production started.`;
  };

  $('project-form').addEventListener('submit', (event) => { event.preventDefault(); buildProject(); });
  $('download-project').addEventListener('click', () => {
    if (!project) return;
    const link = document.createElement('a');
    link.href = URL.createObjectURL(new Blob([JSON.stringify(project, null, 2)], { type: 'application/json' }));
    link.download = `${project.projectId}.json`; link.click();
    setTimeout(() => URL.revokeObjectURL(link.href), 500);
  });
  $('voice-idea').addEventListener('click', () => {
    const Recognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!Recognition) { $('project-status').textContent = 'Voice recognition is unavailable in this browser. Type the summary instead.'; return; }
    const recognition = new Recognition();
    recognition.lang = navigator.language || 'en-US';
    recognition.interimResults = false;
    recognition.onresult = (event) => { $('idea-summary').value = event.results[0][0].transcript.trim(); buildProject(); };
    recognition.onerror = (event) => { $('project-status').textContent = `Voice error: ${event.error}`; };
    $('project-status').textContent = 'Listening for a nonconfidential idea summary…';
    recognition.start();
  });
})();
