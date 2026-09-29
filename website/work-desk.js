(function () {
  const workers = [
    ["Buddy", "buddy.html"],
    ["Content", "content-desk.html"],
    ["Games", "game-builder.html"],
    ["Maps", "world-map.html"],
    ["Guardrails", "guardrails.html"],
    ["Models", "model-lab.html"]
  ];
  const select = document.getElementById("worker");
  workers.forEach(function (row) {
    const option = document.createElement("option");
    option.value = row[1];
    option.textContent = row[0];
    select.append(option);
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
      item.append(". Saved here only.");
      list.append(item);
    });
  }
  document.getElementById("assign").addEventListener("submit", function (event) {
    event.preventDefault();
    const rows = saved();
    const worker = select.options[select.selectedIndex];
    rows.push({ job: document.getElementById("job").value.trim(), worker: worker.textContent, page: worker.value });
    localStorage.setItem(key, JSON.stringify(rows));
    document.getElementById("job").value = "";
    draw();
  });
  draw();
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
    const page = "<!DOCTYPE html><html><body style='font-family:sans-serif'>" + body + "</body></html>";
    document.getElementById("preview").srcdoc = page;
  });
})();
