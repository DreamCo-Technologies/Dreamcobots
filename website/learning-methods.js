(function () {
  function card(row) {
    const article = document.createElement("article");
    article.className = "card";
    const title = document.createElement("h2");
    title.textContent = row.name;
    const text = document.createElement("p");
    text.textContent = row.where + ". " + row.group + ". " + row.status + ". " + row.note;
    article.append(title, text);
    if (row.source) {
      const link = document.createElement("a");
      link.href = row.source;
      link.textContent = "Source";
      link.target = "_blank";
      link.rel = "noopener noreferrer";
      article.append(link);
    }
    return article;
  }

  fetch("data/learning-methods.json")
    .then(function (response) { return response.json(); })
    .then(function (data) {
      const training = data.methods.filter(function (row) { return row.where === "training catalog"; }).length;
      const study = data.methods.length - training;
      document.getElementById("lead").textContent = data.methods.length + " methods are already in the repository: " + training + " in the training catalog and " + study + " in the study catalog. None of them were trained on this page. " + data.rule;
      data.methods.forEach(function (row) { document.getElementById("methods").append(card(row)); });
    })
    .catch(function () {
      document.getElementById("lead").textContent = "The method list did not load.";
    });
})();
