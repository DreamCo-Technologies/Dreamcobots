// Buddy Control Panel: renders config/buddy/control-plane.json + the status snapshot.
// Static and token-free. "Run with Buddy" only opens a prefilled GitHub issue; the
// buddy-command-router workflow does all authorization and dispatch server-side.
(function () {
  "use strict";

  var FALLBACK_REPO = "DreamCo-Technologies/Dreamcobots";
  var JOB_ID_RE = /^[a-z][a-z0-9_]{1,63}$/;
  var KEY_RE = /^[a-z][a-z0-9_]{0,39}$/;
  var VALUE_RE = /^[A-Za-z0-9._-]{1,100}$/;
  var WORKFLOW_RE = /^[a-z0-9][a-z0-9._-]{0,98}\.ya?ml$/;
  var REPO_RE = /^[A-Za-z0-9_.-]{1,100}\/[A-Za-z0-9_.-]{1,100}$/;
  var RUN_URL_RE = /^https:\/\/github\.com\/[A-Za-z0-9_.-]+\/[A-Za-z0-9_.-]+\/actions\/runs\/\d+$/;

  var registry = null;
  var status = { jobs: {} };
  var choices = {};

  function esc(value) {
    return String(value == null ? "" : value).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }

  function repo() {
    var r = registry && registry.repository;
    return REPO_RE.test(r || "") ? r : FALLBACK_REPO;
  }

  function isTriggerable(job) {
    var tiers = (registry && registry.risk_tiers) || {};
    var tier = tiers[job.risk_tier] || {};
    return job.triggerable === true && job.destructive !== true && job.risk_tier !== "money" && tier.dispatchable === true;
  }

  function inputsFor(job) {
    var out = [];
    var specs = job.inputs || {};
    Object.keys(specs).forEach(function (key) {
      var spec = specs[key] || {};
      var chosen = (choices[job.id] || {})[key];
      var value = chosen != null ? chosen : spec["default"];
      if (typeof value === "boolean") value = value ? "true" : "false";
      if (value != null && KEY_RE.test(key) && VALUE_RE.test(String(value))) out.push(key + "=" + value);
    });
    return out;
  }

  function issueUrl(job) {
    if (!JOB_ID_RE.test(job.id)) return null;
    var lines = inputsFor(job);
    var body = ["Requested from the Buddy Control Panel (GitHub Pages).", ""];
    if (lines.length) {
      body.push("```buddy-inputs");
      body = body.concat(lines);
      body.push("```", "");
    }
    body.push(
      "- Job: `" + job.id + "` (" + job.risk_tier + ")" + (job.requires_owner_approval ? " - owner approval required" : ""),
      "- Workflow: `" + job.workflow + "` on `" + ((registry && registry.default_ref) || "main") + "`",
      "- Only an authorized Buddy operator with write access can run this. The router comments back with the run link, or the reason it was rejected."
    );
    var label = (registry && registry.command_label) || "buddy-command";
    return "https://github.com/" + repo() + "/issues/new?title=" + encodeURIComponent("/buddy run " + job.id) +
      "&labels=" + encodeURIComponent(label) + "&body=" + encodeURIComponent(body.join("\n"));
  }

  function workflowLinks(job) {
    if (!WORKFLOW_RE.test(job.workflow || "")) return { view: "#", actions: "#" };
    var ref = (registry && registry.default_ref) || "main";
    return {
      view: "https://github.com/" + repo() + "/blob/" + encodeURIComponent(ref) + "/.github/workflows/" + job.workflow,
      actions: "https://github.com/" + repo() + "/actions/workflows/" + job.workflow
    };
  }

  function stateOf(job) {
    var item = (status.jobs || {})[job.id];
    return item || { state: "unknown" };
  }

  function renderSummary() {
    var jobs = registry.jobs || [];
    var counts = { read_only: 0, writes_reports: 0, writes_code: 0, money: 0 };
    var runnable = 0;
    jobs.forEach(function (j) {
      if (counts[j.risk_tier] != null) counts[j.risk_tier] += 1;
      if (isTriggerable(j)) runnable += 1;
    });
    var cards = [
      ["Registered jobs", jobs.length],
      ["Runnable from Pages", runnable],
      ["read_only", counts.read_only],
      ["writes_reports", counts.writes_reports],
      ["writes_code", counts.writes_code],
      ["money (never runnable)", counts.money]
    ];
    document.getElementById("bcp-summary").innerHTML = cards.map(function (c) {
      return "<article class=\"desk-card\"><strong>" + esc(c[1]) + "</strong><p>" + esc(c[0]) + "</p></article>";
    }).join("");
  }

  function renderInputs(job) {
    var specs = job.inputs || {};
    var keys = Object.keys(specs);
    var fixed = job.fixed_inputs || {};
    var parts = keys.map(function (key) {
      var spec = specs[key] || {};
      var options = spec.type === "boolean" ? ["true", "false"] : (spec.options || []);
      if (spec.type !== "choice" && spec.type !== "boolean") return "";
      var current = (choices[job.id] || {})[key];
      if (current == null) current = typeof spec["default"] === "boolean" ? (spec["default"] ? "true" : "false") : spec["default"];
      return "<label>" + esc(key) + " <select data-job=\"" + esc(job.id) + "\" data-key=\"" + esc(key) + "\">" +
        options.map(function (o) {
          return "<option value=\"" + esc(o) + "\"" + (String(o) === String(current) ? " selected" : "") + ">" + esc(o) + "</option>";
        }).join("") + "</select></label>";
    });
    Object.keys(fixed).forEach(function (key) {
      parts.push("<span>" + esc(key) + "=" + esc(fixed[key]) + " (fixed)</span>");
    });
    return parts.join("") ? "<div class=\"bcp-inputs\">" + parts.join("") + "</div>" : "";
  }

  function renderJobs() {
    var filter = document.getElementById("bcp-filter").value;
    var jobs = (registry.jobs || []).filter(function (j) {
      if (filter === "all") return true;
      if (filter === "triggerable") return isTriggerable(j);
      if (filter === "blocked") return !isTriggerable(j);
      return j.risk_tier === filter;
    });
    document.getElementById("bcp-jobs").innerHTML = jobs.map(function (job) {
      var st = stateOf(job);
      var links = workflowLinks(job);
      var runLink = RUN_URL_RE.test(st.run_url || "") ?
        "<a href=\"" + esc(st.run_url) + "\" target=\"_blank\" rel=\"noopener\">last run" + (st.run_number ? " #" + esc(st.run_number) : "") + "</a>" :
        "no run link";
      var run = isTriggerable(job) ?
        "<a class=\"bcp-btn primary\" target=\"_blank\" rel=\"noopener\" href=\"" + esc(issueUrl(job)) + "\">Run with Buddy</a>" :
        "<span class=\"bcp-btn\" aria-disabled=\"true\" title=\"" + esc(job.blocked_reason || "blocked by policy") + "\">Blocked</span>";
      return "<article class=\"desk-card\" id=\"job-" + esc(job.id) + "\">" +
        "<strong>" + esc(job.title) + "</strong>" +
        "<p><span class=\"bcp-tier " + esc(job.risk_tier) + "\">" + esc(job.risk_tier) + "</span> " +
        (job.requires_owner_approval ? "<span class=\"bcp-tier\">owner approval</span> " : "") +
        "<span class=\"bcp-state " + esc(st.state) + "\">" + esc(String(st.state).replace(/_/g, " ")) + "</span></p>" +
        "<p class=\"bcp-meta\">" + esc(job.id) + " · " + esc(job.workflow) + " · " + runLink + (st.updated_at ? " · " + esc(st.updated_at) : "") + "</p>" +
        "<p>" + esc(job.family) + (job.notes ? " - " + esc(job.notes) : "") + (!isTriggerable(job) && job.blocked_reason ? " Blocked: " + esc(job.blocked_reason) : "") + "</p>" +
        renderInputs(job) +
        "<div class=\"bcp-actions\">" + run +
        "<a class=\"bcp-btn\" target=\"_blank\" rel=\"noopener\" href=\"" + esc(links.view) + "\">View workflow</a>" +
        "<a class=\"bcp-btn\" target=\"_blank\" rel=\"noopener\" href=\"" + esc(links.actions) + "\">Open Actions</a>" +
        "</div></article>";
    }).join("") || "<p class=\"desk-note\">No jobs match this filter.</p>";
  }

  function renderStamp(extra) {
    var s = status && status.generated_at ?
      "Status snapshot " + status.generated_at + " (" + (status.source || "unknown") + ")." :
      "No published status snapshot yet; use Refresh live.";
    document.getElementById("bcp-stamp").textContent = s + (extra ? " " + extra : "");
  }

  function render() {
    renderSummary();
    renderJobs();
    renderStamp();
  }

  function fetchJson(url) {
    return fetch(url, { cache: "no-store" }).then(function (r) {
      if (!r.ok) throw new Error("HTTP " + r.status);
      return r.json();
    });
  }

  function loadRegistry() {
    return fetchJson("data/buddy-control-plane.json").catch(function () {
      return fetchJson("https://raw.githubusercontent.com/" + FALLBACK_REPO + "/main/config/buddy/control-plane.json");
    });
  }

  function refreshLive() {
    var btn = document.getElementById("bcp-live");
    btn.setAttribute("aria-disabled", "true");
    var ref = (registry && registry.default_ref) || "main";
    var workflows = {};
    (registry.jobs || []).forEach(function (j) { if (WORKFLOW_RE.test(j.workflow || "")) workflows[j.workflow] = true; });
    var names = Object.keys(workflows);
    var results = {};
    var failures = 0;
    Promise.all(names.map(function (wf) {
      var url = "https://api.github.com/repos/" + repo() + "/actions/workflows/" + wf + "/runs?per_page=1&exclude_pull_requests=true&branch=" + encodeURIComponent(ref);
      return fetch(url, { headers: { Accept: "application/vnd.github+json" } }).then(function (r) {
        if (r.status === 404) { results[wf] = { state: "workflow_missing" }; return; }
        if (!r.ok) throw new Error("HTTP " + r.status);
        return r.json().then(function (data) {
          var run = (data.workflow_runs || [])[0];
          results[wf] = run ? {
            state: run.status !== "completed" ? run.status : (run.conclusion || "unknown"),
            run_url: run.html_url, run_number: run.run_number, updated_at: run.updated_at, event: run.event
          } : { state: "never_run" };
        });
      }).catch(function () { failures += 1; });
    })).then(function () {
      var jobs = {};
      (registry.jobs || []).forEach(function (j) { jobs[j.id] = results[j.workflow] || stateOf(j); });
      status = { generated_at: new Date().toISOString().replace(/\.\d+Z$/, "Z"), source: failures ? "live (partial)" : "live", jobs: jobs };
      renderJobs();
      renderStamp(failures ? failures + " workflow lookups failed (GitHub's anonymous API limit is 60 requests/hour)." : "");
      btn.removeAttribute("aria-disabled");
    });
  }

  document.getElementById("bcp-filter").addEventListener("change", function () { if (registry) renderJobs(); });
  document.getElementById("bcp-live").addEventListener("click", function () { if (registry) refreshLive(); });
  document.getElementById("bcp-jobs").addEventListener("change", function (ev) {
    var t = ev.target;
    if (!t || t.tagName !== "SELECT") return;
    var job = t.getAttribute("data-job");
    var key = t.getAttribute("data-key");
    if (!JOB_ID_RE.test(job || "") || !KEY_RE.test(key || "") || !VALUE_RE.test(t.value)) return;
    choices[job] = choices[job] || {};
    choices[job][key] = t.value;
    renderJobs();
  });

  // Generated jobs + prospectus (tools/build_actions_prospectus.py). Only shown when the
  // fleet runtime outputs are deployed; buddy-run.js is loaded on demand so this page has no
  // hard dependency on them.
  function loadScript(src) {
    return new Promise(function (resolve, reject) {
      var el = document.createElement("script");
      el.src = src; el.onload = resolve; el.onerror = function () { reject(new Error(src)); };
      document.head.appendChild(el);
    });
  }

  function renderGenerated(meta) {
    var BR = window.BuddyRun;
    if (!BR || !meta || !registry) return;
    var curated = {};
    (registry.jobs || []).forEach(function (j) { curated[j.id] = true; curated["wf:" + j.workflow] = true; });
    var cards = (meta.workflows || []).filter(function (c) {
      var wf = (c.links && c.links.workflow || "").split("/").pop();
      return !curated[c.id] && (!wf || !curated["wf:" + wf] || /^fleet_/.test(c.id));
    });
    var list = document.getElementById("bcp-generated-list");
    list.innerHTML = cards.map(function (c) {
      return "<article class=\"desk-card\" id=\"job-" + esc(c.id) + "\"><strong>" + esc(c.title) + "</strong>" +
        "<p><span class=\"bcp-tier " + esc(c.risk_tier) + "\">" + esc(c.risk_tier) + "</span> <span class=\"bcp-meta\">" + esc(c.id) + "</span></p>" +
        BR.runControls(c) + "</article>";
    }).join("") || "<p class=\"desk-note\">Every workflow is covered by a curated job.</p>";
    document.getElementById("bcp-generated-note").insertAdjacentHTML("beforeend",
      " Bots and divisions (Run, prospectus and Customize): <a href=\"fleet-runtime.html\">fleet runtime</a> · <a href=\"divisions.html\">divisions</a> · files: <a href=\"files.html\">file prospectus</a>.");
    document.getElementById("bcp-generated").hidden = false;
  }

  function loadGenerated() {
    return fetchJson("data/run-prospectus.json").then(function (meta) {
      var css = document.createElement("link");
      css.rel = "stylesheet"; css.href = "buddy-run.css";
      document.head.appendChild(css);
      return loadScript("buddy-run.js").then(function () { renderGenerated(meta); });
    }).catch(function () { /* fleet runtime outputs not deployed yet: curated jobs only */ });
  }

  loadRegistry().then(function (reg) {
    registry = reg;
    return fetchJson("data/buddy-control-status.json").then(function (s) { status = s || { jobs: {} }; }, function () { status = { jobs: {} }; });
  }).then(function () {
    if (registry) { render(); loadGenerated(); }
  }).catch(function (err) {
    document.getElementById("bcp-stamp").textContent = "Could not load the Buddy job registry (" + err.message + ").";
  });
})();
