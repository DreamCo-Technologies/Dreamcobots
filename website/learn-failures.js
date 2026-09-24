(function () {
  const status = document.getElementById("learn-status");
  const lessons = document.getElementById("lessons");
  const missing = document.getElementById("missing");
  const rows = document.getElementById("failed-rows");

  function add(box, text) {
    const item = document.createElement("p");
    item.textContent = text;
    box.append(item);
  }

  fetch("data/actions-health-report.json", { cache: "no-store" })
    .then(function (response) { return response.json(); })
    .then(function (data) {
      const summary = data.summary || {};
      const unknown = summary.runtime_unknown_workflows || 0;
      const failed = summary.runtime_failing_workflows || 0;
      status.textContent = failed + " runtime failures. " + unknown + " workflows have no runtime result. Unknown is not a pass. This is not a frontier model, and every benchmark will not be mastered by the end of 2026.";
      if ((summary.static_failing_workflows || 0) === 0) add(lessons, "The static checks passed. A static pass is not a benchmark score.");
      add(lessons, failed ? failed + " runtime failures stay on the list." : "No runtime failure is recorded.");
      if (unknown) add(lessons, unknown + " workflows have no runtime result. Unknown is not mastery.");
      [
        "A runtime result for each benchmark workflow.",
        "A weight file you are allowed to train.",
        "A hidden exam and a published score.",
        "No frontier comparison until that score exists.",
      ].forEach(function (line) { add(missing, line); });
      (data.findings || []).filter(function (row) {
        return row.goal === "benchmarks" || (row.benchmark_commands || []).length;
      }).forEach(function (row) {
        add(rows, row.filename + " — " + (row.runtime_status || "unknown"));
      });
    })
    .catch(function () {
      status.textContent = "The actions report did not load.";
    });
})();
