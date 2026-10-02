(function () {
  function add(list, text) {
    const item = document.createElement("li");
    item.textContent = text;
    list.append(item);
  }

  fetch("data/what-you-have.json")
    .then(function (response) { return response.json(); })
    .then(function (data) {
      document.getElementById("lead").textContent = data.markdown_bots + " markdown bots, " + data.catalog_bots + " bots in the original catalog, and " + data.html_pages + " GitHub Pages files. No files were moved. This is not a frontier model.";
      const mismatches = document.getElementById("mismatches");
      if (!data.mismatches.length) add(mismatches, "None.");
      data.mismatches.forEach(function (line) { add(mismatches, line); });
      const claims = document.getElementById("claims");
      if (!data.unverified_claims.length) add(claims, "None.");
      data.unverified_claims.forEach(function (line) { add(claims, line); });
      document.getElementById("plans-lead").textContent = data.plan_code + " plans are code. " + data.plan_documents + " plans are documents. Documents were not rewritten into fake runners.";
      const shown = data.plans.slice(0, 80);
      shown.forEach(function (plan) { add(document.getElementById("plans"), plan.kind + " — " + plan.path); });
      if (data.plans.length > shown.length) add(document.getElementById("plans"), (data.plans.length - shown.length) + " more plans are in the scan file.");
    })
    .catch(function () {
      document.getElementById("lead").textContent = "The scan did not load.";
    });
})();
