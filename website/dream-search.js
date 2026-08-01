(function () {
  'use strict';

  const data = window.DREAMCO_SEARCH_DATA;
  const byId = (id) => document.getElementById(id);
  const input = byId('dream-search-input');
  const submitButton = byId('dream-search-submit');
  const modeButtons = [byId('search-mode-dreamco'), byId('search-mode-web')];
  const results = byId('search-results');
  const empty = byId('search-empty');
  const loadMore = byId('search-load-more');
  const typeFilter = byId('search-type-filter');
  const divisionFilter = byId('search-division-filter');
  const evidenceFilter = byId('search-evidence-filter');
  const sortControl = byId('search-sort');
  const dreamcoView = byId('dreamco-results-view');
  const webView = byId('web-results-view');
  const modeNote = byId('search-mode-note');
  const statusLabels = {
    implementation_evidence: 'Implementation evidence',
    public_page: 'Public page',
    reference_catalog: 'Reference only',
    repository_catalog: 'Repository catalog',
    repository_evidence: 'Repository evidence',
    roadmap: 'Roadmap idea',
  };
  const typeLabels = {
    bot: 'Bot specialist', capability: 'Capability', division: 'Division', library: 'Library',
    model: 'Model reference', page: 'Public page', provider: 'Provider reference', roadmap: 'Roadmap', system: 'System',
  };
  const typeIcons = { bot: 'B', capability: 'C', division: 'D', library: 'L', model: 'M', page: 'P', provider: 'AI', roadmap: 'R', system: 'S' };
  const state = { mode: 'dreamco', query: '', visibleLimit: 30, ranked: [] };

  function normalize(value) {
    return String(value || '')
      .normalize('NFKD')
      .replace(/[\u0300-\u036f]/g, '')
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, ' ')
      .trim()
      .replace(/\s+/g, ' ');
  }

  function unique(values) {
    return [...new Set(values.filter(Boolean))];
  }

  function expandQuery(query) {
    const policy = data.engine.query_policy;
    const normalized = normalize(query).slice(0, policy.max_length);
    const stopWords = new Set(policy.stop_words.map(normalize));
    const tokens = normalized.split(' ').filter((token) => token && !stopWords.has(token));
    policy.synonym_groups.forEach((group) => {
      const terms = group.terms.map(normalize);
      if (!terms.some((term) => term && (` ${normalized} `).includes(` ${term} `))) return;
      terms.forEach((term) => tokens.push(...term.split(' ').filter((token) => token && !stopWords.has(token))));
    });
    return unique(tokens);
  }

  function includesToken(haystack, token) {
    return (` ${haystack} `).includes(` ${token} `);
  }

  function rankDocuments() {
    const query = normalize(state.query).slice(0, data.engine.query_policy.max_length);
    if (!query) return [];
    const tokens = expandQuery(query);
    const originalTokens = unique(query.split(' ').filter((token) => !data.engine.query_policy.stop_words.includes(token)));
    const weights = data.engine.ranking;
    const filters = {
      type: typeFilter.value,
      division: divisionFilter.value,
      evidence: evidenceFilter.value,
    };

    return data.documents
      .filter((item) => filters.type === 'all' || item.type === filters.type)
      .filter((item) => filters.division === 'all' || item.division === filters.division)
      .filter((item) => filters.evidence === 'all' || item.evidence_level === filters.evidence)
      .map((item) => {
        const title = normalize(item.title);
        const summary = normalize(item.summary);
        const keywords = normalize(item.keywords.join(' '));
        const category = normalize(`${item.category} ${item.division} ${item.type}`);
        let score = weights.type_boosts[item.type] || 0;
        const matched = [];
        if (title === query) score += weights.exact_title;
        else if (title.includes(query)) score += weights.title_phrase;
        if (summary.includes(query)) score += weights.summary_phrase;
        if (keywords.includes(query)) score += weights.keyword_phrase;
        tokens.forEach((token) => {
          let found = false;
          if (includesToken(title, token)) { score += weights.title_token; found = true; }
          if (includesToken(keywords, token)) { score += weights.keyword_token; found = true; }
          if (includesToken(summary, token)) { score += weights.summary_token; found = true; }
          if (includesToken(category, token)) { score += weights.category_token; found = true; }
          if (found) matched.push(token);
        });
        if (item.evidence) score += weights.evidence_bonus;
        if (!item.status.includes('roadmap')) score += weights.status_bonus;
        score += originalTokens.filter((token) => matched.includes(token)).length * 4;
        return { item, score, matched: unique(matched) };
      })
      .filter((result) => result.matched.length || result.score >= weights.title_phrase)
      .sort((a, b) => {
        if (sortControl.value === 'title') return a.item.title.localeCompare(b.item.title);
        if (sortControl.value === 'type') return a.item.type.localeCompare(b.item.type) || b.score - a.score;
        return b.score - a.score || a.item.title.localeCompare(b.item.title) || a.item.id.localeCompare(b.item.id);
      });
  }

  function create(tag, className, text) {
    const element = document.createElement(tag);
    if (className) element.className = className;
    if (text !== undefined) element.textContent = text;
    return element;
  }

  function buddyUrl(item) {
    const prompt = `Help me use the DreamCo search result "${item.title}" for this goal: ${state.query}. Start by confirming its current status (${item.status}) and repository evidence (${item.evidence}). Build a reviewable plan, route to the right specialist, run local tests first, and ask before external, account, payment, outreach, or publishing actions.`;
    return `buddy.html?prompt=${encodeURIComponent(prompt)}`;
  }

  function renderResult(result) {
    const item = result.item;
    const article = create('article', 'search-result');
    const icon = create('div', 'result-type-icon', typeIcons[item.type] || '?');
    icon.setAttribute('aria-hidden', 'true');
    const copy = create('div', 'result-copy');
    const meta = create('div', 'result-meta');
    meta.append(create('span', '', typeLabels[item.type] || item.type));
    meta.append(create('span', '', statusLabels[item.evidence_level] || item.evidence_level.replaceAll('_', ' ')));
    if (item.division) meta.append(create('span', '', item.division));
    const heading = create('h3');
    const titleLink = create('a', '', item.title);
    titleLink.href = item.url;
    heading.append(titleLink);
    copy.append(meta, heading, create('p', '', item.summary));
    copy.append(create('div', 'result-evidence', `Evidence: ${item.evidence} · Status: ${item.status.replaceAll('_', ' ')}`));
    if (result.matched.length) {
      const terms = create('div', 'matched-terms');
      result.matched.slice(0, 8).forEach((term) => terms.append(create('span', '', term)));
      copy.append(terms);
    }
    const actions = create('div', 'result-actions');
    const open = create('a', '', item.type === 'bot' ? 'Prospectus' : 'Open');
    open.href = item.url;
    const buddy = create('a', '', 'Ask Buddy');
    buddy.href = buddyUrl(item);
    actions.append(open, buddy);
    article.append(icon, copy, actions);
    return article;
  }

  function updateBuddyLink() {
    const prompt = state.query
      ? `Search the DreamCo system for "${state.query}" and help me choose the strongest evidence-backed specialist, capability, or tool. Explain what is working, what is reference-only or planned, then build a reviewable task plan.`
      : 'Help me discover the right DreamCo specialist, capability, or tool for my goal.';
    byId('search-ask-buddy').href = `buddy.html?prompt=${encodeURIComponent(prompt)}`;
  }

  function renderDreamcoResults() {
    updateBuddyLink();
    state.ranked = rankDocuments();
    results.replaceChildren();
    const shown = state.ranked.slice(0, state.visibleLimit);
    shown.forEach((result) => results.append(renderResult(result)));
    empty.hidden = Boolean(state.query);
    byId('search-result-label').textContent = state.query ? `Results for "${state.query}"` : 'DreamCo index';
    byId('search-result-count').textContent = state.query
      ? `${state.ranked.length.toLocaleString()} matching records`
      : 'Ready to search';
    if (state.query && !state.ranked.length) {
      empty.hidden = false;
      empty.querySelector('strong').textContent = 'No indexed match yet.';
      empty.querySelector('p').textContent = 'Try a broader phrase, clear a filter, switch to Web, or ask Buddy to define the task and search the nearest capabilities.';
    } else if (!state.query) {
      empty.querySelector('strong').textContent = 'Start with an outcome.';
      empty.querySelector('p').textContent = 'Try a task, industry, capability, bot name, division, model, API, or page. DreamSearch will show what is implemented, cataloged, or still planned.';
    }
    loadMore.hidden = shown.length >= state.ranked.length;
  }

  function webQuery() {
    return state.query.trim().slice(0, data.engine.query_policy.max_length);
  }

  function renderWeb() {
    const query = webQuery();
    const container = byId('web-provider-links');
    container.replaceChildren();
    data.engine.web_search.providers.forEach((provider) => {
      const link = create('a');
      link.target = '_blank';
      link.rel = 'noopener noreferrer';
      link.href = query ? provider.url_template.replace('{query}', encodeURIComponent(query)) : '#';
      link.setAttribute('aria-disabled', query ? 'false' : 'true');
      link.append(create('strong', '', provider.name), create('span', '', 'Open ↗'));
      if (!query) link.addEventListener('click', (event) => event.preventDefault());
      container.append(link);
    });
    byId('web-title').textContent = query ? `Search the web for “${query}”` : 'Choose where to search';
    const prompt = query
      ? `Research this current question using authoritative sources: ${query}. Cite every time-sensitive claim, separate facts from inferences, compare source dates, and do not send private repository content or personal data.`
      : 'Help me define a web research question without sharing private repository content or personal data.';
    byId('web-ask-buddy').href = `buddy.html?prompt=${encodeURIComponent(prompt)}`;
  }

  function syncUrl() {
    const params = new URLSearchParams(location.search);
    if (state.query) params.set('q', state.query); else params.delete('q');
    if (state.mode === 'web') params.set('mode', 'web'); else params.delete('mode');
    history.replaceState(null, '', `${location.pathname}${params.size ? `?${params}` : ''}`);
  }

  function setMode(mode) {
    state.mode = mode === 'web' ? 'web' : 'dreamco';
    modeButtons.forEach((button) => {
      const active = button.dataset.mode === state.mode;
      button.classList.toggle('active', active);
      button.setAttribute('aria-pressed', String(active));
    });
    dreamcoView.hidden = state.mode !== 'dreamco';
    webView.hidden = state.mode !== 'web';
    modeNote.textContent = state.mode === 'dreamco'
      ? 'Searches the generated repository index. No account, API key, or paid service is needed.'
      : 'Opens only the provider you choose. DreamSearch does not claim or store live web results.';
    if (state.mode === 'web') renderWeb(); else renderDreamcoResults();
    syncUrl();
  }

  async function openWithLocalBridge() {
    const query = webQuery();
    const approval = byId('web-local-approval');
    const status = byId('web-local-status');
    const token = sessionStorage.getItem('buddy-local-token') || '';
    if (!query) { status.textContent = 'Enter a search question first.'; return; }
    if (!approval.checked) { status.textContent = 'Approve this one visible browser search first.'; return; }
    if (!token || !['127.0.0.1', 'localhost'].includes(location.hostname)) {
      status.textContent = 'Start the private Buddy local bridge, then open DreamSearch from that local session.';
      return;
    }
    try {
      const response = await fetch('/api/local/browser/search', {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
        body: JSON.stringify({ query, engine: byId('web-local-provider').value, browser: 'system', approved: true }),
      });
      const payload = await response.json().catch(() => ({}));
      if (!response.ok) throw new Error(payload.error || 'The local bridge rejected the search.');
      approval.checked = false;
      status.textContent = `${payload.engine} opened in the system browser. No page control was granted.`;
    } catch (error) {
      status.textContent = error.message;
    }
  }

  function populateFilters() {
    data.filters.divisions.forEach((division) => {
      const option = create('option', '', division);
      option.value = division;
      divisionFilter.append(option);
    });
    data.filters.evidence_levels.forEach((level) => {
      const option = create('option', '', statusLabels[level] || level.replaceAll('_', ' '));
      option.value = level;
      evidenceFilter.append(option);
    });
    byId('search-index-count').textContent = `${data.summary.documents.toLocaleString()} records`;
    byId('search-index-detail').textContent = `${data.summary.indexed_bot_profiles.toLocaleString()} bots · ${data.summary.searchable_capability_terms.toLocaleString()} capability terms · ${data.summary.indexed_divisions} divisions · ${data.summary.indexed_models} models`;
  }

  function runSearch() {
    state.query = input.value.trim().slice(0, data.engine.query_policy.max_length);
    state.visibleLimit = data.engine.result_policy.default_limit;
    if (state.mode === 'web') renderWeb(); else renderDreamcoResults();
    syncUrl();
  }

  if (!data?.documents?.length) {
    byId('search-result-count').textContent = 'Search index unavailable';
    empty.querySelector('p').textContent = 'Regenerate the DreamSearch index before using this page.';
    return;
  }

  populateFilters();
  submitButton.disabled = false;
  const params = new URLSearchParams(location.search);
  input.value = params.get('q') || '';
  state.query = input.value.trim();
  byId('dream-search-form').addEventListener('submit', (event) => { event.preventDefault(); runSearch(); });
  input.addEventListener('input', () => { window.clearTimeout(input._dreamSearchTimer); input._dreamSearchTimer = window.setTimeout(runSearch, 120); });
  modeButtons.forEach((button) => button.addEventListener('click', () => setMode(button.dataset.mode)));
  document.querySelectorAll('[data-query]').forEach((button) => button.addEventListener('click', () => {
    input.value = button.dataset.query;
    state.query = input.value;
    setMode('dreamco');
    input.focus();
  }));
  [typeFilter, divisionFilter, evidenceFilter, sortControl].forEach((control) => control.addEventListener('change', () => {
    state.visibleLimit = data.engine.result_policy.default_limit;
    renderDreamcoResults();
  }));
  byId('search-clear-filters').addEventListener('click', () => {
    typeFilter.value = 'all'; divisionFilter.value = 'all'; evidenceFilter.value = 'all'; sortControl.value = 'relevance';
    renderDreamcoResults();
  });
  loadMore.addEventListener('click', () => { state.visibleLimit += data.engine.result_policy.default_limit; renderDreamcoResults(); });
  byId('web-local-open').addEventListener('click', openWithLocalBridge);
  document.addEventListener('keydown', (event) => {
    if (event.key === '/' && !/input|textarea|select/i.test(document.activeElement?.tagName || '')) {
      event.preventDefault(); input.focus();
    }
  });
  setMode(params.get('mode') === 'web' ? 'web' : 'dreamco');
}());
