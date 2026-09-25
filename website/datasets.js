(function () {
  const rows = document.getElementById("rows");
  const category = document.getElementById("category");
  let data = [];
  let shown = 0;

  function card(row) {
    const article = document.createElement("article");
    article.className = "card";
    const title = document.createElement("h2");
    title.textContent = row.name;
    const text = document.createElement("p");
    text.textContent = row.category + ". " + row.license + ". " + (row.note || "Open listing. The file is not stored here.");
    const link = document.createElement("a");
    link.href = row.href;
    link.textContent = "Open the source";
    link.target = "_blank";
    link.rel = "noopener noreferrer";
    article.append(title, text, link);
    return article;
  }

  function hidden() {
    return (document.getElementById("hide").value || "").toLowerCase().split(",").map(function (item) { return item.trim(); }).filter(Boolean);
  }

  function paint() {
    const wanted = category.value;
    const blocked = hidden();
    const list = data.filter(function (row) {
      const org = (row.name.split("/")[0] || "").toLowerCase();
      return (wanted === "all" || row.category === wanted) && blocked.indexOf(org) === -1;
    });
    rows.replaceChildren();
    list.slice(0, shown).forEach(function (row) { rows.append(card(row)); });
    document.getElementById("more").hidden = shown >= list.length;
  }

  document.getElementById("more").addEventListener("click", function () {
    shown += 40;
    paint();
  });
  category.addEventListener("change", function () {
    shown = 40;
    paint();
  });
  const hide = document.getElementById("hide");
  hide.value = localStorage.getItem("dreamco-hide-companies") || "";
  hide.addEventListener("change", function () {
    localStorage.setItem("dreamco-hide-companies", hide.value.trim());
    shown = 40;
    paint();
  });

  Promise.all([
    fetch("data/free-datasets.json").then(function (response) { return response.json(); }),
    fetch("data/open-platforms.json").then(function (response) { return response.json(); }),
  ]).then(function (payload) {
    const sets = payload[0];
    const tools = payload[1];
    data = sets.datasets;
    const names = ["all"].concat(Array.from(new Set(data.map(function (row) { return row.category; }))).sort());
    names.forEach(function (name) {
      const option = document.createElement("option");
      option.value = name;
      option.textContent = name;
      category.append(option);
    });
    const ready = data.filter(function (row) { return row.train; }).length;
    document.getElementById("data-lead").textContent = data.length + " open datasets in " + (names.length - 1) + " categories, plus " + tools.resources.length + " free Hugging Face and GitHub resources. " + ready + " are marked for training. Buddy has not read the files. " + sets.rule;
    tools.resources.forEach(function (row) { document.getElementById("platforms").append(card(row)); });
    shown = 40;
    paint();
  }).catch(function () {
    document.getElementById("data-lead").textContent = "The study list did not load.";
  });
})();
