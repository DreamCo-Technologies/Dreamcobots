(function () {
  'use strict';

  const index = window.BUDDY_ROUTING_INDEX || { summary: { profiles: 0, capabilities: 0 }, bots: [] };
  const input = document.getElementById('buddy-input');
  const sendButton = document.getElementById('buddy-send');
  const thread = document.getElementById('buddy-thread');
  const welcome = document.getElementById('buddy-welcome');
  const routeStatus = document.getElementById('buddy-route-status');
  const params = new URLSearchParams(location.search);
  const preferredSlug = params.get('bot') || '';
  let activeSlug = preferredSlug;
  let mode = 'Build';

  const stopWords = new Set([
    'about', 'after', 'again', 'also', 'because', 'before', 'build', 'buddy', 'could', 'create',
    'from', 'have', 'help', 'into', 'make', 'need', 'please', 'should', 'that', 'their', 'then',
    'this', 'through', 'using', 'want', 'with', 'would', 'your',
  ]);
  const synonyms = {
    app: ['application', 'software', 'code'], application: ['app', 'software', 'code'],
    bug: ['debug', 'error', 'failure'], class: ['course', 'education', 'learning'],
    code: ['coding', 'software', 'development'], course: ['class', 'education', 'learning'],
    database: ['data', 'server', 'integration'], game: ['gaming', 'player', 'simulation'],
    invention: ['prototype', 'patent', 'design', 'research'], job: ['career', 'employment', 'hiring'],
    money: ['finance', 'income', 'revenue'], prototype: ['design', 'development', 'testing', 'simulation'],
    property: ['real', 'estate', 'commercial'], server: ['database', 'api', 'integration'],
    song: ['music', 'audio', 'production'], video: ['media', 'creative', 'production'],
    website: ['responsive', 'web', 'software'],
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

  function localRoute(objective) {
    const bots = index.bots.map(unpack);
    const preferred = bots.find((bot) => bot.slug === preferredSlug);
    const ranked = bots.map((bot) => ({ bot, score: score(bot, objective) }))
      .sort((a, b) => b.score - a.score || a.bot.slug.localeCompare(b.bot.slug));
    const fallback = bots.find((bot) => bot.slug === 'dreambot') || ranked[0]?.bot;
    const continuation = !preferred && (ranked[0]?.score || 0) < 20
      ? bots.find((bot) => bot.slug === activeSlug)
      : undefined;
    const selected = preferred || continuation || ranked[0]?.bot || fallback;
    const matched = selected ? capabilityMatches(selected, objective).slice(0, 5).map((item) => item.capability) : [];
    return {
      selected,
      matchedCapabilities: matched,
      coverage: index.summary,
      topScore: ranked[0]?.score || 0,
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
          preferredBotSlug: preferredSlug || (fallback.topScore < 20 ? activeSlug || undefined : undefined),
          requestedCapabilities: [],
          liveActionRequested: false,
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
          emoji: fallback.selected?.emoji || 'B',
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
    route.textContent = `I matched this task to ${selected.name} in ${selected.division}. I prepared a governed sandbox route first; anything involving an outside account, spending, publishing, outreach, or data changes will pause for your exact approval.`;
    bubble.append(heading, lead, route);

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

    const actions = document.createElement('div');
    actions.className = 'buddy-response-actions';
    const prospectus = document.createElement('a');
    prospectus.href = `bots.html?prospectus=${encodeURIComponent(selected.slug)}`;
    prospectus.textContent = 'View specialist';
    const calculator = document.createElement('a');
    calculator.href = `calculator.html?bot=${encodeURIComponent(selected.slug)}`;
    calculator.textContent = 'Open ROI calculator';
    const connections = document.createElement('a');
    connections.href = 'connections.html';
    connections.textContent = 'Connect business systems';
    const studio = document.createElement('a');
    studio.href = 'studio.html?type=invention_prototype';
    studio.textContent = 'Open prototype studio';
    actions.append(prospectus, calculator, studio, connections);
    bubble.append(actions);
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
    routeStatus.textContent = `Routed through ${selectedName}.`;
    sendButton.disabled = false;
    sendButton.textContent = 'Send';
    input.focus();
    thread.lastElementChild?.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
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
    routeStatus.textContent = `Ready to route across ${Number(index.summary.profiles).toLocaleString()} verified specialists.`;
  }
  if ('serviceWorker' in navigator && location.protocol !== 'file:') {
    window.addEventListener('load', () => navigator.serviceWorker.register('service-worker.js', { scope: './' }).catch(() => {}));
  }
})();
