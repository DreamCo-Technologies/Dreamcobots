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

  const wikiSummary = document.getElementById("wiki-learning-summary");
  const wikiGoals = document.getElementById("wiki-goal-links");
  const wikiBenchmarks = document.getElementById("wiki-benchmark-links");
  if (wikiSummary && wikiGoals && wikiBenchmarks) {
    function renderTargetLinks(container, headingText, rows, idKey) {
      const heading = document.createElement("h3");
      heading.textContent = headingText;
      container.append(heading);
      const list = document.createElement("ul");
      rows.forEach(function (row) {
        const item = document.createElement("li");
        const link = document.createElement("a");
        const url = new URL(row.wikipedia_search_url);
        if (url.origin !== "https://en.wikipedia.org" || !url.pathname.startsWith("/w/index.php") || !url.searchParams.has("search")) return;
        link.href = url.href;
        link.target = "_blank";
        link.rel = "noopener noreferrer";
        link.textContent = row.label + " (" + row[idKey] + ")";
        item.append(link);
        list.append(item);
      });
      container.append(list);
    }

    fetch("data/wikipedia-learning-target-map.json").then(function (response) {
      if (!response.ok) throw new Error("map unavailable");
      return response.json();
    }).then(function (map) {
      wikiSummary.textContent = map.goal_count + " goals and " + map.benchmark_count + " benchmarks have Wikipedia discovery links. Training remains governed separately.";
      renderTargetLinks(wikiGoals, "Goals", map.goals || [], "goal_id");
      renderTargetLinks(wikiBenchmarks, "Benchmarks", map.benchmarks || [], "benchmark_id");
    }).catch(function () {
      wikiSummary.textContent = "Wikipedia goal and benchmark links are unavailable.";
    });
  }
})();
