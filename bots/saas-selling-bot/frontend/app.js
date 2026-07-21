/**
 * SaaSBot – Frontend Application Logic
 * Handles API calls, rendering, search/filter, chat, and modals.
 */

// ─────────────────────────────────────────────────────────────
// Configuration
// ─────────────────────────────────────────────────────────────
const API_BASE = window.location.origin;
const PAGE_SIZE = 24;

// ─────────────────────────────────────────────────────────────
// State
// ─────────────────────────────────────────────────────────────
let allTools = [];
let filteredTools = [];
let displayedCount = 0;
let chatHistory = [];
let selectedPlan = 'free';

// ─────────────────────────────────────────────────────────────
// Category metadata
// ─────────────────────────────────────────────────────────────
const CATEGORY_META = {
  Analytics: { icon: '📊', color: '#6366f1' },
  Marketing: { icon: '📣', color: '#ec4899' },
  Development: { icon: '💻', color: '#0ea5e9' },
  Collaboration: { icon: '🤝', color: '#f59e0b' },
  Finance: { icon: '💰', color: '#22c55e' },
  AI: { icon: '🤖', color: '#8b5cf6' },
};

function categoryIcon(cat) {
  return (CATEGORY_META[cat] || { icon: '🔧' }).icon;
}

// ─────────────────────────────────────────────────────────────
// Fetch helpers
// ─────────────────────────────────────────────────────────────
async function apiFetch(path, options = {}) {
  const res = await fetch(API_BASE + path, options);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

// ─────────────────────────────────────────────────────────────
// Initialisation
// ─────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', async () => {
  await Promise.all([loadCategories(), loadTools(), loadPlans()]);
  setupSearch();
  setupFilters();
  updateHeroStats();
  initHamburger();
});

// ─────────────────────────────────────────────────────────────
// Load & Render Categories
// ─────────────────────────────────────────────────────────────
async function loadCategories() {
  try {
    const data = await apiFetch('/api/categories');
    const grid = document.getElementById('categoryGrid');
    const filterSelect = document.getElementById('categoryFilter');

    // Clear "All" option already in HTML then add categories
    filterSelect.innerHTML = '<option value="">All Categories</option>';

    grid.innerHTML = '';
    // Add "All" tile first
    const allTile = createCategoryCard({ category: 'All', count: 0 }, true);
    allTile.classList.add('active');
    grid.appendChild(allTile);

    data.categories.forEach((cat) => {
      grid.appendChild(createCategoryCard(cat));
      const opt = document.createElement('option');
      opt.value = cat.category;
      opt.textContent = `${cat.category} (${cat.count})`;
      filterSelect.appendChild(opt);
    });
  } catch (e) {
    console.error('Failed to load categories', e);
  }
}

function createCategoryCard(cat, isAll = false) {
  const icon = isAll ? '🌐' : categoryIcon(cat.category);
  const card = document.createElement('div');
  card.className = 'category-card';
  card.innerHTML = `
    <div class="category-icon">${icon}</div>
    <div class="category-name">${cat.category}</div>
    <div class="category-count">${isAll ? 'All tools' : cat.count + ' tools'}</div>
  `;
  card.addEventListener('click', () => {
    document.querySelectorAll('.category-card').forEach((c) => c.classList.remove('active'));
    card.classList.add('active');
    const select = document.getElementById('categoryFilter');
    select.value = isAll ? '' : cat.category;
    filterAndRender();
    document.getElementById('tools').scrollIntoView({ behavior: 'smooth' });
  });
  return card;
}

// ─────────────────────────────────────────────────────────────
// Load & Render Tools
// ─────────────────────────────────────────────────────────────
async function loadTools() {
  try {
    const data = await apiFetch('/api/tools');
    allTools = data.tools;
    filteredTools = [...allTools];
    renderTools(true);
  } catch (e) {
    document.getElementById('toolsGrid').innerHTML =
      '<p class="loader">Failed to load tools. Make sure the API server is running.</p>';
  }
}

function renderTools(reset = false) {
  const grid = document.getElementById('toolsGrid');
  const loader = document.getElementById('toolsLoader');

  if (reset) {
    displayedCount = 0;
    grid.innerHTML = '';
    if (loader) loader.remove();
  }

  if (filteredTools.length === 0) {
    grid.innerHTML = '<p class="loader">No tools found. Try a different search.</p>';
    document.getElementById('loadMoreWrap').style.display = 'none';
    document.getElementById('resultsCount').textContent = '0 results';
    return;
  }

  const chunk = filteredTools.slice(displayedCount, displayedCount + PAGE_SIZE);
  chunk.forEach((tool) => grid.appendChild(createToolCard(tool)));
  displayedCount += chunk.length;

  const count = filteredTools.length;
  document.getElementById('resultsCount').textContent =
    `Showing ${Math.min(displayedCount, count)} of ${count} tool${count !== 1 ? 's' : ''}`;

  const wrap = document.getElementById('loadMoreWrap');
  wrap.style.display = displayedCount < filteredTools.length ? 'block' : 'none';
}

function createToolCard(tool) {
  const card = document.createElement('div');
  card.className = 'tool-card';
  const icon = categoryIcon(tool.category);
  card.innerHTML = `
    <div class="tool-card-header">
      <div class="tool-name">${escHtml(tool.name)}</div>
      <span class="tool-category-badge">${escHtml(tool.category)}</span>
    </div>
    <p class="tool-description">${escHtml(tool.description)}</p>
    <span class="tool-pricing">💚 ${escHtml(tool.pricing)}</span>
    <div class="tool-actions">
      <button class="btn btn-outline" onclick="openToolDetail(${tool.id})">Details</button>
      <a class="btn btn-primary" href="/api/affiliate/click/${tool.id}" target="_blank"
         onclick="trackClick(${tool.id})">Get Tool →</a>
    </div>
  `;
  return card;
}

function loadMore() {
  renderTools(false);
}

// ─────────────────────────────────────────────────────────────
// Search & Filter
// ─────────────────────────────────────────────────────────────
function setupSearch() {
  const input = document.getElementById('searchInput');
  const clearBtn = document.getElementById('clearSearch');

  let debounceTimer;
  input.addEventListener('input', () => {
    clearBtn.style.display = input.value ? 'block' : 'none';
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(filterAndRender, 250);
  });
}

function setupFilters() {
  document.getElementById('categoryFilter').addEventListener('change', () => {
    // Sync category cards
    const val = document.getElementById('categoryFilter').value;
    document.querySelectorAll('.category-card').forEach((c) => {
      const name = c.querySelector('.category-name').textContent;
      c.classList.toggle('active', val === '' ? name === 'All' : name === val);
    });
    filterAndRender();
  });

  document.getElementById('sortSelect').addEventListener('change', filterAndRender);
}

function filterAndRender() {
  const query = document.getElementById('searchInput').value.toLowerCase();
  const category = document.getElementById('categoryFilter').value;
  const sort = document.getElementById('sortSelect').value;

  filteredTools = allTools.filter((t) => {
    const matchesQuery =
      !query ||
      t.name.toLowerCase().includes(query) ||
      t.description.toLowerCase().includes(query) ||
      t.category.toLowerCase().includes(query);
    const matchesCategory = !category || t.category === category;
    return matchesQuery && matchesCategory;
  });

  if (sort === 'category') {
    filteredTools.sort(
      (a, b) => a.category.localeCompare(b.category) || a.name.localeCompare(b.name)
    );
  } else {
    filteredTools.sort((a, b) => a.name.localeCompare(b.name));
  }

  renderTools(true);
}

function clearSearch() {
  document.getElementById('searchInput').value = '';
  document.getElementById('clearSearch').style.display = 'none';
  filterAndRender();
}

// ─────────────────────────────────────────────────────────────
// Hero stats
// ─────────────────────────────────────────────────────────────
function updateHeroStats() {
  const el = document.getElementById('statTools');
  if (el && allTools.length > 0) el.textContent = allTools.length + '+';
}

// ─────────────────────────────────────────────────────────────
// Pricing
// ─────────────────────────────────────────────────────────────
async function loadPlans() {
  try {
    const data = await apiFetch('/api/plans');
    renderPlans(data.plans);
  } catch (e) {
    console.error('Failed to load plans', e);
  }
}

function renderPlans(plans) {
  const grid = document.getElementById('pricingGrid');
  if (!grid) return;
  grid.innerHTML = '';
  plans.forEach((plan, i) => {
    const featured = plan.id === 'pro';
    const card = document.createElement('div');
    card.className = 'pricing-card' + (featured ? ' featured' : '');
    card.innerHTML = `
      ${featured ? '<div class="featured-badge">Most Popular</div>' : ''}
      <div class="plan-name">${escHtml(plan.name)}</div>
      <div class="plan-price">
        <span class="amount">$${plan.price_usd}</span>
        <span class="period">${plan.price_usd === 0 ? ' forever' : '/month'}</span>
      </div>
      <ul class="plan-features">
        ${plan.features.map((f) => `<li>${escHtml(f)}</li>`).join('')}
      </ul>
      <button class="btn ${featured ? 'btn-primary' : 'btn-outline'} btn-full"
              onclick="openSubscribeModal('${plan.id}')">
        ${plan.price_usd === 0 ? 'Start Free' : 'Get Started'}
      </button>
    `;
    grid.appendChild(card);
  });
}

// ─────────────────────────────────────────────────────────────
// AI Chat
// ─────────────────────────────────────────────────────────────
async function sendMessage() {
  const input = document.getElementById('chatInput');
  const message = input.value.trim();
  if (!message) return;

  input.value = '';
  appendMessage('user', message);
  chatHistory.push({ role: 'user', content: message });

  const loadingId = appendMessage('bot', 'Thinking…', true);

  try {
    const data = await apiFetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message, history: chatHistory }),
    });
    removeMessage(loadingId);
    appendMessage('bot', data.response);
    chatHistory.push({ role: 'assistant', content: data.response });
  } catch (e) {
    removeMessage(loadingId);
    appendMessage('bot', 'Sorry, I encountered an error. Please try again.');
  }
}

function setQuery(q) {
  document.getElementById('chatInput').value = q;
  sendMessage();
  document.getElementById('chat').scrollIntoView({ behavior: 'smooth' });
}

let msgIdCounter = 0;
function appendMessage(role, text, isLoading = false) {
  const id = ++msgIdCounter;
  const messages = document.getElementById('chatMessages');
  const div = document.createElement('div');
  div.className = 'message ' + (role === 'user' ? 'user-message' : 'bot-message');
  div.dataset.id = id;
  div.innerHTML = `
    <div class="message-avatar">${role === 'user' ? '👤' : '🤖'}</div>
    <div class="message-bubble${isLoading ? ' loading' : ''}">${markdownToHtml(text)}</div>
  `;
  messages.appendChild(div);
  messages.scrollTop = messages.scrollHeight;
  return id;
}

function removeMessage(id) {
  const el = document.querySelector(`[data-id="${id}"]`);
  if (el) el.remove();
}

// ─────────────────────────────────────────────────────────────
// Affiliate tracking (client-side signal)
// ─────────────────────────────────────────────────────────────
function trackClick(toolId) {
  // The actual redirect & tracking is handled server-side via /api/affiliate/click/<id>
  console.log(`Tracking affiliate click for tool ${toolId}`);
}

// ─────────────────────────────────────────────────────────────
// Tool Detail Modal
// ─────────────────────────────────────────────────────────────
async function openToolDetail(toolId) {
  const modal = document.getElementById('toolModal');
  const content = document.getElementById('toolModalContent');
  content.innerHTML = '<p>Loading…</p>';
  modal.classList.add('open');

  try {
    const tool = await apiFetch(`/api/tools/${toolId}`);
    const icon = categoryIcon(tool.category);
    content.innerHTML = `
      <div class="tool-detail-header">
        <div class="tool-detail-icon">${icon}</div>
        <div>
          <div class="tool-detail-name">${escHtml(tool.name)}</div>
          <div class="tool-detail-cat">${escHtml(tool.category)}</div>
        </div>
      </div>
      <p class="tool-detail-desc">${escHtml(tool.description)}</p>
      <div class="tool-detail-meta">
        <div class="meta-item"><strong>Pricing</strong>${escHtml(tool.pricing)}</div>
        ${tool.api_url ? `<div class="meta-item"><strong>API Docs</strong><a href="${escHtml(tool.api_url)}" target="_blank">View →</a></div>` : ''}
        ${tool.docs_url ? `<div class="meta-item"><strong>Documentation</strong><a href="${escHtml(tool.docs_url)}" target="_blank">View →</a></div>` : ''}
      </div>
      <div class="tool-detail-actions">
        <a class="btn btn-primary" href="/api/affiliate/click/${tool.id}" target="_blank">
          Get ${escHtml(tool.name)} →
        </a>
        ${tool.docs_url ? `<a class="btn btn-outline" href="${escHtml(tool.docs_url)}" target="_blank">Docs</a>` : ''}
        <button class="btn btn-secondary" onclick="setQuery('Tell me more about ${escHtml(tool.name)}'); closeToolModal();">Ask AI</button>
      </div>
    `;
  } catch (e) {
    content.innerHTML = '<p>Failed to load tool details.</p>';
  }
}

function closeToolModal(event) {
  if (event && event.target !== document.getElementById('toolModal')) return;
  document.getElementById('toolModal').classList.remove('open');
}

// ─────────────────────────────────────────────────────────────
// Subscribe Modal
// ─────────────────────────────────────────────────────────────
async function openSubscribeModal(preselectedPlan = 'free') {
  selectedPlan = preselectedPlan;
  const modal = document.getElementById('subscribeModal');
  const planOptions = document.getElementById('planOptions');
  planOptions.innerHTML = '';
  document.getElementById('subscribeMessage').textContent = '';

  try {
    const data = await apiFetch('/api/plans');
    data.plans.forEach((plan) => {
      const div = document.createElement('div');
      div.className = 'plan-option' + (plan.id === selectedPlan ? ' selected' : '');
      div.innerHTML = `
        <div class="plan-option-name">${escHtml(plan.name)}</div>
        <div class="plan-option-price">$${plan.price_usd}${plan.price_usd === 0 ? '' : '/mo'}</div>
      `;
      div.addEventListener('click', () => {
        selectedPlan = plan.id;
        document.querySelectorAll('.plan-option').forEach((p) => p.classList.remove('selected'));
        div.classList.add('selected');
      });
      planOptions.appendChild(div);
    });
  } catch (e) {
    planOptions.innerHTML = '<p class="text-muted">Could not load plans.</p>';
  }

  modal.classList.add('open');
}

function closeSubscribeModal(event) {
  if (event && event.target !== document.getElementById('subscribeModal')) return;
  document.getElementById('subscribeModal').classList.remove('open');
}

async function submitSubscription() {
  const email = document.getElementById('subEmail').value.trim();
  const msgEl = document.getElementById('subscribeMessage');

  if (!email || !email.includes('@')) {
    msgEl.textContent = 'Please enter a valid email address.';
    msgEl.style.color = 'var(--danger)';
    return;
  }

  msgEl.textContent = 'Processing…';
  msgEl.style.color = 'var(--text-muted)';

  try {
    const data = await apiFetch('/api/subscribe', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, plan: selectedPlan }),
    });

    if (data.success) {
      if (data.url) {
        window.location.href = data.url;
      } else {
        msgEl.textContent = '🎉 ' + (data.message || 'Subscribed successfully!');
        msgEl.style.color = 'var(--success)';
        setTimeout(closeSubscribeModal, 2000);
      }
    } else {
      msgEl.textContent = data.error || 'Something went wrong.';
      msgEl.style.color = 'var(--danger)';
    }
  } catch (e) {
    msgEl.textContent = 'Network error. Please try again.';
    msgEl.style.color = 'var(--danger)';
  }
}

// ─────────────────────────────────────────────────────────────
// Mobile nav
// ─────────────────────────────────────────────────────────────
function initHamburger() {
  document.getElementById('hamburger').addEventListener('click', () => {
    document.getElementById('mobileNav').classList.toggle('open');
  });
}
function closeMobileNav() {
  document.getElementById('mobileNav').classList.remove('open');
}

// ─────────────────────────────────────────────────────────────
// Utilities
// ─────────────────────────────────────────────────────────────
function escHtml(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function markdownToHtml(text) {
  if (!text) return '';
  // Basic markdown: bold, links, line breaks
  return escHtml(text)
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener">$1</a>')
    .replace(/\n/g, '<br/>');
}
