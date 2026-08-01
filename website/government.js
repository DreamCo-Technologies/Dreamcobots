(() => {
  const catalog = window.BUDDY_SPECIALIZED_HUBS?.government;
  const sources = catalog?.sources || [];
  const byId = id => document.getElementById(id);
  const node = (tag, className = '', text = '') => { const item = document.createElement(tag); item.className = className; item.textContent = text; return item; };

  function renderSources(filter = '') {
    const query = filter.trim().toLowerCase();
    const visible = sources.filter(source => [source.label, source.category, source.jurisdiction, ...(source.capabilities || [])].join(' ').toLowerCase().includes(query));
    const grid = byId('government-source-grid');
    grid.replaceChildren();
    visible.forEach(source => {
      const card = node('article', 'gov-source');
      const link = node('a', '', 'Open official source');
      link.href = source.url; link.target = '_blank'; link.rel = 'noopener noreferrer';
      card.append(node('small', '', source.category), node('h3', '', source.label), node('p', '', (source.capabilities || []).join(' · ')), link);
      grid.append(card);
    });
    byId('government-source-count').textContent = `${visible.length} official resource${visible.length === 1 ? '' : 's'}`;
  }

  (catalog?.guardrails || []).forEach(rule => byId('government-guardrails').append(node('div', 'gov-rule', rule)));
  renderSources();
  byId('government-approval').addEventListener('change', event => {
    event.currentTarget.closest('form')?.classList.toggle('is-approved', event.currentTarget.checked);
  });
  byId('government-source-search').addEventListener('input', event => renderSources(event.target.value));

  byId('government-plan-form').addEventListener('submit', event => {
    event.preventDefault();
    if (!event.currentTarget.reportValidity()) return;
    const query = byId('government-query').value.trim();
    const category = byId('government-category').value;
    const jurisdiction = byId('government-jurisdiction').value.trim();
    const matching = sources.filter(source => source.category === category);
    const result = byId('government-result');
    const badge = node('span', jurisdiction.toLowerCase() === 'us federal' ? 'badge badge-green' : 'badge badge-amber', jurisdiction.toLowerCase() === 'us federal' ? 'Verified source registry' : 'Source verification required');
    const steps = node('ol', 'gov-plan-list');
    ['Confirm the jurisdiction and exact outcome.', 'Search official sources and save links and dates.', 'Screen stated requirements against user-provided facts.', 'Build deadline, evidence, and question checklists.', 'Draft materials and mark claims needing proof.', 'Return signatures, certifications, payment, and submission to the user.'].forEach(step => steps.append(node('li', '', step)));
    result.replaceChildren(badge, node('h2', '', `Plan: ${query}`), node('p', '', matching.length ? `${matching.length} verified source${matching.length === 1 ? '' : 's'} match this category.` : 'Start with the general official-service directory.'), steps);
    const prompt = `Help me research this government need using official sources only: ${query} Jurisdiction: ${jurisdiction}. Category: ${category}. Screen eligibility but do not determine it. Do not submit, sign, certify, pay, or expose sensitive data.`;
    byId('government-ask-buddy').href = `buddy.html?prompt=${encodeURIComponent(prompt)}`;
    renderSources(category);
  });
})();
