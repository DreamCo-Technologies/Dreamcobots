(function () {
  const LANES = [
    { id: "detect", name: "Detect", job: "Fingerprint failures. Refuse fake-green.", existing: "actions-failure-sweep.yml, keep-green.yml", never: "Rewriting old failed Actions to green." },
    { id: "branch", name: "Branch", job: "Score every branch against main.", existing: "branch-health-daily.yml", never: "Force-merge to main." },
    { id: "pr", name: "Pull requests", job: "Replay clean diffs onto current main.", existing: "pr-recovery-engine.yml", never: "Silent discard of conflicts." },
    { id: "actions", name: "Actions / CI", job: "Replay relevant failed jobs only.", existing: "actions-failure-watch.yml", never: "Weakening tests to pass." },
    { id: "pages", name: "Pages / original site", job: "Keep buddy.html as home.", existing: "pages.yml overlay", never: "A second Buddy home." },
    { id: "runtime", name: "Buddy runtime", job: "Chat + unique free model per step.", existing: "buddy.js / Command", never: "Claiming trained frontier weights." },
    { id: "catalog", name: "Catalog / evidence", job: "JSON contracts. Missing harness stays blocked.", existing: "website/data/*", never: "Counting yellow as green." },
    { id: "safety", name: "Safety", job: "Money, secrets, outreach stay gated.", existing: "SECURITY.md", never: "Keys in Pages JS. Auto outreach." },
  ];

  const SEED = [
    { title: "Pages must keep original Buddy chat as home", lane: "pages", state: "PLANNED", next: "Merge the Pages overlay." },
    { title: "0 production-ready divisions", lane: "catalog", state: "BLOCKED", next: "Certification on current main. Inventory is not a pass." },
    { title: "500-benchmark harness is incomplete", lane: "catalog", state: "BLOCKED", next: "Keep blocked until a current harness run exists." },
    { title: "Live Stripe / payouts stay off", lane: "safety", state: "WONT_FIX", next: "Human vault + exact charge approval." },
    { title: "Teacher miss still answers locally", lane: "runtime", state: "VERIFYING", next: "Premium on a hosted app only if Grok is needed." },
    { title: "Open PRs may conflict with main", lane: "pr", state: "TRIAGED", next: "Conflict team updates. Never force-merge." },
  ];

  function route(text) {
    const t = text.toLowerCase();
    if (/stripe|payment|secret|oauth|outreach|charge/.test(t)) return "safety";
    if (/buddy\.html|pages|overlay|website/.test(t)) return "pages";
    if (/\bpr\b|conflict|merge/.test(t)) return "pr";
    if (/action|workflow|ci\b/.test(t)) return "actions";
    if (/branch/.test(t)) return "branch";
    if (/benchmark|500|catalog|harness/.test(t)) return "catalog";
    if (/chat|teacher|grok|route/.test(t)) return "runtime";
    return "detect";
  }

  const grid = document.getElementById("lane-grid");
  LANES.forEach((lane) => {
    const el = document.createElement("article");
    el.className = "desk-card";
    el.innerHTML = `<strong>${lane.name}</strong><p>${lane.job}</p><p>Already: ${lane.existing}</p><p class="state-never">Never: ${lane.never}</p>`;
    grid.appendChild(el);
  });

  const list = document.getElementById("incident-list");
  const incidents = SEED.slice();

  function render() {
    list.innerHTML = "";
    incidents.forEach((inc) => {
      const el = document.createElement("article");
      el.className = "desk-card";
      const cls = inc.state === "BLOCKED" || inc.state === "WONT_FIX" ? "state-never" : inc.state === "PLANNED" || inc.state === "TRIAGED" ? "state-paid" : "state-ok";
      el.innerHTML = `<strong>${inc.title}</strong><p class="${cls}">${inc.lane} · ${inc.state}</p><p>${inc.next}</p>`;
      list.appendChild(el);
    });
  }

  document.getElementById("recover-file").addEventListener("click", () => {
    const input = document.getElementById("recover-input");
    const text = (input.value || "").trim();
    if (!text) return;
    const lane = route(text);
    const money = /stripe|payment|charge/.test(text.toLowerCase());
    incidents.unshift({
      title: text.slice(0, 160),
      lane,
      state: money ? "BLOCKED" : "DETECTED",
      next: money ? "Safety owns this. No auto-repair." : LANES.find((l) => l.id === lane).job,
    });
    input.value = "";
    render();
  });

  render();
})();
