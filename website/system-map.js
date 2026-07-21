(function () {
  const formatter = new Intl.NumberFormat("en-US");
  let divisions = [];

  function text(tag, value, className) {
    const node = document.createElement(tag);
    node.textContent = value;
    if (className) node.className = className;
    return node;
  }

  function statusBadge(status) {
    const labels = {
      ready: "Ready",
      cataloged: "Cataloged",
      generated: "Generated",
      candidate_ready: "Candidate-ready",
      in_progress: "In progress",
      prototype: "Prototype",
      approval_required: "Approval required",
    };
    const tones = {
      ready: "green",
      cataloged: "primary",
      generated: "cyan",
      candidate_ready: "green",
      in_progress: "amber",
      prototype: "violet",
      approval_required: "amber",
    };
    return text("span", labels[status] || status, `badge badge-${tones[status] || "gray"}`);
  }

  function renderStats(summary) {
    document.querySelectorAll("[data-map-stat]").forEach((node) => {
      const value = Number(summary[node.dataset.mapStat] || 0);
      node.textContent = formatter.format(value);
    });
  }

  function renderSystems(systems) {
    const target = document.getElementById("system-readiness-grid");
    target.replaceChildren();
    systems.forEach((system) => {
      const card = document.createElement("article");
      card.className = "system-status-card";
      const heading = document.createElement("div");
      heading.className = "system-status-heading";
      heading.append(text("h3", system.label), statusBadge(system.status));
      card.append(heading, text("p", system.detail), text("code", system.source));
      target.append(card);
    });
  }

  function renderLibraries(libraries) {
    const target = document.getElementById("system-library-grid");
    target.replaceChildren();
    libraries.forEach((library) => {
      const card = document.createElement("article");
      card.className = "system-library-card";
      const count = text("strong", formatter.format(Number(library.count || 0)));
      const heading = document.createElement("div");
      heading.append(text("h3", library.name), count);
      card.append(heading, text("p", library.description));
      target.append(card);
    });
  }

  function renderDivisions(query) {
    const target = document.getElementById("division-map-grid");
    const normalized = query.trim().toLowerCase();
    const filtered = divisions.filter((division) =>
      `${division.name} ${division.mission}`.toLowerCase().includes(normalized)
    );
    target.replaceChildren();
    filtered.forEach((division) => {
      const card = document.createElement("article");
      card.className = "division-map-card";
      const heading = document.createElement("div");
      heading.append(
        text("h3", division.name),
        text("strong", formatter.format(Number(division.registered_bots || 0)))
      );
      card.append(
        heading,
        text("p", division.mission),
        text("span", "Money actions require approval", "division-governance")
      );
      target.append(card);
    });
    if (!filtered.length) target.append(text("p", "No divisions match this filter.", "map-empty"));
  }

  async function init() {
    const response = await fetch("data/repository-system-map.json", { cache: "no-store" });
    if (!response.ok) throw new Error(`Repository map request failed: ${response.status}`);
    const payload = await response.json();
    divisions = Array.isArray(payload.divisions) ? payload.divisions : [];
    renderStats(payload.summary || {});
    renderSystems(Array.isArray(payload.systems) ? payload.systems : []);
    renderLibraries(Array.isArray(payload.libraries) ? payload.libraries : []);
    renderDivisions("");
    document.getElementById("map-generated").textContent = `Generated ${payload.generated_at || "from the latest scan"}`;
    document.getElementById("division-search").addEventListener("input", (event) => {
      renderDivisions(event.target.value || "");
    });
  }

  init().catch((error) => {
    const target = document.getElementById("system-readiness-grid");
    target.replaceChildren(text("p", "Repository map data could not be loaded. Run the site through a local web server or GitHub Pages.", "map-error"));
    document.documentElement.dataset.systemMap = "offline";
    console.error(error);
  });
})();
