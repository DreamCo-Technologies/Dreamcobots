/* Tasks desk — device / internet / API / MCP. Watch or screen-off. No keys. */
(function () {
  const C = window.BUDDY_CHAT;
  const TASKS_KEY = "buddy.tasks.v1";
  const MODE_KEY = "buddy.work.mode";
  const LOG_KEY = "buddy.work.log";
  const $ = (id) => document.getElementById(id);
  let wake = null;

  function sid(prefix) {
    return `${prefix}-${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 7)}`;
  }
  function loadTasks() {
    try {
      const rows = JSON.parse(localStorage.getItem(TASKS_KEY) || "[]");
      return Array.isArray(rows) ? rows : [];
    } catch { return []; }
  }
  function saveTasks(rows) { localStorage.setItem(TASKS_KEY, JSON.stringify(rows.slice(0, 40))); }
  function mode() {
    const v = localStorage.getItem(MODE_KEY);
    if (v === "idle" || v === "off") return "off";
    if (v === "either") return "either";
    return "watch";
  }
  function setMode(v) { localStorage.setItem(MODE_KEY, v); }
  function log(line) {
    const next = (localStorage.getItem(LOG_KEY) || "Task desk. Watch, screen off, or either. A closed laptop is not a worker.\n") + line;
    localStorage.setItem(LOG_KEY, next.slice(-12000));
    return next;
  }

  function matchOcc(text) {
    const tokens = text.toLowerCase().split(/[^a-z0-9+]+/).filter((t) => t.length > 2);
    if (!tokens.length) return C.occupations[0];
    return C.occupations.map((occ) => {
      const hay = `${occ.title} ${occ.dream} ${occ.keywords.join(" ")} ${occ.tasks.join(" ")}`.toLowerCase();
      let score = 0;
      tokens.forEach((tok) => { if (occ.keywords.includes(tok)) score += 6; else if (hay.includes(tok)) score += 2; });
      return Object.assign({ score }, occ);
    }).filter((r) => r.score > 0).sort((a, b) => b.score - a.score)[0] || null;
  }

  function step(channel, tool, title, input, status, out) {
    return { id: sid("s"), channel, tool, title, input, status: status || "queued", out: out || "" };
  }

  function route(text) {
    const raw = text.trim().slice(0, 2000);
    const steps = [step("device", "buddy.plan", "Plan on this device", raw)];
    if (/take ?over|wifi|wi-fi|bluetooth|app store/i.test(raw) && /any device|all devices|hijack|control/i.test(raw)) {
      steps.push(step("device", "buddy.block", "Refuse device takeover", raw, "blocked", "Pairing only. No Wi-Fi, Bluetooth, or store takeover."));
    }
    if (/stripe|charge|payout|send money|credit card/i.test(raw)) {
      steps.push(step("device", "buddy.block", "Refuse live money", raw, "blocked", "Live Stripe stays off."));
    }
    if (/\b(gmail|outlook|send mail|calendar event)\b/i.test(raw) && /send|write|delete|trash/i.test(raw)) {
      steps.push(step("device", "buddy.block", "Needs a grant", raw, "blocked", "Mail and calendar writes wait on Connect + approve."));
    }
    const urls = raw.match(/https:\/\/[^\s)]+/g) || [];
    urls.forEach((u) => {
      try {
        const host = new URL(u).hostname.toLowerCase();
        const ok = C.allowHosts.some((h) => host === h || host.endsWith("." + h));
        steps.push(ok ? step("internet", "buddy.web.get", "GET " + host, u) : step("internet", "buddy.web.get", "Blocked host", u, "blocked", "Not on the public allowlist."));
      } catch { /* skip */ }
    });
    if (/huggingface|dataset|squad|glue|hub card|\bhf\b|model card/i.test(raw)) {
      const idHit = raw.match(/\b([A-Za-z0-9._-]+\/[A-Za-z0-9._-]+)\b/);
      const q = /squad/i.test(raw) ? "squad" : /glue/i.test(raw) ? "glue" : (idHit ? idHit[1] : raw.split(/\s+/).slice(0, 4).join(" ")).slice(0, 80);
      steps.push(step("internet", "buddy.hub.search", "Search Hub", q));
      if (idHit) steps.push(step("internet", "buddy.hub.study", "Study " + idHit[1], idHit[1]));
      else if (/squad/i.test(raw)) steps.push(step("internet", "buddy.hub.study", "Study squad", "squad"));
    }
    if (/github|actions|workflow|pull request|\brepo\b/i.test(raw)) {
      steps.push(step("internet", "buddy.github.actions", "GitHub Actions", raw));
    }
    if (/mcp|tool list|tools buddy/i.test(raw)) {
      steps.push(step("mcp", "buddy.mcp.list", "List MCP tools", raw));
    }
    if (/grok|claude|openai|teacher|ask\b|summar/i.test(raw)) {
      steps.push(step("api", "buddy.teacher.ask", "Ask the teacher API", raw, "blocked", "Teacher API is hosted-only. No keys on GitHub Pages."));
    }
    if (steps.length === 1) {
      steps.push(step("mcp", "buddy.mcp.list", "Pick a live tool", raw));
      steps.push(step("internet", "buddy.hub.search", "Search Hub for the ask", raw.slice(0, 80)));
    }
    steps.push(step("device", "buddy.notify", "Notify when done", raw));
    return steps;
  }

  async function runStep(s) {
    if (s.status === "blocked" || s.status === "done") return s;
    if (s.tool === "buddy.block") return Object.assign({}, s, { status: "blocked", out: s.out || "Blocked." });
    if (s.tool === "buddy.plan") {
      const occ = matchOcc(s.input);
      if (!occ) return Object.assign({}, s, { status: "blocked", out: "No occupation match. Try a work verb." });
      return Object.assign({}, s, { status: "done", out: JSON.stringify({ occupation: occ.title, soc: occ.soc, dream: occ.dream, cut: occ.middlemen, hubQuery: occ.hubQuery }, null, 2) });
    }
    if (s.tool === "buddy.notify") {
      if (window.Notification && Notification.permission === "granted") {
        try { new Notification("Buddy", { body: "Task finished on this device." }); } catch { /* ignore */ }
      }
      return Object.assign({}, s, { status: "done", out: "Pinged this device if notifications are allowed." });
    }
    if (s.tool === "buddy.mcp.list") {
      return Object.assign({}, s, { status: "done", out: JSON.stringify(C.mcp, null, 2) });
    }
    if (s.tool === "buddy.hub.search") {
      const kind = /dataset|squad|glue|imdb/i.test(s.input) ? "datasets" : "datasets";
      const url = `https://huggingface.co/api/${kind}?search=${encodeURIComponent(s.input || "buddy")}&limit=6&full=true`;
      const res = await fetch(url, { headers: { Accept: "application/json" } });
      if (!res.ok) return Object.assign({}, s, { status: "blocked", out: "hub_" + res.status });
      const rows = await res.json();
      const brief = (Array.isArray(rows) ? rows : []).slice(0, 6).map((r) => {
        const tags = r.tags || [];
        const lic = (tags.find((t) => String(t).startsWith("license:")) || "license:unspecified").slice(8);
        return { id: r.id, license: lic, likes: r.likes || 0, verdict: C.licenseVerdict(lic).verdict };
      });
      return Object.assign({}, s, { status: "done", out: JSON.stringify(brief, null, 2) });
    }
    if (s.tool === "buddy.hub.study") {
      let id = String(s.input || "squad").replace(/^datasets\//, "");
      let res = await fetch(`https://huggingface.co/api/datasets/${id}`, { headers: { Accept: "application/json" } });
      if (res.status === 404 && !id.includes("/")) {
        const sres = await fetch(`https://huggingface.co/api/datasets?search=${encodeURIComponent(id)}&limit=1&full=true`);
        const arr = await sres.json();
        if (Array.isArray(arr) && arr[0]) {
          id = arr[0].id;
          res = await fetch(`https://huggingface.co/api/datasets/${id}`, { headers: { Accept: "application/json" } });
        }
      }
      if (!res.ok) return Object.assign({}, s, { status: "blocked", out: "study_" + res.status });
      const row = await res.json();
      const tags = row.tags || [];
      const lic = (tags.find((t) => String(t).startsWith("license:")) || "license:unspecified").slice(8);
      const v = C.licenseVerdict(lic);
      return Object.assign({}, s, { status: "done", out: JSON.stringify({ id: row.id || id, license: lic, verdict: v.verdict, reason: v.reason }, null, 2) });
    }
    if (s.tool === "buddy.github.actions") {
      const res = await fetch("data/actions-health-report.json", { headers: { Accept: "application/json" } });
      if (!res.ok) return Object.assign({}, s, { status: "blocked", out: "Cached Actions JSON missing. Live GitHub REST is blocked from Pages." });
      const body = await res.json();
      const brief = {
        generated: body.generated_at || body.generated || body.timestamp || "cached",
        note: "Same-origin cache. api.github.com is CORS-blocked from github.io.",
        keys: Object.keys(body).slice(0, 12),
      };
      return Object.assign({}, s, { status: "done", out: JSON.stringify(brief, null, 2) });
    }
    if (s.tool === "buddy.web.get") {
      try {
        const res = await fetch(s.input, { method: "GET" });
        const text = (await res.text()).replace(/\s+/g, " ").trim().slice(0, 1200);
        return Object.assign({}, s, { status: "done", out: res.status + " " + s.input + "\n" + text });
      } catch (err) {
        return Object.assign({}, s, { status: "blocked", out: "CORS or network blocked: " + (err && err.message ? err.message : "fetch") });
      }
    }
    if (s.tool === "buddy.teacher.ask") {
      return Object.assign({}, s, { status: "blocked", out: "Teacher API is hosted-only. No XAI/OpenAI/Anthropic keys on GitHub Pages." });
    }
    return Object.assign({}, s, { status: "blocked", out: "No handler for " + s.tool + " on Pages." });
  }

  function hiddenOk(task) {
    const m = task.mode;
    const vis = document.visibilityState === "visible";
    if (m === "watch") return vis;
    if (m === "off") return true;
    return true;
  }

  async function tick() {
    const rows = loadTasks();
    const next = [];
    for (const task of rows) {
      if (task.status === "done" || task.status === "blocked") { next.push(task); continue; }
      if (!hiddenOk(task) && document.visibilityState !== "visible") { next.push(task); continue; }
      const steps = task.steps.slice();
      const idx = steps.findIndex((s) => s.status === "queued" || s.status === "running");
      if (idx === -1) {
        const blocked = steps.some((s) => s.status === "blocked");
        next.push(Object.assign({}, task, { status: blocked ? "blocked" : "done", doneAt: Date.now() }));
        continue;
      }
      steps[idx] = Object.assign({}, steps[idx], { status: "running" });
      steps[idx] = await runStep(steps[idx]);
      const blocked = steps.some((s) => s.status === "blocked");
      const open = steps.some((s) => s.status === "queued" || s.status === "running");
      const status = open ? "running" : blocked && !steps.some((s) => s.status === "done") ? "blocked" : "done";
      next.push(Object.assign({}, task, { steps, status, doneAt: status === "done" || status === "blocked" ? Date.now() : task.doneAt }));
    }
    saveTasks(next);
    render();
  }

  function enqueue(text, m) {
    const task = { id: sid("t"), text: text.trim().slice(0, 2000), mode: m || mode(), steps: route(text), status: "queued", added: Date.now() };
    saveTasks([task].concat(loadTasks()).slice(0, 40));
    log(`\n[${new Date().toISOString()}] queued ${task.text}\n${task.steps.map((s) => s.channel + ":" + s.tool).join(" · ")}\n`);
    render();
    tick();
  }

  function render() {
    const rows = loadTasks();
    const m = mode();
    $("mode-now").textContent = m === "off" ? "Screen may be off (tab must stay open)" : m === "either" ? "Watch or off" : "Watch this tab";
    ["watch", "off", "either"].forEach((k) => {
      const b = document.querySelector('[data-mode="' + k + '"]');
      if (b) b.classList.toggle("primary", k === m);
    });
    $("stat-queue").textContent = String(rows.filter((t) => t.status === "queued" || t.status === "running").length);
    $("stat-done").textContent = String(rows.filter((t) => t.status === "done").length);
    $("stat-tools").textContent = String(C.mcp.filter((t) => t.live).length);
    $("task-list").innerHTML = rows.slice(0, 12).map((t) => {
      const steps = t.steps.map((s) => `<div class="desk-step ${s.status}"><span class="desk-pill">${s.channel} · ${s.status}</span><strong> ${s.title}</strong><pre class="desk-pre">${(s.out || s.tool).slice(0, 600)}</pre></div>`).join("");
      return `<article class="desk-card"><strong>${t.text}</strong><p>${t.mode} · ${t.status}</p>${steps}</article>`;
    }).join("") || "<p class=\"desk-note\">No tasks yet. Queue one below.</p>";
    $("task-log").textContent = localStorage.getItem(LOG_KEY) || "";
  }

  $("task-go").addEventListener("click", () => {
    const text = $("task-text").value.trim();
    if (!text) return;
    enqueue(text, mode());
  });
  C.templates.forEach((t) => {
    const b = document.createElement("button");
    b.type = "button";
    b.textContent = t;
    b.addEventListener("click", () => { $("task-text").value = t; enqueue(t, mode()); });
    $("task-templates").appendChild(b);
  });
  document.querySelectorAll("[data-mode]").forEach((b) => b.addEventListener("click", () => { setMode(b.getAttribute("data-mode")); render(); }));
  $("task-notify").addEventListener("click", () => {
    if (!window.Notification) { $("task-log").textContent = "This browser has no Notification API."; return; }
    Notification.requestPermission().then((p) => { log("\nNotification permission: " + p + "\n"); render(); });
  });
  $("task-wake").addEventListener("click", async () => {
    try {
      if (navigator.wakeLock) {
        wake = await navigator.wakeLock.request("screen");
        log("\nWake Lock held. Screen-off still needs this tab alive and the device powered.\n");
      } else log("\nWake Lock not supported.\n");
    } catch (err) { log("\nWake Lock: " + (err && err.message ? err.message : "denied") + "\n"); }
    render();
  });
  $("mcp-list").innerHTML = C.mcp.map((t) =>
    `<article class="desk-card"><strong>${t.name}</strong><p>${t.channel} · ${t.live ? "live" : "blocked on Pages"}</p><p>${t.desc}</p></article>`
  ).join("");
  const boot = new URLSearchParams(location.search).get("q");
  if (boot) { $("task-text").value = boot; }
  render();
  setInterval(() => { tick().catch(() => {}); }, 1800);
  document.addEventListener("visibilitychange", () => { tick().catch(() => {}); });
})();
