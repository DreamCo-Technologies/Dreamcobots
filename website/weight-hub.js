(function () {
  const box = document.getElementById("settings");
  const status = document.getElementById("weight-status");
  const refused = ["copy gpt", "copy claude", "distill gpt", "distill claude", "proprietary weights", "closed weights"];
  const slug = /^[A-Za-z0-9_.-]+\/[A-Za-z0-9_.-]+$/;
  let catalog = [];

  function say(text) { status.textContent = text; }

  function field(item) {
    const wrap = document.createElement("label");
    wrap.className = "card";
    const title = document.createElement("strong");
    title.textContent = item.plain;
    const help = document.createElement("p");
    help.textContent = item.what;
    wrap.append(title, help);
    const locked = item.id === "trust_remote_code" || item.id === "closed_weights" || item.id === "allow_custom_code";
    let input;
    if (item.kind === "bool") {
      input = document.createElement("input");
      input.type = "checkbox";
      input.checked = Boolean(item.default);
      input.disabled = locked;
    } else if (item.kind === "choice") {
      input = document.createElement("select");
      item.choices.forEach(function (choice) {
        const option = document.createElement("option");
        option.value = choice;
        option.textContent = choice;
        if (choice === item.default) option.selected = true;
        input.append(option);
      });
    } else {
      input = document.createElement("input");
      input.type = item.kind === "number" ? "number" : "text";
      input.value = item.default;
    }
    input.dataset.id = item.id;
    wrap.append(input);
    return wrap;
  }

  function readSheet() {
    const values = {};
    box.querySelectorAll("[data-id]").forEach(function (input) {
      values[input.dataset.id] = input.type === "checkbox" ? input.checked : input.type === "number" ? Number(input.value) : input.value;
    });
    values.trust_remote_code = false;
    values.closed_weights = false;
    values.allow_custom_code = false;
    return values;
  }

  fetch("data/weight-settings.json").then(function (response) { return response.json(); }).then(function (data) {
    catalog = data.settings;
    const saved = JSON.parse(localStorage.getItem("dreamco-weight-sheet") || "null");
    const groups = [];
    catalog.forEach(function (item) {
      if (groups.indexOf(item.group) === -1) groups.push(item.group);
    });
    groups.forEach(function (group) {
      const heading = document.createElement("h2");
      heading.textContent = group;
      box.append(heading);
      catalog.filter(function (item) { return item.group === group; }).forEach(function (item) {
        const node = field(item);
        box.append(node);
        if (saved && Object.prototype.hasOwnProperty.call(saved, item.id)) {
          const input = node.querySelector("[data-id]");
          if (input.type === "checkbox") input.checked = Boolean(saved[item.id]);
          else input.value = saved[item.id];
        }
      });
    });
    say(catalog.length + " settings on the sheet. No weight file is on this site, so the sheet does not change one.");
  }).catch(function () { say("The settings list did not load."); });

  document.getElementById("save-sheet").addEventListener("click", function () {
    const values = readSheet();
    localStorage.setItem("dreamco-weight-sheet", JSON.stringify(values));
    say("Saved in this browser. Nothing was written to a weight file.");
  });

  document.getElementById("debug-form").addEventListener("submit", function (event) {
    event.preventDefault();
    const kind = document.getElementById("debug-kind").value;
    const name = document.getElementById("debug-name").value.trim();
    const goal = document.getElementById("debug-goal").value;
    const blob = (name + " " + goal).toLowerCase();
    const out = document.getElementById("debug-out");
    if (refused.some(function (phrase) { return blob.indexOf(phrase) !== -1; })) {
      out.textContent = "Buddy will not debug by copying a closed model.";
      return;
    }
    if (!slug.test(name)) {
      out.textContent = "Use owner/name.";
      return;
    }
    const steps = [
      kind === "repository" ? "Open the repository file list and the latest check results." : "Open the model card and the file list.",
      "Read the license before loading anything.",
      "Check that the id exists. Do not download weights here.",
      "Look for a config, a tokenizer, and a weight file name.",
      "Refuse remote code.",
      "Run a small held-out check on a machine you control.",
      "Write down what failed. A missing file is not a trained model.",
    ];
    const href = kind === "repository" ? "https://github.com/" + name : "https://huggingface.co/" + name;
    out.textContent = steps.map(function (step, index) { return (index + 1) + ". " + step; }).join("\n");
    const link = document.getElementById("debug-link");
    link.hidden = false;
    link.href = href;
    link.textContent = "Open " + name;
  });
})();
