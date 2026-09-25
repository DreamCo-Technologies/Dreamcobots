(function () {
  const box = document.getElementById("bench");
  const lead = document.getElementById("bench-lead");

  function card(title, body) {
    const article = document.createElement("article");
    article.className = "card";
    const heading = document.createElement("h2");
    heading.textContent = title;
    const text = document.createElement("p");
    text.textContent = body;
    article.append(heading, text);
    return article;
  }

  function section(title) {
    const heading = document.createElement("h2");
    heading.textContent = title;
    box.append(heading);
  }

  Promise.all([
    fetch("data/benchmarks.json").then(function (response) { return response.json(); }),
    fetch("data/benchmark-index.json").then(function (response) { return response.json(); }),
  ]).then(function (payload) {
    const score = payload[0];
    const index = payload[1];
    const summary = index.summary || {};
    lead.textContent = "Measured here: " + score.passed + " of " + score.checks + " gate checks passed. Catalog: " + summary.repositorySuites + " suites and " + summary.benchmarkPrograms + " programs. Live program runs completed: " + summary.liveBenchmarkPrograms + ". A catalog entry is not a score.";

    section("Measured on our code");
    (score.goals || []).forEach(function (goal) {
      box.append(card(goal.goal, goal.met ? "Met" : "Not met"));
    });
    (score.rows || []).forEach(function (row) {
      box.append(card(row.name, row.passed ? "Passed" : "Failed"));
    });

    section("Repository suites");
    (index.repositorySuites || []).forEach(function (suite) {
      const page = suite.public_page ? " Page: " + suite.public_page + "." : "";
      box.append(card(suite.name, suite.status + ". Tests listed: " + (suite.test_count || 0) + "." + page));
    });

    section("Programs");
    (index.programs || []).forEach(function (program) {
      box.append(card(program.name, "Live results completed: " + program.live_results_completed + ". Data: " + program.public_data));
    });

    section("Open these pages");
    [
      ["datasets.html", "Free datasets"],
      ["benchmark-tracker.html", "Benchmark tracker"],
      ["benchmark-scanner.html", "Benchmark scanner"],
      ["benchmark-candidate-finder.html", "Candidate finder"],
      ["model-bench.html", "Model bench"],
      ["test-center.html", "Test center"],
    ].forEach(function (item) {
      const article = document.createElement("article");
      article.className = "card";
      const link = document.createElement("a");
      link.href = item[0];
      link.textContent = item[1];
      article.append(link);
      box.append(article);
    });
  }).catch(function () {
    lead.textContent = "The benchmark list did not load.";
  });
})();
