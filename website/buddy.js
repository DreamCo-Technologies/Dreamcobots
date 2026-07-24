(function () {
  'use strict';

  const index = window.BUDDY_ROUTING_INDEX || { summary: { profiles: 0, capabilities: 0 }, bots: [] };
  const modelPolicy = window.BUDDY_MODEL_ROUTER || { defaultMode: 'free', connectors: [] };
  const certifications = window.BUDDY_CAPABILITY_CERTIFICATIONS || { summary: {}, bots: {} };
  const bots = index.bots.map(unpack);
  const botBySlug = new Map(bots.map((bot) => [bot.slug, bot]));

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
  const params = new URLSearchParams(location.search);
  const preferredSlug = params.get('bot') || '';
  let activeSlug = preferredSlug;
  let ownerSelectedSpecialist = Boolean(preferredSlug);
  let mode = 'Build';
  let modelMode = modelPolicy.defaultMode || 'free';

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
    };
  }

  async function routePrompt(objective) {
    const fallback = localRoute(objective);
    if (!location.protocol.startsWith('http')) return fallback;
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
    };
    return leads[taskMode] || leads.Build;
  }

  function planSteps(taskMode) {
    const steps = {
      Build: ['Confirm the result and acceptance checks.', 'Create the smallest testable version.', 'Run sandbox checks and show the evidence.'],
      Fix: ['Reproduce the failure.', 'Repair the smallest responsible area.', 'Rerun the affected checks and keep rollback ready.'],
      Create: ['Set the audience, rights, and creative goal.', 'Build a reviewable draft or prototype.', 'Test quality, safety, and export requirements.'],
      Plan: ['Clarify the decision and constraints.', 'Compare practical routes, costs, and risks.', 'Prepare an approval-ready next action.'],
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
    actions.append(testButton, prospectus, calculator, connections, launch);
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
  sendButton.addEventListener('click', send);
  input.addEventListener('keydown', (event) => {
    if (event.key === 'Enter' && (event.metaKey || event.ctrlKey)) {
      event.preventDefault();
      send();
    }
  });

  const prompt = params.get('prompt');
  if (prompt) input.value = prompt;
  if (index.summary.profiles) {
    routeStatus.textContent = `Ready to route across ${Number(index.summary.profiles).toLocaleString()} verified specialists in free mode.`;
  }
  if ('serviceWorker' in navigator && location.protocol !== 'file:') {
    window.addEventListener('load', () => navigator.serviceWorker.register('service-worker.js', { scope: './' }).catch(() => {}));
  }
})();
