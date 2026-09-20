/* Hub OS — public Hugging Face cards. License first. No parquet. No keys. */
(function () {
  const C = window.BUDDY_CHAT;
  const PKG = "buddy.packages";
  const $ = (id) => document.getElementById(id);

  function loadPkg() {
    try {
      const raw = JSON.parse(localStorage.getItem(PKG) || "[]");
      return Array.isArray(raw) ? raw : [];
    } catch {
      return [];
    }
  }
  function savePkg(rows) {
    localStorage.setItem(PKG, JSON.stringify(rows.slice(0, 80)));
  }

  function groups() {
    const map = {};
    C.tasks.forEach((t) => {
      (map[t.group] ||= []).push(t);
    });
    return map;
  }

  function renderTasks() {
    const host = $("hub-tasks");
    const g = groups();
    host.innerHTML = Object.keys(g).map((name) => {
      const cards = g[name].map((t) =>
        `<article class="desk-card"><strong>${t.name}</strong><p>${t.studies}</p><p>${t.other}</p>
         <div class="desk-actions"><a class="desk-btn" href="${t.href}" target="_blank" rel="noopener">Hub task</a>
         <button type="button" data-search="${t.id}">Search live</button></div></article>`
      ).join("");
      return `<h2 class="desk-kicker">${name} · ${g[name].length}</h2><div class="desk-grid">${cards}</div>`;
    }).join("");
  }

  function renderCompare() {
    $("hub-compare").innerHTML = C.compare.map((r) =>
      `<article class="desk-card"><strong>${r.need}</strong><p>HF: ${r.hf}</p><p>Buddy: ${r.buddy}</p><p>${r.other}</p></article>`
    ).join("");
  }

  function renderPkg() {
    const rows = loadPkg();
    $("hub-pkg").textContent = rows.length
      ? rows.map((r) => `${r.verdict.toUpperCase()}  ${r.id}  ${r.license}  — ${r.reason}`).join("\n")
      : "No cards indexed on this device yet.";
    $("stat-pkg").textContent = String(rows.length);
  }

  function cardLine(row) {
    const id = row.id || row.modelId || "unknown";
    const tags = row.tags || [];
    const licTag = tags.find((t) => String(t).startsWith("license:"));
    const license = licTag ? licTag.slice(8) : (row.cardData && row.cardData.license) || "unspecified";
    const lic = Array.isArray(license) ? license[0] : String(license || "unspecified");
    const v = C.licenseVerdict(lic);
    return { id, license: lic, likes: row.likes || 0, downloads: row.downloads || 0, verdict: v.verdict, reason: v.reason, url: `https://huggingface.co/datasets/${id}` };
  }

  async function searchHub(q) {
    const query = String(q || "").trim().slice(0, 80) || "squad";
    $("hub-out").textContent = "Searching Hub…";
    const url = `https://huggingface.co/api/datasets?search=${encodeURIComponent(query)}&limit=8&full=true`;
    const res = await fetch(url, { headers: { Accept: "application/json" } });
    if (!res.ok) throw new Error("hub_" + res.status);
    const rows = await res.json();
    if (!Array.isArray(rows) || !rows.length) {
      $("hub-out").textContent = "No cards for “" + query + "”. Try squad, glue, or an id like rajpurkar/squad.";
      return;
    }
    const studied = rows.map(cardLine);
    $("hub-out").textContent = studied.map((s) => `${s.verdict.toUpperCase()}  ${s.id}  ${s.license}  likes ${s.likes}\n${s.reason}`).join("\n\n");
    $("hub-results").innerHTML = studied.map((s) =>
      `<article class="desk-card"><strong>${s.id}</strong><span class="desk-status ${s.verdict === "index" ? "healthy" : s.verdict === "refuse" ? "blocked" : "watch"}">${s.verdict}</span>
       <p>${s.license} · ${s.likes} likes</p>
       <div class="desk-actions">
         <button type="button" class="primary" data-study="${s.id}">Study</button>
         <a class="desk-btn" href="${s.url}" target="_blank" rel="noopener">Open card</a>
       </div></article>`
    ).join("");
  }

  async function studyId(id) {
    const clean = String(id || "").replace(/^datasets\//, "").trim();
    if (!/^[A-Za-z0-9._-]+(\/[A-Za-z0-9._-]+)?$/.test(clean)) {
      $("hub-out").textContent = "Bad dataset id.";
      return;
    }
    $("hub-out").textContent = "Loading card " + clean + "…";
    let res = await fetch(`https://huggingface.co/api/datasets/${clean}`, { headers: { Accept: "application/json" } });
    if (res.status === 404 && !clean.includes("/")) {
      res = await fetch(`https://huggingface.co/api/datasets?search=${encodeURIComponent(clean)}&limit=1&full=true`);
      const arr = await res.json();
      if (Array.isArray(arr) && arr[0]) {
        return studyId(arr[0].id);
      }
    }
    if (!res.ok) throw new Error("study_" + res.status);
    const row = await res.json();
    const card = Array.isArray(row) ? cardLine(row[0]) : cardLine(row);
    const files = ((row.siblings) || []).map((s) => s.rfilename).filter(Boolean).slice(0, 10);
    $("hub-out").textContent = JSON.stringify({
      id: card.id,
      license: card.license,
      verdict: card.verdict,
      reason: card.reason,
      likes: card.likes,
      files,
      note: "Card only. Buddy does not download parquet from Pages."
    }, null, 2);
    if (card.verdict !== "refuse") {
      const rows = loadPkg().filter((r) => r.id !== card.id);
      rows.unshift({ id: card.id, license: card.license, verdict: card.verdict, reason: card.reason, at: new Date().toISOString() });
      savePkg(rows);
      renderPkg();
    }
  }

  $("hub-search-btn").addEventListener("click", () => searchHub($("hub-q").value).catch((e) => { $("hub-out").textContent = String(e.message || e); }));
  $("hub-study-btn").addEventListener("click", () => studyId($("hub-id").value || $("hub-q").value).catch((e) => { $("hub-out").textContent = String(e.message || e); }));
  document.addEventListener("click", (e) => {
    const t = e.target;
    if (!(t instanceof HTMLElement)) return;
    if (t.dataset.search) searchHub(t.dataset.search).catch((err) => { $("hub-out").textContent = String(err.message || err); });
    if (t.dataset.study) studyId(t.dataset.study).catch((err) => { $("hub-out").textContent = String(err.message || err); });
  });
  C.canonical.forEach((id) => {
    const b = document.createElement("button");
    b.type = "button";
    b.textContent = id;
    b.dataset.study = id;
    $("hub-canon").appendChild(b);
  });
  $("stat-tasks").textContent = String(C.tasks.length);
  const boot = new URLSearchParams(location.search).get("q");
  if (boot) $("hub-q").value = boot;
  renderTasks();
  renderCompare();
  renderPkg();
  if (boot) searchHub(boot).catch((e) => { $("hub-out").textContent = String(e.message || e); });
})();
