const botSelector = document.getElementById('bot-selector');
const blueprint = document.getElementById('blueprint');
const divisionCache = new Map();
let compactCatalog = null;

function escapeHtml(value) {
  return String(value ?? '')
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#39;');
}

function list(items, transform = (item) => item) {
  return `<ul>${items.map((item) => `<li>${escapeHtml(transform(item))}</li>`).join('')}</ul>`;
}

async function loadDivision(name) {
  if (divisionCache.has(name)) return divisionCache.get(name);
  const response = await fetch(`data/bot-fleet/${encodeURIComponent(name)}.json`, { cache: 'no-store' });
  if (!response.ok) throw new Error(`Division catalog returned ${response.status}`);
  const data = await response.json();
  divisionCache.set(name, data);
  return data;
}

function renderBot(bot) {
  const business = bot.business_system;
  const leads = business.lead_system;
  const qualification = Object.entries(leads.qualification.score_dimensions)
    .map(([name, score]) => `${name.replaceAll('_', ' ')}: ${score} points`);
  blueprint.innerHTML = `<div class="blueprint-head">
      <div>
        <span class="blueprint-label">${escapeHtml(bot.identity.division)} / ${escapeHtml(bot.identity.category)}</span>
        <h2>${escapeHtml(bot.identity.display_name)}</h2>
        <p>${escapeHtml(business.specialization.core_offer)}</p>
      </div>
      <span class="blueprint-status">${escapeHtml(leads.status.replaceAll('_', ' '))}</span>
    </div>
    <div class="blueprint-grid">
      <div class="blueprint-panel"><h3>Ideal customers</h3>${list(business.specialization.ideal_customer_segments)}</div>
      <div class="blueprint-panel"><h3>Promised outputs</h3>${list(business.specialization.promised_outputs)}</div>
      <div class="blueprint-panel"><h3>Lead queries</h3>${list(leads.discovery.query_templates)}</div>
      <div class="blueprint-panel"><h3>Authorized sources</h3>${list(leads.discovery.authorized_source_types)}</div>
      <div class="blueprint-panel"><h3>Qualification score</h3>${list(qualification)}<p><code>Review threshold: ${leads.qualification.minimum_score_for_owner_review}/100 plus documented permission</code></p></div>
      <div class="blueprint-panel"><h3>Follow-up controls</h3>${list([
        `${leads.follow_up.maximum_follow_ups} follow-ups maximum`,
        `${leads.follow_up.minimum_interval_hours} hours minimum between messages`,
        'Exact approval for every message',
        ...leads.follow_up.stop_conditions.map((item) => `Stop: ${item}`),
      ])}</div>
    </div>`;
}

async function selectBot(slug) {
  const compact = compactCatalog.bots.find((bot) => bot.identity.slug === slug);
  if (!compact) return;
  blueprint.innerHTML = '<p class="blueprint-loading">Loading bot blueprint.</p>';
  const division = await loadDivision(compact.identity.division);
  const bot = division.bots.find((candidate) => candidate.identity.slug === slug);
  if (!bot) throw new Error('Bot blueprint not found');
  renderBot(bot);
}

botSelector.addEventListener('change', () => {
  selectBot(botSelector.value).catch((error) => {
    blueprint.innerHTML = `<p class="blueprint-loading">${escapeHtml(error.message)}</p>`;
  });
});

document.getElementById('guardrail-form').addEventListener('submit', (event) => {
  event.preventDefault();
  const source = document.getElementById('test-source').value;
  const state = document.getElementById('test-state').value;
  const permission = document.getElementById('test-permission').checked;
  const approval = document.getElementById('test-approval').checked;
  const result = document.getElementById('guardrail-result');
  result.className = 'guardrail-result';
  if (['replied', 'unsubscribed', 'bounced', 'complaint'].includes(state)) {
    result.classList.add('stop');
    result.textContent = `Stopped: ${state.replaceAll('_', ' ')} is on the suppression path. No draft or follow-up is eligible.`;
    return;
  }
  if (!permission) {
    result.textContent = source === 'directory'
      ? 'Research only: a public business listing is not recipient permission to send a message.'
      : 'Research only: document recipient permission for the selected channel before drafting outreach.';
    return;
  }
  if (!approval) {
    result.textContent = 'Approval required: permission allows a relevant draft, but the owner must approve this exact message before dispatch.';
    return;
  }
  result.classList.add('ready');
  result.textContent = 'Adapter gate: recipient permission and owner approval are present. A configured backend adapter, cadence check, and idempotency check are still required. Nothing was sent.';
});

fetch('data/bot-fleet-catalog.json', { cache: 'no-store' })
  .then((response) => response.ok ? response.json() : Promise.reject(new Error(`Fleet catalog returned ${response.status}`)))
  .then(async (data) => {
    compactCatalog = data;
    document.getElementById('lead-profile-count').textContent = data.summary.per_bot_governed_lead_systems;
    document.getElementById('lead-division-count').textContent = data.summary.divisions;
    botSelector.innerHTML = data.bots
      .slice()
      .sort((a, b) => a.identity.display_name.localeCompare(b.identity.display_name))
      .map((bot) => `<option value="${escapeHtml(bot.identity.slug)}">${escapeHtml(bot.identity.display_name)} - ${escapeHtml(bot.identity.division)}</option>`)
      .join('');
    botSelector.disabled = false;
    const preferred = data.bots.find((bot) => bot.identity.slug === 'commercial-scanner') ?? data.bots[0];
    botSelector.value = preferred.identity.slug;
    await selectBot(preferred.identity.slug);
  })
  .catch((error) => {
    blueprint.innerHTML = `<p class="blueprint-loading">${escapeHtml(error.message)}</p>`;
  });
