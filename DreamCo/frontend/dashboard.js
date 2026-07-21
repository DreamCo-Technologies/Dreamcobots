/**
 * DreamCo LeadGenBot — Dashboard JavaScript
 *
 * Handles all frontend interactions:
 *   - Load and display leads from the backend API
 *   - Search and filter leads
 *   - Export leads as CSV
 *   - Trigger scrape requests
 *   - Add leads manually
 *   - Display active bots
 */

const API_BASE = '/api';

// ---------------------------------------------------------------------------
// State
// ---------------------------------------------------------------------------
let _allLeads = [];

// ---------------------------------------------------------------------------
// DOM helpers
// ---------------------------------------------------------------------------
const $ = (id) => document.getElementById(id);

function showToast(message, type = 'success') {
  const toast = $('toast');
  toast.textContent = message;
  toast.className = `toast toast--${type}`;
  toast.classList.remove('hidden');
  setTimeout(() => toast.classList.add('hidden'), 3500);
}

function showLoading(visible) {
  $('loadingIndicator').classList.toggle('hidden', !visible);
}

function showError(message) {
  const el = $('errorMessage');
  if (message) {
    el.textContent = message;
    el.classList.remove('hidden');
  } else {
    el.classList.add('hidden');
  }
}

function showModal(id) {
  $(id).classList.remove('hidden');
}

function hideModal(id) {
  $(id).classList.add('hidden');
}

// ---------------------------------------------------------------------------
// Leads
// ---------------------------------------------------------------------------

async function loadLeads(industry = '') {
  showLoading(true);
  showError('');
  try {
    const url = industry
      ? `${API_BASE}/leads?industry=${encodeURIComponent(industry)}`
      : `${API_BASE}/leads`;
    const res = await fetch(url);
    const data = await res.json();
    if (!data.success) {
      throw new Error(data.error || 'Unknown error');
    }
    _allLeads = data.leads || [];
    renderLeads(_allLeads);
    updateStats(_allLeads);
  } catch (err) {
    showError(`Failed to load leads: ${err.message}`);
  } finally {
    showLoading(false);
  }
}

function renderLeads(leads) {
  const tbody = $('leadsBody');
  if (!leads || leads.length === 0) {
    tbody.innerHTML =
      '<tr><td colspan="7" class="empty-state">No leads found. Click <strong>Scrape Leads</strong> to get started.</td></tr>';
    return;
  }

  tbody.innerHTML = leads
    .map(
      (lead) => `
    <tr>
      <td><strong>${escapeHtml(lead.name || '—')}</strong></td>
      <td><a href="mailto:${escapeHtml(lead.email || '')}">${escapeHtml(lead.email || '—')}</a></td>
      <td>${escapeHtml(lead.company || '—')}</td>
      <td><span class="industry-badge">${escapeHtml(lead.industry || '—')}</span></td>
      <td>${escapeHtml(lead.location || '—')}</td>
      <td><span class="score-badge score-${scoreClass(lead.score)}">${lead.score || '—'}</span></td>
      <td>${escapeHtml(lead.source || '—')}</td>
    </tr>
  `
    )
    .join('');
}

function updateStats(leads) {
  $('statTotal').textContent = leads.length;
  const avgScore = leads.length
    ? Math.round(leads.reduce((s, l) => s + (l.score || 0), 0) / leads.length)
    : 0;
  $('statAvgScore').textContent = avgScore;
  const industries = new Set(leads.map((l) => l.industry).filter(Boolean));
  $('statIndustries').textContent = industries.size;

  // "New this week" — leads created within the last 7 days
  const oneWeekAgo = Date.now() - 7 * 24 * 60 * 60 * 1000;
  const newLeads = leads.filter((l) => new Date(l.created_at).getTime() > oneWeekAgo);
  $('statNew').textContent = newLeads.length;
}

function scoreClass(score) {
  if (score >= 90) {
    return 'high';
  }
  if (score >= 70) {
    return 'medium';
  }
  return 'low';
}

function filterLeads() {
  const query = $('searchInput').value.toLowerCase();
  const industry = $('filterIndustry').value;
  let filtered = _allLeads;

  if (industry) {
    filtered = filtered.filter((l) => l.industry === industry);
  }
  if (query) {
    filtered = filtered.filter((l) =>
      [l.name, l.company, l.email, l.industry, l.location].some(
        (f) => f && f.toLowerCase().includes(query)
      )
    );
  }
  renderLeads(filtered);
}

// ---------------------------------------------------------------------------
// Export CSV
// ---------------------------------------------------------------------------

async function exportCSV() {
  try {
    const res = await fetch(`${API_BASE}/leads/export`);
    if (!res.ok) {
      const data = await res.json();
      throw new Error(data.error || 'Export failed');
    }
    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `dreamco_leads_${Date.now()}.csv`;
    a.click();
    URL.revokeObjectURL(url);
    showToast('✅ Leads exported successfully!');
  } catch (err) {
    showToast(`Export failed: ${err.message}`, 'error');
  }
}

// ---------------------------------------------------------------------------
// Scrape
// ---------------------------------------------------------------------------

async function triggerScrape() {
  const industry = $('scrapeIndustry').value;
  const count = parseInt($('scrapeCount').value, 10) || 50;
  hideModal('scrapeModal');
  showToast('🔍 Scraping leads…', 'info');

  try {
    const res = await fetch(`${API_BASE}/leads/scrape`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ industry, count }),
    });
    const data = await res.json();
    if (!data.success) {
      throw new Error(data.error || 'Scrape failed');
    }
    showToast(`✅ ${data.new_leads} new leads added! (${data.total} total)`);
    await loadLeads();
  } catch (err) {
    showToast(`Scrape failed: ${err.message}`, 'error');
  }
}

// ---------------------------------------------------------------------------
// Add Lead Manually
// ---------------------------------------------------------------------------

async function addLeadManually() {
  const name = $('addName').value.trim();
  const email = $('addEmail').value.trim();
  if (!name || !email) {
    showToast('Name and email are required.', 'error');
    return;
  }

  try {
    const res = await fetch(`${API_BASE}/leads`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        name,
        email,
        phone: $('addPhone').value.trim() || undefined,
        company: $('addCompany').value.trim() || undefined,
        industry: $('addIndustry').value,
        location: $('addLocation').value.trim() || undefined,
      }),
    });
    const data = await res.json();
    if (!data.success) {
      throw new Error(data.error || 'Failed to add lead');
    }
    hideModal('addLeadModal');
    showToast('✅ Lead added successfully!');
    // Reset form
    ['addName', 'addEmail', 'addPhone', 'addCompany', 'addLocation'].forEach((id) => {
      $(id).value = '';
    });
    await loadLeads();
  } catch (err) {
    showToast(`Error: ${err.message}`, 'error');
  }
}

// ---------------------------------------------------------------------------
// Bots
// ---------------------------------------------------------------------------

async function loadBots() {
  try {
    const res = await fetch(`${API_BASE}/bots`);
    const data = await res.json();
    if (!data.success) {
      throw new Error(data.error);
    }
    renderBots(data.bots || []);
  } catch {
    $('botsGrid').innerHTML = '<div class="error">Could not load bots.</div>';
  }
}

function renderBots(bots) {
  const grid = $('botsGrid');
  if (!bots.length) {
    grid.innerHTML =
      '<div class="empty-state">No bots yet. Click <strong>Create Bot</strong> to get started.</div>';
    return;
  }
  grid.innerHTML = bots
    .map(
      (bot) => `
    <div class="bot-card">
      <div class="bot-header">
        <span class="bot-icon">🤖</span>
        <span class="bot-name">${escapeHtml(bot.name)}</span>
        <span class="bot-status bot-status--${bot.status}">${bot.status}</span>
      </div>
      <p class="bot-desc">${escapeHtml(bot.description || '')}</p>
      <div class="bot-meta">
        <span class="bot-tier tier-${bot.tier}">${bot.tier}</span>
        <span class="bot-industry">${escapeHtml(bot.industry)}</span>
      </div>
      <div class="bot-features">
        ${(bot.features || []).map((f) => `<span class="feature-tag">${escapeHtml(f)}</span>`).join('')}
      </div>
    </div>
  `
    )
    .join('');
}

async function createBot() {
  const name = prompt('Enter bot name (e.g., LeadGenBot, RealEstateBot):');
  if (!name) {
    return;
  }
  const industry = prompt('Enter industry (e.g., Real Estate, Finance, General):', 'General');

  try {
    const res = await fetch(`${API_BASE}/bots`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, industry: industry || 'General' }),
    });
    const data = await res.json();
    if (!data.success) {
      throw new Error(data.error);
    }
    showToast(`✅ Bot "${data.bot.name}" created!`);
    await loadBots();
  } catch (err) {
    showToast(`Error: ${err.message}`, 'error');
  }
}

// ---------------------------------------------------------------------------
// Pricing
// ---------------------------------------------------------------------------

function handlePlanClick(plan) {
  if (plan === 'buy-leads') {
    const qty = prompt('How many leads would you like to purchase?', '10');
    if (!qty) {
      return;
    }
    showToast(
      `💳 Redirecting to checkout for ${qty} leads… (Stripe integration coming soon)`,
      'info'
    );
  } else {
    showToast(`💳 Redirecting to ${plan} plan checkout… (Stripe integration coming soon)`, 'info');
  }
}

// ---------------------------------------------------------------------------
// Utilities
// ---------------------------------------------------------------------------

function escapeHtml(str) {
  if (!str) {
    return '';
  }
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

// ---------------------------------------------------------------------------
// Event listeners
// ---------------------------------------------------------------------------

document.addEventListener('DOMContentLoaded', () => {
  // Initial data load
  loadLeads();
  loadBots();

  // Export CSV
  $('btnExport').addEventListener('click', exportCSV);

  // Open scrape modal
  $('btnScrape').addEventListener('click', () => showModal('scrapeModal'));
  $('btnScrapeCancelModal').addEventListener('click', () => hideModal('scrapeModal'));
  $('btnScrapeConfirm').addEventListener('click', triggerScrape);

  // Add lead modal
  $('btnAddLead').addEventListener('click', () => showModal('addLeadModal'));
  $('btnAddLeadCancel').addEventListener('click', () => hideModal('addLeadModal'));
  $('btnAddLeadConfirm').addEventListener('click', addLeadManually);

  // Search and filter
  $('searchInput').addEventListener('input', filterLeads);
  $('filterIndustry').addEventListener('change', filterLeads);

  // Bots
  $('btnCreateBot').addEventListener('click', createBot);

  // Pricing buttons
  document.querySelectorAll('.plan-btn').forEach((btn) => {
    btn.addEventListener('click', () => handlePlanClick(btn.dataset.plan));
  });

  // Close modals on backdrop click
  document.querySelectorAll('.modal').forEach((modal) => {
    modal.addEventListener('click', (e) => {
      if (e.target === modal) {
        modal.classList.add('hidden');
      }
    });
  });

  // Nav links
  document.querySelectorAll('.nav-link').forEach((link) => {
    link.addEventListener('click', (_e) => {
      document.querySelectorAll('.nav-link').forEach((l) => l.classList.remove('active'));
      link.classList.add('active');
    });
  });
});
