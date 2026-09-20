/* Complete a goal — O*NET first, cut middlemen. No recruiter story. */
(function () {
  const C = window.BUDDY_CHAT;
  const KEY = "buddy.goals.v1";
  const $ = (id) => document.getElementById(id);

  function load() {
    try { const rows = JSON.parse(localStorage.getItem(KEY) || "[]"); return Array.isArray(rows) ? rows : []; }
    catch { return []; }
  }
  function save(rows) { localStorage.setItem(KEY, JSON.stringify(rows.slice(0, 40))); }

  function match(goal, limit) {
    const tokens = goal.toLowerCase().split(/[^a-z0-9+]+/).filter((t) => t.length > 2);
    if (!tokens.length) return C.occupations.slice(0, limit).map((o) => Object.assign({ score: 0 }, o));
    return C.occupations.map((occ) => {
      const hay = `${occ.title} ${occ.dream} ${occ.keywords.join(" ")} ${occ.tasks.join(" ")} ${occ.division}`.toLowerCase();
      let score = 0;
      tokens.forEach((tok) => { if (occ.keywords.includes(tok)) score += 6; else if (hay.includes(tok)) score += 2; });
      return Object.assign({ score }, occ);
    }).filter((r) => r.score > 0).sort((a, b) => b.score - a.score).slice(0, limit);
  }

  function plan(goal, occ) {
    return {
      goal,
      occupation: occ.title,
      soc: occ.soc,
      dream: occ.dream,
      zone: occ.zone,
      division: occ.division,
      middlemenCut: occ.middlemen,
      tasks: occ.tasks,
      sources: C.sources.filter((s) => s.id === "onet" || s.id === "huggingface" || s.id === "github").map((s) => s.name),
      hubQuery: occ.hubQuery,
      autonomy: "Buddy plans and studies. You approve writes. Live money stays off.",
      steps: [
        { title: "Write done", detail: occ.dream + " for “" + goal + "”." },
        { title: "Stand in the occupation", detail: occ.soc + " " + occ.title + ". Zone " + occ.zone + "." },
        { title: "Cut the middlemen", detail: occ.middlemen.map((m) => "Skip " + m).join(". ") + "." },
        { title: "Hook licensed sources", detail: "O*NET catalog, Hub cards, GitHub evidence. No bulk download." },
        { title: "Queue a task", detail: "Use the Tasks desk. Watch or screen-off. Ping when done." }
      ]
    };
  }

  function renderSaved() {
    const rows = load();
    $("goal-saved").innerHTML = rows.map((r) =>
      `<article class="desk-card"><strong>${r.goal}</strong><p>${r.occupation} · ${r.soc}</p><p>Cut: ${r.middlemenCut.join(", ")}</p></article>`
    ).join("") || "<p class=\"desk-note\">No saved goals on this device.</p>";
    $("stat-occ").textContent = String(C.occupations.length);
    $("stat-saved").textContent = String(rows.length);
  }

  function show(p) {
    $("goal-out").innerHTML =
      `<article class="desk-card"><strong>${p.occupation}</strong><p>${p.soc} · ${p.division} · zone ${p.zone}</p>
       <p>${p.dream}</p><p><strong>Cut:</strong> ${p.middlemenCut.join(", ")}</p>
       <p>Hub query: ${p.hubQuery}</p><p>${p.autonomy}</p></article>` +
      p.steps.map((s) => `<div class="desk-step"><strong>${s.title}</strong><p>${s.detail}</p></div>`).join("");
  }

  $("goal-go").addEventListener("click", () => {
    const goal = $("goal-text").value.trim();
    if (!goal) return;
    const hits = match(goal, 4);
    if (!hits.length) { $("goal-out").innerHTML = "<p class=\"desk-note\">No occupation match. Try a work verb (ship, hire, file, teach).</p>"; return; }
    const p = plan(goal, hits[0]);
    const rows = load().filter((r) => r.goal !== goal);
    rows.unshift(p);
    save(rows);
    $("goal-alts").innerHTML = hits.slice(1).map((h) =>
      `<button type="button" data-soc="${h.soc}">${h.title}</button>`
    ).join("");
    show(p);
    renderSaved();
  });
  document.addEventListener("click", (e) => {
    const t = e.target;
    if (!(t instanceof HTMLElement) || !t.dataset.soc) return;
    const occ = C.occupations.find((o) => o.soc === t.dataset.soc);
    const goal = $("goal-text").value.trim();
    if (!occ || !goal) return;
    const p = plan(goal, occ);
    show(p);
  });
  $("goal-hub").addEventListener("click", () => {
    const q = ($("goal-text").value || "software").split(/\s+/).slice(0, 3).join(" ");
    location.href = "hub.html?q=" + encodeURIComponent(q);
  });
  $("goal-task").addEventListener("click", () => {
    const goal = $("goal-text").value.trim();
    location.href = "work.html?q=" + encodeURIComponent(goal || "Plan: ship an app without a staffing firm");
  });
  renderSaved();
})();
