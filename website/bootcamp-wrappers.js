(function () {
  const steps = ["lesson", "practice", "sandbox", "transfer", "score", "remediate", "regression", "evidence"];
  const sources = { huggingface: true, github: true, frontier: true };
  const key = "dreamco-step-models";
  const notesKey = "dreamco-step-notes";
  const form = document.getElementById("steps");
  const saved = JSON.parse(localStorage.getItem(key) || "{}");

  steps.forEach(function (step) {
    const row = document.createElement("p");
    const name = document.createElement("input");
    name.id = "name-" + step;
    name.placeholder = "model name, or leave blank";
    name.value = (saved[step] && saved[step].name) || "";
    const source = document.createElement("select");
    source.id = "source-" + step;
    ["huggingface", "github", "frontier"].forEach(function (item) {
      const option = document.createElement("option");
      option.textContent = item;
      source.append(option);
    });
    if (saved[step] && saved[step].source) source.value = saved[step].source;
    row.append(step + " ");
    row.append(name);
    row.append(source);
    form.append(row);
    const option = document.createElement("option");
    option.textContent = step;
    document.getElementById("note-step").append(option);
  });

  function readChoices() {
    const choices = {};
    steps.forEach(function (step) {
      choices[step] = { name: document.getElementById("name-" + step).value.trim(), source: document.getElementById("source-" + step).value, added_by_user: true };
    });
    return choices;
  }

  function show(choices) {
    const list = document.getElementById("plan");
    list.replaceChildren();
    steps.forEach(function (step) {
      const choice = choices[step] || {};
      const item = document.createElement("li");
      const named = choice.name && sources[choice.source];
      item.textContent = step + ": " + (named ? choice.name + " (" + choice.source + "), until your model finishes training" : "Buddy's own code") + ". Not called.";
      list.append(item);
    });
  }

  document.getElementById("save").addEventListener("click", function () {
    const choices = readChoices();
    localStorage.setItem(key, JSON.stringify(choices));
    show(choices);
  });
  show(saved);

  document.getElementById("note-form").addEventListener("submit", function (event) {
    event.preventDefault();
    const notes = JSON.parse(localStorage.getItem(notesKey) || "[]");
    notes.push({ step: document.getElementById("note-step").value, name: document.getElementById("note-model").value.trim(), score: Number(document.getElementById("note-score").value), ran: true });
    localStorage.setItem(notesKey, JSON.stringify(notes));
    const step = document.getElementById("note-step").value;
    const mine = notes.filter(function (note) { return note.step === step && note.ran === true; });
    const winner = mine.slice().sort(function (a, b) { return b.score - a.score; })[0];
    document.getElementById("best").textContent = step + ": your notes rank " + winner.name + " at " + winner.score + ". Buddy did not run the test.";
  });
})();
