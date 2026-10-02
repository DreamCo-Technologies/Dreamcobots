(function () {
  const key = "dreamco-my-model";
  const saved = JSON.parse(localStorage.getItem(key) || "null");
  if (saved && saved.name) {
    document.getElementById("name").value = saved.name;
    document.getElementById("source").value = saved.source;
    document.getElementById("shared").checked = saved.shared === true;
    document.getElementById("mine").textContent = "Your model is " + saved.name + " (" + saved.source + "). Shared: " + (saved.shared ? "yes" : "no") + ". Not called.";
  }
  document.getElementById("pick").addEventListener("submit", function (event) {
    event.preventDefault();
    const choice = {
      name: document.getElementById("name").value.trim(),
      source: document.getElementById("source").value,
      shared: document.getElementById("shared").checked
    };
    if (choice.name.length < 2) return;
    localStorage.setItem(key, JSON.stringify(choice));
    document.getElementById("mine").textContent = "Your model is " + choice.name + " (" + choice.source + "). Shared: " + (choice.shared ? "yes" : "no") + ". Not called.";
  });
  fetch("data/monthly-lists.json").then(function (response) { return response.json(); }).then(function (data) {
    document.getElementById("lead").textContent = "Refreshed " + data.refreshed_on + ". " + data.resources + " resource versions. " + data.needs_practice + " tasks still need practice. Plugins called: no.";
    const list = document.getElementById("routes");
    data.failed_routes.forEach(function (row) {
      const item = document.createElement("li");
      item.textContent = row.task + " — study with " + row.kind + " plugin " + row.plugin + ". " + row.use;
      list.append(item);
    });
  });
})();
