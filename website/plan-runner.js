(function () {
  function bootcamp(unit) {
    const missing = ["capability_id", "objective", "benchmark", "provenance"].filter(function (key) { return !String(unit[key] || "").trim(); });
    return { status: missing.length ? "blocked" : "ready", missing: missing, trained: false };
  }
  function verify(required, known, simulated) {
    const have = new Set(known);
    const missing = required.filter(function (asset) { return asset && !have.has(asset); });
    const issues = [];
    if (missing.length) issues.push("Missing assets: " + missing.join(", "));
    if (!simulated) issues.push("Plan has not completed a simulation preflight");
    return { issues: issues, approved: false };
  }
  function utility(step) {
    if (step.probability < 0 || step.probability > 1 || step.cost < 0) return { accepted: false, reason: "Probability must be 0 to 1 and cost cannot be negative." };
    return { accepted: true, expected_utility: Math.round((step.probability * step.utility - step.cost) * 10000) / 10000, executed: false };
  }

  document.getElementById("lesson-form").addEventListener("submit", function (event) {
    event.preventDefault();
    const result = bootcamp({
      capability_id: document.getElementById("capability").value,
      objective: document.getElementById("objective").value,
      benchmark: document.getElementById("benchmark").value,
      provenance: document.getElementById("provenance").value
    });
    document.getElementById("lesson-status").textContent = result.status === "ready" ? "Ready to teach. Nothing is trained." : "Blocked. Missing: " + result.missing.join(", ");
  });
  document.getElementById("verify-form").addEventListener("submit", function (event) {
    event.preventDefault();
    const needed = document.getElementById("needed").value.split(",").map(function (item) { return item.trim(); }).filter(Boolean);
    const known = document.getElementById("known").value.split(",").map(function (item) { return item.trim(); }).filter(Boolean);
    const result = verify(needed, known, document.getElementById("simulated").checked);
    document.getElementById("verify-status").textContent = (result.issues.join(" ") || "No missing piece.") + " Not approved to act.";
  });
  document.getElementById("score-form").addEventListener("submit", function (event) {
    event.preventDefault();
    const result = utility({
      probability: Number(document.getElementById("chance").value),
      utility: Number(document.getElementById("value").value),
      cost: Number(document.getElementById("cost").value)
    });
    document.getElementById("score-status").textContent = result.accepted ? "Expected value " + result.expected_utility + ". Not executed." : result.reason;
  });

  fetch("data/built-plans.json").then(function (response) { return response.json(); }).then(function (data) {
    document.getElementById("lead").textContent = data.counts.lora + " LoRA plans, " + data.counts.customers + " customer plans, and " + data.counts.frontier_steps + " frontier steps. No weights are trained. The repository is not production ready.";
    data.lora.forEach(function (row) {
      const item = document.createElement("li");
      item.textContent = row.recipe.id + " — plan only. CI will not launch it.";
      document.getElementById("lora").append(item);
    });
    data.customers.forEach(function (row) {
      const item = document.createElement("li");
      item.textContent = row.track + ": " + row.base + " Trained weights: no.";
      document.getElementById("customers").append(item);
    });
    data.frontier_loop.forEach(function (step) {
      const item = document.createElement("li");
      item.textContent = step;
      document.getElementById("loop").append(item);
    });
  });
})();
