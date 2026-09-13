(() => {
  'use strict';
  const $ = (id) => document.getElementById(id);
  const esc = (value) => String(value ?? '').replace(/[&<>"']/g, (character) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[character]));
  const state = { divisions: [], fleet: null, active: null };

  function missionFor(division) {
    const bots = state.fleet.bots.filter((bot) => bot.identity.division === division.name);
    const capabilities = bots.flatMap((bot) => String(bot.capability_search || '').split(' · ')).filter(Boolean);
    return capabilities.slice(0, 5).join(' · ') || 'Specialist task routing, local planning, evidence, and governed execution.';
  }

  function render() {
    const query = $('division-search').value.trim().toLowerCase();
    const rows = state.divisions.filter((division) => !query || `${division.name} ${division.bot_ids.join(' ')} ${missionFor(division)}`.toLowerCase().includes(query));
    $('division-count').textContent = `${rows.length} of ${state.divisions.length} divisions shown`;
    $('divisions-grid').innerHTML = rows.map((division) => {
      const summary = state.fleet.divisions.find((item) => item.name === division.name) || {};
      return `<article class="division-card"><span class="division-status">${esc(division.status)} · specialist division</span><h2>${esc(division.name)}</h2><p>${esc(missionFor(division))}</p><div class="division-metrics"><span><strong>${division.bot_ids.length}</strong> bots</span><span><strong>${summary.api_candidate_count || 0}</strong> API candidates</span></div><div class="division-actions"><button class="btn btn-outline" type="button" data-division-prospectus="${esc(division.name)}">Prospectus + questionnaire</button><a class="btn btn-primary" href="bots.html?div=${encodeURIComponent(division.name)}">Open specialists</a></div></article>`;
    }).join('') || '<p>No division matches that search.</p>';
  }

  function openProspectus(name) {
    const division = state.divisions.find((item) => item.name === name);
    const summary = state.fleet.divisions.find((item) => item.name === name) || {};
    if (!division) return;
    state.active = division;
    $('division-dialog-content').innerHTML = `<p class="division-status">${esc(division.status)} · repository evidence</p><h2>${esc(division.name)} prospectus</h2><p>${esc(missionFor(division))}</p><dl><dt>Registered specialists</dt><dd>${division.bot_ids.length}</dd><dt>API candidates</dt><dd>${summary.api_candidate_count || 0} · candidates are not live connections</dd><dt>Registry source</dt><dd>${esc(summary.source || division.source_refs.join(', '))}</dd><dt>Evidence</dt><dd>${esc(division.evidence_refs.join(', '))}</dd></dl><h3>Specialist roster</h3><div class="division-roster">${division.bot_ids.map((slug) => `<a href="bots.html?prospectus=${encodeURIComponent(slug)}">${esc(slug)}</a>`).join('')}</div><h3>Can this division help?</h3><form id="division-questionnaire"><textarea name="goal" required minlength="5" placeholder="What do you need this division to accomplish?"></textarea><input name="outcome" required placeholder="Required finished result" /><input name="constraints" placeholder="Budget, deadline, privacy, location, or tools" /><select name="mode"><option value="local_only">Local only</option><option value="hybrid">Local first + approved online handoffs</option></select><button class="btn btn-primary" type="submit">Prepare division task</button><a id="division-buddy-link" class="btn btn-outline" href="buddy.html">Open with Buddy</a><p id="division-questionnaire-status">No task packet prepared.</p></form>`;
    $('division-dialog').showModal();
  }

  Promise.all([
    fetch('data/command-center/divisions.json', { cache: 'no-store' }).then((response) => response.json()),
    fetch('data/bot-fleet-catalog.json', { cache: 'no-store' }).then((response) => response.json()),
  ]).then(([divisions, fleet]) => {
    state.divisions = divisions.items;
    state.fleet = fleet;
    $('division-summary').textContent = `${divisions.summary.registered_divisions} implemented divisions · ${fleet.summary.profiles.toLocaleString()} specialist bot profiles · prospectus and local questionnaire for every division`;
    render();
  }).catch((error) => { $('division-summary').textContent = `Division registry unavailable: ${error.message}`; });

  $('division-search').addEventListener('input', render);
  $('divisions-grid').addEventListener('click', (event) => {
    const button = event.target.closest('[data-division-prospectus]');
    if (button) openProspectus(button.dataset.divisionProspectus);
  });
  $('close-division-dialog').addEventListener('click', () => $('division-dialog').close());
  $('division-dialog').addEventListener('click', (event) => { if (event.target === $('division-dialog')) $('division-dialog').close(); });
  $('division-dialog-content').addEventListener('submit', (event) => {
    if (event.target.id !== 'division-questionnaire') return;
    event.preventDefault();
    const data = new FormData(event.target);
    const goal = String(data.get('goal') || '').trim();
    const outcome = String(data.get('outcome') || '').trim();
    const constraints = String(data.get('constraints') || '').trim();
    const mode = String(data.get('mode') || 'local_only');
    const prompt = `Route this task through the ${state.active.name} specialist division. Goal: ${goal}. Required result: ${outcome}. Constraints: ${constraints || 'none stated'}. Mode: ${mode}. Match the smallest qualified specialist team from ${state.active.bot_ids.join(', ')}. Start locally, preserve evidence, and require a verified adapter plus exact approval before any online write, account action, purchase, or publish step.`;
    $('division-buddy-link').href = `buddy.html?prompt=${encodeURIComponent(prompt)}`;
    $('division-questionnaire-status').textContent = `${state.active.name} task packet ready. Open it with Buddy to route the registered specialists.`;
  });
})();
