(function () {
  const box = document.getElementById("hub");
  const search = document.getElementById("hub-search");
  const count = document.getElementById("hub-count");
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
    note.textContent = item.github ? "GitHub calls this " + item.github + ". " + item.say : item.say;
    article.append(title, note);
    return article;
  }

  function show(query) {
    const q = (query || "").trim().toLowerCase();
    box.replaceChildren();
    let shown = 0;
    ["lanes", "marketplace", "services", "repo"].forEach(function (key) {
      const rows = (data[key] || []).filter(function (item) {
        const blob = (item.plain + " " + item.github + " " + item.say).toLowerCase();
        return !q || blob.indexOf(q) !== -1;
      });
      if (!rows.length) return;
      const heading = document.createElement("h2");
      heading.textContent = { lanes: "Four desks", marketplace: "Marketplace connections", services: "GitHub services", repo: "Resources already in this repo" }[key];
      box.append(heading);
      rows.forEach(function (item) {
        box.append(card(item));
        shown += 1;
      });
    });
    count.textContent = shown + " shown. GitHub still runs its own services.";
  }

  fetch("data/github-hub.json")
    .then(function (response) { return response.json(); })
    .then(function (json) {
      data = json;
      show("");
      search.addEventListener("input", function () { show(search.value); });
    })
    .catch(function () {
      count.textContent = "The hub list did not load.";
    });
})();
