// DreamCo Empire OS — Shared Navigation
(function() {
  const current = location.pathname.split('/').pop() || 'index.html';
  const links = [
    { href: 'dashboard.html', label: '📊 Dashboard' },
    { href: 'buddy.html', label: '🧠 Buddy Bot' },
    { href: 'studio.html', label: '🎮 Creative Studio' },
    { href: 'divisions.html', label: '🏛️ Divisions' },
    { href: 'bots.html', label: '🤖 Bot Fleet' },
    { href: 'chat.html', label: '💬 Chat' },
    { href: 'autonomy.html', label: '⚡ Autonomy' },
    { href: 'ecosystem.html', label: '🌐 Ecosystem' },
    { href: 'orchestration.html', label: '🎛️ Orchestration' },
    { href: 'marketplace.html', label: '🛍️ Marketplace' },
    { href: 'formulas.html', label: '🔢 Formulas' },
    { href: 'deals.html', label: '🏠 Deals' },
    { href: 'debug.html', label: '🛠️ Debug' },
    { href: 'connections.html', label: '🔗 Connections' },
    { href: 'models.html', label: '🤖 AI Models' },
    { href: 'leaders.html', label: '🏆 AI Leaders' },
    { href: 'learning.html', label: '📚 Learning' },
    { href: 'timecapsule.html', label: '⏱️ Time Capsule' },
    { href: 'costs.html', label: '💲 Cost Tracking' },
    { href: 'revenue.html', label: '💰 Revenue' },
    { href: 'settings.html', label: '⚙️ Settings' },
  ];
  const navHTML = `
<nav>
  <div class="container">
    <div class="nav-inner">
      <a href="buddy.html" class="nav-brand">
        <div class="nav-logo">⚡</div>
        <span>DreamCo <strong>Empire OS</strong></span>
      </a>
      <div class="nav-links" id="nav-links-desktop">
        ${links.slice(0,9).map(l=>`<a href="${l.href}" class="${current===l.href?'nav-active':''}">${l.label}</a>`).join('')}
        <div class="nav-more">
          <a href="#" class="nav-more-btn" onclick="toggleMoreMenu(event)">More ▾</a>
          <div class="nav-more-menu" id="nav-more-menu">
            ${links.slice(9).map(l=>`<a href="${l.href}">${l.label}</a>`).join('')}
          </div>
        </div>
      </div>
      <div class="nav-cta">
        <a href="pricing.html" class="btn btn-outline btn-sm">Plans</a>
        <a href="buddy.html" class="btn btn-primary btn-sm">Open Buddy</a>
      </div>
    </div>
  </div>
</nav>`;
  const placeholder = document.getElementById('nav-placeholder');
  if (placeholder) placeholder.outerHTML = navHTML;

  const style = document.createElement('style');
  style.textContent = `
    .nav-active { color: var(--text) !important; background: var(--card2) !important; border-radius: 8px; }
    .nav-more { position: relative; }
    .nav-more-btn { cursor: pointer; }
    .nav-more-menu { display: none; position: absolute; top: 100%; right: 0; background: var(--card); border: 1px solid var(--border); border-radius: 12px; padding: 8px; min-width: 220px; z-index: 200; box-shadow: var(--shadow2); }
    .nav-more-menu a { display: block; padding: 8px 14px; border-radius: 8px; font-size: .83rem; color: var(--text2); transition: all .15s; }
    .nav-more-menu a:hover { background: var(--card2); color: var(--text); }
    .nav-more-menu.open { display: block; }
  `;
  document.head.appendChild(style);
  if (!document.querySelector('script[data-buddy-site-sync]')) {
    const syncScript = document.createElement('script');
    syncScript.src = 'buddy-site-sync.js';
    syncScript.defer = true;
    syncScript.dataset.buddySiteSync = 'true';
    document.body.appendChild(syncScript);
  }
})();

function toggleMoreMenu(e) {
  e.preventDefault();
  document.getElementById('nav-more-menu').classList.toggle('open');
}
document.addEventListener('click', function(e) {
  const menu = document.getElementById('nav-more-menu');
  if (menu && !e.target.closest('.nav-more')) menu.classList.remove('open');
});
