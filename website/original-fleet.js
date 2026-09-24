(function () {
  const box = document.getElementById("original-bots");
  const lead = document.getElementById("original-lead");
  if (!box) return;
  fetch("data/original-bots.json", { cache: "no-store" })
    .then(function (response) { return response.json(); })
    .then(function (data) {
      lead.textContent = data.count + " original bots are in the fleet. " + data.systems + " system notes and " + data.income_notes + " income notes. " + data.rule;
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
