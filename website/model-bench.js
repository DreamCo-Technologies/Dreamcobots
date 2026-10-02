(function () {
  const refused = ["copy gpt", "copy claude", "distill gpt", "distill claude", "proprietary weights", "closed weights", "gpt astra", "claude mythos"];
  const idOk = /^[A-Za-z0-9][A-Za-z0-9._-]{0,80}\/[A-Za-z0-9][A-Za-z0-9._-]{0,80}$/;
  const status = document.getElementById("bench-status");
  const localOut = document.getElementById("local-out");
  const cases = [
    ["i'm new", "new"],
    ["save my work", "save"],
    ["what's broken", "broken"],
    ["plain words", "plain"],
    ["change request", "change"],
    ["ticket", "ticket"],
  ];

  function say(text) { status.textContent = text; }

  function review(modelId, goal, owns, held, openLicense) {
    const blob = (modelId + " " + goal).toLowerCase();
    if (refused.some(function (phrase) { return blob.indexOf(phrase) !== -1; })) {
      return { accepted: false, reason: "This bench will not copy or distill a closed model." };
    }
    if (!idOk.test(modelId.trim())) {
      return { accepted: false, reason: "Use a public id like organization/model-name." };
    }
    const url = "https://huggingface.co/" + modelId.trim();
    if (!(owns && held && openLicense)) {
      return { accepted: false, url: url, reason: "To plan training, you must own the data, keep a hidden test, and use a license that allows training." };
    }
    return { accepted: true, url: url, reason: "Plan accepted. Open the model on Hugging Face to try its widget. Training runs on a machine you control, not on this page." };
  }

  document.getElementById("run-local").addEventListener("click", function () {
    const lines = cases.map(function (row) {
      return row[0] + " → look for the word “" + row[1] + "” in Buddy's written replies.";
    });
    localOut.textContent = lines.join("\n") + "\nThis checked the lesson list, not a downloaded model.";
  });

  document.getElementById("bench-form").addEventListener("submit", function (event) {
    event.preventDefault();
    const result = review(
      document.getElementById("model-id").value,
      document.getElementById("goal").value,
      document.getElementById("owns").checked,
      document.getElementById("held").checked,
      document.getElementById("open-license").checked
    );
    say(result.reason);
    const link = document.getElementById("model-link");
    if (result.url) {
      link.hidden = false;
      link.href = result.url;
      link.textContent = "Open this model on Hugging Face";
    } else {
      link.hidden = true;
    }
    if (result.accepted) {
      const plans = JSON.parse(localStorage.getItem("dreamco-train-plans") || "[]");
      plans.push({ model: document.getElementById("model-id").value.trim(), at: new Date().toISOString(), trains_here: false });
      localStorage.setItem("dreamco-train-plans", JSON.stringify(plans.slice(-20)));
    }
  });
})();
