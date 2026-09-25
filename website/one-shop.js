(function () {
  const local = ["world map", "game", "idea", "dataset", "data set", "study", "notes", "benchmark", "guardrail"];
  const middlemen = ["email", "stripe", "openai", "claude", "grok", "charge", "wrapper"];
  const pages = {
    "world map": "world-map.html",
    game: "game-builder.html",
    idea: "idea.html",
    dataset: "datasets.html",
    "data set": "datasets.html",
    study: "learning-methods.html",
    notes: "note-model.html",
    benchmark: "benchmarks.html",
    guardrail: "guardrails.html"
  };

  document.getElementById("shop-form").addEventListener("submit", function (event) {
    event.preventDefault();
    const status = document.getElementById("shop-status");
    const text = document.getElementById("task").value.replace(/\s+/g, " ").trim().toLowerCase();
    if (text.length < 3) {
      status.textContent = "Name the task.";
      return;
    }
    if (middlemen.some(function (word) { return text.indexOf(word) !== -1; })) {
      status.textContent = "Buddy does not hand this to another company.";
      return;
    }
    const key = local.find(function (word) { return text.indexOf(word) !== -1; });
    if (!key) {
      status.textContent = "Buddy's own code does not do that task. No wrapper was called.";
      return;
    }
    status.textContent = "Buddy can do this here. No wrapper was called. ";
    const link = document.createElement("a");
    link.href = pages[key];
    link.textContent = "Open it";
    status.append(link);
  });
})();
