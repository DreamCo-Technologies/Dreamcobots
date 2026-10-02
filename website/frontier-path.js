(function () {
  fetch("data/frontier-path.json")
    .then(function (response) { return response.json(); })
    .then(function (data) {
      document.getElementById("lead").textContent = data.ready_study_methods.length + " study procedures finish. This repository does not compete with a frontier model. No weight was trained.";
      data.ready_study_methods.forEach(function (name) {
        const item = document.createElement("li");
        item.textContent = name.replaceAll("_", " ");
        document.getElementById("ready").append(item);
      });
      data.missing.forEach(function (line) {
        const item = document.createElement("li");
        item.textContent = line;
        document.getElementById("missing").append(item);
      });
    })
    .catch(function () {
      document.getElementById("lead").textContent = "The frontier scan did not load.";
    });
})();
