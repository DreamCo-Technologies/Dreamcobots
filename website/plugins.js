(function () {
  fetch("data/plugins.json").then(function (response) { return response.json(); }).then(function (data) {
    document.getElementById("lead").textContent = data.plugins + " plugins. " + data.industries + " industries and " + data.apps + " apps. Installed: no.";
    const kind = document.getElementById("kind");
    const list = document.getElementById("rows");
    function draw() {
      list.replaceChildren();
      data.items.filter(function (row) { return kind.value === "all" || row.kind === kind.value; }).forEach(function (row) {
        const item = document.createElement("li");
        item.textContent = row.kind + ": " + row.name + " (" + row.domain.replaceAll("_", " ") + "). Not installed.";
        list.append(item);
      });
    }
    kind.addEventListener("change", draw);
    draw();
  });
})();
