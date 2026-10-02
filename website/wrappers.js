(function () {
  const key = "dreamco-wrappers";
  const sources = { huggingface: true, github: true, frontier: true };

  function saved() {
    try {
      const rows = JSON.parse(localStorage.getItem(key) || "[]");
      return Array.isArray(rows) ? rows : [];
    } catch (error) {
      return [];
    }
  }

  function choose(task, wrappers) {
    const text = task.replace(/\s+/g, " ").trim().toLowerCase();
    const usable = wrappers.filter(function (item) {
      const quality = Number(item.quality);
      const names = (item.tasks || []).map(function (name) { return String(name).replace(/\s+/g, " ").trim().toLowerCase(); });
      return item.added_by_user === true && sources[item.source] && quality >= 0 && quality <= 100 && names.indexOf(text) !== -1;
    });
    if (!usable.length) return { task: task, picked: "Buddy's own code", called: false };
    const best = Math.max.apply(null, usable.map(function (item) { return Number(item.quality); }));
    const tied = usable.filter(function (item) { return Number(item.quality) === best; });
    const winner = tied.find(function (item) { return item.free === true; }) || tied[0];
    return { task: task, picked: winner.name, free: winner.free === true, called: false };
  }

  document.getElementById("add-form").addEventListener("submit", function (event) {
    event.preventDefault();
    const rows = saved();
    rows.push({
      name: document.getElementById("name").value.trim(),
      source: document.getElementById("source").value,
      tasks: [document.getElementById("task").value.trim()],
      quality: Number(document.getElementById("quality").value),
      free: document.getElementById("free").checked,
      added_by_user: true
    });
    localStorage.setItem(key, JSON.stringify(rows));
    document.getElementById("name").value = "";
    document.getElementById("task").value = "";
  });

  document.getElementById("ask-form").addEventListener("submit", function (event) {
    event.preventDefault();
    const list = document.getElementById("picks");
    list.replaceChildren();
    const tasks = document.getElementById("ask").value.split("\n").map(function (line) { return line.trim(); }).filter(Boolean);
    tasks.forEach(function (task) {
      const pick = choose(task, saved());
      const item = document.createElement("li");
      item.textContent = task + ": " + pick.picked + (pick.free ? " (free)" : "") + ". Not called.";
      list.append(item);
    });
  });
})();
