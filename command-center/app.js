const tabs = ["Dashboard", "Buddy", "Bots", "Deals", "Capabilities", "Memory", "Schedule", "Vibe", "Legal"];
let current = "Dashboard";

async function api(path, opts) {
  try {
    const res = await fetch(path, opts);
    if (!res.ok) throw new Error("bad status");
    return await res.json();
  } catch {
    return localApi(path, opts);
  }
}

let localBots = null;
async function getLocalBots() {
  if (localBots) return localBots;
  const res = await fetch("command-center/bots.json");
  localBots = await res.json();
  return localBots;
}

async function localApi(path, opts) {
  const bots = await getLocalBots();
  if (path === "/api/health") return { status: "ok", replit: false, bots: bots.length, mode: "local" };
  if (path.startsWith("/api/bots")) return { total: bots.length, bots: bots.slice(0, 200) };
  if (path === "/api/export/investor") return { dealsScored: 0, memoryItems: 0, revenue: "not connected" };
  if (path === "/api/capabilities") return { capabilities: [{ name: "Buddy router", status: "live" }, { name: "Voice", status: "needs_key" }] };
  if (path === "/api/memory") return { memory: [] };
  if (path === "/api/schedule") return { schedules: [] };
  if (path === "/api/legal/terms") return { title: "Terms", text: "No Replit required. No guaranteed revenue." };
  if (path === "/api/legal/privacy") return { title: "Privacy", text: "Local mode keeps data in this browser." };
  if (path === "/api/buddy/chat") {
    const message = JSON.parse(opts.body).message.toLowerCase();
    const target = message.includes("deal") ? "DealAnalyzer" : message.includes("build") ? "BuildBot" : "BuddyAI";
    return { reply: `Local mode. Matched ${target}.`, engine: "local-router" };
  }
  return { ok: true, mode: "local" };
}

function setTab(name) {
  current = name;
  render();
}

async function render() {
  document.getElementById("tabs").innerHTML = tabs.map((t) => `<button class="tab ${t===current?"active":""}" onclick="setTab('${t}')">${t}</button>`).join("");
  const app = document.getElementById("app");
  if (current === "Dashboard") {
    const health = await api("/api/health");
    const exportData = await api("/api/export/investor");
    app.innerHTML = `<div class="grid">
      <div class="card"><h2>Health</h2><p class="ok">${health.status}</p><p>${health.bots} bots cataloged</p></div>
      <div class="card"><h2>Live Buddy</h2><p><a href="https://dreamco-technologies.github.io/Dreamcobots/" target="_blank">Official Pages</a></p><p><a href="https://dreamco.vercel.app/" target="_blank">Vercel Buddy</a></p><p><a href="https://github.com/DreamCo-Technologies/DreamCo-Command-Center"" target="_blank">Vercel Buddy</a></p></div>
      <div class="card"><h2>Investor export</h2><p>Deals scored: ${exportData.dealsScored}</p><p>Memory: ${exportData.memoryItems}</p><p class="warn">Revenue: ${exportData.revenue}</p></div>
    </div>`;
  }
  if (current === "Buddy") {
    app.innerHTML = `<form id="chat"><textarea id="msg" rows="4" placeholder="Ask Buddy to route a task"></textarea><button class="primary">Send</button></form><div class="log" id="log"></div>`;
    document.getElementById("chat").onsubmit = async (e) => {
      e.preventDefault();
      const message = document.getElementById("msg").value;
      const data = await api("/api/buddy/chat", { method:"POST", headers:{"Content-Type":"application/json"}, body: JSON.stringify({ message }) });
      document.getElementById("log").innerHTML = `<p>${data.reply}</p><p>Engine: ${data.engine}</p>`;
    };
  }
  if (current === "Bots") {
    const data = await api("/api/bots?q=");
    app.innerHTML = `<input id="q" placeholder="Search bots" /><div class="grid" id="bots"></div>`;
    const draw = async () => {
      const q = document.getElementById("q").value;
      const found = await api("/api/bots?q=" + encodeURIComponent(q));
      document.getElementById("bots").innerHTML = found.bots.slice(0, 60).map((b) => `<div class="card"><strong>${b.name}</strong><p>${b.category} · ${b.status}</p><button onclick="runBot('${b.slug}')">Heartbeat</button></div>`).join("");
    };
    document.getElementById("q").oninput = draw;
    draw();
  }
  if (current === "Deals") {
    app.innerHTML = `<form id="deal"><input name="name" placeholder="Deal name" /><input name="upside" type="number" placeholder="Upside 0-100" /><input name="risk" type="number" placeholder="Risk 0-100" /><input name="urgency" type="number" placeholder="Urgency 0-100" /><input name="fit" type="number" placeholder="Fit 0-100" /><input name="owner" placeholder="Owner" /><button class="primary">Score</button></form><div class="log" id="dealOut"></div>`;
    document.getElementById("deal").onsubmit = async (e) => {
      e.preventDefault();
      const fd = new FormData(e.target);
      const body = Object.fromEntries(fd.entries());
      const data = await api("/api/deals/score", { method:"POST", headers:{"Content-Type":"application/json"}, body: JSON.stringify(body) });
      document.getElementById("dealOut").innerHTML = `<p>Score ${data.score}</p><p>${data.next}</p><p>${(data.flags||[]).join(", ")}</p>`;
    };
  }
  if (current === "Capabilities") {
    const data = await api("/api/capabilities");
    app.innerHTML = `<div class="grid">${data.capabilities.map((c) => `<div class="card"><strong>${c.name}</strong><p class="${c.status==="live"?"ok":"warn"}">${c.status}</p></div>`).join("")}</div>`;
  }
  if (current === "Memory") {
    const data = await api("/api/memory");
    app.innerHTML = `<form id="mem"><input id="text" placeholder="Save a note" /><button class="primary">Save</button></form><div class="log">${data.memory.map((m) => `<p>${m.at}: ${m.message} → ${m.routedTo}</p>`).join("") || "<p>No memory yet.</p>"}</div>`;
    document.getElementById("mem").onsubmit = async (e) => { e.preventDefault(); await api("/api/memory", { method:"POST", headers:{"Content-Type":"application/json"}, body: JSON.stringify({ text: document.getElementById("text").value }) }); render(); };
  }
  if (current === "Schedule") {
    const data = await api("/api/schedule");
    app.innerHTML = `<form id="sch"><input id="slug" placeholder="bot slug" /><input id="mins" type="number" value="60" /><button class="primary">Schedule heartbeat</button></form><div class="log">${data.schedules.map((s) => `<p>${s.slug} every ${s.everyMinutes} min</p>`).join("") || "<p>No schedules.</p>"}</div>`;
    document.getElementById("sch").onsubmit = async (e) => { e.preventDefault(); await api("/api/schedule", { method:"POST", headers:{"Content-Type":"application/json"}, body: JSON.stringify({ slug: document.getElementById("slug").value, everyMinutes: document.getElementById("mins").value }) }); render(); };
  }
  if (current === "Vibe") {
    app.innerHTML = `<form id="vibe"><select id="mode"><option>code</option><option>game</option><option>lesson</option><option>simulation</option></select><input id="prompt" placeholder="What should Buddy build?" /><button class="primary">Build</button></form><pre class="log" id="art"></pre>`;
    document.getElementById("vibe").onsubmit = async (e) => { e.preventDefault(); const data = await api("/api/vibe/build", { method:"POST", headers:{"Content-Type":"application/json"}, body: JSON.stringify({ mode: document.getElementById("mode").value, prompt: document.getElementById("prompt").value }) }); document.getElementById("art").textContent = data.artifact; };
  }
  if (current === "Legal") {
    const terms = await api("/api/legal/terms");
    const privacy = await api("/api/legal/privacy");
    app.innerHTML = `<div class="card"><h2>${terms.title}</h2><p>${terms.text}</p></div><div class="card"><h2>${privacy.title}</h2><p>${privacy.text}</p></div><button class="primary" onclick="consent()">Record adult consent for media</button>`;
  }
}

async function runBot(slug) {
  const data = await api(`/api/bots/${slug}/run`, { method: "POST" });
  alert(`${data.slug}: ${data.note} (${data.invocations})`);
}
async function consent() {
  await api("/api/consent", { method:"POST", headers:{"Content-Type":"application/json"}, body: JSON.stringify({ kind: "media", adult: true }) });
  alert("Consent recorded locally.");
}
window.setTab = setTab;
window.runBot = runBot;
window.consent = consent;
render();
