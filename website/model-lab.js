(function () {
  fetch("data/model-lab.json").then(function (response) { return response.json(); }).then(function (data) {
    document.getElementById("lead").textContent = data.models.length + " models to look up. Scored: " + data.scored_models + ". Frontier rows are links, not a test.";
    const query = document.getElementById("query");
    const list = document.getElementById("models");
    function draw() {
      const text = query.value.trim().toLowerCase();
      list.replaceChildren();
      data.models.filter(function (row) {
        return text.length < 2 || (row.label + " " + row.access + " " + row.id).toLowerCase().indexOf(text) !== -1;
      }).forEach(function (row) {
        const item = document.createElement("li");
        const link = document.createElement("a");
        link.href = row.source;
        link.target = "_blank";
        link.rel = "noreferrer";
        link.textContent = row.label;
        item.append(link);
        item.append(" — " + row.access + ". No score.");
        list.append(item);
      });
    }
    query.addEventListener("input", draw);
    draw();
    document.getElementById("scan").textContent = data.scan.bot_files + " bot files and " + data.scan.resource_files + " resource files. Missing ranges " + data.scan.missing_resource_ranges.join(" and ") + ". Fits the whole vision: no.";
    data.wrapper_lessons.rows.forEach(function (row) {
      const item = document.createElement("li");
      item.textContent = row.task + " — " + row.lesson;
      document.getElementById("lessons").append(item);
    });
    document.getElementById("pick").addEventListener("submit", function (event) {
      event.preventDefault();
      const choice = document.getElementById("choice").value.trim();
      const known = data.models.some(function (row) { return row.id === choice; });
      document.getElementById("result").textContent = known ? "Your choice is " + choice + ". It was not called, and it has no score." : "That id is not in the lookup. Nothing was called.";
    });
    document.getElementById("best").addEventListener("click", function () {
      document.getElementById("result").textContent = "No recorded score exists for this step, so there is no best model. A frontier test has not been run.";
    });
  });
})();
