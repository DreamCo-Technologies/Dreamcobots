const results = document.getElementById('platform-results');
const search = document.getElementById('platform-search');
const title = document.getElementById('platform-view-title');
const count = document.getElementById('platform-result-count');
let registry = null;
let currentView = 'capabilities';

const VIEW_TITLES = {
  capabilities: 'Implemented capability contracts',
  innovation: '100 evaluated product innovations',
  companion: '100 companion experience ideas',
  assets: 'Free original presets',
};

function containsQuery(values) {
  const query = search.value.trim().toLowerCase();
  return !query || values.join(' ').toLowerCase().includes(query);
}

function makeRow(primary, secondary, status, actionLabel, action) {
  const row = document.createElement('article');
  row.className = 'platform-row';

  const heading = document.createElement('div');
  const name = document.createElement('h2');
  name.textContent = primary;
  const state = document.createElement('span');
  state.className = 'platform-status';
  state.textContent = status.replaceAll('_', ' ');
  heading.append(name, state);

  const description = document.createElement('p');
  description.textContent = secondary;
  row.append(heading, description);
  if (actionLabel) {
    const button = document.createElement('button');
    button.className = 'platform-action';
    button.type = 'button';
    button.textContent = actionLabel;
    button.addEventListener('click', action);
    row.append(button);
  } else {
    row.append(document.createElement('span'));
  }
  return row;
}

function buddyPrompt(text) {
  location.href = `buddy.html?prompt=${encodeURIComponent(text)}`;
}

function renderCapabilities() {
  const items = registry.implemented_capabilities.filter(item => containsQuery([
    item.id, item.name, item.status, item.evidence,
  ]));
  for (const item of items) {
    const row = makeRow(
      item.name,
      `Evidence: ${item.evidence}`,
      item.status,
      'Open in Buddy',
      () => buddyPrompt(`Use Buddy's ${item.name} system for this task. Start with a local or sandbox plan, show evidence, and stop for approval before any external action.`),
    );
    results.append(row);
  }
  return items.length;
}

function renderIdeas(kind) {
  const source = kind === 'innovation' ? registry.revolutionary_ideas : registry.companion_ideas;
  const items = source.filter(item => containsQuery([item.id, item.theme, item.kind, item.idea]));
  for (const item of items) {
    results.append(makeRow(
      item.theme,
      item.idea,
      item.status,
      'Plan this idea',
      () => buddyPrompt(`Evaluate roadmap idea ${item.id}: ${item.idea} Define the smallest safe prototype, tests, cost, privacy rules, and approval gates. Do not claim it is implemented yet.`),
    ));
  }
  return items.length;
}

function renderAssets() {
  const assets = [
    ...registry.free_asset_catalog.voices.map(item => ({ ...item, assetType: 'voice preset' })),
    ...registry.free_asset_catalog.avatars.map(item => ({ ...item, assetType: 'avatar preset' })),
  ].filter(item => containsQuery([item.id, item.name, item.kind, item.assetType]));
  for (const item of assets) {
    const detail = item.assetType === 'voice preset'
      ? `Synthetic parameter preset. Rate ${item.rate}, pitch ${item.pitch}. No recorded voice is bundled.`
      : `Original geometric avatar preset using ${item.primary} and ${item.accent}.`;
    const row = makeRow(item.name, detail, item.assetType, 'Customize Buddy', () => (
      buddyPrompt(`Customize my Buddy using ${item.id}. Show the local preview and keep the profile owner-controlled and traceable.`)
    ));
    if (item.primary && item.accent) {
      const swatches = document.createElement('div');
      swatches.className = 'platform-swatches';
      for (const color of [item.primary, item.accent]) {
        const swatch = document.createElement('span');
        swatch.className = 'platform-swatch';
        swatch.style.backgroundColor = color;
        swatch.title = color;
        swatches.append(swatch);
      }
      row.children[1].append(swatches);
    }
    results.append(row);
  }
  return assets.length;
}

function render() {
  if (!registry) return;
  results.replaceChildren();
  title.textContent = VIEW_TITLES[currentView];
  let total = 0;
  if (currentView === 'capabilities') total = renderCapabilities();
  else if (currentView === 'assets') total = renderAssets();
  else total = renderIdeas(currentView);
  count.textContent = `${total} result${total === 1 ? '' : 's'}`;
  if (!total) {
    const empty = document.createElement('p');
    empty.className = 'platform-empty';
    empty.textContent = 'No registry entries match this search.';
    results.append(empty);
  }
}

document.querySelectorAll('[data-view]').forEach(button => {
  button.addEventListener('click', () => {
    document.querySelectorAll('[data-view]').forEach(item => item.classList.remove('active'));
    button.classList.add('active');
    currentView = button.dataset.view;
    render();
  });
});
search.addEventListener('input', render);

fetch('data/buddy-platform-expansion.json', { cache: 'no-store' })
  .then(response => response.ok ? response.json() : Promise.reject(new Error('Registry unavailable')))
  .then(data => {
    registry = data;
    document.getElementById('metric-capabilities').textContent = data.counts.implemented_capability_contracts;
    document.getElementById('metric-targets').textContent = data.counts.release_targets;
    document.getElementById('metric-ideas').textContent = data.counts.revolutionary_roadmap_ideas + data.counts.companion_roadmap_ideas;
    document.getElementById('metric-assets').textContent = data.counts.free_voice_presets + data.counts.free_avatar_presets;
    render();
  })
  .catch(error => {
    results.textContent = error.message;
    count.textContent = 'Unavailable';
  });
