/**
 * OS Observability SLO/soak tiles (SET 5).
 * Fail-closed: missing/invalid JSON → all yellow; yellow never renders as green.
 * Feed: website/data/os-observability-metrics.json (control-plane artifact when present).
 */
(function () {
  "use strict";

  var DATA_URL = "data/os-observability-metrics.json";
  var STATES = { green: "#22c55e", red: "#ef4444", yellow: "#eab308", gray: "#64748b" };

  function failClosedPayload(reason) {
    return {
      schema_version: "1.0.0",
      provenance: { evidence_complete: false },
      anti_vanity: { yellow_never_counts_as_green: true },
      surfaces: {
        actions: { state: "yellow", soak_ok: null },
        pr: { state: "yellow", soak_ok: null },
        issues: { state: "yellow", soak_ok: null },
        agents: { state: "yellow", soak_ok: null },
      },
      aggregate: {
        os_green_pct: null,
        os_soak_ok: null,
        os_pages_publish_freshness_hours: null,
        counts: { green: 0, red: 0, yellow: 25 },
      },
      metrics: [],
      production_ready: false,
      _load_error: reason || "missing evidence",
    };
  }

  function normalizeState(s) {
    if (s === "green" || s === "red" || s === "yellow" || s === "gray") return s;
    return "yellow";
  }

  /** Never promote yellow/gray/null to green. */
  function displayState(metric) {
    var st = normalizeState(metric && metric.state);
    var ev = metric && metric.evidence;
    if (st === "green" && !(ev && ev.present)) return "yellow";
    return st;
  }

  function fmtValue(m) {
    if (!m || m.value === null || m.value === undefined) return "—";
    if (typeof m.value === "object") {
      try {
        return Object.keys(m.value)
          .map(function (k) {
            var v = m.value[k];
            return k + ":" + (v === null || v === undefined ? "?" : v);
          })
          .join(" ");
      } catch (e) {
        return "—";
      }
    }
    if (typeof m.value === "boolean") return m.value ? "yes" : "no";
    if (m.unit === "%") return String(m.value) + "%";
    return String(m.value);
  }

  function renderStrip(root, data) {
    if (!root) return;
    var agg = data.aggregate || {};
    var counts = agg.counts || { green: 0, red: 0, yellow: 0 };
    var status =
      data._load_error ||
      (data.provenance && data.provenance.evidence_complete
        ? "Control-plane evidence loaded"
        : "Fail-closed stub — awaiting control-plane artifact");

    var header =
      '<div class="os-obs-head">' +
      '<div><p class="actions-kicker">SET 5 · no vanity green</p>' +
      "<h2>OS SLO / soak</h2>" +
      "<p>" +
      status +
      ". Yellow ≠ green. production_ready=" +
      String(!!data.production_ready) +
      ".</p></div>" +
      '<div class="os-obs-agg">' +
      "<div><span>Green%</span><strong>" +
      (agg.os_green_pct === null || agg.os_green_pct === undefined ? "—" : agg.os_green_pct + "%") +
      "</strong></div>" +
      "<div><span>Soak OK</span><strong>" +
      (agg.os_soak_ok === null || agg.os_soak_ok === undefined ? "—" : agg.os_soak_ok ? "yes" : "no") +
      "</strong></div>" +
      "<div><span>G/R/Y</span><strong>" +
      counts.green +
      "/" +
      counts.red +
      "/" +
      counts.yellow +
      "</strong></div>" +
      "</div></div>";

    var surfaces = data.surfaces || {};
    var surfHtml = '<div class="os-obs-surfaces">';
    ["actions", "pr", "issues", "agents"].forEach(function (key) {
      var s = surfaces[key] || { state: "yellow" };
      var st = normalizeState(s.state);
      if (st === "green" && !(data.provenance && data.provenance.evidence_complete)) st = "yellow";
      surfHtml +=
        '<div class="os-obs-surface" data-state="' +
        st +
        '" style="border-left:4px solid ' +
        (STATES[st] || STATES.yellow) +
        '"><strong>' +
        key.toUpperCase() +
        "</strong><span>" +
        st +
        "</span></div>";
    });
    surfHtml += "</div>";

    var metrics = Array.isArray(data.metrics) ? data.metrics : [];
    var tiles = '<div class="os-obs-tiles" role="list">';
    metrics.forEach(function (m) {
      var st = displayState(m);
      tiles +=
        '<article class="os-obs-tile" role="listitem" data-state="' +
        st +
        '" data-id="' +
        (m.id || "") +
        '" style="border-top:3px solid ' +
        (STATES[st] || STATES.yellow) +
        '"><span class="os-obs-label">' +
        (m.label || m.id) +
        '</span><strong class="os-obs-value">' +
        fmtValue(m) +
        '</strong><span class="os-obs-state">' +
        st +
        "</span></article>";
    });
    tiles += "</div>";

    root.innerHTML = header + surfHtml + tiles;
    root.setAttribute("data-os-obs-ready", "1");
    root.setAttribute("data-production-ready", String(!!data.production_ready));
  }

  function ensureStyles() {
    if (document.getElementById("os-obs-styles")) return;
    var css = document.createElement("style");
    css.id = "os-obs-styles";
    css.textContent =
      ".os-obs-strip{margin:24px 0;padding:20px;border:1px solid var(--border,#263244);border-radius:18px;background:var(--card,#111827)}" +
      ".os-obs-head{display:flex;flex-wrap:wrap;gap:16px;justify-content:space-between;align-items:flex-start;margin-bottom:14px}" +
      ".os-obs-agg{display:flex;gap:14px;flex-wrap:wrap}.os-obs-agg div{min-width:72px}.os-obs-agg span{display:block;opacity:.7;font-size:.75rem}.os-obs-agg strong{font-size:1.25rem}" +
      ".os-obs-surfaces{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px;margin-bottom:14px}" +
      ".os-obs-surface{padding:10px 12px;border-radius:10px;background:var(--card2,#172033);display:flex;justify-content:space-between;gap:8px;text-transform:uppercase;font-size:.75rem}" +
      ".os-obs-tiles{display:grid;grid-template-columns:repeat(auto-fill,minmax(160px,1fr));gap:10px}" +
      ".os-obs-tile{padding:12px;border-radius:12px;background:var(--card2,#172033);display:grid;gap:6px}" +
      ".os-obs-label{font-size:.72rem;opacity:.8;line-height:1.3}.os-obs-value{font-size:1.05rem}.os-obs-state{font-size:.65rem;text-transform:uppercase;opacity:.75}" +
      "@media(max-width:760px){.os-obs-surfaces{grid-template-columns:1fr 1fr}}";
    document.head.appendChild(css);
  }

  function mount() {
    ensureStyles();
    var roots = document.querySelectorAll("[data-os-observability]");
    if (!roots.length) return;
    fetch(DATA_URL, { cache: "no-store" })
      .then(function (r) {
        if (!r.ok) throw new Error("HTTP " + r.status);
        return r.json();
      })
      .then(function (data) {
        if (!data || typeof data !== "object") throw new Error("invalid json");
        if (data.production_ready === true) {
          // Contract: this stub path must not claim production_ready
          data.production_ready = false;
        }
        roots.forEach(function (el) {
          renderStrip(el, data);
        });
        try {
          window.dispatchEvent(
            new CustomEvent("dreamco:observability.tile_state", {
              detail: {
                production_ready: false,
                aggregate: data.aggregate,
                evidence_complete: !!(data.provenance && data.provenance.evidence_complete),
              },
            })
          );
        } catch (e) {}
      })
      .catch(function (err) {
        var fc = failClosedPayload(String(err && err.message ? err.message : err));
        roots.forEach(function (el) {
          renderStrip(el, fc);
        });
      });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", mount);
  } else {
    mount();
  }
})();
