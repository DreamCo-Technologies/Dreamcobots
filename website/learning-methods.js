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

  Promise.all([
    fetch("data/learning-methods.json").then(function (response) { return response.json(); }),
    fetch("data/learning-readiness.json").then(function (response) { return response.json(); }),
  ]).then(function (payload) {
      const data = payload[0];
      const ready = payload[1];
      document.getElementById("lead").textContent = ready.study_ready + " of " + ready.study_total + " study procedures run and finish. " + ready.training_ready + " of " + ready.training_total + " weight-training methods are production ready. " + ready.reason;
      data.methods.forEach(function (row) { document.getElementById("methods").append(card(row)); });
    })
    .catch(function () {
      document.getElementById("lead").textContent = "The method list did not load.";
    });
})();
