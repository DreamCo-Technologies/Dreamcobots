/* Buddy OS syscalls on this device. GitHub is evidence, not the kernel. */
(function () {
  const C = window.BUDDY_CHAT;
  const KEY = "buddy.actions-os.mastery";
  const $ = (id) => document.getElementById(id);

  function loadM() {
    try { const rows = JSON.parse(localStorage.getItem(KEY) || "[]"); return Array.isArray(rows) ? rows : []; }
    catch { return []; }
  }
  function saveM(rows) { localStorage.setItem(KEY, JSON.stringify(rows.slice(0, 400))); }
  function mastered(id) { return loadM().some((m) => m.id === id); }

  function resources() {
    const kernel = C.syscalls.map((s) => ({ id: "k-" + s.id, name: s.title, kind: "kernel", group: "Kernel", href: "os.html", live: true, how: s.how }));
    const src = C.sources.map((s) => ({ id: "src-" + s.id, name: s.name, kind: "source", group: s.live ? "Sources" : "Sources (catalog only)", href: s.href, live: s.live, how: s.how }));
    const week = C.week.map((d) => ({ id: "week-" + d.day, name: "HF week day " + d.day + ": " + d.title, kind: "catalog", group: "Learn week", href: "learn-hf.html", live: true, how: d.thesis }));
    const groups = [...new Set(C.tasks.map((t) => t.group))].map((g) => ({ id: "tasks-" + g.toLowerCase(), name: "Hub tasks · " + g, kind: "catalog", group: "Dataset tasks", href: "hub.html", live: true, how: C.tasks.filter((t) => t.group === g).length + " task categories. Cards only." }));
    const paths = C.paths.map((p) => ({ id: "path-" + p.id, name: p.name, kind: "path", group: "Easier paths", href: "learn-hf.html", live: false, how: p.buddy }));
    const desks = C.desks.map((d) => ({ id: "desk-" + d.href.replace(/[^\w]+/g, "-"), name: d.label, kind: "desk", group: d.group, href: d.href, live: true, how: d.note }));
    return kernel.concat(src, week, groups, paths, desks);
  }

  function hunt(id) {
    const all = resources();
    const rows = loadM();
    const done = new Set(all.filter((r) => mastered(r.id)).map((r) => r.id));
    const current = all.find((r) => r.id === id);
    const hits = [];
    const push = (res, why) => { if (res && !done.has(res.id) && !hits.some((h) => h.id === res.id)) hits.push({ id: res.id, name: res.name, why, href: res.href }); };
    if (current) {
      const sib = all.filter((r) => r.group === current.group);
      const idx = sib.findIndex((r) => r.id === id);
      push(sib[idx + 1], "Next in " + current.group + " after " + current.name + ".");
    }
    all.filter((r) => r.group === "Sources (catalog only)" && !done.has(r.id)).slice(0, 3).forEach((r) => push(r, "In the repo catalog, not a live hook yet."));
    const weekGap = C.week.find((d) => !mastered("week-" + d.day));
    if (weekGap) push(all.find((r) => r.id === "week-" + weekGap.day), "Next evidenced HF week day.");
    all.filter((r) => r.kind === "path" && !done.has(r.id)).slice(0, 1).forEach((r) => push(r, "Easier model-build path still open."));
    if (!hits.length) all.filter((r) => !done.has(r.id)).slice(0, 4).forEach((r) => push(r, "Unmastered on this device."));
    return hits.slice(0, 8);
  }

  function secrets() {
    const hits = [];
    for (let i = 0; i < localStorage.length; i += 1) {
      const k = localStorage.key(i) || "";
      const v = localStorage.getItem(k) || "";
      if (/sk-|xai-|api[_-]?key|BEGIN (RSA |OPENSSH )?PRIVATE/i.test(v)) hits.push(k);
    }
    return hits;
  }

  function run(id) {
    const all = resources();
    const m = loadM();
    const t0 = performance.now();
    let out = {};
    if (id === "doctor") out = { online: navigator.onLine, lang: navigator.language, storage: localStorage.length, occupations: C.occupations.length, sources: C.sources.length, stripe: "off", keys_on_pages: false };
    else if (id === "test") { const hit = C.occupations.find((o) => o.keywords.includes("app") || o.title.includes("Software")); out = { occupation_match: hit ? hit.title : "none", tasks: C.tasks.length }; }
    else if (id === "lint") out = { tasks: C.tasks.length === 52, week: C.week.length === 7, mcp: C.mcp.length === 11 };
    else if (id === "security") out = { secret_keys: secrets(), money: "off", teacher_on_pages: false };
    else if (id === "benchmark") out = { resources: all.length, mastered: m.length, live: all.filter((r) => r.live).length };
    else if (id === "repair") out = { lanes: C.recovery.map((r) => r.id), auto_merge_main: false };
    else if (id === "pages") out = { desks: C.desks.length, home: "buddy.html", keys: "never" };
    else if (id === "bundle") out = { catalogs: ["tasks", "week", "sources", "mcp", "occupations"] };
    else if (id === "datasets") out = { indexed: (JSON.parse(localStorage.getItem("buddy.packages") || "[]") || []).length, rule: "cards only" };
    else if (id === "resources") out = { total: all.length, mastered: m.length };
    else if (id === "hunt") out = hunt(m[0] ? m[0].id : "k-doctor");
    else if (id === "tasks") out = { queued: (JSON.parse(localStorage.getItem("buddy.tasks.v1") || "[]") || []).length, mode: localStorage.getItem("buddy.work.mode") || "watch" };
    else out = { error: "unknown syscall" };
    return { syscall: id, ms: Math.round(performance.now() - t0), out };
  }

  function render() {
    const all = resources();
    const m = loadM();
    $("stat-res").textContent = String(all.length);
    $("stat-mastered").textContent = String(m.length);
    $("stat-open").textContent = String(all.length - m.length);
    $("os-syscalls").innerHTML = C.syscalls.map((s) =>
      `<article class="desk-card"><strong>${s.title}</strong><p>${s.how}</p><p>GitHub twin: ${s.twin}</p>
       <button type="button" class="primary" data-run="${s.id}">Run</button></article>`
    ).join("");
    const kind = $("os-kind").value;
    const rows = kind === "all" ? all : all.filter((r) => r.kind === kind);
    $("os-res").innerHTML = rows.map((r) =>
      `<article class="desk-card"><strong>${r.name}</strong><span class="desk-status ${mastered(r.id) ? "healthy" : r.live ? "watch" : "blocked"}">${mastered(r.id) ? "mastered" : r.live ? "live" : "catalog"}</span>
       <p>${r.how}</p>
       <div class="desk-actions">
         <a class="desk-btn" href="${r.href}">Open</a>
         <button type="button" data-master="${r.id}">Master</button>
       </div></article>`
    ).join("");
  }

  $("os-kind").addEventListener("change", render);
  document.addEventListener("click", (e) => {
    const t = e.target;
    if (!(t instanceof HTMLElement)) return;
    if (t.dataset.run) {
      const report = run(t.dataset.run);
      $("os-out").textContent = JSON.stringify(report, null, 2);
    }
    if (t.dataset.master) {
      const evidence = ($("os-evidence").value || "").trim();
      if (evidence.length < 8) { $("os-out").textContent = "Mastery needs evidence (≥ 8 characters)."; return; }
      const rows = loadM().filter((m) => m.id !== t.dataset.master);
      rows.unshift({ id: t.dataset.master, at: new Date().toISOString(), evidence: evidence.slice(0, 400) });
      saveM(rows);
      $("os-out").textContent = JSON.stringify({ mastered: t.dataset.master, next: hunt(t.dataset.master) }, null, 2);
      render();
    }
  });
  render();
})();
