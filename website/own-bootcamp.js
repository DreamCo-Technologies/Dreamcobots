(function () {
  const stolen = ["distill", "copy the page", "download the page", "full transcript"];
  const status = document.getElementById("view-status");

  document.getElementById("search-form").addEventListener("submit", function (event) {
    event.preventDefault();
    const query = document.getElementById("query").value.trim();
    window.open("https://duckduckgo.com/?q=" + encodeURIComponent(query + " free to read"), "_blank", "noopener");
  });

  document.getElementById("view-form").addEventListener("submit", function (event) {
    event.preventDefault();
    const notes = [];
    document.getElementById("views").value.split("\n").forEach(function (line) {
      const parts = line.split("|");
      if (parts.length < 2) return;
      const text = parts[0].replace(/\s+/g, " ").trim();
      const source = parts.slice(1).join("|").trim();
      notes.push({ text: text, source: source });
    });
    const own = document.getElementById("own").value.replace(/\s+/g, " ").trim();
    const blob = notes.map(function (item) { return item.text; }).concat([own]).join(" ").toLowerCase();
    const list = document.getElementById("source-list");
    list.replaceChildren();
    if (stolen.some(function (phrase) { return blob.indexOf(phrase) !== -1; })) {
      status.textContent = "Do not copy or download the page. Cite it and write your own line.";
      return;
    }
    const good = notes.filter(function (item) {
      try {
        const url = new URL(item.source);
        return item.text.length >= 20 && (url.protocol === "http:" || url.protocol === "https:");
      } catch (error) {
        return false;
      }
    });
    if (good.length < 10) {
      status.textContent = "Each of 10 views needs its own sentence and its own source link.";
      return;
    }
    if (own.length < 20 || good.some(function (item) { return item.text === own; })) {
      status.textContent = "Your own line has to be new. It cannot repeat a view.";
      return;
    }
    good.slice(0, 10).forEach(function (item) {
      const row = document.createElement("li");
      const link = document.createElement("a");
      link.href = item.source;
      link.textContent = item.source;
      link.target = "_blank";
      link.rel = "noopener noreferrer";
      row.append(link);
      list.append(row);
    });
    status.textContent = "Kept 10 sources and your own line. No page was downloaded, and no weight was trained.";
  });

  const box = document.getElementById("settings");
  fetch("data/weight-settings.json").then(function (response) { return response.json(); }).then(function (data) {
    const saved = JSON.parse(localStorage.getItem("dreamco-model-settings") || "{}");
    document.getElementById("settings-lead").textContent = data.settings.length + " settings. Defaults stay until you change them. Nothing here trains.";
    data.settings.forEach(function (setting) {
      const label = document.createElement("label");
      label.textContent = setting.plain + " ";
      const input = document.createElement("input");
      input.dataset.id = setting.id;
      input.value = saved[setting.id] != null ? saved[setting.id] : String(setting.default);
      label.append(input);
      const help = document.createElement("p");
      help.textContent = setting.what;
      box.append(label, help);
    });
  }).catch(function () {
    document.getElementById("settings-lead").textContent = "The settings sheet did not load.";
  });

  document.getElementById("save-settings").addEventListener("click", function () {
    const saved = {};
    box.querySelectorAll("input").forEach(function (input) { saved[input.dataset.id] = input.value; });
    localStorage.setItem("dreamco-model-settings", JSON.stringify(saved));
    document.getElementById("settings-lead").textContent = "Saved in this browser. No weight was changed.";
  });
})();
