(function () {
  fetch("data/plugins.json").then(function (response) { return response.json(); }).then(function (data) {
    document.getElementById("lead").textContent = data.plugins + " plugins. Installed: no. Called: no.";
    const query = document.getElementById("query");
    const list = document.getElementById("rows");
    function draw() {
      const text = query.value.trim().toLowerCase();
      list.replaceChildren();
      if (text.length < 2) {
        const item = document.createElement("li");
        item.textContent = "Type at least two letters. The full catalog is too large to list on one screen.";
        list.append(item);
        return;
      }
      const found = data.items.filter(function (row) {
        return (row.name + " " + row.domain + " " + row.action).toLowerCase().indexOf(text) !== -1;
      }).slice(0, 40);
      if (!found.length) {
        const item = document.createElement("li");
        item.textContent = "No match in the catalog.";
        list.append(item);
        return;
      }
      found.forEach(function (row) {
        const item = document.createElement("li");
        item.textContent = row.kind + ": " + (row.action ? row.action + " / " : "") + row.name + " (" + row.domain + "). Not installed. ";
        const link = document.createElement("a");
        link.href = "step-models.html?task=" + encodeURIComponent(row.action ? row.action + " " + row.name : row.name);
        link.textContent = "Steps";
        item.append(link);
        list.append(item);
      });
    }
    query.addEventListener("input", draw);
    draw();
  });
})();
