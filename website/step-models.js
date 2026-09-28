(function () {
  const params = new URLSearchParams(window.location.search);
  fetch("data/step-board.json").then(function (response) { return response.json(); }).then(function (data) {
    document.getElementById("lead").textContent = data.steps.length + " steps, " + data.approved_models.length + " approved models, " + data.connections.length + " connections, " + data.apis.length + " APIs, " + data.workflows.length + " workflows, " + data.plugins + " plugins. No measured best. Nothing is called.";
    const task = document.getElementById("task");
    task.value = params.get("task") || "";
    const box = document.getElementById("steps");
    data.steps.forEach(function (step, index) {
      const row = document.createElement("p");
      const select = document.createElement("select");
      select.id = "model-" + index;
      const own = document.createElement("option");
      own.textContent = "Buddy's own code";
      select.append(own);
      data.approved_models.forEach(function (model) {
        const option = document.createElement("option");
        option.value = model.id;
        option.textContent = model.id;
        select.append(option);
      });
      const start = document.createElement("button");
      start.type = "button";
      start.className = "btn btn-outline";
      start.textContent = "Start";
      start.addEventListener("click", function () {
        const name = task.value.trim();
        if (name.length < 2) {
          document.getElementById("status").textContent = "Name the task first. Nothing was called.";
          return;
        }
        const saved = JSON.parse(localStorage.getItem("dreamco-step-models-task") || "{}");
        saved[name] = saved[name] || {};
        saved[name][step] = select.value || "Buddy's own code";
        localStorage.setItem("dreamco-step-models-task", JSON.stringify(saved));
        document.getElementById("status").textContent = step + " for " + name + " is saved as " + (select.value || "Buddy's own code") + ". Not called. There is no measured best.";
      });
      row.append(step + " ");
      row.append(select);
      row.append(start);
      box.append(row);
    });
    document.getElementById("all").addEventListener("click", function () {
      data.steps.forEach(function (step, index) {
        const select = document.getElementById("model-" + index);
        select.value = data.approved_models[index % data.approved_models.length].id;
      });
      document.getElementById("status").textContent = "Every step has an approved model selected. Nothing was called, and none is a measured best.";
    });
    function buttons(target, rows, label) {
      rows.forEach(function (row) {
        const link = document.createElement("a");
        link.className = "btn btn-outline";
        link.style.margin = "0.25rem";
        link.target = "_blank";
        link.rel = "noreferrer";
        if (label === "workflow") {
          link.href = "https://github.com/DreamCo-Technologies/Dreamcobots/blob/main/.github/workflows/" + row;
          link.textContent = row.replace(".yml", "");
        } else {
          link.href = row.page && row.page.indexOf("http") !== 0 ? row.page : row.setup_url;
          link.textContent = row.name;
        }
        target.append(link);
      });
    }
    buttons(document.getElementById("connections"), data.connections, "connection");
    buttons(document.getElementById("apis"), data.apis, "api");
    buttons(document.getElementById("workflows"), data.workflows, "workflow");
  });
})();
