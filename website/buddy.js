(function () {
  'use strict';

  const index = window.BUDDY_ROUTING_INDEX || { summary: { profiles: 0, capabilities: 0 }, bots: [] };
  const modelPolicy = window.BUDDY_MODEL_ROUTER || { defaultMode: 'free', connectors: [] };
  const certifications = window.BUDDY_CAPABILITY_CERTIFICATIONS || { summary: {}, bots: {} };
  const setupCatalog = window.BUDDY_SETUP_CATALOG || { repository: {}, summary: {}, launchers: [] };
  const bots = index.bots.map(unpack);
  const botBySlug = new Map(bots.map((bot) => [bot.slug, bot]));
  const launcherById = new Map(setupCatalog.launchers.map((launcher) => [launcher.id, launcher]));

  const input = document.getElementById('buddy-input');
  const sendButton = document.getElementById('buddy-send');
  const thread = document.getElementById('buddy-thread');
  const welcome = document.getElementById('buddy-welcome');
  const routeStatus = document.getElementById('buddy-route-status');
  const freeButton = document.getElementById('model-free');
  const premiumButton = document.getElementById('model-premium');
  const premiumPanel = document.getElementById('premium-panel');
  const premiumProvider = document.getElementById('premium-provider');
  const premiumModelId = document.getElementById('premium-model-id');
  const premiumApproval = document.getElementById('premium-approval');
  const premiumBack = document.getElementById('premium-back');
  const specialistOpen = document.getElementById('specialist-open');
  const specialistDialog = document.getElementById('specialist-dialog');
  const specialistSearch = document.getElementById('specialist-search');
  const specialistResults = document.getElementById('specialist-results');
  const specialistClose = document.getElementById('specialist-close');
  const specialistSummary = document.getElementById('specialist-summary');
  const localOpen = document.getElementById('local-open');
  const localDialog = document.getElementById('local-dialog');
  const localClose = document.getElementById('local-close');
  const localStatus = document.getElementById('local-status');
  const localStatusDetail = document.getElementById('local-status-detail');
  const localStatusDot = document.getElementById('local-status-dot');
  const localPause = document.getElementById('local-pause');
  const localAudit = document.getElementById('local-audit');
  const boundaryOpen = document.getElementById('boundary-open');
  const boundaryDialog = document.getElementById('boundary-dialog');
  const boundaryClose = document.getElementById('boundary-close');
  const boundaryForm = document.getElementById('boundary-form');
  const setupDialog = document.getElementById('setup-dialog');
  const setupClose = document.getElementById('setup-close');
  const setupTitle = document.getElementById('setup-title');
  const setupEyebrow = document.getElementById('setup-eyebrow');
  const setupOptions = document.getElementById('setup-options');
  const setupCount = document.getElementById('setup-count');
  const setupStatus = document.getElementById('setup-status');
  const setupRun = document.getElementById('setup-run');
  const setupWorkspace = document.getElementById('setup-workspace');
  const scheduleControls = document.getElementById('schedule-controls');
  const scheduleOpen = document.getElementById('schedule-open');
  const scheduleDialog = document.getElementById('schedule-dialog');
  const scheduleClose = document.getElementById('schedule-close');
  const scheduleList = document.getElementById('schedule-list');
  const scheduleSummary = document.getElementById('schedule-summary');
  const params = new URLSearchParams(location.search);
  const preferredSlug = params.get('bot') || '';
  let activeSlug = preferredSlug;
  let ownerSelectedSpecialist = Boolean(preferredSlug);
  let mode = 'Build';
  let modelMode = modelPolicy.defaultMode || 'free';
  let localBridgePaused = false;
  let boundaryPreferences = loadBoundaryPreferences();
  let activeLauncher = null;
  let executionMode = 'now';
  let selectedSetupOptions = new Set();
  let scheduledTaskRunning = false;
  const scheduleStorageKey = 'buddy-scheduled-tasks-v2';

  function loadBoundaryPreferences() {
    const defaults = {
      guidanceDepth: 'standard',
      riskDisclosure: 'detailed',
      approvalMode: 'confirm_each_external_action',
      moneyActionMode: 'plan_only',
      professionalSupport: 'draft_and_prepare',
      communicationStyle: 'conversational',
      voiceToneAdaptation: false,
    };
    try {
      return { ...defaults, ...JSON.parse(localStorage.getItem('buddy-boundary-preferences-v1') || '{}') };
    } catch (_error) {
      return defaults;
    }
  }

  const localHash = new URLSearchParams(location.hash.slice(1));
  if (localHash.has('buddy-local-token')) {
    sessionStorage.setItem('buddy-local-token', localHash.get('buddy-local-token'));
    history.replaceState(null, '', `${location.pathname}${location.search}`);
  }
  const localToken = sessionStorage.getItem('buddy-local-token') || '';

  const stopWords = new Set([
    'about', 'after', 'again', 'also', 'because', 'before', 'build', 'buddy', 'could', 'create',
    'from', 'have', 'help', 'into', 'make', 'need', 'please', 'should', 'that', 'their', 'then',
    'this', 'through', 'using', 'want', 'with', 'would', 'your',
  ]);
  const synonyms = {
    app: ['application', 'software', 'code', 'device'], application: ['app', 'software', 'code'],
    bug: ['debug', 'error', 'failure'], class: ['course', 'education', 'learning'],
    code: ['coding', 'software', 'development'], course: ['class', 'education', 'learning'],
    database: ['data', 'server', 'integration'], device: ['app', 'connection', 'automation'],
    domain: ['website', 'dns', 'hosting', 'launch'], game: ['gaming', 'player', 'simulation'],
    actor: ['video', 'media', 'creative', 'production'], car: ['vehicle', 'automotive', 'simulation', 'repair'],
    house: ['building', 'construction', 'real', 'estate', 'simulation'], movie: ['film', 'video', 'media', 'creative', 'production'],
    simulation: ['game', 'training', 'model', 'practice'], vehicle: ['car', 'automotive', 'repair', 'simulation'],
    invention: ['prototype', 'patent', 'design', 'research'], job: ['career', 'employment', 'hiring'],
    money: ['finance', 'income', 'revenue'], prototype: ['design', 'development', 'testing', 'simulation'],
    property: ['real', 'estate', 'commercial'], server: ['database', 'api', 'integration'],
    song: ['music', 'audio', 'production'], video: ['media', 'creative', 'production'],
    website: ['responsive', 'web', 'software', 'domain'],
  };

  function normalize(value) {
    return String(value || '').toLowerCase().replace(/[^a-z0-9]+/g, ' ').trim();
  }

  function tokens(value) {
    const base = normalize(value).split(/\s+/).filter((token) => token.length >= 3 && !stopWords.has(token));
    const expanded = new Set(base);
    base.forEach((token) => (synonyms[token] || []).forEach((item) => expanded.add(item)));
    return expanded;
  }

  function unpack(row) {
    return {
      slug: row[0], name: row[1], division: row[2], category: row[3], mission: row[4],
      capabilities: String(row[5] || '').split(' | ').filter(Boolean), emoji: row[6] || 'B',
    };
  }

  function capabilityMatches(bot, objective) {
    const normalizedObjective = normalize(objective);
    const objectiveTokens = tokens(objective);
    return bot.capabilities.map((capability) => {
      const overlap = [...tokens(capability)].filter((token) => objectiveTokens.has(token)).length;
      return { capability, score: (normalizedObjective.includes(normalize(capability)) ? 80 : 0) + overlap * 14 };
    }).filter((match) => match.score > 0).sort((a, b) => b.score - a.score || a.capability.localeCompare(b.capability));
  }

  function score(bot, objective) {
    const normalizedObjective = normalize(objective);
    const objectiveTokens = tokens(objective);
    const overlap = (value, weight) => [...tokens(value)].filter((token) => objectiveTokens.has(token)).length * weight;
    let total = 0;
    if (normalizedObjective.includes(normalize(bot.name))) total += 180;
    if (normalizedObjective.includes(normalize(bot.slug))) total += 220;
    total += overlap(`${bot.name} ${bot.slug}`, 20);
    total += overlap(`${bot.division} ${bot.category}`, 8);
    total += overlap(bot.mission, 3);
    total += capabilityMatches(bot, objective).reduce((sum, match) => sum + match.score, 0);
    return total;
  }

  function localModelPlan() {
    const connectorId = modelMode === 'premium' ? premiumProvider.value : 'buddy_native';
    const connector = modelPolicy.connectors.find((item) => item.id === connectorId)
      || modelPolicy.connectors.find((item) => item.mode === modelMode)
      || { id: 'buddy_native', label: 'Buddy Native' };
    const paidApproved = modelMode === 'premium' && premiumApproval.checked;
    return {
      mode: modelMode,
      connector,
      selectedModelId: premiumModelId.value.trim() || 'provider_default_for_task',
      status: modelMode === 'free'
        ? 'free_route_ready'
        : paidApproved ? 'configuration_required' : 'paid_approval_required',
      paidUseApprovedForThisRequest: paidApproved,
      automaticPaidUpgrade: false,
      providerCallExecuted: false,
    };
  }

  function localRoute(objective) {
    const preferred = ownerSelectedSpecialist ? botBySlug.get(activeSlug) : undefined;
    const ranked = bots.map((bot) => ({ bot, score: score(bot, objective) }))
      .sort((a, b) => b.score - a.score || a.bot.slug.localeCompare(b.bot.slug));
    const fallback = botBySlug.get('dreambot') || ranked[0]?.bot;
    const continuation = !preferred && (ranked[0]?.score || 0) < 20 ? botBySlug.get(activeSlug) : undefined;
    const selected = preferred || continuation || ranked[0]?.bot || fallback;
    const matched = selected ? capabilityMatches(selected, objective).slice(0, 5).map((item) => item.capability) : [];
    return {
      selected,
      matchedCapabilities: matched,
      coverage: index.summary,
      topScore: ranked[0]?.score || 0,
      modelPlan: localModelPlan(),
      execution: { status: 'sandbox_task_packet_ready' },
      discovery: localDiscovery(objective, ranked[0]?.score || 0),
    };
  }

  function localDiscovery(objective, topScore) {
    const uncertain = topScore < 20 || /\b(not sure|do not know|don't know|figure out|where do i start|anything)\b/i.test(objective);
    const normalized = objective.toLowerCase();
    const role = normalized.match(/invest|investment|stock|portfolio|financial advisor|retirement|loan|credit|tax|accountant/)
      ? { id: 'financial education assistant', boundary: 'I can explain, calculate, organize, draft, and prepare questions. Regulated advice and transactions still require the appropriate licensed person or institution.' }
      : normalized.match(/medical|diagnose|symptom|medicine|health|therapy|doctor|nurse|psychiatrist|psychologist/)
        ? { id: 'health information assistant', boundary: 'I can explain general information, organize records, draft questions, and help prepare for care. I do not diagnose, prescribe, claim a clinical role, or replace a qualified clinician.' }
        : normalized.match(/legal advice|lawsuit|court|contract|patent|trademark|immigration|lawyer|attorney/)
          ? { id: 'legal information assistant', boundary: 'I can explain general information, organize evidence, compare official sources, and prepare drafts and questions. I do not claim to be a lawyer, represent anyone, or replace qualified legal review.' }
          : { id: 'task partner', boundary: 'I can teach, plan, draft, test, and coordinate. Live account changes, purchases, filings, messages, or publications require a configured adapter and exact approval.' };
    return {
      needsQuestion: uncertain,
      question: 'What would a successful result let you do, even if you do not know the steps yet?',
      role,
      boundaryPreferences,
    };
  }

  async function routePrompt(objective) {
    const fallback = localRoute(objective);
    const staticPreview = location.hostname.endsWith('github.io') || location.hostname.endsWith('vercel.app');
    if (!location.protocol.startsWith('http') || staticPreview) return fallback;
    try {
      const response = await fetch('/api/buddy/route-capability', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          objective,
          preferredBotSlug: ownerSelectedSpecialist ? activeSlug : (fallback.topScore < 20 ? activeSlug || undefined : undefined),
          requestedCapabilities: [],
          liveActionRequested: false,
          modelMode,
          modelConnectorId: modelMode === 'premium' ? premiumProvider.value : 'buddy_native',
          selectedModelId: modelMode === 'premium' ? premiumModelId.value.trim() || undefined : undefined,
          approvePaidModelForThisRequest: modelMode === 'premium' && premiumApproval.checked,
        }),
      });
      if (!response.ok) return fallback;
      const result = await response.json();
      return {
        ...result,
        discovery: fallback.discovery,
        selected: {
          slug: result.selected.slug,
          name: result.selected.display_name,
          division: result.selected.division,
          category: result.selected.category,
          emoji: botBySlug.get(result.selected.slug)?.emoji || 'B',
        },
      };
    } catch (_error) {
      return fallback;
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

  function responseLead(taskMode) {
    const leads = {
      Build: 'Absolutely. I will turn that into a bounded build and start with the smallest working version.',
      Fix: 'Got it. I will reproduce the problem, isolate the cause, and keep each repair reversible.',
      Create: 'I understand the direction. I will shape it into a clear creative brief, prototype, and review loop.',
      Plan: 'I can help with that. I will organize the decisions, costs, risks, evidence, and next actions.',
      Discover: 'You do not need to know the steps. I will help define the result, teach unfamiliar parts, and begin with a safe practice task.',
    };
    return leads[taskMode] || leads.Build;
  }

  function planSteps(taskMode) {
    const steps = {
      Build: ['Confirm the result and acceptance checks.', 'Create the smallest testable version.', 'Run sandbox checks and show the evidence.'],
      Fix: ['Reproduce the failure.', 'Repair the smallest responsible area.', 'Rerun the affected checks and keep rollback ready.'],
      Create: ['Set the audience, rights, and creative goal.', 'Build a reviewable draft or prototype.', 'Test quality, safety, and export requirements.'],
      Plan: ['Clarify the decision and constraints.', 'Compare practical routes, costs, and risks.', 'Prepare an approval-ready next action.'],
      Discover: ['Describe what success should feel or look like.', 'Map the missing knowledge, tools, specialists, permissions, and costs.', 'Practice each unfamiliar step in a sandbox before doing anything live.'],
    };
    return steps[taskMode] || steps.Build;
  }

  function runCertification(selected, output, button) {
    const certification = certifications.bots?.[selected.slug];
    button.disabled = true;
    if (!certification) {
      output.textContent = 'No generated certification was found for this specialist. Regenerate the fleet test report before using it live.';
      return;
    }
    const passed = Number(certification.capabilityTestsPassed || 0);
    const total = Number(certification.declaredCapabilityCount || 0);
    const failed = Number(certification.capabilityTestsFailed || 0);
    output.textContent = failed === 0
      ? `${selected.name} passed ${passed.toLocaleString()} of ${total.toLocaleString()} repository-controlled sandbox capability contracts. External provider behavior still needs configured adapters and provider sandboxes.`
      : `${selected.name} has ${failed.toLocaleString()} failed sandbox capability contracts out of ${total.toLocaleString()}. Keep live actions off until repaired.`;
    button.textContent = failed === 0 ? 'Capability tests passed' : 'Review failed tests';
  }

  function addBuddyMessage(result) {
    const selected = result.selected || { slug: 'dreambot', name: 'DreamBot', division: 'CommandCore', emoji: 'B' };
    const row = document.createElement('article');
    row.className = 'buddy-chat-row assistant';
    const avatar = document.createElement('img');
    avatar.className = 'buddy-chat-avatar';
    avatar.src = 'assets/images/buddy-icon-192.png';
    avatar.alt = 'Buddy';
    const bubble = document.createElement('div');
    bubble.className = 'buddy-chat-bubble';

    const heading = document.createElement('div');
    heading.className = 'buddy-specialist-heading';
    const specialistEmoji = document.createElement('span');
    specialistEmoji.setAttribute('aria-hidden', 'true');
    specialistEmoji.textContent = selected.emoji || 'B';
    const specialistName = document.createElement('strong');
    specialistName.textContent = `Buddy with ${selected.name}`;
    heading.append(specialistEmoji, specialistName);

    const lead = document.createElement('p');
    lead.textContent = responseLead(mode);
    const route = document.createElement('p');
    route.textContent = `I matched this to ${selected.name} in ${selected.division}. I will prepare and test the work first, then pause before any outside account, purchase, signup, message, publication, or data change.`;
    bubble.append(heading, lead, route);

    const planList = document.createElement('ol');
    planList.className = 'buddy-plan-list';
    planSteps(mode).forEach((step) => {
      const item = document.createElement('li');
      item.textContent = step;
      planList.append(item);
    });
    bubble.append(planList);

    if (result.discovery?.needsQuestion || mode === 'Discover') {
      const discovery = document.createElement('div');
      discovery.className = 'buddy-discovery-question';
      const label = document.createElement('strong');
      label.textContent = 'One question to aim us';
      const question = document.createElement('p');
      question.textContent = result.discovery?.question || 'What would a successful result let you do?';
      discovery.append(label, question);
      bubble.append(discovery);
    }
    if (result.discovery?.role?.boundary) {
      const boundary = document.createElement('p');
      boundary.className = 'buddy-role-boundary';
      boundary.textContent = `${result.discovery.role.id}: ${result.discovery.role.boundary}`;
      bubble.append(boundary);
    }
    if (result.discovery?.boundaryPreferences) {
      const preferences = result.discovery.boundaryPreferences;
      const preferenceNote = document.createElement('p');
      preferenceNote.className = 'buddy-role-boundary';
      preferenceNote.textContent = `Your settings: ${preferences.communicationStyle.replaceAll('_', ' ')} style, ${preferences.riskDisclosure} risk detail, ${preferences.moneyActionMode.replaceAll('_', ' ')} for money actions. Exact approval remains required for every outside action.`;
      bubble.append(preferenceNote);
    }

    if (result.matchedCapabilities?.length) {
      const list = document.createElement('div');
      list.className = 'buddy-capability-list';
      result.matchedCapabilities.slice(0, 4).forEach((capability) => {
        const chip = document.createElement('span');
        chip.textContent = capability;
        list.append(chip);
      });
      bubble.append(list);
    }

    const modelNote = document.createElement('div');
    modelNote.className = 'buddy-model-note';
    const modelPlan = result.modelPlan || localModelPlan();
    if (modelPlan.mode === 'free') {
      modelNote.textContent = 'Free mode: Buddy Native prepared this route without calling a paid model.';
    } else if (modelPlan.status === 'paid_approval_required') {
      modelNote.textContent = 'Premium is selected, but no provider call is allowed until you approve this one message.';
    } else if (modelPlan.status === 'configuration_required') {
      modelNote.textContent = `${modelPlan.connector?.label || 'The premium provider'} needs a backend connection. Buddy used the free local route instead and did not charge anything.`;
    } else {
      modelNote.textContent = `${modelPlan.connector?.label || 'Premium'} is approved for this message. Provider use still runs only through the authenticated backend adapter.`;
    }
    bubble.append(modelNote);

    const testResult = document.createElement('div');
    testResult.className = 'buddy-test-result';
    testResult.hidden = true;
    const actions = document.createElement('div');
    actions.className = 'buddy-response-actions';
    const testButton = document.createElement('button');
    testButton.type = 'button';
    testButton.textContent = 'Test capabilities';
    testButton.addEventListener('click', () => {
      testResult.hidden = false;
      runCertification(selected, testResult, testButton);
    });
    const prospectus = document.createElement('a');
    prospectus.href = `bots.html?prospectus=${encodeURIComponent(selected.slug)}`;
    prospectus.textContent = 'View specialist';
    const calculator = document.createElement('a');
    calculator.href = `calculator.html?bot=${encodeURIComponent(selected.slug)}`;
    calculator.textContent = 'ROI calculator';
    const connections = document.createElement('a');
    connections.href = 'connections.html';
    connections.textContent = 'Connect an app';
    const launch = document.createElement('a');
    launch.href = 'install.html';
    launch.textContent = 'Launch or domain';
    const benchmark = document.createElement('a');
    benchmark.href = 'models.html';
    benchmark.textContent = 'Compare models';
    const sourceLab = document.createElement('a');
    sourceLab.href = 'open-model-lab.html';
    sourceLab.textContent = 'Open-source lab';
    const dataControl = document.createElement('a');
    dataControl.href = 'data-control.html';
    dataControl.textContent = 'Data & memory';
    const repository = document.createElement('a');
    repository.href = setupCatalog.repository.url || 'https://github.com/DreamCo-Technologies/Dreamcobots';
    repository.target = '_blank';
    repository.rel = 'noopener';
    repository.textContent = 'GitHub repository';
    const githubActions = document.createElement('a');
    githubActions.href = setupCatalog.repository.actions || 'https://github.com/DreamCo-Technologies/Dreamcobots/actions';
    githubActions.target = '_blank';
    githubActions.rel = 'noopener';
    githubActions.textContent = 'GitHub Actions';
    actions.append(testButton, prospectus, calculator, connections, launch, benchmark, sourceLab, dataControl, repository, githubActions);
    bubble.append(testResult, actions);
    row.append(avatar, bubble);
    thread.append(row);
  }

  async function send() {
    const objective = input.value.trim();
    if (!objective) return;
    welcome.hidden = true;
    addUserMessage(objective);
    input.value = '';
    sendButton.disabled = true;
    sendButton.textContent = 'Routing...';
    routeStatus.textContent = `Checking ${Number(index.summary.profiles || 0).toLocaleString()} specialists...`;
    const result = await routePrompt(objective);
    addBuddyMessage(result);
    const selectedName = result.selected?.name || result.selected?.display_name || 'the best available specialist';
    activeSlug = result.selected?.slug || activeSlug;
    routeStatus.textContent = `Routed through ${selectedName} in ${modelMode === 'free' ? 'free' : 'premium-requested'} mode.`;
    sendButton.disabled = false;
    sendButton.textContent = 'Send';
    premiumApproval.checked = false;
    input.focus();
    thread.lastElementChild?.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  }

  function setModelMode(nextMode) {
    modelMode = nextMode;
    const free = nextMode === 'free';
    freeButton.classList.toggle('active', free);
    premiumButton.classList.toggle('active', !free);
    freeButton.setAttribute('aria-pressed', String(free));
    premiumButton.setAttribute('aria-pressed', String(!free));
    premiumPanel.hidden = free;
    if (free) premiumApproval.checked = false;
    routeStatus.textContent = free
      ? 'Free mode is on. Buddy will not call a paid model.'
      : 'Premium mode is ready. Approve each message separately.';
    input.focus();
  }

  function specialistSearchScore(bot, query) {
    if (!query) return 1;
    const normalized = normalize(query);
    const haystack = normalize(`${bot.name} ${bot.slug} ${bot.division} ${bot.category} ${bot.mission} ${bot.capabilities.join(' ')}`);
    if (haystack.includes(normalized)) return 100;
    return [...tokens(query)].filter((token) => haystack.includes(token)).length * 10;
  }

  function renderSpecialists() {
    const query = specialistSearch.value.trim();
    const matches = bots.map((bot) => ({ bot, score: specialistSearchScore(bot, query) }))
      .filter((item) => item.score > 0)
      .sort((a, b) => b.score - a.score || a.bot.name.localeCompare(b.bot.name))
      .slice(0, 30);
    specialistResults.replaceChildren(...matches.map(({ bot }) => {
      const button = document.createElement('button');
      button.type = 'button';
      button.className = 'buddy-specialist-result';
      const name = document.createElement('strong');
      name.textContent = `${bot.emoji} ${bot.name}`;
      const detail = document.createElement('small');
      detail.textContent = `${bot.division} / ${bot.category} / ${bot.capabilities.slice(0, 3).join(' / ')}`;
      const certification = certifications.bots?.[bot.slug];
      const status = document.createElement('span');
      status.textContent = certification?.status === 'sandbox_certified'
        ? `${certification.capabilityTestsPassed}/${certification.declaredCapabilityCount} passed`
        : 'Needs test';
      button.append(name, detail, status);
      button.addEventListener('click', () => {
        activeSlug = bot.slug;
        ownerSelectedSpecialist = true;
        input.value = `Help me use ${bot.name} for `;
        specialistDialog.close();
        routeStatus.textContent = `${bot.name} selected. Finish your request.`;
        input.focus();
        input.setSelectionRange(input.value.length, input.value.length);
      });
      return button;
    }));
    specialistSummary.textContent = `${matches.length.toLocaleString()} shown from ${bots.length.toLocaleString()} specialists. Select one, then tell Buddy the outcome you want.`;
  }

  function setLocalStatus(label, detail, connected) {
    localStatus.textContent = label;
    localStatusDetail.textContent = detail;
    localStatusDot.classList.toggle('connected', connected);
  }

  function renderLocalAudit(events) {
    localAudit.replaceChildren();
    if (!events?.length) {
      localAudit.textContent = 'No local actions in this session.';
      return;
    }
    events.slice(0, 12).forEach((event) => {
      const row = document.createElement('div');
      const copy = document.createElement('span');
      copy.textContent = `${event.action.replaceAll('_', ' ')} · ${event.target}`;
      const time = document.createElement('time');
      time.dateTime = event.at;
      time.textContent = new Date(event.at).toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' });
      row.append(copy, time);
      localAudit.append(row);
    });
  }

  async function localRequest(path, body) {
    if (!localToken) throw new Error('Start the private local bridge from the repository first.');
    const response = await fetch(path, {
      method: body ? 'POST' : 'GET',
      headers: {
        Authorization: `Bearer ${localToken}`,
        ...(body ? { 'Content-Type': 'application/json' } : {}),
      },
      ...(body ? { body: JSON.stringify(body) } : {}),
    });
    const result = await response.json().catch(() => ({ error: 'The local bridge returned an unreadable response.' }));
    if (!response.ok) throw new Error(result.error || 'The local bridge rejected the action.');
    return result;
  }

  async function checkLocalBridge() {
    if (!localToken) {
      setLocalStatus('Not connected', 'Run the command below from this repository to start a private session.', false);
      return;
    }
    try {
      const result = await localRequest('/api/local/health');
      localBridgePaused = Boolean(result.paused);
      localPause.textContent = localBridgePaused ? 'Resume' : 'Pause';
      setLocalStatus(localBridgePaused ? 'Connected and paused' : 'Connected to this laptop', 'Loopback only, short-lived token, memory-only action log.', true);
      renderLocalAudit(result.audit);
    } catch (error) {
      setLocalStatus('Local bridge unavailable', error.message, false);
    }
  }

  async function runLocalSearch() {
    const query = document.getElementById('local-query').value.trim();
    const approval = document.getElementById('local-approval');
    if (!query) {
      setLocalStatus('Search needs a question', 'Describe what Buddy should search for.', Boolean(localToken));
      return;
    }
    if (!approval.checked) {
      setLocalStatus('Approval required', 'Approve this one visible browser search.', Boolean(localToken));
      return;
    }
    try {
      const result = await localRequest('/api/local/browser/search', {
        query,
        browser: document.getElementById('local-browser').value,
        engine: document.getElementById('local-engine').value,
        approved: true,
      });
      approval.checked = false;
      setLocalStatus('Search opened', `${result.engine} opened in ${result.browser === 'system' ? 'the system browser' : result.browser}.`, true);
      await checkLocalBridge();
    } catch (error) {
      setLocalStatus('Search was not opened', error.message, false);
    }
  }

  async function openLocalApp() {
    const app = document.getElementById('local-app');
    const label = app.options[app.selectedIndex]?.textContent || 'this app';
    if (!window.confirm(`Open ${label} once? This does not grant Buddy control of the app.`)) return;
    try {
      await localRequest('/api/local/apps/open', { app: app.value, approved: true });
      setLocalStatus(`${label} opened`, 'Buddy did not read, type, click, sign in, or submit anything.', true);
      await checkLocalBridge();
    } catch (error) {
      setLocalStatus(`${label} was not opened`, error.message, false);
    }
  }

  async function toggleLocalPause() {
    const nextPaused = !localBridgePaused;
    if (!window.confirm(`${nextPaused ? 'Pause' : 'Resume'} local Buddy actions?`)) return;
    try {
      const result = await localRequest('/api/local/pause', { paused: nextPaused, approved: true });
      localBridgePaused = result.paused;
      await checkLocalBridge();
    } catch (error) {
      setLocalStatus('Pause control failed safely', error.message, false);
    }
  }

  function localDateTimeValue(date) {
    const local = new Date(date.getTime() - date.getTimezoneOffset() * 60_000);
    return local.toISOString().slice(0, 16);
  }

  function loadScheduledTasks() {
    try {
      const rows = JSON.parse(localStorage.getItem(scheduleStorageKey) || '[]');
      return Array.isArray(rows) ? rows.filter((row) => row && typeof row.id === 'string') : [];
    } catch (_error) {
      return [];
    }
  }

  function saveScheduledTasks(tasks) {
    localStorage.setItem(scheduleStorageKey, JSON.stringify(tasks.slice(-100)));
  }

  function selectedOptionLabels() {
    if (!activeLauncher) return [];
    return activeLauncher.options
      .filter((option) => selectedSetupOptions.has(option.id))
      .map((option) => option.label);
  }

  function updateSetupCount() {
    const count = selectedSetupOptions.size;
    setupCount.textContent = `${count} of 30 selected`;
    setupStatus.textContent = count
      ? `${count} setup choice${count === 1 ? '' : 's'} ready. No outside action is approved.`
      : 'Choose one or more setup options.';
  }

  function renderSetupOptions() {
    setupOptions.replaceChildren();
    if (!activeLauncher) return;
    activeLauncher.options.forEach((option) => {
      const button = document.createElement('button');
      button.type = 'button';
      button.className = 'buddy-setup-option';
      button.textContent = option.label;
      button.dataset.optionId = option.id;
      button.setAttribute('aria-pressed', String(selectedSetupOptions.has(option.id)));
      button.addEventListener('click', () => {
        if (selectedSetupOptions.has(option.id)) selectedSetupOptions.delete(option.id);
        else selectedSetupOptions.add(option.id);
        button.classList.toggle('selected', selectedSetupOptions.has(option.id));
        button.setAttribute('aria-pressed', String(selectedSetupOptions.has(option.id)));
        updateSetupCount();
      });
      setupOptions.append(button);
    });
    updateSetupCount();
  }

  function setExecutionMode(nextMode) {
    executionMode = nextMode;
    document.querySelectorAll('[data-execution-mode]').forEach((button) => {
      const selected = button.dataset.executionMode === nextMode;
      button.classList.toggle('active', selected);
      button.setAttribute('aria-pressed', String(selected));
    });
    scheduleControls.hidden = nextMode !== 'schedule';
    setupRun.textContent = nextMode === 'schedule' ? 'Save timed task' : 'Call specialist now';
  }

  function updateScheduleFields() {
    const cadence = document.getElementById('schedule-cadence').value;
    const endMode = document.getElementById('schedule-end-mode');
    const once = cadence === 'once';
    const returningFromOneTime = endMode.disabled;
    document.getElementById('schedule-custom-label').hidden = cadence !== 'custom';
    endMode.disabled = once;
    if (once) endMode.value = 'after_runs';
    else if (returningFromOneTime) endMode.value = 'until_stopped';
    document.getElementById('schedule-end-date-label').hidden = once || endMode.value !== 'on_date';
    document.getElementById('schedule-run-count-label').hidden = once || endMode.value !== 'after_runs';
  }

  function openSetup(launcherId) {
    const launcher = launcherById.get(launcherId);
    if (!launcher) {
      routeStatus.textContent = 'That setup catalog entry is unavailable.';
      return;
    }
    activeLauncher = launcher;
    selectedSetupOptions = new Set();
    setupEyebrow.textContent = `${launcher.options.length} guided setup choices`;
    setupTitle.textContent = launcher.label;
    setupWorkspace.href = launcher.workspace;
    setupWorkspace.textContent = 'Open full workspace';
    document.getElementById('schedule-start').value = localDateTimeValue(new Date(Date.now() + 5 * 60_000));
    document.getElementById('schedule-end-date').value = localDateTimeValue(new Date(Date.now() + 30 * 86_400_000)).slice(0, 10);
    document.getElementById('schedule-cadence').value = 'once';
    document.getElementById('schedule-end-mode').value = 'after_runs';
    document.getElementById('schedule-run-count').value = '10';
    document.getElementById('schedule-interval').value = '60';
    document.getElementById('schedule-unit').value = 'minutes';
    document.getElementById('schedule-run-limit').value = '3600';
    setExecutionMode('now');
    updateScheduleFields();
    renderSetupOptions();
    setupDialog.showModal();
    setupOptions.querySelector('button')?.focus();
  }

  function customIntervalSeconds() {
    const amount = Number(document.getElementById('schedule-interval').value);
    const unit = document.getElementById('schedule-unit').value;
    const multiplier = unit === 'days' ? 86_400 : unit === 'hours' ? 3_600 : 60;
    return Math.round(amount * multiplier);
  }

  function cadenceLabel(schedule) {
    const labels = {
      once: 'one time', hourly: 'every hour', daily: 'every day', weekdays: 'every weekday',
      weekly: 'every week', monthly: 'every month', custom: `every ${schedule.intervalSeconds / 60} minutes`,
    };
    return labels[schedule.cadence] || schedule.cadence;
  }

  function readScheduleDefinition() {
    const start = new Date(document.getElementById('schedule-start').value);
    if (Number.isNaN(start.getTime()) || start.getTime() < Date.now() - 60_000) {
      throw new Error('Choose a valid first run time that is not in the past.');
    }
    const cadence = document.getElementById('schedule-cadence').value;
    const intervalSeconds = cadence === 'custom' ? customIntervalSeconds() : null;
    if (cadence === 'custom' && (!Number.isFinite(intervalSeconds) || intervalSeconds < 900)) {
      throw new Error('Custom recurring tasks must wait at least 15 minutes between runs.');
    }
    const requestedEndMode = document.getElementById('schedule-end-mode').value;
    const endMode = cadence === 'once' ? 'after_runs' : requestedEndMode;
    const endDateValue = document.getElementById('schedule-end-date').value;
    const endAt = endMode === 'on_date' && endDateValue ? new Date(`${endDateValue}T23:59:59`).toISOString() : null;
    const maxRuns = cadence === 'once' ? 1 : endMode === 'after_runs' ? Number(document.getElementById('schedule-run-count').value) : null;
    if (endMode === 'after_runs' && (!Number.isInteger(maxRuns) || maxRuns < 1 || maxRuns > 10_000)) {
      throw new Error('Maximum runs must be between 1 and 10,000.');
    }
    if (endMode === 'on_date' && (!endAt || new Date(endAt).getTime() <= start.getTime())) {
      throw new Error('The end date must be after the first run.');
    }
    return {
      cadence,
      intervalSeconds,
      endMode,
      endAt,
      maxRuns,
      maxRuntimeSeconds: Number(document.getElementById('schedule-run-limit').value),
    };
  }

  function nextRunAt(task, from = new Date()) {
    const next = new Date(from);
    if (task.schedule.cadence === 'once') return null;
    if (task.schedule.cadence === 'hourly') next.setHours(next.getHours() + 1);
    if (task.schedule.cadence === 'daily') next.setDate(next.getDate() + 1);
    if (task.schedule.cadence === 'weekly') next.setDate(next.getDate() + 7);
    if (task.schedule.cadence === 'monthly') next.setMonth(next.getMonth() + 1);
    if (task.schedule.cadence === 'custom') next.setSeconds(next.getSeconds() + task.schedule.intervalSeconds);
    if (task.schedule.cadence === 'weekdays') {
      next.setDate(next.getDate() + 1);
      while (next.getDay() === 0 || next.getDay() === 6) next.setDate(next.getDate() + 1);
    }
    return next.toISOString();
  }

  function taskPrompt(launcher, options, schedule = null) {
    const choices = options.length ? options.map((option) => `- ${option}`).join('\n') : '- Start with Buddy\'s recommended setup.';
    const timing = schedule
      ? `\nTiming: ${cadenceLabel(schedule)} beginning ${new Date(document.getElementById('schedule-start').value).toLocaleString()}. ${schedule.endMode === 'until_stopped' ? 'Continue until I pause or cancel it.' : schedule.endMode === 'after_runs' ? `Stop after ${schedule.maxRuns} runs.` : `Stop after ${new Date(schedule.endAt).toLocaleDateString()}.`} Each run may use at most ${schedule.maxRuntimeSeconds / 3600} hour(s).`
      : '';
    return `${launcher.prompt}\n\nRequested setup:\n${choices}${timing}\n\nUse repository DreamCo-Technologies/Dreamcobots as the code source. Work in a sandbox first. Do not spend money, contact anyone, publish, sign, submit, change an account, or perform another external write without exact approval for that one action.`;
  }

  function newTaskId() {
    return globalThis.crypto?.randomUUID ? `buddy-task-${globalThis.crypto.randomUUID()}` : `buddy-task-${Date.now()}-${Math.random().toString(16).slice(2)}`;
  }

  function formatTaskTime(value) {
    if (!value) return 'No next run';
    const date = new Date(value);
    return Number.isNaN(date.getTime()) ? 'Invalid time' : date.toLocaleString();
  }

  function renderSchedules() {
    const tasks = loadScheduledTasks().sort((a, b) => String(a.nextRunAt || '').localeCompare(String(b.nextRunAt || '')));
    const active = tasks.filter((task) => task.status === 'active').length;
    scheduleSummary.textContent = tasks.length
      ? `${active} active and ${tasks.length - active} paused or completed on this device`
      : 'No schedules on this device';
    scheduleList.replaceChildren();
    if (!tasks.length) {
      const empty = document.createElement('p');
      empty.className = 'buddy-schedule-empty';
      empty.textContent = 'Use any Buddy starter and choose Schedule to create a timed task.';
      scheduleList.append(empty);
      return;
    }
    tasks.forEach((task) => {
      const row = document.createElement('article');
      row.className = 'buddy-schedule-item';
      const title = document.createElement('strong');
      title.textContent = task.label;
      const detail = document.createElement('p');
      detail.textContent = `${cadenceLabel(task.schedule)} · ${task.status} · ${task.runCount} run${task.runCount === 1 ? '' : 's'}`;
      const next = document.createElement('small');
      next.textContent = task.status === 'active' ? `Next: ${formatTaskTime(task.nextRunAt)}` : task.status === 'completed' ? 'Schedule completed' : 'Paused by owner';
      detail.append(next);
      const actions = document.createElement('div');
      actions.className = 'buddy-schedule-actions';
      const run = document.createElement('button');
      run.type = 'button';
      run.textContent = 'Run now';
      run.disabled = task.status === 'completed';
      run.addEventListener('click', () => executeScheduledTask(task.id, true));
      const pause = document.createElement('button');
      pause.type = 'button';
      pause.textContent = task.status === 'paused' ? 'Resume' : 'Pause';
      pause.disabled = task.status === 'completed';
      pause.addEventListener('click', () => {
        const current = loadScheduledTasks();
        const selected = current.find((item) => item.id === task.id);
        if (!selected) return;
        selected.status = selected.status === 'paused' ? 'active' : 'paused';
        if (selected.status === 'active' && new Date(selected.nextRunAt).getTime() < Date.now()) {
          selected.nextRunAt = new Date(Date.now() + 60_000).toISOString();
        }
        saveScheduledTasks(current);
        renderSchedules();
      });
      const remove = document.createElement('button');
      remove.type = 'button';
      remove.textContent = 'Delete';
      remove.addEventListener('click', () => {
        if (!window.confirm(`Delete the ${task.label} schedule from this device?`)) return;
        saveScheduledTasks(loadScheduledTasks().filter((item) => item.id !== task.id));
        renderSchedules();
      });
      actions.append(run, pause, remove);
      row.append(title, detail, actions);
      scheduleList.append(row);
    });
  }

  async function executeScheduledTask(taskId, manual = false) {
    if (scheduledTaskRunning) return;
    const tasks = loadScheduledTasks();
    const task = tasks.find((item) => item.id === taskId);
    if (!task || (!manual && task.status !== 'active') || task.status === 'completed') return;
    scheduledTaskRunning = true;
    try {
      if (scheduleDialog.open) scheduleDialog.close();
      welcome.hidden = true;
      addUserMessage(`[Timed task: ${task.label}]\n${task.prompt}`);
      routeStatus.textContent = `Calling the scheduled ${task.label} specialist in the local sandbox...`;
      const result = await routePrompt(task.prompt);
      addBuddyMessage(result);
      activeSlug = result.selected?.slug || activeSlug;
      task.runCount += 1;
      task.lastRunAt = new Date().toISOString();
      const proposedNext = nextRunAt(task, new Date());
      const reachedRuns = task.schedule.endMode === 'after_runs' && task.runCount >= task.schedule.maxRuns;
      const reachedDate = task.schedule.endMode === 'on_date' && proposedNext && new Date(proposedNext).getTime() > new Date(task.schedule.endAt).getTime();
      if (!proposedNext || reachedRuns || reachedDate) {
        task.status = 'completed';
        task.nextRunAt = null;
      } else {
        task.status = 'active';
        task.nextRunAt = proposedNext;
      }
      saveScheduledTasks(tasks);
      routeStatus.textContent = task.status === 'completed'
        ? `${task.label} completed its schedule.`
        : `${task.label} ran safely. Next run: ${formatTaskTime(task.nextRunAt)}.`;
      renderSchedules();
      thread.lastElementChild?.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    } finally {
      scheduledTaskRunning = false;
    }
  }

  async function checkDueSchedules() {
    if (scheduledTaskRunning || document.hidden) return;
    const due = loadScheduledTasks().find((task) => task.status === 'active' && task.nextRunAt && new Date(task.nextRunAt).getTime() <= Date.now());
    if (due) await executeScheduledTask(due.id);
  }

  async function runSetup() {
    if (!activeLauncher) return;
    const choices = selectedOptionLabels();
    if (!choices.length) {
      setupStatus.textContent = 'Choose at least one of the 30 setup options.';
      setupOptions.querySelector('button')?.focus();
      return;
    }
    if (executionMode === 'now') {
      input.value = taskPrompt(activeLauncher, choices);
      setupDialog.close();
      await send();
      return;
    }
    try {
      const schedule = readScheduleDefinition();
      const tasks = loadScheduledTasks();
      if (tasks.length >= 100) throw new Error('This device already has 100 task plans. Delete an old plan before adding another.');
      const task = {
        schema: 'dreamco.buddy_local_schedule.v2',
        id: newTaskId(),
        launcherId: activeLauncher.id,
        label: activeLauncher.label,
        prompt: taskPrompt(activeLauncher, choices, schedule),
        selectedOptions: choices,
        schedule,
        status: 'active',
        runCount: 0,
        nextRunAt: new Date(document.getElementById('schedule-start').value).toISOString(),
        lastRunAt: null,
        createdAt: new Date().toISOString(),
        executionBoundary: 'local_sandbox_routing_only_external_actions_require_fresh_approval',
      };
      tasks.push(task);
      saveScheduledTasks(tasks);
      setupDialog.close();
      renderSchedules();
      scheduleDialog.showModal();
      routeStatus.textContent = schedule.endMode === 'until_stopped'
        ? `${activeLauncher.label} will recur until you pause or cancel it while an approved runner is available.`
        : `${activeLauncher.label} schedule saved on this device.`;
    } catch (error) {
      setupStatus.textContent = error.message;
    }
  }

  document.querySelectorAll('[data-buddy-mode]').forEach((button) => {
    button.addEventListener('click', () => {
      document.querySelectorAll('[data-buddy-mode]').forEach((item) => {
        const selected = item === button;
        item.classList.toggle('active', selected);
        item.setAttribute('aria-selected', String(selected));
      });
      mode = button.dataset.buddyMode || 'Build';
      input.focus();
    });
  });

  document.querySelectorAll('[data-buddy-prompt]').forEach((button) => {
    button.addEventListener('click', () => {
      input.value = button.dataset.buddyPrompt || '';
      input.focus();
    });
  });

  document.querySelectorAll('[data-buddy-launcher]').forEach((button) => {
    button.addEventListener('click', () => openSetup(button.dataset.buddyLauncher));
  });
  document.querySelectorAll('[data-execution-mode]').forEach((button) => {
    button.addEventListener('click', () => setExecutionMode(button.dataset.executionMode));
  });
  document.getElementById('schedule-cadence').addEventListener('change', updateScheduleFields);
  document.getElementById('schedule-end-mode').addEventListener('change', updateScheduleFields);
  setupRun.addEventListener('click', runSetup);
  setupClose.addEventListener('click', () => setupDialog.close());
  setupDialog.addEventListener('click', (event) => {
    if (event.target === setupDialog) setupDialog.close();
  });
  scheduleOpen.addEventListener('click', () => {
    renderSchedules();
    scheduleDialog.showModal();
  });
  scheduleClose.addEventListener('click', () => scheduleDialog.close());
  scheduleDialog.addEventListener('click', (event) => {
    if (event.target === scheduleDialog) scheduleDialog.close();
  });

  modelPolicy.connectors.filter((connector) => connector.mode === 'premium').forEach((connector) => {
    const option = document.createElement('option');
    option.value = connector.id;
    option.textContent = connector.label;
    premiumProvider.append(option);
  });

  freeButton.addEventListener('click', () => setModelMode('free'));
  premiumButton.addEventListener('click', () => setModelMode('premium'));
  premiumBack.addEventListener('click', () => setModelMode('free'));
  specialistOpen.addEventListener('click', () => {
    renderSpecialists();
    specialistDialog.showModal();
    specialistSearch.focus();
  });
  specialistClose.addEventListener('click', () => specialistDialog.close());
  specialistSearch.addEventListener('input', renderSpecialists);
  specialistDialog.addEventListener('click', (event) => {
    if (event.target === specialistDialog) specialistDialog.close();
  });
  localOpen.addEventListener('click', () => {
    localDialog.showModal();
    checkLocalBridge();
  });
  document.querySelectorAll('[data-local-search-open]').forEach((button) => button.addEventListener('click', () => {
    localDialog.showModal();
    checkLocalBridge();
    document.getElementById('local-query').focus();
  }));
  localClose.addEventListener('click', () => localDialog.close());
  localDialog.addEventListener('click', (event) => {
    if (event.target === localDialog) localDialog.close();
  });
  document.getElementById('local-search').addEventListener('click', runLocalSearch);
  document.getElementById('local-app-open').addEventListener('click', openLocalApp);
  localPause.addEventListener('click', toggleLocalPause);
  boundaryOpen.addEventListener('click', () => {
    document.getElementById('boundary-support').value = boundaryPreferences.professionalSupport;
    document.getElementById('boundary-risk').value = boundaryPreferences.riskDisclosure;
    document.getElementById('boundary-approval').value = boundaryPreferences.approvalMode;
    document.getElementById('boundary-money').value = boundaryPreferences.moneyActionMode;
    document.getElementById('boundary-communication').value = boundaryPreferences.communicationStyle;
    document.getElementById('boundary-depth').value = boundaryPreferences.guidanceDepth;
    document.getElementById('boundary-tone').checked = boundaryPreferences.voiceToneAdaptation;
    boundaryDialog.showModal();
  });
  boundaryClose.addEventListener('click', () => boundaryDialog.close());
  boundaryDialog.addEventListener('click', (event) => {
    if (event.target === boundaryDialog) boundaryDialog.close();
  });
  boundaryForm.addEventListener('submit', (event) => {
    event.preventDefault();
    boundaryPreferences = {
      professionalSupport: document.getElementById('boundary-support').value,
      riskDisclosure: document.getElementById('boundary-risk').value,
      approvalMode: document.getElementById('boundary-approval').value,
      moneyActionMode: document.getElementById('boundary-money').value,
      communicationStyle: document.getElementById('boundary-communication').value,
      guidanceDepth: document.getElementById('boundary-depth').value,
      voiceToneAdaptation: document.getElementById('boundary-tone').checked,
    };
    localStorage.setItem('buddy-boundary-preferences-v1', JSON.stringify(boundaryPreferences));
    document.getElementById('boundary-status').textContent = 'Saved. Hard professional and transaction boundaries remain on.';
  });
  sendButton.addEventListener('click', send);
  input.addEventListener('keydown', (event) => {
    if (event.key === 'Enter' && (event.metaKey || event.ctrlKey)) {
      event.preventDefault();
      send();
    }
  });

  const prompt = params.get('prompt');
  if (prompt) input.value = prompt;
  if (params.get('preferences') === '1') boundaryOpen.click();
  if (index.summary.profiles) {
    routeStatus.textContent = `Ready to route across ${Number(index.summary.profiles).toLocaleString()} verified specialists in free mode.`;
  }
  renderSchedules();
  window.setInterval(checkDueSchedules, 30_000);
  window.setTimeout(checkDueSchedules, 1_500);
  if ('serviceWorker' in navigator && location.protocol !== 'file:') {
    window.addEventListener('load', () => navigator.serviceWorker.register('service-worker.js', { scope: './' }).catch(() => {}));
  }
})();
