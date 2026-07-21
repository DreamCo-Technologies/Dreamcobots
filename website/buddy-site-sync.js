// DreamCo website build sync. Reads generated Buddy status data when hosted.
(function () {
  const DATA_URL = "data/buddy-site-status.json";

  const fmt = new Intl.NumberFormat("en-US");

  function setText(selector, value) {
    document.querySelectorAll(selector).forEach((node) => {
      node.textContent = value;
    });
  }

  function setHtml(selector, value) {
    document.querySelectorAll(selector).forEach((node) => {
      node.innerHTML = value;
    });
  }

  function badge(text, kind) {
    return `<span class="badge badge-${kind}">${text}</span>`;
  }

  function renderQueue(items) {
    const target = document.querySelector("[data-buddy-completion-queue]");
    if (!target || !Array.isArray(items)) return;
    target.innerHTML = items.slice(0, 6).map((item) => `
      <div class="buddy-sync-row">
        <span class="badge ${item.completion_status === "code_core_runtime_now" ? "badge-amber" : "badge-primary"}">#${item.sprint_rank}</span>
        <div>
          <strong>${item.name}</strong>
          <div>${item.path}</div>
        </div>
        <a href="bots.html" class="btn btn-outline btn-sm">Review</a>
      </div>
    `).join("");
  }

  function renderRoutes(routes) {
    const target = document.querySelector("[data-buddy-native-routes]");
    if (!target || !Array.isArray(routes)) return;
    target.innerHTML = routes.slice(0, 8).map((route) => `
      <div class="buddy-route-pill">
        <span>${route.task_type.replaceAll("_", " ")}</span>
        <strong>${route.primary_native_bot}</strong>
      </div>
    `).join("");
  }

  function applyStatus(payload) {
    const summary = payload.summary || {};
    const total = fmt.format(summary.product_bot_files || 0);
    const ready = fmt.format(summary.native_runnable_candidates || 0);
    const queue = fmt.format(summary.completion_queue || 0);
    const core = fmt.format(summary.need_core_runtime || 0);
    const freeModels = fmt.format(summary.free_model_resources || 0);
    const apiRoutes = fmt.format(summary.professional_api_routes || 0);
    const nativeRoutes = fmt.format(summary.native_task_routes || 0);
    const studioTracks = fmt.format(summary.creative_studio_tracks || 0);
    const readiness = `${summary.readiness_percent || 0}%`;

    setText("[data-buddy-stat='product-bots']", total);
    setText("[data-buddy-stat='ready-bots']", ready);
    setText("[data-buddy-stat='completion-queue']", queue);
    setText("[data-buddy-stat='core-runtime']", core);
    setText("[data-buddy-stat='free-models']", freeModels);
    setText("[data-buddy-stat='api-routes']", apiRoutes);
    setText("[data-buddy-stat='native-routes']", nativeRoutes);
    setText("[data-buddy-stat='studio-tracks']", studioTracks);
    setText("[data-buddy-stat='readiness']", readiness);
    setHtml("[data-buddy-status-badges]", [
      badge(`${ready} native-ready`, "green"),
      badge(`${queue} in sprint`, "amber"),
      badge(`${freeModels} free resources`, "primary"),
    ].join(" "));
    renderQueue(payload.top_completion_queue || []);
    renderRoutes(payload.native_routes || []);
  }

  async function init() {
    try {
      const response = await fetch(DATA_URL, { cache: "no-store" });
      if (!response.ok) return;
      applyStatus(await response.json());
    } catch (error) {
      document.documentElement.dataset.buddySiteSync = "offline";
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
