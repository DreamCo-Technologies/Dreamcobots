// DreamCo Rebuild V2 — contextual task buttons for existing Codex-built pages.
(function () {
  const page = location.pathname.split('/').pop() || 'index.html';

  const actionMaps = {
    'studio.html': [
      ['🎬 Build Movie', () => selectStudioType('feature_film')],
      ['📺 Build Series', () => selectStudioType('animated_series')],
      ['🧑 Build Actors', () => focusStudio('actor-controls')],
      ['✍️ Write Script', () => selectStudioType('feature_film', 'project-objective')],
      ['🎞️ Build Episodes', () => selectStudioType('fiction_or_variety_show', 'show-controls')],
      ['🎵 Music Video', () => selectStudioType('music_video')],
      ['📢 Build Commercial', () => selectStudioType('commercial')],
      ['🎓 Build Course', () => selectStudioType('college_course')],
      ['🎮 Build Game', () => selectStudioType('game')],
      ['📱 Social Series', () => selectStudioType('social_content_series')],
      ['🚀 Prepare Release', () => focusStudio('show-controls')],
    ],
    'buddy.html': [
      ['🏢 Build Business', () => route('success.html#business-builder')],
      ['📱 Build App', () => route('codelab.html#app-builder')],
      ['🌐 Build Website', () => route('codelab.html#website-builder')],
      ['🎬 Make Movie', () => route('studio.html?project=feature_film')],
      ['📺 Make Series', () => route('studio.html?project=fiction_or_variety_show')],
      ['💰 Make Money', () => route('revenue.html#opportunities')],
      ['🎯 Find Customers', () => route('leads.html')],
      ['⚙️ Automate Work', () => route('orchestration.html')],
      ['🔗 Connect Apps', () => route('connections.html')],
      ['🧠 Train Company Buddy', () => route('learning.html#company-buddy')],
    ],
    'dashboard.html': [
      ['🏢 Business', () => route('success.html#business-builder')],
      ['📱 App', () => route('codelab.html#app-builder')],
      ['🌐 Website', () => route('codelab.html#website-builder')],
      ['🎬 Movie', () => route('studio.html?project=feature_film')],
      ['💵 Revenue', () => route('revenue.html')],
      ['🤖 Bots', () => route('bots.html')],
      ['⚙️ Automations', () => route('orchestration.html')],
      ['🔗 Devices & Apps', () => route('connections.html')],
    ],
    'success.html': [
      ['🏢 Start Business', () => emit('dreamco:workshop', { kind: 'business', action: 'start' })],
      ['🧭 Pick Market', () => emit('dreamco:workshop', { kind: 'business', action: 'market' })],
      ['📦 Build Offer', () => emit('dreamco:workshop', { kind: 'business', action: 'offer' })],
      ['💲 Price It', () => emit('dreamco:workshop', { kind: 'business', action: 'pricing' })],
      ['🎯 Find Customers', () => route('leads.html')],
      ['📣 Build Marketing', () => emit('dreamco:workshop', { kind: 'business', action: 'marketing' })],
      ['🧾 Build Operations', () => route('orchestration.html')],
      ['🤖 Train Business Buddy', () => route('learning.html#company-buddy')],
    ],
    'codelab.html': [
      ['📱 New App', () => emit('dreamco:workshop', { kind: 'app', action: 'new' })],
      ['🌐 New Website', () => emit('dreamco:workshop', { kind: 'website', action: 'new' })],
      ['🧱 Architecture', () => emit('dreamco:workshop', { kind: 'app', action: 'architecture' })],
      ['🎨 UI Builder', () => emit('dreamco:workshop', { kind: 'app', action: 'ui' })],
      ['🗄️ Database', () => emit('dreamco:workshop', { kind: 'app', action: 'database' })],
      ['🔌 API Builder', () => emit('dreamco:workshop', { kind: 'app', action: 'api' })],
      ['🧪 Test', () => route('test-center.html')],
      ['🚀 Deploy', () => emit('dreamco:workshop', { kind: 'app', action: 'deploy' })],
    ],
    'leads.html': [
      ['🔎 Find Companies', () => emit('dreamco:workshop', { kind: 'sales', action: 'companies' })],
      ['👤 Find Decision Makers', () => emit('dreamco:workshop', { kind: 'sales', action: 'decision-makers' })],
      ['🧠 Research Prospect', () => emit('dreamco:workshop', { kind: 'sales', action: 'research' })],
      ['✉️ Draft Outreach', () => emit('dreamco:workshop', { kind: 'sales', action: 'outreach' })],
      ['📄 Build Proposal', () => emit('dreamco:workshop', { kind: 'sales', action: 'proposal' })],
      ['📊 Pipeline', () => emit('dreamco:workshop', { kind: 'sales', action: 'pipeline' })],
    ],
    'revenue.html': [
      ['💡 Find Opportunity', () => emit('dreamco:workshop', { kind: 'business', action: 'opportunity' })],
      ['💵 Price Service', () => emit('dreamco:workshop', { kind: 'business', action: 'pricing' })],
      ['🧮 Profit Simulation', () => emit('dreamco:workshop', { kind: 'business', action: 'profit' })],
      ['🎯 Get Customers', () => route('leads.html')],
      ['🧾 Build Invoice Flow', () => route('payments.html')],
      ['📈 Track Results', () => emit('dreamco:workshop', { kind: 'business', action: 'results' })],
    ],
    'orchestration.html': [
      ['➕ New Workflow', () => emit('dreamco:workflow', { action: 'new' })],
      ['🤖 Pick Bots', () => route('bots.html')],
      ['🔗 Connect Tools', () => route('connections.html')],
      ['⏱️ Schedule', () => emit('dreamco:workflow', { action: 'schedule' })],
      ['🧪 Sandbox Test', () => route('test-center.html')],
      ['▶️ Run Approved', () => emit('dreamco:workflow', { action: 'execute' })],
    ],
    'connections.html': [
      ['📱 Connect App', () => emit('dreamco:connection', { kind: 'app' })],
      ['💻 Pair Computer', () => emit('dreamco:connection', { kind: 'desktop' })],
      ['📱 Pair Phone', () => emit('dreamco:connection', { kind: 'phone' })],
      ['📺 Pair TV', () => emit('dreamco:connection', { kind: 'tv' })],
      ['📶 Wi‑Fi Device', () => emit('dreamco:connection', { kind: 'wifi' })],
      ['🔵 Bluetooth Device', () => emit('dreamco:connection', { kind: 'bluetooth' })],
      ['🔐 Review Permissions', () => emit('dreamco:connection', { kind: 'permissions' })],
    ],
    'learning.html': [
      ['🏢 Train Company Buddy', () => emit('dreamco:training', { kind: 'company' })],
      ['📚 Add SOPs', () => emit('dreamco:training', { kind: 'sop' })],
      ['🧰 Add Tools', () => route('connections.html')],
      ['🧑‍💼 Add Roles', () => emit('dreamco:training', { kind: 'roles' })],
      ['🧪 Test Skills', () => route('test-center.html')],
      ['✅ Certify Workflow', () => emit('dreamco:training', { kind: 'certify' })],
    ],
  };

  const actions = actionMaps[page];
  if (!actions?.length) return;

  const dock = document.createElement('section');
  dock.className = 'buddy-page-actions';
  dock.setAttribute('aria-label', 'Quick actions');
  dock.innerHTML = `<div class="buddy-page-actions-inner"><strong>What do you want to do?</strong><div class="buddy-page-actions-buttons"></div></div>`;
  const buttons = dock.querySelector('.buddy-page-actions-buttons');
  for (const [label, handler] of actions) {
    const button = document.createElement('button');
    button.type = 'button';
    button.className = 'buddy-page-action-button';
    button.textContent = label;
    button.addEventListener('click', handler);
    buttons.appendChild(button);
  }

  const main = document.querySelector('main');
  if (main) main.insertBefore(dock, main.firstChild);
  else document.body.insertBefore(dock, document.body.firstChild);

  const style = document.createElement('style');
  style.textContent = `
    .buddy-page-actions{margin:16px auto 22px;max-width:1400px;padding:0 18px}
    .buddy-page-actions-inner{background:var(--card,#111827);border:1px solid var(--border,#263244);border-radius:16px;padding:14px 16px;box-shadow:var(--shadow2,0 8px 28px rgba(0,0,0,.2))}
    .buddy-page-actions-inner>strong{display:block;margin-bottom:10px;font-size:.92rem}
    .buddy-page-actions-buttons{display:flex;gap:8px;overflow-x:auto;padding-bottom:2px;scrollbar-width:thin}
    .buddy-page-action-button{flex:0 0 auto;border:1px solid var(--border,#334155);background:var(--card2,#172033);color:var(--text,#f8fafc);border-radius:999px;padding:9px 13px;font:600 .82rem Inter,system-ui;cursor:pointer}
    .buddy-page-action-button:hover,.buddy-page-action-button:focus-visible{transform:translateY(-1px);border-color:var(--primary,#7c3aed);outline:none}
  `;
  document.head.appendChild(style);

  function route(url) { location.href = url; }
  function emit(name, detail) {
    window.dispatchEvent(new CustomEvent(name, { detail }));
    document.dispatchEvent(new CustomEvent(name, { detail }));
  }
  function focusStudio(id) {
    const el = document.getElementById(id);
    if (el) { el.hidden = false; el.scrollIntoView({ behavior: 'smooth', block: 'start' }); }
  }
  function selectStudioType(value, focusId) {
    const select = document.getElementById('project-type');
    if (select) {
      select.value = value;
      select.dispatchEvent(new Event('change', { bubbles: true }));
    }
    const target = focusId ? document.getElementById(focusId) : document.getElementById('studio-form');
    target?.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  // Deep-link support used by Buddy/dashboard action buttons.
  const requestedProject = new URLSearchParams(location.search).get('project');
  if (page === 'studio.html' && requestedProject) selectStudioType(requestedProject);
})();
