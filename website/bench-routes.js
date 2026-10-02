(function () {
  function fill(select, rows) {
    rows.forEach(function (row) {
      const option = document.createElement("option");
      option.value = row.id;
      option.textContent = row.family + ": " + row.name;
      select.append(option);
    });
  }
  fetch("data/bench-routes.json").then(function (response) { return response.json(); }).then(function (data) {
    document.getElementById("lead").textContent = data.metrics.length + " metrics and " + data.frameworks.length + " test frameworks. Picking one does not run it. Live scores: " + data.live_scores + ".";
    fill(document.getElementById("metric"), data.metrics);
    fill(document.getElementById("framework"), data.frameworks);
    const saved = JSON.parse(localStorage.getItem("buddy-bench-route") || "null");
    if (saved) {
      document.getElementById("metric").value = saved.metric;
      document.getElementById("framework").value = saved.framework;
      document.getElementById("choice").textContent = "Saved on this browser only: " + saved.metric + " with " + saved.framework + ". Not run.";
    }
    document.getElementById("save").addEventListener("click", function () {
      const choice = { metric: document.getElementById("metric").value, framework: document.getElementById("framework").value };
      localStorage.setItem("buddy-bench-route", JSON.stringify(choice));
      document.getElementById("choice").textContent = "Saved on this browser only: " + choice.metric + " with " + choice.framework + ". Not run.";
    });
    if (window.BuddyAdvice) window.BuddyAdvice.show("plans");
  });
})();
