// DreamCo Empire OS — Shared Navigation
(function() {
  const current = location.pathname.split('/').pop() || 'index.html';
  const links = [
    { href: 'dashboard.html', label: 'Dashboard' },
    { href: 'buddy.html', label: 'Buddy Bot' },
    { href: 'goals.html', label: 'Complete a goal' },
    { href: 'desks.html', label: 'All plan desks' },
    { href: 'sources.html', label: 'Connect sources' },
    { href: 'actions.html', label: 'Actions' },
    { href: 'connect-desk.html', label: 'Grant an app' },
    { href: 'data-control.html', label: 'Data and memory' },
    { href: 'learn.html', label: 'Learn' },
    { href: 'devices.html', label: 'Devices' },
    { href: 'os.html', label: 'Buddy OS' },
    { href: 'buddy-expert-mode.html', label: 'Expert Mode' },
    { href: 'buddy-invention-lab.html', label: 'Idea-to-Store' },
    { href: 'master-build.html', label: 'Master Build' },
    { href: 'buddy-command-center.html', label: 'Command Center' },
    { href: 'world-lens.html', label: 'World Lens GPS' },
    { href: 'family-circle.html', label: 'Family Circle' },
    { href: 'resource-211.html', label: '211 Resource Guide' },
    { href: 'voice-command-center.html', label: 'Voice Commands' },
    { href: 'world-source-center.html', label: 'World Sources' },
    { href: 'my-buddy.html', label: 'My Buddy' },
    { href: 'sign-in.html', label: 'Sign In' },
    { href: 'resource-connection-center.html', label: 'Resource Connections' },
    { href: 'independence-center.html', label: 'Independence' },
    { href: 'buddy-workspace.html', label: 'Buddy Workspace' },
    { href: 'opportunity-hub.html', label: 'Opportunity Hub' },
    { href: 'setup-center.html', label: 'Setup Center' },
    { href: 'buddy-operating-system.html', label: 'Buddy AGI OS' },
    { href: 'success.html', label: 'Success Center' },
    { href: 'search.html', label: 'DreamSearch' },
    { href: 'studio.html', label: 'Creative Studio' },
    { href: 'practice.html', label: 'Practice Lab' },
    { href: 'platform.html', label: 'Platform Registry' },
    { href: 'calculator.html', label: 'Calculator Lab' },
    { href: 'divisions.html', label: 'Divisions' },
    { href: 'bots.html', label: 'Bot Fleet' },
    { href: 'test-center.html', label: 'Test Center' },
    { href: 'security.html', label: 'Defense Center' },
    { href: 'system-map.html', label: 'Repository Map' },
    { href: 'chat.html', label: 'Chat' },
    { href: 'install.html', label: 'Install and Launch' },
    { href: 'leads.html', label: 'Lead Systems' },
    { href: 'autonomy.html', label: 'Autonomy' },
    { href: 'ecosystem.html', label: 'Ecosystem' },
    { href: 'orchestration.html', label: 'Orchestration' },
    { href: 'marketplace.html', label: 'Marketplace' },
    { href: 'formulas.html', label: 'Formulas' },
    { href: 'deals.html', label: 'Deals' },
    { href: 'debug.html', label: 'Debug' },
    { href: 'wiring.html', label: 'Wiring map' },
    { href: 'branch-health.html', label: 'Branch health' },
    { href: 'command.html', label: 'Command' },
    { href: 'ops.html', label: 'Ops' },
    { href: 'work.html', label: 'Watch / idle' },
    { href: 'connections.html', label: 'Connections' },
    { href: 'government.html', label: 'Government Resources' },
    { href: 'crypto.html', label: 'Crypto Safety Lab' },
    { href: 'models.html', label: 'AI Models' },
    { href: 'benchmark-tracker.html', label: 'Benchmark Tracker' },
    { href: 'open-model-lab.html', label: 'Open Model Lab' },
    { href: 'buddy-open-core.html', label: 'Buddy Open Core' },
    { href: 'buddy-learning-lab.html', label: 'Learning Lab' },
    { href: 'leaders.html', label: 'AI Leaders' },
    { href: 'learning.html', label: 'Learning' },
    { href: 'timecapsule.html', label: 'Time Capsule' },
    { href: 'costs.html', label: 'Cost Tracking' },
    { href: 'revenue.html', label: 'Revenue' },
    { href: 'settings.html', label: 'Settings' }
  ];
  const navHTML = `
<nav>
  <div class="container">
    <div class="nav-inner">
      <a href="buddy.html" class="nav-brand">
        <div class="nav-logo">*</div>
        <span>DreamCo <strong>Empire OS</strong></span>
      </a>
      <div class="nav-links" id="nav-links-desktop">
        ${links.slice(0,9).map(l=>`<a href="${l.href}" class="${current===l.href?'nav-active':''}">${l.label}</a>`).join('')}
        <div class="nav-more">
          <a href="#" class="nav-more-btn" onclick="toggleMoreMenu(event)">More</a>
          <div class="nav-more-menu" id="nav-more-menu">
            ${links.slice(9).map(l=>`<a href="${l.href}" class="${current===l.href?'nav-active':''}">${l.label}</a>`).join('')}
          </div>
        </div>
      </div>
      <div class="nav-cta">
        <a href="install.html" class="btn btn-outline btn-sm">Install</a>
        <a href="buddy.html" class="btn btn-primary btn-sm">Open Buddy</a>
      </div>
    </div>
  </div>
</nav>
<div class="site-preview-notice" role="status">
  <div class="container">
    <strong>Repository preview</strong>
    <span>Generated inventory is real repository data. Revenue, payment, task, and autonomy screens are demos unless connected to an approved backend.</span>
    <a href="system-map.html">View verified status</a>
  </div>
</div>`;
  const placeholder = document.getElementById('nav-placeholder');
  if (placeholder) placeholder.outerHTML = navHTML;
  if ('serviceWorker' in navigator && location.protocol !== 'file:') {
    window.addEventListener('load', () => { navigator.serviceWorker.register('service-worker.js', { scope: './' }).catch(() => {}); });
  }
  const style = document.createElement('style');
  style.textContent = `.nav-active { color: var(--text) !important; background: var(--card2) !important; border-radius: 8px; } .nav-more { position: relative; } .nav-more-menu { display: none; position: absolute; top: 100%; right: 0; background: var(--card); border: 1px solid var(--border); border-radius: 12px; padding: 8px; min-width: 220px; z-index: 200; } .nav-more-menu.open { display: block; }`;
  document.head.appendChild(style);
})();
function toggleMoreMenu(e) {
  e.preventDefault();
  document.getElementById('nav-more-menu').classList.toggle('open');
}
document.addEventListener('click', function(e) {
  const menu = document.getElementById('nav-more-menu');
  if (menu && !e.target.closest('.nav-more')) menu.classList.remove('open');
});
