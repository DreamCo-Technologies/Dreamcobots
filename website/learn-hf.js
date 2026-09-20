/* 7-day Hugging Face mastery. Evidence required. No keys. */
(function () {
  const C = window.BUDDY_CHAT;
  const KEY = "buddy.hf-week.v1";
  const $ = (id) => document.getElementById(id);

  function load() {
    try {
      const parsed = JSON.parse(localStorage.getItem(KEY) || "{}");
      return parsed && typeof parsed === "object" ? { start: parsed.start, days: parsed.days || {} } : { days: {} };
    } catch {
      return { days: {} };
    }
  }
  function save(state) {
    localStorage.setItem(KEY, JSON.stringify(state));
  }
  function dayLog(state, day) {
    return state.days[String(day)] || { drills: [], evidence: "", pretest: "", posttest: "" };
  }
  function complete(plan, log) {
    return plan.drills.every((d) => log.drills.includes(d.id)) && (log.evidence || "").trim().length >= 8;
  }

  function render() {
    const state = load();
    const done = C.week.filter((d) => complete(d, dayLog(state, d.day))).length;
    $("stat-days").textContent = `${done}/7`;
    $("stat-hours").textContent = "22.5h";
    $("stat-paths").textContent = String(C.paths.length);
    const day = Number($("week-day").value || "1");
    const plan = C.week.find((d) => d.day === day) || C.week[0];
    const log = dayLog(state, plan.day);
    const path = C.paths.find((p) => p.id === plan.pathId);
    $("week-title").textContent = `Day ${plan.day} · ${plan.title}`;
    $("week-thesis").textContent = plan.thesis;
    $("week-pre").textContent = plan.pretest;
    $("week-post").textContent = plan.posttest;
    $("week-need").textContent = plan.evidence;
    $("week-path").innerHTML = path
      ? `<strong>${path.name}</strong><p>${path.buddy}</p><ol>${path.steps.map((s) => `<li>${s}</li>`).join("")}</ol><p><a href="${path.href}" target="_blank" rel="noopener">Hub docs</a></p>`
      : "";
    $("week-drills").innerHTML = plan.drills.map((d) => {
      const on = log.drills.includes(d.id);
      return `<article class="desk-card"><strong>${d.name}</strong><p>${d.how}</p>
        <button type="button" data-drill="${d.id}" class="${on ? "primary" : ""}">${on ? "Done" : "Mark drill"}</button></article>`;
    }).join("");
    $("week-evidence").value = log.evidence;
    $("week-pre-in").value = log.pretest;
    $("week-post-in").value = log.posttest;
    $("week-status").textContent = complete(plan, log) ? "Day complete" : "Evidence still open";
    $("week-status").className = "desk-status " + (complete(plan, log) ? "healthy" : "watch");
  }

  function patch(mut) {
    const state = load();
    if (!state.start) state.start = new Date().toISOString();
    const day = Number($("week-day").value || "1");
    const log = Object.assign({ drills: [], evidence: "", pretest: "", posttest: "" }, state.days[String(day)] || {});
    mut(log);
    state.days[String(day)] = log;
    save(state);
    render();
  }

  $("week-day").innerHTML = C.week.map((d) => `<option value="${d.day}">Day ${d.day} · ${d.title}</option>`).join("");
  $("week-day").addEventListener("change", render);
  $("week-save").addEventListener("click", () => patch((log) => {
    log.evidence = $("week-evidence").value.slice(0, 800);
    log.pretest = $("week-pre-in").value.slice(0, 400);
    log.posttest = $("week-post-in").value.slice(0, 400);
  }));
  document.addEventListener("click", (e) => {
    const t = e.target;
    if (!(t instanceof HTMLElement) || !t.dataset.drill) return;
    patch((log) => {
      if (log.drills.includes(t.dataset.drill)) log.drills = log.drills.filter((x) => x !== t.dataset.drill);
      else log.drills = log.drills.concat(t.dataset.drill);
    });
  });
  $("path-list").innerHTML = C.paths.map((p) =>
    `<article class="desk-card"><strong>${p.name}</strong><p>${p.vsHub}</p><p>${p.buddy}</p></article>`
  ).join("");
  render();
})();
