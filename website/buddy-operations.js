(function () {
  'use strict';
  const host = document.getElementById('buddy-operations');
  if (!host) return;
  const base = 'https://github.com/DreamCo-Technologies/Dreamcobots';
  const stamp = document.getElementById('ops-status');
  const list = document.getElementById('ops-list');
  const session = document.getElementById('ops-session');
  let generation = 0;
  function showSession(data) {
    session.textContent = `Browser session ${data.id.slice(0, 8)} · ${data.events.length} UI events · ${data.storage ? 'saved on this browser' : 'memory only'}. This log proves no runtime execution.`;
  }
  showSession(BuddySession.snapshot());
  BuddySession.subscribe(showSession);
  function card(title, detail, href) {
    const article = document.createElement('article'); article.className = 'desk-card';
    const link = document.createElement('a'); link.textContent = title; link.href = href;
    const note = document.createElement('p'); note.textContent = detail;
    article.append(link, note); list.append(article);
  }
  async function refresh() {
    const view = ['issues', 'agents', 'pulls'].includes(location.hash.slice(1)) ? location.hash.slice(1) : 'issues';
    const ticket = ++generation;
    BuddySession.emit('context.updated', view);
    list.replaceChildren(); stamp.textContent = 'Loading evidence…';
    const endpoint = view === 'agents' ? 'data/fleet-runtime-status.json' : `https://api.github.com/repos/DreamCo-Technologies/Dreamcobots/${view}?state=open&per_page=30&sort=updated&direction=desc`;
    try {
      const response = await fetch(endpoint, { cache: 'no-store', signal: AbortSignal.timeout(15000) });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const data = await response.json();
      if (ticket !== generation) return;
      if (view === 'agents') {
        if (!Array.isArray(data.bots)) throw new Error('Fleet evidence unavailable');
        for (const bot of data.bots.slice(0, 30)) card(bot.name || bot.slug, `${bot.state || 'UNKNOWN'} · ${bot.division || 'unassigned'} · repository snapshot; live health unknown`, 'fleet-runtime.html');
        stamp.textContent = `Showing first ${Math.min(30, data.bots.length)} of ${data.bots.length} catalog entries. Open Fleet Truth for the full registry and repair gaps. No active-agent claim.`;
      } else {
        if (!Array.isArray(data)) throw new Error('Invalid GitHub response');
        const rows = view === 'issues' ? data.filter(row => !row.pull_request) : data;
        for (const row of rows) {
          if (!Number.isSafeInteger(row.number) || row.number < 1) continue;
          card(`#${row.number} ${row.title}`, `${row.state} · updated ${row.updated_at}`, `${base}/${view === 'pulls' ? 'pull' : 'issues'}/${row.number}`);
        }
        stamp.textContent = `${rows.length} ${view} in this bounded GitHub response; not a repository total. Retrieved ${new Date().toISOString()}. ${rows.length ? '' : 'No matching entries in this response.'}`;
      }
    } catch (error) {
      if (ticket !== generation) return;
      stamp.textContent = `UNKNOWN — ${error.message}. Use the GitHub or Fleet Truth links; unavailable evidence is not a pass.`;
      BuddySession.emit('action.failed', view);
    }
  }
  document.getElementById('ops-refresh').addEventListener('click', refresh);
  rootHash();
  function rootHash() { addEventListener('hashchange', refresh); refresh(); }
})();
