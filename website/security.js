(function () {
  'use strict';

  const catalog = window.BUDDY_OPEN_SECURE_AI_DEFENSE;
  const byId = (id) => document.getElementById(id);
  const FLOATING_REVISIONS = new Set(['main', 'master', 'latest', 'head', 'stable', 'dev', 'develop', 'nightly']);
  const SAFE_MODEL_FORMATS = new Set(['safetensors', 'gguf', 'onnx', 'tflite']);
  const APPROVED_HOSTS = new Set(['github.com', 'gitlab.com', 'codeberg.org', 'huggingface.co', 'pypi.org', 'npmjs.com', 'www.npmjs.com', 'ghcr.io']);
  const TOKEN_LIKE = /(?:github_pat_|gh[opsu]_|ghs_|(?:sk|rk)_(?:live|test)_|BEGIN .*PRIVATE KEY)/i;
  const modelTasks = [
    ['reasoning', 'Reasoning'],
    ['coding', 'Coding'],
    ['agents', 'Agent and tool use'],
    ['vision', 'Vision'],
    ['audio', 'Audio'],
    ['video', 'Video'],
    ['multilingual', 'Multilingual'],
    ['embeddings', 'Embeddings'],
    ['safety', 'Safety and security'],
  ];
  let currentAssessment = null;
  let currentGitHubPlan = null;
  let currentModelPlan = null;

  function text(node, value) {
    node.textContent = String(value ?? '');
    return node;
  }

  function element(tag, className, value) {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (value !== undefined) text(node, value);
    return node;
  }

  function setHidden(id, hidden) {
    byId(id).hidden = hidden;
  }

  function selectedValues(name) {
    return Array.from(document.querySelectorAll(`input[name="${name}"]:checked`)).map((input) => input.value);
  }

  function downloadJson(name, value) {
    const blob = new Blob([`${JSON.stringify(value, null, 2)}\n`], { type: 'application/json' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = name;
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(link.href);
  }

  function hash16(value) {
    let first = 2166136261;
    let second = 2246822519;
    for (let index = 0; index < value.length; index += 1) {
      first ^= value.charCodeAt(index);
      first = Math.imul(first, 16777619);
      second ^= value.charCodeAt(index) + index;
      second = Math.imul(second, 3266489917);
    }
    const left = (first >>> 0).toString(16).padStart(8, '0');
    const right = (second >>> 0).toString(16).padStart(8, '0');
    return `${left}${right}`;
  }

  function finding(id, severity, title, action) {
    return { id, severity, title, action };
  }

  function validatedSource(raw) {
    const source = new URL(raw);
    if (source.protocol !== 'https:' || source.username || source.password || source.search || source.hash) {
      throw new Error('Use an official HTTPS source without credentials, query strings, or fragments.');
    }
    if (!APPROVED_HOSTS.has(source.hostname.toLowerCase())) {
      throw new Error('This source host needs a manual trust review before Buddy may inspect it.');
    }
    return source;
  }

  function evidenceValue(id) {
    const value = byId(id).value.trim();
    if (TOKEN_LIKE.test(value)) throw new Error('Evidence fields accept references only, never credentials.');
    return value || null;
  }

  function readAssessmentRequest() {
    const sourceKind = byId('defense-source-kind').value;
    return {
      userProfileId: byId('defense-profile').value.trim(),
      sourceKind,
      sourceUrl: byId('defense-source-url').value.trim(),
      exactRevision: byId('defense-revision').value.trim(),
      declaredLicense: byId('defense-license').value.trim(),
      intendedUse: byId('defense-purpose').value,
      ownerConfirmsRights: byId('defense-rights').checked,
      checksum: evidenceValue('defense-checksum'),
      signatureEvidence: evidenceValue('defense-signature'),
      sbomReference: evidenceValue('defense-sbom'),
      provenanceReference: evidenceValue('defense-provenance'),
      modelCardReference: sourceKind === 'model_weights' ? evidenceValue('defense-model-card') : null,
      artifactFormat: sourceKind === 'model_weights' ? byId('defense-format').value : null,
      trustRemoteCode: byId('defense-remote-code').checked,
      networkDuringBuild: byId('defense-network').checked,
      requestsProtectedBranchWrite: byId('defense-protected-write').checked,
      requestsAutomaticMerge: byId('defense-auto-merge').checked,
      containsUnredactedSecrets: byId('defense-secrets').checked,
    };
  }

  function assessLocally(request) {
    const source = validatedSource(request.sourceUrl);
    const findings = [];
    if (!/^[A-Za-z0-9_.:-]{3,96}$/.test(request.userProfileId)) {
      throw new Error('Profile IDs may use letters, numbers, dots, colons, underscores, and hyphens.');
    }
    if (!request.exactRevision || FLOATING_REVISIONS.has(request.exactRevision.toLowerCase())) {
      findings.push(finding('floating-revision', 'blocked', 'Revision is mutable', 'Pin an exact commit, immutable tag, package version, image digest, or model revision.'));
    }
    if (!request.ownerConfirmsRights) findings.push(finding('rights-unconfirmed', 'blocked', 'Usage rights are not confirmed', 'Confirm the exact source and dependency terms.'));
    if (request.containsUnredactedSecrets) findings.push(finding('secret-material', 'blocked', 'Unredacted secrets are present', 'Remove credentials and use approved vault references.'));
    if (request.trustRemoteCode) findings.push(finding('remote-code', 'blocked', 'Remote model code was requested', 'Use a reviewed adapter with remote code disabled.'));
    if (request.requestsProtectedBranchWrite) findings.push(finding('protected-branch', 'blocked', 'Protected-branch write was requested', 'Use a dedicated review branch and draft pull request.'));
    if (request.requestsAutomaticMerge) findings.push(finding('automatic-merge', 'blocked', 'Automatic merge was requested', 'Require tests and exact owner approval before merge.'));
    if (request.sourceKind === 'model_weights') {
      if (!SAFE_MODEL_FORMATS.has(String(request.artifactFormat).toLowerCase())) findings.push(finding('unsafe-model-format', 'blocked', 'Model format is unsafe', 'Use Safetensors, GGUF, ONNX, or TFLite.'));
      if (!request.modelCardReference) findings.push(finding('missing-model-card', 'review', 'Model card is missing', 'Record the exact model card and usage limits.'));
    }
    if (!/^sha256:[a-f0-9]{64}$/i.test(request.checksum || '')) findings.push(finding('missing-checksum', 'review', 'Valid SHA-256 evidence is missing', 'Calculate and record the artifact checksum.'));
    if (!request.signatureEvidence) findings.push(finding('missing-signature', 'review', 'Signature evidence is missing', 'Verify a publisher signature or document a manual provenance review.'));
    if (!request.sbomReference) findings.push(finding('missing-sbom', 'review', 'SBOM evidence is missing', 'Generate an SBOM and map known vulnerabilities.'));
    if (!request.provenanceReference) findings.push(finding('missing-provenance', 'review', 'Build provenance is missing', 'Record source, builder, dependency lock, and artifact evidence.'));
    if (request.networkDuringBuild) findings.push(finding('network-request', 'review', 'Build network access was requested', 'Approve a one-run destination allowlist and capture every request.'));
    const hasBlocked = findings.some((row) => row.severity === 'blocked');
    const hasReview = findings.some((row) => row.severity === 'review');
    const status = hasBlocked ? 'blocked' : hasReview ? 'review_required' : 'sandbox_candidate';
    return {
      schema: 'dreamco.buddy_defense_assessment.v1',
      assessmentId: `def-${hash16([request.userProfileId, request.sourceUrl, request.exactRevision, request.intendedUse].join('|'))}`,
      status,
      riskScore: Math.min(100, findings.reduce((score, row) => score + (row.severity === 'blocked' ? 24 : 8), 0)),
      source: {
        kind: request.sourceKind,
        url: source.toString(),
        host: source.hostname,
        exactRevision: request.exactRevision,
        declaredLicense: request.declaredLicense,
        artifactFormat: request.artifactFormat,
      },
      intendedUse: request.intendedUse,
      findings,
      evidence: {
        checksum: request.checksum,
        signature: request.signatureEvidence,
        sbom: request.sbomReference,
        provenance: request.provenanceReference,
        modelCard: request.modelCardReference,
      },
      nextStage: status === 'sandbox_candidate' ? 'owner_approved_disposable_sandbox' : status === 'review_required' ? 'complete_missing_evidence' : 'resolve_blocking_findings',
      executionPerformed: false,
      sourceDownloaded: false,
      connectionEstablished: false,
      controls: catalog.open_source_upgrade_contract,
    };
  }

  function renderAssessment(result) {
    const titles = {
      blocked: 'Blocked before execution',
      review_required: 'Evidence review required',
      sandbox_candidate: 'Ready for an approved sandbox',
    };
    text(byId('defense-assessment-title'), titles[result.status]);
    text(byId('defense-risk-score'), result.riskScore);
    text(byId('defense-assessment-detail'), `Assessment ${result.assessmentId}. No source was downloaded or executed. Next: ${result.nextStage.replaceAll('_', ' ')}.`);
    const list = byId('defense-finding-list');
    list.replaceChildren();
    if (!result.findings.length) {
      list.appendChild(element('li', '', 'All intake evidence gates passed. Execution still requires an owner-approved disposable sandbox.'));
    } else {
      for (const row of result.findings) {
        const item = element('li');
        const title = element('strong', '', `${row.severity.toUpperCase()}: ${row.title}. `);
        item.append(title, document.createTextNode(row.action));
        list.appendChild(item);
      }
    }
    byId('defense-download-assessment').disabled = false;
    byId('defense-prepare-upgrade').disabled = result.status !== 'sandbox_candidate';
  }

  function onAssessmentSubmit(event) {
    event.preventDefault();
    try {
      currentAssessment = assessLocally(readAssessmentRequest());
      renderAssessment(currentAssessment);
    } catch (error) {
      currentAssessment = null;
      text(byId('defense-assessment-title'), 'Assessment could not start');
      text(byId('defense-risk-score'), '--');
      text(byId('defense-assessment-detail'), error instanceof Error ? error.message : 'Invalid assessment request.');
      byId('defense-finding-list').replaceChildren();
      byId('defense-download-assessment').disabled = true;
      byId('defense-prepare-upgrade').disabled = true;
    }
  }

  function readRepositories() {
    const values = byId('github-repositories').value.split(/[\s,]+/).map((value) => value.trim()).filter(Boolean);
    const unique = Array.from(new Set(values));
    if (!unique.length || unique.some((value) => !/^[A-Za-z0-9_.-]+\/[A-Za-z0-9_.-]+$/.test(value))) {
      throw new Error('Use at least one repository in owner/name format.');
    }
    return unique;
  }

  function onGitHubPlanSubmit(event) {
    event.preventDefault();
    try {
      if (!byId('github-connection-approval').checked) throw new Error('Approve the repository-scoped connection plan first.');
      const callback = new URL(byId('github-callback').value);
      const loopback = callback.protocol === 'http:' && ['127.0.0.1', 'localhost', '::1'].includes(callback.hostname);
      if (callback.protocol !== 'https:' && !loopback) throw new Error('Use HTTPS or an owner-controlled loopback callback.');
      const githubLogin = byId('github-login').value.trim();
      if (!/^[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?$/.test(githubLogin)) throw new Error('Enter a valid GitHub login.');
      currentGitHubPlan = {
        schema: 'dreamco.buddy_github_profile_connection_plan.v1',
        status: 'deployment_configuration_required',
        userProfileId: byId('github-user-profile').value.trim(),
        expectedGitHubLogin: githubLogin,
        callbackOrigin: callback.origin,
        repositoryAllowlist: readRepositories(),
        identity: { protocol: 'oauth_pkce', scopes: ['read:user'], authorizationPerformed: false },
        repositoryAuthority: {
          protocol: 'github_app_installation',
          permissions: Array.from(new Set(['metadata:read', ...selectedValues('github-permission')])),
          installationPerformed: false,
          organizationWideAccess: false,
        },
        credentialHandling: {
          browserAcceptsRawToken: false,
          publicApiReturnsRawToken: false,
          storage: 'encrypted_vault_reference_only',
          rotationAndRevocationRequired: true,
        },
        connected: false,
        connectionHealthVerified: false,
        requiredSteps: [
          'Configure the OAuth client and exact callback URL.',
          'Install the repository app only on the selected repositories.',
          'Complete owner authorization and verify the returned GitHub identity.',
          'Store only encrypted credential references under this Buddy profile.',
          'Run a read-only health check and record the granted permissions.',
        ],
      };
      text(byId('github-plan-title'), 'Configuration and owner authorization required');
      text(byId('github-plan-detail'), `${currentGitHubPlan.repositoryAllowlist.length} repository or repositories are allowlisted. This plan is not a live connection.`);
      const steps = byId('github-plan-steps');
      steps.replaceChildren(...currentGitHubPlan.requiredSteps.map((step) => element('li', '', step)));
      byId('download-github-plan').disabled = false;
    } catch (error) {
      currentGitHubPlan = null;
      text(byId('github-plan-title'), 'Connection plan could not be prepared');
      text(byId('github-plan-detail'), error instanceof Error ? error.message : 'Invalid GitHub plan.');
      byId('github-plan-steps').replaceChildren();
      byId('download-github-plan').disabled = true;
    }
  }

  function checkboxOption(name, value, label, checked) {
    const wrapper = element('label');
    const input = document.createElement('input');
    input.type = 'checkbox';
    input.name = name;
    input.value = value;
    input.checked = Boolean(checked);
    wrapper.append(input, document.createTextNode(label));
    return wrapper;
  }

  function renderModelOptions() {
    const sourceOptions = byId('model-source-options');
    const taskOptions = byId('model-task-options');
    sourceOptions.replaceChildren();
    taskOptions.replaceChildren();
    catalog.model_discovery_sources.forEach((source, index) => {
      sourceOptions.appendChild(checkboxOption('model-source', source.id, source.label, index < 4));
    });
    modelTasks.forEach(([id, label], index) => {
      taskOptions.appendChild(checkboxOption('model-task', id, label, index < 3 || id === 'safety'));
    });
  }

  function onModelDiscoverySubmit(event) {
    event.preventDefault();
    const sourceIds = selectedValues('model-source');
    const taskCategories = selectedValues('model-task');
    if (!sourceIds.length || !taskCategories.length) {
      text(byId('model-discovery-title'), 'Choose at least one source and task');
      text(byId('model-discovery-detail'), 'Discovery plans need both an official source and a task-matched benchmark goal.');
      return;
    }
    const sources = sourceIds.map((id) => catalog.model_discovery_sources.find((source) => source.id === id)).filter(Boolean);
    const allowNetwork = byId('model-discovery-network').checked;
    const approvePaid = byId('model-discovery-paid').checked;
    const maxBudgetUsd = Number(byId('model-discovery-budget').value || 0);
    const hasHosted = sources.some((source) => ['hosted_api', 'hosted_and_open_weight'].includes(source.access));
    const status = !allowNetwork && hasHosted
      ? 'network_approval_required'
      : allowNetwork && approvePaid && maxBudgetUsd <= 0
        ? 'positive_budget_required'
        : allowNetwork
          ? 'configured_discovery_adapters_required'
          : 'local_discovery_plan_ready';
    currentModelPlan = {
      schema: 'dreamco.buddy_model_discovery_plan.v1',
      status,
      sources,
      taskCategories,
      currentOpenModelWatchlist: catalog.priority_open_model_watchlist_2026,
      maxBudgetUsd,
      networkApprovedForThisPlan: allowNetwork,
      paidDiscoveryApprovedForThisPlan: approvePaid,
      discoveryPerformed: false,
      liveModelsCalled: 0,
      qualityClaimsProduced: 0,
      evidenceRequired: [
        'exact model id and revision',
        'official source and access terms',
        'task-matched signed fixtures',
        'latency, resource, cost, safety, and failure results',
        'UTC observation time and adapter version',
      ],
    };
    text(byId('model-discovery-title'), status.replaceAll('_', ' '));
    text(byId('model-discovery-detail'), `${sources.length} sources and ${taskCategories.length} task groups selected. No model was called and no quality result was invented.`);
    byId('download-model-discovery').disabled = false;
  }

  function catalogRows() {
    const alliance = catalog.alliance_reference_tools.map((row) => ({ ...row, group: 'alliance', summary: row.purpose }));
    const projects = catalog.openssf_projects.map((row) => ({ ...row, group: 'openssf', summary: row.purpose }));
    const models = catalog.model_discovery_sources.map((row) => ({ ...row, group: 'models', summary: `${row.discovery_method}. Status: ${row.connection_status.replaceAll('_', ' ')}.` }));
    return [...alliance, ...projects, ...models];
  }

  function renderCatalog() {
    const query = byId('defense-catalog-search').value.trim().toLowerCase();
    const group = byId('defense-catalog-filter').value;
    const rows = catalogRows().filter((row) => {
      const matchesGroup = group === 'all' || row.group === group;
      const haystack = `${row.label} ${row.summary} ${row.group}`.toLowerCase();
      return matchesGroup && (!query || haystack.includes(query));
    });
    const list = byId('defense-catalog-list');
    list.replaceChildren();
    text(byId('defense-catalog-count'), `${rows.length} of ${catalogRows().length} references shown.`);
    if (!rows.length) {
      list.appendChild(element('p', 'empty-row', 'No references match these filters.'));
      return;
    }
    for (const row of rows) {
      const item = element('article', 'catalog-row');
      const identity = element('div');
      identity.append(element('span', 'catalog-tag', row.group), element('strong', '', row.label));
      const summary = element('p', '', row.summary);
      const link = element('a', '', 'Official source');
      link.href = row.official_source;
      link.target = '_blank';
      link.rel = 'noopener noreferrer';
      item.append(identity, summary, link);
      list.appendChild(item);
    }
  }

  function renderThreats() {
    const list = byId('defense-threat-list');
    list.replaceChildren();
    for (const threat of catalog.threat_domains) {
      const row = element('div', 'threat-row');
      row.append(element('strong', '', threat.label), element('span', '', threat.required_control));
      list.appendChild(row);
    }
  }

  function renderProducts() {
    const list = byId('defense-product-list');
    list.replaceChildren();
    for (const profile of catalog.product_profiles) {
      const row = element('article', 'product-row');
      row.append(
        element('span', '', 'Policy profile'),
        element('h3', '', profile.label),
        element('p', '', profile.scope),
      );
      list.appendChild(row);
    }
  }

  function renderSummary() {
    text(byId('defense-tool-count'), catalog.summary.alliance_reference_tools);
    text(byId('defense-project-count'), catalog.summary.openssf_projects);
    text(byId('defense-threat-count'), catalog.summary.threat_domains);
    text(byId('defense-source-count'), catalog.summary.model_discovery_sources);
    text(byId('defense-live-count'), catalog.summary.live_company_connections);
    text(byId('defense-catalog-status'), `Reviewed ${catalog.catalog_reviewed_on}`);
  }

  function openBuddy(prompt) {
    window.location.href = `buddy.html?prompt=${encodeURIComponent(prompt)}`;
  }

  function bindEvents() {
    byId('run-defense-assessment').setAttribute('aria-describedby', 'defense-assessment-detail');
    byId('prepare-github-profile').setAttribute('aria-describedby', 'github-plan-detail');
    byId('prepare-model-discovery').setAttribute('aria-describedby', 'model-discovery-detail');
    byId('defense-assessment-form').addEventListener('submit', onAssessmentSubmit);
    byId('defense-source-kind').addEventListener('change', () => {
      const model = byId('defense-source-kind').value === 'model_weights';
      setHidden('defense-format-field', !model);
      setHidden('defense-model-card-field', !model);
    });
    byId('defense-download-assessment').addEventListener('click', () => {
      if (currentAssessment) downloadJson(`${currentAssessment.assessmentId}.json`, currentAssessment);
    });
    byId('defense-prepare-upgrade').addEventListener('click', () => {
      if (!currentAssessment || currentAssessment.status !== 'sandbox_candidate') return;
      openBuddy(`Prepare a secure open-source upgrade for ${currentAssessment.source.url} at ${currentAssessment.source.exactRevision}. Use assessment ${currentAssessment.assessmentId}. Create a review branch and draft pull request only. Verify license, signature, checksum, SBOM, provenance, sandbox tests, rollback, and my exact approval. Do not merge, publish, install, spend, or run outside the sandbox.`);
    });
    byId('github-profile-form').addEventListener('submit', onGitHubPlanSubmit);
    byId('download-github-plan').addEventListener('click', () => {
      if (currentGitHubPlan) downloadJson('buddy-github-profile-connection-plan.json', currentGitHubPlan);
    });
    byId('model-discovery-form').addEventListener('submit', onModelDiscoverySubmit);
    byId('download-model-discovery').addEventListener('click', () => {
      if (currentModelPlan) downloadJson('buddy-model-discovery-plan.json', currentModelPlan);
    });
    byId('defense-catalog-search').addEventListener('input', renderCatalog);
    byId('defense-catalog-filter').addEventListener('change', renderCatalog);
    byId('defense-ask-buddy').addEventListener('click', () => {
      openBuddy('Open Buddy Defense Center mode. Help me assess an AI model, agent, package, container, repository, GitHub connection, or secure open-source upgrade. Start with official sources and exact revisions. Explain risks plainly. Do not connect accounts, download, install, execute, spend, merge, publish, or disclose a vulnerability without the required authorization and evidence.');
    });
  }

  if (!catalog || !catalog.summary) {
    text(byId('defense-catalog-status'), 'Catalog unavailable');
    return;
  }
  renderSummary();
  renderModelOptions();
  renderCatalog();
  renderThreats();
  renderProducts();
  bindEvents();
})();
