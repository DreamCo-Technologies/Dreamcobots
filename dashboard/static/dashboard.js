/**
 * DreamCobots Dashboard JavaScript
 * Handles real-time metrics, bot status updates, and control actions.
 */

/* exported startBot, stopBot */

const REFRESH_INTERVAL = 3000;

/**
 * Format a number as a currency string.
 * @param {number} value
 * @returns {string}
 */
function formatCurrency(value) {
  return (
    '$' +
    parseFloat(value || 0)
      .toFixed(2)
      .replace(/\B(?=(\d{3})+(?!\d))/g, ',')
  );
}

/**
 * Format a UTC ISO timestamp to a local time string.
 * @param {string} isoString
 * @returns {string}
 */
function formatTime(isoString) {
  if (!isoString) {
    return '--:--:--';
  }
  try {
    return new Date(isoString).toLocaleTimeString();
  } catch (e) {
    return '--:--:--';
  }
}

/**
 * Fetch and update system resource metrics.
 */
async function fetchMetrics() {
  try {
    const response = await fetch('/api/metrics');
    const data = await response.json();

    const cpu = parseFloat(data.cpu_percent || 0).toFixed(1);
    const ram = parseFloat(data.ram_percent || 0).toFixed(1);
    const disk = parseFloat(data.disk_percent || 0).toFixed(1);

    document.getElementById('cpu-value').textContent = cpu + '%';
    document.getElementById('cpu-bar').style.width = cpu + '%';

    document.getElementById('ram-value').textContent = ram + '%';
    document.getElementById('ram-bar').style.width = ram + '%';

    const ramUsed = parseFloat(data.ram_used_gb || 0).toFixed(1);
    const ramTotal = parseFloat(data.ram_total_gb || 0).toFixed(1);
    document.getElementById('ram-detail').textContent = ramUsed + ' / ' + ramTotal + ' GB';

    document.getElementById('disk-value').textContent = disk + '%';
    document.getElementById('disk-bar').style.width = disk + '%';

    document.getElementById('last-updated').textContent =
      'Updated: ' + new Date().toLocaleTimeString();
  } catch (err) {
    console.warn('Metrics fetch failed:', err);
  }
}

/**
 * Start a bot by name.
 * @param {string} name
 */
async function startBot(name) {
  try {
    const response = await fetch('/api/bot/' + encodeURIComponent(name) + '/start', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
    });
    const data = await response.json();
    if (data.success) {
      addEventEntry('Bot started: ' + name);
      fetchBots();
    } else {
      addEventEntry('Failed to start ' + name + ': ' + (data.error || 'unknown error'));
    }
  } catch (err) {
    addEventEntry('Error starting bot: ' + name);
  }
}

/**
 * Stop a bot by name.
 * @param {string} name
 */
async function stopBot(name) {
  try {
    const response = await fetch('/api/bot/' + encodeURIComponent(name) + '/stop', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
    });
    const data = await response.json();
    if (data.success) {
      addEventEntry('Bot stopped: ' + name);
      fetchBots();
    } else {
      addEventEntry('Failed to stop ' + name + ': ' + (data.error || 'unknown error'));
    }
  } catch (err) {
    addEventEntry('Error stopping bot: ' + name);
  }
}

/**
 * Add an entry to the on-screen event log.
 * @param {string} message
 */
function addEventEntry(message) {
  const log = document.getElementById('event-log');
  const entry = document.createElement('div');
  entry.className = 'event-item';
  entry.innerHTML =
    '<span class="event-time">' + new Date().toLocaleTimeString() + '</span>' + message;
  log.insertBefore(entry, log.firstChild);
  while (log.children.length > 50) {
    log.removeChild(log.lastChild);
  }
}

/**
 * Build a bot card HTML string.
 * @param {Object} bot
 * @returns {string}
 */
function buildBotCard(bot) {
  const isRunning = bot.status === 'running';
  const statusClass = isRunning ? 'status-running' : 'status-stopped';
  const statusText = isRunning ? '● RUNNING' : '○ STOPPED';
  const cardClass = isRunning ? 'bot-card running' : 'bot-card';
  const revenue = formatCurrency(bot.revenue || 0);
  const desc = bot.description || 'AI Bot';
  const shortDesc = desc.length > 80 ? desc.substring(0, 77) + '...' : desc;
  const encodedName = encodeURIComponent(bot.name);

  return `
    <div class="${cardClass}">
        <div class="bot-header">
            <div class="bot-name">${bot.name}</div>
            <span class="bot-status ${statusClass}">${statusText}</span>
        </div>
        <div class="bot-description">${shortDesc}</div>
        <div class="bot-revenue">${revenue}</div>
        <div class="bot-actions">
            <button class="btn btn-start" onclick="startBot(decodeURIComponent('${encodedName}'))" ${isRunning ? 'disabled style="opacity:0.4"' : ''}>
                ▶ Start
            </button>
            <button class="btn btn-stop" onclick="stopBot(decodeURIComponent('${encodedName}'))" ${!isRunning ? 'disabled style="opacity:0.4"' : ''}>
                ■ Stop
            </button>
        </div>
    </div>`;
}

/**
 * Fetch and update the bots grid.
 */
async function fetchBots() {
  try {
    const response = await fetch('/api/bots');
    const data = await response.json();
    const bots = data.bots || [];

    const grid = document.getElementById('bots-grid');
    if (bots.length === 0) {
      grid.innerHTML =
        '<div class="loading">No bots registered. Start the platform to load bots.</div>';
      return;
    }

    grid.innerHTML = bots.map(buildBotCard).join('');

    const running = bots.filter((b) => b.status === 'running').length;
    document.getElementById('active-bots').textContent = running;
    document.getElementById('total-bots').textContent = 'of ' + bots.length + ' registered';
    document.getElementById('bots-count').textContent =
      running + ' running / ' + bots.length + ' total';
    const botsCountRev = document.getElementById('bots-count-rev');
    if (botsCountRev) {
      botsCountRev.textContent = bots.length;
    }
  } catch (err) {
    console.warn('Bots fetch failed:', err);
  }
}

/**
 * Fetch and update revenue information.
 */
async function updateRevenue() {
  try {
    const response = await fetch('/api/revenue');
    const data = await response.json();

    const total = data.total_revenue || 0;
    const clientShare = total * 0.5;

    document.getElementById('total-revenue').textContent = formatCurrency(total);
    document.getElementById('client-revenue').textContent = formatCurrency(clientShare);

    const botsCount = Object.keys(data.bot_revenues || {}).length;
    const el = document.getElementById('bots-count');
    if (el) {
      el.textContent = botsCount;
    }
  } catch (err) {
    console.warn('Revenue fetch failed:', err);
  }
}

/**
 * Fetch and update the event log.
 */
async function fetchEvents() {
  try {
    const response = await fetch('/api/events');
    const data = await response.json();
    const events = data.events || [];

    if (events.length > 0) {
      const log = document.getElementById('event-log');
      const fragment = document.createDocumentFragment();
      events
        .slice(-20)
        .reverse()
        .forEach((e) => {
          const entry = document.createElement('div');
          entry.className = 'event-item';
          const time = formatTime(e.timestamp);
          const msg = e.message || e.event || JSON.stringify(e);
          entry.innerHTML = '<span class="event-time">' + time + '</span>' + msg;
          fragment.appendChild(entry);
        });
      log.innerHTML = '';
      log.appendChild(fragment);
    }
  } catch (err) {
    console.warn('Events fetch failed:', err);
  }
}

/**
 * Update all dashboard data.
 */
async function updateAll() {
  await Promise.all([fetchMetrics(), fetchBots(), updateRevenue(), fetchEvents()]);
}

// Handle missing bots-count-rev element gracefully
document.addEventListener('DOMContentLoaded', function () {
  if (!document.getElementById('bots-count-rev')) {
    const el = document.getElementById('bots-count');
    if (el) {
      el.id = 'bots-count-rev';
    }
  }

  updateAll();
  setInterval(updateAll, REFRESH_INTERVAL);
});
