(function () {
  const fmt = new Intl.NumberFormat("en-US");
  const metrics = document.getElementById("metrics");
  const partsEl = document.getElementById("parts");
  const itemsEl = document.getElementById("items");
  const truth = document.getElementById("truth");
  const resultCount = document.getElementById("result-count");
  const statusFilter = document.getElementById("status-filter");
  const search = document.getElementById("search");
  let payload = null;
  let selfBuild = null;

  function card(label, value, cls) {
    const el = document.createElement("article");
    el.className = "desk-card";
    el.innerHTML = `<strong class="${cls || ""}">${value}</strong><p>${label}</p>`;
    return el;
  }

  function renderMetrics() {
    const c = payload.summary.status_counts;
    metrics.replaceChildren(
      card("Catalogued", `${fmt.format(c.catalogued)} / ${fmt.format(payload.summary.directive_sections)}`),
      card("Implemented", `${fmt.format(c.implemented)} / ${fmt.format(payload.summary.directive_sections)}`),
      card("Sandbox verified", `${fmt.format(c.sandbox_verified)} / ${fmt.format(payload.summary.directive_sections)}`),
      card("Benchmark verified", `${fmt.format(c.benchmark_verified)} / ${fmt.format(payload.summary.directive_sections)}`, "state-never"),
      card("Regression verified", `${fmt.format(c.regression_verified)} / ${fmt.format(payload.summary.directive_sections)}`, "state-never"),
      card("Production verified", `${fmt.format(c.production_verified)} / ${fmt.format(payload.summary.directive_sections)}`, "state-never"),
    );
  }

  function renderParts() {
    partsEl.replaceChildren();
    const rows = (selfBuild && selfBuild.parts) || [];
    if (!rows.length) {
      partsEl.append(card("Self-build", "Run the daily Action. Counts here stay honest until then."));
      return;
    }
    rows.forEach((part) => {
      const el = document.createElement("article");
      el.className = "desk-card";
      const cls = part.status === "built" ? "state-ok" : part.status === "gated" ? "state-paid" : "state-never";
      el.innerHTML = `<strong>${part.id}</strong><p class="${cls}">${part.status}</p><p>${part.self_fix}</p>`;
      partsEl.append(el);
    });
  }

  function renderItems() {
    const q = (search.value || "").trim().toLowerCase();
    const status = statusFilter.value;
    const rows = payload.items.filter((item) => {
      if (status && item.status !== status) return false;
      if (!q) return true;
      return `${item.section} ${item.title} ${item.acceptance_excerpt}`.toLowerCase().includes(q);
    });
    resultCount.textContent = `${fmt.format(rows.length)} of ${fmt.format(payload.items.length)} sections`;
    itemsEl.replaceChildren();
    rows.slice(0, 80).forEach((item) => {
      const el = document.createElement("article");
      el.className = "desk-card";
      const cls = item.status === "sandbox_verified" ? "state-ok" : item.status === "implemented" ? "state-grant" : "state-paid";
      const evidence = item.evidence_refs.length ? item.evidence_refs.join(" · ") : "No implementation files yet.";
      el.innerHTML = `<strong>${item.section}. ${item.title}</strong><p class="${cls}">${item.status} · next ${item.next_status || "none"}</p><p>${item.acceptance_excerpt}</p><p>Evidence: ${evidence}</p><p>Self-build: ${item.self_build}. Self-fix: ${item.self_fix}.</p>`;
      itemsEl.append(el);
    });
    if (rows.length > 80) {
      const note = document.createElement("p");
      note.className = "desk-note";
      note.textContent = "Showing 80. Narrow status or search.";
      itemsEl.append(note);
    }
  }

  Promise.all([
    fetch("data/master-directive-status.json", { cache: "no-store" }).then((r) => r.json()),
    fetch("data/self-build.json", { cache: "no-store" }).then((r) => (r.ok ? r.json() : null)).catch(() => null),
  ])
    .then(([dir, build]) => {
      payload = dir;
      selfBuild = build;
      truth.textContent = dir.summary.truth;
      renderMetrics();
      renderParts();
      renderItems();
      statusFilter.addEventListener("change", renderItems);
      search.addEventListener("input", renderItems);
    })
    .catch((err) => {
      truth.textContent = err.message;
    });
})();
