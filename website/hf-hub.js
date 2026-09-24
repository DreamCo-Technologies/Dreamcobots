(function () {
  const box = document.getElementById("hub");
  const search = document.getElementById("hub-search");
  const count = document.getElementById("hub-count");
  const labels = { lanes: "Four desks", tasks: "Model tasks", libraries: "Libraries and services", resources: "Hugging Face resources" };
  let data = null;

  function card(item) {
    const article = document.createElement("article");
    article.className = "card";
    const title = document.createElement("h2");
    const link = document.createElement("a");
    link.href = item.href;
    link.textContent = item.plain;
    if (/^https?:/i.test(item.href)) {
      link.target = "_blank";
      link.rel = "noopener noreferrer";
    }
    title.append(link);
    const note = document.createElement("p");
    note.textContent = item.say;
    article.append(title, note);
    return article;
  }

  function show(query) {
    const q = (query || "").trim().toLowerCase();
    box.replaceChildren();
    let shown = 0;
    Object.keys(labels).forEach(function (key) {
      const rows = (data[key] || []).filter(function (item) {
        return !q || (item.plain + " " + item.say).toLowerCase().indexOf(q) !== -1;
      });
      if (!rows.length) return;
      const heading = document.createElement("h2");
      heading.textContent = labels[key];
      box.append(heading);
      rows.forEach(function (item) { box.append(card(item)); shown += 1; });
    });
    count.textContent = shown + " shown. Hugging Face still hosts the models.";
  }

  fetch("data/hf-hub.json").then(function (response) { return response.json(); }).then(function (json) {
    data = json;
    show("");
    search.addEventListener("input", function () { show(search.value); });
  }).catch(function () { count.textContent = "The hub list did not load."; });
})();
