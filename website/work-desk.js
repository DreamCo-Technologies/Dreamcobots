fetch("data/worker-rules.json").then(function (response) { return response.json(); }).then(function (rules) {
  const select = document.getElementById("worker");
  const personality = document.getElementById("personality");
  const pages = {};
  rules.routes.concat([rules.fallback]).forEach(function (row) {
    if (pages[row.page]) return;
    pages[row.page] = row.worker;
    const option = document.createElement("option");
    option.value = row.page;
    option.textContent = row.worker;
    select.append(option);
  });
  rules.presets.forEach(function (row) {
    const option = document.createElement("option");
    option.value = row.id;
    option.textContent = row.name;
    personality.append(option);
  });
  function match(task) {
    const text = task.toLowerCase();
    const found = rules.routes.find(function (row) { return text.indexOf(row.word) !== -1; });
    return found || rules.fallback;
  }
  document.getElementById("build").addEventListener("click", function () {
    const job = document.getElementById("job").value.trim();
    if (job.length < 3) return;
    const row = match(job);
    select.value = row.page;
    personality.value = row.personality;
  });
  const key = "dreamco-workers";
  function saved() {
    try { return JSON.parse(localStorage.getItem(key) || "[]"); } catch (error) { return []; }
  }
  function draw() {
    const list = document.getElementById("jobs");
    list.replaceChildren();
    saved().forEach(function (row) {
      const item = document.createElement("li");
      const link = document.createElement("a");
      link.href = row.page;
      link.textContent = row.worker;
      item.append(row.job + " — ");
      item.append(link);
      item.append(" — " + row.personality + ". A setting, not a trained model.");
      list.append(item);
    });
  }
  document.getElementById("assign").addEventListener("submit", function (event) {
    event.preventDefault();
    const rows = saved();
    const worker = select.options[select.selectedIndex];
    const preset = personality.options[personality.selectedIndex];
    rows.push({ job: document.getElementById("job").value.trim(), worker: worker.textContent, page: worker.value, personality: preset.textContent });
    localStorage.setItem(key, JSON.stringify(rows));
    document.getElementById("job").value = "";
    draw();
  });
  draw();
});
document.getElementById("vibe").addEventListener("submit", function (event) {
  event.preventDefault();
  const name = document.getElementById("app").value.trim().replace(/[&<>"]/g, function (char) {
    return { "&": "&", "<": "<", ">": ">", '"': """ }[char];
  });
  const kind = document.getElementById("kind").value;
  const body = kind === "form"
    ? "<form><p>" + name + "</p><input placeholder='your answer'><button type='button'>Save later</button></form>"
    : kind === "note"
      ? "<article><h1>" + name + "</h1><p>Write this in your own words. Nothing was published.</p></article>"
      : "<h1>" + name + "</h1><ul><li>First step</li><li>Practice on a new example</li><li>Record the result</li></ul>";
  document.getElementById("preview").srcdoc = "<!DOCTYPE html><html><body style='font-family:sans-serif'>" + body + "</body></html>";
});