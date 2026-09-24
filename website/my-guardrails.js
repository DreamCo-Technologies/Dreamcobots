(function () {
  const locked = ["copy gpt", "copy claude", "distill gpt", "distill claude", "official us certification", "united states certified"];
  const secret = /ghp_|github_pat_|sk-|hf_|AKIA/;
  const status = document.getElementById("mine-status");
  const list = document.getElementById("your-rules");
  const key = "dreamco-my-guardrails";

  function load() {
    try { return JSON.parse(localStorage.getItem(key) || "[]"); }
    catch (error) { return []; }
  }
  function save(rules) { localStorage.setItem(key, JSON.stringify(rules.slice(0, 40))); }
  function clean(text) { return (text || "").toLowerCase().replace(/[-_]/g, " ").replace(/\s+/g, " ").trim(); }

  function draw() {
    list.replaceChildren();
    load().forEach(function (phrase) {
      const row = document.createElement("p");
      row.textContent = phrase + " ";
      const remove = document.createElement("button");
      remove.type = "button";
      remove.textContent = "Remove";
      remove.addEventListener("click", function () {
        save(load().filter(function (item) { return item !== phrase; }));
        draw();
      });
      row.append(remove);
      list.append(row);
    });
  }

  document.getElementById("add-rule").addEventListener("submit", function (event) {
    event.preventDefault();
    const phrase = clean(document.getElementById("rule-text").value);
    if (!phrase) return;
    if (locked.indexOf(phrase) !== -1) {
      status.textContent = "That rule is already locked. It cannot be added or removed.";
      return;
    }
    const rules = load();
    if (rules.indexOf(phrase) === -1) rules.push(phrase);
    save(rules);
    document.getElementById("rule-text").value = "";
    status.textContent = "Saved in this browser.";
    draw();
  });

  document.getElementById("test-form").addEventListener("submit", function (event) {
    event.preventDefault();
    const answer = document.getElementById("answer").value;
    const blob = clean(answer);
    const model = document.getElementById("model-id").value.trim();
    const reasons = [];
    if (secret.test(answer)) reasons.push("A key-shaped string is in the text.");
    locked.concat(load()).forEach(function (phrase) {
      if (blob.indexOf(phrase) !== -1) reasons.push("Blocked: " + phrase);
    });
    const link = document.getElementById("model-link");
    if (/^[A-Za-z0-9][A-Za-z0-9._-]{0,80}\/[A-Za-z0-9][A-Za-z0-9._-]{0,80}$/.test(model)) {
      link.hidden = false;
      link.href = "https://huggingface.co/" + model;
      link.textContent = "Try this model on Hugging Face";
    } else {
      link.hidden = true;
    }
    status.textContent = (reasons[0] || "No blocked phrase and no key-shaped string.") + " No weights were loaded. This is not a United States certification.";
  });

  draw();
})();
