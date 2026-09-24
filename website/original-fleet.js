(function () {
  const box = document.getElementById("original-bots");
  const lead = document.getElementById("original-lead");
  if (!box) return;
  const blocked = ["mine", "trade", "buy", "sell", "pay", "send", "wire", "order"];
  let bots = [];

  const form = document.createElement("form");
  form.className = "card";
  form.innerHTML = "<h2>Ask an original bot</h2><p><label>Bot <input id=\"original-bot-name\" required placeholder=\"SaaS Builder Bot\"></label></p><p><label>Task <input id=\"original-bot-task\" required placeholder=\"list the features\"></label></p><button class=\"btn btn-primary\" type=\"submit\">Ask</button><p id=\"original-answer\">Nothing asked yet.</p>";
  box.append(form);

  form.addEventListener("submit", function (event) {
    event.preventDefault();
    const name = document.getElementById("original-bot-name").value.trim().toLowerCase();
    const task = document.getElementById("original-bot-task").value.trim().toLowerCase();
    const answer = document.getElementById("original-answer");
    const bot = bots.find(function (item) { return item.name.toLowerCase() === name || item.id === name; });
    if (!bot) {
      answer.textContent = "That original bot is not in the notes.";
      return;
    }
    if (task.split(/\s+/).some(function (word) { return blocked.indexOf(word) !== -1; })) {
      answer.textContent = bot.name + ": the original file is a feature note. It does not mine, trade, pay, or send anything.";
      return;
    }
    answer.textContent = bot.name + ": " + bot.mission + " Read the original note. Nothing was bought, sold, mined, or sent.";
  });

  fetch("data/original-bots.json", { cache: "no-store" })
    .then(function (response) { return response.json(); })
    .then(function (data) {
      bots = data.bots;
      lead.textContent = data.count + " original bots answer from their notes. " + data.systems + " system notes and " + data.income_notes + " income notes. " + data.rule;
      data.bots.forEach(function (bot) {
        const article = document.createElement("article");
        article.className = "card";
        const title = document.createElement("h3");
        title.textContent = bot.name;
        const text = document.createElement("p");
        text.textContent = bot.mission;
        const link = document.createElement("a");
        link.href = "https://github.com/DreamCo-Technologies/Dreamcobots/blob/main/" + bot.file;
        link.textContent = "Original note";
        article.append(title, text, link);
        box.append(article);
      });
    })
    .catch(function () {
      lead.textContent = "The original bot list did not load.";
    });
})();
