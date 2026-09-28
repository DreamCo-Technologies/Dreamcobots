(function () {
  fetch("data/plugins-summary.json").then(function (response) { return response.json(); }).then(function (data) {
    document.getElementById("lead").textContent = data.plugins + " plugins are in the repository at " + data.full_catalog + ". They are not on this website, because the site has a size limit. Installed: no.";
    const list = document.getElementById("rows");
    const item = document.createElement("li");
    item.textContent = data.note;
    list.append(item);
  });
})();
