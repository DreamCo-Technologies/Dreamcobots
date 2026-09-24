(function () {
  const lead = document.getElementById("repo-lead");
  const box = document.getElementById("repo-tree");
  const search = document.getElementById("repo-search");
  const repo = "DreamCo-Technologies/Dreamcobots";
  let files = [];

  function linkFile(path) {
    const row = document.createElement("p");
    const github = document.createElement("a");
    github.href = "https://github.com/" + repo + "/blob/main/" + path;
    github.textContent = path;
    github.target = "_blank";
    github.rel = "noopener noreferrer";
    row.append(github);
    if (path.startsWith("website/") && path.endsWith(".html")) {
      const page = document.createElement("a");
      page.href = path.slice("website/".length);
      page.textContent = " On this site";
      row.append(page);
    }
    return row;
  }

  function show(query) {
    const q = (query || "").trim().toLowerCase();
    box.replaceChildren();
    if (q) {
      const hits = files.filter(function (path) { return path.toLowerCase().indexOf(q) !== -1; }).slice(0, 80);
      lead.textContent = hits.length + " shown of " + files.length + " files. Search again to narrow the rest.";
      hits.forEach(function (path) { box.append(linkFile(path)); });
      return;
    }
    const groups = {};
    files.forEach(function (path) {
      const name = path.indexOf("/") === -1 ? "(top)" : path.split("/")[0];
      groups[name] = (groups[name] || 0) + 1;
    });
    lead.textContent = files.length + " files in the latest main tree. Open a folder, or search a name.";
    Object.keys(groups).sort(function (a, b) { return groups[b] - groups[a]; }).forEach(function (name) {
      const details = document.createElement("details");
      const summary = document.createElement("summary");
      summary.textContent = name + " (" + groups[name] + ")";
      details.append(summary);
      details.addEventListener("toggle", function () {
        if (!details.open || details.dataset.filled) return;
        details.dataset.filled = "yes";
        files.filter(function (path) {
          return name === "(top)" ? path.indexOf("/") === -1 : path.startsWith(name + "/");
        }).forEach(function (path) { details.append(linkFile(path)); });
      });
      box.append(details);
    });
  }

  function use(list, source) {
    files = list;
    show("");
    lead.textContent = files.length + " files from " + source + ". Open a folder, or search a name.";
  }

  fetch("https://api.github.com/repos/" + repo + "/git/trees/main?recursive=1", { headers: { Accept: "application/vnd.github+json" } })
    .then(function (response) { return response.ok ? response.json() : Promise.reject(); })
    .then(function (data) {
      const list = (data.tree || []).filter(function (item) { return item.type === "blob"; }).map(function (item) { return item.path; });
      if (!list.length) throw new Error("empty");
      use(list, "GitHub just now");
    })
    .catch(function () {
      fetch("data/repo-summary.json").then(function (response) { return response.json(); }).then(function (data) {
        lead.textContent = "GitHub did not answer, so this is the saved folder list from the last publish. " + data.files + " files across " + data.groups.length + " folders.";
        data.groups.forEach(function (group) {
          const row = document.createElement("p");
          const link = document.createElement("a");
          link.href = "https://github.com/" + repo + "/tree/main/" + group.name;
          link.textContent = group.name + " (" + group.files + " files)";
          row.append(link);
          box.append(row);
        });
      }).catch(function () {
        lead.textContent = "The repository list did not load.";
      });
    });

  search.addEventListener("input", function () { if (files.length) show(search.value); });
})();
